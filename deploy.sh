#!/usr/bin/env bash
# 로컬 빌드 → gh-pages 배포 (정적 SPA, data/ 전부 포함).
# 공개 URL: https://statkclee.github.io/hs-dashboard-clone/
# 사용: ./deploy.sh   (npm 빌드 후 dist/를 gh-pages 브랜치로 강제 푸시)
set -euo pipefail
cd "$(dirname "$0")"
REMOTE="git@github.com:statkclee/hs-dashboard-clone.git"

echo "▶ 빌드"
npm run build

TMP="$(mktemp -d)"
cp -R dist/. "$TMP"/
cd "$TMP"
touch .nojekyll                       # Vite assets 폴더 Jekyll 처리 방지
git init -q
git checkout -q -b gh-pages
git add -A
git -c user.name="statkclee" -c user.email="kwangchun.lee.7@gmail.com" \
    commit -q -m "deploy $(date +%F' '%H:%M)"
git push -q -f "$REMOTE" gh-pages
cd - >/dev/null
rm -rf "$TMP"
echo "✔ 배포 완료 → https://statkclee.github.io/hs-dashboard-clone/"
