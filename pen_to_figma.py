"""pen -> figma-plugin-data converter.
Reads kasir-pos.pen (schema v2.19 subset we generate) and emits
figma-plugin/pen-data.js : `const PEN = {...}` consumed by code.js.
Keeps ALL screens/components/variables/text content; drops x/y inside
auto-layout parents (Figma ignores them the same way pen does).
"""
import json, pathlib

SRC = pathlib.Path(__file__).with_name("kasir-pos.pen")
PLUGDIR = pathlib.Path(__file__).parent / "figma-plugin"
DST_DATA = PLUGDIR / "pen-data.js"
TEMPLATE = PLUGDIR / "code.template.js"
DST_CODE = PLUGDIR / "code.js"

d = json.loads(SRC.read_text())
kids = d.get("children", [])

# resolve variable refs like "$c.pri" -> hex via variables map
varmap = {k: v.get("value") for k, v in d.get("variables", {}).items()}

def col(v):
    if not v:
        return None
    if isinstance(v, str) and v.startswith("$"):
        return varmap.get(v[1:], v)
    return v

def conv(n):
    t = n.get("type")
    o = {"type": t, "name": n.get("name", t)}
    if t == "frame":
        o.update({
            "w": n.get("width"), "h": n.get("height"),
            "fill": col(n.get("fill")),
            "radius": n.get("cornerRadius", 0),
            "stroke": col(n.get("stroke")),
            "layout": n.get("layout"),
            "gap": n.get("gap"), "padding": n.get("padding"),
            "justify": n.get("justifyContent"), "align": n.get("alignItems"),
            "children": [conv(c) for c in n.get("children", [])],
        })
        if n.get("reusable"):
            o["component"] = True
    elif t == "rectangle":
        o.update({
            "w": n.get("width"), "h": n.get("height"),
            "fill": col(n.get("fill")),
            "radius": n.get("cornerRadius", 0),
            "stroke": col(n.get("stroke")),
        })
    elif t == "text":
        o.update({
            "content": n.get("content", ""),
            "size": n.get("fontSize", 14),
            "fill": col(n.get("fill")),
            "align": n.get("textAlign", "left"),
            "weight": str(n.get("fontWeight", "400")),
            "w": n.get("width"),
        })
    elif t == "ref":
        o.update({"ref": n.get("ref"), "desc": n.get("descendants", {}) or {}})
    return o

# component id -> name map for refs
comp_names = {n.get("id"): n.get("name") for n in kids
              if n.get("type") == "frame" and n.get("reusable")}

screens, comps = [], []
for n in kids:
    nm = n.get("name", "")
    if n.get("type") == "text" and nm.startswith("ArtLabel"):
        continue  # pen-only artboard labels, skip in figma
    if n.get("type") == "frame" and (n.get("reusable") or nm.startswith("Cmp ")):
        comps.append(conv(n))
    elif n.get("type") == "frame" and nm[:2].isdigit():
        s = conv(n)
        s["x"], s["y"] = n.get("x", 0), n.get("y", 0)
        screens.append(s)

out = {"vars": varmap, "compNames": comp_names,
       "components": comps, "screens": screens}
PLUGDIR.mkdir(exist_ok=True)
data_js = "const PEN = " + json.dumps(out, ensure_ascii=False) + ";\n"
DST_DATA.write_text(data_js, encoding="utf-8")
# Figma loads ONLY manifest.main (single file) — bundle data + template.
tpl = TEMPLATE.read_text(encoding="utf-8")
DST_CODE.write_text(data_js + tpl, encoding="utf-8")
print(f"screens={len(screens)} comps={len(comps)} vars={len(varmap)} -> {DST_CODE}")
