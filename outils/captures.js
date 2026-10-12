// Images photographiées dans la page (Playwright + Chromium), pour l'accueil :
//   - src/images/originaux/carte-<activité>.png : la feuille de chaque activité, corrections superposées ;
//   - src/images/originaux/carte-cours-1.png, carte-cours-2.png, carte-atelier.png, carte-analytique.png,
//     carte-etude.png : une figure de chaque cours, l'atelier libre, les rubriques à venir ;
//   - src/images/originaux/accueil-*.png : les quatre feuilles du montage de l'accueil.
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node outils/captures.js && bash outils/preparer-images.sh && python3 src/generer.py
const path = require("node:path");
const { chromium } = require("playwright");
(async () => {
  const racine = path.join(__dirname, "..");
  const ORIG = path.join(racine, "src/images/originaux");
  const URL = "file://" + path.join(racine, "index.html");
  const FIGE = "*{animation:none!important;transition:none!important}";
  // feuille de 960 × 540 px : la vue 16:9 la remplit sans bandes
  const CADRE16 = ".at-zone{display:block!important}.atelier{width:960px!important}.at-stage{width:960px;height:540px!important}";
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  const ACTS = ["arbre-transmission", "embiellage-moto", "pompe-petrole", "ellipsographe", "portail-vis", "chargeur-bobcat",
    "suspension-vtt"];
  // feuille d'une activité, toutes corrections superposées, vue recadrée sur le mécanisme
  async function feuille(act, i, fichier, cadre) {
    await p.goto(URL + "?ex=" + act);
    await p.click("[data-mode=training]");
    await p.addStyleTag({ content: FIGE + CADRE16 });
    const id = `at-${act}-${i}`;
    await p.evaluate(([id, cadre]) => {
      const a = window.__ateliers__.find((x) => x.root.id === id);
      Object.keys(a.cfg.corr).forEach((g) => a.reveler(g));
      if (cadre) { a.vue = { x: cadre[0], y: cadre[1], w: cadre[2], h: cadre[2] * 9 / 16 }; a.appliquerVue(); }
    }, [id, cadre]);
    await p.locator("#" + id + " .at-stage").screenshot({ path: path.join(ORIG, fichier) });
  }
  // vues recadrées au format 16:9 des vignettes : x, y et largeur (mm de feuille)
  const CADRES = { "arbre-transmission": [0, 16, 165], "embiellage-moto": [0, 6, 180], "pompe-petrole": [0, 14, 185],
    "ellipsographe": [22, 22, 128], "portail-vis": [0, 12, 190], "chargeur-bobcat": [10, 148, 160],
    "suspension-vtt": [60, 12, 150] };
  for (const a of ACTS) await feuille(a, 1, `carte-${a}.png`, CADRES[a]);
  for (const [a, f] of [["ellipsographe", "accueil-1.png"], ["embiellage-moto", "accueil-2.png"], ["pompe-petrole", "accueil-3.png"],
    ["chargeur-bobcat", "accueil-4.png"]]) await feuille(a, 1, f, CADRES[a]);
  // cours 1 : la roue de vélo et ses trajectoires
  await p.goto(URL + "?ex=cours-cinematique-analytique");
  await p.click("#ca-velo .ca-go");
  await p.waitForTimeout(4200);
  await p.click("#ca-velo .ca-go");
  await p.locator("#ca-velo .simu-fig").screenshot({ path: path.join(ORIG, "carte-cours-1.png") });
  await p.click("#ca-mruv [data-pre=a]");
  await p.locator("#ca-mruv .simu-fig").screenshot({ path: path.join(ORIG, "carte-analytique.png") });
  // cours 2 : le CIR de la bielle, toutes étapes
  await p.goto(URL + "?ex=cours-cinematique-graphique");
  for (let i = 0; i < 5; i++) await p.click("#dm-cir .dm-suiv");
  await p.addStyleTag({ content: FIGE + "#dm-cir .at-stage{width:960px;aspect-ratio:auto!important;height:552px}" });
  await p.locator("#dm-cir .at-stage").screenshot({ path: path.join(ORIG, "carte-cours-2.png") });
  // atelier libre : une construction d'équiprojectivité tracée par le script
  await p.goto(URL + "?ex=atelier-libre");
  await p.evaluate(() => {
    const a = window.__ateliers__[0];
    const A = [70, 120], B = [190, 80], VA = [30, 40], u = [B[0] - A[0], B[1] - A[1]], L = Math.hypot(u[0], u[1]);
    const n = [u[0] / L, u[1] / L], pr = VA[0] * n[0] + VA[1] * n[1], H = [A[0] + n[0] * pr, A[1] + n[1] * pr];
    const K = [B[0] + n[0] * pr, B[1] + n[1] * pr], d = [0, -1], t = pr / (d[0] * n[0] + d[1] * n[1]);
    a.objs = [{ t: "pt", p: A, nom: "A", c: "#1C2530" }, { t: "pt", p: B, nom: "B", c: "#1C2530" },
      { t: "dr", p: A, d: n, c: "#1F5FA8" }, { t: "ve", a: A, b: [A[0] + VA[0], A[1] + VA[1]], nom: "V(A∈1/0)", c: "#1F5FA8" },
      { t: "sg", a: [A[0] + VA[0], A[1] + VA[1]], b: H, pointille: true, c: "#1B7A43" }, { t: "sg", a: B, b: K, c: "#1B7A43" },
      { t: "dr", p: K, d: [-n[1], n[0]], c: "#7B3FA0" }, { t: "ve", a: B, b: [B[0] + d[0] * t, B[1] + d[1] * t], nom: "V(B∈1/0)", c: "#B42318" }];
    a.vue = { x: 35, y: 30, w: 200, h: 112.5 }; a.changer(); a.appliquerVue();
  });
  await p.addStyleTag({ content: FIGE + CADRE16 });
  await p.locator("#at-libre .at-stage").screenshot({ path: path.join(ORIG, "carte-atelier.png") });
  // étude de cas à venir : le chargeur seul
  await p.goto(URL + "?ex=chargeur-bobcat");
  await p.click("[data-mode=training]");
  await p.addStyleTag({ content: FIGE + CADRE16 });
  await p.evaluate(() => { const a = window.__ateliers__[0]; a.vue = { x: 10, y: 150, w: 160, h: 90 }; a.appliquerVue(); });
  await p.locator(".at-stage").first().screenshot({ path: path.join(ORIG, "carte-etude.png") });
  await b.close();
})();
