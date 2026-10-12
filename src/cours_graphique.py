# -*- coding: utf-8 -*-
"""Cours 2 — Cinématique graphique : contenu, figures SVG, démonstrations pas à pas et bielle-manivelle vivante.

Sources : la séquence « Cinématique graphique » (parties 1 à 7, sans ses exercices, qui deviennent les activités
2.1 à 2.7) et la partie « mouvement plan » du chapitre « Cinématique » (équiprojectivité, centre instantané de
rotation). Les démonstrations pas à pas utilisent le moteur de l'atelier (src/atelier/atelier.js, classe Demo) ; les
tracés sont calculés ici (src/geometrie.py).
"""
import math

import geometrie as g
from atelier import Feuille, C_VE, C_DR, C_SG, C_CI, C_PT, C_TX
from cours_commun import course_head, course_section, course_nav, quiz_section, jeu_html, cartes, formule, frac, vec

V = vec("V")


def feuille_bielle():
    """Bielle-manivelle des démonstrations : manivelle 1 (O, A), bielle 2 (A, B), piston 3 (B), bâti 0."""
    F = Feuille(200, 118, "Système bielle-manivelle")
    O = (42.0, 74.0)
    A = g.add(O, g.polar(22, 52))
    L = 92.0
    B = (A[0] + math.sqrt(L * L - (A[1] - O[1]) ** 2), O[1])
    F.axe(O, (1, 0), -14, 150)
    F.cercle(O, 22, "axe")
    F.trait(O, g.add(O, (0, 10)), "tr")
    F.bati(g.add(O, (0, 10)), (0, -1), 12)
    for yy, n in ((O[1] - 9, (0, -1)), (O[1] + 9, (0, 1))):
        F.paroi((B[0] - 14, yy), (B[0] + 22, yy), n)
    F.glissiere(g.add(B, (4, 0)), (1, 0), 18, 16.6, "piece2")
    F.trait(O, A, "tr")
    u = g.unit(g.sub(B, A))
    n = g.perp(u)
    r = 3.6
    p1, p2, p3, p4 = g.add(A, g.mul(n, r)), g.add(B, g.mul(n, r)), g.sub(B, g.mul(n, r)), g.sub(A, g.mul(n, r))
    F.chemin(f"M{p1[0]:.2f},{p1[1]:.2f} L{p2[0]:.2f},{p2[1]:.2f} A{r},{r} 0 0 0 {p3[0]:.2f},{p3[1]:.2f} "
             f"L{p4[0]:.2f},{p4[1]:.2f} A{r},{r} 0 0 0 {p1[0]:.2f},{p1[1]:.2f} Z", "piece")
    for P in (O, A, B):
        F.pivot(P, 1.6)
    F.point("O", O, (-3.4, 4.6))
    F.point("A", A, (-2.6, -4.2))
    F.point("B", B, (0.5, 5.6))
    F.numero(g.add(O, (-13, -12)), "1", g.add(O, g.mul(g.sub(A, O), 0.5)))
    F.numero(g.add(A, g.add(g.mul(u, 45), g.mul(n, -13))), "2", g.add(A, g.add(g.mul(u, 45), g.mul(n, -3.6))))
    F.numero(g.add(B, (8, -16)), "3", g.add(B, (8, -8.3)))
    F.numero(g.add(O, (-14, 14)), "0", g.add(O, (-5, 10)))
    VA = g.vitesse_rotation(O, A, 30.0, "trigo")
    VB = g.equiprojectivite(A, VA, B, (1, 0))
    return F, O, A, B, VA, VB


def demo_equiprojectivite(A_):
    F, O, A, B, VA, VB = feuille_bielle()
    u = g.sub(B, A)
    ha = g.projete(g.add(A, VA), A, u)
    hb = g.add(B, g.sub(ha, A))
    etapes = [
        {"titre": "Tracer le vecteur vitesse connu", "texte": "V(A∈2/0) = V(A∈1/0) : A est le centre de la liaison pivot "
         "1/2 ; la manivelle tourne autour de O, la vitesse de A est perpendiculaire à (OA).",
         "prims": [C_SG(O, A), C_VE(A, VA, "V(A∈2/0)")]},
        {"titre": "Tracer le support du vecteur inconnu", "texte": "V(B∈2/0) = V(B∈3/0) : le piston (3) est en "
         "translation ; le support est l'axe du cylindre.", "prims": [C_DR(B, (1, 0), "res")]},
        {"titre": "Tracer la droite de projection (AB)", "texte": "Elle passe par le point dont la vitesse est connue et "
         "celui dont la vitesse est cherchée : A et B, deux points de la bielle (2).", "prims": [C_DR(A, u, "res")]},
        {"titre": "Projeter orthogonalement le vecteur connu", "texte": "De l'extrémité de V(A), on abaisse la "
         "perpendiculaire à (AB) : le segment [AA'] est la projection.", "prims": [C_SG(g.add(A, VA), ha, "aide"),
                                                                                    C_SG(A, ha, "res"), C_PT(ha, "A'")]},
        {"titre": "Reporter la projection au point B", "texte": "Même longueur, même sens : le segment [BB'].",
         "prims": [C_SG(B, hb, "res"), C_PT(hb, "B'")]},
        {"titre": "Tracer la perpendiculaire à (AB) en B'", "texte": "Toutes les vitesses de B dont la projection sur (AB) "
         "vaut [BB'] ont leur extrémité sur cette droite.", "prims": [C_DR(hb, g.perp(u), "res")]},
        {"titre": "Lire le vecteur cherché", "texte": f"L'intersection avec le support donne l'extrémité de V(B∈2/0) : "
         f"{A_.fr(g.norm(VB), 1)} mm, pour {A_.fr(g.norm(VA), 1)} mm en A.", "prims": [C_VE(B, VB, "V(B∈2/0)")]},
    ]
    return F, etapes


def demo_cir(A_):
    F, O, A, B, VA, VB = feuille_bielle()
    I = g.cir(A, VA, B, (1, 0))
    G = g.add(A, g.mul(g.sub(B, A), 0.5))
    VG = g.vitesse_par_cir(I, A, VA, G)
    u = g.unit(g.sub(A, I))
    G2 = g.add(I, g.mul(u, g.dist(I, G)))
    VG2 = g.mul(VA, g.dist(I, G) / g.dist(I, A))
    etapes = [
        {"titre": "Tracer les perpendiculaires aux deux supports connus", "texte": "En A, la perpendiculaire à V(A) est la "
         "droite (OA) ; en B, la perpendiculaire à l'axe du piston. Le CIR I2/0 est à leur intersection.",
         "prims": [C_VE(A, VA, "V(A∈2/0)", "aide"), C_DR(B, (1, 0)), C_DR(O, g.sub(A, O), "res"), C_DR(B, (0, 1), "res"),
                   C_PT(I, "I2/0")]},
        {"titre": "Direction de la vitesse d'un autre point", "texte": "Pour le milieu G de la bielle, la vitesse est "
         "perpendiculaire à (I G).", "prims": [C_SG(I, G, "res"), C_DR(G, g.perp(g.sub(G, I)))]},
        {"titre": "Tracer la droite de proportionnalité", "texte": "Elle passe par le CIR et l'extrémité du vecteur connu "
         "V(A).", "prims": [C_SG(I, g.add(A, g.mul(VA, 1.35)), "res")]},
        {"titre": "Reporter le point sur le rayon du vecteur connu", "texte": "Au compas, de centre I et de rayon IG : le "
         "point G' sur la droite (IA).", "prims": [C_CI(I, g.dist(I, G)), C_PT(G2, "G'")]},
        {"titre": "Tracer le vecteur et le reporter", "texte": "En G', perpendiculairement au rayon, jusqu'à la droite de "
         f"proportionnalité ; puis on le reporte en G, perpendiculaire à (IG) : {A_.fr(g.norm(VG), 1)} mm.",
         "prims": [C_VE(G2, VG2, "", "aide"), C_VE(G, VG, "V(G∈2/0)")]},
    ]
    return F, etapes


def demo_composition(A_):
    F = Feuille(160, 100, "Composition des vitesses")
    M = (52.0, 62.0)
    v12 = g.mul(g.polar(1, 24), 44)
    d13, d23 = g.polar(1, -4), g.polar(1, -32)
    F.point("M", M, (-2, 5.5))
    F.add(f'<circle cx="{M[0]}" cy="{M[1]}" r="1.4" class="flp"/>')
    x13, my23 = g.composition(v12, d13, g.mul(d23, -1))
    v13, v23 = x13, g.mul(my23, -1)
    etapes = [
        {"titre": "Tracer le vecteur connu", "texte": "V(M∈1/2), entièrement connu (point, direction, sens, norme).",
         "prims": [C_VE(M, v12, "V(M∈1/2)")]},
        {"titre": "Tracer les supports des deux vecteurs inconnus", "texte": "Supports de V(M∈1/3) et de V(M∈2/3), connus "
         "par la nature des mouvements.", "prims": [C_DR(M, d13, "res"), C_DR(M, d23, "res"),
                                                    C_TX(g.add(M, g.add(g.mul(d13, 70), (0, -3))), "support de V(M∈1/3)"),
                                                    C_TX(g.add(M, g.add(g.mul(d23, 60), (2, 4))), "support de V(M∈2/3)")]},
        {"titre": "Par l'extrémité du vecteur connu, tracer la parallèle", "texte": "V(M∈1/3) = V(M∈1/2) + V(M∈2/3) : on "
         "met V(M∈2/3) bout à bout avec V(M∈1/2) ; sa direction part donc de l'extrémité de V(M∈1/2).",
         "prims": [C_DR(g.add(M, v12), d23)]},
        {"titre": "L'intersection donne V(M∈1/3)", "texte": "La parallèle coupe le support de V(M∈1/3) : c'est l'extrémité "
         f"du vecteur somme ({A_.fr(g.norm(v13), 1)} mm).", "prims": [C_VE(M, v13, "V(M∈1/3)")]},
        {"titre": "Lire V(M∈2/3)", "texte": "Il va de l'extrémité de V(M∈1/2) à celle de V(M∈1/3) ; on le reporte en M.",
         "prims": [C_VE(g.add(M, v12), v23, "", "aide"), C_VE(M, v23, "V(M∈2/3)")]},
    ]
    return F, etapes


def demo(A_, ident, fn, titre):
    F, etapes = fn(A_)
    A_.ATELIERS[ident] = A_.atelier.demo_config(F, etapes, "Situation de départ",
                                                "Les données sont sur la figure ; avance étape par étape.")
    return A_.atelier.render_demo(ident, F, etapes, titre)


def render(A):
    H = A.HOUSE
    sections = [("cg-intro", "Introduction"), ("cg-mouvements", "Mouvements et trajectoires"),
                ("cg-vecteur", "Vecteur vitesse"), ("cg-plan", "Cinématique dans le plan"),
                ("cg-equi", "Équiprojectivité"), ("cg-cir", "Centre instantané de rotation"),
                ("cg-composition", "Composition des vitesses"), ("cg-bielle", "Bielle-manivelle vivante"),
                ("cg-methode", "Choisir sa méthode"), ("cg-quiz", "Quiz")]
    s = []
    s.append(course_section(1, "cg-intro", "Introduction", """
<p>Le comportement mécanique d'une structure est conditionné par une géométrie, un ou des matériaux, des mouvements, des
efforts appliqués et des déformations qui en découlent. Prédire et maîtriser le comportement mécanique d'un système,
c'est maîtriser la relation entre tous ces éléments.</p>
<figure class="simu-fig" style="max-width:720px"><svg viewBox="0 0 720 300" role="img" aria-label="Relations entre accélération, effort, matériaux, vitesse et géométrie : dynamique, statique, résistance des matériaux, cinématique">
<g stroke="#1C2530" stroke-width="2" fill="none"><line x1="180" y1="70" x2="150" y2="200"/><line x1="180" y1="70" x2="420" y2="60"/><line x1="420" y1="60" x2="440" y2="230"/>
<line x1="150" y1="200" x2="440" y2="230"/><line x1="160" y1="225" x2="420" y2="250"/><line x1="460" y1="80" x2="610" y2="120"/><line x1="610" y1="120" x2="470" y2="235"/>
<line x1="450" y1="80" x2="450" y2="215"/><line x1="410" y1="85" x2="430" y2="215"/></g>
<g font-family="system-ui,Arial,sans-serif" font-weight="700" font-size="16" text-anchor="middle">
<ellipse cx="160" cy="55" rx="80" ry="27" fill="#E8A3A6"/><text x="160" y="61">Accélération</text>
<ellipse cx="430" cy="55" rx="70" ry="27" fill="#F8C79A"/><text x="430" y="61">Effort</text>
<ellipse cx="625" cy="125" rx="80" ry="27" fill="#D6CDA4"/><text x="625" y="131">Matériaux</text>
<ellipse cx="140" cy="210" rx="70" ry="27" fill="#9BCDEB"/><text x="140" y="216">Vitesse</text>
<ellipse cx="440" cy="240" rx="80" ry="27" fill="#C6DE9F"/><text x="440" y="246">Géométrie</text></g>
<g font-family="system-ui,Arial,sans-serif" font-style="italic" font-size="15" text-anchor="middle">
<text x="105" y="135">Dynamique</text><text x="470" y="150">Statique</text><text x="590" y="200">Résistance des</text><text x="590" y="218">matériaux</text>
<text x="290" y="275" fill="#1F5FA8" font-weight="700">Cinématique</text></g></svg>
<figcaption>La cinématique relie la géométrie d'un mécanisme aux vitesses de ses points.</figcaption></figure>
<p><strong>Objectifs</strong> : représenter graphiquement la vitesse ; utiliser les propriétés cinématiques des
mouvements pour déterminer les vitesses des différents points d'un solide ; savoir appliquer les méthodes de
l'équiprojectivité, du CIR et de la loi de composition. Le <a href="?ex=atelier-libre">atelier de construction</a>
permet de s'y exercer, les activités 2.1 à 2.7 de les appliquer.</p>
"""))
    jeu_traj = jeu_html([("Rotation", "cc"), ("Translation circulaire", "cr"), ("Translation rectiligne", "dp"),
                         ("Translation curviligne", "ci"), ("Mouvement plan", "cq")],
                        [("cc", "Cercles concentriques"), ("cr", "Cercles de même rayon"), ("dp", "Droites parallèles"),
                         ("ci", "Courbes identiques"), ("cq", "Courbes quelconques")], "cg-jeu-traj")
    jeu_dir = jeu_html([("Rotation", "pr"), ("Translation circulaire", "id"), ("Translation rectiligne", "id"),
                        ("Translation curviligne", "id"), ("Mouvement plan", "tg")],
                       [("pr", "Perpendiculaire au rayon"), ("id", "La même pour tous les points"),
                        ("tg", "Différente d'un point à l'autre")], "cg-jeu-dir")
    s.append(course_section(2, "cg-mouvements", "Rappels : mouvements et trajectoires", f"""
<p>Un solide est en mouvement dès l'instant où les coordonnées d'un point de ce solide changent en fonction du temps.
Lorsqu'un solide se déplace, chaque point décrit une courbe : sa <strong>trajectoire</strong>, en relation directe avec
le mouvement de la pièce. On la note <strong>T<sub>A∈1/2</sub></strong> : trajectoire du point A appartenant au solide
(1), dans son mouvement par rapport au solide (2), qui sert de référentiel.</p>
<h3>Les mouvements dans le plan</h3>
<p>Il existe trois types de mouvement : la <strong>translation</strong> (rectiligne, circulaire ou curviligne), la
<strong>rotation</strong> et le <strong>mouvement plan</strong>. Pour caractériser la translation, on utilise les
<strong>vecteurs équipollents</strong> : des vecteurs sont équipollents si, au cours du temps, ils gardent la même
direction, le même sens et la même norme. Dans une translation, n'importe quel segment du solide reste équipollent à
lui-même au cours du déplacement.</p>
<div class="simu" id="cg-mvt"><h3>La même pièce, cinq mouvements</h3>
<div class="simu-btns"><button type="button" class="btn ghost" data-m="ro" aria-pressed="true">Rotation</button>
<button type="button" class="btn ghost" data-m="tc" aria-pressed="false">Translation circulaire</button>
<button type="button" class="btn ghost" data-m="tr" aria-pressed="false">Translation rectiligne</button>
<button type="button" class="btn ghost" data-m="tq" aria-pressed="false">Translation curviligne</button>
<button type="button" class="btn ghost" data-m="pl" aria-pressed="false">Mouvement plan</button></div>
<div class="simu-fig"><svg viewBox="0 0 760 340" role="img" aria-label="Pièce en mouvement ; trajectoires de trois de ses points et leurs vecteurs vitesse"><g class="cg-m-monde"></g></svg></div>
<p class="simu-note">Trois points de la pièce laissent leur trace (rouge, vert, bleu) ; les flèches sont leurs
vecteurs vitesse à l'instant affiché.</p></div>
<h3>Jeu : la nature des trajectoires</h3>{jeu_traj}
<h3>Jeu : la direction des vecteurs vitesse</h3>{jeu_dir}
<h3>Les mouvements relatifs</h3>
<p>Le mouvement est relatif : il faut une référence, un repère, pour le définir. Selon le référentiel choisi, le
mouvement d'une même pièce peut être différent. Un voyageur assis dans un train n'a pas de mouvement par rapport au
wagon ; il est en mouvement par rapport à l'extérieur (mouvement absolu) et par rapport à un autre train (mouvement
relatif). Voir l'animation du <a href="?ex=cours-cinematique-analytique#ca-referentiel">cours 1</a>.</p>
"""))
    s.append(course_section(3, "cg-vecteur", "Le vecteur vitesse", f"""
<p>Soit le point M, appartenant au solide S en mouvement dans le repère R, suivant la trajectoire T<sub>M∈S/R</sub> ; A
est l'origine du mouvement.</p>
<h3>Vitesse moyenne</h3>
<p>X<sub>1</sub> = arc AM<sub>1</sub> : distance parcourue à l'instant t<sub>1</sub> ; X<sub>2</sub> = arc AM<sub>2</sub> :
distance parcourue à l'instant t<sub>2</sub>.</p>
{formule("V<sub>moy</sub> = " + frac("X<sub>2</sub> − X<sub>1</sub>", "t<sub>2</sub> − t<sub>1</sub>"), "en m/s si X est en m et t en s")}
<h3>Représentation graphique</h3>
<div class="cours-split"><div>
<ul><li><strong>Notation</strong> : {V}(M∈S/R) ;</li><li><strong>origine</strong> : le point M ;</li>
<li><strong>direction</strong> : la tangente à la trajectoire en M ;</li><li><strong>sens</strong> : celui du mouvement ;</li>
<li><strong>norme</strong> : la valeur de la vitesse (m/s), tracée à l'<strong>échelle des vitesses</strong>.</li></ul>
<p><strong>Rappel géométrique</strong> : la tangente à une trajectoire rectiligne est la droite elle-même ; la tangente
à une trajectoire en arc de cercle est perpendiculaire au rayon.</p></div>
<div class="simu" id="cg-echelle"><h3>Échelle des vitesses</h3>
<div class="simu-grid" style="grid-template-columns:1fr 1fr"><label>Échelle : 10 mm pour <select class="cg-ech"><option value="0.02">0,02 m/s</option><option value="0.2">0,2 m/s</option>
<option value="1" selected>1 m/s</option><option value="5">5 m/s</option><option value="6">6 m/s</option></select></label>
<label>Vitesse <output class="cg-vo"></output><input type="range" class="cg-vr" min="0" max="100" step="1" value="52"></label></div>
<div class="simu-out" style="grid-template-columns:1fr 1fr"><div><span>Longueur à tracer</span><b class="cg-lo"></b></div><div><span>Règle</span><b class="cg-fo"></b></div></div>
<div class="simu-fig"><svg viewBox="0 0 400 60" role="img" aria-label="Vecteur tracé à l'échelle"><g class="cg-e-monde"></g></svg></div></div></div>
"""))
    s.append(course_section(4, "cg-plan", "Cinématique graphique dans le plan", f"""
<h3>Notion de mécanisme plan</h3>
<p>Les problèmes traités seront assimilés à des mouvements dans le plan : un mécanisme est supposé plan, d'un point de
vue cinématique, dès qu'on peut étudier tous ses mouvements en projection sur un même plan. Exemple : la bielle de moteur,
étudiée dans le plan (X, Y) qui contient l'axe du piston ; le carter (0) est fixe, le vilebrequin (1) tourne, la bielle (2)
a un mouvement plan, le piston (3) est en translation.</p>
<h3>Propriétés des mouvements simples</h3>
<div class="cours-split"><div><h4>Translation</h4>
<p>Un solide est en translation si et seulement si une droite (AB) de ce solide reste toujours parallèle à elle-même au
cours du temps. Les trajectoires de chaque point sont <strong>identiques (superposables)</strong> ; à un instant donné,
les vecteurs vitesse de tous les points sont <strong>égaux</strong> : même direction, même sens, même norme. Exemple :
une cabine de téléphérique : V(A∈cabine/sol) = V(B∈cabine/sol) = V(C∈cabine/sol).</p></div>
<div><h4>Rotation autour d'un axe fixe</h4>
<p>Les points de l'axe sont fixes ; les autres ont des trajectoires circulaires centrées sur l'axe. Le vecteur vitesse
d'un point est perpendiculaire au rayon, orienté selon le sens de rotation, et sa norme vaut :</p>
{formule("‖V(M)‖ = ω × R", "V en m/s ; ω en rad/s ; R en m (distance du point à l'axe)")}
<p>Exemple : une hélice d'avion ; les vitesses de ses points sont proportionnelles à leur distance à l'axe (voir le
<a href="?ex=cours-cinematique-analytique#ca-solide">simulateur du cours 1</a>).</p></div></div>
<h3>Solide indéformable</h3>
<p>Les solides étudiés étant supposés indéformables, le mouvement d'un point dépend forcément du mouvement des autres
points du solide. Ce lien apparaît graphiquement sur les vecteurs vitesse, par deux méthodes : l'<strong>équiprojectivité</strong>
et le <strong>centre instantané de rotation</strong>. Elles sont équivalentes ; l'une peut s'imposer à l'autre pour
des raisons pratiques dues au tracé (CIR hors de la feuille, droites presque parallèles…).</p>
"""))
    s.append(course_section(5, "cg-equi", "Équiprojectivité", f"""
<div class="def"><p>Soient deux points A et B d'un même solide (1) en mouvement plan par rapport à R0. La projection
orthogonale de {V}(A∈1/0) sur la droite (AB) est égale à la projection orthogonale de {V}(B∈1/0) : c'est
l'<strong>équiprojectivité</strong>. Les points de projection sont situés <em>du même côté</em> par rapport à A et à B.</p></div>
<p><strong>Conséquence</strong> : si la vitesse d'un point est totalement connue, on peut déterminer la vitesse d'un autre
point dont on connaît la direction. <strong>Remarque</strong> : les deux points doivent appartenir au même solide.</p>
<h3>Méthode graphique, pas à pas</h3>
{demo(A, "dm-equi", demo_equiprojectivite, "Équiprojectivité sur la bielle d'un système bielle-manivelle")}
<p class="simu-note">Ici V(A∈2/0) = V(A∈1/0), car A est le centre de la liaison entre (1) et (2) : ce vecteur est
perpendiculaire au rayon [OA]. V(B∈2/0) = V(B∈3/0), car B est le centre de la liaison entre (3) et (2) : ce vecteur
est parallèle à la direction de translation du piston.</p>
"""))
    s.append(course_section(6, "cg-cir", "Centre instantané de rotation (CIR)", f"""
<div class="def"><p>Pour tout solide en mouvement plan par rapport à R0, il existe à chaque instant un point I unique dont
la vitesse est nulle : V(I∈1/0) = <span class=vec>0</span>. Ce point I<sub>1/0</sub> est le <strong>centre instantané de rotation</strong> (CIR)
du mouvement de 1/0. Il se trouve à l'intersection des perpendiculaires aux vecteurs vitesse, menées par leurs points
d'application.</p></div>
<ul><li>Le CIR n'est pas fixe : il se déplace à chaque instant et n'est valable que pour l'instant t.</li>
<li>Il n'existe pas dans un mouvement de translation : on dit qu'il est rejeté à l'infini.</li>
<li>À l'instant t, tout se passe comme si le solide tournait autour d'un pivot fictif en I : on retrouve la
<strong>répartition linéaire (triangulaire) des vitesses</strong>.</li></ul>
<h3>Méthode graphique, pas à pas</h3>
{demo(A, "dm-cir", demo_cir, "Centre instantané de rotation de la bielle")}
<p class="simu-note">Conséquences : le CIR permet de déterminer la direction de la vitesse de n'importe quel point du
solide (perpendiculaire à IM) ; en traçant le champ des vecteurs vitesse sur un rayon, à partir d'une vitesse connue,
on détermine la vitesse de n'importe quel point.</p>
"""))
    s.append(course_section(7, "cg-composition", "Loi de composition des vitesses", f"""
<p>Soient trois repères : R<sub>0</sub> = (O<sub>0</sub>, <span class=vec>x</span><sub>0</sub>, <span class=vec>y</span><sub>0</sub>, <span class=vec>z</span><sub>0</sub>) lié au solide
fixe (0), R = (O, <span class=vec>x</span>, <span class=vec>y</span>, <span class=vec>z</span>) lié au solide étudié (S), et R<sub>1</sub> = (O<sub>1</sub>, <span class=vec>x</span><sub>1</sub>, <span class=vec>y</span><sub>1</sub>,
<span class=vec>z</span><sub>1</sub>) repère intermédiaire. Trois mouvements distincts peuvent être considérés :</p>
<ul><li>le mouvement de S par rapport à R<sub>0</sub> : mouvement <strong>absolu</strong> ;</li>
<li>le mouvement de S par rapport à R<sub>1</sub> : mouvement <strong>relatif</strong> ;</li>
<li>le mouvement de R<sub>1</sub> par rapport à R<sub>0</sub> : mouvement d'<strong>entraînement</strong>.</li></ul>
<p>La composition de mouvement est l'expression vectorielle du mouvement du solide S par rapport à un repère fixe, en
fonction des autres repères. Pour les vitesses d'un point M appartenant à S :</p>
{formule("V(M∈S/R<sub>0</sub>) = V(M∈S/R<sub>1</sub>) + V(M∈R<sub>1</sub>/R<sub>0</sub>)", "vitesse absolue = vitesse relative + vitesse d'entraînement")}
<p><strong>Généralisation</strong> : V(M∈R<sub>0</sub>/R<sub>n</sub>) = V(M∈R<sub>0</sub>/R<sub>1</sub>) +
V(M∈R<sub>1</sub>/R<sub>2</sub>) + … + V(M∈R<sub>n−1</sub>/R<sub>n</sub>). <strong>Cas simple</strong> :
V(M∈1/3) = V(M∈1/2) + V(M∈2/3) — les indices « s'enchaînent » comme dans la relation de Chasles.</p>
<h3>Construction graphique, pas à pas</h3>
{demo(A, "dm-compo", demo_composition, "Composition des vitesses : construction du parallélogramme")}
<p class="simu-note">Cas typique : un vérin. V(C∈tige/bâti) = V(C∈tige/corps) + V(C∈corps/bâti) : la vitesse de sortie de
la tige est portée par l'axe du vérin, celle du corps (qui pivote) lui est perpendiculaire. Activités 2.6 (chargeur) et
2.7 (VTT).</p>
"""))
    s.append(course_section(8, "cg-bielle", "Bielle-manivelle vivante", """
<p>La manivelle tourne à vitesse constante ; pour chaque position, la figure construit les vitesses de A et de B et le
CIR de la bielle. Fais tourner la manivelle et observe quand le CIR part à l'infini (bielle en translation instantanée)
ou quand la vitesse du piston s'annule (points morts).</p>
<div class="simu" id="cg-bm">
<div class="simu-grid"><label>Angle de la manivelle θ <output class="cg-bo"></output><input type="range" class="cg-br" min="0" max="360" step="1" value="52"></label>
<label><span><input type="checkbox" class="cg-ba"> Faire tourner</span></label>
<label><span><input type="checkbox" class="cg-be" checked> Équiprojectivité</span> <span><input type="checkbox" class="cg-bc" checked> CIR et champ des vitesses</span></label></div>
<div class="simu-fig"><svg viewBox="0 0 760 360" role="img" aria-label="Système bielle-manivelle : vitesses de A et B, CIR de la bielle, champ des vitesses"><g class="cg-b-monde"></g></svg></div>
<div class="simu-out"><div><span>V(A) : manivelle, constante</span><b>1,00</b></div><div><span>V(B) / V(A)</span><b class="cg-br2"></b></div>
<div><span>CIR I2/0</span><b class="cg-bi"></b></div><div><span>Piston</span><b class="cg-bp"></b></div></div>
<p class="simu-note">Manivelle OA = 60 mm, bielle AB = 200 mm (échelle de la figure), rotation dans le sens trigonométrique.</p></div>
"""))
    s.append(course_section(9, "cg-methode", "Choisir sa méthode", """
<table class="t cours-t"><thead><tr><th>Ce que l'on connaît</th><th>Méthode</th><th>Activités</th></tr></thead><tbody>
<tr><td>Un solide en rotation autour d'un axe fixe et la vitesse d'un de ses points (ou ω)</td><td>V = ω·R ; répartition linéaire</td><td>2.1</td></tr>
<tr><td>La vitesse complète d'un point A et la direction de la vitesse d'un point B du même solide</td><td>Équiprojectivité entre A et B</td><td>2.1, 2.2, 2.3, 2.7</td></tr>
<tr><td>Les directions des vitesses de deux points du même solide, et la norme de l'une</td><td>CIR, puis répartition linéaire</td><td>2.4, 2.5, 2.6, 2.7</td></tr>
<tr><td>Un point commun à trois solides (vérin, coulisseau sur une pièce mobile)</td><td>Composition des vitesses</td><td>2.6, 2.7</td></tr>
</tbody></table>
<p>Au centre d'une liaison pivot entre deux solides, les deux solides ont la même vitesse : c'est le passage obligé d'un
solide à l'autre.</p>
""" + cartes([("Équiprojectivité", "Deux points du même solide : mêmes projections des vitesses sur la droite qui les joint."),
              ("CIR", "Intersection des perpendiculaires aux vitesses ; vitesses proportionnelles à la distance au CIR."),
              ("Composition", "V(M∈1/3) = V(M∈1/2) + V(M∈2/3) : construction du parallélogramme."),
              ("Échelle", "Toujours tracer à l'échelle des vitesses et convertir la longueur mesurée en m/s.")])))
    quiz = [
        ("La trajectoire des points d'un solide en rotation est :", ["des droites parallèles", "des cercles concentriques", "des courbes quelconques"], 1,
         "Cercles centrés sur l'axe de rotation."),
        ("En translation, à un instant donné, les vitesses de tous les points sont :", ["égales", "proportionnelles à la distance à l'axe", "nulles"], 0,
         "Même direction, même sens, même norme."),
        ("Échelle 10 mm pour 5 m/s. Un vecteur de 30 mm représente :", ["6 m/s", "15 m/s", "150 m/s"], 1, "30 / 10 × 5 = 15 m/s."),
        ("L'équiprojectivité s'applique à deux points…", ["quelconques du mécanisme", "d'un même solide", "en liaison glissière"], 1,
         "Elle traduit l'indéformabilité du solide."),
        ("Le CIR d'un solide se trouve…", ["au milieu du solide", "à l'intersection des perpendiculaires aux vitesses", "toujours sur un pivot fixe"], 1,
         "Perpendiculaires aux supports des vitesses, menées par leurs points d'application."),
        ("Dans un mouvement de translation, le CIR :", ["est au centre de gravité", "est à l'infini", "est confondu avec chaque point"], 1,
         "Les perpendiculaires aux vitesses sont parallèles."),
        ("La vitesse d'un point M d'un solide de CIR I est :", ["parallèle à IM", "perpendiculaire à IM", "nulle"], 1,
         "Tout se passe comme une rotation instantanée autour de I."),
        ("Au centre B d'une liaison pivot entre les solides 1 et 2 :", ["V(B∈1/0) = V(B∈2/0)", "V(B∈1/0) = −V(B∈2/0)", "V(B∈1/0) = 0"], 0,
         "Les deux solides ont le même point B en commun."),
        ("Quelle relation de composition est juste ?", ["V(M∈1/3) = V(M∈1/2) + V(M∈2/3)", "V(M∈1/3) = V(M∈1/2) + V(M∈3/2)", "V(M∈1/3) = V(M∈2/1) + V(M∈2/3)"], 0,
         "Les indices s'enchaînent : 1/2 puis 2/3 donne 1/3."),
        ("Pour un vérin, V(C∈tige/corps) a pour direction :", ["l'axe du vérin", "la perpendiculaire à l'axe", "celle de V(C∈corps/bâti)"], 0,
         "La tige coulisse dans le corps : translation le long de l'axe."),
    ]
    s.append(quiz_section(10, "cg-quiz", quiz, "cgq"))
    return (course_head("Cours 2", "graphique", "Cinématique graphique",
                        "Déterminer les vitesses des points d'un mécanisme plan par construction : vecteur vitesse et "
                        "échelle, équiprojectivité, centre instantané de rotation, composition des vitesses.",
                        ["Représenter graphiquement la vitesse.",
                         "Utiliser les propriétés cinématiques des mouvements pour déterminer les vitesses des points d'un solide.",
                         "Appliquer les méthodes de l'équiprojectivité, du CIR et de la loi de composition."],
                        ["Concept de mouvement ; cours 1 (vitesse, rotation, composition des mouvements)."])
            + f'<p class="c-top"><a href="?">{H} Accueil</a></p>' + course_nav(sections) + '<div class="cours">'
            + "".join(s) + '</div><div class="cours-foot"><a class="btn" href="?ex=atelier-libre">Atelier de construction</a>'
            '<a class="btn" href="?ex=arbre-transmission">Activité 2.1 : arbre de transmission</a>'
            f'<a class="btn ghost" href="?ex=cours-cinematique-analytique">Cours 1</a><a class="btn ghost" href="?">{H} Accueil</a></div>')


JS = r"""
  /* ---------------------------------------------------------------- cours 2 : cinématique graphique */
  function initCoursGraphique(root) {
    initCommun(root);
    var NS = "http://www.w3.org/2000/svg";
    function el(g, tag, at, txt) {
      var e = document.createElementNS(NS, tag);
      for (var k in at) e.setAttribute(k, at[k]);
      if (txt !== undefined) e.textContent = txt;
      g.appendChild(e); return e;
    }
    function fl(g, x1, y1, x2, y2, c, w) {
      var dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
      if (L < 1) return;
      var ux = dx / L, uy = dy / L, h = Math.min(11, L * 0.5);
      el(g, "line", { x1: x1, y1: y1, x2: x2 - ux * h * 0.8, y2: y2 - uy * h * 0.8, stroke: c, "stroke-width": w || 3 });
      el(g, "polygon", { points: x2 + "," + y2 + " " + (x2 - ux * h - uy * h * 0.4) + "," + (y2 - uy * h + ux * h * 0.4) + " " + (x2 - ux * h + uy * h * 0.4) + "," + (y2 - uy * h - ux * h * 0.4), fill: c });
    }
    function ligne(g, x1, y1, x2, y2, c, w, d) { el(g, "line", { x1: x1, y1: y1, x2: x2, y2: y2, stroke: c, "stroke-width": w || 1.5, "stroke-dasharray": d || "" }); }
    function q(s) { return root.querySelector(s); }

    // ---------- la même pièce, cinq mouvements
    (function () {
      var box = q("#cg-mvt"); if (!box) return;
      var g = box.querySelector(".cg-m-monde"), mode = "ro", traces = [[], [], []];
      // la pièce de la séquence (deux fois plus grande) ; en rotation, elle tourne autour de son alésage (0, 60)
      var forme = [[0, -110], [52, -110], [68, -76], [32, -60], [32, 76], [-24, 76], [-24, -80]];
      var pts = [[14, 30], [44, -96], [-12, -40]], cols = ["#B42318", "#1B7A43", "#1F5FA8"], piv = [4, 60];
      Array.prototype.forEach.call(box.querySelectorAll("[data-m]"), function (b) {
        b.addEventListener("click", function () {
          mode = b.getAttribute("data-m"); traces = [[], [], []];
          Array.prototype.forEach.call(box.querySelectorAll("[data-m]"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        });
      });
      function pose(t) {  // position (x, y) de l'alésage et angle a de la pièce
        if (mode === "ro") return [380, 220, -0.9 + 0.8 * Math.sin(t * 0.8)];
        if (mode === "tc") return [380 + 90 * Math.cos(t * 0.9), 190 + 55 * Math.sin(t * 0.9), 0];
        if (mode === "tr") return [380 + 230 * Math.sin(t * 0.7), 205 - 40 * Math.sin(t * 0.7), 0];
        if (mode === "tq") return [380 + 230 * Math.sin(t * 0.5), 200 + 30 * Math.sin(t * 1.4), 0];
        return [380 + 200 * Math.sin(t * 0.5), 200 + 25 * Math.cos(t * 0.9), 0.5 * Math.sin(t * 0.7)];
      }
      function place(p, P) { var q = [p[0] - piv[0], p[1] - piv[1]], ca = Math.cos(P[2]), sa = Math.sin(P[2]); return [P[0] + q[0] * ca - q[1] * sa, P[1] + q[0] * sa + q[1] * ca]; }
      animer(function (t) {
        if (RM) t = 1;
        g.innerHTML = "";
        var P = pose(t), P2 = pose(t + 0.02);

        pts.forEach(function (p, i) {
          var a = place(p, P); traces[i].push(a); if (traces[i].length > 420) traces[i].shift();
          if (traces[i].length > 1) el(g, "polyline", { points: traces[i].map(function (x) { return x[0].toFixed(1) + "," + x[1].toFixed(1); }).join(" "), fill: "none", stroke: cols[i], "stroke-width": 1.6 });
        });
        el(g, "polygon", { points: forme.map(function (p) { var a = place(p, P); return a[0].toFixed(1) + "," + a[1].toFixed(1); }).join(" "), fill: "#8E979F", stroke: "#1C2530", "stroke-width": 2, opacity: 0.9 });
        var h = place(piv, P);
        el(g, "circle", { cx: h[0], cy: h[1], r: 7, fill: "#fff", stroke: "#1C2530", "stroke-width": 2 });
        if (mode === "ro") { el(g, "line", { x1: h[0] - 14, y1: h[1] + 16, x2: h[0] + 14, y2: h[1] + 16, stroke: "#1C2530", "stroke-width": 2 }); el(g, "line", { x1: h[0], y1: h[1] + 7, x2: h[0], y2: h[1] + 16, stroke: "#1C2530", "stroke-width": 2 }); }
        pts.forEach(function (p, i) {
          var a = place(p, P), b = place(p, P2), vx = (b[0] - a[0]) * 22, vy = (b[1] - a[1]) * 22;
          el(g, "circle", { cx: a[0], cy: a[1], r: 4, fill: cols[i], stroke: "#fff" });
          fl(g, a[0], a[1], a[0] + vx, a[1] + vy, cols[i], 2.5);
        });
      });
    })();

    // ---------- échelle des vitesses
    (function () {
      var box = q("#cg-echelle"); if (!box) return;
      var ech = box.querySelector(".cg-ech"), vr = box.querySelector(".cg-vr"), g = box.querySelector(".cg-e-monde");
      function maj() {
        var e = +ech.value, v = +vr.value / 100 * 10 * e, L = v / e * 10;
        box.querySelector(".cg-vo").textContent = fr(v, e < 0.1 ? 3 : 2) + " m/s";
        box.querySelector(".cg-lo").textContent = fr(L, 1) + " mm";
        box.querySelector(".cg-fo").textContent = "L = V × 10 / " + fr(e, e < 0.1 ? 2 : 1);
        g.innerHTML = ""; el(g, "circle", { cx: 20, cy: 30, r: 4, fill: "#1C2530" });
        fl(g, 20, 30, 20 + L * 3.5, 30, "#1F5FA8", 3);
        el(g, "text", { x: 26 + L * 3.5, y: 35, "font-size": 13 }, fr(L, 1) + " mm");
      }
      ech.addEventListener("change", maj); vr.addEventListener("input", maj); maj();
    })();

    // ---------- bielle-manivelle vivante
    (function () {
      var box = q("#cg-bm"); if (!box) return;
      var g = box.querySelector(".cg-b-monde"), r = box.querySelector(".cg-br");
      var O = [150, 230], R = 60, L = 200, KV = 70;
      function dessin() {
        var th = +r.value * Math.PI / 180;
        var A = [O[0] + R * Math.cos(th), O[1] - R * Math.sin(th)];
        var B = [A[0] + Math.sqrt(L * L - Math.pow(A[1] - O[1], 2)), O[1]];
        var VA = [-Math.sin(th) * KV, -Math.cos(th) * KV];            // perpendiculaire à OA, sens trigonométrique
        var u = [(B[0] - A[0]) / L, (B[1] - A[1]) / L], p = VA[0] * u[0] + VA[1] * u[1];
        var vb = Math.abs(u[0]) > 1e-9 ? p / u[0] : 0, VB = [vb, 0];
        g.innerHTML = "";
        ligne(g, 40, O[1], 740, O[1], "#7A848C", 1, "10 4 2 4");
        el(g, "circle", { cx: O[0], cy: O[1], r: R, fill: "none", stroke: "#A5ADAA", "stroke-dasharray": "6 4" });
        el(g, "rect", { x: B[0] - 22, y: O[1] - 20, width: 44, height: 40, fill: "#F7EFD9", stroke: "#1C2530", "stroke-width": 2 });
        ligne(g, 280, O[1] - 22, 740, O[1] - 22, "#1C2530", 2); ligne(g, 280, O[1] + 22, 740, O[1] + 22, "#1C2530", 2);
        ligne(g, O[0], O[1], A[0], A[1], "#1C2530", 6); ligne(g, A[0], A[1], B[0], B[1], "#46525C", 9);
        [O, A, B].forEach(function (P) { el(g, "circle", { cx: P[0], cy: P[1], r: 5, fill: "#fff", stroke: "#1C2530", "stroke-width": 2 }); });
        el(g, "text", { x: O[0] - 18, y: O[1] + 22, "font-size": 16, "font-weight": 700 }, "O");
        el(g, "text", { x: A[0] - 18, y: A[1] - 10, "font-size": 16, "font-weight": 700 }, "A");
        el(g, "text", { x: B[0] - 4, y: B[1] + 40, "font-size": 16, "font-weight": 700 }, "B");
        var I = null;
        if (box.querySelector(".cg-bc").checked) {
          // CIR : droite (OA) et verticale en B
          var d = [A[0] - O[0], A[1] - O[1]];
          if (Math.abs(d[0]) > 1e-6) {
            var t = (B[0] - O[0]) / d[0]; I = [B[0], O[1] + d[1] * t];
            if (Math.abs(I[1] - O[1]) < 2000) {
              ligne(g, O[0], O[1], I[0], I[1], "#D35400", 1.2, "6 4"); ligne(g, B[0], B[1], I[0], I[1], "#D35400", 1.2, "6 4");
              if (I[1] > -400 && I[1] < 760) { el(g, "circle", { cx: I[0], cy: I[1], r: 5, fill: "#C62828" }); el(g, "text", { x: I[0] + 8, y: I[1] + 5, "font-size": 15, "font-weight": 700, fill: "#C62828" }, "I2/0"); }
              // champ des vitesses le long de la bielle
              var wI = (VA[0] * (A[1] - I[1]) * -1 + VA[1] * (A[0] - I[0])) / (Math.pow(A[0] - I[0], 2) + Math.pow(A[1] - I[1], 2));
              for (var k = 1; k < 6; k++) {
                var M = [A[0] + (B[0] - A[0]) * k / 6, A[1] + (B[1] - A[1]) * k / 6], im = [M[0] - I[0], M[1] - I[1]];
                fl(g, M[0], M[1], M[0] - wI * im[1], M[1] + wI * im[0], "#7A9CC6", 1.8);
              }
            }
          } else I = null;
        }
        if (box.querySelector(".cg-be").checked) {
          var ha = [A[0] + u[0] * p, A[1] + u[1] * p], hb = [B[0] + u[0] * p, B[1] + u[1] * p];
          ligne(g, A[0] - u[0] * 60, A[1] - u[1] * 60, B[0] + u[0] * 120, B[1] + u[1] * 120, "#7B3FA0", 1, "4 3");
          ligne(g, A[0] + VA[0], A[1] + VA[1], ha[0], ha[1], "#7B3FA0", 1, "3 3");
          ligne(g, A[0], A[1], ha[0], ha[1], "#7B3FA0", 4); ligne(g, B[0], B[1], hb[0], hb[1], "#7B3FA0", 4);
        }
        fl(g, A[0], A[1], A[0] + VA[0], A[1] + VA[1], "#1F5FA8", 3.5);
        fl(g, B[0], B[1], B[0] + VB[0], B[1] + VB[1], "#1B7A43", 3.5);
        el(g, "text", { x: A[0] + VA[0] + 6, y: A[1] + VA[1] - 6, "font-size": 14, "font-weight": 700, fill: "#1F5FA8" }, "V(A∈2/0)");
        el(g, "text", { x: B[0] + VB[0] + (vb >= 0 ? 6 : -70), y: B[1] - 30, "font-size": 14, "font-weight": 700, fill: "#1B7A43" }, "V(B∈2/0)");
        box.querySelector(".cg-bo").textContent = r.value + "°";
        box.querySelector(".cg-br2").textContent = fr(Math.abs(vb) / KV, 2);
        box.querySelector(".cg-bi").textContent = I && Math.abs(I[1] - O[1]) < 2000 ? "à " + fr(Math.hypot(I[0] - A[0], I[1] - A[1]) / 100, 2) + " × AB de A" : "à l'infini (translation instantanée)";
        box.querySelector(".cg-bp").textContent = Math.abs(vb) < 0.5 ? "point mort : V(B) = 0" : (vb > 0 ? "recule vers la droite" : "avance vers O");
      }
      r.addEventListener("input", dessin);
      Array.prototype.forEach.call(box.querySelectorAll("input[type=checkbox]"), function (c) { c.addEventListener("change", dessin); });
      var last = 0;
      animer(function (s) { var dt = Math.min(0.05, s - last); last = s; if (box.querySelector(".cg-ba").checked) { r.value = (+r.value + dt * 40) % 360; dessin(); } });
      dessin();
    })();
  }
"""

CSS = """
/* cours 2 */
.page-cours-cinematique-graphique .at-demo .dm-texte{min-height:4.5em}
"""
