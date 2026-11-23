# TODO — hs-dashboard-clone (화성특례시 대시보드 복제, 안전 설계)

목표: 원본 다모아 대시보드를 대체하는 복제본. **인증키는 서버에만**(study 8장). 스택은 **Python Shiny**.
분석·판정 근거는 이웃 `nice/hs-dashboard-study`(9장 데이터 판정, 8장 보안·한도).

## 0. 사전 작업 (스택 전환)

- [x] Python Shiny 설치 — venv `~/.venvs/hs-dashboard-clone` (shiny · pandas · faicons)
- [x] 스택 전환: Quarto-R 대시보드 → Shiny-Python(`app.py`). 초판(Quarto)은 git 이력에 남김
- [x] 빌드 등록 정리: `quarto-builds.txt`에서 제외(Quarto 렌더 아님), `git-repos.txt`는 유지
- [ ] 실행/배포 문서화 — 로컬 `shiny run`, 배포 후보 Posit Connect(`connect:deploy-to-connect`)
- [ ] 개인정보 규칙: 통합돌봄·복지 대상자는 행 수집 금지, 집계·합성만

## 1. 와이어프레임 (images/wireframe/)

각 화면을 SVG로 설계한다. 위젯 배치·데이터 바인딩을 함께 적는다.

- [x] `home.svg` — 홈 (위상 카드 · 날씨 · 행사 · 물때 · 지도 · 공약)
- [x] `menus.svg` — 나머지 7개 메뉴 레이아웃 한 장 요약
- [ ] 메뉴별 상세 와이어프레임 (도시현황 · 교통 · 재난/안전 — 1차 범위부터)
- [ ] 화면 명세서(위젯·데이터소스·갱신주기) — study 9장 판정과 연결

## 2. 데이터 수집 (data/)

수집 규칙은 study README "데이터 확보 규칙". 공개 1순위 → 다모아 공개값 → 집계/합성.

- [x] 공개 웹: 교류도시 · 수상실적 · 위상지표
- [x] 다모아 공개 표시값: 위상 카드 · 행사 · 제부도 물때 · 공약
- [ ] **공개 데이터 포털 파일/API** — 인증키 필요(대기). 목록·URL은 study `data/collection-status.csv`
- [ ] **🔑 인증키 발급·설정 (사용자 작업)** — `docs-apikey.md` · `images/apikey-flow.svg` 참고
  - [ ] data.go.kr 가입 → 인증키 확인 → 아래 API 활용신청(운영계정 권장)
  - [x] **기상청 단기예보 신청 완료** — 개발계정 승인 2026-11-23 ~ 2028-11-23
  - 개발계정 한도(일 ~10,000건)로 충분: 서버 수집은 하루 ≈24건(원본은 방문자별이라 수만 건→429)
  - [ ] (data.go.kr 키) 에어코리아(15073861·15073877) · 충전소(15076352) · 관세청 수출입(15134344) · 워크넷(3038225) · 조위(15142507)
  - [~] **(safetydata.go.kr — 서비스별 키 따로)** 산사태(DSSP-IF-10694)=env `SAFETY_LANDSLIDE_KEY` · 붕괴위험=env `SAFETY_STEEPSLOPE_KEY` — 이용신청함(승인 대기)
  - [ ] (선택) 경기데이터드림 가입·키
  - [x] 키 적용: 기존 data.go.kr 키(minjoo/election-ops 계정)를 clone `.env`(gitignore)에 연결, `_collect.py` 로더 추가
  - [x] **날씨 수집 성공 — 2°C** (서버 1회 호출, 개발계정 한도 충분)

  - [ ] 인구(행안부 15097972) · 대기질(에어코리아) · 충전소 · 주차장 · 복지시설 · 철도역
- [ ] `_collect.py` — 서버측 수집(키 `DATA_GO_KR_KEY` env), 스냅숏 `data/snapshot/`
- [ ] 합성 데이터 — 통합돌봄·복지 지도/목록 (구조 재현용, "합성" 표기)
- [ ] 행정경계 GeoJSON(읍면동/구) — 지도용

## 3. 구현 (Shiny, app.py)

- [x] 홈 — 위상 값 상자 · 날씨(서버 수집 자리) · 행사 · 물때 · 위상 표 · 공약
- [ ] 지도 — ipyleaflet/folium + 공개 GeoJSON (홈 중앙, 권역 선택)
- [ ] 도시현황 · 교통 · 재난/안전 (1차 범위 D3)
- [ ] 문화/관광 · 행정현황 · 사업관리
- [ ] 바로이웃 통합돌봄 — 합성 데이터로 구조만(D4)
- [ ] 반응형 레이아웃(고정 폭 1920 금지 — 원본 결함 R5)
- [ ] 다크 모드 선택 (D5)

## 실행

```bash
source ~/.venvs/hs-dashboard-clone/bin/activate
python _collect.py          # 서버측 수집(키 있으면). 없으면 '대기'
shiny run app.py --reload   # http://127.0.0.1:8000
```
