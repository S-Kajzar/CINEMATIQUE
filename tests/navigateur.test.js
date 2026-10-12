// Tests navigateur (Playwright + Chromium) : accueil, cours, atelier libre, activités en entraînement et en examen.
//   NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const fs = require("node:fs");
const { chromium } = require("playwright");

const FILE = path.join(__dirname, "..", "index.html");
const URL = "file://" + FILE;
const html = fs.readFileSync(FILE, "utf8");
const EXOS = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
const ACTS = Object.keys(EXOS);
let browser;

test.before(async () => { browser = await chromium.launch(); });
test.after(async () => { await browser.close(); });

async function open(url, viewport) {
  const context = await browser.newContext({ viewport: viewport || { width: 1500, height: 1000 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("dialog", (d) => d.accept());
  await page.goto(URL + url);
  return { context, page, errors };
}
const text = (page, sel) => page.locator(sel).first().innerText();

// ------------------------------------------------------------------ outils de l'atelier, pilotés comme le ferait l'élève
async function ecran(page, id, p) {
  return page.evaluate(([id, x, y]) => {
    const a = window.__ateliers__.find((t) => t.root.id === id), r = a.svg.getBoundingClientRect(), v = a.vue;
    const k = Math.min(r.width / v.w, r.height / v.h), ox = r.left + (r.width - v.w * k) / 2, oy = r.top + (r.height - v.h * k) / 2;
    return [ox + (x - v.x) * k, oy + (y - v.y) * k];
  }, [id, p[0], p[1]]);
}
async function clic(page, id, p) {
  await page.locator(`#${id} .at-stage`).scrollIntoViewIfNeeded();
  const s = await ecran(page, id, p);
  await page.mouse.click(s[0], s[1]);
}
async function outil(page, id, o) { await page.click(`#${id} [data-outil=${o}]`); }
async function nommer(page, id, nom) {
  await page.fill(`#${id} .at-p-nom`, nom);
  await page.locator(`#${id} .at-p-nom`).dispatchEvent("change");
}
async function vecteur(page, id, o, v, nom) {
  await outil(page, id, "vecteur");
  await clic(page, id, o);
  await clic(page, id, [o[0] + v[0] * 0.9, o[1] + v[1] * 0.9]);
  await page.fill(`#${id} .at-p-long`, String(Math.hypot(v[0], v[1]).toFixed(2)).replace(".", ","));
  await page.locator(`#${id} .at-p-long`).dispatchEvent("change");
  if (nom) await nommer(page, id, nom);
}
const objets = (page, id) => page.evaluate((id) => window.__ateliers__.find((t) => t.root.id === id).objs.map((o) => o.t), id);
const pts = (page, id) => page.evaluate((id) => Object.fromEntries(window.__ATELIERS__[id].pts.map((q) => [q[0], [q[1], q[2]]])), id);
const items = (page, id) => page.evaluate((id) => window.__ATELIERS__[id].items, id);

// une solution complète d'une construction, posée dans l'atelier par son interface de programmation
async function poserSolution(page, id) {
  await page.evaluate((id) => {
    const a = window.__ateliers__.find((t) => t.root.id === id);
    Object.values(a.cfg.items).forEach((it) => {
      if (it.k === "ve") a.objs.push({ t: "ve", a: it.o, b: [it.o[0] + it.v[0], it.o[1] + it.v[1]], nom: it.nom, c: "#1F5FA8" });
      else if (it.k === "dir") a.objs.push({ t: "dr", p: it.o, d: it.d, c: "#1F5FA8" });
      else if (it.k === "pt") a.objs.push({ t: "pt", p: it.p, nom: it.nom, c: "#1F5FA8" });
      else if (it.k === "ci") a.objs.push({ t: "ci", c: it.c, r: it.r, c2: "" });
    });
    a.changer();
  }, id);
}
// réponses justes des questions saisies et des étiquettes, lues dans la configuration et dans les corrections
async function repondreTout(page, key) {
  const qcfg = EXOS[key].qcfg;
  for (const [id, q] of Object.entries(qcfg)) {
    const g = q.grader;
    if ((g.type === "num" || g.type === "chasles") && await page.isDisabled(`#in-${id}`)) continue;
    if (g.type === "num") await page.fill(`#in-${id}`, `${String(g.value).replace(".", ",")} ${g.unit.label}`);
    if (g.type === "chasles") {
      const s = Object.keys(g.solids);
      const rel = s.includes("s4") ? "V(C∈S4/S0) = V(C∈S4/S5) + V(C∈S5/S0)" : "V(C∈5/0) = V(C∈5/4) + V(C∈4/0)";
      await page.fill(`#in-${id}`, rel);
    }
  }
  for (const dz of await page.locator("#parts .dz:not(:disabled)").all()) {
    const id = (await dz.getAttribute("id")).slice(3), bk = await dz.getAttribute("data-bank");
    const bonne = await page.evaluate(([id]) => {
      const g = document.getElementById(id.replace(/_\d+$/, "")), cases = [...g.querySelectorAll("input[data-q]")].map((i) => i.id.slice(3));
      return g.querySelectorAll(".grp-sol tbody tr")[cases.indexOf(id)].children[1].textContent;
    }, [id]);
    await page.locator(`#${bk}`).getByRole("button", { name: bonne, exact: true }).click();
    await dz.click();
  }
}

test("accueil : cartes illustrées (cours, atelier, activités analytiques et graphiques, études de cas)", async () => {
  const { context, page, errors } = await open("");
  assert.ok(await page.locator("body.hub").count());
  assert.ok(!(await page.isVisible("main.page")));
  assert.match(await text(page, "#home h1"), /Cinématique/);
  const card = (sel) => page.locator(sel).evaluateAll((cs) => cs.map((c) => [
    c.querySelector(".mc-tag").textContent.trim(), c.querySelector("h3").textContent,
    c.querySelector("a") ? c.querySelector("a").getAttribute("href") : null]));
  assert.deepEqual(await card(".cours-grid .mode-card"), [
    ["Cours 1 Analytique", "Cinématique analytique", "?ex=cours-cinematique-analytique"],
    ["Cours 2 Graphique", "Cinématique graphique", "?ex=cours-cinematique-graphique"]]);
  assert.deepEqual(await card(".outil-grid .mode-card"), [["Atelier", "Atelier de construction libre", "?ex=atelier-libre"]]);
  assert.deepEqual(await card(".analytique-grid .mode-card"), [["Activité 1.1 Analytique", "Cinématique du point", null]]);
  assert.deepEqual((await card(".exo-grid .mode-card")).map((c) => c[0]), ACTS.map((_, i) => `Activité 2.${i + 1} Graphique`));
  assert.deepEqual((await card(".exo-grid .mode-card")).map((c) => c[2]), ACTS.map((k) => `?ex=${k}`));
  assert.deepEqual(await page.locator("#home h2").allInnerTexts(), ["Les cours", "L'atelier de construction",
    "Activités de cinématique analytique", "Activités de résolution graphique", "Études de cas"]);
  const cartes = await page.locator("#home .carte-v").evaluateAll((cs) => cs.map((c) => ({
    img: c.querySelector("img.cv-img") ? c.querySelector("img.cv-img").naturalWidth : -1,
    mots: c.querySelectorAll(".cv-mots li").length, p: c.querySelectorAll("p:not(.etat)").length,
    w: Math.round(c.offsetWidth), h: c.offsetHeight })));
  assert.equal(cartes.length, 12);
  for (const c of cartes) {
    assert.ok(c.mots >= 3 && c.mots <= 5 && c.p === 0 && c.img > 0, JSON.stringify(c));
    assert.equal(c.w, cartes[0].w); assert.ok(Math.abs(c.h - cartes[0].h) <= 1, JSON.stringify(cartes));
  }
  assert.equal(await page.locator(".en-edition .etat").count(), 2);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  const src = html.replace(/data:[^"]+/g, "");
  assert.doesNotMatch(src, /\b(BTS|STI2D|bac(calaur[ée]at)?|session \d|[ée]preuve|acad[ée]mie|sujet z[ée]ro|brevet|C\.I\.M)\b/i);
  assert.deepEqual(errors, []);
  await context.close();
});

test("adresse inconnue : retour à l'accueil", async () => {
  const { context, page, errors } = await open("?ex=inconnu");
  assert.ok(await page.locator(".cours-grid").count());
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 1 : simulateurs (train, vélo, vecteurs, hélice, MRUV, rotation), jeu, quiz", async () => {
  const { context, page, errors } = await open("?ex=cours-cinematique-analytique");
  assert.match(await text(page, "#home .home-head"), /Cours 1[\s\S]*Analytique[\s\S]*Cinématique analytique/);
  assert.equal(await page.locator(".cours-sec").count(), 9);
  await page.click("#ca-train [data-marche='-1']");
  await page.waitForTimeout(150);
  assert.equal((await text(page, "#ca-train .ca-v20")).trim(), "18,5 m/s");
  await page.click("#ca-train [data-vue='1']");
  await page.waitForTimeout(150);
  assert.match(await text(page, "#ca-train .ca-obs"), /relatif/);
  await page.click("#ca-velo .ca-go"); await page.waitForTimeout(500);
  assert.ok(await page.locator("#ca-velo polyline").count() >= 3, "trois trajectoires");
  await page.locator("#ca-vect .ca-tr").fill("0");
  assert.equal((await text(page, "#ca-vect .ca-vit")).trim(), "0,00 ; 2,00");
  await page.locator("#ca-helice .ca-nr").fill("1000");
  assert.equal((await text(page, "#ca-helice .ca-va")).trim(), "104,7 m/s");
  await page.locator("#ca-helice .ca-rr").fill("0.5");
  assert.equal((await text(page, "#ca-helice .ca-vp")).trim(), "52,4 m/s");
  await page.click("#ca-mruv [data-pre=f]");
  assert.equal((await text(page, "#ca-mruv .ca-on")).trim(), "décéléré");
  await page.locator("#ca-mruv .ca-gr").fill("0");
  assert.equal((await text(page, "#ca-mruv .ca-on")).trim(), "uniforme");
  await page.locator("#ca-rot .ca-wpr").fill("-0.2");
  assert.equal((await text(page, "#ca-rot .ca-onat")).trim(), "décéléré");
  const lignes = page.locator("#ca-jeu-mvt .jeu-l");
  for (let i = 0; i < await lignes.count(); i++) {
    const ok = await lignes.nth(i).getAttribute("data-ok");
    await lignes.nth(i).locator(`button[data-v="${ok}"]`).click();
  }
  assert.equal((await text(page, "#ca-jeu-mvt .jeu-s")).trim(), "8 / 8");
  const q = await page.locator(".quiz-q").count();
  for (let i = 0; i < q; i++) { const f = page.locator(".quiz-q").nth(i); await f.locator(`input[value="${await f.getAttribute("data-ok")}"]`).check(); }
  assert.equal((await text(page, "#qz-score")).trim(), `${q} / ${q}`);
  assert.equal((await text(page, "#qz-stars")).trim(), "★★★");
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 2 : démonstrations pas à pas, bielle-manivelle vivante, jeux, quiz", async () => {
  const { context, page, errors } = await open("?ex=cours-cinematique-graphique");
  assert.equal(await page.locator(".cours-sec").count(), 10);
  for (const [id, n] of [["dm-equi", 7], ["dm-cir", 5], ["dm-compo", 5]]) {
    assert.equal((await text(page, `#${id} .dm-num`)).trim(), `Étape 0 / ${n}`);
    assert.ok(await page.isDisabled(`#${id} .dm-prec`));
    for (let i = 0; i < n; i++) await page.click(`#${id} .dm-suiv`);
    assert.equal((await text(page, `#${id} .dm-num`)).trim(), `Étape ${n} / ${n}`);
    assert.ok(await page.isDisabled(`#${id} .dm-suiv`));
    assert.ok(await page.locator(`#${id} .at-cons text`).count() >= 1, "le vecteur cherché est nommé");
    await page.click(`#${id} .dm-zero`);
    assert.equal(await page.locator(`#${id} .at-cons > *`).count(), 0);
  }
  await page.locator("#cg-bm .cg-br").fill("90");
  assert.match(await text(page, "#cg-bm .cg-bi"), /infini/);
  await page.locator("#cg-bm .cg-br").fill("0");
  assert.match(await text(page, "#cg-bm .cg-bp"), /point mort/);
  for (const j of ["#cg-jeu-traj", "#cg-jeu-dir"]) {
    const l = page.locator(j + " .jeu-l");
    for (let i = 0; i < await l.count(); i++) await l.nth(i).locator(`button[data-v="${await l.nth(i).getAttribute("data-ok")}"]`).click();
    assert.equal((await text(page, j + " .jeu-s")).trim(), "5 / 5");
  }
  await page.selectOption("#cg-echelle .cg-ech", "5");
  assert.match(await text(page, "#cg-echelle .cg-fo"), /5/);
  const q = await page.locator(".quiz-q").count();
  for (let i = 0; i < q; i++) { const f = page.locator(".quiz-q").nth(i); await f.locator(`input[value="${await f.getAttribute("data-ok")}"]`).check(); }
  assert.equal((await text(page, "#qz-score")).trim(), `${q} / ${q}`);
  assert.deepEqual(errors, []);
  await context.close();
});

test("atelier libre : règle, équerre, compas, projeté, mesure, texte, gomme, annuler, clavier, plein écran", async () => {
  const { context, page, errors } = await open("?ex=atelier-libre");
  const id = "at-libre";
  await outil(page, id, "point"); await clic(page, id, [50, 50]); await nommer(page, id, "A");
  await outil(page, id, "point"); await clic(page, id, [150, 100]);
  await outil(page, id, "droite"); await clic(page, id, [50.4, 50.3]); await clic(page, id, [150.2, 99.8]);  // accroché aux points
  let [pa, pb, o] = await page.evaluate(() => window.__ateliers__[0].objs.slice(-3));
  assert.equal(o.t, "dr"); assert.deepEqual(o.p, pa.p);
  const pente = (pb.p[1] - pa.p[1]) / (pb.p[0] - pa.p[0]);
  assert.ok(Math.abs(o.d[1] / o.d[0] - pente) < 1e-9, "droite passant exactement par les deux points");
  await outil(page, id, "perp"); await clic(page, id, [100, 75]); await clic(page, id, [150, 100]);
  o = await page.evaluate(() => window.__ateliers__[0].objs.at(-1));
  assert.ok(Math.abs(o.d[0] + o.d[1] * pente) < 1e-9, "perpendiculaire");
  await outil(page, id, "para"); await clic(page, id, [100, 75]); await clic(page, id, [60, 120]);
  await outil(page, id, "vecteur"); await clic(page, id, [150, 100]); await clic(page, id, [150, 70]);
  assert.match(await text(page, `#${id} .at-p-type`), /Vecteur de 30,0 mm/);
  await outil(page, id, "proj"); await clic(page, id, [150, 70]); await clic(page, id, [80, 65]);
  const h = await page.evaluate(() => window.__ateliers__[0].objs.at(-1).p);
  assert.ok(Math.abs((h[1] - pa.p[1]) - pente * (h[0] - pa.p[0])) < 1e-9, "le projeté est sur la droite");
  await outil(page, id, "cercle"); await clic(page, id, [50, 50]); await clic(page, id, [70, 50]);
  await outil(page, id, "compas"); await clic(page, id, [50, 50]); await clic(page, id, [150, 100]); await clic(page, id, [200, 150]);
  o = await page.evaluate(() => window.__ateliers__[0].objs.at(-1));
  assert.ok(Math.abs(o.r - Math.hypot(pb.p[0] - pa.p[0], pb.p[1] - pa.p[1])) < 1e-9, "report de longueur au compas");
  await outil(page, id, "mesure"); await clic(page, id, [50, 50]); await clic(page, id, [150, 100]);
  assert.match(await text(page, `#${id} .at-mesure`), /Distance : 111,8 mm/);
  await outil(page, id, "texte"); await clic(page, id, [20, 20]);
  await page.keyboard.type("Bonjour"); await page.keyboard.press("Enter");
  const n = (await objets(page, id)).length;
  assert.equal(n, 11);
  await outil(page, id, "gomme"); await clic(page, id, [50, 50]);
  assert.equal((await objets(page, id)).length, n - 1);
  await page.click(`#${id} [data-act=annuler]`);
  assert.equal((await objets(page, id)).length, n);
  await page.click(`#${id} [data-act=retablir]`);
  assert.equal((await objets(page, id)).length, n - 1);
  // clavier : touche P (point), flèches, Entrée
  await page.locator(`#${id} .at-svg`).focus();
  await page.keyboard.press("p");
  for (let i = 0; i < 5; i++) await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Enter");
  assert.equal((await objets(page, id)).at(-1), "pt");
  await page.keyboard.press("Control+z");
  await page.click(`#${id} [data-act=zoom-plus]`);
  assert.equal((await text(page, `#${id} .at-zoom`)).trim(), "140 %");
  await page.click(`#${id} [data-act=ajuster]`);
  await page.click(`#${id} [data-act=plein]`);
  assert.ok(await page.locator(".at-zone.plein").count());
  await page.keyboard.press("Escape"); await page.keyboard.press("Escape");
  assert.equal(await page.locator(".at-zone.plein").count(), 0);
  const [popup] = await Promise.all([page.waitForEvent("popup"), page.click(`#${id} [data-act=vierge]`)]);
  await popup.waitForLoadState();
  assert.match(await popup.locator("svg").getAttribute("width"), /277mm/);
  await page.click(`#${id} [data-act=effacer]`); await page.click(`#${id} [data-act=effacer]`);
  assert.equal((await objets(page, id)).length, 0);
  assert.deepEqual(errors, []);
  await context.close();
});

test("arbre de transmission, entraînement : constructions à l'outil, étiquettes, valeurs — 20/20", async () => {
  const { context, page, errors } = await open("?ex=arbre-transmission");
  await page.click("[data-mode=training]");
  const id = "at-arbre-transmission-1", P = await pts(page, id), I = await items(page, id);
  // Q1 a) puis b) : V(A) et V(B) à l'outil Vecteur, longueur saisie, nom
  await page.fill("#in-a1", "5,24 m/s"); await page.click("#a1 .btn-validate");
  await vecteur(page, id, P.A, I.a2_1.v, "V(A∈4/0)");
  assert.equal(await page.inputValue("#in-a2_1"), "juste");
  assert.equal((await text(page, "#it-a2_1 .it-etat")).trim(), "tracé repéré");
  await page.click("#a2 .btn-trace");
  assert.match(await text(page, "#a2 .q-msg"), /Pas encore tracé : Vecteur V\(B∈4\/0\)/);
  await vecteur(page, id, P.B, I.a2_2.v, "V(B∈4/0)");
  await page.click("#a2 .btn-trace");
  assert.equal((await text(page, "#a2 .q-status")).trim(), "2 réponses justes sur 2");
  assert.ok(!(await page.isDisabled(`#${id} [data-act=correction]`)), "la correction peut se superposer");
  // Q2 a) : droite (AB), projetés des extrémités
  await outil(page, id, "droite"); await clic(page, id, P.A); await clic(page, id, P.B);
  const mAB = [(P.A[0] + P.B[0]) / 2, (P.A[1] + P.B[1]) / 2];
  for (const f of ["a2_1", "a2_2"]) {
    const it = I[f];
    await outil(page, id, "proj"); await clic(page, id, [it.o[0] + it.v[0], it.o[1] + it.v[1]]); await clic(page, id, mAB);
  }
  await page.click("#a3 .btn-trace");
  assert.equal((await text(page, "#a3 .q-status")).trim(), "3 réponses justes sur 3");
  // Q3 et Q4 : même chose pour C
  await page.fill("#in-a5", "2,62 m/s"); await page.click("#a5 .btn-validate");
  await vecteur(page, id, P.C, I.a6_1.v, "V(C∈1/0)");
  await page.click("#a6 .btn-trace");
  await outil(page, id, "droite"); await clic(page, id, P.A); await clic(page, id, P.C);
  const mAC = [(P.A[0] + P.C[0]) / 2, (P.A[1] + P.C[1]) / 2];
  for (const f of ["a2_1", "a6_1"]) {
    const it = I[f];
    await outil(page, id, "proj"); await clic(page, id, [it.o[0] + it.v[0], it.o[1] + it.v[1]]); await clic(page, id, mAC);
  }
  await page.click("#a7 .btn-trace");
  assert.equal((await text(page, "#a7 .q-status")).trim(), "3 réponses justes sur 3");
  // étiquettes Q2 b), Q4 b), Q5
  await repondreTout(page, "arbre-transmission");
  for (const g of ["a4", "a8", "a9"]) await page.click(`#${g} .btn-fast`);
  assert.equal((await text(page, "#score-val")).replace(/\s/g, ""), "20,0/20");
  assert.equal((await text(page, "#recap .final-note")).trim(), "20,0/20");
  assert.deepEqual(errors, []);
  await context.close();
});

test("ellipsographe, examen : CIR construit à l'équerre, rien n'est corrigé avant la remise", async () => {
  const { context, page, errors } = await open("?ex=ellipsographe");
  await page.click("[data-mode=exam]");
  const id = "at-ellipsographe-1", P = await pts(page, id), I = await items(page, id);
  assert.equal(await page.locator(".btn-trace:visible").count(), 0);
  // perpendiculaire à l'axe x en A, perpendiculaire à l'axe y en B, point à l'intersection
  await outil(page, id, "perp"); await clic(page, id, [P.O[0] + 40, P.O[1]]); await clic(page, id, P.A);
  await outil(page, id, "perp"); await clic(page, id, [P.O[0], P.O[1] - 100]); await clic(page, id, P.B);
  const cir = Object.values(I).find((x) => x.k === "pt").p;
  await outil(page, id, "point"); await clic(page, id, [cir[0] + 0.6, cir[1] - 0.6]);
  await nommer(page, id, "I2/0");
  const pt = await page.evaluate(() => window.__ateliers__[0].objs.at(-1).p);
  assert.ok(Math.hypot(pt[0] - cir[0], pt[1] - cir[1]) < 1e-6, "le point s'accroche à l'intersection");
  await vecteur(page, id, P.A, [30, 0], "V(A∈1/0)");
  assert.match(await text(page, "#score-count"), /réponse\(s\) renseignée\(s\)/);
  assert.ok(await page.locator("#d8 .q-expl[hidden]").count(), "pas de correction avant la remise");
  await page.click("#exam-submit"); await page.click("#exam-submit");
  assert.ok(await page.locator("body.graded").count());
  assert.match(await page.getAttribute("#it-d8_1 .sol", "class"), /is-ok/);
  assert.match(await page.getAttribute("#it-d5_1 .sol", "class"), /is-ok/);
  assert.match(await page.getAttribute("#it-d10_1 .sol", "class"), /is-ko/);
  assert.equal((await text(page, "#it-d10_1 .it-diag")).trim(), "non tracé");
  assert.equal(await page.getAttribute(`#${id} [data-act=correction]`, "aria-pressed"), "true");
  assert.ok(await page.locator(`#${id} .at-corr line`).count() > 5, "corrections superposées");
  assert.match(await text(page, "#recap .final-note"), /\/20/);
  assert.deepEqual(errors, []);
  await context.close();
});

for (const key of ACTS) {
  test(`${key} : solution complète posée sur chaque feuille — 20/20, sans erreur`, async () => {
    const { context, page, errors } = await open("?ex=" + key);
    await page.click("[data-mode=training]");
    for (const id of await page.$$eval(".atelier", (l) => l.map((x) => x.id))) await poserSolution(page, id);
    await repondreTout(page, key);
    for (const b of await page.locator(".btn-validate").all()) await b.click();
    for (const b of await page.locator(".btn-trace").all()) await b.click();
    for (const b of await page.locator(".fast-q:not(.trace) .btn-fast").all()) await b.click();
    assert.equal((await text(page, "#score-val")).replace(/\s/g, ""), "20,0/20");
    assert.equal(await page.locator(".sol.is-ko, .q.is-ko, .q.is-half").count(), 0);
    assert.deepEqual(errors, []);
    await context.close();
  });
}

test("téléphone et impression : la feuille reste utilisable, la barre d'outils disparaît à l'impression", async () => {
  const { context, page, errors } = await open("?ex=pompe-petrole", { width: 390, height: 844 });
  await page.click("[data-mode=training]");
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
  const box = await page.locator(".at-stage").first().boundingBox();
  assert.ok(box.width > 280 && box.height >= 300, JSON.stringify(box));
  await page.emulateMedia({ media: "print" });
  assert.ok(!(await page.isVisible(".at-bar")));
  assert.ok(await page.isVisible(".at-svg"));
  assert.deepEqual(errors, []);
  await context.close();
});
