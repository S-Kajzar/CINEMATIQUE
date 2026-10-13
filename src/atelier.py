# -*- coding: utf-8 -*-
"""Atelier de construction graphique : feuilles (figures SVG en millimètres, points et axes d'accrochage), éléments
attendus par les questions (« items ») et corrections, barre d'outils. Le moteur est dans src/atelier/atelier.js,
son style dans src/atelier/atelier.css et src/atelier/figure.css.

Coordonnées de feuille : millimètres, x vers la droite, y vers le bas (voir src/geometrie.py). Une feuille peut
porter des graphes (Feuille.graphe) : axes gradués en unités physiques, quadrillage, et conversion des coordonnées
physiques (t, y) en coordonnées de feuille.
"""
import html
import math
import pathlib

import geometrie as g

ICI = pathlib.Path(__file__).resolve().parent / "atelier"
JS = (ICI / "atelier.js").read_text(encoding="utf-8")
CSS = (ICI / "atelier.css").read_text(encoding="utf-8")
CSS_FIG = (ICI / "figure.css").read_text(encoding="utf-8")


def f(x):
    """Nombre court pour le SVG."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def esc(s):
    return html.escape(s, quote=True)


# ====================================================================== feuille
class Feuille:
    """Une feuille de construction : dimensions (mm), dessin, points nommés, axes et cercles d'accrochage."""

    def __init__(self, w, h, titre="Document réponse"):
        self.w, self.h, self.titre = w, h, titre
        self.el = []
        self.pts = {}          # nom -> (x, y)
        self.lignes = []       # droites fixes (accrochage, référence des perpendiculaires et parallèles)
        self.cercles = []      # cercles fixes (trajectoires dessinées)
        self.graphes = []      # graphes (axes gradués) : lecture des coordonnées physiques, accrochage au quadrillage

    # ---------------------------------------------------------- primitives
    def add(self, s):
        self.el.append(s)

    def trait(self, a, b, cls="tr"):
        self.add(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" class="{cls}"/>')

    def poly(self, pts, cls="tr", ferme=False):
        tag = "polygon" if ferme else "polyline"
        self.add(f'<{tag} points="{" ".join(f(p[0]) + "," + f(p[1]) for p in pts)}" class="{cls}"/>')

    def chemin(self, d, cls="tr"):
        self.add(f'<path d="{d}" class="{cls}"/>')

    def cercle(self, c, r, cls="fin", accroche=False):
        self.add(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" class="{cls}"/>')
        if accroche:
            self.cercles.append((c, r))

    def arc(self, c, r, a0, a1, cls="fin"):
        """Arc de cercle, angles en degrés (sens trigonométrique à l'écran), de a0 vers a1."""
        p0, p1 = g.add(c, g.polar(r, a0)), g.add(c, g.polar(r, a1))
        grand = 1 if abs(a1 - a0) > 180 else 0
        sens = 0 if a1 > a0 else 1
        self.add(f'<path d="M{f(p0[0])},{f(p0[1])} A{f(r)},{f(r)} 0 {grand} {sens} {f(p1[0])},{f(p1[1])}" class="{cls}"/>')

    def texte(self, p, s, cls="lab", taille=3.6, ancre="middle", rot=None):
        tr = f' transform="rotate({f(rot)} {f(p[0])} {f(p[1])})"' if rot else ""
        self.add(f'<text x="{f(p[0])}" y="{f(p[1])}" font-size="{f(taille)}" class="{cls}" text-anchor="{ancre}"'
                 f' dominant-baseline="middle"{tr}>{s}</text>')

    def pivot(self, p, r=1.5):
        self.add(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r)}" class="pivot"/>')

    def point(self, nom, p, lab=(3, -3), taille=3.8, marque=False, etiquette=None):
        """Point nommé : accrochage, nom écrit à côté (lab : décalage du nom en mm)."""
        self.pts[nom] = p
        if marque:
            self.add(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="0.75" class="pt"/>')
        if lab is not None:
            self.texte(g.add(p, lab), etiquette if etiquette is not None else nom, "lab", taille)

    def axe(self, p, d, t0=-1e3, t1=1e3, accroche=True, cls="axe", borne=None):
        """Axe (trait mixte) de direction d passant par p, dessiné entre les paramètres t0 et t1 (mm)."""
        u = g.unit(d)
        self.trait(g.add(p, g.mul(u, t0)), g.add(p, g.mul(u, t1)), cls)
        if accroche:
            self.lignes.append((p, u))

    def bati(self, p, normale, larg=9, n=6, prof=2.4):
        """Liaison au bâti : un trait de largeur larg centré en p, hachuré du côté opposé à « normale »."""
        u = g.unit(normale)
        t = g.perp(u)
        a, b = g.add(p, g.mul(t, -larg / 2)), g.add(p, g.mul(t, larg / 2))
        self.trait(a, b, "tr")
        for i in range(n + 1):
            q = g.add(a, g.mul(t, larg * i / n))
            self.trait(q, g.add(q, g.add(g.mul(u, -prof), g.mul(t, -prof * 0.7))), "hach")

    def paroi(self, a, b, cote, pas=2.6, prof=2.2):
        """Paroi fixe (cylindre, glissière) de a à b, hachurée du côté « cote » (vecteur)."""
        self.trait(a, b, "tr")
        u, n = g.unit(g.sub(b, a)), g.unit(cote)
        L = g.dist(a, b)
        k = 0.0
        while k <= L + 1e-6:
            q = g.add(a, g.mul(u, k))
            self.trait(q, g.add(q, g.add(g.mul(n, prof), g.mul(u, -prof * 0.7))), "hach")
            k += pas

    def fleche(self, a, b, cls="fl", tete=2.2):
        u = g.unit(g.sub(b, a))
        base = g.sub(b, g.mul(u, tete))
        p1, p2 = g.add(base, g.mul(g.perp(u), tete * 0.38)), g.sub(base, g.mul(g.perp(u), tete * 0.38))
        self.trait(a, base, cls)
        self.poly([b, p1, p2], "flp", True)

    def fleche_arc(self, c, r, a0, a1, tete=2.2):
        """Flèche courbe (sens de rotation) de a0 vers a1, en degrés."""
        self.arc(c, r, a0, a1, "fl")
        p1 = g.add(c, g.polar(r, a1))
        tang = g.polar(1, a1 + (90 if a1 > a0 else -90))
        tang = (tang[0], tang[1])
        self.fleche(g.sub(p1, g.mul(tang, tete * 1.2)), g.add(p1, g.mul(tang, 0.4)), tete=tete)

    def numero(self, p, n, vers=None, r=2.6):
        """Repère de pièce : numéro cerclé, relié par un trait fin à la pièce."""
        if vers:
            u = g.unit(g.sub(vers, p))
            self.trait(g.add(p, g.mul(u, r)), vers, "fin")
        self.add(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r)}" class="num-c"/>')
        self.texte(p, str(n), "num", r * 1.25)

    def repere(self, o, lx="x", ly="y", L=12, rot=0):
        """Repère (x vers la droite, y vers le haut, tournés de rot degrés)."""
        ux, uy = g.polar(1, rot), g.polar(1, rot + 90)
        self.fleche(o, g.add(o, g.mul(ux, L)))
        self.fleche(o, g.add(o, g.mul(uy, L)))
        self.texte(g.add(o, g.add(g.mul(ux, L + 2.5), g.mul(uy, -1.5))), f"{lx}", "lab", 3.6)
        self.texte(g.add(o, g.add(g.mul(uy, L + 2.5), g.mul(ux, 2.2))), f"{ly}", "lab", 3.6)

    def echelle(self, p, mm, texte, taille=3.2):
        """Échelle des vitesses : un segment gradué de « mm » millimètres et son libellé."""
        b = g.add(p, (mm, 0))
        self.trait(p, b, "tr")
        for q in (p, b):
            self.trait(g.add(q, (0, -1.4)), g.add(q, (0, 1.4)), "fin")
        self.texte(g.add(p, (mm + 2.5, 0.2)), texte, "ech", taille, "start")

    def glissiere(self, c, d, L, e, cls="piece"):
        """Rectangle (coulisseau, piston) de longueur L selon d et d'épaisseur e, centré en c."""
        u = g.unit(d)
        n = g.perp(u)
        hl, he = g.mul(u, L / 2), g.mul(n, e / 2)
        self.poly([g.add(g.add(c, hl), he), g.add(g.sub(c, hl), he), g.sub(g.sub(c, hl), he), g.sub(g.add(c, hl), he)],
                  cls, True)

    def image(self, src, x, y, w, h, opacite=1.0):
        self.add(f'<image href="{src}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" opacity="{opacite}"'
                 f' preserveAspectRatio="none"/>')

    def graphe(self, nom, o, kx, ky, t_max, y_min, y_max, grille_t, grille_y, nx="t", ny="x", ux="s", uy="mm",
               up=None, dx=2, dy=1, titre=None, labels_y=None):
        """Graphe d'une grandeur en fonction du temps : origine o (mm de feuille), échelles kx (mm par unité de temps)
        et ky (mm par unité de la grandeur, vers le haut). grille_t et grille_y : (pas fin, pas épais, pas des
        graduations chiffrées). up : unité de la pente affichée pendant un tracé. labels_y : graduations
        supplémentaires {valeur: texte} (ex. 20π)."""
        G = Graphe(self, len(self.graphes), nom, o, kx, ky, t_max, y_min, y_max, grille_t, grille_y, nx, ny, ux, uy, up,
                   dx, dy)
        x0, x1 = o[0], o[0] + t_max * kx
        y0, y1 = o[1] - y_max * ky, o[1] - y_min * ky
        pf, pe, pg = grille_t

        def pas(v0, v1, h):
            n0, n1 = math.ceil(v0 / h - 1e-9), math.floor(v1 / h + 1e-9)
            return [round(i * h, 9) for i in range(n0, n1 + 1)]

        for t in pas(0, t_max, pf):
            cls = "gr2" if abs(t / pe - round(t / pe)) < 1e-6 else "gr"
            self.trait(G.p(t, y_min), G.p(t, y_max), cls)
        qf, qe, qg = grille_y
        for y in pas(y_min, y_max, qf):
            cls = "gr2" if abs(y / qe - round(y / qe)) < 1e-6 else "gr"
            self.trait(G.p(0, y), G.p(t_max, y), cls)
        # axes, flèches, graduations
        self.fleche(G.p(0, 0), (x1 + 7, o[1]), "fl", 2.4)
        self.fleche((x0, y1), (x0, y0 - 6), "fl", 2.4)
        for t in pas(0, t_max, pg):
            if abs(t) < 1e-9:
                continue
            self.trait(G.p(t, 0), g.add(G.p(t, 0), (0, 1.3)), "fin")
            self.texte(g.add(G.p(t, 0), (0, 3.6)), num(t), "note", 3, "middle")
        for y in pas(y_min, y_max, qg):
            self.trait(G.p(0, y), g.add(G.p(0, y), (-1.3, 0)), "fin")
            if abs(y) > 1e-9 or y_min < 0:  # zéro : écrit une seule fois, au coin de l'origine si l'axe y part de 0
                self.texte(g.add(G.p(0, y), (-2.2, 0.1)), num(y), "note", 3, "end")
        for y, txt in (labels_y or {}).items():
            self.trait(G.p(0, y), g.add(G.p(0, y), (-1.3, 0)), "fin")
            self.texte(g.add(G.p(0, y), (-2.2, 0.1)), txt, "note", 3, "end")
        if y_min >= 0:
            self.texte(g.add(G.p(0, 0), (-2.2, 3.4)), "0", "note", 3, "end")
        self.texte((x1 + 8, o[1] - 3.2), f"{nx} ({ux})", "lab", 3.4, "end")
        self.texte((x0 + 2.5, y0 - 4.5), f"{ny} ({uy})", "lab", 3.4, "start")
        if titre:
            self.texte((x1 + 8, y0 - 4.5), titre, "note", 3.2, "end")
        self.lignes.append((o, (1, 0)))
        self.lignes.append((o, (0, 1)))
        self.graphes.append(G)
        return G

    # ---------------------------------------------------------- sorties
    def svg_fig(self):
        return '<g class="at-fig">' + "".join(self.el) + "</g>"

    def config(self):
        return {"w": self.w, "h": self.h,
                "pts": [[n, round(p[0], 3), round(p[1], 3)] for n, p in self.pts.items()],
                "lignes": [[round(p[0], 3), round(p[1], 3), round(u[0], 6), round(u[1], 6)] for p, u in self.lignes],
                "cercles": [[round(c[0], 3), round(c[1], 3), round(r, 3)] for c, r in self.cercles],
                **({"graphes": [G.config() for G in self.graphes], "outil": "segment"} if self.graphes else {})}


def num(x):
    """Graduation d'un graphe : 0,5 ; 100 ; −40."""
    s = f"{x:.3f}".rstrip("0").rstrip(".").replace(".", ",")
    return s.replace("-", "−") if s not in ("-0", "") else "0"


class Graphe:
    """Un graphe d'une feuille : conversions entre unités physiques et millimètres de feuille, tracés de courbes."""

    def __init__(self, F, i, nom, o, kx, ky, t_max, y_min, y_max, grille_t, grille_y, nx, ny, ux, uy, up, dx, dy):
        self.F, self.i, self.nom, self.o, self.kx, self.ky = F, i, nom, o, kx, ky
        self.t_max, self.y_min, self.y_max = t_max, y_min, y_max
        self.grille_t, self.grille_y = grille_t, grille_y
        self.nx, self.ny, self.ux, self.uy, self.up, self.dx, self.dy = nx, ny, ux, uy, up, dx, dy

    def p(self, t, y):
        return (self.o[0] + t * self.kx, self.o[1] - y * self.ky)

    def box(self):
        return [self.o[0], self.o[1] - self.y_max * self.ky, self.o[0] + self.t_max * self.kx,
                self.o[1] - self.y_min * self.ky]

    def echantillons(self, f, t0, t1, n=None):
        n = n or max(12, int(abs(t1 - t0) * self.kx / 2.5))
        return [self.p(t0 + (t1 - t0) * i / n, f(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]

    def courbe(self, f, t0, t1, cls="crb"):
        """Courbe donnée (graphe d'un énoncé), dessinée sur la feuille."""
        self.F.poly(self.echantillons(f, t0, t1, max(40, int(abs(t1 - t0) * self.kx))), cls)

    def config(self):
        return {"nom": self.nom, "o": [round(self.o[0], 3), round(self.o[1], 3)], "kx": self.kx, "ky": self.ky,
                "box": [round(v, 3) for v in self.box()], "nx": self.nx, "ny": self.ny, "ux": self.ux, "uy": self.uy,
                "up": self.up, "px": self.grille_t[0], "py": self.grille_y[0], "dx": self.dx, "dy": self.dy}


# ====================================================================== éléments attendus (items)
def IT_VE(o, v, nom, lab=None, tolA=3.0, tolL=0.06, tolO=1.5):
    """Vecteur d'origine o et de composantes v (mm de feuille)."""
    return {"k": "ve", "o": list(g.r2(o, 3)), "v": list(g.r2(v, 3)), "nom": nom, "tolA": tolA, "tolL": tolL,
            "tolO": tolO, "lab": lab or f"Vecteur {nom}"}


def IT_DIR(o, d, lab, tolA=3.0, tolO=1.5):
    """Droite (support) passant par o, de direction d."""
    return {"k": "dir", "o": list(g.r2(o, 3)), "d": list(g.r2(g.unit(d), 6)), "tolA": tolA, "tolO": tolO, "lab": lab}


def IT_PT(p, nom, lab=None, tolP=2.0):
    return {"k": "pt", "p": list(g.r2(p, 3)), "nom": nom, "tolP": round(tolP, 2), "lab": lab or f"Point {nom}"}


def IT_CI(c, r, lab, tolO=1.5):
    return {"k": "ci", "c": list(g.r2(c, 3)), "r": round(r, 3), "tolO": tolO, "lab": lab}


def IT_COURBE(G, f, t0, t1, lab, tol=2.0):
    """Portion de la courbe y = f(t) d'un graphe, entre t0 et t1 : échantillonnée tous les 2,5 mm environ."""
    pts = G.echantillons(f, t0, t1)
    return {"k": "courbe", "g": G.i, "pts": [list(g.r2(q, 3)) for q in pts], "x0": round(G.p(t0, 0)[0], 3),
            "x1": round(G.p(t1, 0)[0], 3), "tol": tol, "lab": lab}


def tol_cir(i, *pts):
    """Tolérance de position d'un centre instantané : il s'éloigne vite quand les perpendiculaires se coupent sous un
    angle faible ; on accepte 4 % de sa distance aux points qui le construisent (2 mm au moins)."""
    return max(2.0, 0.04 * max(g.dist(i, p) for p in pts))


# ====================================================================== corrections (tracés superposés)
def C_VE(a, v, lab="", st="res"):
    b = g.add(a, v)
    return {"t": "ve", "a": list(g.r2(a, 3)), "b": list(g.r2(b, 3)), "lab": lab, "st": st}


def C_DR(p, d, st="aide"):
    return {"t": "dr", "p": list(g.r2(p, 3)), "d": list(g.r2(g.unit(d), 6)), "st": st}


def C_SG(a, b, st="aide"):
    return {"t": "sg", "a": list(g.r2(a, 3)), "b": list(g.r2(b, 3)), "st": st}


def C_CI(c, r, st="aide"):
    return {"t": "ci", "c": list(g.r2(c, 3)), "r": round(r, 3), "st": st}


def C_PT(p, lab="", st="res"):
    return {"t": "pt", "p": list(g.r2(p, 3)), "lab": lab, "st": st}


def C_PL(pts, st="res"):
    """Courbe (ligne brisée fine) de la correction."""
    return {"t": "pl", "pts": [list(g.r2(q, 3)) for q in pts], "st": st}


def C_COURBE(item, st="res"):
    """Correction d'un item « courbe » : la courbe attendue."""
    return {"t": "pl", "pts": item["pts"], "st": st}


def C_TX(p, s, st="res", ancre="start"):
    return {"t": "tx", "p": list(g.r2(p, 3)), "s": s, "st": st, "ancre": ancre}


def corr_equiprojectivite(a, va, b, vb, la="", lb=""):
    """Tracés de la méthode : droite (AB), projetés des deux vecteurs, perpendiculaires à (AB) par les projetés."""
    u = g.sub(b, a)
    ha = g.projete(g.add(a, va), a, u)
    hb = g.projete(g.add(b, vb), a, u)
    return [C_DR(a, u), C_SG(g.add(a, va), ha), C_SG(a, ha, "res"), C_SG(b, hb, "res"), C_DR(hb, g.perp(u)),
            C_VE(a, va, la, "aide"), C_VE(b, vb, lb)]


def corr_cir(i, pts_dirs, lab="I"):
    """Tracés du CIR : les perpendiculaires aux supports des vitesses connues, et le point I."""
    out = [C_DR(p, g.perp(d)) for p, d in pts_dirs]
    out.append(C_PT(i, lab))
    return out


def corr_triangle(i, a, va, m, vm, la="", lm=""):
    """Répartition linéaire autour du CIR : report de IM sur (IA), droite de proportionnalité, vecteur de m."""
    u = g.unit(g.sub(a, i))
    m2 = g.add(i, g.mul(u, g.dist(i, m)))
    va2 = g.mul(va, g.dist(i, m) / g.dist(i, a))
    out = [C_SG(i, g.add(i, g.mul(u, max(g.dist(i, m), g.dist(i, a)) * 1.08))),
           C_CI(i, g.dist(i, m)), C_VE(a, va, la, "aide"), C_SG(i, g.add(a, va)),
           C_VE(m2, va2, "", "aide"), C_SG(i, m), C_VE(m, vm, lm)]
    return out


# ====================================================================== barre d'outils et feuille
ICONES = {
    "main": '<path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/>',
    "point": '<path d="M7 7l10 10M17 7 7 17"/>',
    "droite": '<path d="M2 19 22 5"/><circle cx="8" cy="14.8" r="1.6"/><circle cx="16" cy="9.2" r="1.6"/>',
    "segment": '<path d="M5 18 19 6"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/>',
    "vecteur": '<path d="M4 19 19 5M19 5h-7M19 5v7"/>',
    "perp": '<path d="M3 20h18M12 20V4M12 15h5v5"/>',
    "para": '<path d="M3 17 15 5M9 21 21 9"/>',
    "proj": '<path d="M3 20h18M15 5v15" stroke-dasharray="2.5 2"/><path d="M5 20 15 5"/><circle cx="15" cy="5" r="1.6"/>',
    "cercle": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="1.2"/>',
    "compas": '<path d="M12 3v3M12 6 6 21M12 6l6 15M8.5 14h7"/>',
    "mesure": '<path d="M3 15 15 3l6 6L9 21z"/><path d="M7 11l2 2M10 8l2 2M13 5l2 2"/>',
    "texte": '<path d="M5 6V4h14v2M12 4v16M9 20h6"/>',
    "gomme": '<path d="M4 16 13 7l6 6-7 7H7z"/><path d="M9 11l6 6M12 20h8"/>',
    "courbe": '<path d="M3 20c4-1 6-4 8-8s4-7 10-8"/><circle cx="3" cy="20" r="1.4"/><circle cx="11" cy="12" r="1.4"/><circle cx="21" cy="4" r="1.4"/>',
}
OUTILS = [("main", "Déplacer", "H"), ("point", "Point", "P"), ("droite", "Droite", "D"), ("segment", "Segment", "S"),
          ("vecteur", "Vecteur", "V"), ("perp", "Perpendiculaire", "E"), ("para", "Parallèle", "A"),
          ("proj", "Projeté", "O"), ("cercle", "Cercle", "C"), ("compas", "Compas", "K"), ("mesure", "Mesurer", "M"),
          ("texte", "Texte", "T"), ("gomme", "Gomme", "G"), ("courbe", "Courbe", "U")]
GROUPES_OUTILS = [["main"], ["point", "droite", "segment", "vecteur", "courbe"], ["perp", "para", "proj"],
                  ["cercle", "compas"], ["mesure", "texte", "gomme"]]
OUTILS_FIGURE = ["main", "point", "droite", "segment", "vecteur", "perp", "para", "proj", "cercle", "compas", "mesure",
                 "texte", "gomme"]
OUTILS_GRAPHE = ["main", "point", "segment", "droite", "courbe", "mesure", "texte", "gomme"]
COULEURS = [("#1F5FA8", "bleue"), ("#1B7A43", "verte"), ("#7B3FA0", "violette"), ("#1C2530", "noire")]


def barre(ident, outils=None):
    lab = {o: (n, k) for o, n, k in OUTILS}
    outils = outils or OUTILS_FIGURE
    grp = []
    for gr in GROUPES_OUTILS:
        gr = [o for o in gr if o in outils]
        if not gr:
            continue
        grp.append('<span class="at-grp">' + "".join(
            f'<button type="button" data-outil="{o}" aria-pressed="false" title="{lab[o][0]} (touche {lab[o][1]})">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONES[o]}</svg>{lab[o][0]}</button>' for o in gr) + "</span>")
    sw = "".join(f'<button type="button" class="at-sw" data-couleur="{c}" aria-label="Couleur {n}" '
                 f'aria-pressed="{"true" if i == 0 else "false"}" style="background:{c}"></button>'
                 for i, (c, n) in enumerate(COULEURS))
    grp.append(f'<span class="at-grp">{sw}</span>')
    grp.append('<span class="at-grp"><button type="button" data-act="annuler" title="Annuler (Ctrl+Z)">Annuler</button>'
               '<button type="button" data-act="retablir" title="Rétablir (Ctrl+Y)">Rétablir</button>'
               '<button type="button" data-act="effacer">Tout effacer</button></span>')
    grp.append('<span class="at-grp"><button type="button" data-act="zoom-moins" aria-label="Réduire le zoom">−</button>'
               '<span class="at-zoom">100 %</span><button type="button" data-act="zoom-plus" aria-label="Agrandir le zoom">+</button>'
               '<button type="button" data-act="ajuster">Ajuster</button>'
               '<button type="button" data-act="grille" aria-pressed="false">Quadrillage</button></span>')
    grp.append('<span class="at-grp"><button type="button" data-act="correction" aria-pressed="false" '
               'title="Superposer la correction des questions déjà corrigées">Correction</button>'
               '<button type="button" data-act="vierge" title="Document réponse vierge, à imprimer à taille réelle">DR vierge</button>'
               '<button type="button" data-act="plein" aria-pressed="false">Plein écran</button></span>')
    return f'<div class="at-bar" role="toolbar" aria-label="Outils de construction">{"".join(grp)}</div>'


def form_coord(ident, feuille):
    """Placement d'un point par ses coordonnées physiques (feuilles à graphes)."""
    gs = feuille.graphes
    choix = ("" if len(gs) < 2 else '<label>Graphe <select class="at-c-g">' + "".join(
        f'<option value="{G.i}">{esc(G.nom)}</option>' for G in gs) + "</select></label>")
    return (f'<form class="at-coord" autocomplete="off"><span class="at-c-t">Placer un point :</span>{choix}'
            f'<label><span class="at-c-lx">t</span> <input class="at-c-x" inputmode="decimal" aria-label="Abscisse du point"></label>'
            f'<label><span class="at-c-ly">y</span> <input class="at-c-y" inputmode="decimal" aria-label="Ordonnée du point"></label>'
            '<button type="submit">Placer</button><button type="button" class="at-c-fin">Terminer la courbe</button>'
            '<span class="at-c-msg" role="alert"></span></form>')


def render(ident, feuille, legende="", noms=(), outils=None):
    """HTML d'un atelier : barre d'outils, feuille SVG (figure + calques du moteur), aide, propriétés."""
    W, H = feuille.w, feuille.h
    if feuille.graphes and outils is None:
        outils = OUTILS_GRAPHE
    dl = "".join(f'<option value="{esc(n)}"></option>' for n in noms)
    svg = (f'<svg class="at-svg" viewBox="0 0 {f(W)} {f(H)}" preserveAspectRatio="xMidYMid meet" tabindex="0" '
           f'role="application" aria-roledescription="feuille de construction" aria-label="{esc(feuille.titre)} : '
           'construis avec les outils ; au clavier, les flèches déplacent le curseur et Entrée pose un point" '
           f'xmlns="http://www.w3.org/2000/svg"><rect class="at-papier" x="0" y="0" width="{f(W)}" height="{f(H)}"/>'
           f'{feuille.svg_fig()}<g class="at-grille"></g><g class="at-cons"></g><g class="at-corr"></g>'
           '<g class="at-tmp"></g></svg>')
    haut = " at-haut" if H > 1.15 * W else ""
    return (f'<div class="atelier{haut}" data-cfg="{ident}" id="{ident}" data-titre="{esc(feuille.titre)}">'
            f'{barre(ident, outils)}'
            f'<div class="at-stage" style="--ar:{f(W)}/{f(H)}">{svg}</div>'
            '<div class="at-info" aria-live="polite"><span class="at-aide"></span><span class="at-mesure"></span></div>'
            + (form_coord(ident, feuille) if feuille.graphes else "") +
            '<div class="at-prop" hidden><span class="at-p-type"></span>'
            f'<label class="at-p-nomw">Nom <input class="at-p-nom" list="dl-{ident}" autocomplete="off" '
            'placeholder="ex. V(A∈1/0)"></label>'
            '<label class="at-p-longw">Longueur <input class="at-p-long" inputmode="decimal" autocomplete="off"> mm</label>'
            '<label class="at-p-lissew" hidden><input type="checkbox" class="at-p-lisse"> courbe lissée</label>'
            '<button type="button" class="at-p-suppr">Supprimer</button></div>'
            f'<datalist id="dl-{ident}">{dl}</datalist>'
            + (f'<p class="at-legende">{legende}</p>' if legende else "") + "</div>")


def render_demo(ident, feuille, etapes, titre, intro=""):
    """Démonstration pas à pas : la feuille, la liste des étapes, les boutons de navigation."""
    W, H = feuille.w, feuille.h
    svg = (f'<svg class="at-svg" viewBox="0 0 {f(W)} {f(H)}" preserveAspectRatio="xMidYMid meet" role="img" '
           f'aria-label="{esc(titre)}" xmlns="http://www.w3.org/2000/svg"><rect class="at-papier" x="0" y="0" '
           f'width="{f(W)}" height="{f(H)}"/>{feuille.svg_fig()}<g class="at-cons"></g></svg>')
    liste = "".join(f"<li>{e['titre']}</li>" for e in etapes)
    return (f'<div class="at-demo" data-cfg="{ident}" id="{ident}"><div class="at-stage" style="--ar:{f(W)}/{f(H)}">{svg}</div>'
            '<div class="dm-side"><div class="dm-nav"><span class="dm-num"></span>'
            '<button type="button" class="btn ghost dm-zero">Recommencer</button>'
            '<button type="button" class="btn ghost dm-prec">Étape précédente</button>'
            '<button type="button" class="btn dm-suiv">Étape suivante</button></div>'
            f'<p class="dm-titre"></p><p class="dm-texte"></p><ol class="dm-liste">{liste}</ol>'
            + (f'<p class="small">{intro}</p>' if intro else "") + "</div></div>")


def demo_config(feuille, etapes, depart="Situation de départ", texte0=""):
    c = feuille.config()
    c.update({"etapes": etapes, "depart": depart, "texte0": texte0})
    return c


def angle_deg(v):
    return math.degrees(math.atan2(-v[1], v[0]))
