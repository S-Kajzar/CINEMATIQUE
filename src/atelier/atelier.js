/* =====================================================================================================
   ATELIER DE CONSTRUCTION GRAPHIQUE — cinématique graphique
   Une instance par élément .atelier (document réponse d'une activité, atelier libre) ; une démonstration pas à
   pas par élément .at-demo (cours). Configuration : window.__ATELIERS__[identifiant] (générée par src/atelier.py).

   La feuille est en millimètres (y vers le bas). Les outils reprennent ceux du papier : règle (droite, segment),
   équerre (perpendiculaire, parallèle, projeté orthogonal), compas (cercle, report de longueur), vecteur, mesure.
   Chaque construction attendue par une question (« item ») est vérifiée en continu : le champ masqué que lit le
   moteur du gabarit reçoit « juste », « faux » ou rien (rien de tracé) ; la note et les modes restent ceux du
   gabarit. Une fois la question corrigée, sa correction se superpose à la feuille.
   ===================================================================================================== */
(function () {
  "use strict";
  var CFGS = window.__ATELIERS__ || {};
  var COULEURS = [["#1F5FA8", "Bleu"], ["#1B7A43", "Vert"], ["#7B3FA0", "Violet"], ["#1C2530", "Noir"]];
  var ROUGE = "#C62828", ORANGE = "#D35400";
  var SNAP_PX = 11;

  // ------------------------------------------------------------------ géométrie
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function add(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function mul(a, k) { return [a[0] * k, a[1] * k]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1]; }
  function crs(a, b) { return a[0] * b[1] - a[1] * b[0]; }
  function len(a) { return Math.hypot(a[0], a[1]); }
  function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }
  function unit(a) { var n = len(a) || 1; return [a[0] / n, a[1] / n]; }
  function perp(a) { return [-a[1], a[0]]; }
  /* angle d'une direction, en degrés, sens trigonométrique à l'écran */
  function ang(a) { return Math.atan2(-a[1], a[0]) * 180 / Math.PI; }
  /* écart angulaire entre deux vecteurs (0 à 180°) ; entre deux directions (0 à 90°) */
  function ecartV(a, b) { var c = dot(unit(a), unit(b)); return Math.acos(Math.max(-1, Math.min(1, c))) * 180 / Math.PI; }
  function ecartD(a, b) { var e = ecartV(a, b); return Math.min(e, 180 - e); }
  function projLigne(p, q, d) { var u = unit(d); return add(q, mul(u, dot(sub(p, q), u))); }
  function distLigne(p, q, d) { return Math.abs(crs(unit(d), sub(p, q))); }
  function distSeg(p, a, b) {
    var d = sub(b, a), L2 = dot(d, d), t = L2 ? Math.max(0, Math.min(1, dot(sub(p, a), d) / L2)) : 0;
    return dist(p, add(a, mul(d, t)));
  }
  /* courbes : droite (bornée ou non) {k:"L", p, d, t0, t1} — d non normé, paramètre t le long de d — ou cercle {k:"C"} */
  function interLL(A, B) {
    var den = crs(A.d, B.d);
    if (Math.abs(den) < 1e-9) return [];
    var w = sub(B.p, A.p), t = crs(w, B.d) / den, u = crs(w, A.d) / den;
    if (t < A.t0 - 1e-9 || t > A.t1 + 1e-9 || u < B.t0 - 1e-9 || u > B.t1 + 1e-9) return [];
    return [add(A.p, mul(A.d, t))];
  }
  function interLC(A, C) {
    var f = sub(A.p, C.c), a = dot(A.d, A.d), b = 2 * dot(f, A.d), c = dot(f, f) - C.r * C.r, D = b * b - 4 * a * c, out = [];
    if (D < 0) return out;
    [(-b - Math.sqrt(D)) / (2 * a), (-b + Math.sqrt(D)) / (2 * a)].forEach(function (t) {
      if (t >= A.t0 - 1e-9 && t <= A.t1 + 1e-9) out.push(add(A.p, mul(A.d, t)));
    });
    return out;
  }
  function interCC(A, B) {
    var d = dist(A.c, B.c);
    if (d < 1e-9 || d > A.r + B.r || d < Math.abs(A.r - B.r)) return [];
    var a = (A.r * A.r - B.r * B.r + d * d) / (2 * d), h = Math.sqrt(Math.max(0, A.r * A.r - a * a));
    var u = unit(sub(B.c, A.c)), m = add(A.c, mul(u, a));
    return [add(m, mul(perp(u), h)), sub(m, mul(perp(u), h))];
  }
  function inter(A, B) {
    if (A.k === "L" && B.k === "L") return interLL(A, B);
    if (A.k === "L") return interLC(A, B);
    if (B.k === "L") return interLC(B, A);
    return interCC(A, B);
  }
  function surCourbe(p, C) {
    if (C.k === "C") { var v = sub(p, C.c); return add(C.c, mul(unit(v), C.r)); }
    var t = dot(sub(p, C.p), C.d) / dot(C.d, C.d);
    t = Math.max(C.t0, Math.min(C.t1, t));
    return add(C.p, mul(C.d, t));
  }
  /* segment visible d'une droite infinie dans le rectangle [x0, x1] × [y0, y1] */
  function clipLigne(p, d, x0, y0, x1, y1) {
    var t0 = -1e9, t1 = 1e9;
    function borne(q, dd, lo, hi) {
      if (Math.abs(dd) < 1e-12) return q >= lo && q <= hi;
      var a = (lo - q) / dd, b = (hi - q) / dd;
      if (a > b) { var t = a; a = b; b = t; }
      t0 = Math.max(t0, a); t1 = Math.min(t1, b);
      return true;
    }
    if (!borne(p[0], d[0], x0, x1) || !borne(p[1], d[1], y0, y1) || t0 > t1) return null;
    return [add(p, mul(d, t0)), add(p, mul(d, t1))];
  }

  // ------------------------------------------------------------------ écriture
  function fr(x, d) { return x.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/^-/, "−"); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function n2(x) { return Math.round(x * 100) / 100; }
  /* nom d'un vecteur ou d'un point, ramené à sa forme compacte : « V(A∈4/0) », « VA4/0 », « A∈4/0 » → « a40 » */
  function nomNorm(s) {
    var c = String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
    if (/^v[a-z]/.test(c)) c = c.slice(1);
    return c;
  }
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  // ------------------------------------------------------------------ dessin (chaînes SVG, unités : mm de feuille)
  function svgLigne(a, b, c, w, cls, dash) {
    return '<line x1="' + n2(a[0]) + '" y1="' + n2(a[1]) + '" x2="' + n2(b[0]) + '" y2="' + n2(b[1]) + '" stroke="' + c +
      '" stroke-width="' + w + '"' + (dash ? ' stroke-dasharray="' + dash + '"' : "") + ' class="' + (cls || "") + '"/>';
  }
  function svgFleche(a, b, c, w, k, cls) {
    var L = dist(a, b);
    if (L < 1e-6) return "";
    var u = unit(sub(b, a)), h = Math.min(10 / k, L * 0.6), e = 3.6 / k, base = sub(b, mul(u, h));
    var p1 = add(base, mul(perp(u), e)), p2 = sub(base, mul(perp(u), e));
    return svgLigne(a, sub(b, mul(u, h * 0.8)), c, w, cls) + '<polygon points="' + n2(b[0]) + "," + n2(b[1]) + " " + n2(p1[0]) + "," +
      n2(p1[1]) + " " + n2(p2[0]) + "," + n2(p2[1]) + '" fill="' + c + '" class="' + (cls || "") + '"/>';
  }
  function svgTexte(p, s, c, k, taille, cls, ancre) {
    return '<text x="' + n2(p[0]) + '" y="' + n2(p[1]) + '" font-size="' + n2((taille || 14) / k) + '" fill="' + c +
      '" class="at-lab ' + (cls || "") + '" text-anchor="' + (ancre || "start") + '" stroke-width="' + n2(3.2 / k) + '">' + esc(s) + "</text>";
  }
  function svgCroix(p, c, k, w) {
    var r = 3.6 / k;
    return svgLigne([p[0] - r, p[1] - r], [p[0] + r, p[1] + r], c, w || 1.8) + svgLigne([p[0] - r, p[1] + r], [p[0] + r, p[1] - r], c, w || 1.8);
  }
  /* étiquette d'un vecteur : au milieu, décalée du côté gauche du sens de parcours */
  function posEtiquette(a, b, k) {
    var u = unit(sub(b, a)), m = mul(add(a, b), 0.5), n = perp(u);
    if (n[1] > 0) n = mul(n, -1);
    return add(m, mul(n, 9 / k));
  }

  // =====================================================================================================
  function Atelier(root, cfg) {
    var self = this;
    this.root = root; this.cfg = cfg;
    this.svg = $("svg.at-svg", root);
    this.W = cfg.w; this.H = cfg.h;
    this.L = { grille: $(".at-grille", this.svg), cons: $(".at-cons", this.svg), corr: $(".at-corr", this.svg), tmp: $(".at-tmp", this.svg) };
    this.objs = []; this.hist = []; this.futur = []; this.nid = 1;
    this.tool = cfg.outil || "vecteur"; this.step = []; this.couleur = COULEURS[0][0];
    this.sel = null; this.hover = null; this.mesure = null; this.curseur = null;
    this.vue = { x: 0, y: 0, w: this.W, h: this.H };
    this.grille = !!cfg.grille; this.voirCorr = false; this.reveles = {};
    this.items = cfg.items || {}; this.etats = {};
    this.zone = root.closest(".at-zone") || root;
    this.figPts = (cfg.pts || []).map(function (q) { return { p: [q[1], q[2]], nom: q[0] }; });
    this.figCourbes = (cfg.lignes || []).map(function (l) { return { k: "L", p: [l[0], l[1]], d: unit([l[2], l[3]]), t0: -1e9, t1: 1e9, fixe: true }; })
      .concat((cfg.cercles || []).map(function (c) { return { k: "C", c: [c[0], c[1]], r: c[2], fixe: true }; }));

    // ---------- barre d'outils
    $$("[data-outil]", root).forEach(function (b) {
      b.addEventListener("click", function () { self.choisir(b.getAttribute("data-outil")); });
    });
    $$("[data-couleur]", root).forEach(function (b) {
      b.addEventListener("click", function () {
        self.couleur = b.getAttribute("data-couleur");
        $$("[data-couleur]", root).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        if (self.sel && self.sel.t !== "fig") { self.memo(); self.sel.c = self.couleur; self.changer(); }
      });
    });
    function act(nom, f) { var b = $('[data-act="' + nom + '"]', root); if (b) b.addEventListener("click", f); return b; }
    act("annuler", function () { self.annuler(); });
    act("retablir", function () { self.retablir(); });
    var eff = act("effacer", function () {
      if (!self.objs.length) return;
      if (eff.dataset.arme) { self.memo(); self.objs = []; self.sel = null; self.changer(); desarmer(); return; }
      eff.dataset.arme = "1"; eff.textContent = "Confirmer"; eff.classList.add("arme");
      self.tEff = setTimeout(desarmer, 3000);
    });
    function desarmer() { delete eff.dataset.arme; eff.textContent = "Tout effacer"; eff.classList.remove("arme"); clearTimeout(self.tEff); }
    act("zoom-plus", function () { self.zoomer(1.4); });
    act("zoom-moins", function () { self.zoomer(1 / 1.4); });
    act("ajuster", function () { self.ajuster(); });
    act("grille", function () { self.grille = !self.grille; this.setAttribute("aria-pressed", self.grille ? "true" : "false"); self.dessinerGrille(); });
    this.btnCorr = act("correction", function () {
      self.voirCorr = !self.voirCorr; this.setAttribute("aria-pressed", self.voirCorr ? "true" : "false"); self.rendre();
    });
    act("plein", function () { self.plein(); });
    act("vierge", function () { self.imprimerVierge(); });
    if (this.btnCorr) this.btnCorr.disabled = true;
    var bg = $('[data-act="grille"]', root); if (bg) bg.setAttribute("aria-pressed", this.grille ? "true" : "false");

    // ---------- propriétés de l'objet choisi
    this.prop = $(".at-prop", root);
    if (this.prop) {
      $(".at-p-nom", this.prop).addEventListener("change", function () {
        if (!self.sel) return; self.memo(); self.sel.nom = this.value.trim(); self.changer();
      });
      $(".at-p-long", this.prop).addEventListener("change", function () {
        var o = self.sel, L = parseFloat(String(this.value).replace(",", "."));
        if (!o || o.t !== "ve" || !(L > 0)) return;
        self.memo(); o.b = add(o.a, mul(unit(sub(o.b, o.a)), L)); self.changer();
      });
      $(".at-p-suppr", this.prop).addEventListener("click", function () {
        if (!self.sel) return; self.memo(); self.supprimer(self.sel); self.sel = null; self.changer();
      });
    }

    // ---------- souris, doigt, stylet
    var sv = this.svg, pointeurs = {}, glisse = null, pince = null;
    sv.addEventListener("pointerdown", function (e) {
      sv.focus({ preventScroll: true });
      pointeurs[e.pointerId] = [e.clientX, e.clientY];
      var ids = Object.keys(pointeurs);
      if (ids.length === 2) {  // deux doigts : déplacer et zoomer la vue
        var a = pointeurs[ids[0]], b = pointeurs[ids[1]];
        pince = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), m: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], vue: Object.assign({}, self.vue) };
        glisse = null; return;
      }
      sv.setPointerCapture(e.pointerId);
      var pan = self.tool === "main" || e.button === 1 || self.espace;
      glisse = { x: e.clientX, y: e.clientY, vue: Object.assign({}, self.vue), pan: pan, bouge: false, gomme: self.tool === "gomme" };
      if (glisse.gomme) { self.gommer(self.versFeuille(e), true); }
      e.preventDefault();
    });
    sv.addEventListener("pointermove", function (e) {
      if (pointeurs[e.pointerId]) pointeurs[e.pointerId] = [e.clientX, e.clientY];
      var ids = Object.keys(pointeurs);
      if (pince && ids.length === 2) {
        var a = pointeurs[ids[0]], b = pointeurs[ids[1]], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
        var m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], k = self.k(), f = pince.d / Math.max(10, d);
        var v = pince.vue, c = self.versFeuilleXY(pince.m[0], pince.m[1], v);
        var w = Math.max(self.W / 14, Math.min(self.W * 2.5, v.w * f)), h = v.h * w / v.w;
        self.vue = { x: c[0] - (c[0] - v.x) * w / v.w - (m[0] - pince.m[0]) / k, y: c[1] - (c[1] - v.y) * h / v.h - (m[1] - pince.m[1]) / k, w: w, h: h };
        self.appliquerVue(); return;
      }
      if (glisse && (glisse.pan || glisse.gomme)) {
        if (Math.hypot(e.clientX - glisse.x, e.clientY - glisse.y) > 3) glisse.bouge = true;
        if (glisse.gomme) { self.gommer(self.versFeuille(e), false); return; }
        if (glisse.bouge) {
          var kk = self.k();
          self.vue = Object.assign({}, glisse.vue, { x: glisse.vue.x - (e.clientX - glisse.x) / kk, y: glisse.vue.y - (e.clientY - glisse.y) / kk });
          self.appliquerVue();
        }
        return;
      }
      self.survol(self.versFeuille(e));
    });
    function fin(e) {
      delete pointeurs[e.pointerId];
      if (pince) { if (Object.keys(pointeurs).length < 2) pince = null; glisse = null; return; }
      if (!glisse) return;
      var g = glisse; glisse = null;
      if (g.gomme) { self.finGomme(); return; }
      if (g.pan && g.bouge) return;
      if (e.type === "pointercancel") return;
      self.clic(self.versFeuille(e));
    }
    sv.addEventListener("pointerup", fin);
    sv.addEventListener("pointercancel", fin);
    sv.addEventListener("pointerleave", function () { if (!glisse) { self.hover = null; self.rendreTmp(); } });
    sv.addEventListener("wheel", function (e) {
      if (!e.ctrlKey && !self.zone.classList.contains("plein")) return;  // la molette seule fait défiler la page
      e.preventDefault();
      self.zoomer(e.deltaY < 0 ? 1.15 : 1 / 1.15, self.versFeuille(e));
    }, { passive: false });
    sv.addEventListener("keydown", function (e) { self.clavier(e); });
    sv.addEventListener("keyup", function (e) { if (e.key === " ") self.espace = false; });
    sv.addEventListener("blur", function () { self.curseur = null; self.rendreTmp(); });
    if (window.ResizeObserver) new ResizeObserver(function () { self.appliquerVue(); }).observe(sv);

    // ---------- questions liées : bouton « Valider ma construction », état des items, correction
    this.lierQuestions();
    this.choisir(this.tool);
    this.appliquerVue();
    this.dessinerGrille();
    this.changer(true);
  }

  var P = Atelier.prototype;

  // ------------------------------------------------------------------ vue
  P.k = function () {
    var r = this.svg.getBoundingClientRect();
    return Math.min(r.width / this.vue.w, r.height / this.vue.h) || 1;
  };
  P.versFeuilleXY = function (cx, cy, vue) {
    var r = this.svg.getBoundingClientRect(), v = vue || this.vue;
    var k = Math.min(r.width / v.w, r.height / v.h) || 1;
    var ox = r.left + (r.width - v.w * k) / 2, oy = r.top + (r.height - v.h * k) / 2;
    return [v.x + (cx - ox) / k, v.y + (cy - oy) / k];
  };
  P.versFeuille = function (e) { return this.versFeuilleXY(e.clientX, e.clientY); };
  P.appliquerVue = function () {
    var v = this.vue;
    this.svg.setAttribute("viewBox", n2(v.x) + " " + n2(v.y) + " " + n2(v.w) + " " + n2(v.h));
    var z = $(".at-zoom", this.root);
    if (z) z.textContent = Math.round(this.W / v.w * 100) + " %";
    this.rendre();
  };
  P.zoomer = function (f, centre) {
    var v = this.vue, c = centre || [v.x + v.w / 2, v.y + v.h / 2];
    var w = Math.max(this.W / 14, Math.min(this.W * 1.2, v.w / f)), h = v.h * w / v.w;
    this.vue = { x: c[0] - (c[0] - v.x) * w / v.w, y: c[1] - (c[1] - v.y) * h / v.h, w: w, h: h };
    this.appliquerVue();
  };
  P.ajuster = function () { this.vue = { x: 0, y: 0, w: this.W, h: this.H }; this.appliquerVue(); };
  P.dessinerGrille = function () {
    var s = "";
    if (this.grille) {
      for (var x = 0; x <= this.W + 1e-6; x += 5) s += '<line x1="' + x + '" y1="0" x2="' + x + '" y2="' + this.H + '" class="' + (x % 10 ? "g5" : "g10") + '"/>';
      for (var y = 0; y <= this.H + 1e-6; y += 5) s += '<line x1="0" y1="' + y + '" x2="' + this.W + '" y2="' + y + '" class="' + (y % 10 ? "g5" : "g10") + '"/>';
    }
    this.L.grille.innerHTML = s;
  };
  P.plein = function () {
    var on = !this.zone.classList.contains("plein");
    this.zone.classList.toggle("plein", on);
    document.body.classList.toggle("at-plein-ouvert", on);
    var b = $('[data-act="plein"]', this.root);
    if (b) { b.setAttribute("aria-pressed", on ? "true" : "false"); b.textContent = on ? "Quitter le plein écran" : "Plein écran"; }
    var self = this;
    requestAnimationFrame(function () { self.ajuster(); });
    if (!on) this.zone.scrollIntoView({ block: "start" });
  };

  // ------------------------------------------------------------------ outils
  var AIDES = {
    main: ["Fais glisser la feuille pour la déplacer ; touche un tracé pour le choisir (nom, longueur, suppression)."],
    point: ["Touche l'endroit du point : il s'accroche aux points, aux intersections et aux tracés."],
    droite: ["Premier point de la droite.", "Second point de la droite."],
    segment: ["Première extrémité du segment.", "Seconde extrémité du segment."],
    vecteur: ["Origine du vecteur (le point où l'on cherche la vitesse).", "Extrémité du vecteur : sa longueur s'affiche ; tu pourras la saisir au millimètre."],
    perp: ["Touche la droite (ou le segment, le vecteur, l'axe) de référence.", "Touche le point par lequel passe la perpendiculaire."],
    para: ["Touche la droite (ou le segment, le vecteur, l'axe) de référence.", "Touche le point par lequel passe la parallèle."],
    proj: ["Touche le point à projeter (l'extrémité d'un vecteur, par exemple).", "Touche la droite de projection."],
    cercle: ["Centre du cercle.", "Un point du cercle (le rayon s'affiche)."],
    compas: ["Écartement du compas : première pointe.", "Écartement du compas : seconde pointe.", "Pique le compas au centre du cercle à tracer."],
    mesure: ["Premier point de la mesure.", "Second point : la distance et l'angle s'affichent."],
    texte: ["Touche l'endroit du texte, puis écris-le."],
    gomme: ["Touche ou balaie un tracé pour l'effacer (tes tracés seulement, jamais la figure)."]
  };
  P.choisir = function (t) {
    this.tool = t; this.step = []; this.mesure = null;
    if (t !== "main") this.selectionner(null);
    $$("[data-outil]", this.root).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-outil") === t ? "true" : "false"); });
    this.root.setAttribute("data-outil-actif", t);
    this.aide();
    this.rendreTmp();
  };
  P.aide = function (extra) {
    var a = $(".at-aide", this.root);
    if (a) a.textContent = (AIDES[this.tool] || [""])[Math.min(this.step.length, (AIDES[this.tool] || [""]).length - 1)];
    var m = $(".at-mesure", this.root);
    if (m && extra !== undefined) m.textContent = extra;
  };
  P.annulerEtape = function () {
    if (this.step.length) { this.step = []; this.aide(""); this.rendreTmp(); return true; }
    if (this.mesure) { this.mesure = null; this.aide(""); this.rendreTmp(); return true; }
    if (this.sel) { this.selectionner(null); return true; }
    return false;
  };

  // ------------------------------------------------------------------ objets, accrochage
  P.points = function () {  // points d'accrochage : figure, puis constructions
    var out = this.figPts.slice();
    this.objs.forEach(function (o) {
      if (o.t === "pt") out.push({ p: o.p, nom: o.nom });
      else if (o.t === "sg" || o.t === "ve") { out.push({ p: o.a }); out.push({ p: o.b }); }
      else if (o.t === "ci") out.push({ p: o.c });
    });
    return out;
  };
  function courbe(o) {
    if (o.t === "dr") return { k: "L", p: o.p, d: o.d, t0: -1e9, t1: 1e9, o: o };
    if (o.t === "sg" || o.t === "ve") return { k: "L", p: o.a, d: sub(o.b, o.a), t0: 0, t1: 1, o: o };
    if (o.t === "ci") return { k: "C", c: o.c, r: o.r, o: o };
    return null;
  }
  P.courbes = function () {
    return this.figCourbes.concat(this.objs.map(courbe).filter(Boolean));
  };
  P.recalculer = function () {
    var cs = this.courbes(), X = [];
    for (var i = 0; i < cs.length; i++)
      for (var j = i + 1; j < cs.length; j++) {
        if (cs[i].fixe && cs[j].fixe) { inter(cs[i], cs[j]).forEach(function (p) { X.push(p); }); continue; }
        inter(cs[i], cs[j]).forEach(function (p) { X.push(p); });
      }
    this.cacheCourbes = cs; this.cacheInter = X; this.cachePts = this.points();
  };
  P.accrocher = function (p) {
    var r = SNAP_PX / this.k(), best = null, d, i;
    for (i = 0; i < this.cachePts.length; i++) {
      d = dist(p, this.cachePts[i].p);
      if (d < r && (!best || d < best.d)) best = { p: this.cachePts[i].p, d: d, type: "point", nom: this.cachePts[i].nom };
    }
    if (best) return best;
    for (i = 0; i < this.cacheInter.length; i++) {
      d = dist(p, this.cacheInter[i]);
      if (d < r && (!best || d < best.d)) best = { p: this.cacheInter[i], d: d, type: "intersection" };
    }
    if (best) return best;
    for (i = 0; i < this.cacheCourbes.length; i++) {
      var q = surCourbe(p, this.cacheCourbes[i]);
      d = dist(p, q);
      if (d < r * 0.8 && (!best || d < best.d)) best = { p: q, d: d, type: "sur", c: this.cacheCourbes[i] };
    }
    return best || { p: p, d: 0, type: "libre" };
  };
  /* droite de référence sous le pointeur (perpendiculaire, parallèle, projeté) : axes de la figure ou tracés */
  P.ligneSous = function (p) {
    var r = SNAP_PX / this.k(), best = null;
    this.cacheCourbes.forEach(function (c) {
      if (c.k !== "L") return;
      var d = c.t0 < -1e8 ? distLigne(p, c.p, c.d) : distSeg(p, c.p, add(c.p, c.d));
      if (d < r && (!best || d < best.d)) best = { c: c, d: d };
    });
    return best && best.c;
  };
  P.objetSous = function (p) {
    var r = SNAP_PX / this.k(), best = null;
    this.objs.forEach(function (o) {
      var d = Infinity;
      if (o.t === "pt") d = dist(p, o.p);
      else if (o.t === "dr") d = distLigne(p, o.p, o.d);
      else if (o.t === "sg" || o.t === "ve") d = distSeg(p, o.a, o.b);
      else if (o.t === "ci") d = Math.abs(dist(p, o.c) - o.r);
      else if (o.t === "tx") d = Math.max(0, dist(p, o.p) - r);
      if (d < r && (!best || d < best.d)) best = { o: o, d: d };
    });
    return best && best.o;
  };

  // ------------------------------------------------------------------ historique
  P.memo = function () {
    this.hist.push(JSON.stringify(this.objs));
    if (this.hist.length > 200) this.hist.shift();
    this.futur = [];
  };
  P.annuler = function () {
    if (this.annulerEtape()) return;
    if (!this.hist.length) return;
    this.futur.push(JSON.stringify(this.objs));
    this.objs = JSON.parse(this.hist.pop()); this.sel = null; this.changer();
  };
  P.retablir = function () {
    if (!this.futur.length) return;
    this.hist.push(JSON.stringify(this.objs));
    this.objs = JSON.parse(this.futur.pop()); this.sel = null; this.changer();
  };
  P.ajouter = function (o) {
    this.memo();
    o.id = this.nid++; o.c = o.c || this.couleur;
    this.objs.push(o);
    this.changer();
    return o;
  };
  P.supprimer = function (o) { this.objs = this.objs.filter(function (x) { return x !== o; }); };
  P.gommer = function (p, debut) {
    var o = this.objetSous(p);
    if (!o) return;
    if (debut || !this.gommeMemo) { this.memo(); this.gommeMemo = true; }
    this.supprimer(o); if (this.sel === o) this.sel = null;
    this.changer();
  };
  P.finGomme = function () { this.gommeMemo = false; };

  // ------------------------------------------------------------------ actions
  P.survol = function (p) {
    this.hover = { brut: p, s: this.tool === "main" || this.tool === "gomme" || this.tool === "texte" ? null : this.accrocher(p) };
    if (this.attendLigne()) this.hover.ligne = this.ligneSous(p);
    var m = this.lecture(this.hover.s ? this.hover.s.p : p);
    if (m !== null) this.aide(m);
    this.rendreTmp();
  };
  P.attendLigne = function () {
    return ((this.tool === "perp" || this.tool === "para") && this.step.length === 0) || (this.tool === "proj" && this.step.length === 1);
  };
  /* mesure en direct pendant le tracé */
  P.lecture = function (p) {
    var s = this.step;
    if ((this.tool === "vecteur" || this.tool === "segment" || this.tool === "mesure") && s.length === 1)
      return "Longueur : " + fr(dist(s[0], p), 1) + " mm · angle : " + fr(ang(sub(p, s[0])), 1) + "°";
    if (this.tool === "cercle" && s.length === 1) return "Rayon : " + fr(dist(s[0], p), 1) + " mm";
    if (this.tool === "compas" && s.length === 1) return "Écartement : " + fr(dist(s[0], p), 1) + " mm";
    if (this.tool === "compas" && s.length === 2) return "Rayon reporté : " + fr(dist(s[0], s[1]), 1) + " mm";
    return null;
  };
  P.clic = function (p) {
    if (this.tool === "main") { this.selectionner(this.objetSous(p)); return; }
    if (this.tool === "gomme") return;
    if (this.tool === "texte") { this.saisirTexte(p); return; }
    var s = this.step;
    if (this.attendLigne()) {
      var c = this.ligneSous(p);
      if (!c) { this.aide("Aucune droite à cet endroit : touche un axe, une droite, un segment ou un vecteur."); return; }
      s.push(c); this.aide(); this.rendreTmp();
      if (this.tool === "proj") this.finir();
      return;
    }
    var q = this.accrocher(p).p;
    s.push(q);
    var besoin = { point: 1, droite: 2, segment: 2, vecteur: 2, perp: 2, para: 2, proj: 2, cercle: 2, compas: 3, mesure: 2 }[this.tool];
    if (s.length >= besoin) this.finir();
    else { this.aide(); this.rendreTmp(); }
  };
  P.finir = function () {
    var s = this.step, t = this.tool, o = null;
    this.step = [];
    if (t === "point") o = this.ajouter({ t: "pt", p: s[0], nom: "" });
    else if (t === "droite" && dist(s[0], s[1]) > 1e-6) o = this.ajouter({ t: "dr", p: s[0], d: unit(sub(s[1], s[0])) });
    else if (t === "segment" && dist(s[0], s[1]) > 1e-6) o = this.ajouter({ t: "sg", a: s[0], b: s[1] });
    else if (t === "vecteur" && dist(s[0], s[1]) > 1e-6) o = this.ajouter({ t: "ve", a: s[0], b: s[1], nom: "" });
    else if (t === "perp") o = this.ajouter({ t: "dr", p: s[1], d: unit(perp(s[0].d)) });
    else if (t === "para") o = this.ajouter({ t: "dr", p: s[1], d: unit(s[0].d) });
    else if (t === "proj") {
      var h = projLigne(s[0], s[1].p, s[1].d);
      this.memo();
      var n1 = { t: "sg", a: s[0], b: h, pointille: true, id: this.nid++, c: this.couleur };
      var n2_ = { t: "pt", p: h, nom: "", id: this.nid++, c: this.couleur };
      this.objs.push(n1, n2_); this.changer(); o = n2_;
    } else if (t === "cercle" && dist(s[0], s[1]) > 1e-6) o = this.ajouter({ t: "ci", c: s[0], r: dist(s[0], s[1]) });
    else if (t === "compas" && dist(s[0], s[1]) > 1e-6) o = this.ajouter({ t: "ci", c: s[2], r: dist(s[0], s[1]) });
    else if (t === "mesure") {
      this.mesure = [s[0], s[1]];
      this.aide("Distance : " + fr(dist(s[0], s[1]), 1) + " mm · angle : " + fr(ang(sub(s[1], s[0])), 1) + "° (Échap pour effacer la mesure)");
      this.rendreTmp(); return;
    }
    if (o && (o.t === "ve" || o.t === "pt") && t !== "proj") this.selectionner(o, true);
    this.aide(o ? this.description(o) : "");
    this.rendreTmp();
  };
  P.description = function (o) {
    if (o.t === "ve") return "Vecteur de " + fr(dist(o.a, o.b), 1) + " mm, angle " + fr(ang(sub(o.b, o.a)), 1) + "°" + (o.nom ? " — " + o.nom : "");
    if (o.t === "sg") return "Segment de " + fr(dist(o.a, o.b), 1) + " mm";
    if (o.t === "ci") return "Cercle de rayon " + fr(o.r, 1) + " mm";
    if (o.t === "dr") return "Droite, angle " + fr(((ang(o.d) % 180) + 180) % 180, 1) + "°";
    if (o.t === "pt") return "Point" + (o.nom ? " " + o.nom : "");
    return "";
  };
  P.saisirTexte = function (p) {
    var self = this, stage = $(".at-stage", this.root), r = stage.getBoundingClientRect(), sr = this.svg.getBoundingClientRect();
    var k = this.k(), v = this.vue, ox = sr.left + (sr.width - v.w * k) / 2, oy = sr.top + (sr.height - v.h * k) / 2;
    var inp = document.createElement("input");
    inp.className = "at-texte"; inp.type = "text"; inp.setAttribute("aria-label", "Texte à placer sur la feuille");
    inp.style.left = (ox + (p[0] - v.x) * k - r.left) + "px"; inp.style.top = (oy + (p[1] - v.y) * k - r.top - 14) + "px";
    stage.appendChild(inp); setTimeout(function () { inp.focus(); }, 0);
    var fait = false;
    function valider(ok) {
      if (fait) return; fait = true;
      if (ok && inp.value.trim()) self.ajouter({ t: "tx", p: p, s: inp.value.trim() });
      inp.remove(); self.svg.focus({ preventScroll: true });
    }
    inp.addEventListener("keydown", function (e) { e.stopPropagation(); if (e.key === "Enter") valider(true); if (e.key === "Escape") valider(false); });
    inp.addEventListener("blur", function () { valider(true); });
  };
  P.selectionner = function (o, focusNom) {
    this.sel = o || null;
    var pr = this.prop;
    if (pr) {
      pr.hidden = !o;
      if (o) {
        $(".at-p-type", pr).textContent = this.description(o);
        var nomOk = o.t === "ve" || o.t === "pt";
        $(".at-p-nomw", pr).hidden = !nomOk;
        $(".at-p-nom", pr).value = o.nom || "";
        $(".at-p-longw", pr).hidden = o.t !== "ve";
        if (o.t === "ve") $(".at-p-long", pr).value = n2(dist(o.a, o.b)).toString().replace(".", ",");
        if (focusNom && nomOk && window.matchMedia("(pointer:fine)").matches) { /* le nom se saisit tout de suite au clavier */ }
      }
    }
    this.rendre();
  };

  // ------------------------------------------------------------------ clavier : curseur et raccourcis
  var RACC = { v: "vecteur", d: "droite", s: "segment", p: "point", e: "perp", a: "para", o: "proj", c: "cercle", k: "compas", m: "mesure", t: "texte", g: "gomme", h: "main" };
  P.clavier = function (e) {
    if (e.target !== this.svg) return;
    var pas = e.shiftKey ? 0.2 : 1, c = this.curseur || [this.vue.x + this.vue.w / 2, this.vue.y + this.vue.h / 2];
    var dirs = { ArrowLeft: [-pas, 0], ArrowRight: [pas, 0], ArrowUp: [0, -pas], ArrowDown: [0, pas] };
    if (dirs[e.key]) {
      e.preventDefault(); this.curseur = add(c, dirs[e.key]); this.survol(this.curseur); return;
    }
    if ((e.key === "Enter" || e.key === " ") && !e.ctrlKey) {
      e.preventDefault();
      if (e.key === " " && !this.curseur) { this.espace = true; return; }
      this.curseur = c; this.clic(c); this.survol(c); return;
    }
    if (e.key === "Escape") { if (this.annulerEtape()) { e.preventDefault(); e.stopPropagation(); } return; }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") { e.preventDefault(); this.annuler(); return; }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") { e.preventDefault(); this.retablir(); return; }
    if ((e.key === "Delete" || e.key === "Backspace") && this.sel) { e.preventDefault(); this.memo(); this.supprimer(this.sel); this.sel = null; this.changer(); return; }
    if (e.key === "+" || e.key === "=") { e.preventDefault(); this.zoomer(1.25); return; }
    if (e.key === "-") { e.preventDefault(); this.zoomer(1 / 1.25); return; }
    if (!e.ctrlKey && !e.metaKey && !e.altKey && RACC[e.key.toLowerCase()]) { e.preventDefault(); this.choisir(RACC[e.key.toLowerCase()]); }
  };

  // ------------------------------------------------------------------ rendu
  P.changer = function (initial) {
    this.recalculer();
    if (this.sel && this.objs.indexOf(this.sel) < 0) this.sel = null;
    this.selectionner(this.sel);
    this.evaluer(initial);
  };
  P.rendre = function () {
    var k = this.k(), self = this, s = "", m = 6 / k;
    var X0 = -this.W, Y0 = -this.H, X1 = 2 * this.W, Y1 = 2 * this.H;
    this.objs.forEach(function (o) {
      var c = o.c, choisi = o === self.sel, w = choisi ? 3.2 : 1.6, cls = choisi ? "at-choisi" : "";
      if (o.t === "dr") { var seg = clipLigne(o.p, o.d, X0, Y0, X1, Y1); if (seg) s += svgLigne(seg[0], seg[1], c, choisi ? 2.6 : 1.2, cls); }
      else if (o.t === "sg") s += svgLigne(o.a, o.b, c, o.pointille ? 1.3 : w, cls, o.pointille ? "5 4" : "");
      else if (o.t === "ve") {
        s += svgFleche(o.a, o.b, c, choisi ? 3.6 : 2.6, k, cls);
        if (o.nom) s += svgTexte(posEtiquette(o.a, o.b, k), o.nom, c, k, 14, "", "middle");
      } else if (o.t === "ci") s += '<circle cx="' + n2(o.c[0]) + '" cy="' + n2(o.c[1]) + '" r="' + n2(o.r) + '" fill="none" stroke="' + c + '" stroke-width="' + (choisi ? 2.6 : 1.2) + '" class="' + cls + '"/>';
      else if (o.t === "pt") { s += svgCroix(o.p, c, k, choisi ? 2.6 : 1.8); if (o.nom) s += svgTexte([o.p[0] + m, o.p[1] - m], o.nom, c, k, 14); }
      else if (o.t === "tx") s += svgTexte(o.p, o.s, c, k, 15, choisi ? "at-choisi" : "");
    });
    this.L.cons.innerHTML = s;
    // correction des questions déjà corrigées
    var cs = "";
    if (this.voirCorr) Object.keys(this.reveles).forEach(function (g) { cs += self.svgCorrection((self.cfg.corr || {})[g] || [], k); });
    this.L.corr.innerHTML = cs;
    this.rendreTmp();
  };
  P.svgCorrection = function (prims, k) {
    var s = "", X0 = -this.W, Y0 = -this.H, X1 = 2 * this.W, Y1 = 2 * this.H;
    prims.forEach(function (q) {
      var aide = q.st === "aide", c = aide ? ORANGE : ROUGE, dash = aide ? "6 4" : "";
      if (q.t === "ve") { s += svgFleche(q.a, q.b, c, aide ? 1.8 : 2.8, k, "at-c"); if (q.lab) s += svgTexte(posEtiquette(q.a, q.b, k), q.lab, c, k, 14, "at-c", "middle"); }
      else if (q.t === "dr") { var g = clipLigne(q.p, unit(q.d), X0, Y0, X1, Y1); if (g) s += svgLigne(g[0], g[1], c, 1.3, "at-c", dash || "8 3 2 3"); }
      else if (q.t === "sg") s += svgLigne(q.a, q.b, c, aide ? 1.4 : 2.4, "at-c", dash);
      else if (q.t === "ci") s += '<circle cx="' + n2(q.c[0]) + '" cy="' + n2(q.c[1]) + '" r="' + n2(q.r) + '" fill="none" stroke="' + c + '" stroke-width="1.4" stroke-dasharray="' + (dash || "") + '" class="at-c"/>';
      else if (q.t === "pt") { s += svgCroix(q.p, c, k, 2.2); if (q.lab) s += svgTexte([q.p[0] + 6 / k, q.p[1] - 6 / k], q.lab, c, k, 15, "at-c"); }
      else if (q.t === "tx") s += svgTexte(q.p, q.s, c, k, 14, "at-c", q.ancre);
    });
    return s;
  };
  P.rendreTmp = function () {
    var k = this.k(), s = "", h = this.hover, st = this.step, t = this.tool, c = this.couleur;
    var X0 = -this.W, Y0 = -this.H, X1 = 2 * this.W, Y1 = 2 * this.H;
    var p = h && h.s ? h.s.p : (h ? h.brut : null);
    if (p && st.length && !this.attendLigne()) {
      if (t === "droite") { var g = clipLigne(st[0], unit(sub(p, st[0])), X0, Y0, X1, Y1); if (g && dist(p, st[0]) > 1e-6) s += svgLigne(g[0], g[1], c, 1, "at-apercu", "4 3"); }
      else if (t === "segment" || t === "mesure") s += svgLigne(st[0], p, t === "mesure" ? "#555" : c, 1.4, "at-apercu", t === "mesure" ? "3 3" : "");
      else if (t === "vecteur") s += svgFleche(st[0], p, c, 2.2, k, "at-apercu");
      else if (t === "cercle") s += '<circle cx="' + n2(st[0][0]) + '" cy="' + n2(st[0][1]) + '" r="' + n2(dist(st[0], p)) + '" fill="none" stroke="' + c + '" stroke-dasharray="4 3" class="at-apercu"/>';
      else if (t === "compas" && st.length === 1) s += svgLigne(st[0], p, "#555", 1.2, "at-apercu", "3 3");
      else if (t === "compas" && st.length === 2) s += '<circle cx="' + n2(p[0]) + '" cy="' + n2(p[1]) + '" r="' + n2(dist(st[0], st[1])) + '" fill="none" stroke="' + c + '" stroke-dasharray="4 3" class="at-apercu"/>';
      else if ((t === "perp" || t === "para") && st[0]) {
        var d = t === "perp" ? perp(st[0].d) : st[0].d, g2 = clipLigne(p, unit(d), X0, Y0, X1, Y1);
        if (g2) s += svgLigne(g2[0], g2[1], c, 1, "at-apercu", "4 3");
      }
    }
    if (t === "proj" && st.length === 1 && h && h.ligne) {
      var hh = projLigne(st[0], h.ligne.p, h.ligne.d); s += svgLigne(st[0], hh, c, 1.2, "at-apercu", "4 3") + svgCroix(hh, c, k, 1.4);
    }
    if (h && h.ligne && this.attendLigne()) {
      var L = h.ligne, g3 = L.t0 < -1e8 ? clipLigne(L.p, unit(L.d), X0, Y0, X1, Y1) : [L.p, add(L.p, L.d)];
      if (g3) s += svgLigne(g3[0], g3[1], "#F2B705", 5, "at-surligne");
    }
    st.forEach(function (q) { if (Array.isArray(q)) s += '<circle cx="' + n2(q[0]) + '" cy="' + n2(q[1]) + '" r="' + n2(3 / k) + '" fill="' + c + '"/>'; });
    if (this.mesure) {
      var a = this.mesure[0], b = this.mesure[1];
      s += svgLigne(a, b, "#555", 1.4, "", "3 3") + svgTexte(add(mul(add(a, b), 0.5), [6 / k, -6 / k]), fr(dist(a, b), 1) + " mm", "#333", k, 14);
    }
    if (h && h.s && h.s.type !== "libre") {
      var q = h.s.p, r = 6 / k;
      s += '<circle cx="' + n2(q[0]) + '" cy="' + n2(q[1]) + '" r="' + n2(r) + '" class="at-accroche at-' + h.s.type + '"/>';
      if (h.s.type === "point" && h.s.nom) s += svgTexte([q[0] + r * 1.4, q[1] + r * 2.6], h.s.nom, "#7A5300", k, 13);
    }
    if (this.curseur) {
      var cu = this.curseur, rr = 9 / k;
      s += svgLigne([cu[0] - rr, cu[1]], [cu[0] + rr, cu[1]], "#B42318", 1.2) + svgLigne([cu[0], cu[1] - rr], [cu[0], cu[1] + rr], "#B42318", 1.2);
    }
    this.L.tmp.innerHTML = s;
  };

  // ------------------------------------------------------------------ vérification des items
  /* Un item décrit ce que la question attend sur la feuille :
       ve  : un vecteur d'origine o, de composantes v (mm de feuille) ; tolérances tolO (mm), tolA (°), tolL (relative)
       dir : une droite (ou un segment, un vecteur) passant par o, de direction d ; tolA (°)
       pt  : un point placé en p (tolP en mm), nommé ou non
       ci  : un cercle de centre c et de rayon r
     Un tracé nommé ne compte que pour l'item du même nom ; un tracé sans nom compte pour tout item qui lui convient. */
  P.evaluerItem = function (it) {
    var tolO = it.tolO || 1.5, attendu = nomNorm(it.nom);
    function nomOk(o) { return !o.nom || !attendu || nomNorm(o.nom) === attendu; }
    var cands, best = null;
    if (it.k === "ve") {
      cands = this.objs.filter(function (o) { return o.t === "ve" && dist(o.a, it.o) <= tolO && nomOk(o); });
      if (!cands.length) return { etat: "vide" };
      var Lx = len(it.v);
      cands.forEach(function (o) {
        var v = sub(o.b, o.a), eA = ecartV(v, it.v), eL = Math.abs(len(v) - Lx), okL = eL <= Math.max((it.tolL || 0.06) * Lx, it.tolMin || 1.2);
        var ok = eA <= (it.tolA || 3) && okL, sc = eA / (it.tolA || 3) + eL / Math.max(1, Lx * 0.06);
        if (!best || ok > best.ok || (ok === best.ok && sc < best.sc)) best = { ok: ok, sc: sc, eA: eA, L: len(v) };
      });
      return { etat: "present", ok: best.ok, diag: best.ok ? "" : (best.eA > (it.tolA || 3) ? "direction ou sens à revoir (écart de " + fr(best.eA, 0) + "°)" : "longueur " + fr(best.L, 1) + " mm, attendue " + fr(Lx, 1) + " mm") };
    }
    if (it.k === "dir") {
      cands = this.objs.filter(function (o) {
        if (o.t === "dr") return distLigne(it.o, o.p, o.d) <= tolO;
        if (o.t === "sg" || o.t === "ve") return dist(o.a, o.b) > 1 && distLigne(it.o, o.a, sub(o.b, o.a)) <= tolO;
        return false;
      });
      if (!cands.length) return { etat: "vide" };
      cands.forEach(function (o) {
        var d = o.t === "dr" ? o.d : sub(o.b, o.a), e = ecartD(d, it.d);
        if (!best || e < best.e) best = { e: e };
      });
      var okd = best.e <= (it.tolA || 3);
      return { etat: "present", ok: okd, diag: okd ? "" : "aucune droite passant par ce point n'a la bonne direction (écart de " + fr(best.e, 0) + "°)" };
    }
    if (it.k === "pt") {
      cands = this.objs.filter(function (o) { return o.t === "pt" && nomOk(o); });
      var nommes = cands.filter(function (o) { return attendu && nomNorm(o.nom) === attendu; });
      var proches = cands.filter(function (o) { return dist(o.p, it.p) <= (it.tolP || 2); });
      if (!nommes.length && !proches.length) {
        var pres = cands.filter(function (o) { return !o.nom && dist(o.p, it.p) <= 4 * (it.tolP || 2); });
        if (!pres.length) return { etat: "vide" };
        return { etat: "present", ok: false, diag: "point placé à " + fr(Math.min.apply(null, pres.map(function (o) { return dist(o.p, it.p); })), 1) + " mm de la position attendue" };
      }
      if (proches.length) return { etat: "present", ok: true };
      var dm = Math.min.apply(null, nommes.map(function (o) { return dist(o.p, it.p); }));
      return { etat: "present", ok: false, diag: "point placé à " + fr(dm, 1) + " mm de la position attendue" };
    }
    if (it.k === "ci") {
      cands = this.objs.filter(function (o) { return o.t === "ci" && dist(o.c, it.c) <= tolO; });
      if (!cands.length) return { etat: "vide" };
      var okc = cands.some(function (o) { return Math.abs(o.r - it.r) <= Math.max(1, 0.03 * it.r); });
      return { etat: "present", ok: okc, diag: okc ? "" : "rayon à revoir" };
    }
    return { etat: "vide" };
  };
  P.evaluer = function (initial) {
    var self = this;
    Object.keys(this.items).forEach(function (fid) {
      var r = self.evaluerItem(self.items[fid]), inp = document.getElementById("in-" + fid);
      self.etats[fid] = r;
      var row = document.getElementById("it-" + fid);
      if (row && !row.classList.contains("corrige")) {
        row.classList.toggle("present", r.etat === "present");
        var e = $(".it-etat", row); if (e) e.textContent = r.etat === "present" ? "tracé repéré" : "à construire";
      }
      if (!inp || inp.disabled) return;
      var v = r.etat === "vide" ? "" : (r.ok ? "juste" : "faux");
      if (inp.value !== v) { inp.value = v; if (!initial) inp.dispatchEvent(new Event("input", { bubbles: true })); }
    });
  };

  // ------------------------------------------------------------------ questions liées
  P.lierQuestions = function () {
    var self = this;
    var groupes = this.cfg.groupes || {};
    Object.keys(groupes).forEach(function (gid) {
      var g = document.getElementById(gid);
      if (!g) return;
      var relais = $(".btn-trace", g), btn = $(".btn-fast", g), msg = $(".q-msg", g);
      if (relais) relais.addEventListener("click", function () {
        if (btn.disabled) return;
        var fids = groupes[gid], vides = fids.filter(function (f) { return !self.etats[f] || self.etats[f].etat === "vide"; });
        if (vides.length === fids.length) { msg.textContent = "Rien à valider : construis d'abord sur le document réponse ce que demande la question."; return; }
        if (vides.length && !relais.dataset.confirme) {
          relais.dataset.confirme = "1";
          relais.textContent = "Valider quand même";
          msg.textContent = "Pas encore tracé : " + vides.map(function (f) { return self.items[f].lab; }).join(", ") + ". Ces éléments seront comptés faux.";
          return;
        }
        msg.textContent = "";
        btn.dataset.confirm = "1";  // la confirmation a déjà été demandée ici
        btn.click();
      });
    });
    // une question corrigée (validée en entraînement, ou copie remise en examen) dévoile sa correction sur la feuille
    var parts = this.zone;
    new MutationObserver(function (ms) {
      ms.forEach(function (m) {
        var b = m.target;
        if (!b.disabled || !b.classList.contains("btn-fast")) return;
        var g = b.closest(".fast-q");
        if (g && groupes[g.id]) self.reveler(g.id);
      });
    }).observe(parts, { subtree: true, attributes: true, attributeFilter: ["disabled"] });
  };
  P.reveler = function (gid) {
    if (this.reveles[gid]) return;
    var self = this;
    this.reveles[gid] = true;
    (this.cfg.groupes[gid] || []).forEach(function (fid) {
      var row = document.getElementById("it-" + fid), r = self.etats[fid] || { etat: "vide" };
      if (!row) return;
      row.classList.add("corrige");
      var d = $(".it-diag", row);
      if (d) d.textContent = r.etat === "vide" ? "non tracé" : (r.ok ? "" : r.diag || "");
    });
    var relais = $("#" + gid + " .btn-trace"); if (relais) { relais.disabled = true; relais.textContent = "Construction validée"; }
    if (this.btnCorr) { this.btnCorr.disabled = false; this.voirCorr = true; this.btnCorr.setAttribute("aria-pressed", "true"); }
    this.rendre();
  };

  // ------------------------------------------------------------------ impression du document réponse vierge
  P.imprimerVierge = function () {
    var w = window.open("", "_blank");
    if (!w) { alert("La fenêtre d'impression a été bloquée par le navigateur : autorise les fenêtres surgissantes, puis réessaie."); return; }
    var fig = $(".at-fig", this.svg).outerHTML, titre = this.root.getAttribute("data-titre") || "Document réponse";
    var paysage = this.W >= this.H, css = $("#at-css-fig") ? $("#at-css-fig").textContent : "";
    w.document.write('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>' + esc(titre) + "</title><style>" +
      "@page{size:A4 " + (paysage ? "landscape" : "portrait") + ";margin:8mm}body{margin:0;font:13px system-ui,Arial,sans-serif;color:#1C2530}" +
      "header{display:flex;justify-content:space-between;border-bottom:1.5px solid #1C2530;padding:0 0 2mm;margin:0 0 3mm}" +
      ".bar{background:#1C2530;color:#fff;padding:8px 14px;display:flex;gap:12px;align-items:center}.bar button{background:#F2B705;border:0;padding:7px 14px;font-weight:700;cursor:pointer}" +
      "@media print{.bar{display:none}}" + css + "</style></head><body>" +
      '<div class="bar"><b>Document réponse à imprimer</b><span>Imprime à 100 % (taille réelle) : les longueurs mesurées sur le papier sont celles de la feuille.</span>' +
      '<button type="button" onclick="window.print()">Imprimer</button></div>' +
      "<header><b>" + esc(titre) + "</b><span>Nom : ______________________</span></header>" +
      '<svg xmlns="http://www.w3.org/2000/svg" class="at-svg" width="' + this.W + 'mm" height="' + this.H + 'mm" viewBox="0 0 ' + this.W + " " + this.H + '">' + fig + "</svg></body></html>");
    w.document.close();
  };
  P.avantImpression = function () { this.vueAvant = this.vue; this.vue = { x: 0, y: 0, w: this.W, h: this.H }; this.appliquerVue(); };
  P.apresImpression = function () { if (this.vueAvant) { this.vue = this.vueAvant; this.vueAvant = null; this.appliquerVue(); } };

  // =====================================================================================================
  // DÉMONSTRATION PAS À PAS (cours) : la même feuille, des étapes qui ajoutent chacune leurs tracés
  function Demo(root, cfg) {
    var self = this;
    this.root = root; this.cfg = cfg; this.i = 0;
    this.svg = $("svg.at-svg", root);
    this.W = cfg.w; this.H = cfg.h; this.vue = { x: 0, y: 0, w: cfg.w, h: cfg.h };
    this.L = { cons: $(".at-cons", this.svg) };
    $(".dm-prec", root).addEventListener("click", function () { self.aller(self.i - 1); });
    $(".dm-suiv", root).addEventListener("click", function () { self.aller(self.i + 1); });
    var tout = $(".dm-tout", root); if (tout) tout.addEventListener("click", function () { self.aller(cfg.etapes.length); });
    var zero = $(".dm-zero", root); if (zero) zero.addEventListener("click", function () { self.aller(0); });
    if (window.ResizeObserver) new ResizeObserver(function () { self.dessiner(); }).observe(this.svg);
    this.aller(0);
  }
  Demo.prototype.k = Atelier.prototype.k;
  Demo.prototype.aller = function (i) {
    var n = this.cfg.etapes.length;
    this.i = Math.max(0, Math.min(n, i));
    $(".dm-num", this.root).textContent = "Étape " + this.i + " / " + n;
    var e = this.i ? this.cfg.etapes[this.i - 1] : { titre: this.cfg.depart || "Situation de départ", texte: this.cfg.texte0 || "" };
    $(".dm-titre", this.root).innerHTML = e.titre;
    $(".dm-texte", this.root).innerHTML = e.texte || "";
    $(".dm-prec", this.root).disabled = this.i === 0;
    $(".dm-suiv", this.root).disabled = this.i === n;
    var cur = this.i;
    $$(".dm-liste li", this.root).forEach(function (li, j) { li.classList.toggle("fait", j < cur); li.classList.toggle("en-cours", j === cur - 1); });
    this.dessiner();
  };
  Demo.prototype.dessiner = function () {
    var k = this.k(), s = "", self = this;
    for (var j = 0; j < this.i; j++) {
      var prims = this.cfg.etapes[j].prims, actuelle = j === this.i - 1;
      s += '<g class="' + (actuelle ? "dm-actuelle" : "dm-passee") + '">' + Atelier.prototype.svgCorrection.call(self, prims, k).replace(/#C62828/g, actuelle ? "#C62828" : "#1F5FA8").replace(/#D35400/g, actuelle ? "#D35400" : "#7A848C") + "</g>";
    }
    this.L.cons.innerHTML = s;
  };

  // =====================================================================================================
  var ateliers = [];
  $$(".atelier[data-cfg]").forEach(function (el) {
    var cfg = CFGS[el.getAttribute("data-cfg")];
    if (cfg) ateliers.push(new Atelier(el, cfg));
  });
  $$(".at-demo[data-cfg]").forEach(function (el) {
    var cfg = CFGS[el.getAttribute("data-cfg")];
    if (cfg) new Demo(el, cfg);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var z = $(".at-zone.plein");
    if (!z) return;
    var a = ateliers.filter(function (x) { return x.zone === z; })[0];
    if (a && document.activeElement === a.svg && (a.step.length || a.mesure || a.sel)) return;
    if (a) a.plein();
  });
  window.addEventListener("beforeprint", function () { ateliers.forEach(function (a) { a.avantImpression(); }); });
  window.addEventListener("afterprint", function () { ateliers.forEach(function (a) { a.apresImpression(); }); });
  window.__ateliers__ = ateliers;
  window.__atelierGeo__ = { nomNorm: nomNorm, inter: inter, clipLigne: clipLigne, ecartV: ecartV, ecartD: ecartD };
})();
