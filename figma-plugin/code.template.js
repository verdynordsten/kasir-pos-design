// Kasir POS sync plugin — builds all screens + components from PEN data.
// Flow: Plugins > Development > Import plugin from manifest > select this folder,
// then Plugins > Development > Kasir POS Sync > Sync.
function hex(h) {
  if (!h || typeof h !== "string" || !h.startsWith("#")) return null;
  const n = h.slice(1);
  const v = n.length === 3 ? n.split("").map((c) => c + c).join("") : n;
  const i = parseInt(v, 16);
  return { r: ((i >> 16) & 255) / 255, g: ((i >> 8) & 255) / 255, b: (i & 255) / 255 };
}
function paint(fill) {
  const c = hex(fill);
  if (!c) return [];
  return [{ type: "SOLID", color: c }];
}
function applyLayout(frame, n) {
  if (n.layout === "vertical" || n.layout === "horizontal") {
    frame.layoutMode = n.layout === "vertical" ? "VERTICAL" : "HORIZONTAL";
    if (typeof n.gap === "number") frame.itemSpacing = n.gap;
    if (typeof n.padding === "number") {
      frame.paddingTop = frame.paddingRight = frame.paddingBottom = frame.paddingLeft = n.padding;
    }
    if (n.justify === "space_between") frame.primaryAxisAlignItems = "SPACE_BETWEEN";
    else if (n.justify === "center") frame.primaryAxisAlignItems = "CENTER";
    if (n.align === "center") frame.counterAxisAlignItems = "CENTER";
  }
}
async function loadFont(weight) {
  const style = weight === "700" ? "Bold" : weight === "600" ? "SemiBold" : "Regular";
  try { await figma.loadFontAsync({ family: "Inter", style }); }
  catch (e) { await figma.loadFontAsync({ family: "Inter", style: "Regular" }); }
}
async function buildText(n) {
  await loadFont(String(n.weight || "400"));
  const t = figma.createText();
  t.name = n.name || "Text";
  t.characters = String(n.content ?? "");
  t.fontSize = n.size || 14;
  const fills = paint(n.fill);
  if (fills.length) t.fills = fills;
  if (n.align === "center") t.textAlignHorizontal = "CENTER";
  else if (n.align === "right") t.textAlignHorizontal = "RIGHT";
  if (n.w) { try { t.resize(n.w, t.height); } catch (e) {} }
  return t;
}
function buildRect(n) {
  const r = figma.createRectangle();
  r.name = n.name || "Rect";
  r.resize(n.w || 100, n.h || 40);
  const fills = paint(n.fill);
  if (fills.length) r.fills = fills;
  if (n.radius) r.cornerRadius = n.radius;
  if (n.stroke) { r.strokes = paint(n.stroke); r.strokeWeight = 1; }
  return r;
}
async function buildNode(n, compsById) {
  if (n.type === "text") return buildText(n);
  if (n.type === "rectangle") return buildRect(n);
  if (n.type === "frame") {
    const f = figma.createFrame();
    f.name = n.name || "Frame";
    f.resize(n.w || 100, n.h || 60);
    const fills = paint(n.fill);
    if (fills.length) f.fills = fills; else f.fills = [];
    if (n.radius) f.cornerRadius = n.radius;
    if (n.stroke) { f.strokes = paint(n.stroke); f.strokeWeight = 1; }
    applyLayout(f, n);
    for (const c of n.children || []) f.appendChild(await buildNode(c, compsById));
    return f;
  }
  if (n.type === "ref") {
    const target = compsById[n.ref];
    if (target) {
      const inst = target.createInstance();
      inst.name = n.name || target.name;
      const desc = n.desc || {};
      const queue = [inst];
      while (queue.length) {
        const node = queue.pop();
        if (node.type === "TEXT" && desc[node.getPluginData("penId")]) {
          await loadFont("400");
          try { node.characters = String(desc[node.getPluginData("penId")].content ?? node.characters); } catch (e) {}
        }
        if ("children" in node) for (const c of node.children) queue.push(c);
      }
      return inst;
    }
    const ph = figma.createFrame();
    ph.name = (n.name || "Ref") + " (missing)";
    ph.resize(100, 40);
    return ph;
  }
  const g = figma.createFrame();
  g.name = n.name || n.type;
  return g;
}
async function run() {
  const compsById = {};
  for (const c of PEN.components || []) {
    const node = await buildNode(c, {});
    node.name = c.name;
    const comp = figma.createComponentFromNode(node);
    const tag = async (nd, src) => {
      if (nd.type === "TEXT" && src && src.id) nd.setPluginData("penId", src.id);
      const sk = (src && src.children) || [];
      if ("children" in nd) for (let i = 0; i < nd.children.length && i < sk.length; i++) await tag(nd.children[i], sk[i]);
    };
    await tag(comp, c);
    const rawId = Object.keys(PEN.compNames).find((id) => PEN.compNames[id] === c.name);
    if (rawId) compsById[rawId] = comp;
  }
  let x = 0;
  const gap = 120;
  for (const s of PEN.screens || []) {
    const node = await buildNode(s, compsById);
    node.name = s.name;
    node.x = x; node.y = 0;
    figma.currentPage.appendChild(node);
    x += (s.w || 390) + gap;
  }
  figma.notify(`Synced ${PEN.screens.length} screens + ${PEN.components.length} components`);
}
run();
