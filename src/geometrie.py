# -*- coding: utf-8 -*-
"""Géométrie plane des constructions : vecteurs, droites, intersections, et les trois méthodes graphiques
(équiprojectivité, centre instantané de rotation, composition des vitesses) écrites sous forme de calcul.

Coordonnées de feuille : en millimètres, axe des x vers la droite, axe des y VERS LE BAS (comme le SVG).
Un vecteur vitesse est exprimé en millimètres de feuille, échelle des vitesses appliquée.
"""
import math


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def norm(a):
    return math.hypot(a[0], a[1])


def dist(a, b):
    return norm(sub(a, b))


def unit(a):
    n = norm(a)
    return (a[0] / n, a[1] / n)


def perp(a):
    """Vecteur tourné d'un quart de tour (sens horaire à l'écran, puisque y descend)."""
    return (-a[1], a[0])


def rot(a, deg):
    """Rotation d'un angle en degrés, sens trigonométrique À L'ÉCRAN (y vers le bas : on change le signe)."""
    t = math.radians(-deg)
    c, s = math.cos(t), math.sin(t)
    return (a[0] * c - a[1] * s, a[0] * s + a[1] * c)


def polar(r, deg):
    """Point à la distance r, angle en degrés compté sens trigonométrique à l'écran (0° vers la droite)."""
    t = math.radians(deg)
    return (r * math.cos(t), -r * math.sin(t))


def angle(a):
    """Angle en degrés d'un vecteur, sens trigonométrique à l'écran."""
    return math.degrees(math.atan2(-a[1], a[0]))


def inter(p1, d1, p2, d2):
    """Intersection des droites (p1, d1) et (p2, d2)."""
    den = cross(d1, d2)
    if abs(den) < 1e-12:
        raise ValueError("droites parallèles")
    t = cross(sub(p2, p1), d2) / den
    return add(p1, mul(d1, t))


def projete(p, a, d):
    """Projeté orthogonal du point p sur la droite (a, d)."""
    u = unit(d)
    return add(a, mul(u, dot(sub(p, a), u)))


def cercles(c1, r1, c2, r2):
    """Les deux points d'intersection de deux cercles."""
    d = dist(c1, c2)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    u = unit(sub(c2, c1))
    m = add(c1, mul(u, a))
    return add(m, mul(perp(u), h)), sub(m, mul(perp(u), h))


def r2(p, n=2):
    return (round(p[0], n), round(p[1], n))


# ---------------------------------------------------------------- méthodes graphiques
def vitesse_rotation(centre, point, v_norme, sens):
    """Vitesse d'un point d'un solide en rotation autour de « centre » : perpendiculaire au rayon, de norme v_norme
    (en mm de feuille), sens « horaire » ou « trigo » tel qu'on le voit sur la feuille."""
    r = unit(sub(point, centre))
    t = perp(r) if sens == "horaire" else mul(perp(r), -1)
    return mul(t, v_norme)


def equiprojectivite(a, va, b, db):
    """Vitesse de b connaissant la vitesse va de a (même solide) et la direction db du support de V(b)."""
    u = unit(sub(b, a))
    proj = dot(va, u)
    k = proj / dot(unit(db), u)
    return mul(unit(db), k)


def cir(a, da, b, db):
    """Centre instantané de rotation : intersection des perpendiculaires aux supports des vitesses en a et en b."""
    return inter(a, perp(da), b, perp(db))


def vitesse_par_cir(i, a, va, m):
    """Vitesse de m connaissant celle de a et le CIR i : perpendiculaire à (IM), norme proportionnelle à IM,
    même sens de rotation autour de i."""
    w = cross(sub(a, i), va) / dot(sub(a, i), sub(a, i))  # « vitesse angulaire » en mm de feuille par mm
    im = sub(m, i)
    return (-w * im[1], w * im[0])


def composition(v_connu, d_inconnu1, d_inconnu2):
    """Décompose v_connu = x·d1 + y·d2 (directions d1, d2) : renvoie les deux vecteurs composantes."""
    u1, u2 = unit(d_inconnu1), unit(d_inconnu2)
    den = cross(u1, u2)
    x = cross(v_connu, u2) / den
    y = cross(u1, v_connu) / den
    return mul(u1, x), mul(u2, y)
