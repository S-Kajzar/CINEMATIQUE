# -*- coding: utf-8 -*-
"""Cours 1 — compléments tirés de la séquence « Cinématique analytique » : abscisse curviligne, vitesse instantanée,
accélérations moyenne et instantanée, composantes tangentielle et normale ; analyse de quatre mouvements (laboratoire
et exercices) ; mouvement rectiligne uniforme (MRU) et ses applications ; mouvement rectiligne uniformément varié
(MRUV) ; mouvement circulaire (MC, MCU, MCUV) et l'application « transmission de puissance ».

Les exercices d'application sont vérifiés par le moteur de correction du gabarit (cours_commun.exo) : l'élève
vérifie autant de fois qu'il le veut, puis peut afficher la solution. Les études de systèmes de la séquence
(imprimante 3D, vanne d'air, AGV, moteur électrique) sont des activités notées : le cours y renvoie.
"""
import math

from cours_commun import exo, formule, frac, nombre, num, vec

V, G, OM = vec("V"), vec("Γ"), vec("OM")
X_, Y_, T_, N_ = vec("x"), vec("y"), vec("t"), vec("n")
PI = math.pi
MM = ["mm", "millimetre", "millimetres"]
MMS = ["mm/s", "mms-1"]
MMS2 = ["mm/s2", "mms-2", "mm/s/s"]
M_ = ["m", "metre", "metres"]
MS = ["m/s", "ms-1"]
MS2 = ["m/s2", "ms-2", "m/s/s"]
RADS = ["rad/s", "rads-1", "radian/s", "radians/s"]
S_ = ["s", "sec", "seconde", "secondes"]


def VM(nom, pt="M", sol="S/R"):
    return f'<span class="vv">{vec(nom)}<sub>{pt}∈{sol}</sub></span>'


def nb(x, d=3):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s.replace("-", "−")


def tab(entetes, lignes):
    th = "".join(f"<th>{h}</th>" for h in entetes)
    tr = "".join("<tr><th>" + l[0] + "</th>" + "".join(f"<td>{c}</td>" for c in l[1:]) + "</tr>" for l in lignes)
    return f'<table class="t"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def lien_activite(key, tag, titre, texte):
    return (f'<a class="ca-act" href="?ex={key}"><span class="mc-tag">{tag}</span><b>{titre}</b>'
            f"<span>{texte}</span></a>")


# ====================================================================== petits graphes de principe (SVG, px)
def schema(ident, panels, label, w=250, h=176):
    """Graphes de principe côte à côte : chaque panneau a un titre, un nom d'axe vertical et des courbes données en
    coordonnées réduites (u de 0 à 1 le long du temps, v de 0 à 1 vers le haut ; l'axe des temps est en v = v0)."""
    W = w * len(panels)
    out = [f'<svg viewBox="0 0 {W} {h}" role="img" aria-label="{label}"><defs><marker id="{ident}-f" viewBox="0 0 10 10" '
           'refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 10,5 0,10z" fill="#1C2530"/>'
           "</marker></defs>"]
    for i, p in enumerate(panels):
        x0, y0, pw, ph = i * w + 30, 22, w - 62, h - 64
        v0 = p.get("v0", 0)

        def P(u, v):
            return (x0 + u * pw, y0 + (1 - v) * ph)
        yz = P(0, v0)[1]
        out.append(f'<line x1="{x0}" y1="{yz:.1f}" x2="{x0 + pw + 18}" y2="{yz:.1f}" stroke="#1C2530" stroke-width="1.6" '
                   f'marker-end="url(#{ident}-f)"/><line x1="{x0}" y1="{y0 + ph + 4}" x2="{x0}" y2="{y0 - 12}" '
                   f'stroke="#1C2530" stroke-width="1.6" marker-end="url(#{ident}-f)"/>'
                   f'<text x="{x0 + 6}" y="{y0 - 6}" font-size="13" font-weight="700">{p["y"]}</text>'
                   f'<text x="{x0 + pw + 16}" y="{yz - 6:.1f}" font-size="13" text-anchor="end">t</text>'
                   f'<text x="{x0 - 6}" y="{yz + 14:.1f}" font-size="12" text-anchor="end">0</text>')
        for pts, c in p["courbes"]:
            q = " ".join(f"{P(u, v)[0]:.1f},{P(u, v)[1]:.1f}" for u, v in pts)
            out.append(f'<polyline points="{q}" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>')
        for u, v, txt, anc in p.get("notes", ()):
            x, y = P(u, v)
            out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="12" text-anchor="{anc}" fill="#46525C">{txt}</text>')
        for u0, v0_, u1, v1_ in p.get("tirets", ()):
            a, b = P(u0, v0_), P(u1, v1_)
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#7A848C" '
                       'stroke-dasharray="4 3"/>')
        if p.get("aire"):
            q = " ".join(f"{P(u, v)[0]:.1f},{P(u, v)[1]:.1f}" for u, v in p["aire"])
            out.append(f'<polygon points="{q}" fill="#1F5FA8" opacity=".14"/>')
        out.append(f'<text x="{x0 + pw / 2:.1f}" y="{h - 8}" font-size="13" font-weight="700" text-anchor="middle" '
                   f'fill="#1F5FA8">{p["titre"]}</text>')
    out.append("</svg>")
    return f'<figure class="simu-fig ca-schema" style="max-width:{W}px">{"".join(out)}</figure>'


def parabole(a, b, c, n=24):
    return [(i / n, a * (i / n) ** 2 + b * (i / n) + c) for i in range(n + 1)]


# ====================================================================== graphes d'énoncé (feuille de l'atelier, mm)
def fig_feuille(F, alt, maxw):
    return (f'<figure class="fig fig-svg" style="max-width:{maxw}px"><svg viewBox="0 0 {F.w} {F.h}" role="img" '
            f'aria-label="{alt}" xmlns="http://www.w3.org/2000/svg">{F.svg_fig()}</svg></figure>')


def graphe_mru2(A):
    F = A.atelier.Feuille(170, 82, "Graphe des espaces")
    Gr = F.graphe("x(t)", (14, 72), 5.2, 7, 27, 0, 8, (1, 5, 5), (1, 1, 1), "t", "x", "s", "", dx=1, dy=1)
    pts = [(0, 0), (5, 5), (15, 5), (17, 7), (25, 0)]
    F.poly([Gr.p(*q) for q in pts], "crb")
    for t, x in [(5, 5), (15, 5), (17, 7)]:
        F.trait(Gr.p(t, 0), Gr.p(t, x), "tire")
        F.trait(Gr.p(0, x), Gr.p(t, x), "tire")
    F.texte(Gr.p(17, -0.55), "17", "note", 3, "middle")
    return fig_feuille(F, "Graphe des espaces : x croît de 0 à 5 entre 0 et 5 s, reste à 5 jusqu'à 15 s, croît jusqu'à 7 "
                          "à 17 s, puis décroît jusqu'à 0 à 25 s", 560)


def graphe_mru4(A):
    F = A.atelier.Feuille(176, 128, "Graphe des positions de quatre solides")
    Gr = F.graphe("x(t)", (20, 116), 9, 0.42, 16, 0, 250, (1, 5, 5), (10, 30, 30), "t", "x", "s", "mm", dx=1, dy=0)
    F.poly([Gr.p(0, 0), Gr.p(15.5, 46.5)], "crb")
    F.poly([Gr.p(0, 0), Gr.p(15.5, 186)], "crb crb-t")
    F.poly([Gr.p(0, 100), Gr.p(15, 250)], "crb crb-m")
    F.poly([Gr.p(2, 140), Gr.p(8, 60), Gr.p(11, 60), Gr.p(12, 0)], "crb")
    for nom, q, d in [("A", (0, 0), (-3.5, -2.5)), ("B", (0, 100), (-3.5, -2.5)), ("C", (2, 140), (0, -3.2)),
                      ("D", (8, 60), (0, 3.6)), ("E", (11, 60), (0.5, -3.2)), ("F", (12, 0), (3, -2.6))]:
        F.point(nom, Gr.p(*q), d, 3.4, marque=True)
    for n, q in [("1", (15.8, 50)), ("2", (15.8, 192)), ("3", (14.6, 246)), ("4", (5, 116))]:
        F.texte(Gr.p(*q), n, "lab", 3.6)
    return fig_feuille(F, "Graphe des positions : mouvements 1, 2 et 3 rectilignes uniformes (droites), mouvement 4 par "
                          "les points C, D, E et F", 600)


# ====================================================================== 3. compléments : abscisse curviligne…
FIG_ABS = """<figure class="simu-fig ca-fig" style="width:400px"><svg viewBox="0 0 420 200" role="img" aria-label="Trajectoire orientée : origine A, point M, abscisse curviligne x, mesure de l'arc AM">
<defs><marker id="ca-ab-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 10,5 0,10z" fill="#1C2530"/></marker></defs>
<path d="M30,160 C110,40 230,30 390,120" fill="none" stroke="#1C2530" stroke-width="2.5"/>
<path d="M58,124 C120,48 190,42 252,58" fill="none" stroke="#B42318" stroke-width="6" opacity=".55"/>
<path d="M330,86 L372,108" stroke="#1C2530" stroke-width="2" marker-end="url(#ca-ab-f)"/>
<circle cx="58" cy="124" r="5" fill="#1C2530"/><circle cx="252" cy="58" r="5" fill="#1F5FA8"/>
<g font-size="15" font-weight="700"><text x="34" y="122">A</text><text x="248" y="44">M</text><text x="146" y="40" fill="#B42318">x = arc AM</text>
<text x="380" y="98">+</text><text x="300" y="150" font-weight="400" font-size="13">T(M∈S/R) orientée</text></g></svg></figure>"""

FIG_FRENET = """<figure class="simu-fig ca-fig" style="width:420px"><svg viewBox="0 0 440 250" role="img" aria-label="Repère local en M : vecteur t tangent, vecteur n normal orienté vers l'extérieur ; accélération et ses composantes tangentielle et normale, dirigée vers le centre de courbure">
<defs><marker id="ca-fr-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 10,5 0,10z" fill="context-stroke"/></marker></defs>
<path d="M40,210 C90,70 260,40 410,120" fill="none" stroke="#1C2530" stroke-width="2.5"/>
<line x1="208" y1="79" x2="225" y2="203" stroke="#7A848C" stroke-dasharray="4 3"/><circle cx="225" cy="203" r="3.5" fill="#7A848C"/>
<line x1="208" y1="79" x2="282" y2="69" stroke="#1C2530" stroke-width="2.2" marker-end="url(#ca-fr-f)"/>
<line x1="208" y1="79" x2="200" y2="20" stroke="#1C2530" stroke-width="2.2" marker-end="url(#ca-fr-f)"/>
<line x1="208" y1="79" x2="252" y2="73" stroke="#1B7A43" stroke-width="4" marker-end="url(#ca-fr-f)"/>
<line x1="208" y1="79" x2="219" y2="163" stroke="#1B7A43" stroke-width="4" marker-end="url(#ca-fr-f)"/>
<line x1="252" y1="73" x2="264" y2="157" stroke="#1B7A43" stroke-dasharray="3 3"/><line x1="219" y1="163" x2="264" y2="157" stroke="#1B7A43" stroke-dasharray="3 3"/>
<line x1="208" y1="79" x2="264" y2="157" stroke="#0B5A2E" stroke-width="2.6" marker-end="url(#ca-fr-f)"/>
<circle cx="208" cy="79" r="5" fill="#1F5FA8"/>
<g font-size="16" font-weight="700"><text x="186" y="74">M</text><text x="286" y="66">t</text><text x="184" y="22">n</text>
<text x="236" y="64" fill="#1B7A43" font-size="14">Γt</text><text x="196" y="160" fill="#1B7A43" font-size="14">Γn</text>
<text x="270" y="162" fill="#0B5A2E">Γ</text><text x="236" y="222" fill="#7A848C" font-size="13" font-weight="400">centre de courbure ; R = rayon</text></g>
</svg></figure>"""


def vitesse_avant():
    v1, v2, dv = VM("V", "M1"), VM("V", "M2"), "Δ" + V
    G_MOY = f"{G}<sub>moy</sub> = {frac(dv, 'Δt')} = {frac(v2 + ' − ' + v1, 't<sub>2</sub> − t<sub>1</sub>')}"
    G_INST = f"{G} = lim<sub>Δt→0</sub> {frac(dv, 'Δt')} = {frac('d' + V, 'dt')}"
    return f"""
<h3>Abscisse curviligne</h3>
<div class="cours-split"><div>
<p>Sur sa trajectoire T(M∈S/R), orientée, la position du point M se repère par une seule grandeur : l'<strong>abscisse
curviligne</strong> x, mesure algébrique, à l'instant t, de l'arc AM, A étant l'origine du mouvement. Cette longueur
d'arc varie avec le temps.</p>
{formule("x = f(t)", "équation horaire du mouvement ; x en m (ou mm), t en s")}
</div>{FIG_ABS}</div>
<h3>Vitesse instantanée</h3>
<p>Entre les instants t et t + Δt, le point M parcourt l'arc Δx : sa vitesse moyenne est Δx / Δt. La vitesse
<strong>instantanée</strong> est la limite de ce rapport quand Δt tend vers zéro : c'est la dérivée de l'abscisse
curviligne par rapport au temps.</p>
{formule(f"v = lim<sub>Δt→0</sub> {frac('Δx', 'Δt')} = {frac('dx', 'dt')} = x'(t)", "vitesse algébrique, en m/s")}
<h3>Accélération moyenne et instantanée</h3>
<p>Deux points M<sub>1</sub> et M<sub>2</sub> de la trajectoire, atteints aux instants t<sub>1</sub> et t<sub>2</sub>,
ont pour vitesses {VM('V', 'M1')} et {VM('V', 'M2')}. Δ{V} = {VM('V', 'M2')} − {VM('V', 'M1')} est la variation de la
vitesse du point M entre t<sub>1</sub> et t<sub>2</sub>.</p>
<div class="cours-split"><div>{formule(G_MOY, "accélération moyenne")}</div>
<div>{formule(G_INST, "accélération instantanée, en m/s²")}</div></div>
"""


def vitesse_apres():
    return f"""
<h3>Composantes tangentielle et normale de l'accélération</h3>
<div class="cours-split"><div>
<p>On définit un repère local (M, {T_}, {N_}) lié au point M : (M, {T_}) tangent à la trajectoire, dans le sens du
déplacement ; (M, {N_}) normal à la trajectoire et orienté vers l'<strong>extérieur</strong> de la courbe. R est le
rayon de courbure de la trajectoire en M.</p>
{formule(f"{VM('Γ')} = Γ<sub>t</sub>·{T_} + Γ<sub>n</sub>·{N_}", f"avec Γ<sub>t</sub> = {frac('dv', 'dt')} et Γ<sub>n</sub> = −{frac('v²', 'R')}")}
<ul><li><strong>Γ<sub>t</sub></strong>, composante tangentielle : traduit la variation de la norme de la vitesse ;
elle est nulle si la vitesse est constante en norme ;</li>
<li><strong>Γ<sub>n</sub></strong>, composante normale : traduit le changement de direction de la vitesse ; elle est
toujours dirigée vers l'intérieur de la courbe, d'où le signe −, {N_} étant orienté vers l'extérieur.</li></ul>
</div>{FIG_FRENET}</div>
<div class="cours-split"><div class="remarque"><p><strong>Mouvement de translation rectiligne</strong> : la trajectoire
est une droite, son rayon de courbure est infini. Γ<sub>n</sub> = 0 : l'accélération est portée par la trajectoire,
{VM('Γ')} = Γ<sub>t</sub>·{T_}.</p></div>
<div class="remarque"><p><strong>Mouvement de rotation</strong> : la trajectoire est un cercle de rayon R constant.
Γ<sub>n</sub> = −v²/R = −R·ω² n'est jamais nulle tant que le point tourne ; Γ<sub>t</sub> = R·θ'' est nulle si la
rotation est uniforme (section 10).</p></div></div>
"""


# ====================================================================== 4. analyse de mouvements
def analyse():
    r10 = math.sqrt(10)
    m1 = [
        exo("M1 · Q1", "Calcule l'abscisse x du point M aux instants t = 0 à t = 5 s, par incrément d'une seconde "
                       "(y vaut 1 mm à chaque instant).",
            [(f"x({t}) (mm)", nombre(3 * t + 1)) for t in range(6)],
            "<p>x = 3t + 1 : 1 ; 4 ; 7 ; 10 ; 13 ; 16 mm. Les positions M<sub>0</sub> à M<sub>5</sub> sont sur la droite "
            "y = 1, régulièrement espacées de 3 mm : c'est la trajectoire.</p>",
            tab(["t (s)"] + [str(t) for t in range(6)], [("x (mm)",) + tuple(f"[[{t + 1}]]" for t in range(6))])),
        exo("M1 · Q5", "Montre que le mouvement est uniforme : calcule la norme de la vitesse de M.",
            [("‖V‖", num(3, "mm/s", MMS))],
            f"<p>{VM('V')} = (x' ; y') = (3 ; 0) : la vitesse est constante, 3 mm/s, et la trajectoire est une droite : "
            "mouvement rectiligne uniforme. Le graphe x(t) est une droite de pente 3 mm/s.</p>",
            aide="Saisis la valeur et son unité (ex. 3 mm/s)."),
    ]
    m2 = [
        exo("M2 · Q3", "Détermine l'équation de la trajectoire du point M, sous la forme y = a·x + b.",
            [("a", nombre(1 / 3)), ("b", nombre(-4 / 3))],
            "<p>t² = (x − 1)/3, donc y = t² − 1 = (x − 1)/3 − 1 = <strong>(x − 4)/3</strong> : a = 1/3 ≈ 0,333 et "
            "b = −4/3 ≈ −1,333. La trajectoire est une droite, parcourue de (1 ; −1) à t = 0 jusqu'à (13 ; 3) à t = 2 s.</p>",
            "<i>y</i> = [[1]] · <i>x</i> + [[2]]", "Saisis des valeurs décimales (au millième)."),
        exo("M2 · Q4", "Quelle est la distance parcourue par M entre t = 0 et t = 2 s ?",
            [("distance", num(math.hypot(12, 4), "mm", MM))],
            "<p>La trajectoire est une droite et le point ne revient pas en arrière : distance = M<sub>0</sub>M<sub>4</sub> "
            "= √(12² + 4²) = √160 = <strong>12,65 mm</strong>.</p>", aide="Valeur et unité."),
        exo("M2 · Q6", "Calcule la norme de la vitesse de M aux instants t = 0 ; 0,5 ; 1 ; 1,5 et 2 s.",
            [(f"‖V‖({nb(t, 1)}) (mm/s)", nombre(2 * r10 * t, 0.01)) for t in (0, 0.5, 1, 1.5, 2)],
            f"<p>{VM('V')} = (6t ; 2t) ; ‖V‖ = √(36t² + 4t²) = 2√10·t ≈ 6,325·t : 0 ; 3,16 ; 6,32 ; 9,49 ; 12,65 mm/s. "
            "La vitesse croît proportionnellement au temps.</p>",
            tab(["t (s)", "0", "0,5", "1", "1,5", "2"], [("‖V‖ (mm/s)", "[[1]]", "[[2]]", "[[3]]", "[[4]]", "[[5]]")])),
        exo("M2 · Q8", "Calcule la norme du vecteur accélération de M.", [("‖Γ‖", num(2 * r10, "mm/s²", MMS2))],
            f"<p>{VM('Γ')} = (6 ; 2) à chaque instant : ‖Γ‖ = √40 = <strong>6,32 mm/s²</strong>, constante. Courbes "
            "obtenues : x(t) = 3t² + 1, une parabole ; ‖V‖(t) = 6,32 t, une droite ; ‖Γ‖ constante, une horizontale : "
            "mouvement rectiligne uniformément accéléré.</p>", aide="Valeur et unité."),
    ]
    m3 = [
        exo("M3 · Q1 à Q6", "Calcule la norme du vecteur position, celle de la vitesse et celle de l'accélération : "
                            "sont-elles constantes ?",
            [("‖OM‖ (mm)", nombre(1)), ("‖V‖ (mm/s)", nombre(1)), ("‖Γ‖ (mm/s²)", nombre(1))],
            f"<p>‖OM‖ = √(cos² t + sin² t) = 1 mm : la trajectoire est le cercle de centre O et de rayon 1 mm. "
            f"{VM('V')} = (−sin t ; cos t), de norme 1 mm/s, perpendiculaire à OM : tangente au cercle. "
            f"{VM('Γ')} = (−cos t ; −sin t) = −{OM}, de norme 1 mm/s², dirigée vers le centre. Les trois normes sont "
            "constantes : mouvement circulaire uniforme ; l'accélération n'est pas nulle pour autant.</p>",
            "‖" + OM + "‖ = [[1]] mm ; ‖" + V + "‖ = [[2]] mm/s ; ‖" + G + "‖ = [[3]] mm/s²"),
    ]
    m4 = [
        exo("M4 · Q1", "Détermine l'équation de la trajectoire de M dans le repère R.",
            [("coefficient", nombre(0.5)), ("décalage en x", nombre(1)), ("ordonnée du sommet", nombre(2))],
            "<p>t = x − 1, donc y = ½ (x − 1)² + 2 : une parabole de sommet (1 ; 2).</p>",
            "<i>y</i> = [[1]] · (<i>x</i> − [[2]])² + [[3]]"),
        exo("M4 · Q3", "Détermine les composantes du vecteur vitesse aux instants t = −2, t = 0 et t = 3 s.",
            [(f"{c}({t})", nombre(v)) for t in (-2, 0, 3) for c, v in (("x'", 1), ("y'", t))],
            f"<p>{VM('V')} = (x' ; y') = (1 ; t) : (1 ; −2), (1 ; 0) et (1 ; 3). À t = 0, la vitesse est horizontale : M "
            "passe au sommet de la parabole.</p>",
            tab(["t (s)", "−2", "0", "3"], [("x'", "[[1]]", "[[3]]", "[[5]]"), ("y'", "[[2]]", "[[4]]", "[[6]]")])),
        exo("M4 · Q5", "Détermine les composantes du vecteur accélération (elles sont les mêmes aux trois instants).",
            [("x''", nombre(0)), ("y''", nombre(1))],
            f"<p>{VM('Γ')} = (0 ; 1), constant : l'accélération garde toujours la même direction (verticale), comme pour "
            "un projectile. Elle n'est pas portée par la vitesse : la trajectoire est courbe.</p>",
            f"{VM('Γ')} = ( [[1]] ; [[2]] )"),
    ]
    btn = "".join(f'<button type="button" class="btn ghost" data-lm="{i}" aria-pressed="{"true" if i == 1 else "false"}">'
                  f"Mouvement {i}</button>" for i in range(1, 5))
    return f"""
<p>Quatre mouvements de points, définis par leur vecteur position dans le repère R (O, {X_}, {Y_}, {vec('z')}) (z = 0) :
le laboratoire place les positions aux instants de l'énoncé, trace la trajectoire, les vecteurs vitesse et
accélération, et calcule leurs composantes ; les exercices se vérifient seuls.</p>
<div class="simu" id="ca-labo"><h3>Laboratoire : quatre mouvements</h3>
<div class="simu-btns">{btn}</div>
<p class="ca-l-def"></p>
<div class="simu-grid"><label>Instant t <output class="ca-l-t"></output><input type="range" class="ca-l-tr" min="0" max="5" step="0.01" value="1"></label>
<label><span><input type="checkbox" class="ca-l-anim"> Animer</span></label>
<label><span><input type="checkbox" class="ca-l-vec" checked> Vecteurs vitesse et accélération</span></label></div>
<div class="simu-fig"><svg viewBox="0 0 760 330" role="img" aria-label="Trajectoire du point M, positions aux instants de l'énoncé, vecteurs vitesse et accélération"><g class="ca-l-monde"></g></svg></div>
<div class="simu-out"><div><span>Position (x ; y)</span><b class="ca-l-p"></b></div><div><span>Vitesse : (x' ; y')</span><b class="ca-l-v"></b></div>
<div><span>Norme de la vitesse</span><b class="ca-l-nv"></b></div><div><span>Accélération : (x'' ; y'') ; norme</span><b class="ca-l-g"></b></div></div>
<div class="ca-l-tab"></div>
<p class="simu-note ca-l-obs"></p></div>
<h3>Mouvement 1 : x = 3t + 1 ; y = 1 (mm, s)</h3>{"".join(m1)}
<h3>Mouvement 2 : x = 3t² + 1 ; y = t² − 1 (mm, s)</h3>{"".join(m2)}
<h3>Mouvement 3 : x = cos t ; y = sin t (mm, s)</h3>{"".join(m3)}
<h3>Mouvement 4 : x = t + 1 ; y = ½ t² + 2</h3>{"".join(m4)}
"""


# ====================================================================== 8. MRU
def mru(A):
    s5 = math.hypot(10, 15)
    ex1 = [
        exo("1.1 et 1.2", "Calcule les positions de M aux instants t = 0, 3 et 5 s.",
            [(f"{c}({t})", nombre(v)) for t in (0, 3, 5) for c, v in (("x", 2 * t), ("y", 3 * t - 5))],
            "<p>x = 2t et y = 3t − 5 sont des fonctions affines du temps : (0 ; −5), (6 ; 4), (10 ; 10). Première "
            "remarque : les composantes de la vitesse (2 ; 3) sont constantes, le mouvement est rectiligne "
            "uniforme.</p>",
            tab(["t (s)", "0", "3", "5"], [("x (m)", "[[1]]", "[[3]]", "[[5]]"), ("y (m)", "[[2]]", "[[4]]", "[[6]]")])),
        exo("1.3", "Détermine l'équation de la trajectoire.", [("a", nombre(1.5)), ("b", nombre(-5))],
            "<p>t = x/2, donc y = 3x/2 − 5 = <strong>1,5 x − 5</strong> : une droite.</p>",
            "<i>y</i> = [[1]] · <i>x</i> + [[2]]"),
        exo("1.4", "Détermine la distance parcourue durant ces 5 secondes.", [("distance", num(s5, "m", M_))],
            "<p>Distance = √(10² + 15²) = √325 = <strong>18,03 m</strong>.</p>", aide="Valeur et unité."),
        exo("1.5", "Détermine la vitesse de M<sub>S</sub>.", [("vitesse", num(math.hypot(2, 3), "m/s", MS))],
            f"<p>{VM('V')} = (2 ; 3) : ‖V‖ = √13 = <strong>3,61 m/s</strong> (ou 18,03 m / 5 s).</p>",
            aide="Valeur et unité."),
        exo("1.6", "Écris l'équation horaire du mouvement (abscisse curviligne s comptée sur la trajectoire depuis la "
                   "position à t = 0).", [("v", nombre(math.hypot(2, 3), 0.01))],
            "<p>s = v·t + s<sub>0</sub> avec s<sub>0</sub> = 0 : <strong>s = 3,61 t</strong> (s en m, t en s).</p>",
            "<i>s</i>(<i>t</i>) = [[1]] · <i>t</i>"),
    ]
    ex2 = [
        exo("2.1", "Analyse les quatre phases : détermine la vitesse de la glissière pendant chacune.",
            [(f"v phase {i}", nombre(v)) for i, v in enumerate((1, 0, 1, -0.875), 1)],
            "<p>Phase 1 (0 à 5 s) : MRU, v = 5/5 = 1 ; phase 2 (5 à 15 s) : arrêt en x = 5, v = 0 ; phase 3 (15 à "
            "17 s) : MRU, v = 2/2 = 1 ; phase 4 (17 à 25 s) : MRU de retour, v = −7/8 = −0,875 (unités de longueur "
            "par seconde).</p>",
            tab(["Phase", "1", "2", "3", "4"], [("v", "[[1]]", "[[2]]", "[[3]]", "[[4]]")])),
        exo("2.2", "Détermine l'équation x(t) de chaque phase, exprimée dans le repère absolu (t = 0 au départ).",
            [("phase 1 : v", nombre(1)), ("phase 1 : x0", nombre(0)), ("phase 2 : v", nombre(0)), ("phase 2 : x0", nombre(5)),
             ("phase 3 : v", nombre(1)), ("phase 3 : x0", nombre(-10)), ("phase 4 : v", nombre(-0.875)),
             ("phase 4 : x0", nombre(21.875))],
            "<p>x = v·t + x<sub>0</sub> ; x<sub>0</sub> s'obtient avec un point de la phase. Phase 1 : x = t ; phase 2 : "
            "x = 5 ; phase 3 : x(15) = 5 = 15 + x<sub>0</sub>, x = t − 10 ; phase 4 : x(25) = 0 = −0,875 × 25 + "
            "x<sub>0</sub>, x = −0,875 t + 21,875.</p>",
            "".join(f'<p class="ch-l">Phase {i} : <i>x</i> = [[{2 * i - 1}]] · <i>t</i> + [[{2 * i}]]</p>' for i in range(1, 5))),
    ]
    ex3 = [
        exo("3.1", "Détermine l'équation horaire du mouvement du chariot.", [("v", nombre(50)), ("x0", nombre(-350))],
            "<p>v = Δx/Δt = (50 − (−100)) / (8 − 5) = 50 mm/s ; x(5) = −100 = 50 × 5 + x<sub>0</sub>, d'où "
            "<strong>x = 50 t − 350</strong> (mm, s). Graphe des espaces : une droite qui coupe l'axe des temps à "
            "t = 7 s ; graphe des vitesses : une horizontale à 50 mm/s.</p>",
            "<i>x</i>(<i>t</i>) = [[1]] · <i>t</i> + [[2]] <span class=\"ch-u\">(mm, s)</span>"),
        exo("3.3", "À partir des graphes, déduis l'espace parcouru entre t = 0 et t = 10 s.",
            [("espace", num(500, "mm", MM))],
            "<p>C'est l'aire sous le graphe des vitesses : 50 mm/s × 10 s = <strong>500 mm</strong> (le chariot va de "
            "x = −350 mm à x = 150 mm).</p>", aide="Valeur et unité."),
    ]
    tI = 166.667 / (12 + 13.333)
    ex4 = [
        exo("4.1 et 4.2", "Écris les équations horaires des mouvements 1 et 2. Lequel est le plus rapide ?",
            [("v1", nombre(3, 0.05)), ("v2", nombre(12, 0.1))],
            "<p>Les deux droites partent de A (origine) : x<sub>1</sub> = 3 t et x<sub>2</sub> = 12 t (mm, s). Le "
            "mouvement 2 est le plus rapide : la pente de sa droite (sa vitesse, 12 mm/s) est plus forte.</p>",
            "<i>x</i><sub>1</sub> = [[1]] · <i>t</i> ; <i>x</i><sub>2</sub> = [[2]] · <i>t</i>"),
        exo("4.3", "Quelle est la particularité du mouvement 3 ? Écris son équation horaire.",
            [("v3", nombre(10, 0.1)), ("x03", nombre(100, 1))],
            "<p>Le mouvement 3 ne part pas de l'origine : à t = 0, le solide est en B, à 100 mm. x<sub>3</sub> = "
            "<strong>10 t + 100</strong> (mm, s).</p>",
            "<i>x</i><sub>3</sub> = [[1]] · <i>t</i> + [[2]]"),
        exo("4.4", "Quelle est la particularité du mouvement 4 ? Écris son équation horaire, phase par phase.",
            [("CD : v", nombre(-80 / 6, 0.1)), ("CD : x0", nombre(140 + 80 / 3, 1)), ("DE : x", nombre(60, 0.5)),
             ("EF : v", nombre(-60, 0.5)), ("EF : x0", nombre(720, 5))],
            "<p>Le mouvement 4 commence à t = 2 s, en C (140 mm), et se fait en trois phases : retour à vitesse "
            "constante de C à D, arrêt de D à E, retour rapide de E à F. CD : x = −13,33 t + 166,67 (2 ≤ t ≤ 8 s) ; "
            "DE : x = 60 mm (8 ≤ t ≤ 11 s) ; EF : x = −60 t + 720 (11 ≤ t ≤ 12 s).</p>",
            '<p class="ch-l">De C à D : <i>x</i> = [[1]] · <i>t</i> + [[2]]</p><p class="ch-l">De D à E : <i>x</i> = '
            '[[3]]</p><p class="ch-l">De E à F : <i>x</i> = [[4]] · <i>t</i> + [[5]]</p>'),
        exo("4.5", "Détermine par le calcul l'instant et la position de l'intersection des mouvements 2 et 4.",
            [("instant", num(tI, "s", S_)), ("position", num(12 * tI, "mm", MM))],
            f"<p>12 t = −13,33 t + 166,67, soit 25,33 t = 166,67 : <strong>t = {nb(tI, 2)} s</strong>, en "
            f"x = 12 × {nb(tI, 3)} = <strong>{nb(12 * tI, 1)} mm</strong>. Sur le graphe, les deux droites se coupent "
            "entre C et D, un peu avant t = 7 s.</p>",
            "<i>t</i> = [[1]] ; <i>x</i> = [[2]]", "Valeurs et unités."),
    ]
    graphes = schema("ca-sch-mru", [
        {"titre": "Graphe des espaces", "y": "x", "courbes": [([(0, 0.25), (1, 0.9)], "#B42318")],
         "notes": [(-0.02, 0.25, "x₀", "end"), (0.62, 0.78, "pente v", "middle")]},
        {"titre": "Graphe des vitesses", "y": "v", "courbes": [([(0, 0.6), (1, 0.6)], "#1F5FA8")],
         "notes": [(-0.02, 0.6, "v", "end"), (0.5, 0.25, "aire = distance", "middle")],
         "aire": [(0.15, 0), (0.15, 0.6), (0.85, 0.6), (0.85, 0)]},
        {"titre": "Graphe des accélérations", "y": "γ", "courbes": [([(0, 0.0), (1, 0.0)], "#1B7A43")],
         "v0": 0, "notes": [(0.5, 0.12, "γ = 0", "middle")]}], "Graphes du mouvement rectiligne uniforme")
    return f"""
<p>Le solide S se déplace suivant une trajectoire rectiligne (A, {Y_}) ; il y a déplacement, donc {VM('V')} ≠ {vec('0')}.</p>
<div class="def"><p><strong>MRU</strong> : la trajectoire est une droite et le vecteur vitesse est constant :
{VM('V')} = constante ≠ {vec('0')}.</p></div>
<div class="cours-split"><div><h3>Caractéristiques</h3>
{formule("γ = 0 ; v = constante ; x = v·t + x<sub>0</sub>", "équation horaire (abscisse curviligne) ; x<sub>0</sub> : position à t = 0")}
</div><div><h3>Les vecteurs</h3>
<ul><li>position : {OM} = (v·t + x<sub>0</sub>)·{Y_} ;</li><li>vitesse : {VM('V')} = v·{Y_} ;</li>
<li>accélération : {VM('Γ')} = {vec('0')}.</li></ul></div></div>
<h3>Graphiquement</h3>{graphes}
<p class="simu-note">Le graphe des espaces est une droite dont la pente est la vitesse ; l'aire sous le graphe des
vitesses, entre deux instants, est la distance parcourue.</p>
<h3>Applications</h3>
<h4>Mouvement 1 — dans R (O, {X_}, {Y_}, {vec('z')}), {OM} : x = 2t ; y = 3t − 5 ; z = 0 (m, s)</h4>{"".join(ex1)}
<h4>Mouvement 2 — le mouvement d'une liaison glissière est défini par son graphe des espaces</h4>
{graphe_mru2(A)}{"".join(ex2)}
<h4>Mouvement 3 — un chariot de machine-outil en MRU : x = −100 mm à t = 5 s, x = 50 mm à t = 8 s</h4>{"".join(ex3)}
<h4>Mouvement 4 — caractéristiques de quatre mouvements d'après leur graphe des positions</h4>
{graphe_mru4(A)}{"".join(ex4)}
"""


# ====================================================================== 9. MRUV
def mruv(simu):
    graphes = schema("ca-sch-mruv", [
        {"titre": "Graphe des espaces", "y": "x", "courbes": [(parabole(0.55, 0.2, 0.2), "#B42318")],
         "notes": [(-0.02, 0.2, "x₀", "end"), (0.55, 0.85, "parabole", "middle")]},
        {"titre": "Graphe des vitesses", "y": "v", "courbes": [([(0, 0.25), (1, 0.85)], "#1F5FA8")],
         "notes": [(-0.02, 0.25, "v₀", "end"), (0.6, 0.85, "pente γ", "middle")],
         "aire": [(0, 0), (0, 0.25), (0.8, 0.73), (0.8, 0)]},
        {"titre": "Graphe des accélérations", "y": "γ", "courbes": [([(0, 0.6), (1, 0.6)], "#1B7A43")],
         "notes": [(-0.02, 0.6, "γ", "end")]}], "Graphes du mouvement rectiligne uniformément accéléré")
    acts = "".join([
        lien_activite("imprimante-3d", "Activité 1.1", "Imprimante 3D", "Mise en vitesse, ralentissement sur 25 mm, arrêt : "
                      "équations et graphes x, v, γ."),
        lien_activite("vanne-admission", "Activité 1.2", "Vanne d'admission d'air", "Cinq phases MRU et MRUV pour fermer "
                      "le boisseau sur 3 mm."),
        lien_activite("agv", "Activité 1.3", "Automotrice à grande vitesse", "De 0 à 360 km/h en trois phases uniformément "
                      "accélérées.")])
    return f"""
<p>Le solide S se déplace suivant une trajectoire rectiligne (A, {Y_}) ; il y a déplacement, donc {VM('V')} ≠ {vec('0')}.</p>
<div class="def"><p><strong>MRUV</strong> : la trajectoire est une droite et l'accélération est constante :
{VM('Γ')} = constante ≠ {vec('0')}.</p></div>
<div class="cours-split"><div><h3>Caractéristiques</h3>
<p>Conditions initiales à t = 0 : position x<sub>0</sub>, vitesse v<sub>0</sub> ; accélération γ.</p>
{formule("x = ½·γ·t² + v<sub>0</sub>·t + x<sub>0</sub>", "équation horaire")}
{formule("v = γ·t + v<sub>0</sub> ; γ = constante", "équation de vitesse")}
{formule("v² − v<sub>0</sub>² = 2·γ·(x − x<sub>0</sub>)", "sans le temps")}
</div><div><h3>Les vecteurs</h3>
<ul><li>position : {OM} = (½·γ·t² + v<sub>0</sub>·t + x<sub>0</sub>)·{Y_} ;</li>
<li>vitesse : {VM('V')} = (γ·t + v<sub>0</sub>)·{Y_} ;</li><li>accélération : {VM('Γ')} = γ·{Y_}.</li></ul>
<div class="remarque"><p>Mouvement <strong>accéléré</strong> si γ et v sont de même signe, <strong>décéléré</strong>
(ralenti) s'ils sont de signes contraires.</p></div></div></div>
<h3>Graphiquement</h3>{graphes}
<div class="cours-split"><div class="remarque"><p><strong>Distance parcourue</strong> : c'est l'aire sous le graphe des
vitesses. En MRUV, la vitesse moyenne sur une phase vaut (v<sub>début</sub> + v<sub>fin</sub>) / 2 :
d = (v<sub>début</sub> + v<sub>fin</sub>) / 2 × Δt.</p></div>
<div class="remarque"><p><strong>Mouvement en plusieurs phases</strong> : on peut écrire les équations d'une phase en
plaçant l'origine des temps au début de la phase (t' = t − t<sub>début</sub> ; x<sub>0</sub> et v<sub>0</sub> sont alors
la position et la vitesse au début de la phase), ou dans le repère absolu (t = 0 au départ) en écrivant la continuité
de la position et de la vitesse au début de la phase.</p></div></div>
{simu}
<h3>Applications : études de systèmes</h3><div class="ca-acts">{acts}</div>
"""


# ====================================================================== 10. mouvement circulaire
FIG_MC = """<figure class="simu-fig ca-fig" style="width:340px"><svg viewBox="0 0 360 250" role="img" aria-label="Trajectoire circulaire de centre O et de rayon R : origine L, point M, arc s et angle θ">
<defs><marker id="ca-mc-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 10,5 0,10z" fill="context-stroke"/></marker></defs>
<line x1="40" y1="125" x2="320" y2="125" stroke="#A5ADAA"/><line x1="180" y1="235" x2="180" y2="12" stroke="#A5ADAA"/>
<circle cx="180" cy="125" r="95" fill="none" stroke="#1C2530" stroke-width="2.4"/>
<path d="M180,220 A95,95 0 0 0 262,172" fill="none" stroke="#B42318" stroke-width="6" opacity=".55"/>
<path d="M180,165 A40,40 0 0 0 208,153" fill="none" stroke="#1F5FA8" stroke-width="2.2" marker-end="url(#ca-mc-f)"/>
<line x1="180" y1="125" x2="180" y2="220" stroke="#46525C" stroke-width="1.5"/><line x1="180" y1="125" x2="262" y2="172" stroke="#46525C" stroke-width="1.5"/>
<circle cx="180" cy="220" r="5" fill="#1C2530"/><circle cx="262" cy="172" r="5" fill="#1F5FA8"/>
<g font-size="15" font-weight="700"><text x="164" y="118">O</text><text x="166" y="240">L</text><text x="270" y="182">M</text>
<text x="226" y="216" fill="#B42318">s</text><text x="200" y="182" fill="#1F5FA8">θ</text><text x="300" y="118" font-weight="400">x</text>
<text x="186" y="22" font-weight="400">y</text><text x="226" y="128" font-weight="400" font-size="13">R</text></g></svg></figure>"""


def circulaire(A, simu, essentiel):
    w3 = 1650 * 2 * PI / 60
    vM = 0.3 * w3
    gM = 0.3 * w3 ** 2
    w1 = w3 * 360 / 120
    trans = [
        exo("2.1", "Détermine la vitesse angulaire de l'arbre qui porte le volant.", [("ω", num(w3, "rad/s", RADS))],
            f"<p>ω<sub>3</sub> = 2π·N / 60 = 2π × 1 650 / 60 = <strong>{nb(w3, 2)} rad/s</strong>.</p>",
            aide="Valeur et unité."),
        exo("2.2", "Calcule la vitesse linéaire d'un point M situé sur la périphérie du volant.",
            [("V", num(vM, "m/s", MS))],
            f"<p>V = R·ω = 0,300 × {nb(w3, 2)} = <strong>{nb(vM, 2)} m/s</strong> (le volant a un diamètre de 600 mm).</p>",
            aide="Valeur et unité."),
        exo("2.3", "Quelle est l'accélération de ce point M ?", [("Γ", num(gM, "m/s²", MS2, 0.01))],
            f"<p>La rotation est uniforme : Γ<sub>t</sub> = 0 et ‖Γ‖ = |Γ<sub>n</sub>| = R·ω² = 0,3 × {nb(w3, 2)}² ≈ "
            f"<strong>{nb(gM, 0)} m/s²</strong>, dirigée vers l'axe (plus de 900 fois l'accélération de la pesanteur).</p>",
            aide="Valeur et unité (norme)."),
        exo("2.4", "Quelle est la vitesse angulaire de la poulie motrice (1), en sortie du réducteur ?",
            [("ω1", num(w1, "rad/s", RADS))],
            f"<p>La courroie ne glisse pas : elle a la même vitesse sur les deux poulies, ω<sub>1</sub>·R<sub>1</sub> = "
            f"ω<sub>2</sub>·R<sub>2</sub>, et la poulie (2) tourne avec le volant. ω<sub>1</sub> = {nb(w3, 2)} × 360/120 = "
            f"<strong>{nb(w1, 1)} rad/s</strong> (4 950 tr/min). La vitesse du moteur lui-même dépend en plus du rapport "
            "du réducteur, non donné.</p>", aide="Valeur et unité."),
    ]
    graphes = schema("ca-sch-mcu", [
        {"titre": "Graphe de l'abscisse angulaire", "y": "θ", "courbes": [([(0, 0.15), (1, 0.9)], "#B42318")],
         "notes": [(-0.02, 0.15, "θ₀", "end"), (0.62, 0.78, "pente ω", "middle")]},
        {"titre": "Graphe de la vitesse angulaire", "y": "ω", "courbes": [([(0, 0.6), (1, 0.6)], "#1F5FA8")],
         "notes": [(-0.02, 0.6, "ω", "end"), (0.5, 0.28, "aire = angle parcouru", "middle")],
         "aire": [(0.15, 0), (0.15, 0.6), (0.85, 0.6), (0.85, 0)]}], "Graphes du mouvement circulaire uniforme")
    return f"""
<p>Sur une trajectoire circulaire (mouvement de rotation d'axe fixe), la position d'un point M se repère de deux
manières, à partir d'une position d'origine L.</p>
<div class="cours-split"><div>
<h3>Repérage par l'abscisse curviligne</h3>
<p>L'abscisse curviligne est la longueur de l'arc parcouru sur la trajectoire : s = arc LM, en mètres, fonction du
temps. La vitesse est v = ds/dt (m/s) et l'accélération tangentielle Γ<sub>t</sub> = dv/dt (m/s²).</p>
<h3>Repérage par l'abscisse angulaire</h3>
<p>L'abscisse angulaire est l'angle parcouru : θ = angle (OL, OM), en radians, fonction du temps. La vitesse angulaire
est ω = θ' = dθ/dt (rad/s), l'accélération angulaire θ'' = dω/dt (rad/s²).</p>
</div>{FIG_MC}</div>
<h3>Relation entre abscisse curviligne et abscisse angulaire</h3>
<div class="cours-split"><div>{formule("s = R·θ", "θ en rad, R et s en m")}</div>
<div>{formule("v = R·θ' = R·ω ; Γ<sub>t</sub> = R·θ''", "ω = 2π·N / 60, N en tr/min")}</div></div>
<h3>Mouvement circulaire uniforme (MCU)</h3>
<p>Le solide S est en liaison pivot d'axe (A, {vec('z')}) ; il y a mouvement, donc θ' ≠ 0.</p>
<div class="def"><p><strong>MCU</strong> : la trajectoire est un cercle et la vitesse angulaire est constante :
θ' = ω = constante ≠ 0.</p></div>
<div class="cours-split"><div>
{formule("θ'' = 0 ; θ' = ω = constante ; θ = ω·t + θ<sub>0</sub>", "équation horaire (abscisse angulaire)")}
</div><div><ul><li>vecteur vitesse : {VM('V')} = R·θ'·{T_}, tangent au cercle ;</li>
<li>vecteur accélération : {VM('Γ')} = −R·θ'²·{N_}, dirigé vers le centre ({N_} orienté vers l'extérieur) ; sa norme
R·ω² = v²/R n'est pas nulle.</li></ul></div></div>
{graphes}
<h3>Mouvement circulaire uniformément varié (MCUV)</h3>
<p>θ'' = constante ≠ 0 : ω = θ''·t + ω<sub>0</sub> ; θ = ½·θ''·t² + ω<sub>0</sub>·t + θ<sub>0</sub> ;
ω² − ω<sub>0</sub>² = 2·θ''·(θ − θ<sub>0</sub>). L'accélération a deux composantes :
{VM('Γ')} = R·θ''·{T_} − R·θ'²·{N_}. Mouvement <strong>accéléré</strong> si Γ<sub>t</sub> est dans le sens de la
vitesse, <strong>décéléré</strong> sinon ; Γ<sub>n</sub> est toujours dirigée vers le centre.</p>
{simu}
<h3>Application : transmission de puissance</h3>
<div class="cours-split"><div>
<p>La figure représente une partie de la transmission de puissance d'une machine. Le volant d'inertie (3), de diamètre
600 mm, tourne à 1 650 tr/min. L'arbre qui le supporte est entraîné par une transmission par courroie, supposée sans
glissement : la poulie (1), en sortie du moteur et de son réducteur, a un diamètre de 120 mm, la poulie réceptrice (2)
un diamètre de 360 mm.</p>{"".join(trans)}</div>
{A.figure("photo-transmission", "Moteur, réducteur, poulie (1) de diamètre 120 mm, courroie, poulie (2) de diamètre 360 mm et volant (3) de diamètre 600 mm", "Transmission par courroie et volant d'inertie.", 380)}</div>
<h3>Application : étude de système</h3><div class="ca-acts">{lien_activite("moteur-electrique", "Activité 1.4", "Moteur électrique", "Du graphe de l'espace angulaire aux équations de chaque phase et au graphe des vitesses angulaires.")}</div>
<h3>L'essentiel à retenir</h3>{essentiel}
"""


QUIZ = [
    ("Dans un mouvement rectiligne uniforme, le graphe des espaces x(t) est…", ["une droite", "une parabole", "une horizontale"], 0,
     "x = v·t + x0 : une droite de pente v (horizontale seulement à l'arrêt)."),
    ("Un mobile en MRUV passe de 10 m/s à 30 m/s en 4 s. Son accélération vaut :", ["2,5 m/s²", "5 m/s²", "10 m/s²"], 1,
     "γ = Δv / Δt = 20 / 4 = 5 m/s²."),
    ("Entre deux instants, la distance parcourue est…", ["la pente du graphe v(t)", "l'aire sous le graphe v(t)", "l'aire sous le graphe x(t)"], 1,
     "v × Δt sur chaque petit intervalle : l'aire sous la courbe des vitesses."),
    ("Une phase commence à t = 2 s. En plaçant l'origine des temps au début de la phase, on pose :", ["t' = t + 2", "t' = 2·t", "t' = t − 2"], 2,
     "t' = t − t<sub>début</sub> : t' vaut 0 au début de la phase."),
    ("Abscisse curviligne s et abscisse angulaire θ d'un point sur un cercle de rayon R :", ["s = R·θ", "s = θ / R", "s = R·θ²"], 0,
     "La longueur d'un arc est le rayon multiplié par l'angle en radians."),
    ("Un point à 0,3 m de l'axe tourne à ω = 10 rad/s constante. Son accélération vaut :", ["0", "3 m/s²", "30 m/s²"], 2,
     "MCU : Γt = 0 mais ‖Γn‖ = R·ω² = 0,3 × 100 = 30 m/s², vers le centre."),
    ("Un MRUV est décéléré lorsque…", ["γ est négative", "γ et v sont de signes contraires", "v est négative"], 1,
     "C'est le signe relatif de γ et de v qui compte : γ < 0 avec v < 0, c'est un mouvement accéléré."),
]


CSS = """
.ca-schema svg text{font-family:var(--f-texte)}
.ca-fig{max-width:100%; flex:0 1 auto}
.ca-acts{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:10px; margin:8px 0 12px}
.ca-act{display:flex; flex-direction:column; gap:4px; padding:10px 14px; border:2px solid var(--encre); border-left:8px solid var(--vert); background:#fff; color:var(--encre); text-decoration:none}
.ca-act:hover{background:var(--jaune-pale)}
.ca-act b{font:700 1.05rem var(--f-titre)}
.ca-act span:last-child{font-size:.9rem; color:var(--encre-2)}
.ca-act .mc-tag{align-self:flex-start}
.ca-l-def{font:600 1.02rem var(--f-texte); margin:6px 0}
.ca-l-tab{overflow-x:auto}
.ca-l-tab table{margin:6px 0; font-size:.88rem}
.ca-l-tab td,.ca-l-tab th{text-align:center; padding:3px 7px; white-space:nowrap}
"""

JS = r"""
  /* ---------------------------------------------------------------- cours 1 : laboratoire des quatre mouvements */
  function initLaboMouvements(root, el, fleche) {
    var box = root.querySelector("#ca-labo"); if (!box) return;
    var g = box.querySelector(".ca-l-monde"), tr = box.querySelector(".ca-l-tr"), an = box.querySelector(".ca-l-anim"), vv = box.querySelector(".ca-l-vec");
    var PI = Math.PI, cur = 1;
    function c(v) { return function () { return v; }; }
    var M = {
      1: { def: "x = 3t + 1 ; y = 1 (mm, s)", x: function (t) { return 3 * t + 1; }, y: c(1), vx: c(3), vy: c(0), ax: c(0), ay: c(0),
           t0: 0, t1: 5, ti: 1, inst: [0, 1, 2, 3, 4, 5], lab: ["0", "1", "2", "3", "4", "5"], b: [-1, -3, 18, 5], pas: 1, kv: 1, kg: 1, u: ["mm", "mm/s", "mm/s²"],
           obs: "Trajectoire : la droite y = 1. Les positions sont équidistantes à intervalles de temps égaux ; vitesse constante (3 mm/s), accélération nulle : mouvement rectiligne uniforme." },
      2: { def: "x = 3t² + 1 ; y = t² − 1 (mm, s)", x: function (t) { return 3 * t * t + 1; }, y: function (t) { return t * t - 1; },
           vx: function (t) { return 6 * t; }, vy: function (t) { return 2 * t; }, ax: c(6), ay: c(2),
           t0: 0, t1: 2, ti: 1.5, inst: [0, 0.5, 1, 1.5, 2], lab: ["0", "0,5", "1", "1,5", "2"], b: [-1, -3, 16, 5], pas: 1, kv: 0.35, kg: 0.5, u: ["mm", "mm/s", "mm/s²"],
           obs: "Trajectoire : la droite y = (x − 4)/3, parcourue de (1 ; −1) à (13 ; 3) entre 0 et 2 s (12,65 mm). Les positions s'écartent de plus en plus : la vitesse croît proportionnellement au temps (‖V‖ = 2√10·t), l'accélération est constante (‖Γ‖ = 6,32 mm/s²) et portée par la trajectoire : mouvement rectiligne uniformément accéléré." },
      3: { def: "x = cos t ; y = sin t (mm, s)", x: Math.cos, y: Math.sin, vx: function (t) { return -Math.sin(t); }, vy: Math.cos,
           ax: function (t) { return -Math.cos(t); }, ay: function (t) { return -Math.sin(t); },
           t0: 0, t1: 2 * PI, ti: PI / 4, inst: [0, PI / 8, PI / 4, 3 * PI / 8, PI / 2], lab: ["0", "π/8", "π/4", "3π/8", "π/2"], b: [-1.7, -1.5, 1.9, 1.5], pas: 0.5, kv: 0.55, kg: 0.55, u: ["mm", "mm/s", "mm/s²"],
           obs: "Trajectoire : le cercle de centre O et de rayon 1 mm. ‖V‖ = 1 mm/s, constante : mouvement circulaire uniforme. La vitesse est tangente au cercle ; l'accélération, de norme 1 mm/s², est dirigée vers le centre (Γ = −OM) : elle n'est pas nulle, la direction de la vitesse change." },
      4: { def: "x = t + 1 ; y = ½ t² + 2", x: function (t) { return t + 1; }, y: function (t) { return t * t / 2 + 2; }, vx: c(1), vy: function (t) { return t; }, ax: c(0), ay: c(1),
           t0: -3, t1: 3.5, ti: 3, inst: [-2, 0, 3], lab: ["−2", "0", "3"], b: [-3, -0.5, 6, 9], pas: 1, kv: 0.8, kg: 1.2, u: ["", "", ""],
           obs: "Trajectoire : la parabole y = ½ (x − 1)² + 2, de sommet (1 ; 2) atteint à t = 0. V = (1 ; t) : composante horizontale constante, composante verticale croissante ; Γ = (0 ; 1) est constante, comme pour un projectile : elle n'est pas portée par la vitesse, la trajectoire est courbe." }
    };
    function n3(x) { return fr(x, Math.abs(x) < 100 ? 2 : 1); }
    function choisir(i) {
      cur = i; var m = M[i];
      Array.prototype.forEach.call(box.querySelectorAll("[data-lm]"), function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-lm") === i ? "true" : "false"); });
      tr.min = m.t0; tr.max = m.t1; tr.step = (m.t1 - m.t0) / 500; tr.value = m.ti;
      box.querySelector(".ca-l-def").textContent = "Mouvement " + i + " : " + m.def;
      box.querySelector(".ca-l-obs").textContent = m.obs;
      var h = "<table class=\"t\"><thead><tr><th>t</th><th>x</th><th>y</th><th>‖OM‖</th><th>x'</th><th>y'</th><th>‖V‖</th><th>x''</th><th>y''</th><th>‖Γ‖</th></tr></thead><tbody>";
      m.inst.forEach(function (t, k) {
        h += "<tr><th>" + m.lab[k] + "</th>" + [m.x(t), m.y(t), Math.hypot(m.x(t), m.y(t)), m.vx(t), m.vy(t), Math.hypot(m.vx(t), m.vy(t)), m.ax(t), m.ay(t), Math.hypot(m.ax(t), m.ay(t))]
          .map(function (v) { return "<td>" + n3(v) + "</td>"; }).join("") + "</tr>";
      });
      box.querySelector(".ca-l-tab").innerHTML = h + "</tbody></table>";
      dessin();
    }
    function dessin() {
      g.innerHTML = "";
      var m = M[cur], t = +tr.value, b = m.b, W = 720, H = 300;
      var k = Math.min(W / (b[2] - b[0]), H / (b[3] - b[1])), ox = 20 + (W - k * (b[2] - b[0])) / 2, oy = 15 + (H - k * (b[3] - b[1])) / 2;
      function P(x, y) { return [ox + (x - b[0]) * k, oy + (b[3] - y) * k]; }
      for (var gx = Math.ceil(b[0] / m.pas) * m.pas; gx <= b[2] + 1e-9; gx += m.pas) { var a1 = P(gx, b[1]), a2 = P(gx, b[3]); el(g, "line", { x1: a1[0], y1: a1[1], x2: a2[0], y2: a2[1], stroke: "#E6EBF1" }); }
      for (var gy = Math.ceil(b[1] / m.pas) * m.pas; gy <= b[3] + 1e-9; gy += m.pas) { var c1 = P(b[0], gy), c2 = P(b[2], gy); el(g, "line", { x1: c1[0], y1: c1[1], x2: c2[0], y2: c2[1], stroke: "#E6EBF1" }); }
      var o = P(0, 0), xa = P(b[2], 0), ya = P(0, b[3]);
      fleche(g, P(b[0], 0)[0], o[1], xa[0], xa[1], "#46525C", 1.5); fleche(g, o[0], P(0, b[1])[1], ya[0], ya[1], "#46525C", 1.5);
      el(g, "text", { x: xa[0] - 12, y: xa[1] - 6, "font-size": 14 }, "x"); el(g, "text", { x: ya[0] + 6, y: ya[1] + 14, "font-size": 14 }, "y");
      el(g, "text", { x: o[0] - 14, y: o[1] + 16, "font-size": 14, "font-weight": 700 }, "O");
      var pts = [];
      for (var i = 0; i <= 300; i++) { var u = m.t0 + (m.t1 - m.t0) * i / 300, q = P(m.x(u), m.y(u)); pts.push(q[0].toFixed(1) + "," + q[1].toFixed(1)); }
      el(g, "polyline", { points: pts.join(" "), fill: "none", stroke: "#1C2530", "stroke-width": 2.2 });
      m.inst.forEach(function (u, j) {
        var q = P(m.x(u), m.y(u));
        el(g, "circle", { cx: q[0], cy: q[1], r: 4.5, fill: "#fff", stroke: "#1C2530", "stroke-width": 2 });
        el(g, "text", { x: q[0] + 6, y: q[1] + (cur === 3 ? -8 : 18), "font-size": 12, fill: "#46525C" }, cur === 4 ? "t = " + m.lab[j] : "M" + j);
      });
      var M_ = P(m.x(t), m.y(t));
      el(g, "line", { x1: o[0], y1: o[1], x2: M_[0], y2: M_[1], stroke: "#B42318", "stroke-width": 1.5, "stroke-dasharray": "5 3" });
      if (vv.checked) {
        fleche(g, M_[0], M_[1], M_[0] + m.vx(t) * m.kv * k, M_[1] - m.vy(t) * m.kv * k, "#1F5FA8", 3.5);
        fleche(g, M_[0], M_[1], M_[0] + m.ax(t) * m.kg * k, M_[1] - m.ay(t) * m.kg * k, "#1B7A43", 3);
      }
      el(g, "circle", { cx: M_[0], cy: M_[1], r: 6, fill: "#B42318" });
      el(g, "text", { x: 30, y: 316, "font-size": 12, fill: "#46525C" }, "Bleu : vitesse V ; vert : accélération Γ (échelles différentes) ; rouge : position OM.");
      var u_ = m.u;
      box.querySelector(".ca-l-t").textContent = fr(t, 2) + " s";
      box.querySelector(".ca-l-p").textContent = n3(m.x(t)) + " ; " + n3(m.y(t)) + (u_[0] ? " " + u_[0] : "");
      box.querySelector(".ca-l-v").textContent = n3(m.vx(t)) + " ; " + n3(m.vy(t));
      box.querySelector(".ca-l-nv").textContent = n3(Math.hypot(m.vx(t), m.vy(t))) + (u_[1] ? " " + u_[1] : "");
      box.querySelector(".ca-l-g").textContent = n3(m.ax(t)) + " ; " + n3(m.ay(t)) + " ; " + n3(Math.hypot(m.ax(t), m.ay(t))) + (u_[2] ? " " + u_[2] : "");
    }
    Array.prototype.forEach.call(box.querySelectorAll("[data-lm]"), function (b) { b.addEventListener("click", function () { choisir(+b.getAttribute("data-lm")); }); });
    tr.addEventListener("input", dessin); vv.addEventListener("change", dessin);
    var last = 0;
    animer(function (s) {
      var dt = Math.min(0.05, s - last); last = s;
      if (!an.checked) return;
      var m = M[cur], t = +tr.value + dt * (m.t1 - m.t0) / 8;
      tr.value = t > m.t1 ? m.t0 : t; dessin();
    });
    choisir(1);
  }
"""
