// Tests unitaires du moteur de correction appliqué aux activités, et des réponses attendues des constructions.
//   node --test tests/correction.test.js
// Le moteur (Grading), la configuration (__EXOS__, __ATELIERS__) et les questions sont lus dans la page générée :
// on teste exactement ce que l'élève utilisera.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const code = html.slice(html.indexOf("/*GRADING-START*/"), html.indexOf("/*GRADING-END*/"));
const mod = { exports: {} };
new Function("module", code + "\nmodule.exports = Grading;")(mod);
const G = mod.exports;
const EXOS = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
const AT = JSON.parse(html.match(/window\.__ATELIERS__ = (.*?);<\/script>/)[1]);
const ANA = ["imprimante-3d", "vanne-admission", "agv", "moteur-electrique"];
const ACTS = ["arbre-transmission", "embiellage-moto", "pompe-petrole", "ellipsographe", "portail-vis", "chargeur-bobcat", "suspension-vtt"];
const crypto = require("node:crypto");
const score = (ans, gr) => { const r = G.grade(ans, gr); return r.invalid ? "invalid" : r.score; };
const fr = (x, d) => x.toFixed(d).replace(".", ",");

// questions à étiquettes, lues dans les modèles de la page : étiquettes proposées et réponse attendue de chaque case
function etiquettes(key) {
  const tpl = html.match(new RegExp(`<template id="tpl-parts-${key}">([\\s\\S]*?)</template>`))[1];
  const out = [];
  for (const m of tpl.matchAll(/<div class="fast-q grp" id="(\w+)">([\s\S]*?)<\/tbody><\/table>/g)) {
    const banque = [...m[2].matchAll(/<button type="button" class="etq"[^>]*>([^<]*)<\/button>/g)].map((x) => x[1].replace(/&#x27;/g, "'"));
    const cases = [...m[2].matchAll(/data-q="(\w+)"/g)].map((x) => x[1]);
    const attendus = [...m[2].matchAll(/<tr><td>[\s\S]*?<\/td><td>([^<]*)<\/td><\/tr>/g)].map((x) => x[1].replace(/&#x27;/g, "'"));
    out.push({ id: m[1], banque, cases, attendus });
  }
  return out;
}

test("gabarit : copie conforme de celui du dépôt Chaîne fonctionnelle (empreinte SHA-256)", () => {
  const g = fs.readFileSync(path.join(__dirname, "..", "src", "gabarit-exercice-interactif.html"));
  assert.equal(crypto.createHash("sha256").update(g).digest("hex"), "d39968afd8d398aed6e0b56968445e3b9ddbd19d503efe9adabef898d93db91a");
});

test("configuration : quatre activités analytiques puis sept activités graphiques, barème cohérent", () => {
  assert.deepEqual(Object.keys(EXOS), ANA.concat(ACTS));
  for (const k of ANA) {
    const E = EXOS[k];
    assert.equal(E.consignes, "tpl-consignes-ana", k);
    assert.ok(E.minutes === E.parts.reduce((s, p) => s + p.minutes, 0), k);
    for (const p of E.parts) assert.equal(Object.keys(E.qcfg).filter((id) => E.qcfg[id].part === p.num).length, p.points, `${k} ${p.num}`);
  }
  assert.ok(!EXOS["vanne-admission"].atelier && EXOS["agv"].atelier && AT["at-agv-2"] && !AT["at-agv-1"]);
  for (const k of ACTS) {
    const E = EXOS[k];
    assert.ok(E.atelier && E.parts.length >= 1 && E.minutes === E.parts.reduce((s, p) => s + p.minutes, 0), k);
    for (const p of E.parts) {
      const ids = Object.keys(E.qcfg).filter((id) => E.qcfg[id].part === p.num);
      assert.equal(ids.length, p.points, `${k} partie ${p.num}`);
      assert.ok(AT[`at-${k}-${p.num}`], `${k} : feuille de la partie ${p.num}`);
    }
    for (const id of Object.keys(E.qcfg)) assert.ok(["num", "code", "chasles"].includes(E.qcfg[id].grader.type), id);
  }
  assert.equal(EXOS["suspension-vtt"].parts.length, 3);
});

test("constructions : chaque élément attendu a son champ, corrigé « juste » seulement", () => {
  for (const k of ACTS) {
    const E = EXOS[k];
    for (const [aid, cfg] of Object.entries(AT).filter(([a]) => a.startsWith(`at-${k}-`))) {
      for (const [gid, fids] of Object.entries(cfg.groupes)) {
        assert.ok(cfg.corr[gid].length > 0, `${aid} ${gid} : correction`);
        for (const fid of fids) {
          assert.ok(cfg.items[fid], fid);
          assert.equal(score("juste", E.qcfg[fid].grader), 1, fid);
          assert.equal(score("faux", E.qcfg[fid].grader), 0, fid);
          assert.equal(score("", E.qcfg[fid].grader), "invalid", fid);
        }
      }
    }
  }
});

test("constructions : les éléments attendus tiennent dans leur feuille et partent d'un point de la figure", () => {
  for (const [aid, cfg] of Object.entries(AT)) {
    const noms = Object.fromEntries(cfg.pts.map((p) => [p[0], [p[1], p[2]]]));
    const dedans = (p) => p[0] >= -0.5 && p[0] <= cfg.w + 0.5 && p[1] >= -0.5 && p[1] <= cfg.h + 0.5;
    for (const [fid, it] of Object.entries(cfg.items || {})) {
      if (it.k === "courbe") {
        const b = cfg.graphes[it.g].box;
        assert.ok(it.pts.every((q) => q[0] >= b[0] - 1e-6 && q[0] <= b[2] + 1e-6 && q[1] >= b[1] - 1e-6 && q[1] <= b[3] + 1e-6), `${aid} ${fid} : courbe hors du graphe`);
        continue;
      }
      const o = it.o || it.p || it.c;
      assert.ok(dedans(o), `${aid} ${fid} : origine hors de la feuille`);
      if (it.k === "ve") {
        assert.ok(dedans([o[0] + it.v[0], o[1] + it.v[1]]), `${aid} ${fid} : extrémité hors de la feuille`);
        assert.ok(Math.hypot(it.v[0], it.v[1]) > 8, `${aid} ${fid} : vecteur trop court pour être tracé`);
        assert.ok(Object.values(noms).some((q) => Math.hypot(q[0] - o[0], q[1] - o[1]) < 1e-3), `${aid} ${fid} : origine sur un point nommé`);
      }
    }
  }
});

// vecteur attendu d'un item, retrouvé par son nom
function vecteur(aid, nom) {
  const it = Object.values(AT[aid].items).find((x) => x.k === "ve" && x.nom === nom);
  assert.ok(it, `${aid} : ${nom}`);
  return it;
}
function proj(it, sur) { const u = [sur[0] - it.o[0], sur[1] - it.o[1]], L = Math.hypot(u[0], u[1]); return (it.v[0] * u[0] + it.v[1] * u[1]) / L; }

test("cinématique : les vitesses attendues vérifient équiprojectivité, CIR et composition", () => {
  // embiellage : équiprojectivité sur chaque bielle
  const e = "at-embiellage-moto-1", B = vecteur(e, "V(B∈1/0)"), C = vecteur(e, "V(C∈2/0)"), D = vecteur(e, "V(D∈3/0)");
  assert.ok(Math.abs(proj(B, C.o) + proj(C, B.o)) < 0.02, "B et C : projections égales sur (BC)");
  assert.ok(Math.abs(proj(B, D.o) + proj(D, B.o)) < 0.02, "B et D : projections égales sur (BD)");
  // ellipsographe : V(M) et V(B) perpendiculaires à IM et IB, proportionnelles aux distances
  const l = "at-ellipsographe-1", I = Object.values(AT[l].items).find((x) => x.k === "pt").p;
  for (const n of ["V(M∈2/0)", "V(B∈2/0)"]) {
    const it = vecteur(l, n), im = [it.o[0] - I[0], it.o[1] - I[1]];
    assert.ok(Math.abs(it.v[0] * im[0] + it.v[1] * im[1]) < 0.05, n + " ⊥ IM");
    assert.ok(Math.abs(Math.hypot(...it.v) / Math.hypot(...im) - 30 / 39.83) < 0.01, n + " : ω constant");
  }
  // VTT, document 3 : V(C∈S4/S0) = V(C∈S4/S5) + V(C∈S5/S0), avec V(C∈S4/S0) de 15 m/s (50 mm)
  const v = "at-suspension-vtt-3", c = vecteur(v, "V(C∈S3/S0)"), r = vecteur(v, "V(C∈S4/S5)");
  assert.ok(Math.abs(Math.hypot(...c.v) - 50) < 0.01);
  assert.ok(Math.hypot(...r.v) < Math.hypot(...c.v), "la composante relative est plus courte que la vitesse absolue");
});

test("valeurs numériques : valeur et unité notées, valeur seule à moitié, autre valeur fausse", () => {
  let n = 0;
  for (const k of ANA.concat(ACTS)) {
    for (const [id, q] of Object.entries(EXOS[k].qcfg)) {
      const g = q.grader;
      if (g.type !== "num" || !g.unit) continue;
      n++;
      const v = g.value, d = Math.abs(v) < 0.1 ? 4 : 3;
      assert.equal(score(`${fr(v, d)} ${g.unit.label}`, g), 1, `${k} ${q.label}`);
      assert.equal(score(`${fr(v, d)}`, g), 0.5, `${k} ${q.label} sans unité`);
      assert.equal(score(`${fr(v * (1 + 3 * g.relTol), d)} ${g.unit.label}`, g), 0, `${k} ${q.label} hors tolérance`);
      for (const w of g.variants || []) assert.equal(score(`${fr(w.value, 3)} ${w.unit.label}`, g), 1, `${k} ${q.label} en ${w.unit.label}`);
    }
  }
  assert.ok(n >= 45, `${n} questions numériques`);
  // quelques réponses d'élèves, écrites de plusieurs façons
  const arbre = EXOS["arbre-transmission"].qcfg;
  assert.equal(score("5,24 m/s", arbre.a1.grader), 1);
  assert.equal(score("V = 5.236 m.s-1", arbre.a1.grader), 1);
  assert.equal(score("5,24 m·s⁻¹", arbre.a1.grader), 1);
  assert.equal(score("5,24 km/h", arbre.a1.grader), 0.5);
  const pompe = Object.values(EXOS["pompe-petrole"].qcfg).find((q) => q.label === "Q7 b)").grader;
  assert.equal(score("6,2e-3 m3/s", pompe), 1);
  assert.equal(score("6,2·10^-3 m³/s", pompe), 1);
  assert.equal(score("6,2 L/s", pompe), 1);
  const port = EXOS["portail-vis"].qcfg;
  assert.equal(score("60 mm/s", port.e2.grader), 1);
  assert.equal(score("0,06 m/s", port.e2.grader), 1);
});

test("étiquettes : la réponse attendue est proposée et seule acceptée dans sa liste", () => {
  let n = 0;
  for (const k of ANA.concat(ACTS)) {
    for (const q of etiquettes(k)) {
      assert.equal(q.cases.length, q.attendus.length, q.id);
      q.cases.forEach((fid, i) => {
        const g = EXOS[k].qcfg[fid].grader, bonne = q.attendus[i];
        assert.ok(q.banque.includes(bonne), `${fid} : « ${bonne} » proposée`);
        for (const e of q.banque) assert.equal(score(e, g), e === bonne ? 1 : 0, `${fid} : ${e}`);
        n++;
      });
    }
  }
  assert.ok(n >= 30, `${n} cases à étiquettes`);
});

test("composition des vitesses : toute relation juste est acceptée, les autres refusées", () => {
  const bob = Object.values(EXOS["chargeur-bobcat"].qcfg).find((q) => q.label === "Q9 a)").grader;
  for (const ok of ["V(C∈5/0) = V(C∈5/4) + V(C∈4/0)", "V(C,5/0)=V(C,5/4)+V(C,4/0)", "V(C∈5/4) + V(C∈4/0) = V(C∈5/0)", "V C 5/0 = V C 4/0 + V C 5/4"])
    assert.equal(score(ok, bob), 1, ok);
  for (const ko of ["V(C∈5/0) = V(C∈5/4) + V(C∈0/4)", "V(C∈5/0) = V(C∈4/5) + V(C∈4/0)", "V(C∈5/0) = V(C∈5/4) - V(C∈4/0)"])
    assert.equal(score(ko, bob), 0, ko);
  const vtt = Object.values(EXOS["suspension-vtt"].qcfg).find((q) => q.label === "Q12").grader;
  assert.equal(score("V(C∈S4/S0) = V(C∈S4/S5) + V(C∈S5/S0)", vtt), 1);
  assert.equal(score("V(C∈S4/S0) = V(C∈S5/S4) + V(C∈S5/S0)", vtt), 0);
});

// ------------------------------------------------------------------ cinématique analytique
const num = (k, label) => Object.values(EXOS[k].qcfg).find((q) => q.label === label).grader;
const cases = (k, label) => Object.values(EXOS[k].qcfg).filter((q) => q.label.startsWith(label + " — ")).map((q) => q.grader.value);

test("cinématique analytique : valeurs des quatre études (calculées depuis les données de la séquence)", () => {
  const near = (a, b, e = 1e-3) => assert.ok(Math.abs(a - b) <= e * Math.max(1, Math.abs(b)), `${a} ≠ ${b}`);
  // imprimante 3D : ralentissement uniforme sur 25 mm depuis 64 mm/s
  near(num("imprimante-3d", "Q5 a)").value, 0.78125);
  near(num("imprimante-3d", "Q5 b)").value, -81.92);
  assert.deepEqual(cases("imprimante-3d", "Q6 a)").map((v) => +v.toFixed(5)), [-40.96, 64, 114, -81.92, 64, -81.92, 2.78125, 139]);
  // vanne : Vmax = 375/60 × 0,5 ; la somme des cinq distances fait 3 mm
  near(num("vanne-admission", "Q1 b)").value, 3.125);
  const d = ["Q2 c)", "Q3 c)", "Q4 b)", "Q5 c)", "Q6"].map((l) => num("vanne-admission", l).value);
  near(d.reduce((a, b) => a + b, 0), 3);
  near(num("vanne-admission", "Q8").value, 0.25 + d[4] / 3.125 + 0.8);
  assert.ok(num("vanne-admission", "Q3 b)").abs);
  assert.equal(score("10,625 mm/s²", num("vanne-admission", "Q3 b)")), 1);
  assert.equal(score("-10,625 mm/s2", num("vanne-admission", "Q3 b)")), 1);
  // AGV : continuité en t1 et 21 km en 300 s
  near(num("agv", "Q3 a)").value, 3); near(num("agv", "Q3 b)").value, -30);
  near(num("agv", "Q3 c)").value, 37 / 0.35); near(num("agv", "Q4 c)").value, 23.24286, 1e-4);
  assert.equal(score("23 243 m", num("agv", "Q4 c)")), 1);
  assert.equal(score("23,24 km", num("agv", "Q4 c)")), 1);
  // moteur : θ(t) = −20π t + 220π dans le repère absolu
  near(num("moteur-electrique", "Q1.1 a)").value, 10 * Math.PI); near(num("moteur-electrique", "Q1.1 d)").value, -20 * Math.PI);
  assert.deepEqual(cases("moteur-electrique", "Q1.1 e)"), [-20, 20, -20, 220]);
  assert.equal(score("300 tr/min", num("moteur-electrique", "Q1.1 g)")), 1);
});

test("cases d'équation : un nombre, à la virgule ou au point ; zéro écrit ; autre valeur fausse", () => {
  const g = Object.values(EXOS["imprimante-3d"].qcfg).filter((q) => q.label.startsWith("Q6 a) — "));
  assert.equal(score("-40,96", g[0].grader), 1);
  assert.equal(score("−40.96", g[0].grader), 1);
  assert.equal(score("40,96", g[0].grader), 0);
  const zero = Object.values(EXOS["imprimante-3d"].qcfg).find((q) => q.label === "Q4 a) — x : coefficient de t").grader;
  assert.equal(score("0", zero), 1);
  assert.equal(score("0,1", zero), 0);
  assert.equal(score("", zero), "invalid");
});

test("courbes attendues : échantillons réguliers, phases accolées, valeurs propres à chaque phase", () => {
  for (const [aid, cfg] of Object.entries(AT).filter(([, c]) => c.graphes)) {
    for (const [fid, it] of Object.entries(cfg.items)) {
      assert.equal(it.k, "courbe", fid);
      for (let i = 1; i < it.pts.length; i++) assert.ok(it.pts[i][0] > it.pts[i - 1][0] && it.pts[i][0] - it.pts[i - 1][0] < 4, `${aid} ${fid} : pas des échantillons`);
      assert.ok(Math.abs(it.pts[0][0] - it.x0) < 1e-6 && Math.abs(it.pts.at(-1)[0] - it.x1) < 1e-6, fid);
    }
  }
  // graphe discontinu : la phase 2 du moteur vaut 0 dès son début, la phase 3 vaut −20π dès t = 10 s
  const c = AT["at-moteur-electrique-1"], G = c.graphes[1], y = (q) => (G.o[1] - q[1]) / G.ky;
  assert.ok(Math.abs(y(c.items.k8_2.pts[0])) < 1e-3);
  assert.ok(Math.abs(y(c.items.k8_3.pts[0]) + 20 * Math.PI) < 1e-2);
});
