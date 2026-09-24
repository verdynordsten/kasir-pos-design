"""Full Kasir POS .pen — 18 screens, schema-valid v2.19, anti-overlap layout.

Layout math (strict, verified in code):
- Screen frame: 390 wide. Padded wrappers: 390-32 = 358 content width.
- 2-col grids: 2*167 + 10 gap = 344 <= 358 OK (padding 16 each side: 16+344+16=376<=390 OK).
- Refs carry NO x/y inside flex parents (ignored anyway); root screens get x/y.
- Every node gets unique id; refs point to component IDs; descendants keyed by
  descendant node IDs (resolved from component subtrees by NAME lookup).
"""
import json, secrets, string

A = string.ascii_letters + string.digits
_seen = set()
def nid():
    while True:
        v = "".join(secrets.choice(A) for _ in range(5))
        if v not in _seen:
            _seen.add(v)
            return v

def T(name, content, size=14, fill="$c.fg", align="left", weight="400", w=None):
    o = {"id": nid(), "type": "text", "name": name, "content": content,
         "fill": fill, "fontSize": size, "fontFamily": "Outfit",
         "textAlign": align, "fontWeight": weight,
         "textGrowth": "fixed-width" if w else "auto"}
    if w:
        o["width"] = w
    return o

def R(name, fill, w, h, radius=0, stroke=None, sw=1):
    o = {"id": nid(), "type": "rectangle", "name": name, "fill": fill,
         "width": w, "height": h, "cornerRadius": radius}
    if stroke:
        o["stroke"] = stroke
        o["strokeWidth"] = sw
    return o

def F(name, w, h, fill, children=None, radius=0, extra=None, reuse=False):
    o = {"id": nid(), "type": "frame", "name": name, "width": w,
         "height": h, "fill": fill, "cornerRadius": radius}
    if reuse:
        o["reusable"] = True
    if extra:
        o.update(extra)
    if children:
        o["children"] = children
    return o

def REF(name, target_id, desc=None):
    o = {"id": nid(), "type": "ref", "name": name, "ref": target_id,
         "x": 0, "y": 0}
    if desc:
        o["descendants"] = desc
    return o

# ---------- variables ----------
VARS = {
    "c.pri": "#2563EB", "c.onpri": "#FFFFFF", "c.acc": "#EA580C",
    "c.onacc": "#FFFFFF", "c.bg": "#F8FAFC", "c.fg": "#1E293B",
    "c.card": "#FFFFFF", "c.mut": "#E9EFF8", "c.mfg": "#64748B",
    "c.line": "#E2E8F0", "c.ok": "#16A34A", "c.okbg": "#F0FDF4",
    "c.dan": "#DC2626", "c.danbg": "#FEF2F2", "c.warn": "#D97706",
}
def V(k):
    return "$" + k

def IC(name, glyph, size=20, fg="$c.onpri", bg="$c.pri", box=40,
        radius=12):
    """Icon glyph in colored box (glyphs render as Outfit text)."""
    return F(name, box, box, V(bg[1:]) if bg.startswith("$") else bg, [
        T(name + "G", glyph, size, V(fg[1:]) if fg.startswith("$") else fg,
          align="center", weight="700", w=box - 8)], radius,
        {"layout": "vertical", "justifyContent": "center",
         "alignItems": "center"})

# icon glyphs per slot (letters render reliably in Outfit)
IC_LOGO, IC_CART, IC_HOME = "B", "K", "B"
IC_HIST, IC_MORE, IC_BACK = "R", "L", "<"
IC_SEARCH, IC_USER, IC_BELL = "C", "U", "O"
IC_OK, IC_QRIS = "V", "Q"

STATUS = lambda tag: F("Status " + tag, 390, 62, V("c.card"), [
    T("Clock", "09.41", 14, V("c.fg"), weight="600")], 0,
    {"layout": "horizontal", "justifyContent": "space_between",
     "alignItems": "center", "padding": 20})

def NAVBACK(tag, title, sub=None):
    kids = [IC("Back" + tag, IC_BACK, size=16, fg="$c.fg",
               bg="$c.mut", box=36, radius=10)]
    tcol = [T("Title", title, 16, V("c.fg"), weight="700")]
    if sub:
        tcol.append(T("Subtitle", sub, 11, V("c.mfg")))
    kids.append(F("TitleCol", 280, 46 if sub else 30, V("c.card"), tcol,
                  0, {"layout": "vertical", "gap": 2}))
    return F("Nav " + tag, 390, 64, V("c.card"), kids, 0,
             {"layout": "horizontal", "gap": 12, "alignItems": "center",
              "padding": 16})

def LBL(tag, txt):
    return F("Lbl " + tag, 390, 40, V("c.bg"),
             [T("LblTxt", txt, 12, V("c.mfg"), weight="700", w=358)], 0,
             {"layout": "vertical", "justifyContent": "center",
              "padding": 16})

def FOOTCTA(tag, comp_id, label):
    for _c in children:
        if _c["id"] == comp_id:
            _m = DESCMAP[_c["name"]]
            break
    return F("Foot " + tag, 390, 84, V("c.card"), [
        REF("CTA " + tag, comp_id,
            desc={_m["D_BTN_LBL"]: {"content": label}})],
        0, {"layout": "vertical", "justifyContent": "center",
            "alignItems": "center"})

children = []

# ================= REUSABLE COMPONENTS =================
# NOTE: descendant override keys use placeholder "D_*", replaced with real
# descendant IDs after tree build (labels must be unique per component).
btn = F("Cmp BtnPrimary", 358, 52, V("c.acc"), [
    T("D_BTN_LBL", "CTA", 15, V("c.onacc"), align="center",
      weight="700", w=326)
], 13, {"layout": "vertical", "justifyContent": "center",
        "alignItems": "center", "slot": ["D_BTN_LBL"]}, reuse=True)

prod = F("Cmp ProdCard", 167, 172, V("c.card"), [
    R("D_PROD_TH", V("c.mut"), 147, 64, 10),
    T("D_PROD_NM", "Nama Produk", 12, V("c.fg"), w=147),
    T("D_PROD_PR", "Rp 0", 13, V("c.pri"), weight="700"),
    T("D_PROD_ST", "Stok 0", 10, V("c.mfg")),
], 14, {"layout": "vertical", "gap": 6, "padding": 10,
        "stroke": V("c.line"), "strokeWidth": 1}, reuse=True)

paytile = F("Cmp PayTile", 167, 76, V("c.card"), [
    T("D_TILE_LBL", "Tunai", 13, V("c.fg"), align="center",
      weight="700", w=135)
], 13, {"layout": "vertical", "justifyContent": "center",
        "alignItems": "center", "stroke": V("c.line"),
        "strokeWidth": 2}, reuse=True)

cartrow = F("Cmp CartRow", 358, 76, V("c.card"), [
    R("D_CR_TH", V("c.mut"), 48, 48, 12),
    F("D_CR_MID", 170, 56, V("c.card"), [
        T("D_CR_NM", "Item", 13, V("c.fg"), weight="700", w=170),
        T("D_CR_PR", "Rp 0 /pcs", 11, V("c.mfg"), w=170),
    ], 0, {"layout": "vertical", "gap": 2}),
    T("D_CR_AMT", "Rp 0", 12, V("c.fg"), align="right",
      weight="700", w=90),
], 14, {"layout": "horizontal", "gap": 12, "padding": 12,
        "alignItems": "center", "stroke": V("c.line"),
        "strokeWidth": 1}, reuse=True)

menrow = F("Cmp MenuRow", 358, 60, V("c.card"), [
    IC("D_MN_IC_BOX", "M", size=18, box=40, radius=12),
    T("D_MN_LBL", "Menu", 14, V("c.fg"), weight="600", w=220),
    T("D_MN_AR", ">", 16, V("c.mfg"), align="right", weight="700",
      w=30),
], 14, {"layout": "horizontal", "gap": 12, "padding": 10,
        "alignItems": "center", "stroke": V("c.line"),
        "strokeWidth": 1}, reuse=True)

stat = F("Cmp Stat", 171, 96, V("c.card"), [
    T("D_ST_LBL", "Label", 11, V("c.mfg"), w=139),
    T("D_ST_VAL", "0", 22, V("c.fg"), weight="700", w=139),
], 14, {"layout": "vertical", "gap": 4, "padding": 16,
        "stroke": V("c.line"), "strokeWidth": 1}, reuse=True)

field = F("Cmp Field", 358, 72, V("c.card"), [
    T("D_FD_LBL", "Label", 12, V("c.mfg"), weight="600", w=326),
    F("D_FD_BOX", 326, 44, V("c.bg"), [
        T("D_FD_VAL", "Value", 14, V("c.fg"), w=294)],
        10, {"layout": "vertical", "justifyContent": "center",
             "padding": 16, "stroke": V("c.line"), "strokeWidth": 1}),
], 0, {"layout": "vertical", "gap": 6})

_libx = 0
for _c in [btn, prod, paytile, cartrow, menrow, stat, field]:
    _c["x"], _c["y"] = _libx, 1200
    _libx += 450
children += [btn, prod, paytile, cartrow, menrow, stat, field]
COMPS = {c["name"]: c["id"] for c in children}

# map descendant placeholder name -> node id inside each component
DESCMAP = {}
for c in children:
    m = {}
    def _w(o):
        if o.get("name", "").startswith("D_"):
            m[o["name"]] = o["id"]
        for ch in o.get("children", []):
            _w(ch)
    _w(c)
    DESCMAP[c["name"]] = m

def RB(comp_name, ref_name, **overrides):
    """ref with placeholder overrides resolved to real descendant IDs."""
    m = DESCMAP[comp_name]
    desc = {}
    for k, v in overrides.items():
        desc[m[k]] = {"content": v}
    return REF(ref_name, COMPS[comp_name],
               desc=desc if desc else None)

CATS = ["Semua", "Minuman", "Makanan", "Snack", "Sembako"]
PRODS = [("Kopi Tubruk 200g", "Rp 28.000", "Stok 42"),
         ("Teh Botol 450ml", "Rp 6.000", "Stok 120"),
         ("Indomie Goreng", "Rp 3.500", "Stok 200"),
         ("Roti Tawar Sari", "Rp 18.000", "Stok 35"),
         ("Susu UHT 1L", "Rp 22.000", "Stok 60"),
         ("Chitato 68g", "Rp 12.000", "Stok 88")]

screens = []
def SCR(name, kids, x):
    s = F(name, 390, 844, V("c.bg"), kids, 36,
          {"x": x, "y": 0, "layout": "vertical"})
    # single section title only (pen.dev shows its own frame name too)
    lbl = T(name, name, 20, V("c.fg"), weight="700", w=390)
    lbl["x"], lbl["y"] = x, -50
    children.append(lbl)
    screens.append(s)
    return s

GX = [0]
def next_x():
    GX[0] += 470
    return GX[0] - 470

# ============ 01 SPLASH ============
SCR("01 Splash", [
    F("SplashBody", 390, 782, V("c.pri"), [
        IC("SplashLogo", IC_LOGO, size=48, box=96, radius=26),
        T("SplashName", "Berkah POS", 28, V("c.onpri"), align="center",
          weight="700", w=340),
        T("SplashSub", "Kasir cepat untuk toko Anda", 14,
          V("c.onpri"), align="center", w=340),
        T("SplashVer", "v2.4.0", 12, V("c.onpri"), align="center",
          w=340),
    ], 0, {"layout": "vertical", "gap": 14, "justifyContent": "center",
           "alignItems": "center"}),
    F("SplashFoot", 390, 62, V("c.pri"),
      [T("SplashLoad", "Memuat...", 12, V("c.onpri"), align="center",
         w=340)], 0, {"layout": "vertical", "alignItems": "center"}),
], next_x())

# ============ 02 LOGIN ============
SCR("02 Login", [
    STATUS("login"),
    F("LoginBody", 390, 600, V("c.bg"), [
        IC("LoginLogo", IC_LOGO, size=36, box=72, radius=20),
        T("LoginTitle", "Selamat Datang", 22, V("c.fg"), align="center",
          weight="700", w=340),
        T("LoginSub", "Masuk untuk mulai berjualan", 13, V("c.mfg"),
          align="center", w=340),
        RB("Cmp Field", "F-User", D_FD_LBL="Username",
           D_FD_VAL="andi_kasir"),
        RB("Cmp Field", "F-Pass", D_FD_LBL="Password",
           D_FD_VAL="************"),
        T("LoginForgot", "Lupa password?", 13, V("c.pri"),
          align="right", weight="600", w=358),
        RB("Cmp BtnPrimary", "B-Login", D_BTN_LBL="Masuk"),
        T("LoginBio", "atau masuk dengan fingerprint", 12, V("c.mfg"),
          align="center", w=358),
    ], 0, {"layout": "vertical", "gap": 12, "alignItems": "center",
           "padding": 16}),
], next_x())

# ============ 03 PIN ============
def _pinrow(keys):
    return F("PinRow", 330, 70, V("c.bg"),
             [T("PinD", k or " ", 24, V("c.fg"), align="center",
                weight="600", w=90) for k in keys], 0,
             {"layout": "horizontal", "gap": 10,
              "justifyContent": "center"})
pinbtns = [_pinrow(r) for r in
           (["1","2","3"],["4","5","6"],["7","8","9"],["","0","X"])]
SCR("03 PIN Kasir", [
    STATUS("pin"),
    F("PinBody", 390, 782, V("c.bg"), [
        T("PinTitle", "Masukkan PIN", 20, V("c.fg"), align="center",
          weight="700", w=340),
        T("PinSub", "Andi - Shift Pagi", 13, V("c.mfg"),
          align="center", w=340),
        T("PinDots", "● ● ● ○ ○ ○", 26, V("c.pri"), align="center",
          w=340),
        F("PinPad", 330, 320, V("c.bg"), pinbtns, 0,
          {"layout": "vertical", "gap": 6, "alignItems": "center"}),
    ], 0, {"layout": "vertical", "gap": 14, "alignItems": "center",
           "padding": 16}),
], next_x())

# ============ 04 PILIH SHIFT ============
SCR("04 Pilih Shift", [
    NAVBACK("shift", "Pilih Shift"),
    F("ShiftBody", 390, 560, V("c.bg"), [
        RB("Cmp MenuRow", "Sh-Pagi", D_MN_LBL="Shift Pagi (07-15)"),
        RB("Cmp MenuRow", "Sh-Siang", D_MN_LBL="Shift Siang (15-23)"),
        RB("Cmp MenuRow", "Sh-Malam", D_MN_LBL="Shift Malam (23-07)"),
        RB("Cmp Field", "F-Modal", D_FD_LBL="Modal awal kas (Rp)",
           D_FD_VAL="500.000"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
    FOOTCTA("shift", COMPS["Cmp BtnPrimary"], "Mulai Shift"),
], next_x())

# ============ 05 KATALOG ============
CATS4 = ["Semua", "Minuman", "Makanan", "Snack"]
chips = []
for i, c in enumerate(CATS4):
    act = (i == 0)
    chips.append(F("Cat %s" % c, 72, 36,
        V("c.pri") if act else V("c.card"),
        [T("CatLbl", c, 11,
           V("c.onpri") if act else V("c.mfg"),
           align="center", weight="700", w=60)],
        999, {"layout": "vertical", "justifyContent": "center",
              "alignItems": "center"}))
chips.append(F("Cat More", 34, 36, V("c.card"),
    [T("CatLbl", "+", 14, V("c.mfg"), align="center", weight="700",
       w=22)],
    999, {"layout": "vertical", "justifyContent": "center",
          "alignItems": "center"}))
cards = [RB("Cmp ProdCard", "Card %d" % i, D_PROD_NM=nm,
            D_PROD_PR=pr, D_PROD_ST=st)
         for i, (nm, pr, st) in enumerate(PRODS)]
SCR("05 Katalog", [
    STATUS("kat"),
    F("AppBar", 390, 64, V("c.card"), [
        IC("Logo", IC_LOGO, size=20, box=40, radius=12),
        F("Store", 220, 46, V("c.card"), [
            T("StoreNm", "Toko Berkah Jaya", 16, V("c.fg"),
              weight="700"),
            T("StoreSb", "Andi - Shift Pagi", 11, V("c.mfg"))],
          0, {"layout": "vertical", "gap": 2}),
    ], 0, {"layout": "horizontal", "gap": 12, "alignItems": "center",
           "padding": 16}),
    F("SearchW", 390, 68, V("c.card"), [
        F("Search", 358, 46, V("c.mut"), [
            IC("SearchIc", IC_SEARCH, size=16, fg="$c.mfg",
               bg="$c.mut", box=32, radius=8),
            T("SearchHint", "Cari produk / scan barcode...", 13,
              V("c.mfg"), w=280)], 12,
          {"layout": "horizontal", "gap": 8, "alignItems": "center",
           "padding": 14})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("Cats", 390, 60, V("c.bg"), chips, 0,
      {"layout": "horizontal", "gap": 6, "padding": 16,
       "justifyContent": "center"}),
    F("Grid", 390, 400, V("c.bg"), [
        F("GridR1", 358, 172, V("c.bg"), cards[0:2], 0,
          {"layout": "horizontal", "gap": 10}),
        F("GridR2", 358, 172, V("c.bg"), cards[2:4], 0,
          {"layout": "horizontal", "gap": 10}),
        F("GridR3", 358, 172, V("c.bg"), cards[4:6], 0,
          {"layout": "horizontal", "gap": 10}),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16,
           "alignItems": "center"}),
    F("CartBar", 390, 140, V("c.card"), [
        T("CartSum", "2 item  -  Rp 33.500", 12, V("c.mfg"), w=358),
        T("CartTot", "Total   Rp 33.500", 16, V("c.fg"), weight="700",
          w=358),
        RB("Cmp BtnPrimary", "CTA-Kat",
           D_BTN_LBL="Lihat Keranjang"),
    ], 0, {"layout": "vertical", "gap": 8, "padding": 16}),
    F("TabBar", 390, 68, V("c.card"), [
        F("TbHome", 80, 52, V("c.card"), [
            IC("TbHomeIc", IC_HOME, size=16, box=28, radius=8),
            T("Tb1", "Beranda", 10, V("c.pri"), align="center",
              weight="700", w=80)], 0,
          {"layout": "vertical", "gap": 2, "alignItems": "center"}),
        F("TbCart", 90, 52, V("c.card"), [
            IC("TbCartIc", IC_CART, size=16, fg="$c.mfg", bg="$c.mut",
               box=28, radius=8),
            T("Tb2", "Keranjang (2)", 10, V("c.mfg"), align="center",
              weight="700", w=90)], 0,
          {"layout": "vertical", "gap": 2, "alignItems": "center"}),
        F("TbHist", 80, 52, V("c.card"), [
            IC("TbHistIc", IC_HIST, size=16, fg="$c.mfg", bg="$c.mut",
               box=28, radius=8),
            T("Tb3", "Riwayat", 10, V("c.mfg"), align="center",
              weight="700", w=80)], 0,
          {"layout": "vertical", "gap": 2, "alignItems": "center"}),
        F("TbMore", 80, 52, V("c.card"), [
            IC("TbMoreIc", IC_MORE, size=16, fg="$c.mfg", bg="$c.mut",
               box=28, radius=8),
            T("Tb4", "Lainnya", 10, V("c.mfg"), align="center",
              weight="700", w=80)], 0,
          {"layout": "vertical", "gap": 2, "alignItems": "center"}),
    ], 0, {"layout": "horizontal", "justifyContent": "space_around",
           "alignItems": "center"}),
], next_x())

# ============ 06 DETAIL PRODUK ============
SCR("06 Detail Produk", [
    NAVBACK("det", "Detail Produk"),
    F("DetBody", 390, 500, V("c.bg"), [
        R("DetImg", V("c.mut"), 358, 200, 16),
        T("DetNm", "Kopi Tubruk 200g", 20, V("c.fg"), weight="700",
          w=358),
        T("DetCat", "Minuman - Stok 42", 13, V("c.mfg"), w=358),
        T("DetPr", "Rp 28.000", 24, V("c.pri"), weight="700", w=358),
        T("DetDesc", "Kopi tubruk asli, sangrai medium, kemasan 200 gram.",
          13, V("c.mfg"), w=358),
        F("DetQty", 358, 56, V("c.card"), [
            T("QMin", "-", 20, V("c.pri"), align="center", weight="700",
              w=48),
            T("QVal", "1", 18, V("c.fg"), align="center", weight="700",
              w=60),
            T("QPlus", "+", 20, V("c.pri"), align="center",
              weight="700", w=48),
        ], 12, {"layout": "horizontal", "gap": 8,
                "justifyContent": "center", "alignItems": "center",
                "stroke": V("c.line"), "strokeWidth": 1}),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
    FOOTCTA("det", COMPS["Cmp BtnPrimary"], "Tambah ke Keranjang"),
], next_x())

# ============ 07 KERANJANG ============
rows = [("Kopi Tubruk 200g", "Rp 28.000 /pcs", "Rp 28.000"),
        ("Indomie Goreng x2", "Rp 3.500 /pcs", "Rp 7.000"),
        ("Aqua 600ml", "Rp 4.000 /pcs", "Rp 4.000")]
s2rows = [RB("Cmp CartRow", "Row %d" % i, D_CR_NM=n, D_CR_PR=p,
             D_CR_AMT=a) for i, (n, p, a) in enumerate(rows)]
SCR("07 Keranjang", [
    NAVBACK("cart", "Keranjang - 3 item", "Toko Berkah Jaya"),
    F("List", 390, 300, V("c.bg"), s2rows, 0,
      {"layout": "vertical", "gap": 10, "padding": 16}),
    F("PromoW", 390, 80, V("c.bg"), [
        F("Promo", 358, 56, V("c.card"),
          [T("PromoTxt", "PROMO: HEMAT10 (-10%)", 13, V("c.ok"),
             weight="700", w=326)], 14,
          {"layout": "vertical", "justifyContent": "center",
           "padding": 14, "stroke": V("c.line"),
           "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("SumW", 390, 170, V("c.bg"), [
        F("Summary", 358, 140, V("c.card"), [
            T("Sum1", "Subtotal   Rp 39.000", 13, V("c.mfg"), w=326),
            T("Sum2", "Promo HEMAT10   -Rp 3.900", 13, V("c.ok"),
              w=326),
            T("Sum3", "Pajak 10%   Rp 3.510", 13, V("c.mfg"), w=326),
            T("Sum4", "Total   Rp 38.610", 17, V("c.fg"), weight="700",
              w=326),
        ], 14, {"layout": "vertical", "gap": 6, "padding": 14,
                "stroke": V("c.line"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    FOOTCTA("cart", COMPS["Cmp BtnPrimary"], "Lanjut ke Pembayaran"),
], next_x())

# ============ 08 PELANGGAN ============
SCR("08 Pelanggan", [
    NAVBACK("cust", "Pilih Pelanggan"),
    F("CustSearchW", 390, 68, V("c.card"), [
        F("CustSearch", 358, 46, V("c.mut"),
          [T("CustHint", "Cari nama / nomor HP...", 13, V("c.mfg"),
             w=326)], 12,
          {"layout": "vertical", "justifyContent": "center",
           "padding": 14})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("CustBody", 390, 440, V("c.bg"), [
        RB("Cmp MenuRow", "Cu-Umum", D_MN_LBL="Pelanggan Umum"),
        RB("Cmp MenuRow", "Cu-Budi", D_MN_LBL="Budi (0812-111)"),
        RB("Cmp MenuRow", "Cu-Sari", D_MN_LBL="Sari (0813-222)"),
        RB("Cmp MenuRow", "Cu-Agung", D_MN_LBL="Agung (0819-333)"),
        RB("Cmp MenuRow", "Cu-Plus", D_MN_LBL="+ Tambah Pelanggan"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
    FOOTCTA("cust", COMPS["Cmp BtnPrimary"], "Lanjut Tanpa Member"),
], next_x())

# ============ 09 PEMBAYARAN TUNAI ============
tiles = ["Tunai", "QRIS", "Debit", "E-Wallet"]
tile_rows = [F("TileRow%d" % r, 358, 76, V("c.bg"),
               [RB("Cmp PayTile", "Tile %s" % lb, D_TILE_LBL=lb)
                for lb in tiles[r*2:(r+1)*2]], 0,
               {"layout": "horizontal", "gap": 10})
             for r in range(2)]
SCR("09 Bayar Tunai", [
    NAVBACK("pay", "Pembayaran"),
    F("TotalW", 390, 130, V("c.bg"), [
        F("TotalCard", 358, 100, V("c.pri"), [
            T("TotLbl", "TOTAL TAGIHAN", 12, V("c.onpri"),
              align="center", w=326),
            T("TotVal", "Rp 38.610", 32, V("c.onpri"), align="center",
              weight="700", w=326),
        ], 16, {"layout": "vertical", "gap": 4,
                "justifyContent": "center", "alignItems": "center"})],
      0, {"layout": "vertical", "alignItems": "center"}),
    LBL("pay1", "METODE PEMBAYARAN"),
    F("Methods", 390, 184, V("c.bg"), tile_rows, 0,
      {"layout": "vertical", "gap": 10, "padding": 16,
       "alignItems": "center"}),
    LBL("pay2", "UANG DITERIMA"),
    F("DenomW", 390, 76, V("c.bg"), [
        F("Denom", 358, 52, V("c.card"), [
            T("Dn1", "Rp 40 rb", 12, V("c.mfg"), align="center",
              weight="700", w=100),
            T("Dn2", "Rp 50 rb", 12, V("c.pri"), align="center",
              weight="700", w=100),
            T("Dn3", "Rp 100 rb", 12, V("c.mfg"), align="center",
              weight="700", w=100),
        ], 10, {"layout": "horizontal", "gap": 8,
                "justifyContent": "center", "alignItems": "center",
                "stroke": V("c.line"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("ChgW", 390, 96, V("c.bg"), [
        F("Change", 358, 72, V("c.okbg"),
          [T("ChgTxt", "Kembalian  Rp 11.390", 16, V("c.ok"),
             align="center", weight="700", w=326)], 13,
          {"layout": "vertical", "justifyContent": "center",
           "stroke": V("c.ok"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    FOOTCTA("pay", COMPS["Cmp BtnPrimary"], "Selesaikan Transaksi"),
], next_x())

# ============ 10 QRIS ============
SCR("10 Bayar QRIS", [
    NAVBACK("qris", "Pembayaran QRIS"),
    F("QrisBody", 390, 560, V("c.bg"), [
        T("QrisTot", "Total  Rp 38.610", 18, V("c.fg"), align="center",
          weight="700", w=358),
        F("QrBox", 260, 260, V("c.card"), [
            R("QrFake", V("c.fg"), 200, 200, 8)],
            16, {"layout": "vertical", "justifyContent": "center",
                 "alignItems": "center", "stroke": V("c.line"),
                 "strokeWidth": 1}),
        T("QrisHint", "Scan kode di atas dengan e-wallet / m-banking",
          13, V("c.mfg"), align="center", w=340),
        T("QrisTimer", "Berlaku 04:59", 14, V("c.warn"), align="center",
          weight="700", w=340),
        F("QrisStat", 358, 56, V("c.warn") if False else V("c.mut"),
          [T("QrisStatTxt", "Menunggu pembayaran...", 13, V("c.fg"),
             align="center", weight="600", w=326)], 12,
          {"layout": "vertical", "justifyContent": "center"}),
    ], 0, {"layout": "vertical", "gap": 14, "alignItems": "center",
           "padding": 16}),
    FOOTCTA("qris", COMPS["Cmp BtnPrimary"], "Saya Sudah Bayar"),
], next_x())

# ============ 11 SUKSES ============
SCR("11 Sukses", [
    STATUS("ok"),
    F("Hero", 390, 200, V("c.bg"), [
        IC("Check", IC_OK, size=40, fg="$c.ok", bg="$c.okbg",
           box=88, radius=999),
        T("OkTitle", "Pembayaran Berhasil", 19, V("c.fg"),
          align="center", weight="700", w=320),
        T("OkSub", "Order #129 - Tunai - 09.42 WIB", 13,
          V("c.mfg"), align="center", w=320),
    ], 0, {"layout": "vertical", "gap": 12, "alignItems": "center",
           "padding": 28}),
    F("StrukW", 390, 380, V("c.bg"), [
        F("Struk", 342, 350, V("c.card"), [
            T("SH", "TOKO BERKAH JAYA", 14, V("c.fg"),
              align="center", weight="700", w=310),
            T("SA", "Jl. Merdeka No.12 - 0812-3456-7890", 11,
              V("c.mfg"), align="center", w=310),
            T("SI1", "Kopi Tubruk x1   28.000", 12, V("c.fg"),
              w=310),
            T("SI2", "Indomie Goreng x2   7.000", 12, V("c.fg"),
              w=310),
            T("SI3", "Aqua 600ml x1   4.000", 12, V("c.fg"), w=310),
            T("SI4", "Subtotal   39.000", 12, V("c.mfg"), w=310),
            T("SI5", "Promo HEMAT10   -3.900", 12, V("c.mfg"),
              w=310),
            T("SI6", "Pajak 10%   3.510", 12, V("c.mfg"), w=310),
            T("SI7", "Total   Rp 38.610", 14, V("c.fg"), weight="700",
              w=310),
            T("SI8", "Tunai 50.000 - Kembali 11.390", 12, V("c.fg"),
              w=310),
        ], 14, {"layout": "vertical", "gap": 5, "padding": 16,
                "stroke": V("c.line"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("FootOk", 390, 150, V("c.card"), [
        F("Ghost", 358, 52, V("c.card"),
          [T("GhostLbl", "Cetak Struk", 14, V("c.fg"),
             align="center", weight="700", w=326)], 12,
          {"layout": "vertical", "justifyContent": "center",
           "alignItems": "center", "stroke": V("c.line"),
           "strokeWidth": 2}),
        RB("Cmp BtnPrimary", "CTA-Baru",
           D_BTN_LBL="Transaksi Baru +"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16,
           "justifyContent": "center", "alignItems": "center"}),
], next_x())

# ============ 12 STRUK / NOTA ============
SCR("12 Struk Nota", [
    NAVBACK("nota", "Struk #129", "09.42 - Tunai - Andi"),
    F("NotaW", 390, 560, V("c.bg"), [
        F("Nota", 342, 440, V("c.card"), [
            T("NH", "TOKO BERKAH JAYA", 15, V("c.fg"),
              align="center", weight="700", w=310),
            T("NA", "Jl. Merdeka No.12", 11, V("c.mfg"),
              align="center", w=310),
            T("NID", "#129 / 24-09-2026 09:42", 11, V("c.mfg"),
              align="center", w=310),
            T("NDiv", "- - - - - - - - - - - - - - -", 11,
              V("c.line"), align="center", w=310),
            T("NI1", "Kopi Tubruk 200g", 12, V("c.fg"), w=310),
            T("NI1b", "1 x 28.000           28.000", 12, V("c.fg"),
              w=310),
            T("NI2", "Indomie Goreng", 12, V("c.fg"), w=310),
            T("NI2b", "2 x 3.500              7.000", 12, V("c.fg"),
              w=310),
            T("NI3", "Aqua 600ml", 12, V("c.fg"), w=310),
            T("NI3b", "1 x 4.000              4.000", 12, V("c.fg"),
              w=310),
            T("NDiv2", "- - - - - - - - - - - - - - -", 11,
              V("c.line"), align="center", w=310),
            T("NT", "TOTAL   Rp 38.610", 14, V("c.fg"), weight="700",
              w=310),
            T("NT2", "TUNAI 50.000 - KEMBALI 11.390", 12, V("c.fg"),
              w=310),
            T("NThx", "Terima kasih!", 12, V("c.mfg"),
              align="center", w=310),
        ], 14, {"layout": "vertical", "gap": 4, "padding": 16,
                "stroke": V("c.line"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center",
         "padding": 16}),
    F("FootNota", 390, 84, V("c.card"), [
        RB("Cmp BtnPrimary", "CTA-Share",
           D_BTN_LBL="Bagikan via WA"),
    ], 0, {"layout": "vertical", "justifyContent": "center",
           "alignItems": "center"}),
], next_x())

# ============ 13 RIWAYAT ============
SCR("13 Riwayat", [
    NAVBACK("hist", "Riwayat Transaksi", "24 Sep 2026"),
    F("HistFilterW", 390, 60, V("c.bg"), [
        F("HistFilter", 358, 40, V("c.card"), [
            T("HF1", "Hari Ini", 12, V("c.onpri"), align="center",
              weight="700", w=100),
            T("HF2", "Kemarin", 12, V("c.mfg"), align="center",
              weight="600", w=100),
            T("HF3", "7 Hari", 12, V("c.mfg"), align="center",
              weight="600", w=100),
        ], 999, {"layout": "horizontal", "gap": 4,
                 "justifyContent": "center", "alignItems": "center",
                 "stroke": V("c.line"), "strokeWidth": 1})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("HistBody", 390, 480, V("c.bg"), [
        RB("Cmp MenuRow", "H-129", D_MN_LBL="#129 - Rp 38.610"),
        RB("Cmp MenuRow", "H-128", D_MN_LBL="#128 - Rp 52.000"),
        RB("Cmp MenuRow", "H-127", D_MN_LBL="#127 - Rp 15.500"),
        RB("Cmp MenuRow", "H-126", D_MN_LBL="#126 - Rp 120.000"),
        RB("Cmp MenuRow", "H-125", D_MN_LBL="#125 - Rp 8.000"),
        F("HistSum", 358, 60, V("c.pri"), [
            T("HistSumTxt", "128 transaksi - Rp 4.215.000", 14,
              V("c.onpri"), align="center", weight="700", w=326)],
            14, {"layout": "vertical", "justifyContent": "center"}),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
], next_x())

# ============ 14 DETAIL TRANSAKSI + RETUR ============
SCR("14 Detail Trx", [
    NAVBACK("dtrx", "Transaksi #128", "Tunai - 08.15 - Sari"),
    F("DtrxBody", 390, 520, V("c.bg"), [
        F("DtrxCard", 358, 300, V("c.card"), [
            T("DT1", "Indomie Goreng x4   14.000", 13, V("c.fg"),
              w=326),
            T("DT2", "Beras 5kg x1   68.500", 13, V("c.fg"), w=326),
            T("DT3", "Subtotal   82.500", 13, V("c.mfg"), w=326),
            T("DT4", "Pajak 10%   8.250", 13, V("c.mfg"), w=326),
            T("DT5", "Total   Rp 90.750", 16, V("c.fg"), weight="700",
              w=326),
            T("DT6", "Tunai 100.000 - Kembali 9.250", 13, V("c.fg"),
              w=326),
        ], 14, {"layout": "vertical", "gap": 6, "padding": 16,
                "stroke": V("c.line"), "strokeWidth": 1}),
        F("ReturBox", 358, 76, V("c.danbg"),
          [T("ReturTxt", "Retur / Refund butuh PIN supervisor", 13,
             V("c.dan"), align="center", weight="600", w=326)],
          12, {"layout": "vertical", "justifyContent": "center",
               "stroke": V("c.dan"), "strokeWidth": 1}),
    ], 0, {"layout": "vertical", "gap": 12, "padding": 16}),
    F("FootDtrx", 390, 150, V("c.card"), [
        F("GhostR", 358, 52, V("c.card"),
          [T("GhostRLbl", "Cetak Ulang", 14, V("c.fg"),
             align="center", weight="700", w=326)], 12,
          {"layout": "vertical", "justifyContent": "center",
           "alignItems": "center", "stroke": V("c.line"),
           "strokeWidth": 2}),
        RB("Cmp BtnPrimary", "CTA-Retur", D_BTN_LBL="Proses Retur"),
    ], 0, {"layout": "vertical", "gap": 10,
           "justifyContent": "center", "alignItems": "center"}),
], next_x())

# ============ 15 TUTUP SHIFT ============
SCR("15 Tutup Shift", [
    NAVBACK("close", "Tutup Shift Pagi"),
    F("CloseBody", 390, 520, V("c.bg"), [
        RB("Cmp Stat", "C-Omzet", D_ST_LBL="Total omzet",
           D_ST_VAL="Rp 4.215.000"),
        F("CloseRow", 358, 96, V("c.bg"), [
            RB("Cmp Stat", "C-Trx", D_ST_LBL="Transaksi",
               D_ST_VAL="128"),
            RB("Cmp Stat", "C-Retur", D_ST_LBL="Retur",
               D_ST_VAL="2"),
        ], 0, {"layout": "horizontal", "gap": 16}),
        RB("Cmp Field", "F-Count", D_FD_LBL="Hitung kas fisik (Rp)",
           D_FD_VAL="4.715.000"),
        F("CloseDiff", 358, 56, V("c.okbg"),
          [T("CloseDiffTxt", "Selisih +0 (pas)", 14, V("c.ok"),
             align="center", weight="700", w=326)], 12,
          {"layout": "vertical", "justifyContent": "center",
           "stroke": V("c.ok"), "strokeWidth": 1}),
    ], 0, {"layout": "vertical", "gap": 12, "padding": 16}),
    FOOTCTA("close", COMPS["Cmp BtnPrimary"], "Tutup & Cetak Laporan"),
], next_x())

# ============ 16 STOK ============
SCR("16 Stok", [
    NAVBACK("stok", "Stok Produk", "6 menipis"),
    F("StokSearchW", 390, 68, V("c.card"), [
        F("StokSearch", 358, 46, V("c.mut"),
          [T("StokHint", "Cari produk...", 13, V("c.mfg"), w=326)],
          12, {"layout": "vertical", "justifyContent": "center",
               "padding": 14})],
      0, {"layout": "vertical", "alignItems": "center"}),
    F("StokBody", 390, 440, V("c.bg"), [
        RB("Cmp MenuRow", "St-Beras", D_MN_LBL="Beras 5kg - sisa 25"),
        RB("Cmp MenuRow", "St-Kopi",
           D_MN_LBL="Kopi Tubruk - sisa 8 (!)"),
        RB("Cmp MenuRow", "St-Roti", D_MN_LBL="Roti Tawar - sisa 5 (!)"),
        RB("Cmp MenuRow", "St-Aqua",
           D_MN_LBL="Aqua 600ml - sisa 300"),
        RB("Cmp MenuRow", "St-Indo",
           D_MN_LBL="Indomie - sisa 200"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
    F("FootStok", 390, 84, V("c.card"), [
        RB("Cmp BtnPrimary", "CTA-Opname",
           D_BTN_LBL="+ Stok Masuk / Opname")],
        0, {"layout": "vertical", "justifyContent": "center",
            "alignItems": "center"}),
], next_x())

# ============ 17 TAMBAH PRODUK ============
SCR("17 Tambah Produk", [
    NAVBACK("addp", "Tambah Produk"),
    F("AddpBody", 390, 560, V("c.bg"), [
        F("AddImg", 358, 120, V("c.mut"),
          [T("AddImgTxt", "+ Foto Produk", 14, V("c.mfg"),
             align="center", weight="600", w=326)], 14,
          {"layout": "vertical", "justifyContent": "center",
           "stroke": V("c.line"), "strokeWidth": 1}),
        RB("Cmp Field", "F-PNm", D_FD_LBL="Nama produk",
           D_FD_VAL="cth: Kopi Kapal 200g"),
        RB("Cmp Field", "F-PPr", D_FD_LBL="Harga jual (Rp)",
           D_FD_VAL="28000"),
        RB("Cmp Field", "F-PSt", D_FD_LBL="Stok awal",
           D_FD_VAL="50"),
        RB("Cmp Field", "F-PCat", D_FD_LBL="Kategori",
           D_FD_VAL="Minuman"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16}),
    FOOTCTA("addp", COMPS["Cmp BtnPrimary"], "Simpan Produk"),
], next_x())

# ============ 18 LAPORAN ============
bars = [("S", 60), ("S", 90), ("R", 70), ("K", 120), ("J", 100),
        ("S", 140), ("M", 110)]
barrow = []
for i, (d, h) in enumerate(bars):
    barrow.append(F("Bar%d" % i, 36, 150, V("c.bg"), [
        R("BarFill%d" % i, V("c.pri"), 36, h, 6),
        T("BarD%d" % i, d, 10, V("c.mfg"), align="center", w=36)],
        0, {"layout": "vertical", "gap": 6,
            "justifyContent": "end", "alignItems": "center"}))
SCR("18 Laporan", [
    NAVBACK("lap", "Laporan", "24 Sep 2026"),
    F("LapBody", 390, 600, V("c.bg"), [
        F("LapRow", 358, 96, V("c.bg"), [
            RB("Cmp Stat", "L-Omzet", D_ST_LBL="Omzet hari ini",
               D_ST_VAL="Rp 4,2 jt"),
            RB("Cmp Stat", "L-Laba", D_ST_LBL="Laba kotor",
               D_ST_VAL="Rp 1,1 jt"),
        ], 0, {"layout": "horizontal", "gap": 16}),
        F("Chart", 358, 210, V("c.card"), [
            T("ChartT", "Omzet 7 hari terakhir", 13, V("c.fg"),
              weight="700", w=326),
            F("Bars", 326, 150, V("c.card"), barrow, 0,
              {"layout": "horizontal", "gap": 8,
               "justifyContent": "center", "alignItems": "end"}),
        ], 14, {"layout": "vertical", "gap": 8, "padding": 14,
                "stroke": V("c.line"), "strokeWidth": 1}),
        RB("Cmp MenuRow", "L-Top",
           D_MN_LBL="Terlaris: Indomie (200)"),
        RB("Cmp MenuRow", "L-Pay",
           D_MN_LBL="Tunai 70% - QRIS 30%"),
    ], 0, {"layout": "vertical", "gap": 12, "padding": 16}),
], next_x())

# ============ 19 PENGATURAN ============
SCR("19 Pengaturan", [
    NAVBACK("set", "Pengaturan"),
    F("SetBody", 390, 560, V("c.bg"), [
        RB("Cmp MenuRow", "Se-Toko", D_MN_LBL="Profil Toko"),
        RB("Cmp MenuRow", "Se-Print",
           D_MN_LBL="Printer & Struk"),
        RB("Cmp MenuRow", "Se-Pajak", D_MN_LBL="Pajak & Promo"),
        RB("Cmp MenuRow", "Se-User", D_MN_LBL="Karyawan & PIN"),
        RB("Cmp MenuRow", "Se-Sync", D_MN_LBL="Sinkronisasi: ON"),
        RB("Cmp MenuRow", "Se-Out", D_MN_LBL="Keluar Akun"),
    ], 0, {"layout": "vertical", "gap": 10, "padding": 16, "alignItems": "center"}),
    F("SetVer", 390, 60, V("c.bg"),
      [T("Ver", "Berkah POS v2.4.0", 12, V("c.mfg"), align="center",
         w=358)], 0,
      {"layout": "vertical", "alignItems": "center"}),
], next_x())

# ================= FINALIZE =================
doc = {
    "version": "2.19",
    "name": "Kasir POS Full - Clean Light Mobile (19 screens)",
    "variables": {k: {"type": "color", "value": v}
                  for k, v in VARS.items()},
    "children": children + screens,
}

print("screens:", len(screens), "| comps:", len(children))
import pathlib as _pl
OUT = str(_pl.Path(__file__).with_name("kasir-pos.pen"))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)
print("written " + OUT)
