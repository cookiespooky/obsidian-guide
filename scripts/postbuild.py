#!/usr/bin/env python3
"""Доводка собранного сайта под поиск — после движка, в конце scripts/build.sh. Без пакетов.

    python3 scripts/postbuild.py <dist> <base_url>

1. Слэш в конце внутренних ссылок. Вики-ссылки движок пишет без него (`…/chto-takoe-vs-code`), а GitHub Pages
   отвечает на такой адрес редиректом 301 на `…/chto-takoe-vs-code/` — лишний переход на каждой ссылке.
2. Размеры у снимков: `width` и `height` из самого файла, чтобы текст не прыгал, пока картинка грузится;
   `loading="lazy"` — у всех, кроме первой на странице (её браузер должен грузить сразу).
3. llms.txt — карта гайда для языковых моделей (формат llmstxt.org): адреса из карты сайта, названия и
   описания — из самих страниц, ступени — из надписи «Ступень N» над заголовком, порядок — как в дереве.
"""
import html
import re
import struct
import sys
from pathlib import Path
from urllib.parse import urlparse

DIST = Path(sys.argv[1])
BASE = sys.argv[2].rstrip("/")
BASE_PATH = urlparse(BASE).path


def image_size(f):
    """(ширина, высота) PNG или JPEG — по заголовку файла."""
    data = f.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def local_file(src):
    """Файл в dist/ по адресу картинки, если она своя."""
    if not src.startswith(BASE + "/"):
        return None
    f = DIST / src[len(BASE) + 1:]
    return f if f.is_file() else None


LINK = re.compile(r'href="(' + re.escape(BASE) + r'(?:/[^"#?]*)?)([#?][^"]*)?"')
IMG = re.compile(r"<img\b[^>]*>")


def slash(m):
    url, tail = m.group(1), m.group(2) or ""
    last = url[len(BASE):].rsplit("/", 1)[-1]
    if not url.endswith("/") and "." not in last:
        url += "/"
    return f'href="{url}{tail}"'


def sizes(text):
    first = [True]

    def one(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        f = local_file(src.group(1)) if src else None
        add = ""
        if f and "width=" not in tag:
            wh = image_size(f)
            if wh:
                add += f' width="{wh[0]}" height="{wh[1]}"'
        if not first[0] and "loading=" not in tag:
            add += ' loading="lazy" decoding="async"'
        first[0] = False
        return tag[:-1].rstrip("/").rstrip() + add + ">" if add else tag

    return IMG.sub(one, text)


def page_info(url):
    path = urlparse(url).path[len(BASE_PATH):] or "/"
    f = DIST / path.strip("/") / "index.html" if path.strip("/") else DIST / "index.html"
    text = f.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)"', text, re.S)
    step = re.search(r'<p class="eyebrow">Ступень (\d+)', text)
    return dict(url=url, path=path, title=html.unescape(title.group(1).strip()) if title else path,
                desc=html.unescape(desc.group(1).strip()) if desc else "", step=int(step.group(1)) if step else None)


def llms():
    urls = []
    for sm in sorted(DIST.glob("sitemap-0*.xml")):
        urls += re.findall(r"<loc>(.*?)</loc>", sm.read_text(encoding="utf-8"))
    pages = [page_info(u) for u in urls]
    home = next((p for p in pages if p["path"] == "/"), None)
    side = (DIST / "index.html").read_text(encoding="utf-8")
    names = dict(re.findall(r'<span class="side__num">(\d+)</span>([^<]+)</p>', side))
    nav = side.split('<nav class="side__nav"', 1)[-1].split("</nav>", 1)[0]
    order = {u.rstrip("/") + "/": i for i, u in enumerate(re.findall(r'href="([^"]+)"', nav))}
    pages.sort(key=lambda p: order.get(p["url"], len(order)))   # как в дереве меню
    out = [f"# {home['title'] if home else 'Гайд по Obsidian'}", ""]
    if home and home["desc"]:
        out += [f"> {home['desc']}", ""]
    for n in sorted({p["step"] for p in pages if p["step"]}):
        out += [f"## Ступень {n}. {names.get(str(n), '').strip()}".rstrip(". "), ""]
        out += [f"- [{p['title']}]({p['url']}){': ' + p['desc'] if p['desc'] else ''}" for p in pages if p["step"] == n]
        out.append("")
    rest = [p for p in pages if not p["step"] and p["path"] != "/"]
    if rest:
        out += ["## Страницы", ""] + [f"- [{p['title']}]({p['url']}){': ' + p['desc'] if p['desc'] else ''}" for p in rest] + [""]
    (DIST / "llms.txt").write_text("\n".join(out), encoding="utf-8")
    return len(pages)


def main():
    changed = 0
    for f in DIST.rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        new = sizes(LINK.sub(slash, text))
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed += 1
    n = llms()
    print(f"доводка: страниц поправлено {changed}, в llms.txt — {n}")


if __name__ == "__main__":
    main()
