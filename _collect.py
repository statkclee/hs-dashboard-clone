"""서버측 수집 (hs-dashboard-study 8장 해법 D2).

인증키는 환경변수 DATA_GO_KR_KEY 에서만 읽고, 받은 값은 data/snapshot/ 에 저장한다.
브라우저로 키를 보내지 않는다. 대시보드(app.py)는 이 스냅숏만 읽는다.
키가 없으면 수집을 건너뛰고 화면은 "서버 수집 대기"로 표시된다(안전한 기본값).

  서버 cron 예:  */60 * * * *  python _collect.py
  키 설정:       export DATA_GO_KR_KEY=...   # 저장소에 넣지 않는다
"""
from __future__ import annotations
import json, os, datetime, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).parent


def load_dotenv(path: Path) -> None:
    """프로젝트 .env(gitignore)에서 KEY=VALUE를 환경변수로. 외부 의존성 없음.
    이미 설정된 환경변수는 덮어쓰지 않는다(서버 Secret 우선)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'").strip('"'))


load_dotenv(HERE / ".env")
SNAP = HERE / "data" / "snapshot"
SNAP.mkdir(parents=True, exist_ok=True)
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save(name: str, value: dict) -> None:
    (SNAP / f"{name}.json").write_text(
        json.dumps({**value, "collectedAt": NOW}, ensure_ascii=False), encoding="utf-8")


def collect_weather(key: str) -> None:
    base = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    q = {"serviceKey": key, "dataType": "JSON", "numOfRows": 1000, "pageNo": 1,
         "base_date": datetime.date.today().strftime("%Y%m%d"),
         "base_time": "0500", "nx": 57, "ny": 119}
    url = base + "?" + urllib.parse.urlencode(q)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body = json.loads(r.read())
        items = body["response"]["body"]["items"]["item"]
        # 가장 이른 예보시각(현재에 가장 가까운) 기준으로 각 항목 선택
        def first(cat):
            vs = [i for i in items if i["category"] == cat]
            return vs[0]["fcstValue"] if vs else None
        def day_ext(cat):  # TMN/TMX 는 하루 중 특정 시각에만 — 아무 값
            return next((i["fcstValue"] for i in items if i["category"] == cat), None)
        tmp = first("TMP")
        wx = {"status": "ok" if tmp is not None else "error", "tempC": tmp,
              "tmin": day_ext("TMN"), "tmax": day_ext("TMX"),
              "humidity": first("REH"), "windSpeed": first("WSD"),
              "windDir": first("VEC"), "precip": first("PCP"),
              "pop": first("POP"), "sky": first("SKY"), "pty": first("PTY")}
        save("weather", wx)
        print(f"weather 수집: {tmp}°C (최저 {wx['tmin']}/최고 {wx['tmax']}, 습도 {wx['humidity']}%)"
              if tmp is not None else "weather 실패(429 등)")
    except Exception as e:  # 429 포함 — 키 노출 없이 상태만 기록
        save("weather", {"status": "error", "reason": type(e).__name__})
        print(f"weather 수집 실패: {type(e).__name__}")


HS_STATIONS = {"남양읍", "동탄", "봉담읍", "새솔동", "서신면", "송산3동", "우정읍", "청계동",
               "향남읍", "병점", "비봉", "매송", "정남", "장안", "팔탄", "양감", "마도", "송산"}


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())


def collect_air(key: str) -> None:
    """에어코리아 실시간 대기 — 경기 측정소 중 화성 측정소만."""
    base = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    q = {"serviceKey": key, "returnType": "json", "numOfRows": 800, "pageNo": 1,
         "sidoName": "경기", "ver": "1.0"}
    try:
        items = _get(base + "?" + urllib.parse.urlencode(q))["response"]["body"]["items"]
        hs = [i for i in items if any(h in (i.get("stationName") or "") for h in HS_STATIONS)]
        def num(x):
            try: return float(x)
            except Exception: return None
        clean = [{"station": i["stationName"], "time": i.get("dataTime"),
                  "pm10": num(i.get("pm10Value")), "pm25": num(i.get("pm25Value")),
                  "o3": num(i.get("o3Value")), "khai": i.get("khaiGrade")} for i in hs]
        pm10 = [c["pm10"] for c in clean if c["pm10"] is not None]
        pm25 = [c["pm25"] for c in clean if c["pm25"] is not None]
        save("air", {"status": "ok", "stations": clean,
                     "pm10_avg": round(sum(pm10) / len(pm10), 1) if pm10 else None,
                     "pm25_avg": round(sum(pm25) / len(pm25), 1) if pm25 else None,
                     "n": len(clean)})
        print(f"air 수집: 화성 측정소 {len(clean)}곳 · PM2.5 평균 {clean and round(sum(pm25)/len(pm25),1) if pm25 else '-'}")
    except Exception as e:
        save("air", {"status": "error", "reason": type(e).__name__})
        print(f"air 수집 실패: {type(e).__name__}")


def collect_stations(key: str) -> None:
    """측정소 좌표(지도용)."""
    base = "https://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList"
    q = {"serviceKey": key, "returnType": "json", "numOfRows": 100, "pageNo": 1, "addr": "경기 화성"}
    try:
        items = _get(base + "?" + urllib.parse.urlencode(q))["response"]["body"]["items"]
        st = [{"station": i["stationName"], "lat": float(i["dmX"]), "lng": float(i["dmY"]),
               "addr": i.get("addr")} for i in items if i.get("dmX") and i.get("dmY")]
        save("stations", {"status": "ok", "stations": st, "n": len(st)})
        print(f"stations 수집: {len(st)}곳")
    except Exception as e:
        save("stations", {"status": "error", "reason": type(e).__name__})
        print(f"stations 수집 실패: {type(e).__name__}")


def collect_evcharger(key: str) -> None:
    """전기차 충전소 — 화성시(zscode 41590) 서버측 필터. 충전기 → 충전소 단위로 접음."""
    import xml.etree.ElementTree as ET
    base = "https://apis.data.go.kr/B552584/EvCharger/getChargerInfo"
    try:
        q = {"serviceKey": key, "pageNo": 1, "numOfRows": 20000, "zscode": 41590}
        with urllib.request.urlopen(base + "?" + urllib.parse.urlencode(q), timeout=60) as r:
            root = ET.fromstring(r.read())
        uniq = {}
        for it in root.findall(".//item"):
            g = lambda t: (it.findtext(t) or "")
            kstat = (g("statNm"), g("lat"), g("lng"))
            if kstat not in uniq:
                uniq[kstat] = {"name": g("statNm"), "addr": g("addr"),
                               "lat": g("lat"), "lng": g("lng"), "connectors": 0}
            uniq[kstat]["connectors"] += 1
        chg = list(uniq.values())
        save("evcharger", {"status": "ok", "chargers": chg, "n": len(chg)})
        print(f"evcharger 수집: 화성 충전소 {len(chg)}곳")
    except Exception as e:
        save("evcharger", {"status": "error", "reason": type(e).__name__})
        print(f"evcharger 수집 실패: {type(e).__name__}")


def collect_population(key: str) -> None:
    """행안부 행정동별 주민등록 인구(15108072) — 화성시 읍면동. 최신 가용월 자동 탐색."""
    import datetime as _dt
    base = "https://apis.data.go.kr/1741000/admmSexdAgePpltn/selectAdmmSexdAgePpltn"
    today = _dt.date.today()
    months = [(today.replace(day=1) - _dt.timedelta(days=28 * i)).strftime("%Y%m") for i in range(1, 7)]
    try:
        for ym in months:
            q = {"serviceKey": key, "admmCd": "4159000000", "srchFrYm": ym, "srchToYm": ym,
                 "lv": 3, "type": "JSON", "numOfRows": 100, "pageNo": 1}
            try:
                data = _get(base + "?" + urllib.parse.urlencode(q))
            except Exception:
                continue
            items = data.get("Response", {}).get("items", "")
            if isinstance(items, dict):
                items = items.get("item", [])
            if items:
                dongs = [{"dong": i.get("dongNm"), "total": int(i.get("totNmprCnt") or 0)} for i in items]
                dongs = [d for d in dongs if d["dong"]]
                save("population", {"status": "ok", "month": ym, "dongs": dongs,
                                    "total": sum(d["total"] for d in dongs), "n": len(dongs)})
                print(f"population 수집: {ym} · 읍면동 {len(dongs)}곳 · 합계 {sum(d['total'] for d in dongs):,}")
                return
        save("population", {"status": "error", "reason": "no month available"})
        print("population 수집 실패: 가용 월 없음")
    except Exception as e:
        save("population", {"status": "error", "reason": type(e).__name__})
        print(f"population 수집 실패: {type(e).__name__}")


def collect_landslide(key: str) -> None:
    """산사태우려지역(safetydata DSSP-IF-10694) — 전국에서 화성(법정동 4159…)만 필터.
    별도 키 SAFETY_LANDSLIDE_KEY. 서비스가 sigunguCd 필터를 무시하므로 클라이언트 필터."""
    base = "https://www.safetydata.go.kr/V2/api/DSSP-IF-10694"
    try:
        rows, page = [], 1
        while True:
            q = {"serviceKey": key, "numOfRows": 1000, "pageNo": page, "type": "json"}
            data = _get(base + "?" + urllib.parse.urlencode(q))
            body = data.get("body") or []
            if not body:
                break
            rows += body
            if len(rows) >= int(data.get("totalCount", 0)) or page > 10:
                break
            page += 1
        hs = [r for r in rows if str(r.get("STDG_CD", "")).startswith("4159")]
        clean = [{"읍면동법정코드": r.get("STDG_CD"), "지명": r.get("PPLRLYKNWN_NM"),
                  "예상피해": r.get("EXPC_DAM_ETC_CN")} for r in hs]
        save("landslide", {"status": "ok", "items": clean, "n": len(clean),
                           "nationwide": len(rows)})
        print(f"landslide 수집: 화성 산사태우려지역 {len(clean)}곳 (전국 {len(rows)})")
    except Exception as e:
        save("landslide", {"status": "error", "reason": type(e).__name__})
        print(f"landslide 수집 실패: {type(e).__name__}")


def collect_steepslope(key: str) -> None:
    """급경사지 붕괴위험지역(safetydata DSSP-IF-10167) — 화성(MNG_NO 앞 5자리 41590)만 필터.
    별도 키 SAFETY_STEEPSLOPE_KEY. 지역 필터 파라미터가 없어 MNG_NO 접두로 클라이언트 필터."""
    base = "https://www.safetydata.go.kr/V2/api/DSSP-IF-10167"
    grade = {"SDG001": "A", "SDG002": "B", "SDG003": "C", "SDG004": "D", "SDG005": "E"}
    try:
        rows, page = [], 1
        while page <= 6:
            q = {"serviceKey": key, "numOfRows": 1000, "pageNo": page, "type": "json"}
            data = _get(base + "?" + urllib.parse.urlencode(q))
            body = data.get("body") or []
            if not body:
                break
            rows += body
            total = int(data.get("totalCount", 0) or 0)
            if len(rows) >= total:
                break
            page += 1
        hs = [r for r in rows if str(r.get("MNG_NO", "")).strip().startswith("41590")]
        clean = [{"지구명": r.get("CLPS_RSK_DSTRCT_NM"),
                  "등급": grade.get(str(r.get("DST_DADE_EVL_GRD_CD")), r.get("DST_DADE_EVL_GRD_CD")),
                  "평가점수": r.get("DST_DADE_EVL_SCR_SUM"),
                  "지정일": r.get("CLPS_RSK_DSTRCT_DSGN_DT"),
                  "지정사유": r.get("CLPS_RSK_DSTRCT_DSGN_RSN_CN")} for r in hs]
        save("steepslope", {"status": "ok", "items": clean, "n": len(clean), "nationwide": len(rows)})
        print(f"steepslope 수집: 화성 급경사지 {len(clean)}곳 (전국 {len(rows)})")
    except Exception as e:
        save("steepslope", {"status": "error", "reason": type(e).__name__})
        print(f"steepslope 수집 실패: {type(e).__name__}")


def collect_parking(key: str) -> None:
    """전국주차장표준데이터(15012896) — 화성시만. 승인 후 1~2h 활성화되면 수집됨."""
    base = "https://api.data.go.kr/openapi/tn_pubr_public_prkplce_info_api"
    try:
        q = {"serviceKey": key, "type": "json", "numOfRows": 2000, "pageNo": 1}
        data = _get(base + "?" + urllib.parse.urlencode(q))
        items = (((data.get("response") or {}).get("body") or {}).get("items")) or []
        hs = [i for i in items if "화성" in (i.get("instt_nm", "") + i.get("rdnmadr", "") + i.get("lnmadr", ""))]
        clean = [{"name": i.get("prkplce_nm"), "addr": i.get("rdnmadr") or i.get("lnmadr"),
                  "구분": i.get("prkplce_se"), "주차면수": i.get("prkcmprt_co"),
                  "lat": i.get("latitude"), "lng": i.get("longitude")} for i in hs]
        save("parking", {"status": "ok", "items": clean, "n": len(clean)})
        print(f"parking 수집: 화성 주차장 {len(clean)}곳")
    except Exception as e:
        save("parking", {"status": "pending", "reason": type(e).__name__})
        print(f"parking 수집 보류(활성화 대기 가능): {type(e).__name__}")


def main() -> None:
    key = os.environ.get("DATA_GO_KR_KEY", "")
    if not key:
        print("DATA_GO_KR_KEY 없음 — 수집 건너뜀. 화면은 '서버 수집 대기'로 표시됨.")
        for n in ("weather", "air", "stations", "evcharger"):
            save(n, {"status": "pending", "reason": "no key on server"})
        return
    collect_weather(key)
    collect_air(key)
    collect_stations(key)
    collect_evcharger(key)
    collect_population(key)
    collect_parking(key)
    lk = os.environ.get("SAFETY_LANDSLIDE_KEY", "")
    if lk:
        collect_landslide(lk)
    else:
        print("SAFETY_LANDSLIDE_KEY 없음 — 산사태 수집 건너뜀.")
    sk = os.environ.get("SAFETY_STEEPSLOPE_KEY", "")
    if sk:
        collect_steepslope(sk)
    else:
        print("SAFETY_STEEPSLOPE_KEY 없음 — 급경사지 수집 건너뜀.")


if __name__ == "__main__":
    main()
