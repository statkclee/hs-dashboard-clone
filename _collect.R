# _collect.R — 서버측 수집 (hs-dashboard-study 8장 해법 D2)
#   인증키는 환경변수에서만 읽고, 받은 값은 data/snapshot/ 에 저장한다.
#   브라우저로 키를 보내지 않는다. 대시보드 화면은 이 스냅숏만 읽는다.
#
#   실행(서버 cron, 예: 매시 정각):  Rscript _collect.R
#   키 설정(서버에서만):             export DATA_GO_KR_KEY=...   # 저장소에 넣지 않는다
#
# 인증키가 없으면 수집을 건너뛰고 화면은 "서버 수집 대기"로 표시된다(안전한 기본값).

suppressPackageStartupMessages({ library(jsonlite) })

dir.create("data/snapshot", showWarnings = FALSE, recursive = TRUE)
key <- Sys.getenv("DATA_GO_KR_KEY", "")
now <- format(Sys.time(), "%Y-%m-%d %H:%M:%S")

save_snapshot <- function(name, value) {
  writeLines(toJSON(c(value, list(collectedAt = now)), auto_unbox = TRUE),
             file.path("data/snapshot", paste0(name, ".json")))
}

if (!nzchar(key)) {
  message("DATA_GO_KR_KEY 없음 — 수집 건너뜀. 화면은 '서버 수집 대기'로 표시됨.")
  save_snapshot("weather", list(status = "pending", reason = "no key on server"))
} else {
  # 기상청 단기예보 — 서버에서만 호출. 키는 로그·응답에 남기지 않는다.
  base <- "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
  q <- list(serviceKey = key, dataType = "JSON", numOfRows = 1000, pageNo = 1,
            base_date = format(Sys.Date(), "%Y%m%d"), base_time = "0500", nx = 57, ny = 119)
  url <- paste0(base, "?", paste(names(q), vapply(q, URLencode, "", reserved = TRUE), sep = "=", collapse = "&"))
  res <- tryCatch(fromJSON(url), error = function(e) NULL)
  temp <- tryCatch({
    it <- res$response$body$items$item
    as.numeric(it$fcstValue[it$category == "TMP"][1])
  }, error = function(e) NA_real_)
  save_snapshot("weather", list(status = if (is.na(temp)) "error" else "ok", tempC = temp))
  message(sprintf("weather 수집: %s", if (is.na(temp)) "실패(429 등)" else paste0(temp, "°C")))
}
