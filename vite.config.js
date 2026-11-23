import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 복제본 프론트(Vue 3). base './' 로 정적 배포 호환.
// public/data -> ../data 심링크로 snapshot/CSV/geojson 을 /data/ 에서 읽는다(키 없음).
export default defineConfig({
  base: './',
  plugins: [vue()],
  server: { host: '127.0.0.1', port: 5173, strictPort: false, fs: { allow: ['..'] } },
})
