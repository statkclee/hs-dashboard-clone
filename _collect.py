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

SNAP = Path(__file__).parent / "data" / "snapshot"
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
        tmp = next((i["fcstValue"] for i in items if i["category"] == "TMP"), None)
        save("weather", {"status": "ok" if tmp is not None else "error", "tempC": tmp})
        print(f"weather 수집: {tmp}°C" if tmp is not None else "weather 실패(429 등)")
    except Exception as e:  # 429 포함 — 키 노출 없이 상태만 기록
        save("weather", {"status": "error", "reason": type(e).__name__})
        print(f"weather 수집 실패: {type(e).__name__}")


def main() -> None:
    key = os.environ.get("DATA_GO_KR_KEY", "")
    if not key:
        print("DATA_GO_KR_KEY 없음 — 수집 건너뜀. 화면은 '서버 수집 대기'로 표시됨.")
        save("weather", {"status": "pending", "reason": "no key on server"})
        return
    collect_weather(key)


if __name__ == "__main__":
    main()
