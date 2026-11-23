# hs-dashboard-clone — 화성특례시 통합 대시보드 복제본 (안전 설계)

원본 다모아 대시보드(`total.hscity.go.kr/…/415bf387…`)를 대체하는 복제본. 분석·판정은 이웃 프로젝트 `nice/hs-dashboard-study`에 있다.

스택은 **Python Shiny**. 핵심 차이: **인증키를 브라우저로 보내지 않는다.** 외부 공공 API는 서버(`_collect.py`)가 받아 `data/snapshot/`에 저장하고, 화면은 그 스냅숏만 읽는다. 원본의 키 노출·429(온도 공백)가 구조적으로 사라진다(study 8장).

```
hs-dashboard-clone/
├── app.py            # Shiny 앱 — 내비 8메뉴, 홈(위상·날씨·행사·물때·공약)
├── _collect.py       # 서버측 수집(키 env, 스냅숏 저장). cron 매시
├── styles.css        # 회색조 + 강조색 하나 · Pretendard
├── requirements.txt  # shiny · pandas · faicons
├── TODO.md           # 사전 작업·단계 계획
├── images/wireframe/ # home.svg · menus.svg (화면 설계)
└── data/             # 수집 데이터(공개 웹 + 다모아 공개 표시값)
```

```bash
source ~/.venvs/hs-dashboard-clone/bin/activate   # uv venv (shiny·pandas·faicons)
export DATA_GO_KR_KEY=...    # 서버에서만. 저장소에 넣지 않는다
python _collect.py           # 매시 수집(날씨 등) → data/snapshot/
shiny run app.py --reload    # http://127.0.0.1:8000
```

## 범위 (복제 설계 D3)

1차: 홈(현재). 다음: 도시현황 · 교통 · 재난/안전. 지도는 Leaflet + 공개 GeoJSON(다음 단계). 통합돌봄·복지 대상자는 개인정보라 합성 데이터로 구조만 재현(D4).
