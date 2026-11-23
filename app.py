"""화성특례시 통합 대시보드 · 복제본 (Python Shiny).

원본 다모아 대시보드 대체. 인증키는 서버에만(hs-dashboard-study 8장) —
외부 공공 API는 _collect.py 가 서버에서 받아 data/snapshot/ 에 저장하고,
이 화면은 그 스냅숏만 읽는다. 키는 브라우저로 전송하지 않는다.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from shiny import App, ui, render
from faicons import icon_svg

HERE = Path(__file__).parent
DATA = HERE / "data"
MENUS = ["홈", "도시현황", "행정현황", "사업관리", "재난/안전", "교통", "문화/관광", "바로이웃 통합돌봄"]


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


wi = load("위상카드-다모아.csv")
ev = load("행사.csv")
ti = load("제부도물때.csv")
pl = load("공약사업-요약.csv")
pc = load("공약사업-분야별.csv")
st_ind = load("위상지표.csv")
aw = load("수상실적.csv")
pledge_rate = pl.loc[pl["항목"] == "이행률", "값"].iloc[0]
pledge_done = pl.loc[pl["항목"] == "이행 완료", "값"].iloc[0]
pledge_total = pl.loc[pl["항목"] == "전체 공약 수", "값"].iloc[0]


def snapshot(name: str) -> dict:
    f = DATA / "snapshot" / f"{name}.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "pending"}


def _cell(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return str(v)


def df_to_table(df: pd.DataFrame) -> ui.Tag:
    head = ui.tags.thead(ui.tags.tr(*[ui.tags.th(c) for c in df.columns]))
    rows = [ui.tags.tr(*[ui.tags.td(_cell(v)) for v in r]) for r in df.itertuples(index=False)]
    return ui.tags.table({"class": "tbl"}, head, ui.tags.tbody(*rows))


def value_box(title: str, value: str, icon: str) -> ui.Tag:
    return ui.value_box(title, value, showcase=icon_svg(icon), theme="bg-gradient-light")


def home_panel() -> ui.Tag:
    return ui.nav_panel(
        "홈",
        ui.layout_columns(
            value_box("인구", "1,074,002명", "users"),
            value_box("GRDP · 전국 1위", "90.4조원", "won-sign"),
            value_box("고용률 · 경기 1위", "67.9%", "briefcase"),
            value_box("출생아 · 전국 1위", "8,116명", "baby"),
            value_box("공약 이행률", str(pledge_rate), "list-check"),
            col_widths=(2, 3, 2, 2, 3), fill=False,
        ),
        ui.layout_columns(
            ui.card(ui.card_header("화성시 날씨 · 대기"), ui.output_ui("weather")),
            ui.card(ui.card_header("이 달의 행사"), ui.output_ui("events")),
            ui.card(ui.card_header("화성특례시의 위상"), ui.output_ui("status")),
            col_widths=(4, 4, 4),
        ),
        ui.layout_columns(
            ui.card(ui.card_header("읍면동 인구 지도 — 공개 행정동 GeoJSON (네이버 키 불필요)"),
                    ui.output_ui("pop_map"), height="460px"),
            ui.card(ui.card_header("제부도 바닷길"), ui.output_ui("tide")),
            col_widths=(8, 4),
        ),
        ui.layout_columns(
            ui.card(ui.card_header("공약사업 — 분야별 추진 현황"), ui.output_ui("pledge_cat")),
            ui.card(ui.card_header("공약 이행"),
                    ui.div(ui.h1(f"{pledge_done} / {pledge_total}"),
                           ui.p(f"이행 완료 · 이행률 {pledge_rate}", class_="muted"),
                           class_="pledge-big")),
            col_widths=(8, 4),
        ),
    )


def pop_map_html() -> str:
    """읍면동 인구 choropleth — 공개 행정동 GeoJSON(vuski/admdongkor) + 인구 스냅숏.
    네이버 키 불필요. 동 이름으로 조인."""
    import folium
    pop = snapshot("population")
    geo = DATA / "geo" / "hwaseong_emd.geojson"
    m = folium.Map(location=[37.17, 126.92], zoom_start=10,
                   tiles="OpenStreetMap", control_scale=True)
    if not geo.exists():
        return m._repr_html_()
    gj = json.loads(geo.read_text(encoding="utf-8"))
    # 화성시 경계에 맞춰 지도 확대
    xs, ys = [], []
    def _walk(c):
        if c and isinstance(c[0], (int, float)):
            xs.append(c[0]); ys.append(c[1])
        else:
            for x in c:
                _walk(x)
    for f in gj["features"]:
        _walk(f["geometry"]["coordinates"])
    if xs and ys:
        m.fit_bounds([[min(ys), min(xs)], [max(ys), max(xs)]])
    pm = {d["dong"]: d["total"] for d in pop.get("dongs", [])} if pop.get("status") == "ok" else {}
    if pm:
        df = pd.DataFrame({"dong": list(pm), "pop": list(pm.values())})
        folium.Choropleth(
            geo_data=gj, data=df, columns=["dong", "pop"],
            key_on="feature.properties.dong",
            fill_color="YlOrRd", fill_opacity=0.75, line_color="#ffffff",
            line_weight=1, nan_fill_color="#cccccc",
            legend_name="읍면동 주민등록 인구(명)").add_to(m)
    # 동 이름 + 인구 툴팁
    for f in gj["features"]:
        f["properties"]["pop_fmt"] = f"{pm.get(f['properties']['dong'], 0):,}명"
    folium.GeoJson(
        gj, style_function=lambda x: {"fillOpacity": 0, "weight": 0},
        tooltip=folium.GeoJsonTooltip(fields=["dong", "pop_fmt"],
                                      aliases=["읍면동", "인구"])).add_to(m)
    # 대기질 측정소 마커(공개 측정소 좌표)
    stn = snapshot("stations")
    if stn.get("status") == "ok":
        for s in stn["stations"]:
            try:
                folium.CircleMarker(
                    [float(s["lat"]), float(s["lng"])], radius=4,
                    color="#167aff", fill=True, fill_color="#167aff", fill_opacity=0.9,
                    popup=f"측정소 {s['station']}").add_to(m)
            except Exception:
                continue
    return m._repr_html_()


def ev_map_html() -> str:
    """충전소 좌표를 Leaflet(folium) 지도로. 공개 타일 — 네이버 키 불필요."""
    import folium
    from folium.plugins import MarkerCluster
    ev = snapshot("evcharger")
    m = folium.Map(location=[37.2, 126.9], zoom_start=11, tiles="OpenStreetMap")
    if ev.get("status") == "ok":
        mc = MarkerCluster().add_to(m)
        for c in ev["chargers"]:
            try:
                lat, lng = float(c["lat"]), float(c["lng"])
            except Exception:
                continue
            folium.CircleMarker([lat, lng], radius=3, color="#273449", fill=True,
                                fill_opacity=0.7, popup=c.get("name")).add_to(mc)
    return m._repr_html_()


def traffic_panel() -> ui.Tag:
    ev = snapshot("evcharger")
    n = ev.get("n", 0) if ev.get("status") == "ok" else 0
    return ui.nav_panel(
        "교통",
        ui.layout_columns(
            value_box("전기차 충전소", f"{n:,}곳" if n else "— (서버 수집 대기)", "charging-station"),
            col_widths=(4,), fill=False),
        ui.layout_columns(
            ui.card(ui.card_header("전기차 충전소 지도 — 화성시 (Leaflet · 공개 타일)"),
                    ui.HTML(ev_map_html()), height="520px"),
            ui.card(ui.card_header("충전소 목록"), ui.output_ui("ev_table")),
            col_widths=(7, 5),
        ),
    )


def city_panel() -> ui.Tag:
    pop = snapshot("population")
    total = pop.get("total", 0) if pop.get("status") == "ok" else 0
    return ui.nav_panel(
        "도시현황",
        ui.layout_columns(
            value_box("주민등록 인구", f"{total:,}명" if total else "— (서버 수집 대기)", "users"),
            value_box("읍면동", f"{pop.get('n', 0)}곳" if total else "—", "map-location-dot"),
            col_widths=(4, 3), fill=False),
        ui.card(ui.card_header(f"읍면동별 인구 — {pop.get('month', '')} 기준 (주민등록 내국인)"),
                ui.output_ui("pop_table")),
    )


def safety_panel() -> ui.Tag:
    air = snapshot("air")
    ls = snapshot("landslide")
    pm = air.get("pm10_avg") if air.get("status") == "ok" else None
    nls = ls.get("n", 0) if ls.get("status") == "ok" else 0
    return ui.nav_panel(
        "재난/안전",
        ui.layout_columns(
            value_box("미세먼지(PM10) 평균", f"{pm} µg/m³" if pm is not None else "— (수집 대기)", "wind"),
            value_box("초미세먼지(PM2.5) 평균",
                      f"{air.get('pm25_avg')} µg/m³" if air.get("status") == "ok" else "—", "smog"),
            value_box("산사태우려지역", f"{nls}곳" if ls.get("status") == "ok" else "— (수집 대기)",
                      "mountain"),
            col_widths=(4, 4, 4), fill=False),
        ui.layout_columns(
            ui.card(ui.card_header("실시간 대기질 — 화성시 측정소"), ui.output_ui("air_table")),
            ui.card(ui.card_header("산사태우려지역 — 화성시 (safetydata)"), ui.output_ui("ls_table")),
            col_widths=(7, 5),
        ),
    )


def culture_panel() -> ui.Tag:
    return ui.nav_panel(
        "문화/관광",
        ui.layout_columns(
            ui.card(ui.card_header("이 달의 행사"), ui.output_ui("events2")),
            ui.card(ui.card_header("제부도 바닷길 물때"), ui.output_ui("tide2")),
            col_widths=(7, 5),
        ),
        ui.card(ui.card_header("국제교류도시 · 자매·우호도시"), ui.output_ui("sister")),
    )


def business_panel() -> ui.Tag:
    return ui.nav_panel(
        "사업관리",
        ui.layout_columns(
            value_box("전체 공약 수", f"{pledge_total}개", "list-check"),
            value_box("이행 완료", f"{pledge_done}개", "circle-check"),
            value_box("이행률", str(pledge_rate), "chart-line"),
            col_widths=(4, 4, 4), fill=False),
        ui.card(ui.card_header("공약사업 — 분야별 추진 현황 (민선8기)"), ui.output_ui("biz_cat")),
    )


def admin_panel() -> ui.Tag:
    return ui.nav_panel(
        "행정현황",
        ui.layout_columns(
            value_box("지방자치경쟁력", "종합 1위", "trophy"),
            value_box("인구", "전국 4위", "ranking-star"),
            value_box("재정·행정 수상", f"{len(aw)}건", "award"),
            col_widths=(4, 4, 4), fill=False),
        ui.layout_columns(
            ui.card(ui.card_header("화성특례시 위상 지표"), ui.output_ui("stature_tbl")),
            ui.card(ui.card_header("최근 수상·평가 실적"), ui.output_ui("award_tbl")),
            col_widths=(6, 6),
        ),
    )


def care_panel() -> ui.Tag:
    ct = load("통합돌봄-유형별.csv")
    total = int(ct["대상자수"].sum())
    svc = int(ct["월평균 서비스건수"].sum())
    return ui.nav_panel(
        "바로이웃 통합돌봄",
        ui.div("⚠ 합성(가상) 데이터 — 개인정보 비수집 원칙에 따라 실제 대상자 행은 수집하지 않고, "
               "구조·화면 재현용 집계만 생성했습니다. 실데이터는 소관부서 승인·가명처리 후 연결.",
               class_="synth-note"),
        ui.layout_columns(
            value_box("돌봄 대상자(합성)", f"{total:,}명", "hand-holding-heart"),
            value_box("돌봄 유형", f"{len(ct)}종", "layer-group"),
            value_box("월평균 서비스(합성)", f"{svc:,}건", "house-medical"),
            col_widths=(4, 4, 4), fill=False),
        ui.layout_columns(
            ui.card(ui.card_header("돌봄 유형별 현황 (합성)"), ui.output_ui("care_type")),
            ui.card(ui.card_header("읍면동별 대상자 분포 (합성)"), ui.output_ui("care_dong")),
            col_widths=(6, 6),
        ),
    )


def stub_panel(name: str) -> ui.Tag:
    return ui.nav_panel(name, ui.card(ui.card_header(name),
        ui.p(f"{name} 화면 — 와이어프레임(images/wireframe/menus.svg)에 따라 구현 예정.", class_="muted")))


def panel_for(name: str) -> ui.Tag:
    if name == "교통":
        return traffic_panel()
    if name == "도시현황":
        return city_panel()
    if name == "재난/안전":
        return safety_panel()
    if name == "문화/관광":
        return culture_panel()
    if name == "사업관리":
        return business_panel()
    if name == "행정현황":
        return admin_panel()
    if name == "바로이웃 통합돌봄":
        return care_panel()
    return stub_panel(name)


app_ui = ui.page_navbar(
    home_panel(),
    *[panel_for(m) for m in MENUS[1:]],
    title="화성특례시 통합 대시보드 · 복제본",
    id="menu",
    header=ui.head_content(
        ui.tags.script("document.documentElement.setAttribute('data-bs-theme','dark');"),
        ui.include_css(HERE / "styles.css")),
    fillable=False,
)


def server(input, output, session):
    @render.ui
    def weather():
        wx = snapshot("weather")
        air = snapshot("air")
        if wx.get("status") != "ok":
            return ui.TagList(
                ui.div("— °C", class_="pending"),
                ui.p("서버 수집 대기 — 인증키가 서버에 설정되면 매시 수집됩니다. "
                     "키는 브라우저로 전송하지 않습니다(원본의 노출·429 문제를 구조적으로 제거).",
                     class_="collect-note"),
            )
        parts = [ui.h1(f"{wx['tempC']}°C")]
        if air.get("status") == "ok":
            parts.append(ui.div(
                ui.span(f"초미세 {air.get('pm25_avg')} ", class_="muted"),
                ui.span(f"· 미세 {air.get('pm10_avg')} µg/m³ ", class_="muted"),
                ui.span(f"· 측정소 {air.get('n')}곳", class_="muted small")))
            st = pd.DataFrame(air["stations"])[["station", "pm10", "pm25", "o3"]]
            st.columns = ["측정소", "미세(PM10)", "초미세(PM2.5)", "오존"]
            parts.append(df_to_table(st))
        parts.append(ui.p(f"서버 수집 {wx.get('collectedAt','')} · 키는 서버에만", class_="muted small"))
        return ui.TagList(*parts)

    @render.ui
    def pop_map():
        return ui.HTML(pop_map_html())

    @render.ui
    def pop_table():
        pop = snapshot("population")
        if pop.get("status") != "ok":
            return ui.p("서버 수집 대기", class_="collect-note")
        df = pd.DataFrame(pop["dongs"]).sort_values("total", ascending=False)
        df["total"] = df["total"].map(lambda v: f"{v:,}")
        df.columns = ["읍면동", "인구"]
        return df_to_table(df)

    @render.ui
    def ev_table():
        ev = snapshot("evcharger")
        if ev.get("status") != "ok":
            return ui.p("서버 수집 대기", class_="collect-note")
        df = pd.DataFrame(ev["chargers"])[["name", "addr", "connectors"]].head(30)
        df.columns = ["충전소", "주소", "충전기수"]
        return ui.TagList(ui.p(f"화성시 충전소 {ev['n']:,}곳 (상위 30 표시)", class_="muted small"),
                          df_to_table(df))

    @render.ui
    def events():
        return df_to_table(ev)

    @render.ui
    def status():
        d = wi.copy()
        d["구분"] = d["순위범위"].astype(str) + " " + d["순위"].astype(str) + "위"
        return df_to_table(d[["구분", "지표", "값표기"]])

    @render.ui
    def tide():
        return df_to_table(ti)

    @render.ui
    def pledge_cat():
        return df_to_table(pc)

    @render.ui
    def air_table():
        air = snapshot("air")
        if air.get("status") != "ok":
            return ui.p("서버 수집 대기", class_="collect-note")
        st = pd.DataFrame(air["stations"])[["station", "pm10", "pm25", "o3"]]
        st.columns = ["측정소", "미세(PM10)", "초미세(PM2.5)", "오존"]
        return ui.TagList(ui.p(f"측정소 {air.get('n')}곳 · 수집 {air.get('collectedAt','')}",
                               class_="muted small"), df_to_table(st))

    @render.ui
    def ls_table():
        ls = snapshot("landslide")
        if ls.get("status") != "ok":
            return ui.p("서버 수집 대기", class_="collect-note")
        if not ls["items"]:
            return ui.p("화성시 산사태우려지역 지정 없음(평지).", class_="muted")
        df = pd.DataFrame(ls["items"])
        return ui.TagList(ui.p(f"전국 {ls.get('nationwide')}건 중 화성 {ls['n']}곳",
                               class_="muted small"), df_to_table(df))

    @render.ui
    def events2():
        return df_to_table(ev)

    @render.ui
    def tide2():
        return df_to_table(ti)

    @render.ui
    def biz_cat():
        return df_to_table(pc)

    @render.ui
    def stature_tbl():
        return df_to_table(st_ind)

    @render.ui
    def award_tbl():
        return df_to_table(aw)

    @render.ui
    def care_type():
        return df_to_table(load("통합돌봄-유형별.csv"))

    @render.ui
    def care_dong():
        return df_to_table(load("통합돌봄-읍면동.csv"))

    @render.ui
    def sister():
        try:
            si = load("교류도시.csv")
        except Exception:
            return ui.p("교류도시 데이터 없음", class_="muted")
        return df_to_table(si)


app = App(app_ui, server)
