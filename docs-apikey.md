# 인증키 발급·설정 안내 (복제 대시보드용)

복제본은 **인증키를 서버에만** 둔다(hs-dashboard-study 8장). 아래 순서로 발급받아, 저장소가 아니라 **서버 환경변수**에만 넣는다. 수집은 `_collect.py`가 서버에서 돌리고, 화면(`app.py`)은 스냅숏만 읽는다.

흐름: `images/apikey-flow.svg` 참고.

## 0. 원칙 (먼저 읽기)

- 키는 **코드·CSV·커밋에 절대 넣지 않는다.** `.gitignore`에 스냅숏(`data/snapshot/`)이 들어 있다.
- 키는 **환경변수**로만 준다. 예) `export DATA_GO_KR_KEY=...`
- 발급은 **화성시(데이터 소유 주체) 명의** 계정으로 받는 것이 맞다. 개인 키로 운영하면 책임·한도가 개인에게 간다(원본 대시보드가 그랬다).
- 운영계정(활용)으로 신청해 **일/월 한도**를 넉넉히 받는다. 개발계정은 한도가 작다.

## 1. 공공데이터포털 (data.go.kr) — serviceKey 1개

공공데이터포털은 **계정당 인증키 1개**로 모든 API를 쓴다. 가입 후 각 API에서 "활용신청"을 하면 그 키로 호출된다.

| 순서 | 할 일 |
|---|---|
| 1 | data.go.kr 회원가입·로그인 |
| 2 | 마이페이지에서 **인증키(serviceKey)** 확인 (일반 인증키) |
| 3 | 아래 API마다 "활용신청" (개발계정은 즉시, 운영계정은 심사) |
| 4 | 발급된 키를 서버 환경변수 `DATA_GO_KR_KEY`에 설정 |

### 활용신청할 API (복제본이 쓰는 것)

| 데이터 | API (data.go.kr) | 쓰이는 메뉴 | 한도 확인 |
|---|---|---|---|
| 기상청 단기예보 | `apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst` | 홈 날씨 | **일/월 한도 꼭 확인**(원본 429 원인) |
| 에어코리아 대기오염 | [15073861](https://www.data.go.kr/data/15073861/openapi.do) | 홈·재난안전 대기 | 측정소/시도 단위 |
| 에어코리아 측정소정보 | [15073877](https://www.data.go.kr/data/15073877/openapi.do) | 측정소 좌표 | |
| 전기차 충전소 | [15076352](https://www.data.go.kr/data/15076352/openapi.do) | 교통 | |
| 관세청 시군구 수출입 | [15134344](https://www.data.go.kr/data/15134344/openapi.do) | 위상 | |
| 워크넷 채용정보 | [3038225](https://www.data.go.kr/data/3038225/openapi.do) | 민간일자리 | 상업적 이용·변경 금지 |
| 조위관측소 조위 | [15142507](https://www.data.go.kr/data/15142507/openapi.do) | 제부도(근사) | 바다갈라짐 공식 API 없음 |

> 파일(CSV) 데이터(인구·주차장·복지시설·철도역 등)는 키가 아니라 **포털 다운로드**다. 받아서 `data/`에 둔다.

## 1-B. 재난안전데이터공유플랫폼 (safetydata.go.kr) — 별도 키

산사태·붕괴위험은 **data.go.kr가 아니라 safetydata.go.kr**에 있고, 인증키가 data.go.kr와 별개다. 게다가 **서비스(데이터)마다 키를 따로 발급**하므로, 서비스별 환경변수로 나눠 둔다.

| 서비스 | DSSP-IF | 이용신청 | 환경변수 | 쓰임 |
|---|---|---|---|---|
| 산사태우려지역 | `DSSP-IF-10694` | safetydata.go.kr에서 이용신청 | `SAFETY_LANDSLIDE_KEY` | 재난/안전 |
| 붕괴위험지역(급경사지) | (별도 번호) | 〃 | `SAFETY_STEEPSLOPE_KEY` | 재난/안전 |

| 순서 | 할 일 |
|---|---|
| 1 | safetydata.go.kr 회원가입·로그인 |
| 2 | 서비스별로 각각 **이용신청** (산사태·붕괴위험 따로) |
| 3 | 승인 후 **마이페이지 → 오픈API 인증키**에서 그 서비스의 serviceKey 확인 |
| 4 | 서버 환경변수에 서비스별로 설정 — `SAFETY_LANDSLIDE_KEY`, `SAFETY_STEEPSLOPE_KEY` (저장소 밖) |

- 엔드포인트: `https://www.safetydata.go.kr/V2/api/DSSP-IF-10694`(산사태). 붕괴위험은 별도 DSSP-IF 번호.
- 이용허락: 공공누리 제3유형(공공기관 제공 데이터).

## 2. 경기데이터드림 (data.gg.go.kr) — 별도 키

생활인구·유동인구·민간채용 일부는 경기데이터드림에 있다. **별도 회원가입·인증키**가 필요하다. 쓰게 되면 환경변수 `GG_DATA_KEY`로 둔다.

## 3. 네이버 지도 — 이번 복제본은 불필요

원본은 네이버 지도(`ncpKeyId`)를 쓰지만, 복제본은 **Leaflet + 공개 GeoJSON**으로 간다(키 불필요). 네이버를 쓰려면 네이버 클라우드 콘솔에서 Maps 신청 + **웹 서비스 URL(허용 도메인) 제한**을 반드시 설정한다.

## 4. 키를 받은 다음 (설정)

```bash
# 서버에서만. 셸 프로필이나 배포 환경의 Secret에 넣는다. 저장소에는 넣지 않는다.
export DATA_GO_KR_KEY='받은 키'
# 선택
export GG_DATA_KEY='경기데이터드림 키'

# 수집 → 스냅숏
source ~/.venvs/hs-dashboard-clone/bin/activate
python _collect.py            # data/snapshot/weather.json 등 생성
shiny run app.py --reload     # 날씨 칸이 '대기' → 실제 값으로 바뀜
```

키가 설정되면 홈 날씨가 "서버 수집 대기"에서 실제 기온으로 바뀐다. 호출은 `_collect.py`가 **서버에서** 주기적으로(예: cron 매시) 한 번만 하므로, 방문자 수와 무관하고 한도를 건드리지 않는다.

## 확인용 체크리스트

- [ ] data.go.kr 가입, 인증키 확인
- [ ] 위 API 활용신청(운영계정 권장), **단기예보 일/월 한도 확인**
- [ ] 파일 데이터(CSV) 다운로드 → `data/`
- [ ] (선택) 경기데이터드림 가입·키
- [ ] 서버 환경변수 `DATA_GO_KR_KEY` 설정 (저장소 밖)
- [ ] `python _collect.py` → 날씨 스냅숏 생성 확인
