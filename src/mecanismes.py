# -*- coding: utf-8 -*-
"""Les mécanismes des activités de cinématique graphique : feuille (figure, points, axes d'accrochage), échelles et
vitesses attendues, calculées par les méthodes du cours (src/geometrie.py).

Sources : séquence « Cinématique graphique » (exercices Arbre de transmission, Embiellage de moto, Pompe à pétrole
brut, Ellipsographe, Portail à vis, Chargeur Bobcat S185, Suspension du VTT Vario Bomba). Les schémas cinématiques
simples sont redessinés en SVG avec la géométrie relevée sur les pages (rendues à 300 dpi, 1 mm = 11,811 px) ; les
dessins d'ensemble du chargeur et du VTT restent en fond (src/images/fond-*.png), les points y étant calés au pixel.
Toutes les longueurs sont en millimètres de feuille, y vers le bas ; les vitesses sont des vecteurs de feuille
(échelle des vitesses appliquée).
"""
import math
import types

import geometrie as g
from atelier import Feuille
from medias import png

PX = 300 / 25.4  # pixels par millimètre des pages rendues à 300 dpi


def page(p, x0, y0):
    """Point relevé sur une page (pixels à 300 dpi) → feuille recadrée en (x0, y0)."""
    return ((p[0] - x0) / PX, (p[1] - y0) / PX)


def page_qt(p, x0, y1):
    """Idem, pour un dessin tourné d'un quart de tour sur la page et remis à l'endroit (rotation horaire)."""
    return ((y1 - p[1]) / PX, (p[0] - x0) / PX)


def M(**kw):
    return types.SimpleNamespace(**kw)


# ====================================================================== 2.1 — Arbre de transmission (1:1)
def arbre():
    F = Feuille(165, 150, "Document réponse — arbre de transmission")
    O = (80.0, 76.0)
    A, B, C = g.add(O, g.polar(50, 90)), g.add(O, g.polar(50, -60)), g.add(O, g.polar(25, 180))
    F.axe(O, (1, 0), -66, 68)
    F.axe(O, (0, 1), -66, 70)
    F.fleche(g.add(O, (66, 0)), g.add(O, (74, 0)))
    F.fleche(g.add(O, (0, -64)), g.add(O, (0, -72)))
    F.texte(g.add(O, (76, -3.5)), "x", "lab", 3.8)
    F.texte(g.add(O, (4, -70)), "y", "lab", 3.8)
    F.cercle(O, 50, "tr", accroche=True)
    F.cercle(O, 25, "tr", accroche=True)
    F.point("O", O, (-3.6, 3.8))
    F.point("A", A, (3.4, -3.6), marque=True)
    F.point("B", B, (3.4, 3.6), marque=True)
    F.point("C", C, (-3.8, -3.6), marque=True)
    F.texte(g.add(O, (-47, -48)), "Roue (4) : Ø 100 mm", "note", 3.2, "start")
    F.texte(g.add(O, (-21, -29)), "Roue (1) : Ø 50 mm", "note", 3.2, "start")
    F.fleche_arc(O, 58, 145, 118)
    F.texte(g.add(O, g.polar(63, 150)), "N = 1 000 tr/min", "note", 3.2, "end")
    F.echelle((96, 143), 10, "Échelle des vitesses : 10 mm pour 1 m/s")
    F.texte((6, 143.2), "Dessin à l'échelle 1:1", "note", 3, "start")
    s = 10.0                                   # mm de feuille par m/s
    w = 1000 * 2 * math.pi / 60                # rad/s
    va, vc = w * 0.050, w * 0.025              # m/s
    VA = g.vitesse_rotation(O, A, va * s, "horaire")
    VB = g.vitesse_rotation(O, B, va * s, "horaire")
    VC = g.vitesse_rotation(O, C, vc * s, "horaire")
    return M(F=F, O=O, A=A, B=B, C=C, s=s, w=w, va=va, vc=vc, VA=VA, VB=VB, VC=VC)


# ====================================================================== 2.2 — Embiellage de moto (1:2)
def embiellage():
    F = Feuille(180, 135, "Document réponse — embiellage de moto")
    A = (96.0, 95.0)
    R, L = 19.5, 66.5                          # AB = 39 mm et bielles de 133 mm, dessinées à l'échelle 1:2
    B = g.add(A, g.polar(R, 110))              # manivelle à 65° de l'axe du cylindre de droite
    uC, uD = g.polar(1, 45), g.polar(1, 135)   # cylindres en V à 90°

    def sur_axe(u):
        ab = g.sub(B, A)
        k = g.dot(u, ab)
        return g.add(A, g.mul(u, k + math.sqrt(k * k - g.dot(ab, ab) + L * L)))
    C, D = sur_axe(uC), sur_axe(uD)
    G = g.add(B, g.mul(g.sub(C, B), 1 / 3))
    # axes des cylindres, trajectoire du maneton
    F.axe(A, uC, -30, g.dist(A, C) + 26)
    F.axe(A, uD, -6, g.dist(A, D) + 22)
    F.cercle(A, R, "axe", accroche=True)
    # cylindres et pistons
    for P, u, num in ((C, uC, "5"), (D, uD, "5'")):
        n = g.perp(u)
        s0 = g.dist(A, P)
        for sg in (1, -1):
            a, b = g.add(A, g.add(g.mul(u, s0 - 9), g.mul(n, 9.6 * sg))), g.add(A, g.add(g.mul(u, s0 + 17), g.mul(n, 9.6 * sg)))
            F.paroi(a, b, g.mul(n, sg))
        F.glissiere(g.add(P, g.mul(u, 3.5)), u, 13, 17.4, "piece2")
        F.numero(g.add(P, g.add(g.mul(u, 22), g.mul(n, -15))), num, g.add(P, g.add(g.mul(u, 7), g.mul(n, -6))))
    F.numero(g.add(C, g.add(g.mul(uC, 10), g.mul(g.perp(uC), 18))), "0", g.add(C, g.add(g.mul(uC, 10), g.mul(g.perp(uC), 10.5))))
    # bâti du vilebrequin, manivelle, bielles
    F.trait(A, g.add(A, (0, 9)), "tr")
    F.bati(g.add(A, (0, 9)), (0, -1), 12)
    F.trait(A, B, "tr")
    F.trait(B, C, "tr")
    F.trait(B, D, "tr")
    for P in (A, B, C, D):
        F.pivot(P, 1.7)
    F.add(f'<circle cx="{G[0]:.2f}" cy="{G[1]:.2f}" r="0.9" class="flp"/>')
    F.point("A", A, (4, 3.4))
    F.point("B", B, (-1.5, -4.2))
    F.point("C", C, (4.4, 2.8))
    F.point("D", D, (-4.4, 2.8))
    F.point("G", G, (0, -3.6))
    F.numero(g.add(B, (8, 9)), "1", g.add(A, g.mul(g.sub(B, A), 0.55)))
    F.numero(g.add(G, (8, 8)), "2", g.add(B, g.mul(g.sub(C, B), 0.62)))
    F.numero(g.add(B, (-26, -6)), "3", g.add(B, g.mul(g.sub(D, B), 0.45)))
    # angles et rotation
    F.arc(A, 25, 45, 110, "fin")
    F.texte(g.add(A, g.polar(29.5, 77)), "65°", "note", 3.2)
    F.axe(A, g.polar(1, -45), 0, 30, accroche=False)
    F.arc(A, 22, -45, 45, "fin")
    F.texte(g.add(A, g.polar(26, -8)), "90°", "note", 3.2)
    F.fleche_arc(A, 31, 205, 245)
    F.texte(g.add(A, g.polar(36, 228)), "N1/0", "lab", 3.4, "end")
    F.texte((6, 128), "N1/0 = 7 500 tr/min · AB = 39 mm · dessin à l'échelle 1:2", "note", 3, "start")
    F.echelle((112, 128), 10, "Échelle des vitesses : 10 mm pour 5 m/s")
    s = 2.0                                    # mm par m/s
    w = 7500 * 2 * math.pi / 60
    vb = w * 0.039
    VB = g.vitesse_rotation(A, B, vb * s, "trigo")
    VC = g.equiprojectivite(B, VB, C, uC)
    VD = g.equiprojectivite(B, VB, D, uD)
    return M(F=F, A=A, B=B, C=C, D=D, G=G, uC=uC, uD=uD, s=s, w=w, vb=vb, VB=VB, VC=VC, VD=VD)


# ====================================================================== 2.3 — Pompe à pétrole brut (1:40)
def pompe():
    F = Feuille(185, 142, "Document réponse — pompe à pétrole")
    k = 1 / 40
    D = (82.0, 50.0)

    def R(x, y):  # coordonnées réelles (mm, y vers le haut) depuis D → feuille
        return (D[0] + x * k, D[1] - y * k)
    A = R(-2340, -2440)
    B = g.add(A, g.polar(570 * k, 59.2))
    c1, c2 = g.cercles(D, 2310 * k, B, 2640 * k)
    C = c1 if c1[1] < c2[1] else c2
    E = R(3400, 0)
    N, Mp = g.add(D, g.polar(85, 10.9)), g.add(D, g.polar(85, -43.2))
    u3 = g.unit(g.sub(D, C))
    bout = g.add(D, g.mul(u3, 85))
    # trajectoire de la tête et horizontale de D
    F.arc(D, 85, 46, -82, "axe")
    F.cercles.append((D, 85.0))
    F.axe(D, (1, 0), -8, 96)
    # bâti : pivots A et D
    for P in (A, D):
        F.trait(P, g.add(P, (8, 0)), "tr")
        F.bati(g.add(P, (8, 0)), (-1, 0), 9)
    # manivelle 1, biellette 2, balancier et tête de cheval 3
    F.trait(A, B, "tr")
    F.trait(B, C, "tr")
    F.trait(C, bout, "tr")
    F.arc(D, 85, 10.9, -43.2, "tr")
    F.chemin(f"M{N[0]:.2f},{N[1]:.2f} L{N[0] - 3:.2f},{N[1]:.2f}", "tr")
    # câble 4 et cylindre 5
    yb = D[1] + 3211 * k
    F.trait(E, (E[0], yb), "fin")
    F.glissiere((E[0], yb + 1.5), (0, 1), 3, 7, "piece2")
    F.paroi((E[0] - 4.4, yb - 6), (E[0] - 4.4, yb + 9), (-1, 0))
    F.paroi((E[0] + 4.4, yb - 6), (E[0] + 4.4, yb + 9), (1, 0))
    for P in (A, B, C, D):
        F.pivot(P, 1.5)
    F.point("A", A, (-2.5, 4.5))
    F.point("B", B, (-3.6, -3))
    F.point("C", C, (-3.8, -2.6))
    F.point("D", D, (-1, 5))
    F.point("E", E, (3, -3.2), marque=True)
    F.point("N", N, (2.4, -3.2), marque=True)
    F.point("M", Mp, (3.6, 1.5), marque=True)
    F.numero(g.add(A, (-9, 9)), "1", g.add(A, g.mul(g.sub(B, A), 0.5)))
    F.numero(g.add(B, (-30, -30)), "2", g.add(B, g.mul(g.sub(C, B), 0.42)))
    F.numero(g.add(D, (-22, 12)), "3", g.add(D, g.mul(g.sub(C, D), 0.45)))
    F.numero((E[0] - 12, yb - 22), "4", (E[0], yb - 26))
    F.numero((E[0] - 12, yb + 6), "5", (E[0] - 4.4, yb + 4))
    F.numero(g.add(D, (14, 8)), "0", g.add(D, (8, 3)))
    F.fleche_arc(A, 8, 150, 95, 1.8)
    F.texte(g.add(A, (-7, -10)), "N1/0", "lab", 3.2, "end")
    F.fleche_arc(D, 12, 60, 100, 1.8)
    F.fleche_arc(D, 12, 100, 60, 1.8)
    F.texte(g.add(D, (-5, -13)), "N3/0", "lab", 3.2, "end")
    F.texte((5, 5), "AB = 570 mm · BC = 2 640 mm · CD = 2 310 mm · DE = 3 400 mm", "note", 3, "start")
    F.texte((5, 10), "Dessin à l'échelle 1:40 · N1/0 = 15 tr/min (sens horaire)", "note", 3, "start")
    F.echelle((100, 137), 10, "Échelle des vitesses : 10 mm pour 0,2 m/s")
    s = 50.0                                   # mm par m/s
    w1 = 15 * 2 * math.pi / 60
    vb = w1 * 0.570
    VB = g.vitesse_rotation(A, B, vb * s, "horaire")
    VC = g.equiprojectivite(B, VB, C, g.perp(g.sub(C, D)))
    VE = g.vitesse_par_cir(D, C, VC, E)
    S = math.pi * 0.1 ** 2 / 4
    return M(F=F, A=A, B=B, C=C, D=D, E=E, N=N, Mp=Mp, s=s, w1=w1, vb=vb, VB=VB, VC=VC, VE=VE, S=S,
             q=g.norm(VE) / s * S)


# ====================================================================== 2.4 — Ellipsographe (schéma)
def ellipsographe():
    F = Feuille(160, 160, "Document réponse — ellipsographe")
    O = (84.0, 136.0)
    AB, th = 52.0, 50.0
    A = (O[0] - AB * math.cos(math.radians(th)), O[1])
    B = (O[0], O[1] - AB * math.sin(math.radians(th)))
    Mc = g.add(B, g.sub(B, A))
    e = 6.0
    # rainures du bâti 0, en croix
    for y in (O[1] - e, O[1] + e):
        F.trait((6, y), (O[0] - e, y), "fin")
        F.trait((O[0] + e, y), (154, y), "fin")
    for x in (O[0] - e, O[0] + e):
        F.trait((x, 8), (x, O[1] - e), "fin")
        F.trait((x, O[1] + e), (x, 156), "fin")
    F.axe(O, (1, 0), -80, 66)
    F.axe(O, (0, 1), -124, 22)
    F.fleche(g.add(O, (66, 0)), g.add(O, (73, 0)))
    F.fleche(g.add(O, (0, -122)), g.add(O, (0, -129)))
    F.texte(g.add(O, (73, -4)), "x", "lab", 3.8)
    F.texte(g.add(O, (4.5, -127)), "y", "lab", 3.8)
    # coulisses 1 et 3
    F.glissiere(A, (1, 0), 17, 2 * e - 0.6, "piece2")
    F.glissiere(B, (0, 1), 17, 2 * e - 0.6, "piece2")
    # barre porte-mine 2
    u = g.unit(g.sub(Mc, A))
    n = g.perp(u)
    r = 4.4
    p1, p2 = g.add(A, g.mul(n, r)), g.add(Mc, g.mul(n, r))
    p3, p4 = g.sub(Mc, g.mul(n, r)), g.sub(A, g.mul(n, r))
    F.chemin(f"M{p1[0]:.2f},{p1[1]:.2f} L{p2[0]:.2f},{p2[1]:.2f} A{r},{r} 0 0 0 {p3[0]:.2f},{p3[1]:.2f} "
             f"L{p4[0]:.2f},{p4[1]:.2f} A{r},{r} 0 0 0 {p1[0]:.2f},{p1[1]:.2f} Z", "piece")
    F.axe(A, u, -6, g.dist(A, Mc) + 6, accroche=False)
    for P in (A, B):
        F.pivot(P, 1.8)
    F.cercle(Mc, 2.2, "pivot")
    F.point("O", O, (-3.6, 3.8))
    F.point("A", A, (-1.5, 9.2))
    F.point("B", B, (4.6, 3))
    F.point("M", Mc, (4.6, 3.6))
    F.numero(g.add(A, (-16, -16)), "1", g.add(A, (-6, -3)))
    F.numero(g.add(B, (-24, -6)), "3", g.add(B, (-5, -2)))
    F.numero(g.add(B, g.add(g.mul(u, -22), g.mul(n, 14))), "2", g.add(B, g.add(g.mul(u, -22), g.mul(n, 4.4))))
    F.numero((O[0] + 34, O[1] + 14), "0", (O[0] + 26, O[1] + e))
    F.texte(g.add(Mc, (-4, -5.5)), "crayon", "note", 3, "end")
    F.texte((5, 155.5), "Schéma (dessin sans échelle de longueur)", "note", 3, "start")
    F.echelle((92, 155.5), 10, "Échelle des vitesses : 10 mm pour 1 cm/s")
    s = 10.0                                   # mm par cm/s
    VA = (3 * s, 0.0)
    I = g.cir(A, (1, 0), B, (0, 1))
    VM = g.vitesse_par_cir(I, A, VA, Mc)
    VB = g.vitesse_par_cir(I, A, VA, B)
    return M(F=F, O=O, A=A, B=B, Mc=Mc, s=s, VA=VA, I=I, VM=VM, VB=VB)


# ====================================================================== 2.5 — Portail à vis (1:10)
def portail():
    F = Feuille(195, 262, "Document réponse — portail à vis")
    A = (24.0, 76.0)

    def R(x, y):  # cotes relevées sur le dessin, en mm, depuis A (x vers la droite, y vers le bas)
        return (A[0] + x, A[1] + y)
    B, C, Mp = R(46.7, 16.9), R(132.4, -21.5), R(130.0, 75.0)
    yv = A[1] - 28.96                          # axe de la vis
    nut = (C[0], yv)
    xg = A[0] + 39.2                           # plan des roues dentées
    # carter 4, moteur, engrenage, palier, vis 5, écrou 3
    F.poly([R(11.4, -59.3), R(50.4, -59.3), R(50.4, -7.2), R(11.4, -7.2)], "tr", True)
    F.poly([R(11.4, -52.1), R(28.1, -52.1), R(28.1, -40.5), R(11.4, -40.5)], "tr", True)
    F.texte(R(19.7, -36.6), "Moteur", "note", 2.8)
    ym = A[1] - 46.4
    F.trait(R(28.1, -46.4), (xg + 1.5, ym), "tr")
    for yc, rr in ((ym, 4.35), (yv, 13.05)):
        F.trait((xg, yc - rr), (xg, yc + rr), "tr")
        for yy in (yc - rr, yc + rr):
            F.trait((xg - 1.6, yy), (xg + 1.6, yy), "tr")
    F.trait((xg, yv), (A[0] + 150, yv), "tr")
    F.glissiere(R(50.4, -28.96), (1, 0), 9, 3.6, "piece")
    F.glissiere(nut, (1, 0), 10, 5, "piece2")
    zz = " ".join(f"{nut[0] - 5 + i * 1.25:.2f},{yv + (2.2 if i % 2 else -2.2):.2f}" for i in range(9))
    F.add(f'<polyline points="{zz}" class="fin"/>')
    F.trait((C[0], yv + 2.5), C, "tr")
    F.axe((C[0], yv), (1, 0), -100, 24, accroche=True, cls="axe")
    F.lignes.append((C, (1.0, 0.0)))     # trajectoire de C (parallèle à la vis)
    # portail 1, chape de A, bielle 2 coudée
    F.poly([R(-4.5, -4.8), R(4.5, -4.8), R(2.6, 0.6), R(-2.6, 0.6)], "tr", True)
    F.bati(R(0, -4.8), (0, 1), 11)
    u = g.unit(g.sub(Mp, A))
    n = g.perp(u)
    F.poly([g.add(A, g.mul(n, 1.9)), g.add(Mp, g.mul(n, 1.9)), g.sub(Mp, g.mul(n, 1.9)), g.sub(A, g.mul(n, 1.9))], "piece", True)
    F.trait(B, g.projete(B, A, u), "tr")
    coude = R(116.4, -0.4)
    F.poly([B, coude, C], "tr")
    for P in (A, B, C):
        F.pivot(P, 1.8)
    F.add(f'<path d="M{Mp[0] - 1.6:.2f},{Mp[1] - 1.6:.2f} l3.2,3.2 M{Mp[0] - 1.6:.2f},{Mp[1] + 1.6:.2f} l3.2,-3.2" class="tr"/>')
    # position fermée et repère
    F.trait(A, (A[0], A[1] + 168), "tire")
    F.texte((A[0] - 3.2, A[1] + 120), "position portail fermé", "note", 3, "middle", -90)
    F.point("A", A, (-4.6, 3))
    F.point("B", B, (-1, -4.4))
    F.point("C", C, (4.4, 2.6))
    F.point("M", Mp, (4, 3.5))
    F.numero(g.add(A, g.add(g.mul(u, 95), g.mul(n, -12))), "1", g.add(A, g.add(g.mul(u, 95), g.mul(n, -2))))
    F.numero(R(100, 14), "2", R(96, 3.2))
    F.numero(R(122, -42), "3", R(130, -31))
    F.numero(R(43, -66), "4", R(43, -59.3))
    F.numero(R(90, -40), "5", R(90, -29.5))
    F.texte(R(41.6, -63.5), "Z = 90 dents", "note", 2.6, "start")
    F.texte(R(41.6, -12), "Z = 270 dents", "note", 2.6, "start")
    o = R(160, -40)
    F.fleche(o, g.add(o, (0, 11)))
    F.fleche(o, g.add(o, (-11, 0)))
    F.texte(g.add(o, (2.5, 13)), "x", "lab", 3.6)
    F.texte(g.add(o, (-14, -2.5)), "y", "lab", 3.6)
    F.texte((6, 256), "Dessin à l'échelle 1:10 · vis : 600 tr/min, pas 6 mm", "note", 3, "start")
    F.echelle((112, 256), 10, "Échelle : 1 cm pour 0,02 m/s")
    s = 500.0                                  # mm par m/s
    VC = (-0.06 * s, 0.0)                      # fermeture : l'écrou se rapproche du moteur
    I24 = g.inter(A, g.sub(B, A), C, (0, 1))
    VB = g.vitesse_par_cir(I24, C, VC, B)
    VM = g.vitesse_par_cir(A, B, VB, Mp)
    w = g.norm(VB) / s / (g.dist(A, B) * 10 / 1000)
    # position fermée : le portail tourne autour de A jusqu'à la verticale ; C reste sur sa droite
    a_am = g.angle(g.sub(Mp, A))
    Bf = g.add(A, g.rot(g.sub(B, A), -90 - a_am))
    dy = C[1] - Bf[1]
    Cf = (Bf[0] + math.sqrt(g.dist(B, C) ** 2 - dy ** 2), C[1])
    course = (C[0] - Cf[0]) * 10               # mm réels
    tours_vis = course / 6
    return M(F=F, A=A, B=B, C=C, Mp=Mp, s=s, VC=VC, I24=I24, VB=VB, VM=VM, w=w, Bf=Bf, Cf=Cf, course=course,
             tours_vis=tours_vis, tours_moteur=tours_vis * 270 / 90, rot=-90 - a_am)


# ====================================================================== 2.6 — Chargeur Bobcat S185 (fond)
def bobcat():
    src, wpx, hpx = png("fond-bobcat")
    W, H = wpx * 2 / PX, hpx * 2 / PX          # fond réduit de moitié par outils/preparer-images.sh
    F = Feuille(round(W, 2), round(H, 2), "Document réponse — chargeur Bobcat S185")
    F.image(src, 0, 0, W, H)
    pts = dict(A=(1900, 2408), B=(1935, 2116), C=(1682, 2231), D=(1832, 2848), E=(1497, 2316), F=(1048, 2629),
               H=(629, 1967))
    P = {k: page(v, 230, 280) for k, v in pts.items()}
    for k, p in P.items():
        F.point(k, p, None, marque=True)
    F.axe(P["D"], g.sub(P["C"], P["D"]), -6, g.dist(P["D"], P["C"]) + 12)
    F.echelle((6, 6), 10, "Échelle des vitesses : 10 mm pour 50 mm/s")
    s = 0.2                                    # mm par mm/s
    v54 = g.mul(g.unit(g.sub(P["C"], P["D"])), 635 / 3.5 * s)
    I = g.inter(P["A"], g.sub(P["B"], P["A"]), P["F"], g.sub(P["E"], P["F"]))
    dC50, dC40 = g.perp(g.sub(P["C"], I)), g.perp(g.sub(P["C"], P["D"]))
    a, b = g.composition(v54, dC50, g.mul(dC40, -1))
    v50, v40 = a, g.mul(b, -1)                 # V(C∈5/0) = V(C∈5/4) + V(C∈4/0)
    vH = g.vitesse_par_cir(I, P["C"], v50, P["H"])
    return M(F=F, P=P, s=s, v54=v54, I=I, v50=v50, v40=v40, vH=vH)


# ====================================================================== 2.7 — Suspension du VTT (trois fonds)
def vtt():
    feuilles = []
    releves = [  # (fond, origine du recadrage x0, bas y1, points en pixels de la page, mm par m/s, libellé d'échelle)
        ("fond-vtt-1", 380, 3010, dict(A=(912, 974), B=(1258, 1256), C=(1207, 1463), D=(1118, 1521), F=(1250, 1754),
                                         H=(2000, 1315), G=(1964, 2892)), 10 / 6, "1 cm pour 6 m/s"),
        ("fond-vtt-2", 480, 2650, dict(A=(923, 813), B=(1592, 1357), C=(1492, 1754), D=(1320, 1867), F=(1574, 2313)),
         10 / 5, "1 cm pour 5 m/s"),
        ("fond-vtt-3", 480, 2960, dict(A=(966, 1021), B=(1714, 1626), C=(1603, 2072), D=(1410, 2197), F=(1695, 2697)),
         10 / 3, "1 cm pour 3 m/s"),
    ]
    for i, (fond, x0, y1, pts, s, ech) in enumerate(releves):
        src, wpx, hpx = png(fond)
        W, H = wpx * 2 / PX, hpx * 2 / PX
        F = Feuille(round(W, 2), round(H, 2), f"Document réponse {i + 1} — suspension du VTT")
        F.image(src, 0, 0, W, H)
        P = {k: page_qt(v, x0, y1) for k, v in pts.items()}
        for k, p in P.items():
            F.point(k, p, None, marque=True)
        F.echelle((6, H - 5), 10, "Échelle des vitesses : " + ech)
        feuilles.append(M(F=F, P=P, s=s))
    f1, f2, f3 = feuilles
    P1 = f1.P
    VG = g.vitesse_rotation(P1["H"], P1["G"], 30 * f1.s, "horaire")      # la roue monte : compression
    VF = g.vitesse_par_cir(P1["H"], P1["G"], VG, P1["F"])
    VD = g.equiprojectivite(P1["F"], VF, P1["D"], g.perp(g.sub(P1["D"], P1["B"])))
    sens = "horaire" if g.cross(g.sub(P1["D"], P1["B"]), VD) > 0 else "trigo"
    P2 = f2.P
    VD2 = g.vitesse_rotation(P2["B"], P2["D"], 20 * f2.s, sens)
    VC2 = g.vitesse_par_cir(P2["B"], P2["D"], VD2, P2["C"])
    P3 = f3.P
    VC3 = g.vitesse_rotation(P3["B"], P3["C"], 15 * f3.s, sens)
    axe = g.sub(P3["C"], P3["A"])
    V45, V50 = g.composition(VC3, axe, g.perp(axe))
    f1.__dict__.update(VG=VG, VF=VF, VD=VD)
    f2.__dict__.update(VD=VD2, VC=VC2)
    f3.__dict__.update(VC=VC3, V45=V45, V50=V50)
    return M(f1=f1, f2=f2, f3=f3, sens=sens)


if __name__ == "__main__":
    def ms(v, s):
        return f"{g.norm(v) / s:.4f}"
    a = arbre(); print("arbre", ms(a.VA, a.s), ms(a.VC, a.s))
    e = embiellage(); print("embiellage", ms(e.VB, e.s), ms(e.VC, e.s), ms(e.VD, e.s))
    p = pompe(); print("pompe", ms(p.VB, p.s), ms(p.VC, p.s), ms(p.VE, p.s), p.q)
    el = ellipsographe(); print("ellipsographe", ms(el.VM, el.s), ms(el.VB, el.s), g.r2(el.I))
    po = portail(); print("portail", ms(po.VB, po.s), ms(po.VM, po.s), po.w, g.r2(po.Bf), g.r2(po.Cf), po.course, po.tours_moteur)
    b = bobcat(); print("bobcat", ms(b.v54, b.s), ms(b.v50, b.s), ms(b.vH, b.s), b.F.w, b.F.h)
    v = vtt(); print("vtt", ms(v.f1.VF, v.f1.s), ms(v.f1.VD, v.f1.s), ms(v.f2.VC, v.f2.s), ms(v.f3.V45, v.f3.s), v.sens)
