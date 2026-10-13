#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la page « Cinématique » (index.html) : un accueil sur le modèle du dépôt « Chaîne fonctionnelle » (lui-même
repris du dépôt « Résistance des matériaux »), deux cours interactifs (cinématique analytique, cinématique
graphique), un atelier de construction libre et les activités de cinématique analytique et de résolution graphique,
chacun ouvert par ?ex=….

    python3 src/generer.py

Le bloc <style> du gabarit, le moteur de correction (Grading) et le moteur applicatif sont recopiés tels quels ;
seules les entrées propres au sujet du moteur applicatif sont remplacées, chaque remplacement étant vérifié :
DECOR, DR_NAMES, le texte de la fenêtre « Imprimer les DR », le libellé « Diagramme validé » et le décompte « case(s)
juste(s) » des questions à plusieurs éléments, et CONSEIL_MIN, lu dans window.__CONSEIL_MIN__ puisque la durée
conseillée dépend de l'activité ouverte. Un petit script d'aiguillage, exécuté avant les moteurs, installe le contenu
demandé par l'adresse.

Les activités de résolution graphique (src/activites.py) reprennent chacune un exercice de la séquence « Cinématique
graphique » ; celles de cinématique analytique (src/activites_analytiques.py), une étude de système de la séquence
« Cinématique analytique ». Constructions et graphes se font dans l'atelier (src/atelier.py, src/atelier/), qui écrit
son verdict dans les champs masqués lus par le moteur du gabarit.
"""
import html
import json
import pathlib
import re
import types

import activites
import activites_analytiques
import atelier
import cours_analytique
import cours_commun
import cours_graphique
import cours_mouvements
from medias import IMAGES, image, png

ROOT = pathlib.Path(__file__).resolve().parent.parent
GABARIT = ROOT / "src" / "gabarit-exercice-interactif.html"
SORTIE = ROOT / "index.html"
TITRE = "Cinématique"


# ============================================================ outils
def esc(s):
    return html.escape(s, quote=True)


def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def hm(minutes):
    h, m = divmod(minutes, 60)
    return f"{h} h {m:02d}" if h else f"{m} min"


def sub_once(text, pattern, repl, flags=0):
    """Remplacement vérifié : le motif doit apparaître exactement une fois."""
    new, n = re.subn(pattern, lambda m: repl, text, flags=flags)
    assert n == 1, f"motif introuvable ou multiple : {pattern!r} ({n})"
    return new


def figure(name, alt, caption, maxw, cls="fig"):
    src, w, h = image(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" width="{w}" '
            f'height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def figures(s):
    """Remplace les repères __FIG:nom|texte alternatif|légende|largeur__ par la figure intégrée."""
    return re.sub(r"__FIG:([^|]+)\|([^|]*)\|([^|]*)\|(\d+)__", lambda m: figure(m[1], m[2], m[3], int(m[4])), s)


HOUSE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.3" '
         'stroke-linejoin="round" stroke-linecap="round"><path d="M3 11.5 12 4l9 7.5"/>'
         '<path d="M5.5 9.8V20h4.5v-5.5h4V20h4.5V9.8"/></svg>')


# ============================================================ rendu des questions
def render_q(q):
    qid, label = q["id"], q["num"]
    ins = (f'<button type="button" class="btn ghost ins-app" data-for="in-{qid}" aria-label="Insérer le symbole ∈" '
           'title="Insérer ∈">∈</button>') if q.get("ins") else ""
    return f"""
        <div class="q" id="{qid}" data-q="{qid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{q['stem']}</strong></p>
          <p class="q-hint" id="h-{qid}">{q['hint']}</p>
          <div class="q-row">
            <input type="text" class="q-input" id="in-{qid}" aria-label="Réponse {label}" aria-describedby="h-{qid}" autocomplete="off" autocapitalize="off" spellcheck="false">{ins}
            <button type="button" class="btn btn-validate">Valider</button>
            <span class="q-status" aria-live="polite"></span>
            <span class="print-only pstat">Non validée : comptée fausse</span>
          </div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-unit-msg" hidden></p>
            <p class="q-expected"><span>Réponse attendue :</span> {q['expected']}</p>
            <div class="q-why">{q['why']}</div>
          </div>
        </div>"""


def etiquettes(bank):
    return "".join(f'<button type="button" class="etq" draggable="true" aria-pressed="false">{esc(t)}</button>'
                   for t in bank)


def render_etq(b):
    """Cases à remplir avec des étiquettes : structure « fast-q » du gabarit (un bouton, une correction commune) ;
    chaque case garde le champ (masqué) que lit le moteur, rempli en y glissant une étiquette."""
    gid, label = b["id"], b["num"]
    rows = "".join(
        f'<div class="grp-l"><span class="grp-lab" id="lb-{fid}">{fl}</span><div class="sol">'
        f'<input type="hidden" id="in-{fid}" data-q="{fid}"><button type="button" class="dz" id="dz-{fid}" '
        f'data-bank="bk-{gid}" aria-labelledby="lb-{fid} dzv-{fid}"><span class="dz-v" id="dzv-{fid}">case vide</span>'
        f'</button><span class="mark" aria-live="polite"></span></div></div>'
        for fid, (fl, _g, _e) in zip(b["fids"], b["fields"]))
    sol = "".join(f"<tr><td>{fl}</td><td>{e}</td></tr>" for fl, _g, e in b["fields"])
    n = len(b["fields"])
    return f"""
        <div class="fast-q grp" id="{gid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{b['stem']}</strong></p>
          <p class="q-hint">{b['hint']}</p>
          <div class="bank" id="bk-{gid}" role="group" aria-label="Étiquettes de la question {label}"><span class="bank-t">{b['titre']}</span>{etiquettes(b['banque'])}</div>
          <div class="grp-fields" role="group" aria-label="Cases de la question {label}">{rows}</div>
          <div class="fast-foot"><button type="button" class="btn btn-fast">Valider {'les ' + str(n) + ' cases' if n > 1 else 'la case'}</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <table class="t grp-sol"><thead><tr><th>Case</th><th>Réponse attendue</th></tr></thead><tbody>{sol}</tbody></table>
            <div class="q-why">{b['why']}</div>
          </div>
        </div>"""


def render_champs(b):
    """Cases numériques insérées dans un texte (coefficients d'une équation horaire, tableau de valeurs) : structure
    « fast-q » du gabarit ; le repère [[i]] du modèle reçoit la i-ème case (numérotée à partir de 1)."""
    gid, label = b["id"], b["num"]

    def case(m):
        i = int(m[1]) - 1
        fid, fl = b["fids"][i], b["fields"][i][0]
        return (f'<span class="sol"><input type="text" class="ch-in" id="in-{fid}" data-q="{fid}" inputmode="decimal" '
                f'autocomplete="off" spellcheck="false" aria-label="{esc(re.sub(r"<[^>]+>", "", fl))}">'
                '<span class="mark" aria-live="polite"></span></span>')
    corps = re.sub(r"\[\[(\d+)\]\]", case, b["gabarit"])
    assert corps.count('class="ch-in"') == len(b["fields"]), f"{label} : cases du modèle"
    sol = "".join(f"<tr><td>{fl}</td><td>{e}</td></tr>" for fl, _g, e in b["fields"])
    n = len(b["fields"])
    return f"""
        <div class="fast-q grp champs" id="{gid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{b['stem']}</strong></p>
          <p class="q-hint">{b['hint']}</p>
          <div class="ch-corps">{corps}</div>
          <div class="fast-foot"><button type="button" class="btn btn-fast">Valider {'les ' + str(n) + ' cases' if n > 1 else 'la case'}</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <table class="t grp-sol"><thead><tr><th>Case</th><th>Réponse attendue</th></tr></thead><tbody>{sol}</tbody></table>
            <div class="q-why">{b['why']}</div>
          </div>
        </div>"""


def render_trace(b):
    """Éléments à construire sur la feuille : un champ masqué par élément, que l'atelier remplit (« juste », « faux »
    ou rien tant que rien n'est tracé) ; le bouton « Valider ma construction » relaie le bouton du gabarit."""
    gid, label = b["id"], b["num"]
    rows = "".join(
        f'<li class="it" id="it-{fid}"><span class="sol"><input type="hidden" id="in-{fid}" data-q="{fid}">'
        f'<span class="mark" aria-live="polite"></span></span><span class="it-lab">{esc(it["lab"])}</span>'
        '<span class="it-etat">à construire</span><span class="it-diag"></span></li>'
        for fid, it in zip(b["fids"], b["items"]))
    return f"""
        <div class="fast-q grp trace" id="{gid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{b['stem']}</strong></p>
          <p class="q-hint">{b['hint']}</p>
          <ul class="trace-items" aria-label="Éléments à construire sur la feuille">{rows}</ul>
          <div class="fast-foot"><button type="button" class="btn btn-trace">Valider ma construction</button>
            <button type="button" class="btn btn-fast" hidden>Valider</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-expected"><span>Correction :</span> superposée en rouge sur la feuille (bouton « Correction » de la barre d'outils).</p>
            <div class="q-why">{b['why']}</div>
          </div>
        </div>"""


def item_points(b):
    return {"q": 1, "etq": len(b.get("fields", ())), "trace": len(b.get("fields", ())),
            "champs": len(b.get("fields", ()))}.get(b["kind"], 0)


def part_points(p):
    return sum(item_points(b) for b in p["blocks"])


CUR = {"total": 1}


def pct(minutes):
    return fr(minutes / CUR["total"] * 100, 1)


def render_block(b):
    if b["kind"] == "q":
        return render_q(b)
    if b["kind"] == "etq":
        return render_etq(b)
    if b["kind"] == "trace":
        return render_trace(b)
    if b["kind"] == "champs":
        return render_champs(b)
    return b["html"]


def render_part(e, p):
    pts = part_points(p)
    body = figures("\n      ".join(p["intro"]))
    blocks = "".join(render_block(b) for b in p["blocks"])
    n = p["num"]
    if p.get("meca"):
        leg = ("Construis directement sur la feuille. Les points de la figure, les extrémités et les intersections de tes "
               "tracés attirent le pointeur. Ctrl + molette (ou deux doigts) : zoom ; outil Déplacer : faire glisser la "
               "feuille ; Échap : annuler l'étape en cours.")
        if p["meca"].F.graphes:
            leg = ("Trace sur les graphes : la position du pointeur s'y lit en unités physiques et les nœuds du "
                   "quadrillage l'attirent ; « Placer un point » pose un point par ses coordonnées. Segment pour une "
                   "portion droite, Courbe pour un arc de parabole (pose ses points, puis touche à nouveau le dernier). "
                   "Ctrl + molette (ou deux doigts) : zoom ; Échap : annuler l'étape en cours.")
        zone = (f'<div class="at-zone">{atelier.render(p["at_id"], p["meca"].F, leg, p["noms"])}'
                f'<div class="at-questions">{blocks}</div></div>')
    else:
        zone = blocks
    return f"""
  <section class="part" id="partie-{n}" aria-labelledby="t-partie-{n}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{n}</div>
      <div><h2 id="t-partie-{n}"><span class="sr-only">Partie {n} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {hm(p['minutes'])} · Barème : {pts} points, soit {pct(p['minutes'])} % de la note</div></div></header>
    <div class="part-body">
      {body}{zone}
    </div>
  </section>"""


ATELIERS = {}  # configurations de toutes les feuilles (activités, cours, atelier libre) : window.__ATELIERS__


def prepare_exo(e):
    """Numérote blocs et champs, calcule la configuration des moteurs (gabarit) et des feuilles (atelier)."""
    parts = e["parts"]
    k = 0
    for i, p in enumerate(parts):
        p["num"] = str(i + 1)
        p["at_id"] = f"at-{e['key']}-{p['num']}"
        cfg = p["meca"].F.config() if p.get("meca") else None
        if cfg:
            cfg.update({"items": {}, "groupes": {}, "corr": {}})
        for b in p["blocks"]:
            if b["kind"] in ("q", "etq", "trace", "champs"):
                k += 1
                b["id"] = f"{e['prefix']}{k}"
                if b["kind"] != "q":
                    b["fids"] = [f"{b['id']}_{j + 1}" for j in range(len(b["fields"]))]
                if b["kind"] == "trace":
                    assert cfg, f"{e['key']} : une construction sans feuille"
                    cfg["groupes"][b["id"]] = b["fids"]
                    cfg["corr"][b["id"]] = b["corr"]
                    for fid, it in zip(b["fids"], b["items"]):
                        cfg["items"][fid] = it
        if cfg:
            ATELIERS[p["at_id"]] = cfg
    e["P"] = parts
    e["minutes"] = sum(p["minutes"] for p in parts)
    blocs = [b for p in parts for b in p["blocks"] if b["kind"] in ("q", "etq", "trace", "champs")]
    e["n_q"] = len({re.match(r"Q\d+(?:\.\d+)?", b["num"])[0] for b in blocs})
    e["n_trace"] = sum(len(b["fields"]) for b in blocs if b["kind"] == "trace")
    e["points"] = sum(part_points(p) for p in parts)
    qcfg, parts_cfg = {}, []
    for p in parts:
        parts_cfg.append({"num": p["num"], "title": re.sub(r"<[^>]+>", "", p["title"]), "minutes": p["minutes"],
                          "duration": hm(p["minutes"]), "points": part_points(p)})
        for b in p["blocks"]:
            if b["kind"] == "q":
                qcfg[b["id"]] = {"label": b["num"], "part": p["num"], "pts": 1, "grader": b["grader"]}
            elif b["kind"] in ("etq", "trace", "champs"):
                for fid, (fl, gr, _x) in zip(b["fids"], b["fields"]):
                    qcfg[fid] = {"label": f"{b['num']} — {re.sub(r'<[^>]+>', '', fl)}", "part": p["num"], "pts": 1,
                                 "grader": gr}
    np_ = len(parts)
    traces = f" dont {e['n_trace']} éléments à construire sur la feuille" if e["n_trace"] else ""
    e["cfg"] = {"title": e["title"], "minutes": e["minutes"], "duree": hm(e["minutes"]),
                "consignes": "tpl-consignes-ana" if e.get("dt") == "ana" else "tpl-consignes",
                "atelier": any(p.get("meca") for p in parts),
                "cartouche": f"{e['n_q']} questions, {e['points']} points{traces}, en {np_} partie{'s' if np_ > 1 else ''}"
                             + (" pondérées par leur durée." if np_ > 1 else "."),
                "parts": parts_cfg, "qcfg": qcfg, "skcfg": {}}


# ============================================================ documents des activités
DT1 = ("Méthodes de la cinématique graphique", """<div class="doc-text">
<h3>Le vecteur vitesse</h3>
<p>V(M∈S/R) : vitesse du point M appartenant au solide S, dans son mouvement par rapport à R. Il se décrit par son
<strong>origine</strong> (le point M), sa <strong>direction</strong> (tangente à la trajectoire de M), son
<strong>sens</strong> (celui du mouvement) et sa <strong>norme</strong> (en m/s), tracée à l'échelle des vitesses.</p>
<ul><li>Translation : tous les points ont, à un instant donné, la même vitesse.</li>
<li>Rotation autour d'un axe fixe O : V(M) est perpendiculaire à (OM) ; ‖V(M)‖ = OM × ω, avec ω = 2π·N/60 (rad/s) ;
les vitesses sont proportionnelles à la distance à l'axe (répartition linéaire).</li>
<li>Centre d'une liaison pivot entre deux solides : les deux solides y ont la même vitesse.</li></ul>
<h3>Équiprojectivité (deux points d'un même solide)</h3>
<ol><li>Tracer le vecteur vitesse connu (point A).</li><li>Tracer le support du vecteur vitesse inconnu (point B).</li>
<li>Tracer la droite de projection (AB).</li><li>Projeter orthogonalement le vecteur connu sur (AB) : segment [AA'].</li>
<li>Reporter cette projection au point B : segment [BB'], dans le même sens.</li>
<li>Tracer la perpendiculaire à (AB) passant par B'.</li>
<li>Son intersection avec le support donne l'extrémité du vecteur cherché.</li></ol>
<h3>Centre instantané de rotation (CIR)</h3>
<ol><li>À partir de deux supports de vitesses connus, tracer les perpendiculaires à ces supports : le CIR est à leur
intersection.</li><li>La vitesse d'un autre point M est perpendiculaire à (IM).</li>
<li>Tracer la droite de proportionnalité, par le CIR et l'extrémité d'un vecteur connu.</li>
<li>Reporter le point M sur le rayon du vecteur connu (au compas, IM).</li>
<li>Tracer le vecteur perpendiculaire au rayon jusqu'à la droite de proportionnalité, puis le reporter en M.</li></ol>
<p>Dans un mouvement de translation, le CIR est rejeté à l'infini.</p>
<h3>Composition des vitesses</h3>
<p>V(M∈3/1) = V(M∈3/2) + V(M∈2/1) : vitesse absolue = vitesse relative + vitesse d'entraînement. Si l'un des vecteurs
est connu et que les deux autres n'ont que leur direction, on construit le parallélogramme : par l'extrémité du
vecteur connu, on trace la parallèle à l'une des directions ; elle coupe l'autre.</p>
<h3>L'atelier de construction</h3>
<ul><li><strong>Droite</strong>, <strong>Segment</strong> : par deux points. <strong>Perpendiculaire</strong>,
<strong>Parallèle</strong> : touche d'abord la droite de référence (un axe, une droite, un segment, un vecteur), puis le
point de passage. <strong>Projeté</strong> : le point, puis la droite.</li>
<li><strong>Cercle</strong> : centre, puis un point. <strong>Compas</strong> : prends un écartement entre deux points,
puis pique au centre du cercle à tracer (report de longueur).</li>
<li><strong>Vecteur</strong> : origine, puis extrémité ; la barre sous la feuille permet de le nommer (V(A∈1/0)…) et de
régler sa longueur au millimètre. <strong>Mesurer</strong> : distance et angle entre deux points.</li>
<li>Les tracés s'accrochent aux points, aux extrémités et aux intersections. Raccourcis : V vecteur, D droite, S segment,
E perpendiculaire, A parallèle, O projeté, C cercle, K compas, M mesurer, P point, G gomme, H déplacer ; Ctrl+Z annuler.</li></ul>
</div>""")

DT_ANA = ("Formulaire de cinématique analytique", """<div class="doc-text">
<h3>Position, vitesse, accélération</h3>
<p>Le mouvement d'un point M est connu par son équation horaire x = f(t) (abscisse curviligne, en m ou mm). La
vitesse est la dérivée de la position, l'accélération la dérivée de la vitesse :</p>
<ul><li>v(t) = dx/dt = x'(t) (m/s) ; γ(t) = dv/dt = x''(t) (m/s²) ;</li>
<li>pour un vecteur position OM = x(t)·x + y(t)·y + z(t)·z : V(M∈S/R) = x'·x + y'·y + z'·z et
Γ(M∈S/R) = x''·x + y''·y + z''·z ; ‖V‖ = √(x'² + y'² + z'²).</li>
<li>Accélération moyenne entre t<sub>1</sub> et t<sub>2</sub> : γ<sub>moy</sub> = (v<sub>2</sub> − v<sub>1</sub>) /
(t<sub>2</sub> − t<sub>1</sub>).</li></ul>
<h3>Mouvement rectiligne uniforme (MRU)</h3>
<p>γ = 0 ; v = constante ; x(t) = v·t + x<sub>0</sub>. Graphe des espaces : une droite de pente v ; graphe des
vitesses : une horizontale.</p>
<h3>Mouvement rectiligne uniformément varié (MRUV)</h3>
<p>γ = constante ; v(t) = γ·t + v<sub>0</sub> ; x(t) = ½ γ·t² + v<sub>0</sub>·t + x<sub>0</sub>. Sans le temps :
v² − v<sub>0</sub>² = 2 γ (x − x<sub>0</sub>). Accéléré si γ et v sont de même signe, décéléré sinon. Graphe des
espaces : un arc de parabole ; des vitesses : une droite de pente γ ; des accélérations : une horizontale.</p>
<ul><li>Distance parcourue = aire sous la courbe des vitesses = vitesse moyenne × durée, avec, pour un MRUV,
v<sub>moy</sub> = (v<sub>début</sub> + v<sub>fin</sub>) / 2.</li>
<li>Origine des temps placée au début d'une phase : t' = t − t<sub>début</sub> ; x<sub>0</sub> et v<sub>0</sub> sont
alors la position et la vitesse au début de la phase. Dans le repère absolu, on écrit la continuité de la position et
de la vitesse à l'instant où la phase commence.</li></ul>
<h3>Mouvement circulaire (rotation d'axe fixe)</h3>
<ul><li>Abscisse angulaire θ (rad), vitesse angulaire ω = θ' (rad/s), accélération angulaire θ'' (rad/s²).</li>
<li>Abscisse curviligne s = R·θ ; vitesse v = R·ω ; ω = 2π·N / 60 (N en tr/min).</li>
<li>MCU : θ = ω·t + θ<sub>0</sub> ; accélération normale Γ<sub>n</sub> = R·ω² = v² / R, dirigée vers le centre.</li>
<li>MCUV : θ = ½ θ''·t² + ω<sub>0</sub>·t + θ<sub>0</sub> ; ω = θ''·t + ω<sub>0</sub> ; Γ<sub>t</sub> = R·θ''.</li>
<li>Transmission par poulies et courroie (sans glissement) : même vitesse linéaire de la courroie, ω<sub>1</sub>·R<sub>1</sub>
= ω<sub>2</sub>·R<sub>2</sub>.</li></ul>
<h3>Graphes sur la feuille</h3>
<ul><li>La position du pointeur se lit en unités physiques sous la feuille ; les nœuds du quadrillage attirent le
pointeur ; « Placer un point » pose un point par ses coordonnées (avec l'outil en cours : point, segment, courbe…).</li>
<li><strong>Segment</strong> : une portion droite (sa pente s'affiche pendant le tracé). <strong>Courbe</strong> :
pose les points un à un, puis touche à nouveau le dernier point (ou Entrée, ou « Terminer la courbe ») ; la courbe
passe par les points posés, lissée (une case de la barre de propriétés la rend brisée).</li>
<li>Une portion de courbe est juste si le tracé la suit à 2 mm près sur la feuille. Raccourcis : P point, S segment,
D droite, U courbe, M mesurer, G gomme, H déplacer ; Ctrl+Z annuler.</li></ul>
</div>""")

DP = {
    "imprimante-3d": ("Imprimante 3D", '<div class="doc-text"><h3>Axe x d\'une imprimante 3D</h3><p>Le chariot (1) porte '
                      "la buse qui dépose l'ABS fondu. Il est guidé en translation par deux pivots glissants parallèles "
                      "(A et B) et entraîné par le moteur M<sub>1</sub> par l'intermédiaire d'une liaison hélicoïdale "
                      "(C). L'axe y, identique, est placé en dessous.</p></div>__FIG:photo-imprimante|Schéma de l'axe x "
                      "d'une imprimante 3D|Chariot (1), bâti (0), moteur M<sub>1</sub>.|600__"),
    "vanne-admission": ("Vanne d'admission d'air", '<div class="doc-text"><h3>Vanne additionnelle d\'air</h3><p>Montée '
                        "sur le corps d'injection, elle régule le débit d'air entrant dans le moteur. Le moteur de la "
                        "vanne (liaison pivot) entraîne le boisseau en translation par une glissière hélicoïdale de pas "
                        "0,5 mm ; le boisseau ouvre ou ferme le passage de l'air.</p></div>__FIG:photo-vanne|Corps "
                        "d'injection, vanne d'air et schéma cinématique|Vanne d'air et schéma cinématique.|520__"),
    "agv": ("Automotrice à grande vitesse", '<div class="doc-text"><h3>L\'AGV</h3><p>Train à grande vitesse construit par '
            "Alstom, à motorisation répartie le long de la rame.</p><ul><li>Juin 2004 : lancement du programme de "
            "réalisation du prototype de l'AGV.</li><li>3 avril 2007 : le TGV bat, avec les composants de l'AGV, un "
            "nouveau record du monde sur rail (574,8 km/h).</li><li>17 janvier 2008 : Alstom et NTV, premier opérateur "
            "privé sur les lignes italiennes à grande vitesse, signent le premier contrat AGV.</li><li>5 février 2008 : "
            "l'AGV est officiellement dévoilé à la presse.</li><li>Octobre 2010 : livraison du premier exemplaire en "
            "Italie.</li></ul></div>__FIG:photo-agv|Automotrice à grande vitesse|L'AGV.|640__"),
    "arbre-transmission": ("Arbre de transmission", '<div class="doc-text"><h3>Arbre de transmission</h3><p>L\'arbre porte, '
                           "en liaison encastrement, plusieurs roues dentées de diamètres différents : la roue (1) "
                           "(Ø 50 mm) et la roue (4) (Ø 100 mm). L'ensemble forme un seul solide en rotation autour de "
                           "l'axe (O, <span class=vec>z</span>).</p></div>__FIG:photo-arbre|Arbre de transmission|Roues (1) et (4).|600__"),
    "embiellage-moto": ("Embiellage de moto", '<div class="doc-text"><h3>Embiellage de moto en V</h3><p>Coupe d\'un '
                        "cylindre : 0 bloc ; 1 vilebrequin ; 2 et 3 bielles ; 4 axe de piston ; 5 piston ; 6 ailettes de "
                        "refroidissement ; 7 joint de culasse ; 8 culasse ; 9 soupape d'admission ; 10 soupape "
                        "d'échappement ; 11 chemise.</p></div>__FIG:photo-embiellage|Coupe d'un cylindre de l'embiellage|"
                        "Coupe d'un cylindre.|420__"),
    "pompe-petrole": ("Pompe à tête de cheval", '<div class="doc-text"><h3>Pompe à pétrole « tête de cheval »</h3><p>Le '
                      "moteur entraîne, par un réducteur, la manivelle (1) munie de contrepoids d'équilibrage ; la "
                      "biellette (2) fait osciller le balancier (3), dont la tête tire le câble (4).</p></div>"
                      "__FIG:photo-pompe|Pompe à pétrole à tête de cheval|Figure à échelle réduite.|680__"),
    "suspension-vtt": ("VTT Vario Bomba", '<div class="doc-text"><h3>VTT Vario Bomba</h3><p>Suspension arrière à '
                       "triangle unifié : le bras oscillant S1 pivote en H sur le cadre S0 ; la biellette S2 relie S1 au "
                       "levier basculeur S3, qui comprime l'amortisseur (S4 piston, S5 corps).</p></div>"
                       "__FIG:photo-vtt|VTT tout suspendu|Le VTT.|560____FIG:photo-vtt-suspension|Mécanisme de suspension arrière|"
                       "Le mécanisme de suspension : S0 à S5.|560__"),
}


def render_docs(e):
    docs = []
    if e["key"] in DP:
        docs.append(("DP1", DP[e["key"]][0], "Dossier présentation", False, figures(DP[e["key"]][1])))
    dt = DT_ANA if e.get("dt") == "ana" else DT1
    docs.append(("DT1", dt[0], "Dossier technique", True, dt[1]))
    rail, tabs, secs, first_dt = [], [], [], True
    for key, title, kind, is_dt, content in docs:
        if is_dt and first_dt and rail:
            rail.append('<div class="grp" aria-hidden="true"></div>')
        first_dt = first_dt and not is_dt
        rail.append(f'<button type="button" class="tab{" dt" if is_dt else ""}" data-doc="{key}" aria-selected="false" '
                    f'title="{esc(title)}">{key}</button>')
        tabs.append(f'<button type="button" data-doc="{key}" aria-selected="false">{key}</button>')
        secs.append(f'<section class="doc" id="doc-{key}" data-title="{key} : {esc(title)}" data-kind="{kind}">{content}\n</section>')
    return "".join(rail), "".join(tabs), "\n".join(secs), [d[0] for d in docs]


# ============================================================ accueil
PARTIES = {"analytique": ("Analytique", "n1"), "graphique": ("Graphique", "n2")}


def pastille(partie):
    if not partie:
        return ""
    lab, cls = PARTIES[partie]
    return f' <span class="pastille {cls}">{lab}</span>'


def render_exo_home(e, docs):
    src = e.get("hero")
    fig = ""
    if src:
        s, w, h = image(src[0])
        fig = (f'<figure class="home-hero"><img src="{s}" alt="{esc(src[1])}" width="{w}" height="{h}">'
               f'<figcaption class="small">{src[2]}</figcaption></figure>')
    docs_txt = " et ".join(docs)
    facts = ('<div class="home-facts">'
             f'<div><b>{e["n_q"]} questions</b><span>{e["points"]} points</span></div>'
             f'<div><b>{hm(e["minutes"])}</b><span>durée conseillée</span></div>'
             + (f'<div><b>{e["n_trace"]} tracés</b><span>vérifiés sur la feuille</span></div>' if e["n_trace"] else
                f'<div><b>{len(e["P"])} partie{"s" if len(e["P"]) > 1 else ""}</b><span>pondérées par leur durée</span></div>')
             + f'<div><b>{len(docs)} document{"s" if len(docs) > 1 else ""}</b><span>{docs_txt}</span></div></div>')
    return (f'<div class="home-top{"" if fig else " home-top-single"}"><div class="home-top-l"><header class="home-head">'
            f'<span class="mc-tag">{e["tag"]}</span>{pastille(e.get("partie", "graphique"))}'
            f'<h1 id="home-title">{e["title"]}</h1><p class="home-sub">{e["sub"]}</p></header>{facts}</div>{fig}</div>')


MODES_HTML = """<h2 class="home-choose">Choisis ton mode de travail</h2>
<div class="modes">
  <article class="mode-card">
    <div class="mc-head"><span class="mc-tag">Mode 1</span><h3>Mode entraînement</h3></div>
    <p class="mc-lead">Pour apprendre en avançant, question par question.</p>
    <ul><li>Chaque question se valide isolément ; la démarche corrigée s'affiche aussitôt, et la construction attendue se superpose en rouge à la feuille.</li>
      <li>La note pondérée s'actualise en continu dans le bandeau.</li>
      <li>Les documents et le chronomètre restent disponibles, sans contrainte de temps.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="training">Commencer l'entraînement</button>
  </article>
  <article class="mode-card exam">
    <div class="mc-head"><span class="mc-tag">Mode 2</span><h3>Mode examen</h3></div>
    <p class="mc-lead">Pour se placer dans les conditions d'une évaluation.</p>
    <ul><li>Aucune correction et aucune note pendant la composition ; réponses et tracés restent modifiables.</li>
      <li>Le chronomètre tourne, à comparer à la durée conseillée.</li>
      <li>En fin de sujet, le bouton « J'ai fini, je fais corriger ma copie » dévoile d'un coup les corrections, les notes par partie et la note globale.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="exam">Composer en mode examen</button>
  </article>
</div>
<p class="home-note small">Le mode se choisit une seule fois : pour en changer, reviens à l'accueil (onglet maison) et rouvre l'activité. Rien n'est enregistré sur l'ordinateur.</p>
<p class="home-back"><a class="btn ghost" href="?">""" + HOUSE + """ Retour à l'accueil</a></p>"""

CONSIGNES = """<p class="only-training"><strong>Mode entraînement.</strong> Réponds puis valide question par question : une réponse validée est définitive, sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : réponses et tracés restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>
    <p><strong>Les tracés se font sur la feuille</strong>, à côté des questions (elle reste à l'écran pendant que tu fais défiler les questions ; le bouton « Plein écran » l'agrandit avec les questions). Outils du papier : règle (droite, segment), équerre (perpendiculaire, parallèle, projeté), compas, vecteur, mesure. Les éléments attendus par une question sont listés sous son énoncé : « tracé repéré » indique que l'atelier a trouvé un tracé à cet endroit, sans dire s'il est juste. <strong>Nomme tes vecteurs</strong> (V(A∈1/0)…) : un vecteur nommé ne compte que pour la vitesse de ce nom.</p>
    <p><strong>Tolérances.</strong> Un vecteur est juste si son origine est sur le point (à 1,5 mm près), sa direction à 3° près et sa longueur à 6 % près ; une valeur lue sur le tracé est acceptée à 5 à 8 % près. <strong>Les unités sont notées</strong> : une valeur juste sans unité, ou avec une unité fausse, ne rapporte que la moitié des points.</p>
    <p>Le dossier technique DT1 (méthodes graphiques et mode d'emploi de l'atelier) et, s'il existe, le dossier de présentation DP1 s'ouvrent avec les onglets sur le bord droit.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps.</p>"""

CONSIGNES_ANA = """<p class="only-training"><strong>Mode entraînement.</strong> Réponds puis valide question par question : une réponse validée est définitive, sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : réponses et tracés restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>
    <p><strong>Réponses.</strong> Une valeur se saisit avec son unité : <strong>les unités sont notées</strong>, une valeur juste sans unité, ou avec une unité fausse, ne rapporte que la moitié des points. Les cases d'une équation ou d'un tableau attendent un nombre seul (l'unité est écrite à côté) ; écris 0 pour un terme absent ; elles se valident ensemble. Les valeurs calculées sont acceptées à 1 % près, celles lues sur un graphe à 3 % près.</p>
    <p><strong>Graphes à compléter.</strong> Lorsqu'une partie en comporte, ils se tracent sur la feuille placée à côté des questions (le bouton « Plein écran » l'agrandit avec les questions). Sous la feuille, la position du pointeur se lit en unités physiques et « Placer un point » pose un point par ses coordonnées. Une portion de courbe est juste si ton tracé la suit à 2 mm près sur la feuille.</p>
    <p>Le formulaire DT1 (MRU, MRUV, mouvement circulaire, mode d'emploi des graphes) et, s'il existe, le dossier de présentation DP1 s'ouvrent avec les onglets sur le bord droit.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps.</p>"""

COURS = [
    {"key": "cours-cinematique-analytique", "tag": "Cours 1", "partie": "analytique", "title": "Cinématique analytique",
     "mots": ["Référentiel", "Trajectoire", "Vitesse", "Accélération", "MRUV"], "vign": "carte-cours-1",
     "alt": "Trajectoires des points d'une roue de vélo"},
    {"key": "cours-cinematique-graphique", "tag": "Cours 2", "partie": "graphique", "title": "Cinématique graphique",
     "mots": ["Vecteur vitesse", "Équiprojectivité", "CIR", "Composition"], "vign": "carte-cours-2",
     "alt": "Construction du centre instantané de rotation d'une bielle"},
]
ATELIER_LIBRE = {"key": "atelier-libre", "tag": "Atelier", "title": "Atelier de construction libre",
                 "mots": ["Feuille vierge", "Règle", "Équerre", "Compas", "Vecteurs"], "vign": "carte-atelier",
                 "alt": "Feuille de construction quadrillée et ses outils"}
ANALYTIQUE_A_VENIR = ("Activité 1.1", "Cinématique du point", ["Mouvement uniforme", "Uniformément varié", "Rotation"],
                      "carte-analytique", "Courbes du mouvement uniformément accéléré")
ETUDE_A_VENIR = ("Étude 1", "Étude de cas", ["Système réel", "Analytique", "Graphique"], "carte-etude",
                 "Chargeur compact en position de levage")
OUVRIR = "Ouvrir l'activité"


def carte(tag, title, mots, href, bouton, vign=None, alt="", cls=""):
    """Carte de l'accueil : vignette, étiquette, titre, mots-clés, bouton."""
    img = '<div class="cv-img cv-vide" aria-hidden="true"></div>'
    if vign and ((IMAGES / f"{vign}.png").exists() or (IMAGES / f"{vign}.jpg").exists()):
        src, w, h = image(vign)
        img = f'<img class="cv-img" src="{src}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy">'
    mots_html = '<ul class="cv-mots">' + "".join(f"<li>{m}</li>" for m in mots) + "</ul>"
    btn = f'<a class="btn" href="{href}">{bouton}</a>' if href else '<p class="small ex-meta etat">En cours d\'édition</p>'
    return (f'<article class="mode-card carte-v {cls}">{img}<div class="mc-head"><span class="mc-tag">{tag}</span>'
            f"<h3>{title}</h3></div>{mots_html}{btn}</article>")


def render_hub(exos):
    hero = ""
    if (IMAGES / "accueil.png").exists():
        src, w, h = png("accueil")
        hero = (f'<figure class="home-hero"><img src="{src}" alt="Mécanismes étudiés : ellipsographe, embiellage, pompe à '
                f'pétrole et chargeur compact, avec leurs constructions" width="{w}" height="{h}">'
                '<figcaption class="small">Les mécanismes des activités de résolution graphique.</figcaption></figure>')
    cours = "".join(carte(c["tag"] + pastille(c["partie"]), c["title"], c["mots"], f'?ex={c["key"]}', "Lire le cours",
                          c["vign"], c["alt"], "cours-card") for c in COURS)
    outil = carte(ATELIER_LIBRE["tag"], ATELIER_LIBRE["title"], ATELIER_LIBRE["mots"], f'?ex={ATELIER_LIBRE["key"]}',
                  "Ouvrir l'atelier", ATELIER_LIBRE["vign"], ATELIER_LIBRE["alt"])
    def cartes_de(partie):
        return "".join(carte(e["tag"] + pastille(partie), e["title"], e["mots"], f'?ex={e["key"]}', OUVRIR,
                             f'carte-{e["key"]}', e["title"]) for e in exos if e.get("partie", "graphique") == partie)
    a = ANALYTIQUE_A_VENIR  # tant qu'aucune activité analytique n'est décrite, une carte l'annonce
    analytique = cartes_de("analytique") or carte(a[0] + pastille("analytique"), a[1], a[2], None, None, a[3], a[4],
                                                  "en-edition")
    graphiques = cartes_de("graphique")
    t = ETUDE_A_VENIR
    etudes = carte(t[0], t[1], t[2], None, None, t[3], t[4], "en-edition")
    return (f'<div class="home-top{"" if hero else " home-top-single"}"><div class="home-top-l"><header class="home-head">'
            f'<h1 id="home-title">{TITRE}</h1>'
            "<p class=\"home-sub\">Décrire et quantifier le mouvement des solides : référentiels, trajectoires, vitesses "
            "et accélérations par le calcul (cinématique analytique), puis vitesses des points d'un mécanisme plan par "
            "construction (cinématique graphique : équiprojectivité, centre instantané de rotation, composition des "
            "vitesses). Des cours interactifs, un atelier de construction et des activités à faire en mode entraînement "
            f"ou en mode examen.</p></header></div>{hero}</div>"
            f'<h2 class="home-choose">Les cours</h2><div class="ex-grid cours-grid">{cours}</div>'
            f'<h2 class="home-choose">L\'atelier de construction</h2><div class="ex-grid outil-grid">{outil}</div>'
            f'<h2 class="home-choose">Activités de cinématique analytique</h2><div class="ex-grid analytique-grid">{analytique}</div>'
            f'<h2 class="home-choose">Activités de résolution graphique</h2><div class="ex-grid exo-grid">{graphiques}</div>'
            f'<h2 class="home-choose">Études de cas</h2><div class="ex-grid etude-grid">{etudes}</div>'
            f'<p class="home-note small">Pastilles : {pastille("analytique").strip()} cinématique analytique (calcul), '
            f'{pastille("graphique").strip()} résolution graphique (construction). Chaque activité reprend un exercice '
            "et propose le mode entraînement (correction question par question) ou le mode examen (correction à la "
            "remise de la copie). Rien n'est enregistré sur l'ordinateur.</p>")


# ============================================================ atelier libre
def render_atelier_libre():
    F = atelier.Feuille(277, 190, "Feuille de construction libre")
    F.texte((6, 186), "Feuille A4 paysage, 277 × 190 mm", "note", 3, "start")
    cfg = F.config()
    cfg.update({"items": {}, "groupes": {}, "corr": {}, "grille": True})
    ATELIERS["at-libre"] = cfg
    return (f'<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head">'
            f'<span class="mc-tag">Atelier</span><h1 id="home-title">Atelier de construction libre</h1>'
            '<p class="home-sub">Une feuille quadrillée et les outils des activités, pour s\'exercer aux constructions '
            "(équiprojectivité, CIR, composition des vitesses) ou préparer un tracé. Rien n'est corrigé ni "
            "enregistré ; le bouton « DR vierge » imprime la feuille à taille réelle.</p></header></div></div>"
            '<p class="c-top"><a href="?">' + HOUSE + ' Accueil</a></p>'
            f'<div class="at-zone at-libre">{atelier.render("at-libre", F, "Feuille en millimètres. Ctrl + molette : zoom ; outil Déplacer : faire glisser.", ["V(A∈1/0)", "V(B∈2/0)", "I2/0"])}'
            '<div class="at-questions"><div class="doc-text">' + DT1[1].split("<h3>L'atelier de construction</h3>")[1] +
            "</div></div></div>")


# ============================================================ aiguillage
ROUTER_JS = r"""<script>/* Aiguillage : accueil, cours, atelier ou activité selon ?ex=… — s'exécute avant les moteurs du gabarit */
(function () {
  "use strict";
  var EXOS = window.__EXOS__, ex = new URLSearchParams(location.search).get("ex") || "";
  function $(s) { return document.querySelector(s); }
  function tpl(id) { return document.getElementById(id).innerHTML; }__COURS_JS__
  var home = $("#home .home-inner");
  window.__PARTS__ = []; window.__QCFG__ = {}; window.__SKCFG__ = {}; window.__CONSEIL_MIN__ = 0;
  if (Object.prototype.hasOwnProperty.call(EXOS, ex)) {
    var E = EXOS[ex];
    window.__PARTS__ = E.parts; window.__QCFG__ = E.qcfg; window.__SKCFG__ = E.skcfg;
    window.__CONSEIL_MIN__ = E.minutes;
    document.title = E.title + " — __TITRE__ — activité interactive";
    document.body.classList.add("exo-" + ex);
    if (E.atelier) document.body.classList.add("exo-atelier");
    $(".rail").innerHTML = tpl("tpl-rail-" + ex) + '<div class="grp" aria-hidden="true"></div>' +
      '<a class="tab tab-home" href="?" title="Retour à l\'accueil" aria-label="Retour à l\'accueil">__HOUSE__</a>';
    $(".dp-tabs").innerHTML = tpl("tpl-tabs-" + ex);
    $(".dp-body").innerHTML = tpl("tpl-docs-" + ex);
    $("#parts").innerHTML = tpl("tpl-parts-" + ex);
    $(".consignes").innerHTML = tpl(E.consignes || "tpl-consignes");
    home.innerHTML = tpl("tpl-home-" + ex) + tpl("tpl-modes");
    $(".cartouche h1").textContent = E.title;
    $(".cartouche .title p").textContent = E.cartouche;
    Array.prototype.forEach.call(document.querySelectorAll(".print-conseil"), function (el) { el.textContent = E.duree; });
  } else {
    document.body.classList.add("hub");
    var page = document.getElementById("tpl-" + ex) && /^(cours-|atelier-libre$)/.test(ex) ? "tpl-" + ex : "tpl-hub";
    home.innerHTML = tpl(page);
    if (page !== "tpl-hub") {
      document.body.classList.add("cours-page", "page-" + ex);
      if (typeof INIT[ex] === "function") INIT[ex](home);
      document.title = home.querySelector("h1").textContent + " — __TITRE__";
    } else document.title = "__TITRE__ — cours et activités interactifs";
  }
})();
</script>"""

# insertion du symbole ∈ dans une réponse (relations de composition des vitesses)
INSERT_JS = r"""<script>(function () {
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".ins-app");
    if (!b) return;
    var i = document.getElementById(b.dataset.for);
    if (!i || i.disabled) return;
    var a = i.selectionStart == null ? i.value.length : i.selectionStart, z = i.selectionEnd == null ? a : i.selectionEnd;
    i.value = i.value.slice(0, a) + "∈" + i.value.slice(z);
    i.focus(); i.setSelectionRange(a + 1, a + 1);
    i.dispatchEvent(new Event("input", { bubbles: true }));
  });
})();
</script>"""

# Étiquettes (repris du dépôt « Chaîne fonctionnelle », sans les schémas à cases) : glisser une étiquette sur une case,
# ou la toucher puis toucher la case ; la case garde le champ masqué que lit le moteur du gabarit.
ETIQUETTES_JS = r"""<script>/* Étiquettes : glisser une étiquette sur une case, ou la toucher puis toucher la case. */
(function () {
  "use strict";
  var parts = document.getElementById("parts");
  if (!parts || !parts.querySelector(".bank")) return;
  var sel = null, drag = null;
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function inp(dz) { return document.getElementById("in-" + dz.id.slice(3)); }
  function banque(el) { return el.classList.contains("dz") ? document.getElementById(el.dataset.bank) : el.closest(".bank"); }
  function cases(bk) { return $$('.dz[data-bank="' + bk.id + '"]'); }
  function msgDe(el) { return el.closest(".fast-q").querySelector(".q-msg"); }
  function choisir(b) {
    if (sel) { sel.setAttribute("aria-pressed", "false"); cases(banque(sel)).forEach(function (d) { d.classList.remove("cible"); }); }
    sel = b && b !== sel ? b : null;
    if (sel) { sel.setAttribute("aria-pressed", "true"); cases(banque(sel)).forEach(function (d) { if (!d.disabled) d.classList.add("cible"); }); }
  }
  function poser(dz, v) {
    var i = inp(dz);
    if (i.disabled) return;
    i.value = v;
    dz.classList.toggle("filled", !!v);
    dz.querySelector(".dz-v").textContent = v || "case vide";
    dz.draggable = !!v;
    msgDe(dz).textContent = "";
    i.dispatchEvent(new Event("input", { bubbles: true }));
  }
  parts.addEventListener("click", function (e) {
    var b = e.target.closest(".etq"), dz = e.target.closest(".dz");
    if (b && !b.disabled) {
      choisir(b);
      if (sel && e.detail === 0) {  /* au clavier : on passe à la première case libre qui accepte l'étiquette */
        var libres = cases(banque(sel)).filter(function (d) { return !d.disabled; });
        var d = libres.filter(function (x) { return !inp(x).value; })[0] || libres[0];
        if (d) d.focus();
      }
      return;
    }
    if (!dz || dz.disabled) return;
    if (sel && banque(sel) === banque(dz)) { poser(dz, sel.textContent); choisir(null); dz.focus(); }
    else if (sel) msgDe(dz).textContent = "Cette case attend une étiquette de sa propre liste.";
    else if (inp(dz).value) poser(dz, "");
    else msgDe(dz).textContent = "Choisis d'abord une étiquette dans la liste, puis touche la case.";
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && sel) choisir(null); });
  parts.addEventListener("dragstart", function (e) {
    var b = e.target.closest && e.target.closest(".etq, .dz");
    if (!b || b.disabled) { e.preventDefault(); return; }
    var surCase = b.classList.contains("dz"), v = surCase ? inp(b).value : b.textContent;
    if (!v || (surCase && inp(b).disabled)) { e.preventDefault(); return; }
    choisir(null);
    drag = { v: v, from: surCase ? b : null, bk: banque(b), el: b };
    b.classList.add("is-drag");
    cases(drag.bk).forEach(function (d) { if (!d.disabled && d !== b) d.classList.add("cible"); });
    e.dataTransfer.effectAllowed = "copyMove";
    e.dataTransfer.setData("text/plain", v);
  });
  parts.addEventListener("dragend", function () {
    if (drag) drag.el.classList.remove("is-drag");
    $$(".dz.over, .dz.cible", parts).forEach(function (d) { d.classList.remove("over", "cible"); });
    drag = null;
  });
  function cible(e) {
    if (!drag) return null;
    var t = e.target.closest && e.target.closest(".dz, .bank");
    if (!t) return null;
    if (t.classList.contains("bank")) return t === drag.bk ? t : null;
    return !t.disabled && banque(t) === drag.bk ? t : null;
  }
  parts.addEventListener("dragover", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = drag.from ? "move" : "copy";
    if (t.classList.contains("dz")) t.classList.add("over");
  });
  parts.addEventListener("dragleave", function (e) {
    var t = e.target.closest && e.target.closest(".dz");
    if (t && !t.contains(e.relatedTarget)) t.classList.remove("over");
  });
  parts.addEventListener("drop", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    t.classList.remove("over");
    if (t.classList.contains("bank")) { if (drag.from) poser(drag.from, ""); return; }
    if (t === drag.from) return;
    var ancien = inp(t).value;
    poser(t, drag.v);
    if (drag.from) poser(drag.from, ancien);  /* glisser d'une case à l'autre : les deux étiquettes s'échangent */
  });
  /* une case validée (entraînement) ou corrigée (examen) est verrouillée par le moteur, sa liste aussi quand toutes
     ses cases le sont */
  new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      var t = m.target;
      if (!t.disabled || t.tagName !== "INPUT") return;
      var dz = document.getElementById("dz-" + t.id.slice(3));
      if (!dz) return;
      dz.disabled = true; dz.draggable = false; dz.classList.remove("cible");
      var bk = banque(dz);
      if (cases(bk).every(function (d) { return d.disabled; })) {
        $$(".etq", bk).forEach(function (b) { b.disabled = true; b.draggable = false; });
        if (sel && banque(sel) === bk) choisir(null);
      }
    });
  }).observe(parts, { subtree: true, attributes: true, attributeFilter: ["disabled"] });
})();
</script>"""

CONTENT_CSS = r"""<style>
/* ---------- compléments de contenu (hors gabarit) ---------- */
.eq{margin:.35rem 0 .55rem; overflow-x:auto; line-height:2.1}
.frac{display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 .12em; line-height:1.25}
.frac>span{padding:0 .25em; white-space:nowrap}
.frac>span:first-child{border-bottom:1px solid currentColor}
.doc-text ol,.doc-text ul{padding-left:1.2rem}
.doc-text li{margin:.2rem 0}
.cours-split{display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap}
.cours-split>div{flex:1 1 300px}
.cours-split>.fig{flex:0 1 auto; margin:0 auto}
.part-body .fig{margin:14px auto}
.vv{white-space:nowrap}
.vv sub{font-size:.72em}
.ins-app{padding:6px 12px; font-size:1.05rem}
.remarque{border-left:6px solid var(--jaune); background:var(--jaune-pale); padding:8px 14px; margin:12px 0; max-width:80ch}
.fig-svg svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin)}

/* ---------- cases numériques dans une équation ou un tableau (mécanisme « fast-q » du gabarit) ---------- */
.ch-corps{margin:8px 0 6px; max-width:820px}
.ch-l{margin:.3rem 0; line-height:2.5; font-size:1.02rem}
.ch-u{color:var(--encre-2); font-size:.9rem}
.grp .ch-corps .sol{display:inline-flex; align-items:center; gap:3px; vertical-align:middle; margin:0 .1em}
.ch-in{width:5.6em; border:1.5px solid var(--encre-2); padding:4px 6px; font:600 .95rem var(--f-texte); background:#fff; border-radius:2px; text-align:center}
.ch-in:focus{outline:3px solid var(--jaune); outline-offset:0}
.ch-in:disabled{background:#F2F3F1; color:var(--encre)}
.grp .ch-corps .sol .mark{flex:0 0 auto; font-size:.72rem}
.grp .ch-corps .sol .mark:empty{display:none}
.grp .ch-corps .sol.is-ok .ch-in{border-color:var(--vert); background:var(--vert-pale)}
.grp .ch-corps .sol.is-ko .ch-in{border-color:var(--rouge); background:var(--rouge-pale)}
.ch-tab{margin:6px 0; width:auto}
.ch-tab th,.ch-tab td{text-align:center; padding:4px 8px}
.ch-tab tbody th{text-align:left; font-weight:600}

/* ---------- questions à plusieurs cases (mécanisme « fast-q » du gabarit) et étiquettes ---------- */
.grp{margin:14px 0 6px; padding:10px 0 12px 14px; border-left:3px solid var(--trait-fin)}
.grp-fields{display:flex; flex-direction:column; gap:6px; margin:8px 0 4px; max-width:820px}
.grp-l{display:grid; grid-template-columns:minmax(130px,.9fr) minmax(0,1.3fr); gap:4px 14px; align-items:center; padding:2px 0; border-bottom:1px dashed var(--trait-fin)}
.grp-lab{font-size:.95rem}
.grp .sol{display:flex; align-items:center; gap:8px}
.bank{display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:8px 0 10px; padding:8px 10px; background:var(--bleu-pale); border:1px solid var(--trait-fin); max-width:820px}
.bank-t{font:700 .78rem var(--f-titre); text-transform:uppercase; letter-spacing:.04em; color:var(--encre-2); margin-right:4px}
.etq{font:600 .9rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px solid var(--bleu); border-radius:3px; padding:5px 10px; cursor:grab; touch-action:manipulation; user-select:none; text-align:left}
.etq:hover{background:#EAF1FA}
.etq:focus-visible,.dz:focus-visible{outline:3px solid var(--jaune); outline-offset:1px}
.etq[aria-pressed="true"]{background:var(--bleu); color:#fff}
.etq.is-drag{opacity:.45}
.etq:disabled{cursor:default; opacity:.5; background:#fff; color:var(--encre)}
.dz{flex:1 1 auto; min-width:0; min-height:40px; text-align:left; font:600 .95rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px dashed var(--encre-2); border-radius:3px; padding:7px 10px; cursor:pointer}
.dz .dz-v{display:block}
.dz:not(.filled) .dz-v{font-weight:400; font-style:italic; color:#7A848C}
.dz.filled{border-style:solid; border-color:var(--bleu); cursor:grab}
.dz.cible:not(:disabled),.dz.over{background:var(--jaune-pale); border-color:var(--orange)}
.dz:disabled{cursor:default; background:#F2F3F1}
.grp .sol.is-ok .dz{border:2px solid var(--vert); background:var(--vert-pale)}
.grp .sol.is-ko .dz{border:2px solid var(--rouge); background:var(--rouge-pale)}
.grp .sol .mark{flex:0 0 4.6em; font-size:.82rem; font-weight:700}
.grp .sol.is-ok .mark{color:var(--vert)} .grp .sol.is-ko .mark{color:var(--rouge)}
.grp .fast-foot .q-status{font-weight:700}
.grp-sol{max-width:780px; margin:4px 0 8px}
.grp-sol td:last-child{font-weight:600}
.mode-exam .btn-trace{display:none!important}
@media (max-width:620px){ .grp-l{grid-template-columns:minmax(0,1fr)} }

/* ---------- accueil, cours et retour (d'après le dépôt Chaîne fonctionnelle) ---------- */
a.btn{display:inline-flex; align-items:center; gap:8px; text-decoration:none}
a.btn svg,.c-top svg{width:18px; height:18px; flex:0 0 auto}
.tab-home{display:flex; align-items:center; justify-content:center; padding:8px 0 8px 4px; background:var(--encre); color:var(--jaune); text-decoration:none}
.tab-home svg{width:22px; height:22px; display:block}
.tab-home:hover{background:#2E3B47}
.c-top{margin:0 0 12px}
.c-top a{display:inline-flex; align-items:center; gap:6px; font:600 .95rem var(--f-titre); color:var(--encre); text-decoration:none; border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px 5px 10px}
.c-top a:hover{background:var(--jaune-pale)}
#home{padding:20px 20px 32px}
body.page-atelier-libre .home-inner{max-width:1500px}
.home-top{display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:14px; align-items:stretch; margin:0 0 14px}
.home-top-single{grid-template-columns:1fr}
.home-top-l{display:flex; flex-direction:column; gap:10px; min-width:0}
.home-top .home-head{padding:14px 20px; flex:1}
.home-top .home-head h1{margin:6px 0 6px; font-size:clamp(1.4rem,2.4vw,1.85rem)}
.home-top .home-sub{font-size:.95rem}
.home-top .home-hero{margin:0; padding:8px; display:flex; flex-direction:column; justify-content:center; min-width:0}
.home-top .home-hero img{width:auto!important; max-width:100%; max-height:160px; margin:0 auto}
body.hub .home-top .home-hero img{max-height:210px}
.home-top .home-hero figcaption{font-size:.78rem; line-height:1.3; margin-top:4px}
.home-top .home-facts{grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin:0}
.home-top .home-facts div{padding:6px 10px}
.home-top .home-facts b{font-size:1.02rem}
.home-top .home-facts span{font-size:.76rem; line-height:1.3; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
@media (max-width:980px){ .home-top .home-facts{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:820px){ .home-top{grid-template-columns:1fr} }
#home .home-choose{margin:18px 0 8px; font-size:1.25rem}
#home .mode-card{padding:12px 18px 14px}
#home .mode-card .mc-lead{margin:2px 0 4px; font-size:.92rem}
#home .mode-card ul{margin:0 0 10px; font-size:.9rem; line-height:1.45}
#home .mode-card li{margin:.15rem 0}
#home .mode-card .btn{padding:9px 16px}
#home .home-note{margin:10px 0 0}
.home-back{margin:12px 0 0}
.ex-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:16px}
.ex-grid .mode-card p{margin:4px 0 8px; font-size:.95rem}
.ex-grid .mode-card .ex-meta{margin:0 0 12px; font-size:.85rem}
.ex-grid .mode-card h3{font-size:1.2rem}
.ex-grid .mc-head{flex-direction:column; align-items:flex-start; gap:6px}
.ex-grid .mode-card .btn{margin-top:auto; align-self:flex-start}
.ex-grid .en-edition{border-style:dashed; border-color:var(--trait)}
.ex-grid .en-edition h3,.ex-grid .en-edition p{color:var(--encre-2)}
.ex-grid .etat{font-weight:700; color:var(--orange)}
body.hub .ex-grid{grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); grid-auto-rows:1fr}
.carte-v{display:grid; grid-template-rows:auto auto 62px 46px; gap:8px; padding:0 0 16px!important; overflow:hidden; height:100%}
body.hub .carte-v>*:not(.cv-img){margin-left:18px; margin-right:18px}
.carte-v .cv-img{display:block; width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; background:#fff; border-bottom:2px solid var(--encre); margin:0}
.carte-v .cv-vide{background:repeating-linear-gradient(135deg,#F4F5F2 0 12px,#ECEEEA 12px 24px)}
.carte-v .mc-head{margin:6px 18px 0}
.carte-v h3{margin:0; min-height:2.4em; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; line-height:1.2}
#home .carte-v .cv-mots{display:flex; flex-wrap:wrap; align-content:flex-start; gap:5px; list-style:none; margin:0 18px; padding:0}
#home .carte-v .cv-mots li{margin:0}
body.hub .carte-v .btn,body.hub .carte-v .etat{align-self:end; justify-self:start; margin-top:0; margin-bottom:0}
.cv-mots li{font:600 .8rem var(--f-titre); background:var(--bleu-pale); color:var(--encre); border:1px solid #C9D8EC; padding:2px 8px; border-radius:12px; white-space:nowrap}
.en-edition .cv-img{filter:grayscale(1) opacity(.55)}
.en-edition .cv-mots li{background:#F4F5F2; border-color:var(--trait-fin); color:var(--encre-2)}
.pastille{display:inline-block; font:700 .72rem var(--f-titre); letter-spacing:.03em; background:var(--vert); color:#fff; padding:2px 8px; margin-left:6px; vertical-align:middle}
.pastille.n2{background:var(--bleu)}
.mc-tag .pastille{margin-left:8px; font-size:.68rem; padding:1px 6px}

__COURS_CSS__
@media print{
  .c-top,.home-back{display:none!important}
  /* correctif repris du dépôt RDM : « .sketch .q-expl[hidden] » imprimerait la correction avant la remise */
  body:not(.corrections-open) .sketch .q-expl[hidden]{display:none!important}
  .eq{overflow:visible; line-height:1.7}
  .grp-l{break-inside:avoid}
  .bank{background:none; padding:4px 0; border:0} .etq{border-width:1px; padding:1px 6px; font-size:8.5pt}
  .dz{min-height:0; padding:3px 8px} .dz:not(.filled) .dz-v{visibility:hidden}
  .ins-app{display:none}
}
</style>"""

# ============================================================ assemblage
DECOR_JS = """  var DECOR = {
    // aucun tracé « à main levée » : les constructions se font dans l'atelier (src/atelier/atelier.js)
  };
"""
DR_NAMES_JS = """  var DR_NAMES = {
    // aucun tracé « à main levée »
  };
"""
DATA_RE = re.compile(r"data:image/(?:png|jpeg);base64,[A-Za-z0-9+/=]+")

AIDES_COURS = types.SimpleNamespace(HOUSE=HOUSE, figure=figure, esc=esc, fr=fr, atelier=atelier, ATELIERS=ATELIERS)


def build():
    g_ = GABARIT.read_text(encoding="utf-8")
    s0 = g_.index("<style>:root{")
    style = g_[s0:g_.index("</style>", s0) + len("</style>")]
    grading = re.search(r"<script>/\*GRADING-START\*/.*?</script>", g_, re.S).group(0)
    app_start = g_.index("<script>(function () {")
    app = g_[app_start:g_.rindex("</script>") + len("</script>")]

    # entrées du moteur réservées au sujet ; la durée conseillée dépend de l'activité ouverte
    app = sub_once(app, r"var CONSEIL_MIN = \d+;", "var CONSEIL_MIN = window.__CONSEIL_MIN__ || 0;")
    app = sub_once(app, r"  var DECOR = \{\n.*?\n  \};\n", DECOR_JS, re.S)
    app = sub_once(app, r"  var DR_NAMES = \{\n.*?\n  \};\n", DR_NAMES_JS, re.S)
    app = sub_once(app, r"Quatre pages, une par document", "Une page par document réponse")
    app = sub_once(app, r'btn\.textContent = "Diagramme validé";', 'btn.textContent = "Réponses validées";')
    app = sub_once(app, r'ok \+ " case" \+ \(ok > 1 \? "s" : ""\) \+ " juste" \+ \(ok > 1 \? "s" : ""\) \+ " sur " \+ inputs\.length',
                   'ok + " réponse" + (ok > 1 ? "s" : "") + " juste" + (ok > 1 ? "s" : "") + " sur " + inputs.length')

    exos = [f() for f in activites_analytiques.ACTIVITES + activites.ACTIVITES]
    templates, exos_cfg = [], {}
    for e in exos:
        prepare_exo(e)
    for e in exos:
        CUR["total"] = e["minutes"]
        parts_html = "".join(render_part(e, p) for p in e["P"])
        rail, tabs, secs, docs = render_docs(e)
        k = e["key"]
        templates += [f'<template id="tpl-rail-{k}">{rail}</template>',
                      f'<template id="tpl-tabs-{k}">{tabs}</template>',
                      f'<template id="tpl-docs-{k}">{secs}</template>',
                      f'<template id="tpl-home-{k}">{render_exo_home(e, docs)}</template>',
                      f'<template id="tpl-parts-{k}">{parts_html}\n</template>']
        exos_cfg[k] = e["cfg"]
    templates.append(f'<template id="tpl-consignes">{CONSIGNES}</template>')
    templates.append(f'<template id="tpl-consignes-ana">{CONSIGNES_ANA}</template>')
    templates.append(f'<template id="tpl-modes">{MODES_HTML}</template>')
    templates.append(f'<template id="tpl-hub">{render_hub(exos)}</template>')
    templates.append(f'<template id="tpl-cours-cinematique-analytique">{cours_analytique.render(AIDES_COURS)}</template>')
    templates.append(f'<template id="tpl-cours-cinematique-graphique">{cours_graphique.render(AIDES_COURS)}</template>')
    templates.append(f'<template id="tpl-atelier-libre">{render_atelier_libre()}</template>')

    cours_js = (cours_commun.JS + cours_analytique.JS + cours_mouvements.JS + cours_graphique.JS +
                '\n  var INIT = { "cours-cinematique-analytique": initCoursAnalytique, '
                '"cours-cinematique-graphique": initCoursGraphique };\n')
    config = (f"<script>window.__EXOS__ = {json.dumps(exos_cfg, ensure_ascii=False)};</script>\n"
              f"<script>window.__ATELIERS__ = {json.dumps(ATELIERS, ensure_ascii=False, separators=(',', ':'))};</script>")
    router = (ROUTER_JS.replace("__COURS_JS__", cours_js).replace("__TITRE__", TITRE)
              .replace("__HOUSE__", HOUSE.replace("'", "\\'")))
    css = CONTENT_CSS.replace("__COURS_CSS__", cours_commun.CSS + cours_analytique.CSS + cours_mouvements.CSS +
                              cours_graphique.CSS)

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITRE} — cours et activités interactifs</title>
<meta name="description" content="Cinématique : cours interactifs (cinématique analytique, cinématique graphique), atelier de construction, activités de cinématique analytique (MRU, MRUV, mouvement circulaire) et de résolution graphique (équiprojectivité, centre instantané de rotation, composition des vitesses).">
{style}
{css}
<style>{atelier.CSS}</style>
<style id="at-css-fig">{atelier.CSS_FIG}</style>
</head>
<body class="no-mode">

<nav class="rail" aria-label="Dossiers de présentation et dossier technique"></nav>

<aside id="docpanel" aria-label="Documents de l'activité" aria-hidden="true">
  <div class="dp-head">
    <h3 id="dp-title">Documents</h3>
    <button type="button" id="dp-out" aria-label="Réduire">−</button><span id="dp-zoom" class="small">100 %</span>
    <button type="button" id="dp-in" aria-label="Agrandir">+</button>
    <button type="button" id="dp-fit">Ajuster</button>
    <button type="button" id="dp-close">Fermer</button>
  </div>
  <div class="dp-tabs" role="tablist" aria-label="Choisir un document"></div>
  <div class="dp-body"></div>
</aside>

<section id="home" aria-labelledby="home-title"><div class="home-inner"></div></section>

<main class="page">
  <section class="print-only print-summary">
    <p>Élève : <span class="print-nom"></span> | Copie imprimée le <span class="print-date"></span></p>
    <p>Mode : <span class="print-mode"></span> | Temps de rédaction : <strong class="print-time"></strong> (durée conseillée : <span class="print-conseil"></span>)</p>
    <p class="print-note-line">Note finale pondérée : <strong class="final-note"></strong></p>
    <p class="print-nograde">Copie non corrigée : les corrections et la note n'apparaissent qu'après la remise de la copie en mode examen.</p>
  </section>

  <nav class="c-top" aria-label="Navigation"><a href="?">{HOUSE} Accueil</a></nav>

  <header class="cartouche">
    <div class="title">
      <h1>{TITRE}</h1>
      <p></p></div>
    <div class="nom"><label for="nom-eleve">Nom et prénom</label><input id="nom-eleve" type="text" autocomplete="name"></div>
  </header>

  <div class="consignes"></div>

  <div id="parts"></div>

  <section class="recap" id="recap" aria-labelledby="t-recap">
    <header class="recap-head"><h2 id="t-recap">Récapitulatif et note finale</h2>
      <p class="small">Les réponses non validées comptent comme fausses. Chaque partie est ramenée sur 20, puis pondérée par sa durée conseillée.</p></header>
    <div id="exam-submit-wrap">
      <p class="es-lead">Ta copie n'est pas encore corrigée : aucune réponse n'est verrouillée, tu peux encore revenir sur les questions et les tracés.</p>
      <button type="button" class="btn btn-exam" id="exam-submit">J'ai fini, je fais corriger ma copie</button>
      <p class="es-warn" id="exam-warn" role="alert"></p>
    </div>
    <div id="recap-graded">
      <div class="recap-wrap">
        <table class="t recap-table">
          <thead><tr><th>Partie</th><th>Durée</th><th>Poids</th><th>Points</th><th>Note /20</th><th>Contribution</th></tr></thead>
          <tbody id="recap-body"></tbody>
          <tfoot><tr><th colspan="4">Note globale pondérée</th><th class="final-note"></th><th></th></tr></tfoot>
        </table>
      </div>
      <p class="final-detail small"></p>
    </div>
    <div class="recap-foot" id="recap-foot"><button type="button" class="btn btn-print">Imprimer ma copie</button>
      <span class="small no-print">L'impression reprend tes réponses, tes tracés, les corrections et ce récapitulatif.</span>
      <a class="btn ghost no-print" href="?">{HOUSE} Retour à l'accueil</a></div>
  </section>
</main>

<footer class="banner" aria-label="Suivi de la composition">
  <div class="score-block"><div class="lab">Note provisoire</div><div class="score" id="score-val">–<small>/20</small></div></div>
  <div class="exam-block"><div class="lab">Mode examen</div><div class="exam-state">Note masquée</div></div>
  <div class="timer-block"><div class="lab">Temps</div><div class="timer" id="timer-val">0:00:00</div></div>
  <div class="count" id="score-count" aria-live="polite"></div>
  <div class="spacer"></div>
  <button type="button" class="btn-docs" id="btn-docs">Documents</button>
</footer>

{chr(10).join(templates)}

{config}
{router}
{grading}
{app}
{ETIQUETTES_JS}
{INSERT_JS}
<script>{atelier.JS}</script>
</body>
</html>
"""
    SORTIE.write_text(page, encoding="utf-8")
    imgs = sum(len(m) for m in DATA_RE.findall(page))
    print(f"{SORTIE.name} : {len(page.encode('utf-8')) / 1024:.0f} Kio, dont images {imgs / 1024:.0f} Kio (base64)")
    for e in exos:
        print(f"  ?ex={e['key']} : {e['tag']}, {len(e['P'])} partie(s), {e['n_q']} questions, {e['points']} points "
              f"({e['n_trace']} tracés), {hm(e['minutes'])}")
    for c in COURS:
        print(f"  ?ex={c['key']} : {c['tag']} — {c['title']}")
    print(f"  ?ex={ATELIER_LIBRE['key']} : atelier de construction libre")


if __name__ == "__main__":
    build()
