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


def weather_snapshot() -> dict:
    f = DATA / "snapshot" / "weather.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "pending"}


def df_to_table(df: pd.DataFrame) -> ui.Tag:
    head = ui.tags.thead(ui.tags.tr(*[ui.tags.th(c) for c in df.columns]))
    rows = [ui.tags.tr(*[ui.tags.td(str(v)) for v in r]) for r in df.itertuples(index=False)]
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


def stub_panel(name: str) -> ui.Tag:
    return ui.nav_panel(name, ui.card(ui.card_header(name),
        ui.p(f"{name} 화면 — 와이어프레임(images/wireframe/menus.svg)에 따라 구현 예정.", class_="muted")))


app_ui = ui.page_navbar(
    home_panel(),
    *[stub_panel(m) for m in MENUS[1:]],
    title="화성특례시 통합 대시보드 · 복제본",
    id="menu",
    header=ui.head_content(ui.include_css(HERE / "styles.css")),
    fillable=False,
)


def server(input, output, session):
    @render.ui
    def weather():
        wx = weather_snapshot()
        if wx.get("status") == "ok":
            return ui.h1(f"{wx['tempC']}°C")
        return ui.TagList(
            ui.div("— °C", class_="pending"),
            ui.p("서버 수집 대기 — 인증키가 서버에 설정되면 매시 수집됩니다. "
                 "키는 브라우저로 전송하지 않습니다(원본의 노출·429 문제를 구조적으로 제거).",
                 class_="collect-note"),
            ui.p("초미세·미세·자외선·대기확산도 같은 방식으로 서버 수집", class_="muted small"),
        )

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
