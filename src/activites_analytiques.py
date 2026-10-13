# -*- coding: utf-8 -*-
"""Les activités de cinématique analytique : une étude de système de la séquence « Cinématique analytique » = une
activité (imprimante 3D, vanne d'admission d'air, automotrice à grande vitesse, moteur électrique).

Les questions sont celles de src/activites.py (Q, ETQ, TRACE), plus CHAMPS : des cases numériques insérées dans un
texte (coefficients d'une équation horaire, tableau de valeurs). Les graphes à compléter sont des feuilles de l'atelier
portant des axes gradués (src/atelier.py, Feuille.graphe) ; une portion de courbe attendue est un item « courbe »,
juste lorsque le tracé de l'élève la suit à 2 mm près sur la feuille.
"""
import html
import math
import types

from activites import ETQ, NUM, Q, TRACE, donnees
from atelier import C_COURBE, C_SG, IT_COURBE, Feuille

PI = math.pi


def esc(s):
    return html.escape(s, quote=True)


# ====================================================================== écriture
def VEC(nom, pt, sol):
    """Vecteur cinématique écrit comme dans la séquence : V(B∈1/0), Γ(B∈1/0)."""
    return f'<span class="vv"><span class="vec">{nom}</span><sub>{pt}∈{sol}</sub></span>'


def i_(s):
    return f"<i>{s}</i>"


def nb(x, d=3):
    """Nombre écrit à la française, sans zéros inutiles : 0,781 ; −81,92 ; 50."""
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s.replace("-", "−") if s not in ("-0",) else "0"


def fig_svg(F, alt, legende, maxw):
    """Figure dessinée avec les primitives d'une feuille (graphe d'un énoncé), intégrée en SVG."""
    return (f'<figure class="fig fig-svg" style="max-width:{maxw}px"><svg viewBox="0 0 {F.w} {F.h}" role="img" '
            f'aria-label="{esc(alt)}" xmlns="http://www.w3.org/2000/svg">{F.svg_fig()}</svg>'
            + (f"<figcaption>{legende}</figcaption>" if legende else "") + "</figure>")


def feuille(F):
    """Une partie dont la feuille ne représente pas un mécanisme : l'objet attendu par le générateur (attribut F)."""
    return types.SimpleNamespace(F=F)


# ====================================================================== questions à cases numériques
HC = "Saisis des nombres (virgule ou point décimal) ; écris 0 pour un terme absent. Les cases se valident ensemble."


def C(lab, valeur, attendu=None, tol=0.005, rel=0.01):
    """Une case : libellé (correction), valeur attendue, texte de la réponse attendue, tolérances."""
    return (lab, valeur, attendu if attendu is not None else nb(valeur), tol, rel)


def CHAMPS(num, stem, gabarit, champs, why, hint=HC):
    """Cases numériques insérées dans le modèle HTML gabarit, aux repères [[1]], [[2]]… ; chaque case vaut un point
    (valeur sans unité : l'unité est écrite à côté de la case)."""
    fields = [(lab, {"type": "num", "value": round(v, 6), "relTol": rel, "absTol": tol}, att)
              for lab, v, att, tol, rel in champs]
    return {"kind": "champs", "num": num, "stem": stem, "hint": hint, "gabarit": gabarit, "fields": fields,
            "why": why}


def ligne(*morceaux, unite=""):
    return '<p class="ch-l">' + " ".join(morceaux) + (f' <span class="ch-u">{unite}</span>' if unite else "") + "</p>"


def tableau(entetes, lignes):
    """Tableau de valeurs : entetes = [« t (s) », 0, 1, 2] ; lignes = [(« x (mm) », [[1]], [[2]]…)]."""
    th = "".join(f"<th>{h}</th>" for h in entetes)
    tr = "".join("<tr><th>" + l[0] + "</th>" + "".join(f"<td>{c}</td>" for c in l[1:]) + "</tr>" for l in lignes)
    return f'<table class="t ch-tab"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


H_NUM = "Saisis la valeur et son unité (ex. 12,5 mm/s)."
H_GR = ("Outil <em>Segment</em> pour une portion droite, <em>Courbe</em> pour un arc de parabole (pose ses points, puis "
        "touche à nouveau le dernier) ; «&nbsp;Placer un point&nbsp;» pose un point par ses coordonnées. Une portion "
        "confondue avec l'axe des temps se trace aussi.")

NAT_R = ["Rectiligne uniforme (MRU)", "Rectiligne uniformément accéléré (MRUV)",
         "Rectiligne uniformément décéléré (MRUV)", "Immobilité (arrêt)"]
NAT_C = ["Circulaire uniforme (MCU)", "Circulaire uniformément accéléré (MCUV)",
         "Circulaire uniformément décéléré (MCUV)", "Immobilité (arrêt)"]


def cor_courbes(items, aides=()):
    return [C_COURBE(it) for it in items] + list(aides)


# ====================================================================== 1.1 — IMPRIMANTE 3D
def imprimante():
    T1, D2 = 2.0, 25.0
    V1 = 32 * T1                      # 64 mm/s en fin de phase 1
    X1 = 16 * T1 ** 2 + 50            # 114 mm
    T2 = 2 * D2 / V1                  # durée du ralentissement uniforme : 0,781 25 s
    A2 = -V1 / T2                     # −81,92 mm/s²
    X2 = X1 + D2                      # 139 mm
    TF2, TF3 = T1 + T2, T1 + T2 + 0.5  # 2,781 s et 3,281 s

    def x(t):
        if t <= T1:
            return 16 * t * t + 50
        if t <= TF2:
            u = t - T1
            return A2 / 2 * u * u + V1 * u + X1
        return X2

    def v(t):
        return 32 * t if t <= T1 else (A2 * (t - T1) + V1 if t <= TF2 else 0.0)

    F = Feuille(180, 262, "Graphes du mouvement du chariot (1)")
    GX = F.graphe("x(t)", (22, 89), 40, 0.5, 3.5, 0, 150, (0.1, 0.5, 0.5), (10, 50, 50), "t", "x", "s", "mm",
                  up="mm/s", dx=2, dy=1, titre="Graphe des espaces")
    GV = F.graphe("v(t)", (22, 163), 40, 0.8, 3.5, -10, 70, (0.1, 0.5, 0.5), (5, 10, 10), "t", "v", "s", "mm/s",
                  up="mm/s²", dx=2, dy=1, titre="Graphe des vitesses")
    GA = F.graphe("γ(t)", (22, 209), 40, 0.5, 3.5, -90, 40, (0.1, 0.5, 0.5), (10, 20, 20), "t", "γ", "s", "mm/s²",
                  dx=2, dy=1, titre="Graphe des accélérations")

    def trois(t0, t1, lab, ga):
        return [IT_COURBE(GX, x, t0, t1, f"Graphe des espaces, {lab}"),
                IT_COURBE(GV, v, t0, t1, f"Graphe des vitesses, {lab}"),
                IT_COURBE(GA, lambda t: ga, t0, t1, f"Graphe des accélérations, {lab}")]

    it1 = trois(0, T1, "phase 1 (0 ≤ t ≤ 2 s)", 32)
    it2 = trois(T1, TF2, f"phase 2 (2 ≤ t ≤ {nb(TF2, 2)} s)", A2)
    it3 = trois(TF2, TF3, f"phase 3 ({nb(TF2, 2)} ≤ t ≤ {nb(TF3, 2)} s)", 0)

    VB, GB = VEC("V", "B", "1/0"), VEC("Γ", "B", "1/0")
    x_ = '<span class="vec">x</span>'
    blocks = [
        CHAMPS("Q1", "Détermine la position de B aux instants t = 0, t = 1 s et t = 2 s.",
               tableau(["t (s)", "0", "1", "2"], [("x (mm)", "[[1]]", "[[2]]", "[[3]]")]),
               [C("x(0) (mm)", 50, "50 mm"), C("x(1) (mm)", 66, "66 mm"), C("x(2) (mm)", 114, "114 mm")],
               "<p>On remplace t dans l'équation horaire x = 16 t² + 50 : x(0) = 50 mm ; x(1) = 16 × 1 + 50 = 66 mm ; "
               "x(2) = 16 × 4 + 50 = <strong>114 mm</strong>.</p>"),
        CHAMPS("Q2", f"Détermine les composantes du vecteur vitesse {VB} et sa norme aux mêmes instants.",
               "<p class=\"ch-l\">" + f"{VB} = (d<i>x</i>/d<i>t</i>) · {x_}, le mouvement étant une translation "
               f"rectiligne d'axe (A, {x_}).</p>"
               + tableau(["t (s)", "0", "1", "2"], [(f"Composante sur {x_} (mm/s)", "[[1]]", "[[2]]", "[[3]]"),
                                                   (f"‖{VB}‖ (mm/s)", "[[4]]", "[[5]]", "[[6]]")]),
               [C("Composante à t = 0", 0, "0"), C("Composante à t = 1 s", 32, "32"), C("Composante à t = 2 s", 64, "64"),
                C("Norme à t = 0", 0, "0 mm/s"), C("Norme à t = 1 s", 32, "32 mm/s"), C("Norme à t = 2 s", 64, "64 mm/s")],
               f"<p>La vitesse est la dérivée de la position : v = dx/dt = 2 × 16 t = <strong>32 t</strong> (mm/s). Le "
               f"vecteur vitesse est porté par {x_} : ses composantes sont (32 t ; 0 ; 0), soit 0, 32 et 64 mm/s aux "
               "trois instants ; la composante étant positive, la norme lui est égale.</p>"),
        CHAMPS("Q3", f"Détermine les composantes du vecteur accélération {GB} et sa norme aux mêmes instants.",
               ligne(f"{GB} =", "[[1]]", f"· {x_}", unite="(mm/s², à t = 0, 1 s et 2 s)")
               + ligne(f"‖{GB}‖ =", "[[2]]", unite="mm/s²"),
               [C("Composante sur x (mm/s²)", 32, "32"), C("Norme (mm/s²)", 32, "32 mm/s²")],
               "<p>L'accélération est la dérivée de la vitesse : γ = dv/dt = <strong>32 mm/s²</strong>, la même aux "
               "trois instants : l'accélération est constante.</p>"),
        CHAMPS("Q4 a)", "Écris les équations horaire, de vitesse et d'accélération de la phase 1.",
               ligne("<i>x</i>(<i>t</i>) =", "[[1]]", "· <i>t</i>² +", "[[2]]", "· <i>t</i> +", "[[3]]", unite="(mm)")
               + ligne("<i>v</i>(<i>t</i>) =", "[[4]]", "· <i>t</i> +", "[[5]]", unite="(mm/s)")
               + ligne("γ(<i>t</i>) =", "[[6]]", unite="(mm/s²)"),
               [C("x : coefficient de t²", 16), C("x : coefficient de t", 0), C("x : terme constant", 50),
                C("v : coefficient de t", 32), C("v : terme constant", 0), C("γ", 32)],
               "<p>x(t) = 16 t² + 50 ; v(t) = 32 t ; γ(t) = 32 mm/s². C'est un mouvement rectiligne uniformément "
               "accéléré : x = ½ γ t² + v<sub>0</sub> t + x<sub>0</sub>, avec γ = 32 mm/s², v<sub>0</sub> = 0 et "
               "x<sub>0</sub> = 50 mm.</p>"),
        TRACE("Q4 b)", "Complète les trois graphes pour la phase 1 (0 ≤ t ≤ 2 s).", H_GR, it1,
              cor_courbes(it1),
              "<p>Graphe des espaces : un arc de parabole de (0 ; 50) à (2 ; 114), tangent à l'horizontale en t = 0 "
              "(la vitesse y est nulle). Graphe des vitesses : une droite de (0 ; 0) à (2 ; 64), de pente γ = 32 mm/s². "
              "Graphe des accélérations : un segment horizontal à 32 mm/s².</p>"),
        Q("Q5 a)", "Détermine la durée de la phase 2.",
          "Le ralentissement est uniforme (MRUV) : la vitesse passe de 64 mm/s à zéro sur 25 mm. " + H_NUM,
          NUM(T2, "s", 0.01), f"Δt<sub>2</sub> = {nb(T2, 3)} s",
          f"<p>Pendant un MRUV, la distance parcourue est le produit de la vitesse moyenne par la durée : "
          f"d = (v<sub>début</sub> + v<sub>fin</sub>) / 2 × Δt, soit 25 = (64 + 0) / 2 × Δt, d'où "
          f"Δt = 2 × 25 / 64 = <strong>{nb(T2, 3)} s</strong> (0,781 25 s). La phase 2 se termine à "
          f"t = 2 + {nb(T2, 3)} = {nb(TF2, 3)} s.</p>"),
        Q("Q5 b)", "Détermine l'accélération γ<sub>2</sub> pendant la phase 2 (valeur algébrique).", H_NUM,
          NUM(A2, "mm/s2", 0.01), f"γ<sub>2</sub> = {nb(A2, 2)} mm/s²",
          f"<p>γ<sub>2</sub> = Δv / Δt = (0 − 64) / {nb(T2, 5)} = <strong>{nb(A2, 2)} mm/s²</strong> : négative, "
          "de signe contraire à la vitesse, c'est une décélération.</p>"),
        CHAMPS("Q6 a)", "Écris les équations de la phase 2, en plaçant l'origine des temps au début de la phase "
                        "(t' = t − 2).",
               ligne("<i>x</i>(<i>t'</i>) =", "[[1]]", "· <i>t'</i>² +", "[[2]]", "· <i>t'</i> +", "[[3]]", unite="(mm)")
               + ligne("<i>v</i>(<i>t'</i>) =", "[[4]]", "· <i>t'</i> +", "[[5]]", unite="(mm/s)")
               + ligne("γ(<i>t'</i>) =", "[[6]]", unite="(mm/s²)")
               + ligne("Fin de la phase : <i>t</i> =", "[[7]]", "s, en <i>x</i> =", "[[8]]", unite="mm"),
               [C("x : coefficient de t'²", A2 / 2), C("x : coefficient de t'", V1), C("x : terme constant", X1),
                C("v : coefficient de t'", A2), C("v : terme constant", V1), C("γ", A2),
                C("Instant de fin de phase (s)", TF2, nb(TF2, 3), rel=0.004), C("Position de fin de phase (mm)", X2)],
               f"<p>Au début de la phase 2 : x<sub>0</sub> = 114 mm et v<sub>0</sub> = 64 mm/s ; γ = {nb(A2, 2)} mm/s². "
               f"D'où x(t') = {nb(A2 / 2, 2)} t'² + 64 t' + 114 ; v(t') = {nb(A2, 2)} t' + 64 ; γ = {nb(A2, 2)} mm/s². "
               f"La phase se termine à t' = {nb(T2, 5)} s, soit t = {nb(TF2, 3)} s, en x = 114 + 25 = "
               "<strong>139 mm</strong> (la vitesse y est nulle).</p>"),
        TRACE("Q6 b)", "Complète les trois graphes pour la phase 2.", H_GR, it2,
              cor_courbes(it2, [C_SG(GX.p(TF2, 150), GA.p(TF2, -90), "aide")]),
              "<p>Graphe des espaces : un arc de parabole de (2 ; 114) à (2,78 ; 139), qui arrive à l'horizontale "
              "(vitesse nulle en fin de phase) et prolonge sans cassure l'arc de la phase 1 (même tangente en t = 2 s, "
              "la vitesse étant continue). Graphe des vitesses : une droite de (2 ; 64) à (2,78 ; 0). Graphe des "
              f"accélérations : un segment horizontal à {nb(A2, 2)} mm/s² ; l'accélération change brutalement en "
              "t = 2 s.</p>"),
        CHAMPS("Q7 a)", "Écris les équations de la phase 3 (immobilité pendant 0,5 s).",
               ligne("<i>x</i> =", "[[1]]", unite="(mm)") + ligne("<i>v</i> =", "[[2]]", unite="(mm/s)")
               + ligne("γ =", "[[3]]", unite="(mm/s²)")
               + ligne("Fin de la phase : <i>t</i> =", "[[4]]", unite="s"),
               [C("x (mm)", X2), C("v (mm/s)", 0), C("γ (mm/s²)", 0), C("Instant de fin (s)", TF3, nb(TF3, 3), rel=0.004)],
               f"<p>Le chariot reste en x = 139 mm : v = 0 et γ = 0. La phase dure 0,5 s et se termine à "
               f"t = {nb(TF2, 3)} + 0,5 = <strong>{nb(TF3, 3)} s</strong>.</p>"),
        TRACE("Q7 b)", "Complète les trois graphes pour la phase 3.", H_GR, it3,
              cor_courbes(it3, [C_SG(GX.p(TF3, 150), GA.p(TF3, -90), "aide")]),
              "<p>Trois segments horizontaux, de t = 2,78 s à t = 3,28 s : x = 139 mm, et v = 0, γ = 0 (confondus "
              "avec l'axe des temps).</p>"),
        ETQ("Q7 c)", "Quelle est la nature du mouvement du chariot pendant chaque phase ?",
            [("Phase 1", NAT_R[1]), ("Phase 2", NAT_R[2]), ("Phase 3", NAT_R[3])], NAT_R,
            "<p>Phase 1 : γ constante, de même signe que la vitesse : mouvement rectiligne uniformément accéléré. "
            "Phase 2 : γ constante, de signe contraire à la vitesse : uniformément décéléré. Phase 3 : le chariot "
            "est immobile.</p>", titre="Natures"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>Le schéma représente l'axe x d'une imprimante 3D (l'axe y, identique, est placé en dessous). Le chariot "
        "(1), qui porte la buse déposant l'ABS fondu, est déplacé en translation par le moteur M<sub>1</sub>, par "
        "l'intermédiaire de la liaison hélicoïdale de centre C. Le guidage est assuré par deux pivots glissants "
        "parallèles (A et B).</p>"
        "<p>Le mouvement du chariot (1) par rapport au bâti (0) se fait en trois phases : mise en vitesse, "
        "ralentissement à l'approche de la position visée, puis arrêt pendant le dépôt de matière.</p>"
        + donnees("Phase 1, pour 0 ≤ t ≤ 2 s : x = 16 t² + 50 (x position de B en mm, t en s)",
                  "Phase 2 : afin que la buse arrive précisément aux coordonnées voulues, l'axe x ralentit "
                  "uniformément sur les 25 derniers millimètres, jusqu'à l'arrêt",
                  "Phase 3 : la machine reste immobile durant 0,5 s afin de déposer l'ABS fondu",
                  "Les graphes de la feuille ont une même origine des temps : t = 0 au début de la phase 1")
        + "</div>__FIG:photo-imprimante|Schéma de l'axe x d'une imprimante 3D : chariot 1, moteur M1, pivots glissants A et B, "
          "liaison hélicoïdale C|Axe x de l'imprimante : chariot (1) et bâti (0).|420__</div>"]
    return {"key": "imprimante-3d", "prefix": "h", "partie": "analytique", "tag": "Activité 1.1", "title": "Imprimante 3D",
            "mots": ["MRUV", "Équation horaire", "Graphes x, v, γ", "Décélération"], "methode": "MRUV",
            "sub": "Le chariot porte-buse accélère, ralentit puis s'arrête : écrire les équations de chaque phase et "
                   "compléter les graphes des espaces, des vitesses et des accélérations.",
            "hero": ("photo-imprimante", "Schéma de l'axe x d'une imprimante 3D", "Axe x d'une imprimante 3D."),
            "dt": "ana",
            "parts": [{"title": "Mouvement du chariot porte-buse", "minutes": 50, "intro": intro, "meca": feuille(F),
                       "noms": [], "blocks": blocks}]}


# ====================================================================== 1.2 — VANNE D'ADMISSION D'AIR
def fig_vanne():
    """Loi de vitesse du boisseau (allure, comme dans la séquence)."""
    F = Feuille(132, 80, "Loi de vitesse du boisseau")
    o = (16, 56)
    tx = {0: 16, 0.25: 32, "t2": 66, "t2+0,2": 80, "t2+0,7": 104, "t2+0,8": 110}
    yV, y1 = 20, 44.5
    pts = [o, (tx[0.25], yV), (tx["t2"], yV), (tx["t2+0,2"], y1), (tx["t2+0,7"], y1), (tx["t2+0,8"], o[1])]
    F.fleche(o, (126, o[1]), "fl", 2.4)
    F.fleche((o[0], o[1] + 2), (o[0], 8), "fl", 2.4)
    for q in pts[1:5]:
        F.trait((q[0], o[1]), q, "tire")
    F.trait((o[0], yV), (tx["t2"], yV), "tire")
    F.trait((o[0], y1), (tx["t2+0,7"], y1), "tire")
    F.poly(pts, "crb")
    F.texte((o[0] - 2, yV), "V<tspan font-size=\"70%\" dy=\"1\">max</tspan>", "lab", 3.4, "end")
    F.texte((o[0] - 2, y1), "1 mm/s", "note", 3.2, "end")
    F.texte((o[0] - 2.5, o[1] + 3), "0", "note", 3.2, "end")
    F.texte((o[0] + 3, 6.5), "V (mm/s)", "lab", 3.4, "start")
    F.texte((126, o[1] - 3.5), "t (s)", "lab", 3.4, "end")
    for lab, x in [("0,25", tx[0.25]), ("t<tspan font-size=\"70%\" dy=\"1\">2</tspan>", tx["t2"]),
                   ("t<tspan font-size=\"70%\" dy=\"1\">2</tspan><tspan dy=\"-1\">+0,2</tspan>", tx["t2+0,2"]),
                   ("t<tspan font-size=\"70%\" dy=\"1\">2</tspan><tspan dy=\"-1\">+0,7</tspan>", tx["t2+0,7"]),
                   ("t<tspan font-size=\"70%\" dy=\"1\">2</tspan><tspan dy=\"-1\">+0,8</tspan>", tx["t2+0,8"])]:
        F.texte((x + 1.1, o[1] + 2.5), lab, "note", 3.1, "end", rot=-90)
    for n, p in [(1, (20.5, 33)), (2, (49, 15.5)), (3, (77.5, 29)), (4, (92, 40)), (5, (112, 47))]:
        F.numero(p, n, r=2.4)
    return F


def vanne():
    N, PAS = 375, 0.5
    VM = N / 60 * PAS                       # 3,125 mm/s
    A1, D1 = VM / 0.25, VM * 0.25 / 2       # 12,5 mm/s² ; 0,390 6 mm
    A3, D3 = (1 - VM) / 0.2, (VM + 1) / 2 * 0.2   # −10,625 mm/s² ; 0,412 5 mm
    D4 = 1 * 0.5                            # 0,5 mm
    A5, D5 = -1 / 0.1, 1 / 2 * 0.1          # −10 mm/s² ; 0,05 mm
    D2 = 3 - (D1 + D3 + D4 + D5)            # 1,646 9 mm
    T2D = D2 / VM                           # 0,527 s
    T2 = 0.25 + T2D                         # 0,777 s
    TT = T2 + 0.8                           # 1,577 s
    nat = lambda num, phase, bonne, why: ETQ(num, f"Quelle est la nature du mouvement du boisseau pendant la phase {phase} ?",  # noqa: E731
                                             [(f"Phase {phase}", bonne)], NAT_R, why, titre="Natures")
    p1 = [
        Q("Q1 a)", "Calcule la fréquence de rotation maximale du moteur, en tours par seconde.", H_NUM,
          NUM(N / 60, "tr/s", 0.01), f"N = {nb(N / 60, 2)} tr/s",
          f"<p>N = 375 tr/min = 375 / 60 = <strong>{nb(N / 60, 2)} tr/s</strong>.</p>"),
        Q("Q1 b)", "Montre par le calcul que la vitesse maximale du boisseau est de 3,125 mm/s : calcule V<sub>max</sub>.",
          "À chaque tour du moteur, la glissière hélicoïdale fait avancer le boisseau d'un pas. " + H_NUM,
          NUM(VM, "mm/s", 0.005), "V<sub>max</sub> = 3,125 mm/s",
          f"<p>Le boisseau avance d'un pas (0,5 mm) par tour : V<sub>max</sub> = N × pas = {nb(N / 60, 2)} × 0,5 = "
          "<strong>3,125 mm/s</strong>.</p>"),
        nat("Q2 a)", 1, NAT_R[1], "<p>La vitesse croît linéairement de 0 à V<sub>max</sub> : l'accélération est "
                                  "constante et positive.</p>"),
        Q("Q2 b)", "Détermine l'accélération a<sub>1</sub> pendant la phase 1.", H_NUM, NUM(A1, "mm/s2", 0.01),
          f"a<sub>1</sub> = {nb(A1, 2)} mm/s²",
          f"<p>a<sub>1</sub> = Δv / Δt = (3,125 − 0) / 0,25 = <strong>{nb(A1, 2)} mm/s²</strong>.</p>"),
        Q("Q2 c)", "Détermine la distance parcourue pendant la phase 1.", H_NUM, NUM(D1, "mm", 0.01),
          f"d<sub>1</sub> = {nb(D1, 4)} mm",
          f"<p>d<sub>1</sub> = ½ a<sub>1</sub> t² = 0,5 × 12,5 × 0,25² = <strong>{nb(D1, 4)} mm</strong> (c'est aussi "
          "l'aire du triangle sous la courbe des vitesses : 0,25 × 3,125 / 2).</p>"),
        nat("Q3 a)", 3, NAT_R[2], "<p>La vitesse décroît linéairement de V<sub>max</sub> à 1 mm/s : l'accélération "
                                  "est constante et de signe contraire à la vitesse.</p>"),
        Q("Q3 b)", "Détermine la décélération a<sub>3</sub> pendant la phase 3.", H_NUM,
          NUM(A3, "mm/s2", 0.01, signe=False), f"a<sub>3</sub> = {nb(A3, 3)} mm/s² (décélération de {nb(-A3, 3)} mm/s²)",
          f"<p>a<sub>3</sub> = (1 − 3,125) / 0,2 = <strong>{nb(A3, 3)} mm/s²</strong>. Le signe n'est pas noté ici : "
          "une décélération se donne souvent en valeur absolue.</p>"),
        Q("Q3 c)", "Détermine la distance parcourue pendant la phase 3.", H_NUM, NUM(D3, "mm", 0.01),
          f"d<sub>3</sub> = {nb(D3, 4)} mm",
          f"<p>d<sub>3</sub> = vitesse moyenne × durée = (3,125 + 1) / 2 × 0,2 = <strong>{nb(D3, 4)} mm</strong> "
          "(aire du trapèze sous la courbe des vitesses).</p>"),
        nat("Q4 a)", 4, NAT_R[0], "<p>La vitesse reste égale à 1 mm/s pendant 0,5 s : mouvement uniforme.</p>"),
        Q("Q4 b)", "Détermine la distance parcourue pendant la phase 4.", H_NUM, NUM(D4, "mm", 0.01),
          f"d<sub>4</sub> = {nb(D4, 2)} mm", "<p>d<sub>4</sub> = v × Δt = 1 × 0,5 = <strong>0,5 mm</strong>.</p>"),
        nat("Q5 a)", 5, NAT_R[2], "<p>La vitesse décroît linéairement de 1 mm/s à zéro en 0,1 s.</p>"),
        Q("Q5 b)", "Détermine la décélération a<sub>5</sub> pendant la phase 5.", H_NUM,
          NUM(A5, "mm/s2", 0.01, signe=False), f"a<sub>5</sub> = {nb(A5, 2)} mm/s²",
          "<p>a<sub>5</sub> = (0 − 1) / 0,1 = <strong>−10 mm/s²</strong>.</p>"),
        Q("Q5 c)", "Détermine la distance parcourue pendant la phase 5.", H_NUM, NUM(D5, "mm", 0.01),
          f"d<sub>5</sub> = {nb(D5, 3)} mm", "<p>d<sub>5</sub> = 1 × 0,1 / 2 = <strong>0,05 mm</strong>.</p>"),
    ]
    p2 = [
        Q("Q6", "Quelle est la distance parcourue par le boisseau pendant la phase 2 ?",
          "La course totale de fermeture est de 3 mm. " + H_NUM, NUM(D2, "mm", 0.01), f"d<sub>2</sub> = {nb(D2, 3)} mm",
          f"<p>d<sub>2</sub> = 3 − (d<sub>1</sub> + d<sub>3</sub> + d<sub>4</sub> + d<sub>5</sub>) = 3 − ({nb(D1, 4)} + "
          f"{nb(D3, 4)} + 0,5 + 0,05) = <strong>{nb(D2, 3)} mm</strong>.</p>"),
        Q("Q7", "Quelle est la durée de la phase 2 ?", H_NUM, NUM(T2D, "s", 0.01), f"Δt<sub>2</sub> = {nb(T2D, 3)} s",
          f"<p>La phase 2 est un mouvement uniforme à V<sub>max</sub> : Δt<sub>2</sub> = d<sub>2</sub> / V<sub>max</sub> = "
          f"{nb(D2, 4)} / 3,125 = <strong>{nb(T2D, 3)} s</strong>. La phase 2 se termine donc à "
          f"t<sub>2</sub> = 0,25 + {nb(T2D, 3)} = {nb(T2, 3)} s.</p>"),
        Q("Q8", "Calcule le temps total de déplacement du boisseau sur l'ensemble des 3 mm.", H_NUM,
          NUM(TT, "s", 0.01), f"t = {nb(TT, 3)} s",
          f"<p>Le déplacement se termine à t<sub>2</sub> + 0,8 = {nb(T2, 3)} + 0,8 = <strong>{nb(TT, 3)} s</strong>.</p>"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>Dans un moteur à combustion, l'explosion est obtenue grâce à un mélange d'air et d'essence, dont la "
        "proportion varie avec des paramètres externes : température de l'air, température et vitesse de rotation du "
        "moteur. Une vanne additionnelle d'air, commandée par le calculateur, régule le débit d'air entrant.</p>"
        "<p>La rotation du moteur de la vanne (liaison pivot) est transformée en translation du boisseau de fermeture "
        "par la glissière hélicoïdale, dont le pas est de 0,5 mm. Le boisseau ouvre ou ferme le passage de l'air.</p>"
        + donnees("Vitesse de rotation maximale du moteur : 375 tr/min",
                  "Course maximale de fermeture du boisseau : 3 mm, au moment où il faut réduire les gaz imbrûlés "
                  "lors d'une décélération",
                  "Le déplacement à vitesse maximale est suivi d'une vitesse ralentie à 1 mm/s durant 0,5 s, pour "
                  "éviter le choc mécanique du boisseau sur le bloc moteur")
        + "</div>__FIG:photo-vanne|Corps d'injection et vanne d'air ; schéma cinématique : pivot du moteur, glissière "
          "hélicoïdale, boisseau en translation|Vanne d'air et son schéma cinématique.|330__</div>",
        "<p>Pendant la fermeture de 3 mm, le boisseau est régi par la loi de vitesse ci-dessous : le mouvement se "
        "décompose en cinq phases.</p>"
        + fig_svg(fig_vanne(), "Loi de vitesse du boisseau : montée de 0 à Vmax en 0,25 s, palier jusqu'à t2, descente à "
                  "1 mm/s en 0,2 s, palier de 0,5 s, arrêt en 0,1 s", "Loi de vitesse du boisseau (allure).", 560)]
    return {"key": "vanne-admission", "prefix": "i", "partie": "analytique", "tag": "Activité 1.2",
            "title": "Vanne d'admission d'air",
            "mots": ["MRU", "MRUV", "Glissière hélicoïdale", "Distance parcourue"], "methode": "MRU et MRUV",
            "sub": "Cinq phases pour fermer le passage de l'air : vitesse maximale par le pas de l'hélice, "
                   "accélérations et distances de chaque phase, puis durée totale du déplacement.",
            "hero": ("photo-vanne", "Vanne d'air d'un corps d'injection", "Vanne additionnelle d'air."),
            "dt": "ana",
            "parts": [{"title": "Vitesse maximale et phases à vitesse variable", "minutes": 30, "intro": intro, "blocks": p1},
                      {"title": "Phase à vitesse maximale et durée du déplacement", "minutes": 15, "intro": [], "blocks": p2}]}


# ====================================================================== 1.3 — AUTOMOTRICE À GRANDE VITESSE
def fig_agv():
    """Allure du graphe des accélérations (comme dans la séquence)."""
    F = Feuille(132, 66, "Graphe des accélérations de l'AGV")
    o = (18, 54)
    y5, y35, y2 = o[1] - 35, o[1] - 24.5, o[1] - 14
    t1, t2, ta, tb, t3 = 32, 62, 80, 100, 116
    F.trait((o[0], o[1]), (ta, o[1]), "fl")
    F.trait((ta, o[1]), (tb, o[1]), "tire")
    F.fleche((tb, o[1]), (128, o[1]), "fl", 2.4)
    F.fleche((o[0], o[1] + 2), (o[0], 6), "fl", 2.4)
    F.poly([(o[0], y5), (t1, y5), (t1, y35), (t2, y35), (t2, y2), (ta, y2)], "crb")
    F.trait((ta, y2), (tb, y2), "tire")
    F.poly([(tb, y2), (t3, y2), (t3, o[1])], "crb")
    for y, lab in [(y5, "0,5"), (y35, "0,35"), (y2, "0,2")]:
        F.trait((o[0] - 1.3, y), (o[0], y), "fin")
        F.texte((o[0] - 2.2, y), lab, "note", 3.1, "end")
    F.texte((o[0] - 2.2, o[1] + 2.8), "0", "note", 3.1, "end")
    for x, lab in [(t1, "1"), (t2, "2"), (t3, "3")]:
        F.trait((x, o[1]), (x, o[1] + 1.3), "fin")
        F.texte((x, o[1] + 4), f"t<tspan font-size=\"70%\" dy=\"1\">{lab}</tspan>", "note", 3.2)
    F.texte((o[0] + 3, 5), "a (m/s²)", "lab", 3.4, "start")
    F.texte((128, o[1] - 3.5), "t (s)", "lab", 3.4, "end")
    for n, p in [(1, (25, 28)), (2, (47, 36)), (3, (90, 46))]:
        F.numero(p, n, r=2.4)
    return F


def agv():
    A1, A2, A3 = 0.5, 0.35, 0.2
    V1, V2, V3 = 36 / 3.6, 144 / 3.6, 360 / 3.6     # 10, 40, 100 m/s
    T1 = V1 / A1                                    # 20 s
    X1 = 0.25 * T1 ** 2                             # 100 m
    V02 = V1 - A2 * T1                              # 3 m/s
    X02 = X1 - (A2 / 2 * T1 ** 2 + V02 * T1)        # −30 m
    T2 = (V2 - V02) / A2                            # 105,71 s
    XT2 = A2 / 2 * T2 ** 2 + V02 * T2 + X02         # 2 242,86 m
    T3 = T2 + 300                                   # 405,71 s
    XT3 = XT2 + 21000                               # 23 242,86 m
    assert abs((V2 + V3) / 2 * 300 - 21000) < 1e-6 and abs((V3 - V2) / 300 - A3) < 1e-9
    mn, sec = divmod(T3, 60)
    TL = 200
    VL = V2 + A3 * (TL - T2)                        # 58,86 m/s

    def v(t):
        return A1 * t if t <= T1 else (A2 * t + V02 if t <= T2 else V2 + A3 * (t - T2))

    F = Feuille(180, 196, "Diagrammes des accélérations et des vitesses de l'AGV")
    GA = F.graphe("a(t)", (22, 72), 0.3, 100, 450, 0, 0.6, (10, 50, 50), (0.05, 0.1, 0.1), "t", "a", "s", "m/s²",
                  dx=1, dy=2, titre="Diagramme des accélérations")
    GV = F.graphe("v(t)", (22, 184), 0.3, 0.8, 450, 0, 110, (10, 50, 50), (5, 10, 20), "t", "v", "s", "m/s",
                  up="m/s²", dx=1, dy=1, titre="Diagramme des vitesses")
    bornes = [(0, T1, "phase 1", A1), (T1, T2, "phase 2", A2), (T2, T3, "phase 3", A3)]
    # l'accélération est discontinue : chaque phase a sa valeur, jusqu'à ses bornes comprises
    ita = [IT_COURBE(GA, lambda t, ap=ap: ap, t0, t1, f"Accélérations, {lab}") for t0, t1, lab, ap in bornes]
    itv = [IT_COURBE(GV, v, t0, t1, f"Vitesses, {lab}") for t0, t1, lab, _a in bornes]
    AIRE = ["La distance parcourue", "L'accélération", "La durée de la phase", "La vitesse moyenne"]
    p1 = [
        CHAMPS("Q2 a)", "Convertis en m/s les vitesses atteintes aux différents instants.",
               tableau(["Instant", "t<sub>1</sub>", "t<sub>2</sub>", "t<sub>3</sub>"],
                       [("Vitesse (km/h)", "36", "144", "360"), ("Vitesse (m/s)", "[[1]]", "[[2]]", "[[3]]")]),
               [C("V(t1) (m/s)", V1, "10 m/s"), C("V(t2) (m/s)", V2, "40 m/s"), C("V(t3) (m/s)", V3, "100 m/s")],
               "<p>1 km/h = 1 000 m / 3 600 s : on divise par 3,6. 36 km/h = 10 m/s ; 144 km/h = 40 m/s ; "
               "360 km/h = 100 m/s.</p>"),
        Q("Q2 b)", "Détermine la durée t<sub>1</sub> de la phase 1.", "La phase 1 commence à t = 0. " + H_NUM,
          NUM(T1, "s", 0.01), "t<sub>1</sub> = 20 s",
          "<p>En fin de phase 1, v(t<sub>1</sub>) = 0,5 t<sub>1</sub> = 10 m/s, d'où t<sub>1</sub> = 10 / 0,5 = "
          "<strong>20 s</strong>.</p>"),
        Q("Q2 c)", "Détermine la distance x(t<sub>1</sub>) parcourue pendant la phase 1.", H_NUM, NUM(X1, "m", 0.01),
          "x(t<sub>1</sub>) = 100 m", "<p>x(t<sub>1</sub>) = 0,25 × 20² = <strong>100 m</strong>.</p>"),
        Q("Q3 a)", "Détermine la constante v<sub>02</sub> de la phase 2.",
          "Les équations de la phase 2 sont écrites dans le repère absolu (t = 0 au départ) ; à t = t<sub>1</sub>, "
          "la vitesse vaut 10 m/s. " + H_NUM, NUM(V02, "m/s", 0.01), "v<sub>02</sub> = 3 m/s",
          "<p>Le graphe des accélérations donne a<sub>2</sub> = 0,35 m/s². La vitesse est continue en t<sub>1</sub> : "
          "v(20) = 0,35 × 20 + v<sub>02</sub> = 10, d'où v<sub>02</sub> = 10 − 7 = <strong>3 m/s</strong>. "
          "(v<sub>02</sub> n'est pas une vitesse réellement atteinte : c'est l'ordonnée à l'origine de la droite "
          "des vitesses de la phase 2.)</p>"),
        Q("Q3 b)", "Détermine la constante x<sub>02</sub> de la phase 2.", "La position est continue en t<sub>1</sub>. " + H_NUM,
          NUM(X02, "m", 0.01), "x<sub>02</sub> = −30 m",
          "<p>x(20) = ½ × 0,35 × 20² + 3 × 20 + x<sub>02</sub> = 70 + 60 + x<sub>02</sub> = 100 m, d'où "
          "<strong>x<sub>02</sub> = −30 m</strong>.</p>"),
        Q("Q3 c)", "Détermine l'instant t<sub>2</sub> de fin de la phase 2.", H_NUM, NUM(T2, "s", 0.005),
          f"t<sub>2</sub> = {nb(T2, 2)} s",
          f"<p>v(t<sub>2</sub>) = 0,35 t<sub>2</sub> + 3 = 40 m/s, d'où t<sub>2</sub> = 37 / 0,35 = "
          f"<strong>{nb(T2, 2)} s</strong>.</p>"),
        CHAMPS("Q3 d)", "Écris les équations horaires de la phase 2 (t<sub>1</sub> ≤ t ≤ t<sub>2</sub>).",
               ligne("<i>x</i>(<i>t</i>) =", "[[1]]", "· <i>t</i>² +", "[[2]]", "· <i>t</i> +", "[[3]]", unite="(m)")
               + ligne("<i>v</i>(<i>t</i>) =", "[[4]]", "· <i>t</i> +", "[[5]]", unite="(m/s)")
               + ligne("<i>a</i>(<i>t</i>) =", "[[6]]", unite="(m/s²)"),
               [C("x : coefficient de t²", A2 / 2), C("x : coefficient de t", V02), C("x : terme constant", X02),
                C("v : coefficient de t", A2), C("v : terme constant", V02), C("a", A2)],
               "<p>x(t) = 0,175 t² + 3 t − 30 ; v(t) = 0,35 t + 3 ; a = 0,35 m/s².</p>"),
        Q("Q3 e)", "Calcule la position x(t<sub>2</sub>) en fin de phase 2.", H_NUM,
          NUM(XT2, "m", 0.005, [(XT2 / 1000, "km")]), f"x(t<sub>2</sub>) = {nb(XT2, 1)} m",
          f"<p>x({nb(T2, 2)}) = 0,175 × {nb(T2, 2)}² + 3 × {nb(T2, 2)} − 30 = <strong>{nb(XT2, 1)} m</strong>. "
          "Vérification sans le temps : v² − v<sub>1</sub>² = 2 a<sub>2</sub> (x − x<sub>1</sub>), soit "
          "40² − 10² = 0,7 (x − 100), d'où x = 100 + 2 142,9 = 2 242,9 m.</p>"),
        Q("Q4 a)", "Détermine l'instant t<sub>3</sub> où la vitesse maximale (360 km/h) est atteinte, en secondes.",
          "La phase 3 dure 5 min. " + H_NUM, NUM(T3, "s", 0.005), f"t<sub>3</sub> = {nb(T3, 1)} s",
          f"<p>t<sub>3</sub> = t<sub>2</sub> + 5 × 60 = {nb(T2, 2)} + 300 = <strong>{nb(T3, 1)} s</strong>. "
          "On vérifie l'accélération de la phase 3 : (100 − 40) / 300 = 0,2 m/s², celle du graphe.</p>"),
        CHAMPS("Q4 b)", "Exprime t<sub>3</sub> en heures, minutes et secondes (secondes arrondies à l'unité).",
               ligne("<i>t</i><sub>3</sub> =", "[[1]]", "h", "[[2]]", "min", "[[3]]", "s"),
               [C("Heures", 0, "0"), C("Minutes", mn, nb(mn, 0)), C("Secondes", round(sec), nb(round(sec), 0), tol=0.8)],
               f"<p>{nb(T3, 1)} s = 6 × 60 + {nb(sec, 1)} s : <strong>0 h 6 min {nb(round(sec), 0)} s</strong>.</p>"),
        Q("Q4 c)", "Détermine la distance totale x(t<sub>3</sub>) nécessaire, en kilomètres.",
          "La phase 3 couvre 21 km. " + H_NUM, NUM(XT3 / 1000, "km", 0.005, [(XT3, "m")]),
          f"x(t<sub>3</sub>) = {nb(XT3 / 1000, 2)} km",
          f"<p>x(t<sub>3</sub>) = x(t<sub>2</sub>) + 21 000 = {nb(XT2, 1)} + 21 000 = {nb(XT3, 0)} m, soit "
          f"<strong>{nb(XT3 / 1000, 2)} km</strong>. On vérifie la phase 3 : vitesse moyenne × durée = "
          "(40 + 100) / 2 × 300 = 21 000 m.</p>"),
    ]
    p2 = [
        TRACE("Q1 a)", "Trace, à l'échelle, le diagramme des accélérations de la sortie de gare.", H_GR, ita,
              cor_courbes(ita),
              f"<p>Trois paliers : 0,5 m/s² de 0 à 20 s, 0,35 m/s² de 20 à {nb(T2, 1)} s, 0,2 m/s² de {nb(T2, 1)} à "
              f"{nb(T3, 1)} s.</p>"),
        TRACE("Q1 b)", "Trace, à l'échelle, le diagramme des vitesses.", H_GR + " Pendant le tracé d'un segment, la pente "
              "s'affiche : c'est l'accélération.", itv, cor_courbes(itv),
              f"<p>Trois segments : de (0 ; 0) à (20 ; 10), de (20 ; 10) à ({nb(T2, 1)} ; 40), de ({nb(T2, 1)} ; 40) à "
              f"({nb(T3, 1)} ; 100). Chaque pente est l'accélération de la phase : la courbe des vitesses est de moins "
              "en moins pentue.</p>"),
        Q("Q1 c)", f"Lis sur ton diagramme la vitesse de l'AGV {TL} s après le départ, puis vérifie-la par le calcul.",
          H_NUM, NUM(VL, "m/s", 0.03, [(VL * 3.6, "km/h")]), f"v({TL}) ≈ {nb(VL, 1)} m/s ({nb(VL * 3.6, 0)} km/h)",
          f"<p>À t = {TL} s, l'AGV est en phase 3 : v = 40 + 0,2 × ({TL} − {nb(T2, 2)}) = <strong>{nb(VL, 1)} m/s</strong>, "
          f"soit {nb(VL * 3.6, 0)} km/h.</p>"),
        ETQ("Q1 d)", "Que représente l'aire comprise sous le diagramme des vitesses, entre deux instants ?",
            [("Aire sous la courbe v(t) entre deux instants", AIRE[0])], AIRE,
            "<p>Sur un petit intervalle, v × Δt est la distance parcourue : l'aire sous la courbe des vitesses est la "
            "<strong>distance parcourue</strong>. Pour la phase 3 : trapèze de bases 40 et 100 m/s et de hauteur "
            "300 s, soit 21 000 m.</p>", titre="Grandeurs"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>L'AGV (automotrice à grande vitesse) est un train à grande vitesse construit par Alstom. Successeur des "
        "TGV, il innove par sa motorisation répartie le long de la rame, au lieu de deux motrices placées aux "
        "extrémités : il dispose de plus d'espace pour les voyageurs et sa masse est réduite.</p>"
        "<p><strong>Objectif</strong> : étudier les temps et les distances pour sortir de gare et passer de 0 à "
        "360 km/h. La sortie de gare se fait en trois phases ; le mouvement retenu est une translation rectiligne, "
        "caractérisée par l'allure du graphe des accélérations ci-dessous.</p></div>"
        "__FIG:photo-agv|Automotrice à grande vitesse AGV|L'AGV.|420__</div>",
        fig_svg(fig_agv(), "Graphe des accélérations : 0,5 m/s² jusqu'à t1, 0,35 m/s² jusqu'à t2, 0,2 m/s² jusqu'à t3",
                "Allure du graphe des accélérations (échelle des temps non respectée).", 560)
        + donnees("Vitesses atteintes : V(0) = 0 ; V(t<sub>1</sub>) = 36 km/h ; V(t<sub>2</sub>) = 144 km/h ; "
                  "V(t<sub>3</sub>) = 360 km/h",
                  "Phase 1 (0 ≤ t ≤ t<sub>1</sub>) : x(t) = 0,25 t² (m) ; v(t) = 0,5 t (m/s) ; a(t) = 0,5 m/s²",
                  "Phase 2 (t<sub>1</sub> ≤ t ≤ t<sub>2</sub>) : x(t) = ½ a<sub>2</sub> t² + v<sub>02</sub> t + "
                  "x<sub>02</sub> ; v(t) = a<sub>2</sub> t + v<sub>02</sub> ; a(t) = a<sub>2</sub> = constante",
                  "Phase 3 : elle dure 5 min et l'AGV y parcourt 21 km"),
    ]
    intro2 = ["<p>La question 1 de la séquence (tracer le diagramme des vitesses) se traite ici, une fois "
              "t<sub>1</sub>, t<sub>2</sub> et t<sub>3</sub> connus : les diagrammes sont tracés à l'échelle.</p>"]
    return {"key": "agv", "prefix": "j", "partie": "analytique", "tag": "Activité 1.3",
            "title": "Automotrice à grande vitesse",
            "mots": ["MRUV", "Continuité", "Repère absolu", "Diagramme des vitesses"], "methode": "MRUV",
            "sub": "Sortir de gare et passer de 0 à 360 km/h en trois phases uniformément accélérées : instants, "
                   "constantes des équations horaires, distance totale, puis diagrammes à l'échelle.",
            "hero": ("photo-agv", "Automotrice à grande vitesse", "L'AGV, automotrice à grande vitesse."),
            "dt": "ana",
            "parts": [{"title": "Les trois phases de la sortie de gare", "minutes": 35, "intro": intro, "blocks": p1},
                      {"title": "Diagrammes des accélérations et des vitesses", "minutes": 15, "intro": intro2,
                       "meca": feuille(F), "noms": [], "blocks": p2}]}


# ====================================================================== 1.4 — MOTEUR ÉLECTRIQUE
def moteur():
    W1, W3 = 10 * PI, -20 * PI           # 31,42 rad/s ; −62,83 rad/s
    N1 = W1 * 60 / (2 * PI)              # 300 tr/min

    F = Feuille(186, 190, "Graphes du mouvement de rotation du moteur")
    GT = F.graphe("θ(t)", (24, 86), 12, 1, 12, 0, 70, (0.5, 1, 1), (5, 10, 10), "t", "θ", "s", "rad", up="rad/s",
                  dx=2, dy=2, titre="Espace angulaire (donné)")
    GW = F.graphe("ω(t)", (24, 140), 12, 0.6, 12, -70, 40, (0.5, 1, 1), (5, 10, 20), "t", "ω", "s", "rad/s",
                  up="rad/s²", dx=2, dy=2, titre="Vitesse angulaire (à tracer)")
    F.poly([GT.p(0, 0), GT.p(2, 20 * PI), GT.p(10, 20 * PI), GT.p(11, 0)], "crb")
    F.trait(GT.p(0, 20 * PI), GT.p(2, 20 * PI), "tire")
    F.texte(g_add(GT.p(6, 20 * PI), (0, -2.6)), "θ = 20π rad", "lab", 3.3)
    # ω est discontinue : chaque phase a sa valeur, jusqu'à ses bornes comprises
    itw = [IT_COURBE(GW, lambda t: W1, 0, 2, "Vitesse angulaire, phase 1 (0 < t < 2 s)"),
           IT_COURBE(GW, lambda t: 0.0, 2, 10, "Vitesse angulaire, phase 2 (2 < t < 10 s)"),
           IT_COURBE(GW, lambda t: W3, 10, 11, "Vitesse angulaire, phase 3 (10 < t < 11 s)")]
    pi = "<i>π</i>"
    blocks = [
        Q("Q1.1 a)", "Détermine la vitesse angulaire ω<sub>1</sub> du moteur pendant la phase 1 (0 < t < 2 s).",
          "Lis le graphe : θ passe de 0 à 20π rad en 2 s. Saisis une valeur décimale (π ≈ 3,1416) et son unité. "
          "Sur la feuille, un segment tracé le long de la courbe affiche sa pente.", NUM(W1, "rad/s", 0.01),
          f"ω<sub>1</sub> = 10π = {nb(W1, 2)} rad/s",
          f"<p>θ croît linéairement : la vitesse angulaire est la pente du graphe, ω<sub>1</sub> = Δθ / Δt = 20π / 2 = "
          f"10π = <strong>{nb(W1, 2)} rad/s</strong>.</p>"),
        CHAMPS("Q1.1 b)", "Écris les équations du mouvement pendant la phase 1.",
               ligne("θ(<i>t</i>) =", "[[1]]", f"{pi} · <i>t</i> +", "[[2]]", unite="(rad)")
               + ligne("ω(<i>t</i>) = θ'(<i>t</i>) =", "[[3]]", pi, unite="(rad/s)")
               + ligne("θ''(<i>t</i>) =", "[[4]]", unite="(rad/s²)"),
               [C("θ : coefficient de π·t", 10), C("θ : terme constant", 0), C("ω : coefficient de π", 10), C("θ''", 0)],
               "<p>θ(t) = 10π t ; ω = 10π rad/s ; θ'' = 0 : mouvement circulaire uniforme (MCU), θ = ω t + "
               "θ<sub>0</sub> avec θ<sub>0</sub> = 0.</p>", hint=HC + " Les cases devant π attendent le coefficient de π."),
        CHAMPS("Q1.1 c)", "Écris les équations du mouvement pendant la phase 2 (2 < t < 10 s).",
               ligne("θ(<i>t</i>) =", "[[1]]", pi, unite="(rad)") + ligne("ω(<i>t</i>) =", "[[2]]", unite="(rad/s)"),
               [C("θ : coefficient de π", 20), C("ω (rad/s)", 0)],
               "<p>θ = 20π rad, constant : le moteur est arrêté, ω = 0. Les équations sont les mêmes dans le repère "
               "placé en début de phase et dans le repère absolu.</p>", hint=HC),
        Q("Q1.1 d)", "Détermine la vitesse angulaire ω<sub>3</sub> pendant la phase 3 (10 < t < 11 s), avec son signe.",
          "θ passe de 20π à 0 en 1 s. Saisis une valeur décimale et son unité.", NUM(W3, "rad/s", 0.01),
          f"ω<sub>3</sub> = −20π = {nb(W3, 2)} rad/s",
          f"<p>ω<sub>3</sub> = (0 − 20π) / 1 = −20π = <strong>{nb(W3, 2)} rad/s</strong> : le moteur tourne en sens "
          "inverse, deux fois plus vite qu'en phase 1.</p>"),
        CHAMPS("Q1.1 e)", "Écris l'équation θ(t) de la phase 3, en plaçant le repère en début de phase (t' = t − 10), "
                          "puis dans le repère absolu.",
               ligne("Début de phase : θ(<i>t'</i>) =", "[[1]]", f"{pi} · <i>t'</i> +", "[[2]]", pi, unite="(rad)")
               + ligne("Repère absolu : θ(<i>t</i>) =", "[[3]]", f"{pi} · <i>t</i> +", "[[4]]", pi, unite="(rad)"),
               [C("θ(t') : coefficient de π·t'", -20), C("θ(t') : coefficient de π", 20),
                C("θ(t) : coefficient de π·t", -20), C("θ(t) : coefficient de π", 220)],
               "<p>En début de phase, θ<sub>0</sub> = 20π et ω = −20π : θ(t') = −20π t' + 20π. Avec t' = t − 10 : "
               "θ(t) = −20π (t − 10) + 20π = <strong>−20π t + 220π</strong>. Vérification : θ(11) = −220π + 220π = 0.</p>",
               hint=HC + " Les cases devant π attendent le coefficient de π."),
        ETQ("Q1.1 f)", "Quelle est la nature du mouvement du rotor pendant chaque phase ?",
            [("Phase 1", NAT_C[0]), ("Phase 2", NAT_C[3]), ("Phase 3", NAT_C[0])], NAT_C,
            "<p>Phases 1 et 3 : θ varie linéairement, ω est constante : mouvement circulaire uniforme (dans un sens "
            "puis dans l'autre). Phase 2 : θ constant, le rotor est arrêté.</p>", titre="Natures"),
        Q("Q1.1 g)", "Calcule la fréquence de rotation N<sub>1</sub> du moteur pendant la phase 1, en tr/min.", H_NUM,
          NUM(N1, "tr/min", 0.01), "N<sub>1</sub> = 300 tr/min",
          "<p>N = 60 ω / 2π = 60 × 10π / 2π = <strong>300 tr/min</strong> ; en 2 s, le rotor fait 20π / 2π = 10 tours.</p>"),
        TRACE("Q1.2", "Trace le graphe des vitesses angulaires ω(t).", H_GR, itw,
              cor_courbes(itw, [C_SG(GW.p(2, 40), GW.p(2, -70), "aide"), C_SG(GW.p(10, 40), GW.p(10, -70), "aide")]),
              f"<p>Trois paliers : ω = 10π ≈ {nb(W1, 1)} rad/s de 0 à 2 s, ω = 0 de 2 à 10 s, ω = −20π ≈ {nb(W3, 1)} "
              "rad/s de 10 à 11 s. La vitesse angulaire est la pente du graphe de θ.</p>"),
    ]
    intro = [
        "<p>Le mouvement de rotation d'un moteur électrique est caractérisé par le graphe de l'espace angulaire θ(t), "
        "donné sur la feuille. Il se décompose en trois phases : phase 1 pour 0 < t < 2 s, phase 2 pour 2 < t < 10 s, "
        "phase 3 pour 10 < t < 11 s.</p>"
        + donnees("θ(0) = 0 ; θ = 20π rad de t = 2 s à t = 10 s ; θ(11) = 0",
                  "Entre ces instants, θ varie linéairement avec le temps")]
    return {"key": "moteur-electrique", "prefix": "k", "partie": "analytique", "tag": "Activité 1.4",
            "title": "Moteur électrique",
            "mots": ["MCU", "Abscisse angulaire", "Vitesse angulaire", "Repère absolu"], "methode": "MCU",
            "sub": "Du graphe de l'espace angulaire aux équations de chaque phase, dans le repère de la phase puis "
                   "dans le repère absolu, et au graphe des vitesses angulaires.",
            "hero": ("photo-transmission", "Moteur électrique, réducteur et transmission par courroie vers un volant d'inertie",
                     "Un moteur électrique et sa transmission (figure de la séquence)."), "dt": "ana",
            "parts": [{"title": "Mouvement de rotation du moteur", "minutes": 35, "intro": intro, "meca": feuille(F),
                       "noms": [], "blocks": blocks}]}


def g_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


ACTIVITES = [imprimante, vanne, agv, moteur]
