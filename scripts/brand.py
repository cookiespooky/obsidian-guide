#!/usr/bin/env python3
"""Картинка для ссылок и значок вкладки — рисуются один раз, результат лежит в репозитории.

    python3 scripts/brand.py      # нужен Pillow; сборке он не нужен

- media/og.png (1200×630) — с ней ссылка на гайд приходит в Telegram и соцсетях с картинкой
  (`default_og_image` в config.yaml);
- theme/assets/favicon.svg и theme/assets/apple-touch-icon.png (180×180) — значок вкладки и экрана телефона.
Цвета — из theme/assets/tokens.css, шрифт — Golos Text из theme/assets/fonts/. Поменяли название гайда — перерисуйте. Оформление — как у курса «Вайбкодинг с нуля».
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "theme/assets/fonts"   # подмножества: в кириллическом нет латиницы и знаков препинания
PAPER, INK, INK_1, MUTED, ACCENT, WHITE = "#f5f6f7", "#1b2128", "#3b424a", "#7c8289", "#3e5368", "#ffffff"


def font(size, weight=600):
    """Пара шрифтов: кириллица и латиница со знаками — text() берёт для каждой буквы свой."""
    pair = []
    for part in ("cyrillic", "latin"):
        f = ImageFont.truetype(str(FONTS / f"golos-text-{part}.woff2"), size)
        try:
            f.set_variation_by_axes([weight])
        except (OSError, AttributeError):
            pass
        pair.append(f)
    return pair


def text(d, xy, s, fonts, fill, anchor="ls"):
    """Строка по буквам: кириллица — первым шрифтом, остальное — вторым."""
    cyr, lat = fonts
    pick = lambda ch: cyr if "\u0400" <= ch <= "\u04ff" else lat
    if anchor == "mm":
        d.text(xy, s, font=pick(s[0]), fill=fill, anchor="mm")
        return
    x, y = xy
    for ch in s:
        f = pick(ch)
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += f.getlength(ch)


def og():
    im = Image.new("RGB", (1200, 630), PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80, 80, 152, 152), 18, fill=ACCENT)
    text(d, (116, 113), "о", font(54, 700), WHITE, anchor="mm")
    text(d, (80, 310), "Гайд по Obsidian", font(92, 650), INK)
    text(d, (80, 390), "Заметки, которые работают вместе с ИИ:", font(38, 400), INK_1)
    text(d, (80, 440), "от первой заметки до своей системы", font(38, 400), INK_1)
    text(d, (80, 550), "antonlozhkin.ru/obsidian-guide", font(30, 400), MUTED)
    im.save(ROOT / "media/og.png", optimize=True)


def icons():
    (ROOT / "theme/assets/favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{ACCENT}"/>'
        f'<text x="32" y="44" text-anchor="middle" font-family="Golos Text, Arial, sans-serif" font-size="44" '
        f'font-weight="700" fill="{WHITE}">о</text></svg>\n', encoding="utf-8")
    im = Image.new("RGB", (180, 180), ACCENT)
    text(ImageDraw.Draw(im), (90, 84), "о", font(128, 700), WHITE, anchor="mm")
    im.save(ROOT / "theme/assets/apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    og()
    icons()
    print("media/og.png, theme/assets/favicon.svg, theme/assets/apple-touch-icon.png")
