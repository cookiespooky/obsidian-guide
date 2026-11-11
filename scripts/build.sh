#!/usr/bin/env bash
# Сборка гайда -> dist/. Ничего не коммитит и не публикует. Устроена как у курса «Вайбкодинг с нуля».
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

NOTEPUB_REF="${NOTEPUB_REF:-8ef36a58c94dca5bd7f3f696c05a9201cd140d47}"
NOTEPUB_BIN="${NOTEPUB_BIN:-}"
if [[ -z "$NOTEPUB_BIN" ]]; then
  if [[ -x "$ROOT_DIR/.bin/notepub" ]]; then NOTEPUB_BIN="$ROOT_DIR/.bin/notepub"
  elif command -v notepub >/dev/null 2>&1; then NOTEPUB_BIN="$(command -v notepub)"
  else
    command -v go >/dev/null 2>&1 || { echo "Ошибка: не найден notepub и не установлен Go." >&2; exit 1; }
    mkdir -p "$ROOT_DIR/.bin"
    GOBIN="$ROOT_DIR/.bin" go install "github.com/cookiespooky/notepub/cmd/notepub@${NOTEPUB_REF}"
    NOTEPUB_BIN="$ROOT_DIR/.bin/notepub"
  fi
fi

CONFIG="${CONFIG:-./config.yaml}"; DIST="${DIST:-./dist}"
# Метки вместо ссылок на lava.top (LAVA_FREE_URL, LAVA_MEMORY_URL в lifeos-templates.md): с ними кнопки ведут в никуда —
# сборку для выкладки не пускать. Посмотреть у себя: ALLOW_PLACEHOLDERS=1.
if grep -rl 'LAVA_[A-Z_]*URL' ./obsidian-guide >/dev/null && [[ -z "${ALLOW_PLACEHOLDERS:-}" ]]; then
  echo "Ошибка: в тексте остались метки ссылок lava.top:" >&2; grep -rn 'LAVA_[A-Z_]*URL' ./obsidian-guide >&2; exit 1
fi
echo "Сайт ($CONFIG -> $DIST)"
rm -rf "$DIST" .notepub
mkdir -p "$DIST"
"$NOTEPUB_BIN" validate --config "$CONFIG" --rules ./rules.yaml
"$NOTEPUB_BIN" index --config "$CONFIG" --rules ./rules.yaml
"$NOTEPUB_BIN" validate --config "$CONFIG" --rules ./rules.yaml --resolve ./.notepub/artifacts/resolve.json --links --markdown
"$NOTEPUB_BIN" build --config "$CONFIG" --rules ./rules.yaml --dist "$DIST" --artifacts ./.notepub/artifacts
# картинки из заметок (obsidian-guide/**, кроме .md) и картинка для ссылок (media/og.png) — в dist/media/
mkdir -p "$DIST/media"
rsync -a --prune-empty-dirs --exclude '.obsidian/' --exclude '*.md' ./obsidian-guide/ "$DIST/media/"
[[ -d media ]] && cp -R media/. "$DIST/media/"
BASE_URL="$(sed -n 's/^  base_url: *"\{0,1\}\([^"]*\)"\{0,1\} *$/\1/p' "$CONFIG" | head -1)"
python3 scripts/postbuild.py "$DIST" "$BASE_URL"
touch "$DIST/.nojekyll"
echo "Готово: $DIST — не закоммичено и не опубликовано"
