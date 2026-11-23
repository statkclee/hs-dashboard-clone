// 데이터 레이어 — 프론트는 '스냅숏만' 읽는다. 인증키는 서버(_collect.py)에만 있고
// 브라우저로 전송되지 않는다(원본의 키 노출·429 문제를 구조적으로 제거).
import Papa from 'papaparse'

const BASE = import.meta.env.BASE_URL || './'
const dataUrl = (p) => `${BASE}data/${p}`.replace(/\/\/+/g, '/')

export async function loadJSON(name) {
  try {
    const r = await fetch(dataUrl(`snapshot/${name}.json`))
    if (!r.ok) return { status: 'pending' }
    return await r.json()
  } catch (e) {
    return { status: 'error', reason: String(e) }
  }
}

export async function loadCSV(name) {
  try {
    const r = await fetch(dataUrl(name))
    if (!r.ok) return []
    const text = await r.text()
    const out = Papa.parse(text.trim(), { header: true, skipEmptyLines: true })
    return out.data
  } catch (e) {
    return []
  }
}

export async function loadGeo(name) {
  try {
    const r = await fetch(dataUrl(`geo/${name}`))
    if (!r.ok) return null
    return await r.json()
  } catch (e) {
    return null
  }
}

export const num = (v) => {
  const n = parseFloat(v)
  return Number.isNaN(n) ? null : n
}

export const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString('ko-KR'))

// 대기 등급(환경부 통합): [등급, 색, 이모지]
export function airGrade(kind, v) {
  const n = num(v)
  if (n == null) return ['—', '#9fb3c8', '·']
  const cuts = { pm10: [30, 80, 150], pm25: [15, 35, 75], o3: [0.03, 0.09, 0.15] }[kind]
  const labels = ['좋음', '보통', '나쁨', '매우나쁨']
  // 한국 대기질 표준 색: 좋음=파랑 · 보통=초록 · 나쁨=노랑 · 매우나쁨=빨강
  const cols = ['#1c75d6', '#2fa84f', '#f5a623', '#e53935']
  const emo = ['🙂', '😐', '😷', '😫']
  const i = cuts.reduce((a, c) => a + (n > c ? 1 : 0), 0)
  return [labels[i], cols[i], emo[i], i]
}

export const SKY = { 1: '맑음', 3: '구름많음', 4: '흐림' }
export const PTY = { 0: '없음', 1: '비', 2: '비/눈', 3: '눈', 4: '소나기' }
