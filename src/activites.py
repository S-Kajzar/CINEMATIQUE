# -*- coding: utf-8 -*-
"""Les activités de résolution graphique : un exercice de la séquence « Cinématique graphique » = une activité.

Chaque activité a une ou plusieurs parties ; une partie a sa feuille de construction (src/mecanismes.py) et ses
questions, de trois sortes :
  - Q     : réponse saisie (valeur avec unité, ou relation de composition), corrigée par le moteur du gabarit ;
  - ETQ   : cases à remplir avec des étiquettes (nature d'un mouvement, comparaison de deux vitesses…) ;
  - TRACE : éléments à construire sur la feuille (vecteur, support, point, trajectoire), vérifiés par l'atelier.
Les numéros reprennent ceux de la séquence (Q1, Q2…) ; une question d'origine découpée garde son numéro, suivi d'une
lettre. Les valeurs attendues sont calculées par les méthodes du cours (src/geometrie.py).
"""
import re

import geometrie as g
import mecanismes as mc
from atelier import (IT_VE, IT_DIR, IT_PT, C_VE, C_DR, C_SG, C_CI, C_PT, C_TX, tol_cir, corr_equiprojectivite,
                     corr_cir, corr_triangle)


# ====================================================================== écriture
def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def V(pt, sol):
    """Vecteur vitesse écrit comme dans la séquence : V(A∈1/0), flèche au-dessus."""
    return f'<span class="vv"><span class="vec">V</span><sub>({pt}∈{sol})</sub></span>'


def N(pt, sol):
    return f"‖{V(pt, sol)}‖"


def nom(pt, sol):
    """Nom en texte simple (étiquettes des tracés, suggestions) : V(A∈1/0)."""
    return f"V({pt}∈{sol})"


def compact(s):
    """Forme compacte d'une étiquette, telle que la compare le correcteur « code » du gabarit."""
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.replace("œ", "oe"))


# ====================================================================== correcteurs
UNITES = {
    "m/s": {"label": "m/s", "accept": ["m/s", "ms-1", "m/sec"]},
    "cm/s": {"label": "cm/s", "accept": ["cm/s", "cms-1"]},
    "mm/s": {"label": "mm/s", "accept": ["mm/s", "mms-1"]},
    "rad/s": {"label": "rad/s", "accept": ["rad/s", "rads-1", "radian/s", "radians/s"]},
    "m3/s": {"label": "m³/s", "accept": ["m3/s", "m3s-1"]},
    "L/s": {"label": "L/s", "accept": ["l/s", "ls-1", "litre/s", "litres/s"]},
    "tours": {"label": "tours", "accept": ["tours", "tour", "tr"]},
    "mm": {"label": "mm", "accept": ["mm", "millimetre", "millimetres"]},
    "m": {"label": "m", "accept": ["m", "metre", "metres"]},
    "km": {"label": "km", "accept": ["km", "kilometre", "kilometres"]},
    "s": {"label": "s", "accept": ["s", "sec", "seconde", "secondes"]},
    "mm/s2": {"label": "mm/s²", "accept": ["mm/s2", "mms-2", "mm/s/s"]},
    "m/s2": {"label": "m/s²", "accept": ["m/s2", "ms-2", "m/s/s"]},
    "rad": {"label": "rad", "accept": ["rad", "radian", "radians"]},
    "rad/s2": {"label": "rad/s²", "accept": ["rad/s2", "rads-2"]},
    "tr/s": {"label": "tr/s", "accept": ["tr/s", "trs-1", "tours/s", "tour/s"]},
    "tr/min": {"label": "tr/min", "accept": ["tr/min", "trmin-1", "tr/mn", "tours/min", "tour/min", "rpm"]},
    "km/h": {"label": "km/h", "accept": ["km/h", "kmh-1"]},
}


def NUM(valeur, unite, rel=0.05, variantes=(), signe=True):
    """Valeur numérique avec unité (la moitié des points pour l'unité, règle du gabarit). Les tolérances relatives
    tiennent compte de la précision d'un tracé : 1 à 2 % pour un calcul, 5 à 8 % pour une lecture sur la feuille.
    signe=False : le signe n'est pas noté (une décélération donnée en valeur absolue est acceptée)."""
    gr = {"type": "num", "value": round(valeur, 6), "relTol": rel, "unit": UNITES[unite]}
    if not signe:
        gr["abs"] = True
    if variantes:
        gr["variants"] = [{"value": round(v, 6), "relTol": rel, "unit": UNITES[u], "strictUnit": True} for v, u in variantes]
    return gr


def CODE(*bonnes):
    return {"type": "code", "equals": [compact(b) for b in bonnes]}


def CHASLES(solides):
    """Relation de composition des vitesses (moteur « chasles » du gabarit) : toute relation juste est acceptée."""
    return {"type": "chasles", "solids": solides}


JUSTE = CODE("juste")  # champ masqué d'un élément à construire : l'atelier y écrit « juste » ou « faux »

# ====================================================================== blocs
NATURES = ["Rotation", "Translation rectiligne", "Translation circulaire", "Mouvement plan"]
COMPAR = ["Égales", "Opposées", "Même direction, normes différentes", "Directions différentes"]


def HTML(raw):
    return {"kind": "html", "html": raw}


def Q(num, stem, hint, grader, expected, why, ins=False):
    """Réponse saisie ; ins : propose le bouton « ∈ » (relations de composition)."""
    return {"kind": "q", "num": num, "stem": stem, "hint": hint, "grader": grader, "expected": expected, "why": why,
            "ins": ins}


def ETQ(num, stem, champs, banque, why, hint="Glisse une étiquette dans chaque case (ou touche l'étiquette, puis la case).",
        titre="Étiquettes"):
    """Cases à remplir avec des étiquettes : champs = [(libellé de la case, étiquette juste)]."""
    for _l, bonne in champs:
        assert bonne in banque, bonne
    return {"kind": "etq", "num": num, "stem": stem, "hint": hint, "banque": list(banque), "titre": titre, "why": why,
            "fields": [(lab, CODE(bonne), bonne) for lab, bonne in champs]}


def TRACE(num, stem, hint, items, corr, why):
    """Éléments à construire sur la feuille de la partie ; chaque élément vaut un point."""
    return {"kind": "trace", "num": num, "stem": stem, "hint": hint, "items": items, "corr": corr, "why": why,
            "fields": [(it["lab"], JUSTE, "") for it in items]}


def donnees(*lignes):
    return '<div class="data"><p class="data-title">Données</p><ul>' + "".join(f"<li>{x}</li>" for x in lignes) + "</ul></div>"


def mm_ms(v, s, d=1):
    return f"{fr(g.norm(v), d)} mm"


H_VE = "Trace le vecteur avec l'outil <em>Vecteur</em> depuis son point d'application, puis nomme-le ; sa longueur se règle au millimètre dans la barre qui s'ouvre sous la feuille."
H_DIR = "Trace une droite (outil <em>Droite</em>, <em>Perpendiculaire</em> ou <em>Parallèle</em>) passant par le point."
H_PT = "Place le point à l'intersection de tes tracés (outil <em>Point</em>), puis nomme-le."


# ====================================================================== 2.1 — ARBRE DE TRANSMISSION
def arbre():
    m = mc.arbre()
    O, A, B, C, s = m.O, m.A, m.B, m.C, m.s
    ab, ac = g.sub(B, A), g.sub(C, A)
    ha, hb = g.projete(g.add(A, m.VA), A, ab), g.projete(g.add(B, m.VB), A, ab)
    ha2, hc = g.projete(g.add(A, m.VA), A, ac), g.projete(g.add(C, m.VC), A, ac)
    PROJ = ["Les projections sont égales", "Les projections sont opposées", "Les projections sont nulles",
            "Les vecteurs vitesse sont égaux"]
    CONCL = ["Les vitesses de deux points d'un même solide ont la même projection sur la droite qui joint ces points",
             "Deux points d'un même solide ont toujours la même vitesse",
             "La vitesse d'un point ne dépend pas de sa distance à l'axe de rotation",
             "La projection d'une vitesse sur le rayon est égale à la vitesse"]
    tp = lambda v: max(2.0, 0.07 * g.norm(v))  # noqa: E731  projeté : dépend de la précision du vecteur tracé
    blocks = [
        Q("Q1 a)", f"Calcule la norme {N('A', '4/0')}.", "Arrondis au centième ; saisis la valeur avec son unité.",
          NUM(m.va, "m/s", 0.015), f"{N('A', '4/0')} = {fr(m.va, 2)} m/s",
          f"<p>La roue (4) tourne autour de l'axe (O, <span class=vec>z</span>) : ω = 2π·N / 60 = 2π × 1 000 / 60 = {fr(m.w, 1)} rad/s.</p>"
          f"<p>Le point A est à R = 50 mm = 0,050 m de l'axe : V = R·ω = 0,050 × {fr(m.w, 1)} = <strong>{fr(m.va, 2)} m/s"
          f"</strong>. À l'échelle 10 mm pour 1 m/s, le vecteur mesure {fr(m.va * s, 1)} mm.</p>"),
        TRACE("Q1 b)", f"Trace {V('A', '4/0')} et {V('B', '4/0')} à l'échelle proposée.", H_VE,
              [IT_VE(A, m.VA, nom("A", "4/0")), IT_VE(B, m.VB, nom("B", "4/0"))],
              [C_SG(O, A), C_SG(O, B), C_VE(A, m.VA, nom("A", "4/0")), C_VE(B, m.VB, nom("B", "4/0"))],
              f"<p>Chaque vecteur a pour origine le point, pour direction la perpendiculaire au rayon (OA, puis OB), "
              f"pour sens celui de la rotation (horaire) et pour longueur {fr(m.va * s, 1)} mm : A et B sont à la même "
              f"distance de l'axe, leurs vitesses ont la même norme.</p>"),
        TRACE("Q2 a)", f"Trace la droite (AB) et projette orthogonalement sur elle {V('A', '4/0')} et {V('B', '4/0')}.",
              "Outil <em>Droite</em> par A et B, puis outil <em>Projeté</em> : touche l'extrémité du vecteur, puis la "
              "droite (AB) ; le projeté est marqué d'une croix.",
              [IT_DIR(A, ab, "Droite (AB)"), IT_PT(ha, "", "Projeté de l'extrémité de " + nom("A", "4/0") + " sur (AB)", tp(m.VA)),
               IT_PT(hb, "", "Projeté de l'extrémité de " + nom("B", "4/0") + " sur (AB)", tp(m.VB))],
              [C_DR(A, ab), C_SG(g.add(A, m.VA), ha), C_SG(g.add(B, m.VB), hb), C_SG(A, ha, "res"), C_SG(B, hb, "res"),
               C_PT(ha, ""), C_PT(hb, "")],
              f"<p>Les deux segments projetés, de A à son projeté et de B au sien, mesurent "
              f"{fr(g.dist(A, ha), 1)} mm et {fr(g.dist(B, hb), 1)} mm, dans le même sens.</p>"),
        ETQ("Q2 b)", "Que constates-tu ?", [("Projections de " + V("A", "4/0") + " et de " + V("B", "4/0") + " sur (AB)",
                                             PROJ[0])], PROJ,
            "<p>Les projections orthogonales des deux vitesses sur (AB) sont égales (même longueur, même sens).</p>"),
        Q("Q3 a)", f"Calcule la norme {N('C', '1/0')}.", "Arrondis au centième ; saisis la valeur avec son unité.",
          NUM(m.vc, "m/s", 0.015), f"{N('C', '1/0')} = {fr(m.vc, 2)} m/s",
          f"<p>La roue (1) est encastrée sur l'arbre : elle tourne à la même vitesse angulaire ω = {fr(m.w, 1)} rad/s. "
          f"C est à 25 mm de l'axe : V = 0,025 × {fr(m.w, 1)} = <strong>{fr(m.vc, 2)} m/s</strong>, soit "
          f"{fr(m.vc * s, 1)} mm à l'échelle.</p>"),
        TRACE("Q3 b)", f"Trace {V('C', '1/0')}.", H_VE, [IT_VE(C, m.VC, nom("C", "1/0"))],
              [C_SG(O, C), C_VE(C, m.VC, nom("C", "1/0"))],
              "<p>Perpendiculaire au rayon OC (donc verticale), vers le haut puisque l'arbre tourne dans le sens horaire, "
              f"longueur {fr(m.vc * s, 1)} mm.</p>"),
        TRACE("Q4 a)", f"Trace la droite (AC) et projette orthogonalement sur elle {V('A', '4/0')} et {V('C', '1/0')}.",
              "Même méthode qu'à la question 2.",
              [IT_DIR(A, ac, "Droite (AC)"), IT_PT(ha2, "", "Projeté de l'extrémité de " + nom("A", "4/0") + " sur (AC)", tp(m.VA)),
               IT_PT(hc, "", "Projeté de l'extrémité de " + nom("C", "1/0") + " sur (AC)", tp(m.VC))],
              [C_DR(A, ac), C_SG(g.add(A, m.VA), ha2), C_SG(g.add(C, m.VC), hc), C_SG(A, ha2, "res"), C_SG(C, hc, "res"),
               C_PT(ha2, ""), C_PT(hc, "")],
              f"<p>Les deux projections mesurent {fr(g.dist(A, ha2), 1)} mm et {fr(g.dist(C, hc), 1)} mm : elles sont "
              "encore égales, bien que A et C appartiennent à deux roues différentes.</p>"),
        ETQ("Q4 b)", "Que constates-tu ?", [("Projections de " + V("A", "4/0") + " et de " + V("C", "1/0") + " sur (AC)",
                                             PROJ[0])], PROJ,
            "<p>Les projections sont égales : les roues (1) et (4), encastrées sur l'arbre, forment un seul solide.</p>"),
        ETQ("Q5", "Établis une conclusion générale.", [("Conclusion", CONCL[0])], CONCL,
            "<p>C'est la propriété d'<strong>équiprojectivité</strong> : pour deux points A et B d'un même solide, les "
            "vitesses ont la même projection orthogonale sur la droite (AB). Elle traduit que la distance AB ne change "
            "pas : le solide est indéformable.</p>", titre="Conclusions"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>Un arbre de transmission est en liaison encastrement avec plusieurs roues dentées de diamètres "
        "différents. L'ensemble tourne dans le sens horaire autour de l'axe (O, <span class=vec>z</span>), à 1 000 tr/min.</p>"
        "<p>Sur le document réponse, les cercles représentent les trajectoires des dentures A et B de la roue (4) et "
        "de la denture C de la roue (1).</p>"
        + donnees("Ø<sub>1</sub> = 50 mm (roue 1) et Ø<sub>4</sub> = 100 mm (roue 4)", "N<sub>4/0</sub> = N<sub>1/0</sub> = 1 000 tr/min, sens horaire",
                  "Échelle des vitesses : 10 mm pour 1 m/s ; dessin à l'échelle 1:1")
        + "</div>" + "__FIG:photo-arbre|Arbre de transmission et ses roues dentées (1) et (4)|Roues (1) et (4) encastrées sur l'arbre.|300__</div>"]
    return {"key": "arbre-transmission", "prefix": "a", "partie": "graphique", "tag": "Activité 2.1", "title": "Arbre de transmission",
            "mots": ["Rotation", "V = R·ω", "Projection", "Équiprojectivité"], "methode": "Rotation",
            "sub": "Une seule vitesse de rotation, trois points : tracer les vitesses de dentures à l'échelle, les "
                   "projeter sur la droite qui les joint et découvrir l'équiprojectivité.",
            "hero": ("photo-arbre", "Arbre de transmission avec ses roues dentées", "Arbre de transmission : roues (1) et (4)."),
            "docs": ["DP-arbre", "DT1"],
            "parts": [{"title": "Vitesses des points d'un arbre en rotation", "minutes": 30, "intro": intro, "meca": m,
                       "noms": [nom("A", "4/0"), nom("B", "4/0"), nom("C", "1/0")], "blocks": blocks}]}


# ====================================================================== 2.2 — EMBIELLAGE DE MOTO
def embiellage():
    m = mc.embiellage()
    A, B, C, D, s = m.A, m.B, m.C, m.D, m.s
    blocks = [
        Q("Q1 a)", f"Détermine la norme {N('B', '1/0')}.", "Arrondis au dixième ; saisis la valeur avec son unité.",
          NUM(m.vb, "m/s", 0.015), f"{N('B', '1/0')} = {fr(m.vb, 1)} m/s",
          f"<p>Le vilebrequin (1) tourne autour de A : ω = 2π × 7 500 / 60 = {fr(m.w, 1)} rad/s ; "
          f"V = AB·ω = 0,039 × {fr(m.w, 1)} = <strong>{fr(m.vb, 1)} m/s</strong>, soit {fr(m.vb * s, 1)} mm à l'échelle "
          "10 mm pour 5 m/s.</p>"),
        TRACE("Q1 b)", f"Trace {V('B', '1/0')} : point d'application, direction, sens et norme.", H_VE,
              [IT_VE(B, m.VB, nom("B", "1/0"))], [C_SG(A, B), C_VE(B, m.VB, nom("B", "1/0"))],
              "<p>Point d'application B ; direction perpendiculaire à (AB) ; sens donné par N<sub>1/0</sub> (sens "
              f"trigonométrique) ; longueur {fr(m.vb * s, 1)} mm.</p>"),
        ETQ("Q2", f"Compare {V('B', '1/0')}, {V('B', '2/0')} et {V('B', '3/0')}.",
            [("Les trois vitesses du point B", "Égales")], COMPAR,
            "<p>B est le centre des liaisons pivots entre le vilebrequin (1) et chacune des bielles (2) et (3) : en ce "
            f"point, les trois solides ont la même vitesse. {V('B', '1/0')} = {V('B', '2/0')} = {V('B', '3/0')}.</p>"),
        TRACE("Q3 a)", f"Par la méthode de l'équiprojectivité, détermine {V('C', '2/0')}.",
              "Le support de la vitesse de C est l'axe du cylindre (le piston 5 est en translation). Construis, puis "
              "trace le vecteur et nomme-le.", [IT_VE(C, m.VC, nom("C", "2/0"))],
              corr_equiprojectivite(B, m.VB, C, m.VC, nom("B", "2/0"), nom("C", "2/0")),
              f"<ol><li>{V('B', '2/0')} = {V('B', '1/0')} est connu.</li><li>Le support de {V('C', '2/0')} = {V('C', '5/0')} "
              "est l'axe du cylindre.</li><li>On projette l'extrémité de V(B) sur (BC) ; on reporte la même longueur à "
              "partir de C ; la perpendiculaire à (BC) coupe le support : c'est l'extrémité de V(C).</li></ol>"
              f"<p>Longueur obtenue : {fr(g.norm(m.VC), 1)} mm.</p>"),
        Q("Q3 b)", f"Mesure et donne {N('C', '2/0')}.", "Lis la longueur de ton vecteur (outil Mesurer ou barre du "
          "vecteur), puis applique l'échelle.", NUM(g.norm(m.VC) / s, "m/s", 0.06),
          f"{N('C', '2/0')} ≈ {fr(g.norm(m.VC) / s, 1)} m/s",
          f"<p>{fr(g.norm(m.VC), 1)} mm × (5 m/s pour 10 mm) = {fr(g.norm(m.VC) / s, 1)} m/s. À cet instant, le piston "
          "(5) descend un peu plus vite que le maneton B ne tourne.</p>"),
        TRACE("Q4 a)", f"De la même façon, détermine {V('D', '3/0')}.", "Support : l'axe du cylindre de gauche.",
              [IT_VE(D, m.VD, nom("D", "3/0"))],
              corr_equiprojectivite(B, m.VB, D, m.VD, nom("B", "3/0"), nom("D", "3/0")),
              f"<p>Même construction avec la droite (BD) : {fr(g.norm(m.VD), 1)} mm, le piston (5') monte.</p>"),
        Q("Q4 b)", f"Donne {N('D', '3/0')}.", "Valeur lue sur ton tracé, avec son unité.",
          NUM(g.norm(m.VD) / s, "m/s", 0.07), f"{N('D', '3/0')} ≈ {fr(g.norm(m.VD) / s, 1)} m/s",
          f"<p>{fr(g.norm(m.VD), 1)} mm, soit {fr(g.norm(m.VD) / s, 1)} m/s.</p>"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>Un embiellage de moto disposé en V à 90° se compose d'un vilebrequin (1), de deux bielles (2) et (3) et de "
        "deux pistons (5) et (5'). Le mécanisme occupe la position du schéma ; G est le centre de gravité de la bielle "
        "(2), avec BG = BC/3.</p>"
        + donnees("N<sub>1/0</sub> = 7 500 tr/min (sens indiqué sur le schéma) et AB = 39 mm",
                  "Échelle des vitesses : 10 mm pour 5 m/s ; schéma à l'échelle 1:2") + "</div>"
        "__FIG:photo-embiellage|Coupe d'un cylindre de l'embiellage : piston, bielle, vilebrequin|Coupe d'un cylindre (dossier DP1).|190__</div>"]
    return {"key": "embiellage-moto", "prefix": "b", "partie": "graphique", "tag": "Activité 2.2", "title": "Embiellage de moto",
            "mots": ["Bielle-manivelle", "Équiprojectivité", "Moteur en V"], "methode": "Équiprojectivité",
            "sub": "Un vilebrequin, deux bielles, deux pistons : de la vitesse du maneton, déduire celle de chaque piston "
                   "par équiprojectivité.",
            "hero": ("photo-embiellage", "Coupe de l'embiellage de moto", "Coupe d'un cylindre de l'embiellage."),
            "docs": ["DP-embiellage", "DT1"],
            "parts": [{"title": "Vitesses des pistons d'un moteur en V", "minutes": 30, "intro": intro, "meca": m,
                       "noms": [nom("B", "1/0"), nom("B", "2/0"), nom("C", "2/0"), nom("D", "3/0")], "blocks": blocks}]}


# ====================================================================== 2.3 — POMPE À PÉTROLE BRUT
def pompe():
    m = mc.pompe()
    A, B, C, D, E, s = m.A, m.B, m.C, m.D, m.E, m.s
    ve = g.norm(m.VE) / s
    DEBIT = ["S, l'aire de la section du cylindre (en m²)", "D, le diamètre du cylindre (en m)",
             "C, la course du piston (en m)", "t, la durée d'un cycle (en s)"]
    blocks = [
        ETQ("Q1 a)", "Quelle est la nature du mouvement de 1/0 ?", [("Mouvement de 1/0", "Rotation")], NATURES,
            "<p>La manivelle (1) est en liaison pivot d'axe A avec le réducteur, fixe : 1/0 est une rotation de centre A.</p>",
            titre="Mouvements"),
        TRACE("Q1 b)", f"Déduis-en et trace la direction de {V('B', '1/0')}.", H_DIR,
              [IT_DIR(B, g.perp(g.sub(B, A)), "Direction de " + nom("B", "1/0"))], [C_SG(A, B), C_DR(B, g.perp(g.sub(B, A)), "res")],
              "<p>Trajectoire de B : un cercle de centre A ; la vitesse est tangente, donc perpendiculaire à (AB).</p>"),
        Q("Q2 a)", f"La manivelle tourne à 15 tr/min. Détermine {N('B', '1/0')}.", "Au millième ; avec l'unité.",
          NUM(m.vb, "m/s", 0.02), f"{N('B', '1/0')} = {fr(m.vb, 3)} m/s",
          f"<p>ω = 2π × 15 / 60 = {fr(m.w1, 3)} rad/s ; V = AB·ω = 0,570 × {fr(m.w1, 3)} = <strong>{fr(m.vb, 3)} m/s</strong>, "
          f"soit {fr(m.vb * s, 1)} mm à l'échelle 10 mm pour 0,2 m/s.</p>"),
        TRACE("Q2 b)", f"Trace {V('B', '1/0')}.", H_VE + " La manivelle tourne dans le sens horaire.",
              [IT_VE(B, m.VB, nom("B", "1/0"))], [C_VE(B, m.VB, nom("B", "1/0"))],
              f"<p>Sur la direction tracée, dans le sens horaire autour de A : {fr(m.vb * s, 1)} mm.</p>"),
        ETQ("Q3 a)", "Quelle est la nature du mouvement de 3/0 ?", [("Mouvement de 3/0", "Rotation")], NATURES,
            "<p>La tête de cheval (3) est en liaison pivot en D avec la structure fixe : rotation de centre D.</p>",
            titre="Mouvements"),
        TRACE("Q3 b)", f"Déduis-en et trace la direction de {V('C', '3/0')}.", H_DIR,
              [IT_DIR(C, g.perp(g.sub(C, D)), "Direction de " + nom("C", "3/0"))], [C_SG(D, C), C_DR(C, g.perp(g.sub(C, D)), "res")],
              "<p>Perpendiculaire au rayon (DC).</p>"),
        ETQ("Q4", "Compare les vitesses.", [(f"{V('B', '1/0')} et {V('B', '2/0')}", "Égales"),
                                            (f"{V('C', '3/0')} et {V('C', '2/0')}", "Égales")], COMPAR,
            "<p>B est le centre de la liaison pivot 1/2, C celui de la liaison pivot 2/3 : en chacun de ces points, les "
            "deux solides liés ont la même vitesse.</p>"),
        TRACE("Q5 a)", f"Connaissant {V('B', '2/0')}, détermine par équiprojectivité {V('C', '2/0')}.",
              "Équiprojectivité entre B et C sur la biellette (2) ; le support de V(C) est la direction tracée à la Q3.",
              [IT_VE(C, m.VC, nom("C", "2/0"))], corr_equiprojectivite(B, m.VB, C, m.VC, nom("B", "2/0"), nom("C", "2/0")),
              f"<p>Projection de V(B) sur (BC), report en C, perpendiculaire à (BC) : {fr(g.norm(m.VC), 1)} mm.</p>"),
        Q("Q5 b)", f"Donne {N('C', '2/0')}.", "Valeur lue sur ton tracé, avec son unité.",
          NUM(g.norm(m.VC) / s, "m/s", 0.07), f"{N('C', '2/0')} ≈ {fr(g.norm(m.VC) / s, 2)} m/s",
          f"<p>{fr(g.norm(m.VC), 1)} mm × 0,2 / 10 = {fr(g.norm(m.VC) / s, 2)} m/s.</p>"),
        TRACE("Q6 a)", f"Déduis-en {V('E', '3/0')}.",
              "La tête de cheval tourne autour de D : les vitesses de ses points sont proportionnelles à leur distance à D "
              "(reporte DC sur [DE] au compas, puis trace la droite de proportionnalité).",
              [IT_VE(E, m.VE, nom("E", "3/0"))], corr_triangle(D, C, m.VC, E, m.VE, nom("C", "3/0"), nom("E", "3/0")),
              f"<p>V(E) = V(C) × DE / DC = {fr(g.norm(m.VC) / s, 3)} × 3 400 / 2 310 = {fr(ve, 3)} m/s, verticale (perpendiculaire "
              f"à DE), vers le haut : {fr(g.norm(m.VE), 1)} mm.</p>"),
        Q("Q6 b)", f"Donne {N('E', '3/0')}.", "Avec son unité.", NUM(ve, "m/s", 0.07), f"{N('E', '3/0')} ≈ {fr(ve, 2)} m/s",
          f"<p>{fr(g.norm(m.VE), 1)} mm, soit {fr(ve, 2)} m/s.</p>"),
        ETQ("Q6 c)", f"Compare {V('E', '4/0')} et {V('E', '3/0')}.", [(f"{V('E', '4/0')} et {V('E', '3/0')}", "Égales")],
            COMPAR, "<p>Le câble (4) quitte la tête en E, tangent à l'arc de rayon DE : inextensible, il a en E la "
            "vitesse du point de la tête qui s'y trouve. Le piston monte à cette même vitesse.</p>"),
        ETQ("Q7 a)", "Le débit s'écrit q = V × … Complète la formule.", [("q = V ×", DEBIT[0])], DEBIT,
            "<p>q (m³/s) = V (m/s) × S (m²) : le piston balaie chaque seconde un volume égal à la section du cylindre "
            "multipliée par sa vitesse.</p>", titre="Grandeurs"),
        Q("Q7 b)", "Le cylindre (5) a un alésage de 100 mm. Calcule le débit instantané q dans la position du dessin.",
          "En m³/s (notation scientifique acceptée, 6,2e-3 par exemple) ou en L/s.",
          NUM(m.q, "m3/s", 0.08, [(m.q * 1000, "L/s")]), f"q ≈ {fr(m.q * 1000, 1)}·10⁻³ m³/s, soit {fr(m.q * 1000, 1)} L/s",
          f"<p>S = π × 0,100² / 4 = {fr(m.S * 1e3, 2)}·10⁻³ m² ; q = {fr(ve, 3)} × {fr(m.S * 1e3, 2)}·10⁻³ = "
          f"<strong>{fr(m.q * 1000, 2)}·10⁻³ m³/s</strong> ({fr(m.q * 1000, 1)} L/s).</p>"),
    ]
    intro = [
        '<div class="cours-split"><div>'
        "<p>La pompe à pétrole est utilisée lorsque la pression de la nappe ne suffit pas à l'extraction. Le câble (4), "
        "fixé d'une part sur le piston qui coulisse dans le cylindre (5) et d'autre part en N sur la tête de cheval (3), "
        "lui donne un mouvement vertical de va-et-vient. La tête (3), en liaison pivot en D sur la structure fixe (0), est "
        "commandée en C par la biellette (2), elle-même manœuvrée en B par la manivelle (1), en liaison pivot en A avec "
        "le réducteur. La liaison en B peut coulisser le long de AB (rainure oblongue) : on règle ainsi le débit.</p>"
        + donnees("AB = 570 mm ; BC = 2 640 mm ; CD = 2 310 mm ; DE = 3 400 mm", "N<sub>1/0</sub> = 15 tr/min, uniforme, sens horaire",
                  "Échelle des vitesses : 10 mm pour 0,2 m/s ; dessin à l'échelle 1:40") + "</div>"
        "__FIG:photo-pompe|Pompe à pétrole « tête de cheval » : manivelle, biellette, balancier et câble|La pompe (figure 1 de la séquence).|330__</div>"]
    return {"key": "pompe-petrole", "prefix": "c", "partie": "graphique", "tag": "Activité 2.3", "title": "Pompe à pétrole brut",
            "mots": ["Rotation", "Équiprojectivité", "Débit"], "methode": "Équiprojectivité",
            "sub": "De la manivelle à la tête de cheval : vitesse du câble par équiprojectivité, puis débit de pétrole "
                   "dans la position étudiée.",
            "hero": ("photo-pompe", "Pompe à pétrole à tête de cheval", "La pompe à tête de cheval."),
            "docs": ["DP-pompe", "DT1"],
            "parts": [{"title": "Vitesse du câble et débit de la pompe", "minutes": 45, "intro": intro, "meca": m,
                       "noms": [nom("B", "1/0"), nom("B", "2/0"), nom("C", "2/0"), nom("C", "3/0"), nom("E", "3/0"), nom("E", "4/0")],
                       "blocks": blocks}]}


# ====================================================================== 2.4 — ELLIPSOGRAPHE
def ellipsographe():
    m = mc.ellipsographe()
    A, B, Mc, I, s = m.A, m.B, m.Mc, m.I, m.s
    blocks = [
        ETQ("Q1 a)", "Quelle est la nature du mouvement de 1/0 ?", [("Mouvement de 1/0", "Translation rectiligne")], NATURES,
            "<p>La coulisse (1) se déplace dans une rainure rectiligne du bâti (liaison glissière) : translation rectiligne "
            "de direction <span class=vec>x</span>.</p>", titre="Mouvements"),
        TRACE("Q1 b)", "Trace la trajectoire de A∈1/0.", "Une droite passant par A.",
              [IT_DIR(A, (1, 0), "Trajectoire de A∈1/0")], [C_DR(A, (1, 0), "res")],
              "<p>La droite (A, <span class=vec>x</span>) : l'axe de la rainure horizontale.</p>"),
        ETQ("Q2 a)", "Quelle est la nature du mouvement de 3/0 ?", [("Mouvement de 3/0", "Translation rectiligne")], NATURES,
            "<p>Translation rectiligne de direction <span class=vec>y</span> (rainure verticale).</p>", titre="Mouvements"),
        TRACE("Q2 b)", "Trace la trajectoire de B∈3/0.", "Une droite passant par B.",
              [IT_DIR(B, (0, 1), "Trajectoire de B∈3/0")], [C_DR(B, (0, 1), "res")], "<p>La droite (B, <span class=vec>y</span>).</p>"),
        TRACE("Q3", f"Trace {V('A', '1/0')} à l'échelle.", "‖V(A∈1/0)‖ = 3 cm/s, dans le sens positif de <span class=vec>x</span>. " + H_VE,
              [IT_VE(A, m.VA, nom("A", "1/0"))], [C_VE(A, m.VA, nom("A", "1/0"))],
              "<p>Sur la trajectoire de A, vers la droite, 30 mm (10 mm pour 1 cm/s).</p>"),
        ETQ("Q4", "Compare les vitesses.", [(f"{V('A', '1/0')} et {V('A', '2/0')}", "Égales"),
                                            (f"{V('B', '3/0')} et {V('B', '2/0')}", "Égales")], COMPAR,
            "<p>A est le centre de la liaison pivot 1/2, B celui de la liaison pivot 3/2.</p>"),
        ETQ("Q5", "Quelle est la nature du mouvement de 2/0 ?", [("Mouvement de 2/0", "Mouvement plan")], NATURES,
            "<p>Les vitesses de A et de B, deux points de la barre (2), n'ont pas la même direction : ce n'est pas une "
            "translation ; aucun point de (2) n'est fixe : ce n'est pas une rotation. C'est un mouvement plan.</p>",
            titre="Mouvements"),
        TRACE("Q6", "Détermine le CIR I2/0.", "Les perpendiculaires aux supports de V(A∈2/0) et V(B∈2/0) se coupent en "
              "I2/0. " + H_PT, [IT_PT(I, "I2/0", "Point I2/0", tol_cir(I, A, B))],
              corr_cir(I, [(A, (1, 0)), (B, (0, 1))], "I2/0"),
              "<p>Perpendiculaire à <span class=vec>x</span> en A et perpendiculaire à <span class=vec>y</span> en B : I2/0 est le quatrième sommet du rectangle "
              "construit sur O, A et B.</p>"),
        TRACE("Q7", f"Détermine la direction de {V('M', '2/0')}.", "Elle est perpendiculaire à (I2/0 M).",
              [IT_DIR(Mc, g.perp(g.sub(Mc, I)), "Direction de " + nom("M", "2/0"))],
              [C_SG(I, Mc), C_DR(Mc, g.perp(g.sub(Mc, I)), "res")],
              "<p>À l'instant étudié, la barre tourne autour de I2/0 : la vitesse de M est perpendiculaire au rayon IM.</p>"),
        TRACE("Q8 a)", f"Par la méthode du CIR, détermine {V('M', '2/0')}.",
              "Reporte IM sur la droite (IA) au compas, trace la droite de proportionnalité passant par I et l'extrémité de "
              "V(A), puis reporte la vitesse obtenue en M, perpendiculairement à (IM).",
              [IT_VE(Mc, m.VM, nom("M", "2/0"))], corr_triangle(I, A, m.VA, Mc, m.VM, nom("A", "2/0"), nom("M", "2/0")),
              f"<p>V(M) = V(A) × IM / IA = 3 × {fr(g.dist(I, Mc), 1)} / {fr(g.dist(I, A), 1)} = {fr(g.norm(m.VM) / s, 2)} cm/s : "
              f"{fr(g.norm(m.VM), 1)} mm.</p>"),
        Q("Q8 b)", f"Donne {N('M', '2/0')}.", "Avec son unité.", NUM(g.norm(m.VM) / s, "cm/s", 0.06),
          f"{N('M', '2/0')} ≈ {fr(g.norm(m.VM) / s, 1)} cm/s", f"<p>{fr(g.norm(m.VM), 1)} mm, soit {fr(g.norm(m.VM) / s, 2)} cm/s.</p>"),
        TRACE("Q9 a)", f"Par la même méthode, détermine {V('B', '2/0')}.", "Même construction avec le point B.",
              [IT_VE(B, m.VB, nom("B", "2/0"))], corr_triangle(I, A, m.VA, B, m.VB, nom("A", "2/0"), nom("B", "2/0")),
              f"<p>V(B) = 3 × IB / IA = {fr(g.norm(m.VB) / s, 2)} cm/s, vers le haut : la coulisse (3) monte quand (1) "
              "avance vers O.</p>"),
        Q("Q9 b)", f"Donne {N('B', '2/0')}.", "Avec son unité.", NUM(g.norm(m.VB) / s, "cm/s", 0.06),
          f"{N('B', '2/0')} ≈ {fr(g.norm(m.VB) / s, 1)} cm/s", f"<p>{fr(g.norm(m.VB), 1)} mm, soit {fr(g.norm(m.VB) / s, 2)} cm/s.</p>"),
    ]
    intro = [
        "<p>L'ellipsographe sert à tracer des ellipses. Il se compose d'une barre porte-mine (2), articulée (liaison "
        "pivot) en A et en B sur deux coulisses (1) et (3). Ces coulisses se déplacent dans deux rainures "
        "perpendiculaires du bâti (0) (liaisons glissières). Le crayon, placé en M, décrit une ellipse.</p>"
        + donnees("‖V(A∈1/0)‖ = 3 cm/s ; la coulisse (1) se déplace dans le sens positif de <span class=vec>x</span>",
                  "Échelle des vitesses : 10 mm pour 1 cm/s",
                  "Objectif : déterminer les vitesses de déplacement des points M et B")]
    return {"key": "ellipsographe", "prefix": "d", "partie": "graphique", "tag": "Activité 2.4", "title": "Ellipsographe",
            "mots": ["Translation", "Mouvement plan", "CIR"], "methode": "CIR",
            "sub": "Deux coulisses, une barre porte-mine : trouver le centre instantané de rotation de la barre et en "
                   "déduire la vitesse du crayon.",
            "hero": None, "docs": ["DT1"],
            "parts": [{"title": "Vitesse du crayon d'un ellipsographe", "minutes": 40, "intro": intro, "meca": m,
                       "noms": [nom("A", "1/0"), nom("A", "2/0"), nom("B", "2/0"), nom("M", "2/0"), "I2/0"], "blocks": blocks}]}


# ====================================================================== 2.5 — PORTAIL À VIS
def portail():
    m = mc.portail()
    A, B, C, Mp, I, s = m.A, m.B, m.C, m.Mp, m.I24, m.s
    vb, vm = g.norm(m.VB) / s, g.norm(m.VM) / s
    CIR14 = ["Le point A", "Le point B", "Le point C", "Le point M"]
    blocks = [
        ETQ("Q1", "Quelle est la nature du mouvement de 3/4 ?", [("Mouvement de 3/4", "Translation rectiligne")], NATURES,
            "<p>L'écrou (3), entraîné par la vis (5) et guidé en rotation, se déplace le long de l'axe de la vis : "
            "translation rectiligne.</p>", titre="Mouvements"),
        Q("Q2 a)", f"Détermine {N('C', '3/4')}.", "En m/s, avec l'unité.",
          NUM(0.06, "m/s", 0.01, [(60, "mm/s"), (6, "cm/s")]), f"{N('C', '3/4')} = 0,06 m/s",
          "<p>À chaque tour, l'écrou avance d'un pas : V = p × N = 6 mm × 600 / 60 tr/s = 60 mm/s = <strong>0,06 m/s"
          "</strong>, soit 3 cm à l'échelle 1 cm pour 0,02 m/s.</p>"),
        TRACE("Q2 b)", f"Trace {V('C', '3/4')}.", "À la fermeture, l'écrou se rapproche du moteur. " + H_VE,
              [IT_VE(C, m.VC, nom("C", "3/4"))], [C_VE(C, m.VC, nom("C", "3/4"))],
              "<p>Parallèle à la vis, vers le moteur (sens de <span class=vec>y</span>), 30 mm.</p>"),
        ETQ("Q3", "Quelle est la nature du mouvement de 1/4 ?", [("Mouvement de 1/4", "Rotation")], NATURES,
            "<p>Le portail (1) est en liaison pivot d'axe A avec le pilier : rotation de centre A.</p>", titre="Mouvements"),
        TRACE("Q4", f"Détermine la direction de {V('B', '1/4')}.", H_DIR,
              [IT_DIR(B, g.perp(g.sub(B, A)), "Direction de " + nom("B", "1/4"))], [C_SG(A, B), C_DR(B, g.perp(g.sub(B, A)), "res")],
              "<p>Perpendiculaire au rayon (AB).</p>"),
        ETQ("Q5", "Quelle est la nature du mouvement de 2/4 ?", [("Mouvement de 2/4", "Mouvement plan")], NATURES,
            "<p>La bielle (2) n'a ni point fixe ni direction conservée : mouvement plan.</p>", titre="Mouvements"),
        TRACE("Q6", "Détermine le CIR I2/4.", "Perpendiculaires aux supports de V(C∈2/4) = V(C∈3/4) et de V(B∈2/4) = "
              "V(B∈1/4). " + H_PT, [IT_PT(I, "I2/4", "Point I2/4", tol_cir(I, B, C))],
              corr_cir(I, [(C, m.VC), (B, g.perp(g.sub(B, A)))], "I2/4"),
              "<p>La perpendiculaire en C à la vis et la droite (AB) (perpendiculaire en B à la direction de V(B)) se "
              "coupent en I2/4.</p>"),
        TRACE("Q7 a)", f"Détermine graphiquement, par la méthode de ton choix, {V('B', '1/4')}.",
              "CIR I2/4 ou équiprojectivité entre C et B sur la bielle (2).", [IT_VE(B, m.VB, nom("B", "1/4"))],
              corr_triangle(I, C, m.VC, B, m.VB, nom("C", "2/4"), nom("B", "2/4")),
              f"<p>V(B) = V(C) × I B / I C = 0,06 × {fr(g.dist(I, B), 1)} / {fr(g.dist(I, C), 1)} = {fr(vb, 3)} m/s, soit "
              f"{fr(g.norm(m.VB), 1)} mm. L'équiprojectivité entre C et B donne le même vecteur.</p>"),
        Q("Q7 b)", f"Donne {N('B', '1/4')}.", "Avec son unité.", NUM(vb, "m/s", 0.07), f"{N('B', '1/4')} ≈ {fr(vb, 3)} m/s",
          f"<p>{fr(g.norm(m.VB), 1)} mm × 0,02 / 10 = {fr(vb, 3)} m/s.</p>"),
        ETQ("Q8", "Où est le CIR I1/4 ?", [("I1/4", "Le point A")], CIR14,
            "<p>Le portail tourne autour de l'axe fixe A : son centre de rotation, instantané ou non, est A.</p>",
            titre="Positions"),
        TRACE("Q9 a)", f"Par la méthode du CIR, détermine {V('M', '1/4')}.",
              "Répartition linéaire des vitesses le long de (AM) : reporte AB sur (AM) au compas.",
              [IT_VE(Mp, m.VM, nom("M", "1/4"))], corr_triangle(A, B, m.VB, Mp, m.VM, nom("B", "1/4"), nom("M", "1/4")),
              f"<p>V(M) = V(B) × AM / AB = {fr(vb, 3)} × {fr(g.dist(A, Mp), 1)} / {fr(g.dist(A, B), 1)} = {fr(vm, 3)} m/s "
              f"({fr(g.norm(m.VM), 1)} mm).</p>"),
        Q("Q9 b)", f"Donne {N('M', '1/4')}.", "Avec son unité.", NUM(vm, "m/s", 0.07), f"{N('M', '1/4')} ≈ {fr(vm, 2)} m/s",
          f"<p>{fr(g.norm(m.VM), 1)} mm, soit {fr(vm, 3)} m/s.</p>"),
        Q("Q10", "En relevant les dimensions sur le dessin (échelle 1:10), détermine la vitesse angulaire ω1/4.",
          "En rad/s, avec l'unité.", NUM(m.w, "rad/s", 0.07), f"ω1/4 ≈ {fr(m.w, 3)} rad/s",
          f"<p>AB mesure {fr(g.dist(A, B), 1)} mm sur le dessin, soit {fr(g.dist(A, B) * 10, 0)} mm en réalité ; "
          f"ω = V(B) / AB = {fr(vb, 4)} / {fr(g.dist(A, B) / 100, 3)} = <strong>{fr(m.w, 3)} rad/s</strong>.</p>"),
        TRACE("Q11", "Trace la position fermée du portail et place les images B' et C' des points B et C.",
              "Le portail fermé est sur la droite « position portail fermé » ; B tourne autour de A (compas de rayon AB) ; "
              "C reste sur sa trajectoire parallèle à la vis, à la distance BC de B'.",
              [IT_PT(m.Bf, "B'", "Point B'", 2.5), IT_PT(m.Cf, "C'", "Point C'", 2.5)],
              [C_CI(A, g.dist(A, B)), C_SG(A, g.add(A, (0, g.dist(A, Mp)))), C_PT(m.Bf, "B'"), C_CI(m.Bf, g.dist(B, C)),
               C_PT(m.Cf, "C'"), C_SG(m.Bf, m.Cf, "res")],
              f"<p>B' : rotation de B autour de A, du même angle que le portail ({fr(-m.rot, 1)}°). C' : intersection du "
              f"cercle de centre B' et de rayon BC avec la trajectoire de C.</p>"),
        Q("Q12", "À partir de la position donnée, combien de tours le moteur doit-il effectuer pour fermer le portail ?",
          "Mesure le déplacement CC' sur le dessin, puis tiens compte de l'échelle, du pas de la vis et du train "
          "d'engrenages (90 et 270 dents).", NUM(m.tours_moteur, "tours", 0.06),
          f"environ {fr(m.tours_moteur, 0)} tours",
          f"<p>CC' = {fr(m.course / 10, 1)} mm sur le dessin, soit {fr(m.course, 0)} mm. Tours de vis : {fr(m.course, 0)} / 6 = "
          f"{fr(m.tours_vis, 1)}. Le pignon moteur (90 dents) entraîne la roue de la vis (270 dents) : le moteur fait "
          f"270 / 90 = 3 fois plus de tours, soit <strong>{fr(m.tours_moteur, 0)} tours</strong>.</p>"),
    ]
    intro = [
        "<p>La figure représente un portail (1), en vue de dessus, actionné par une bielle (2) articulée en C sur l'écrou "
        "(3) et en B sur le portail (1). L'écrou (3) est entraîné par la rotation de la vis (5), qui tourne à 600 tr/min "
        "et dont le pas est de 6 mm. La vis est mise en rotation par un moteur électrique et un train d'engrenages "
        "cylindriques dont les roues ont 90 et 270 dents. L'étude porte sur la fermeture du portail.</p>"
        + donnees("Vis (5) : N<sub>5/4</sub> = 600 tr/min, pas p = 6 mm", "Engrenage : pignon moteur 90 dents, roue de la vis 270 dents",
                  "Dessin à l'échelle 1:10 ; échelle des vitesses : 1 cm pour 0,02 m/s")]
    return {"key": "portail-vis", "prefix": "e", "partie": "graphique", "tag": "Activité 2.5", "title": "Portail à vis",
            "mots": ["Vis-écrou", "CIR", "Position fermée", "Engrenages"], "methode": "CIR",
            "sub": "Un écrou qui avance sur sa vis, une bielle, un portail qui pivote : vitesses par le CIR, vitesse "
                   "angulaire et nombre de tours du moteur pour fermer.",
            "hero": None, "docs": ["DT1"],
            "parts": [{"title": "Fermeture d'un portail à vis", "minutes": 60, "intro": intro, "meca": m,
                       "noms": [nom("C", "3/4"), nom("C", "2/4"), nom("B", "1/4"), nom("B", "2/4"), nom("M", "1/4"), "I2/4", "B'", "C'"],
                       "blocks": blocks}]}


# ====================================================================== 2.6 — CHARGEUR BOBCAT S185
def bobcat():
    m = mc.bobcat()
    P, s, I = m.P, m.s, m.I
    v54, v50, vh = g.norm(m.v54) / s / 1000, g.norm(m.v50) / s / 1000, g.norm(m.vH) / s / 1000
    SOL = {"0": ["0"], "1": ["1"], "2": ["2"], "3": ["3"], "4": ["4"], "5": ["5"]}
    blocks = [
        ETQ("Q1", "Quelle est la nature des mouvements ?",
            [("2/0", "Rotation"), ("3/0", "Rotation"), ("5/4", "Translation rectiligne"), ("4/0", "Rotation"),
             ("5/0", "Mouvement plan"), ("1/0", "Mouvement plan")], NATURES,
            "<p>2/0 : rotation de centre A ; 3/0 : rotation de centre F ; 5/4 : translation rectiligne (la tige coulisse "
            "dans le corps du vérin) ; 4/0 : rotation de centre D ; 5/0 et 1/0 : mouvements plans (aucun point fixe, "
            "aucune direction conservée).</p>", titre="Mouvements"),
        Q("Q2 a)", f"Calcule {N('C', '5/4')}.", "En m/s, au millième, avec l'unité.",
          NUM(v54, "m/s", 0.02, [(v54 * 1000, "mm/s")]), f"{N('C', '5/4')} = {fr(v54, 3)} m/s",
          f"<p>Vitesse de sortie constante : V = course / durée = 635 / 3,5 = {fr(v54 * 1000, 1)} mm/s = "
          f"<strong>{fr(v54, 3)} m/s</strong> ; à l'échelle 10 mm pour 50 mm/s : {fr(g.norm(m.v54), 1)} mm.</p>"),
        TRACE("Q2 b)", f"Trace {V('C', '5/4')}.", "Le long de l'axe du vérin (tracé en trait mixte), la tige sort. " + H_VE,
              [IT_VE(P["C"], m.v54, nom("C", "5/4"))], [C_VE(P["C"], m.v54, nom("C", "5/4"))],
              f"<p>Sur l'axe DC, de D vers C (la tige sort), {fr(g.norm(m.v54), 1)} mm.</p>"),
        TRACE("Q3", f"Trace et repère les directions de {V('B', '2/0')} et de {V('E', '3/0')}.", H_DIR,
              [IT_DIR(P["B"], g.perp(g.sub(P["B"], P["A"])), "Direction de " + nom("B", "2/0")),
               IT_DIR(P["E"], g.perp(g.sub(P["E"], P["F"])), "Direction de " + nom("E", "3/0"))],
              [C_SG(P["A"], P["B"]), C_DR(P["B"], g.perp(g.sub(P["B"], P["A"])), "res"), C_SG(P["F"], P["E"]),
               C_DR(P["E"], g.perp(g.sub(P["E"], P["F"])), "res")],
              "<p>2 tourne autour de A : V(B) ⊥ (AB). 3 tourne autour de F : V(E) ⊥ (FE).</p>"),
        ETQ("Q4", "Compare les vitesses.", [(f"{V('B', '2/0')} et {V('B', '1/0')}", "Égales"),
                                            (f"{V('E', '3/0')} et {V('E', '1/0')}", "Égales")], COMPAR,
            "<p>B est le centre de la liaison pivot 1/2, E celui de la liaison pivot 1/3.</p>"),
        TRACE("Q5", "Trace I1/0, le centre instantané de rotation de 1 dans son mouvement par rapport à 0.",
              "Les perpendiculaires aux directions de V(B∈1/0) et V(E∈1/0) sont les droites (AB) et (FE). " + H_PT,
              [IT_PT(I, "I1/0", "Point I1/0", tol_cir(I, P["B"], P["E"]))],
              [C_DR(P["A"], g.sub(P["B"], P["A"])), C_DR(P["F"], g.sub(P["E"], P["F"])), C_PT(I, "I1/0")],
              "<p>I1/0 est à l'intersection des droites (AB) et (FE), au-dessus du point B.</p>"),
        TRACE("Q6", f"Trace et repère les directions de {V('C', '1/0')} et de {V('H', '1/0')}.",
              "Perpendiculaires aux droites (I1/0 C) et (I1/0 H).",
              [IT_DIR(P["C"], g.perp(g.sub(P["C"], I)), "Direction de " + nom("C", "1/0")),
               IT_DIR(P["H"], g.perp(g.sub(P["H"], I)), "Direction de " + nom("H", "1/0"))],
              [C_SG(I, P["C"]), C_DR(P["C"], g.perp(g.sub(P["C"], I)), "res"), C_SG(I, P["H"]),
               C_DR(P["H"], g.perp(g.sub(P["H"], I)), "res")],
              "<p>À l'instant étudié, le bras (1) tourne autour de I1/0.</p>"),
        ETQ("Q7", f"Compare {V('C', '5/0')} et {V('C', '1/0')}.", [(f"{V('C', '5/0')} et {V('C', '1/0')}", "Égales")],
            COMPAR, "<p>C est le centre de la liaison pivot entre la tige (5) et le bras (1).</p>"),
        TRACE("Q8", f"Détermine et trace, en le justifiant, la direction de {V('C', '4/0')}.",
              "Le corps du vérin (4) tourne autour de D.",
              [IT_DIR(P["C"], g.perp(g.sub(P["C"], P["D"])), "Direction de " + nom("C", "4/0"))],
              [C_DR(P["C"], g.perp(g.sub(P["C"], P["D"])), "res")],
              "<p>4/0 est une rotation de centre D : V(C∈4/0) est perpendiculaire à (DC).</p>"),
        Q("Q9 a)", "Écris la composition des vitesses au point C.",
          "Par exemple V(C∈2/0) = V(C∈2/1) + V(C∈1/0) ; le bouton « ∈ » insère le symbole (une virgule convient aussi).",
          CHASLES(SOL), "V(C∈5/0) = V(C∈5/4) + V(C∈4/0)",
          "<p>Le mouvement de la tige (5) par rapport au bâti se compose de son mouvement par rapport au corps (4) et de "
          "celui du corps par rapport au bâti.</p>", ins=True),
        TRACE("Q9 b)", f"Détermine graphiquement {V('C', '5/0')}.",
              "V(C∈5/4) est connu ; V(C∈5/0) a la direction tracée à la Q6, V(C∈4/0) celle de la Q8 : construis le "
              "parallélogramme (outil Parallèle), puis trace le vecteur.",
              [IT_VE(P["C"], m.v50, nom("C", "5/0"), tolL=0.08)],
              [C_VE(P["C"], m.v54, nom("C", "5/4"), "aide"), C_DR(P["C"], g.perp(g.sub(P["C"], I))),
               C_DR(g.add(P["C"], m.v54), g.perp(g.sub(P["C"], P["D"]))), C_VE(g.add(P["C"], m.v54), m.v40, "", "aide"),
               C_VE(P["C"], m.v50, nom("C", "5/0"))],
              f"<p>Par l'extrémité de V(C∈5/4), on trace la parallèle à la direction de V(C∈4/0) ; elle coupe la direction "
              f"de V(C∈5/0) = V(C∈1/0) : {fr(g.norm(m.v50), 1)} mm, soit {fr(v50, 3)} m/s.</p>"),
        Q("Q9 c)", f"Donne {N('C', '5/0')}.", "Avec son unité.", NUM(v50, "m/s", 0.08, [(v50 * 1000, "mm/s")]),
          f"{N('C', '5/0')} ≈ {fr(v50, 2)} m/s", f"<p>{fr(g.norm(m.v50), 1)} mm × 50 / 10 = {fr(v50 * 1000, 0)} mm/s.</p>"),
        TRACE("Q10 a)", f"Par équiprojectivité, détermine {V('H', '1/0')}.",
              "Entre C et H, deux points du bras (1) : V(C∈1/0) = V(C∈5/0) est connu, la direction de V(H∈1/0) est "
              "tracée à la Q6.", [IT_VE(P["H"], m.vH, nom("H", "1/0"), tolL=0.08)],
              corr_equiprojectivite(P["C"], m.v50, P["H"], m.vH, nom("C", "1/0"), nom("H", "1/0")),
              f"<p>{fr(g.norm(m.vH), 1)} mm : prévois la place au-dessus du godet, le vecteur est long.</p>"),
        Q("Q10 b)", f"Donne {N('H', '1/0')}.", "Avec son unité.", NUM(vh, "m/s", 0.08, [(vh * 1000, "mm/s")]),
          f"{N('H', '1/0')} ≈ {fr(vh, 2)} m/s", f"<p>{fr(g.norm(m.vH), 1)} mm × 50 / 10 = {fr(vh * 1000, 0)} mm/s, soit "
          f"{fr(vh, 2)} m/s.</p>"),
        ETQ("Q10 c)", "Pour cette position, la condition de sécurité ‖V(H∈1/0)‖ ≤ 1,2 m/s est-elle respectée ?",
            [("Condition respectée", "Oui")], ["Oui", "Non"],
            f"<p>{fr(vh, 2)} m/s ≤ 1,2 m/s : la condition est respectée dans la position étudiée.</p>", titre="Réponses"),
    ]
    intro = [
        "<p><strong>Vérification du respect d'une condition de sécurité.</strong> L'étude porte sur le mouvement de sortie "
        "de la tige du vérin de levage, dans une position intermédiaire (entre les positions basse et haute) du système "
        "de levage, dessinée sur le document réponse.</p>"
        + donnees("Durée totale du levage : 3,5 s ; course d'un vérin de levage : 635 mm",
                  "Vitesse de sortie de la tige supposée constante : ‖V(C∈5/4)‖ = constante",
                  "Objectif : vérifier que ‖V(H∈1/0)‖ ≤ 1,2 m/s", "Échelle des vitesses : 10 mm pour 50 mm/s")
        + "<p class=\"small\">Repères : 0 bâti (châssis) ; 1 bras de levage ; 2 biellette arrière (A, B) ; 3 biellette "
        "avant (F, E) ; 4 corps du vérin ; 5 tige du vérin.</p>"]
    return {"key": "chargeur-bobcat", "prefix": "f", "partie": "graphique", "tag": "Activité 2.6", "title": "Chargeur Bobcat S185",
            "mots": ["CIR", "Composition", "Équiprojectivité", "Sécurité"], "methode": "Composition",
            "sub": "Le vérin de levage d'un chargeur compact : composer les vitesses au point C, puis vérifier la vitesse "
                   "du godet par rapport à une condition de sécurité.",
            "hero": None, "docs": ["DT1"],
            "parts": [{"title": "Vitesse du godet pendant le levage", "minutes": 50, "intro": intro, "meca": m,
                       "noms": [nom("C", "5/4"), nom("C", "5/0"), nom("C", "4/0"), nom("C", "1/0"), nom("H", "1/0"), "I1/0"],
                       "blocks": blocks}]}


# ====================================================================== 2.7 — SUSPENSION DU VTT VARIO BOMBA
def vtt():
    m = mc.vtt()
    f1, f2, f3 = m.f1, m.f2, m.f3
    P1, P2, P3 = f1.P, f2.P, f3.P
    CIR = ["Le point H", "Le point G", "Le point F", "Le point B"]
    SOL = {"s0": ["s0", "0"], "s1": ["s1", "1"], "s2": ["s2", "2"], "s3": ["s3", "3"], "s4": ["s4", "4"], "s5": ["s5", "5"]}
    vf, vd = g.norm(f1.VF) / f1.s, g.norm(f1.VD) / f1.s
    vc2 = g.norm(f2.VC) / f2.s
    v45 = g.norm(f3.V45) / f3.s
    axe = g.sub(P3["C"], P3["A"])
    p1 = [
        ETQ("Q1 a)", "Quelle est la nature du mouvement du bras oscillant S1/S0 ?", [("Mouvement de S1/S0", "Rotation")],
            NATURES, "<p>Le bras oscillant S1 est en liaison pivot d'axe H avec le cadre : rotation de centre H ; la "
            "trajectoire de G est un cercle de centre H.</p>", titre="Mouvements"),
        TRACE("Q1 b)", f"Définis la direction de {V('G', 'S1/S0')} et trace ce vecteur (30 m/s, la roue monte).", H_VE,
              [IT_VE(P1["G"], f1.VG, nom("G", "S1/S0"))], [C_SG(P1["H"], P1["G"]), C_VE(P1["G"], f1.VG, nom("G", "S1/S0"))],
              f"<p>Perpendiculaire à (HG), vers le haut (compression), 30 m/s : {fr(g.norm(f1.VG), 0)} mm à l'échelle 1 cm "
              "pour 6 m/s.</p>"),
        ETQ("Q2", "Où est le CIR I<sub>S1/S0</sub> ?", [("I S1/S0", "Le point H")], CIR,
            "<p>S1 tourne autour de l'axe fixe H.</p>", titre="Positions"),
        TRACE("Q3 a)", f"Par la méthode du CIR, détermine {V('F', 'S1/S0')}.",
              "Répartition linéaire autour de H : reporte HF sur (HG) au compas.", [IT_VE(P1["F"], f1.VF, nom("F", "S1/S0"))],
              corr_triangle(P1["H"], P1["G"], f1.VG, P1["F"], f1.VF, nom("G", "S1/S0"), nom("F", "S1/S0")),
              f"<p>V(F) = 30 × HF / HG = {fr(vf, 1)} m/s ({fr(g.norm(f1.VF), 1)} mm).</p>"),
        Q("Q3 b)", f"Donne {N('F', 'S1/S0')}.", "Avec son unité.", NUM(vf, "m/s", 0.07),
          f"{N('F', 'S1/S0')} ≈ {fr(vf, 1)} m/s", f"<p>{fr(g.norm(f1.VF), 1)} mm × 6 / 10 = {fr(vf, 1)} m/s.</p>"),
        ETQ("Q4 a)", "Quelle est la nature du mouvement du levier basculeur S3/S0 ?", [("Mouvement de S3/S0", "Rotation")],
            NATURES, "<p>Liaison pivot d'axe B avec le cadre : rotation de centre B.</p>", titre="Mouvements"),
        TRACE("Q4 b)", f"Trace le support de {V('D', 'S3/S0')}.", H_DIR,
              [IT_DIR(P1["D"], g.perp(g.sub(P1["D"], P1["B"])), "Direction de " + nom("D", "S3/S0"))],
              [C_SG(P1["B"], P1["D"]), C_DR(P1["D"], g.perp(g.sub(P1["D"], P1["B"])), "res")],
              "<p>Perpendiculaire à (BD).</p>"),
        ETQ("Q5", "Compare les vitesses.", [(f"{V('F', 'S1/S0')} et {V('F', 'S2/S0')}", "Égales"),
                                            (f"{V('D', 'S2/S0')} et {V('D', 'S3/S0')}", "Égales")], COMPAR,
            "<p>F est le centre de la liaison pivot S1/S2, D celui de la liaison pivot S2/S3.</p>"),
        TRACE("Q6 a)", f"Reporte {V('F', 'S1/S0')} en F et, par équiprojectivité, détermine {V('D', 'S3/S0')}.",
              "Équiprojectivité entre F et D sur la biellette S2.", [IT_VE(P1["D"], f1.VD, nom("D", "S3/S0"), tolL=0.08)],
              corr_equiprojectivite(P1["F"], f1.VF, P1["D"], f1.VD, nom("F", "S2/S0"), nom("D", "S3/S0")),
              f"<p>Projection sur (FD), report, perpendiculaire : {fr(g.norm(f1.VD), 1)} mm, soit {fr(vd, 1)} m/s.</p>"),
        Q("Q6 b)", f"Donne {N('D', 'S3/S0')}.", "Avec son unité.", NUM(vd, "m/s", 0.08),
          f"{N('D', 'S3/S0')} ≈ {fr(vd, 1)} m/s", f"<p>{fr(g.norm(f1.VD), 1)} mm × 6 / 10 = {fr(vd, 1)} m/s (la suite prend 20 m/s).</p>"),
    ]
    p2 = [
        HTML("<p class=\"remarque\">Quel que soit le résultat trouvé précédemment, prends pour la suite "
             f"{N('D', 'S3/S0')} = 20 m/s. Échelle de ce document réponse : 1 cm pour 5 m/s.</p>"),
        TRACE("Q7", f"Trace {V('D', 'S3/S0')} avec la norme donnée.", H_VE, [IT_VE(P2["D"], f2.VD, nom("D", "S3/S0"))],
              [C_SG(P2["B"], P2["D"]), C_VE(P2["D"], f2.VD, nom("D", "S3/S0"))],
              "<p>Perpendiculaire à (BD), dans le sens trouvé sur le document réponse 1, 40 mm.</p>"),
        TRACE("Q8 a)", f"Détermine graphiquement {V('C', 'S3/S0')}.", "Le levier S3 tourne autour de B : CIR (répartition "
              "linéaire) ou équiprojectivité entre D et C.", [IT_VE(P2["C"], f2.VC, nom("C", "S3/S0"))],
              corr_triangle(P2["B"], P2["D"], f2.VD, P2["C"], f2.VC, nom("D", "S3/S0"), nom("C", "S3/S0")),
              f"<p>V(C) = 20 × BC / BD = {fr(vc2, 1)} m/s ({fr(g.norm(f2.VC), 1)} mm).</p>"),
        Q("Q8 b)", f"Donne {N('C', 'S3/S0')}.", "Avec son unité.", NUM(vc2, "m/s", 0.07),
          f"{N('C', 'S3/S0')} ≈ {fr(vc2, 1)} m/s", f"<p>{fr(g.norm(f2.VC), 1)} mm × 5 / 10 = {fr(vc2, 1)} m/s.</p>"),
    ]
    p3 = [
        HTML("<p class=\"remarque\">Quel que soit le résultat trouvé précédemment, prends pour la suite "
             f"{N('C', 'S3/S0')} = 15 m/s. Échelle de ce document réponse : 1 cm pour 3 m/s.</p>"),
        TRACE("Q9", f"Trace {V('C', 'S3/S0')} avec la norme donnée.", H_VE, [IT_VE(P3["C"], f3.VC, nom("C", "S3/S0"))],
              [C_SG(P3["B"], P3["C"]), C_VE(P3["C"], f3.VC, nom("C", "S3/S0"))],
              "<p>Perpendiculaire à (BC), même sens de rotation du levier, 50 mm.</p>"),
        ETQ("Q10", f"Compare {V('C', 'S3/S0')} et {V('C', 'S4/S0')}.", [(f"{V('C', 'S3/S0')} et {V('C', 'S4/S0')}", "Égales")],
            COMPAR, "<p>C est le centre de la liaison pivot entre le levier S3 et la tige S4.</p>"),
        TRACE("Q11", f"Trace les directions de {V('C', 'S4/S5')} et de {V('C', 'S5/S0')}.", H_DIR,
              [IT_DIR(P3["C"], axe, "Direction de " + nom("C", "S4/S5")),
               IT_DIR(P3["C"], g.perp(axe), "Direction de " + nom("C", "S5/S0"))],
              [C_DR(P3["C"], axe, "res"), C_DR(P3["C"], g.perp(axe), "res")],
              "<p>S4/S5 : translation le long de l'axe de l'amortisseur (AC). S5/S0 : rotation de centre A, donc vitesse "
              "perpendiculaire à (AC).</p>"),
        Q("Q12", "Écris la relation de composition des vitesses au point C.",
          "Avec des V(C∈Si/Sj) ; le bouton « ∈ » insère le symbole (une virgule convient aussi).", CHASLES(SOL),
          "V(C∈S4/S0) = V(C∈S4/S5) + V(C∈S5/S0)",
          "<p>Le mouvement de la tige S4 par rapport au cadre se compose de son mouvement dans le corps S5 et du mouvement "
          "du corps par rapport au cadre.</p>", ins=True),
        TRACE("Q13 a)", f"Déduis-en graphiquement la vitesse de rentrée de l'amortisseur {V('C', 'S4/S5')}.",
              "Décompose V(C∈S4/S0) selon les deux directions de la Q11 (parallélogramme).",
              [IT_VE(P3["C"], f3.V45, nom("C", "S4/S5"), tolL=0.08)],
              [C_VE(P3["C"], f3.VC, nom("C", "S4/S0"), "aide"), C_DR(P3["C"], axe), C_DR(P3["C"], g.perp(axe)),
               C_SG(g.add(P3["C"], f3.VC), g.add(P3["C"], f3.V45)), C_SG(g.add(P3["C"], f3.VC), g.add(P3["C"], f3.V50)),
               C_VE(P3["C"], f3.V45, nom("C", "S4/S5")), C_VE(P3["C"], f3.V50, nom("C", "S5/S0"), "aide")],
              f"<p>Projection de V(C∈S4/S0) parallèlement à la direction de V(C∈S5/S0) : {fr(g.norm(f3.V45), 1)} mm, soit "
              f"{fr(v45, 1)} m/s, vers A (la tige rentre).</p>"),
        Q("Q13 b)", f"Donne {N('C', 'S4/S5')}.", "Avec son unité.", NUM(v45, "m/s", 0.08),
          f"{N('C', 'S4/S5')} ≈ {fr(v45, 1)} m/s", f"<p>{fr(g.norm(f3.V45), 1)} mm × 3 / 10 = {fr(v45, 1)} m/s.</p>"),
        ETQ("Q14", "Le critère du cahier des charges (vitesse de rentrée au plus 15 m/s) est-il respecté ?",
            [("Critère respecté", "Oui")], ["Oui", "Non"],
            f"<p>{fr(v45, 1)} m/s ≤ 15 m/s : le critère est validé pour cette position.</p>", titre="Réponses"),
    ]
    noms1 = [nom("G", "S1/S0"), nom("F", "S1/S0"), nom("F", "S2/S0"), nom("D", "S3/S0")]
    intro1 = [
        '<div class="cours-split"><div>'
        "<p>Conçu pour le « freeride » et la descente, ce VTT a une suspension arrière à triangle unifié. Le mécanisme "
        "doit absorber les irrégularités du terrain pour garder le contact entre les roues et le sol ; la vitesse "
        "maximale de rentrée de la tige de l'amortisseur doit rester limitée pour qu'il fonctionne correctement.</p>"
        "<p><strong>Objectif :</strong> calculer la vitesse de rentrée de la tige de l'amortisseur (S4 + S5), "
        "connaissant la vitesse de l'axe G de la roue S1 par rapport au cadre S0, et vérifier qu'elle ne dépasse pas "
        "15 m/s (cahier des charges).</p>"
        "<p class=\"small\">S0 cadre (fixe) ; S1 roue arrière et bras oscillant ; S2 biellette ; S3 levier basculeur ; "
        "S4 piston de l'amortisseur ; S5 corps de l'amortisseur.</p>"
        + donnees("‖V(G∈S1/S0)‖ = 30 m/s", "Échelle de ce document réponse : 1 cm pour 6 m/s") + "</div>"
        "__FIG:photo-vtt|VTT tout suspendu à cadre aluminium|Le VTT étudié.|300__</div>"]
    return {"key": "suspension-vtt", "prefix": "g", "partie": "graphique", "tag": "Activité 2.7", "title": "Suspension du VTT Vario Bomba",
            "mots": ["CIR", "Équiprojectivité", "Composition", "Amortisseur"], "methode": "Composition",
            "sub": "De la roue à l'amortisseur : trois documents réponses pour enchaîner CIR, équiprojectivité et "
                   "composition des vitesses, et valider le cahier des charges.",
            "hero": ("photo-vtt", "VTT tout suspendu", "Le VTT étudié et sa suspension arrière."),
            "docs": ["DP-vtt", "DT1"],
            "parts": [
                {"title": f"Détermination de {V('D', 'S3/S0')}", "minutes": 35, "intro": intro1, "meca": f1, "noms": noms1, "blocks": p1},
                {"title": f"Détermination de {V('C', 'S3/S0')}", "minutes": 15, "intro": [], "meca": f2,
                 "noms": [nom("D", "S3/S0"), nom("C", "S3/S0")], "blocks": p2},
                {"title": f"Détermination de {V('C', 'S4/S5')}", "minutes": 25, "intro": [], "meca": f3,
                 "noms": [nom("C", "S3/S0"), nom("C", "S4/S0"), nom("C", "S4/S5"), nom("C", "S5/S0")], "blocks": p3},
            ]}


ACTIVITES = [arbre, embiellage, pompe, ellipsographe, portail, bobcat, vtt]
