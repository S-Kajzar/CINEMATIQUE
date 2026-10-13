# -*- coding: utf-8 -*-
"""Éléments communs aux cours (repris du dépôt « Chaîne fonctionnelle ») : en-tête, sections numérotées, sommaire,
quiz noté, jeux de classement, cartes à retourner, encadrés de formules, exercices d'application auto-corrigés ;
leur comportement et leur style."""
import html
import json
import re


def pastille(partie):
    lab, cls = {"analytique": ("Analytique", "n1"), "graphique": ("Graphique", "n2")}[partie]
    return f' <span class="pastille {cls}">{lab}</span>'


def course_head(tag, partie, title, sub, objectifs=(), prerequis=()):
    obj = ""
    if objectifs or prerequis:
        obj = ('<div class="cours-obj"><div><h2>Objectifs</h2><ul>' + "".join(f"<li>{o}</li>" for o in objectifs) +
               '</ul></div><div><h2>Prérequis</h2><ul>' + "".join(f"<li>{o}</li>" for o in prerequis) + "</ul></div></div>")
    return (f'<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head">'
            f'<span class="mc-tag">{tag}</span>{pastille(partie)}<h1 id="home-title">{title}</h1>'
            f'<p class="home-sub">{sub}</p></header></div></div>{obj}')


def course_section(n, ident, titre, body):
    return (f'<section class="part cours-sec" id="{ident}" aria-labelledby="{ident}-t"><header class="part-head">'
            f'<div class="part-num" aria-hidden="true">{n}</div><div><h2 id="{ident}-t" style="padding:14px 16px">{titre}'
            f'</h2></div></header><div class="part-body">{body}</div></section>')


def course_nav(items):
    return ('<nav class="cours-nav no-print" aria-label="Sections du cours">' +
            "".join(f'<a href="#{a}">{n}. {t}</a>' for n, (a, t) in enumerate(items, 1)) + "</nav>")


def quiz_html(questions, name):
    """Quiz noté : questions = [(énoncé, [choix], indice juste, explication)]."""
    return "".join(
        f'<fieldset class="quiz-q" data-ok="{ok}"><legend><span class="q-num">{i + 1}</span> {q}</legend>' +
        "".join(f'<label><input type="radio" name="{name}{i}" value="{j}"> {o}</label>' for j, o in enumerate(opts)) +
        f'<p class="quiz-fb" aria-live="polite"></p><p class="quiz-why" hidden>{why}</p></fieldset>'
        for i, (q, opts, ok, why) in enumerate(questions))


def quiz_section(n, ident, questions, name):
    return course_section(n, ident, "Quiz : vérifie tes connaissances",
                          f'<p>Choisis une réponse : la correction s\'affiche aussitôt.</p><div class="quiz">'
                          f'{quiz_html(questions, name)}</div><div class="quiz-score" aria-live="polite">'
                          f'<span id="qz-score">0 / {len(questions)}</span><span id="qz-stars" aria-hidden="true"></span>'
                          '<button type="button" class="btn ghost" id="qz-reset">Recommencer</button></div>')


def jeu_html(lignes, choix, ident):
    """Jeu de classement : chaque ligne (libellé, clé juste) propose les mêmes boutons (clé, texte)."""
    rows = "".join(
        f'<div class="jeu-l" data-ok="{ok}"><span>{t}</span>' +
        "".join(f'<button type="button" class="btn ghost" data-v="{k}">{n}</button>' for k, n in choix) +
        '<b class="jeu-fb" aria-live="polite"></b></div>' for t, ok in lignes)
    return (f'<div class="jeu" id="{ident}">{rows}<p class="jeu-score" aria-live="polite">Score : '
            f'<span class="jeu-s">0 / {len(lignes)}</span> <button type="button" class="btn ghost jeu-reset">'
            'Recommencer</button></p></div>')


def cartes(items, cls=""):
    """Cartes à retourner : (titre, contenu)."""
    return ('<div class="cartes">' + "".join(
        f'<button type="button" class="carte {cls}" aria-expanded="false"><b>{t}</b><span class="dos">{d}</span></button>'
        for t, d in items) + "</div>")


def exo(num, enonce, champs, solution, gabarit=None, aide=""):
    """Exercice d'application auto-corrigé par le moteur de correction du gabarit (window.Grading), sans note :
    l'élève vérifie autant de fois qu'il veut, puis peut afficher la solution. champs = [(libellé, correcteur)] ;
    gabarit : texte HTML où le repère [[i]] reçoit la i-ème case (sinon, une case unique sous l'énoncé)."""
    def case(i, large=False):
        lab, gr = champs[i]
        cls, mode = ("exo-in exo-large", "") if large else ("exo-in", ' inputmode="decimal"')
        g, lb = html.escape(json.dumps(gr, ensure_ascii=False)), html.escape(re.sub(r"<[^>]+>", "", lab))
        return (f'<input type="text" class="{cls}" data-g="{g}" aria-label="{lb}" autocomplete="off" '
                f'spellcheck="false"{mode}>')
    if gabarit is None:
        assert len(champs) == 1
        corps = case(0, True)
    else:
        corps = re.sub(r"\[\[(\d+)\]\]", lambda m: case(int(m[1]) - 1), gabarit)
        assert corps.count('class="exo-in') == len(champs), num
    return (f'<div class="exo-c"><p class="exo-q"><span class="q-num">{num}</span> {enonce}</p>'
            + (f'<p class="exo-aide">{aide}</p>' if aide else "") +
            f'<div class="exo-corps">{corps}</div><div class="exo-pied"><button type="button" class="btn exo-v">Vérifier'
            '</button><button type="button" class="btn ghost exo-s" aria-expanded="false">Voir la solution</button>'
            f'<span class="exo-fb" aria-live="polite"></span></div><div class="exo-sol" hidden>{solution}</div></div>')


def num(valeur, unite, accept, rel=0.01, signe=True):
    """Correcteur d'une valeur avec unité (moteur du gabarit : la moitié des points sans unité)."""
    g = {"type": "num", "value": round(valeur, 6), "relTol": rel, "unit": {"label": unite, "accept": accept}}
    if not signe:
        g["abs"] = True
    return g


def nombre(valeur, tol=0.005, rel=0.01):
    """Correcteur d'un nombre seul (coefficient d'une équation, coordonnée)."""
    return {"type": "num", "value": round(valeur, 6), "relTol": rel, "absTol": tol}


def formule(main, units=""):
    return f'<div class="formule"><span class="f-main">{main}</span>' + (f'<span class="f-units">{units}</span>' if units else "") + "</div>"


def frac(a, b):
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'


def vec(s):
    """Grandeur vectorielle : flèche au-dessus (classe .vec du gabarit)."""
    return f'<span class="vec">{s}</span>'


JS = r"""
  function initQuiz(root) {
    function q(s) { return root.querySelector(s); }
    function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
    var qs = qa(".quiz-q");
    if (!qs.length) return;
    function score() {
      var n = qs.filter(function (f) { return f.classList.contains("is-ok"); }).length;
      var done = qs.filter(function (f) { return f.classList.contains("done"); }).length;
      var st = n === qs.length ? 3 : n >= qs.length - 2 ? 2 : n >= 2 ? 1 : 0;
      q("#qz-score").textContent = n + " / " + qs.length;
      q("#qz-stars").textContent = done === qs.length ? "★★★".slice(0, st) + "☆☆☆".slice(0, 3 - st) : "";
    }
    qs.forEach(function (fs) {
      fs.addEventListener("change", function (e) {
        if (fs.classList.contains("done")) return;
        var ok = e.target.value === fs.getAttribute("data-ok");
        fs.classList.add("done", ok ? "is-ok" : "is-ko");
        fs.querySelector(".quiz-fb").textContent = ok ? "✔ Bonne réponse !" : "✘ Pas tout à fait.";
        fs.querySelector(".quiz-why").hidden = false;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) {
          i.disabled = true;
          if (i.value === fs.getAttribute("data-ok")) i.parentNode.classList.add("good");
        });
        score();
      });
    });
    q("#qz-reset").addEventListener("click", function () {
      qs.forEach(function (fs) {
        fs.classList.remove("done", "is-ok", "is-ko");
        fs.querySelector(".quiz-fb").textContent = "";
        fs.querySelector(".quiz-why").hidden = true;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) { i.disabled = false; i.checked = false; i.parentNode.classList.remove("good"); });
      });
      score();
    });
    score();
  }
  // jeu de classement : un clic par ligne, le bon bouton est montré en cas d'erreur
  function initJeu(box) {
    var lignes = Array.prototype.slice.call(box.querySelectorAll(".jeu-l"));
    function score() {
      box.querySelector(".jeu-s").textContent = lignes.filter(function (l) { return l.classList.contains("is-ok"); }).length + " / " + lignes.length;
    }
    lignes.forEach(function (l) {
      Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) {
        b.addEventListener("click", function () {
          if (l.classList.contains("is-ok") || l.classList.contains("is-ko")) return;
          var good = l.getAttribute("data-ok"), ok = b.getAttribute("data-v") === good;
          l.classList.add(ok ? "is-ok" : "is-ko");
          b.classList.add(ok ? "pick-ok" : "pick-ko");
          if (!ok) l.querySelector('button[data-v="' + good + '"]').classList.add("pick-good");
          l.querySelector(".jeu-fb").textContent = ok ? "✔" : "✘";
          score();
        });
      });
    });
    box.querySelector(".jeu-reset").addEventListener("click", function () {
      lignes.forEach(function (l) {
        l.classList.remove("is-ok", "is-ko");
        l.querySelector(".jeu-fb").textContent = "";
        Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) { b.classList.remove("pick-ok", "pick-ko", "pick-good"); });
      });
      score();
    });
    score();
  }
  function initCartes(root) {
    Array.prototype.forEach.call(root.querySelectorAll(".carte"), function (b) {
      b.addEventListener("click", function () { b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true"); });
    });
  }
  // exercices d'application : vérification par le moteur de correction du gabarit, autant de fois que voulu
  function initExos(root) {
    Array.prototype.forEach.call(root.querySelectorAll(".exo-c"), function (b) {
      var ins = Array.prototype.slice.call(b.querySelectorAll(".exo-in")), fb = b.querySelector(".exo-fb");
      function verifier() {
        var G = window.Grading, vides = 0, justes = 0, demi = 0;
        ins.forEach(function (i) {
          i.classList.remove("ok", "demi", "ko");
          if (!i.value.trim()) { vides++; return; }
          var r = G.grade(i.value, JSON.parse(i.getAttribute("data-g")));
          if (r.invalid) { i.classList.add("ko"); return; }
          if (r.score === 1) { justes++; i.classList.add("ok"); }
          else if (r.score === 0.5) { demi++; i.classList.add("demi"); }
          else i.classList.add("ko");
        });
        b.classList.remove("is-ok", "is-ko");
        if (vides === ins.length) { fb.textContent = "Complète d'abord la réponse."; return; }
        if (justes === ins.length) { fb.textContent = "✔ Juste !"; b.classList.add("is-ok"); return; }
        b.classList.add("is-ko");
        if (demi && justes + demi === ins.length) { fb.textContent = "≈ Valeur juste, mais l'unité manque ou est fausse."; return; }
        fb.textContent = ins.length > 1 ? "✘ " + (ins.length - justes) + " case" + (ins.length - justes > 1 ? "s" : "") +
          " à revoir (en rouge) : corrige, ou consulte la solution." : "✘ Pas encore : corrige, ou consulte la solution.";
      }
      b.querySelector(".exo-v").addEventListener("click", verifier);
      ins.forEach(function (i) {
        i.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); verifier(); } });
        i.addEventListener("input", function () { i.classList.remove("ok", "demi", "ko"); });
      });
      var bs = b.querySelector(".exo-s"), sol = b.querySelector(".exo-sol");
      bs.addEventListener("click", function () {
        sol.hidden = !sol.hidden; bs.setAttribute("aria-expanded", sol.hidden ? "false" : "true");
        bs.textContent = sol.hidden ? "Voir la solution" : "Masquer la solution";
      });
    });
  }
  function initCommun(root) {
    initQuiz(root);
    initExos(root);
    Array.prototype.forEach.call(root.querySelectorAll(".jeu"), initJeu);
    initCartes(root);
  }
  function fr(x, d) { if (Math.abs(x) < 0.5 * Math.pow(10, -d)) x = 0; return x.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/^-/, "−"); }
  var RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  /* boucle d'animation partagée : une fonction par figure, suspendue quand la page est cachée */
  function animer(f) {
    var t0 = null;
    function pas(t) { if (t0 === null) t0 = t; f((t - t0) / 1000); requestAnimationFrame(pas); }
    requestAnimationFrame(pas);
  }
"""

CSS = """
/* ---------- cours interactifs (repris du dépôt Chaîne fonctionnelle) ---------- */
.cours .part{margin-bottom:22px}
body.cours-page .home-inner{max-width:1100px}
.cours-obj{display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 0 14px}
.cours-obj>div{background:var(--papier); border:1px solid var(--trait); padding:8px 16px}
.cours-obj h2{font:700 1rem var(--f-titre); margin:4px 0; padding:2px 8px; background:#EEF0EC; text-align:center}
.cours-obj ul{margin:4px 0 6px; padding-left:1.2rem}
@media (max-width:700px){ .cours-obj{grid-template-columns:1fr} }
.cours-nav{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 16px}
.cours-nav a{font:600 .92rem var(--f-titre); color:var(--encre); background:var(--papier); border:1.5px solid var(--encre); padding:5px 12px; text-decoration:none}
.cours-nav a:hover{background:var(--jaune-pale)}
body.cours-page .part-body>p,body.cours-page .part-body>ul{max-width:none}
.cours-sec .part-body h3{font:700 1.12rem var(--f-titre); margin:18px 0 6px; color:var(--bleu)}
.cours-sec .part-body h4{font:700 1rem var(--f-titre); margin:14px 0 4px}
.formule{display:flex; flex-wrap:wrap; gap:14px 28px; align-items:center; border:2px solid var(--rouge); background:#fff; padding:10px 18px; margin:12px 0; max-width:720px}
.formule .f-main{font:700 1.3rem var(--f-texte); line-height:2}
.formule .f-units{font-size:.9rem; color:var(--encre-2)}
.def{border-left:6px solid var(--rouge); background:#fff; padding:8px 14px; margin:12px 0; max-width:86ch}
.def p{margin:.25rem 0}
.simu{border:2px solid var(--bleu); background:var(--bleu-pale); padding:12px 16px; margin:14px 0}
.simu h3{margin:0 0 8px!important; font:700 1.15rem var(--f-titre); color:var(--bleu)!important}
.simu-grid{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px 18px}
@media (max-width:760px){ .simu-grid{grid-template-columns:1fr} }
.simu-grid label{display:block; font-weight:600; font-size:.92rem}
.simu-grid label output{margin-left:6px}
.simu-grid label input[type=range],.simu-grid label select{display:block; margin-top:4px}
.simu-grid output{font:700 1rem var(--f-titre); color:var(--bleu)}
.simu-grid input[type=range]{width:100%; accent-color:var(--bleu)}
.simu-grid select{padding:5px; border:1.5px solid var(--encre-2); background:#fff; font:inherit}
.simu-out{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin:12px 0 8px}
.simu-out div{background:var(--encre); color:#fff; padding:6px 10px}
.simu-out span{display:block; font-size:.78rem; color:#D7DDE2}
.simu-out b{font:700 1.1rem var(--f-titre); color:var(--jaune)}
@media (max-width:760px){ .simu-out{grid-template-columns:repeat(2,minmax(0,1fr))} }
.simu-btns{display:flex; flex-wrap:wrap; gap:6px; margin:6px 0}
.simu-fig{background:#fff; border:1px solid var(--trait-fin); margin:8px 0}
.simu-fig svg{display:block; width:100%; height:auto; font-family:var(--f-texte)}
.simu-note{font-size:.86rem; color:var(--encre-2); margin:4px 0 0}
.exemple{background:#F6F7F4; border:1px solid var(--trait-fin); padding:6px 16px; margin-top:12px}
.exemple h3{font:700 1.05rem var(--f-titre); margin:10px 0 4px}
.remarque{border-left:6px solid var(--jaune); background:var(--jaune-pale); padding:8px 14px; margin:12px 0; max-width:86ch}
.remarque p{margin:.2rem 0}
.quiz{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px}
.quiz-q{border:1.5px solid var(--encre); background:#fff; padding:8px 14px 10px; margin:0}
.quiz-q legend{font-weight:700; padding:0 4px}
.quiz-q label{display:block; padding:3px 0; cursor:pointer}
.quiz-q.is-ok{border-color:var(--vert); background:var(--vert-pale)}
.quiz-q.is-ko{border-color:var(--rouge); background:var(--rouge-pale)}
.quiz-q label.good{font-weight:700; color:var(--vert)}
.quiz-fb{margin:4px 0 0; font-weight:700}
.quiz-q.is-ok .quiz-fb{color:var(--vert)} .quiz-q.is-ko .quiz-fb{color:var(--rouge)}
.quiz-why{margin:2px 0 0; font-size:.9rem}
.quiz-score{display:flex; align-items:center; gap:14px; margin:14px 0 0; font:700 1.3rem var(--f-titre)}
#qz-stars{color:var(--jaune); font-size:1.6rem; letter-spacing:2px}
.jeu{border:2px solid var(--encre); background:#fff; padding:10px 14px; margin:12px 0 0}
.jeu-l{display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; padding:6px 0; border-top:1px solid var(--trait-fin)}
.jeu-l>span{flex:1 1 170px; font-weight:600}
.jeu-l .btn{padding:4px 9px; font-size:.88rem}
.jeu-l .btn.pick-ok{background:var(--vert); border-color:var(--vert); color:#fff}
.jeu-l .btn.pick-ko{background:var(--rouge); border-color:var(--rouge); color:#fff}
.jeu-l .btn.pick-good{outline:3px solid var(--vert); outline-offset:1px}
.jeu-l.is-ok{background:var(--vert-pale)} .jeu-l.is-ko{background:var(--rouge-pale)}
.jeu-fb{min-width:1.5em; font-size:1.1rem} .jeu-l.is-ok .jeu-fb{color:var(--vert)} .jeu-l.is-ko .jeu-fb{color:var(--rouge)}
.jeu-score{display:flex; align-items:center; gap:12px; font:700 1.2rem var(--f-titre); margin:8px 0 0}
.jeu-score .btn{font-size:.9rem; padding:5px 12px}
.cartes{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin:8px 0 14px}
.carte{display:flex; flex-direction:column; gap:6px; align-items:flex-start; text-align:left; min-height:90px; padding:12px 14px; border:2px solid var(--encre); border-left-width:8px; border-left-color:var(--bleu); background:var(--jaune-pale); font:inherit; cursor:pointer}
.carte b{font:700 1.08rem var(--f-titre); color:var(--bleu)}
.carte .dos{display:none; font-size:.93rem}
.carte[aria-expanded="true"]{background:#fff}
.carte[aria-expanded="true"] .dos{display:block}
.carte[aria-expanded="false"]::after{content:"Clique pour retourner"; font-size:.8rem; color:var(--encre-2)}
.cours-foot{display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 0}
.cours-foot .small{align-self:center}
table.t.cours-t td,table.t.cours-t th{vertical-align:middle}
.exo-c{border:1.5px solid var(--encre); border-left:6px solid var(--bleu); background:#fff; padding:8px 14px 10px; margin:10px 0; max-width:880px}
.exo-c.is-ok{border-left-color:var(--vert)} .exo-c.is-ko{border-left-color:var(--rouge)}
.exo-q{margin:0 0 4px; font-weight:600}
.exo-aide{margin:0 0 4px; font-size:.88rem; color:var(--encre-2)}
.exo-corps{margin:4px 0; line-height:2.5}
.exo-corps .t{margin:4px 0; width:auto}
.exo-corps .t th,.exo-corps .t td{text-align:center; padding:3px 8px}
.exo-in{width:5.6em; border:1.5px solid var(--encre-2); padding:4px 6px; font:600 .95rem var(--f-texte); background:#fff; border-radius:2px; text-align:center; vertical-align:middle}
.exo-in.exo-large{width:min(100%,22em); text-align:left}
.exo-in:focus{outline:3px solid var(--jaune); outline-offset:0}
.exo-in.ok{border-color:var(--vert); background:var(--vert-pale)}
.exo-in.demi{border-color:var(--orange); background:var(--jaune-pale)}
.exo-in.ko{border-color:var(--rouge); background:var(--rouge-pale)}
.exo-pied{display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:4px 0 0}
.exo-pied .btn{padding:6px 12px; font-size:.9rem}
.exo-fb{font-weight:700}
.exo-c.is-ok .exo-fb{color:var(--vert)} .exo-c.is-ko .exo-fb{color:var(--rouge)}
.exo-sol{border-top:1px dashed var(--trait); margin:8px 0 0; padding:6px 0 0; font-size:.94rem}
.exo-sol p{margin:.25rem 0}
.mini-anim{display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:10px; margin:10px 0}
.mini-anim figure{margin:0; background:#fff; border:1px solid var(--trait-fin); padding:6px}
.mini-anim svg{display:block; width:100%; height:auto}
.mini-anim figcaption{font-size:.86rem}
@media print{
  body.cours-page #home{display:block!important; padding:0}
  .no-print,.cours-nav,.cours-foot,.simu-btns{display:none!important}
  .quiz-why[hidden]{display:block!important}
  .exo-sol[hidden]{display:block!important}
  .exo-pied .btn{display:none!important}
  .carte .dos{display:block!important}
  .carte::after{display:none!important}
}
"""
