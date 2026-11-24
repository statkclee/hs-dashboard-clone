import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
// 다크 테마 기본값
Chart.defaults.color = '#9fb3c8'
Chart.defaults.font.family = '"Pretendard Variable", Pretendard, "Apple SD Gothic Neo", sans-serif'
Chart.defaults.borderColor = 'rgba(255,255,255,.12)'
Chart.defaults.plugins.legend.labels.boxWidth = 12
Chart.defaults.plugins.legend.labels.boxHeight = 12

export { Chart }
