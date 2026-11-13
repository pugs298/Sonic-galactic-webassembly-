#!/usr/bin/env python3
"""Inline the Emscripten SINGLE_FILE output (hatch.js, wasm already base64'd inside)
into the HTML template, producing one self-contained .html file.

usage: pack.py <hatch.js> <out.html> [--data Data.hatch]

--data embeds the game's data pack too. For Sonic Galactic's 255 MB Data.hatch that
yields a ~340 MB page which most browsers will choke on; the default (no --data)
lets the player pick Data.hatch once and caches it in IndexedDB.
"""
import argparse, base64, pathlib, sys

ap = argparse.ArgumentParser()
ap.add_argument("js"); ap.add_argument("out")
ap.add_argument("--data", help="optional Data.hatch to embed (only sensible for small games)")
ap.add_argument("--template", default=str(pathlib.Path(__file__).with_name("index.template.html")))
a = ap.parse_args()

tpl = pathlib.Path(a.template).read_text(encoding="utf-8")
js = pathlib.Path(a.js).read_text(encoding="utf-8")
# Never let the module text terminate the surrounding <script> element.
js = js.replace("</script", "<\\/script").replace("<!--", "<\\!--")

MARK = "/*__HATCH_MODULE_JS__*/"
if MARK not in tpl:
    sys.exit("template is missing the module marker")
html = tpl.replace(MARK, js, 1)

if a.data:
    raw = pathlib.Path(a.data).read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    size_mb = len(b64) / 1048576
    if size_mb > 150:
        print(f"warning: embedded data is {size_mb:.0f} MB of base64; many browsers will fail to open this page", file=sys.stderr)
    embed = '<script>window.__EMBEDDED_DATA_HATCH__="' + b64 + '";</script>\n'
    html = html.replace("</head>", embed + "</head>", 1)

out = pathlib.Path(a.out)
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size/1048576:.1f} MB)")
