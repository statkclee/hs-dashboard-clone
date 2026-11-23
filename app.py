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
            ui.card(ui.card_header("지도 — 권역별 (Leaflet + 공개 GeoJSON · 다음 단계)"),
                    ui.div("지도 자리 — 공개 행정경계 GeoJSON으로 구현 예정",
                           class_="map-placeholder")),
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


def traffic_panel() -> ui.Tag:
    ev = snapshot("evcharger")
    n = ev.get("n", 0) if ev.get("status") == "ok" else 0
    return ui.nav_panel(
        "교통",
        ui.layout_columns(
            value_box("전기차 충전소", f"{n:,}곳" if n else "— (서버 수집 대기)", "charging-station"),
            col_widths=(4,), fill=False),
        ui.card(ui.card_header("전기차 충전소 — 화성시 (지도는 다음 단계)"),
                ui.output_ui("ev_table")),
    )


def stub_panel(name: str) -> ui.Tag:
    return ui.nav_panel(name, ui.card(ui.card_header(name),
        ui.p(f"{name} 화면 — 와이어프레임(images/wireframe/menus.svg)에 따라 구현 예정.", class_="muted")))


def panel_for(name: str) -> ui.Tag:
    return traffic_panel() if name == "교통" else stub_panel(name)


app_ui = ui.page_navbar(
    home_panel(),
    *[panel_for(m) for m in MENUS[1:]],
    title="화성특례시 통합 대시보드 · 복제본",
    id="menu",
    header=ui.head_content(ui.include_css(HERE / "styles.css")),
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


app = App(app_ui, server)
