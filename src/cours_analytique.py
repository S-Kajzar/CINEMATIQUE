# -*- coding: utf-8 -*-
"""Cours 1 — Cinématique analytique : contenu, figures SVG et simulateurs.

Source : le chapitre « Cinématique » fourni (13 pages : généralités, cinématique du solide, cinématique du point).
La partie graphique du chapitre (équiprojectivité, centre instantané de rotation) est reprise dans le cours 2. Les
figures du chapitre sont des captures de manuel : aucune n'est reprise telle quelle ; elles sont redessinées en SVG
et rendues vivantes (train et voyageur, roue de vélo, vecteurs position, vitesse et accélération, mouvements plans,
répartition des vitesses, mouvement rectiligne uniformément varié, rotation du point).

La séquence « Cinématique analytique » complète le cours (src/cours_mouvements.py) : abscisse curviligne, composantes
tangentielle et normale de l'accélération, analyse de quatre mouvements, MRU, MRUV et mouvement circulaire, avec leurs
applications en exercices auto-corrigés.
"""
import cours_mouvements as cm
from cours_commun import course_head, course_section, course_nav, quiz_section, jeu_html, cartes, formule, frac, vec

V = vec("V")
G = vec("Γ")
OM = vec("OM")


def render(A):
    H = A.HOUSE
    sections = [("ca-referentiel", "Référentiel et mouvement"), ("ca-trajectoire", "Trajectoire d'un point"),
                ("ca-vitesse", "Vitesse et accélération"), ("ca-analyse", "Analyse de mouvements"),
                ("ca-mouvements", "Mouvements plans particuliers"), ("ca-solide", "Cinématique du solide"),
                ("ca-composition", "Composition des mouvements"), ("ca-mru", "MRU"), ("ca-mruv", "MRUV"),
                ("ca-circulaire", "Mouvement circulaire"), ("ca-quiz", "Quiz")]
    s = []
    # ------------------------------------------------------------------ 1. référentiel
    s.append(course_section(1, "ca-referentiel", "Référentiel, mouvement absolu et relatif", f"""
<p>La <strong>cinématique</strong> étudie le mouvement des corps indépendamment des forces qui le produisent. Elle permet
de définir la géométrie et les dimensions des composants, et participe à l'étude dynamique et énergétique d'un
mécanisme.</p>
<div class="def"><p><strong>Référentiel</strong> : l'association d'un <strong>repère d'espace</strong> et d'un
<strong>repère de temps</strong>.</p></div>
<h3>Repère de référence</h3>
<p>Le mouvement d'un solide (S1) est défini par rapport à un autre solide (S0), choisi comme solide de référence. Un
repère « collé » à (S0) permet de repérer avec précision la position et le mouvement de (S1).
<strong>Notation</strong> : Mvt 1/0 est le mouvement de (S1) par rapport à (S0).</p>
<h3>Repère de temps</h3>
<p>Le temps est considéré comme uniforme et absolu. On le représente par une droite graduée orientée : la lettre
<em>t</em>, appelée <strong>date</strong> ou <strong>instant</strong>, désigne un point de cette droite ; l'écart entre
deux dates est une <strong>durée</strong> ; l'origine est choisie à t = 0.</p>
<figure class="simu-fig" style="max-width:720px"><svg viewBox="0 0 720 130" role="img" aria-label="Axe du temps : origine t = 0, dates t1 et t2, durée t2 − t1, date t du mouvement">
<defs><marker id="ca-fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 10,5 0,10z" fill="#1C2530"/></marker></defs>
<line x1="20" y1="50" x2="700" y2="50" stroke="#1C2530" stroke-width="2.5" marker-end="url(#ca-fl)"/>
<text x="24" y="38" font-size="14" fill="#1F5FA8">passé</text><text x="652" y="38" font-size="14" fill="#1F5FA8">futur</text>
<g font-size="15" text-anchor="middle"><line x1="140" y1="42" x2="140" y2="58" stroke="#1C2530" stroke-width="2"/><text x="140" y="32">t = 0</text>
<line x1="330" y1="42" x2="330" y2="58" stroke="#1C2530" stroke-width="2"/><text x="330" y="32">t₁</text>
<line x1="450" y1="42" x2="450" y2="58" stroke="#1C2530" stroke-width="2"/><text x="450" y="32">t₂</text>
<line x1="590" y1="42" x2="590" y2="58" stroke="#1C2530" stroke-width="2"/><text x="590" y="32">t</text>
<line x1="330" y1="74" x2="450" y2="74" stroke="#B26A00" stroke-width="2" marker-end="url(#ca-fl)" marker-start="url(#ca-fl)"/>
<text x="140" y="100">origine des temps</text><text x="390" y="100" fill="#B26A00">durée t₂ − t₁</text><text x="590" y="100">date du mouvement</text></g>
</svg></figure>
<h3>Mouvement absolu, mouvement relatif</h3>
<p>Le mouvement d'un solide dépend du repère choisi. Un repère <strong>absolu</strong> est considéré comme au repos dans
l'univers (repère galiléen) : le mouvement qu'on y décrit est <strong>absolu</strong>. Un repère <strong>relatif</strong>
est en mouvement par rapport au repère absolu : le mouvement qu'on y décrit est <strong>relatif</strong>.</p>
<div class="simu" id="ca-train"><h3>Un voyageur (2) marche dans un wagon (1) qui roule sur la voie (0)</h3>
<div class="simu-btns"><button type="button" class="btn ghost" data-vue="0" aria-pressed="true">Vu depuis le quai, repère R0</button>
<button type="button" class="btn ghost" data-vue="1" aria-pressed="false">Vu depuis le wagon, repère R1</button>
<span style="flex:1"></span><button type="button" class="btn ghost" data-marche="1" aria-pressed="true">Il marche vers l'avant</button>
<button type="button" class="btn ghost" data-marche="-1" aria-pressed="false">vers l'arrière</button>
<button type="button" class="btn ghost" data-marche="0" aria-pressed="false">Il reste assis</button></div>
<div class="simu-fig"><svg viewBox="0 0 760 210" role="img" aria-label="Animation : un train roule, un voyageur marche dans un wagon ; sa trace dépend du repère d'observation"><g class="ca-tr-monde"></g></svg></div>
<div class="simu-out"><div><span>V(2/1) : voyageur / wagon</span><b class="ca-v21"></b></div><div><span>V(1/0) : wagon / voie</span><b>20,0 m/s</b></div>
<div><span>V(2/0) : voyageur / voie</span><b class="ca-v20"></b></div><div><span>Mouvement observé</span><b class="ca-obs"></b></div></div>
<p class="simu-note">R0 (O, x0, y0) lié à la terre : repère absolu ; R1 lié au train et R2 lié au voyageur : repères relatifs.
Mvt 1/0 et Mvt 2/0 sont des mouvements absolus, Mvt 2/1 un mouvement relatif. Les vitesses s'ajoutent :
V(2/0) = V(2/1) + V(1/0) (composition des mouvements, section 7). Valeurs choisies pour l'animation.</p></div>
"""))
    # ------------------------------------------------------------------ 2. trajectoire
    s.append(course_section(2, "ca-trajectoire", "Trajectoire d'un point", f"""
<h3>Points coïncidents</h3>
<p>À un instant donné, plusieurs points de solides différents peuvent être superposés. Quand on écrit avec un crayon
(1), tenu par une main (2), sur une feuille (3) posée sur une table (0), la pointe A du crayon coïncide avec un point de
la feuille et un point de la table : A lié à 1, A lié à 3, A lié à 0. Selon le point considéré, les mouvements sont
différents : il faut toujours préciser à quel solide le point appartient.</p>
<div class="def"><p>La <strong>trajectoire</strong> d'un point M est la courbe décrite au cours du temps par les positions
successives de ce point, par rapport à un repère de référence. On la note T(M∈1/0), ou T M1/0.</p></div>
<div class="simu" id="ca-velo"><h3>Exemple : la roue avant d'un vélo qui roule sans glisser</h3>
<div class="simu-btns"><button type="button" class="btn ca-go">Rouler</button><button type="button" class="btn ghost ca-raz">Revenir au départ</button>
<label class="small"><input type="checkbox" class="ca-traces" checked> Laisser les traces</label></div>
<div class="simu-fig"><svg viewBox="0 0 760 240" role="img" aria-label="Animation : roue de vélo qui roule ; trajectoires du point A de la jante (cycloïde), du moyeu B et du point C du guidon (droites)"><g class="ca-v-monde"></g></svg></div>
<p class="simu-note">Repères : 0 la route, 1 la roue, 2 le cadre. T(A∈1/0) : arcs de cycloïde, avec un point de
rebroussement à chaque tour, quand A touche la route. T(B∈1/0) = T(B∈2/0) : une droite parallèle à la route.
T(C∈2/0) : une droite. Par rapport au cadre, A décrit un cercle (T(A∈1/2)).</p></div>
"""))
    # ------------------------------------------------------------------ 3. vitesse, accélération
    s.append(course_section(3, "ca-vitesse", "Abscisse curviligne, vitesse et accélération", cm.vitesse_avant() + f"""
<h3>Les vecteurs position, vitesse et accélération</h3>
<p>Le solide (S1) est en mouvement par rapport au repère R0 (O, x0, y0) ; son point M décrit la trajectoire T M1/0.</p>
<div class="cours-split"><div>
<h3>Vecteur position</h3>{formule(f"{OM} = x(t)·<span class=vec>x</span> + y(t)·<span class=vec>y</span>")}
<h3>Vecteur vitesse</h3>{formule(f"{V}(M∈1/0) = {frac(f'd{OM}', 'dt')} = v·<span class=vec>t</span>", "composantes x'(t) et y'(t) ; unité : m/s")}
<ul><li><strong>direction</strong> : la tangente en M à la trajectoire ;</li><li><strong>sens</strong> : celui du
mouvement ;</li><li><strong>norme</strong> : |v|, v étant la vitesse algébrique.</li></ul>
<p>Si v &gt; 0, M se déplace dans le sens + de la trajectoire ; si v &lt; 0, dans le sens − ; si v est constante, le
mouvement se fait à vitesse constante.</p>
<h3>Vecteur accélération</h3>{formule(f"{G}(M∈1/0) = {frac(f'd{V}', 'dt')} = {frac(f'd²{OM}', 'dt²')}", "composantes x''(t) et y''(t) ; unité : m/s²")}
<p>Si l'accélération algébrique γ est de même sens que v, M accélère ; de sens contraire, M décélère.</p>
</div></div>
<div class="simu" id="ca-vect"><h3>Le point M sur sa trajectoire</h3>
<div class="simu-grid"><label>Instant t <output class="ca-t"></output><input type="range" min="0" max="6.28" step="0.01" value="0.8" class="ca-tr"></label>
<label><span><input type="checkbox" class="ca-anim"> Animer</span></label><label><span class="small">x(t) = 3 cos t + 1 ; y(t) = 2 sin t (m, s)</span></label></div>
<div class="simu-fig"><svg viewBox="0 0 760 330" role="img" aria-label="Point M sur une trajectoire elliptique, avec son vecteur position, son vecteur vitesse tangent et son vecteur accélération"><g class="ca-vt-monde"></g></svg></div>
<div class="simu-out"><div><span>x(t) ; y(t)</span><b class="ca-pos"></b></div><div><span>V : x'(t) ; y'(t)</span><b class="ca-vit"></b></div>
<div><span>‖V‖</span><b class="ca-nv"></b></div><div><span>Γ : x''(t) ; y''(t)</span><b class="ca-acc"></b></div></div>
<p class="simu-note">En rouge le vecteur position OM, en bleu la vitesse (toujours tangente à la trajectoire), en vert
l'accélération (tournée vers l'intérieur de la courbe). Échelles différentes pour les trois vecteurs.</p></div>
""" + cm.vitesse_apres()))
    # ------------------------------------------------------------------ 4. analyse de mouvements (séquence analytique)
    s.append(course_section(4, "ca-analyse", "Analyse de mouvements", cm.analyse()))
    # ------------------------------------------------------------------ 4. mouvements plans
    jeu = jeu_html([("Le tiroir d'une commode qu'on ouvre", "tr"), ("Une porte qui pivote sur ses gonds", "ro"),
                    ("La bielle d'un moteur", "pl"), ("La nacelle d'une grande roue de fête foraine", "tc"),
                    ("L'hélice d'un avion, par rapport à l'avion", "ro"), ("La cabine d'un ascenseur", "tr"),
                    ("Le balai d'essuie-glace d'autobus (montage en parallélogramme)", "tc"),
                    ("Une roue de vélo, par rapport à la route", "pl")],
                   [("tr", "Translation rectiligne"), ("tc", "Translation circulaire"), ("ro", "Rotation"),
                    ("pl", "Mouvement plan")], "ca-jeu-mvt")
    s.append(course_section(5, "ca-mouvements", "Mouvements plans particuliers", f"""
<table class="t cours-t"><thead><tr><th>Mouvement</th><th>Exemple</th><th>Nature des trajectoires</th></tr></thead><tbody>
<tr><td><strong>Translation rectiligne</strong></td><td>Coulisseau sur une barre</td><td>Droites parallèles, de direction l'axe de translation ; tout segment AB reste parallèle à lui-même (A0A = B0B).</td></tr>
<tr><td><strong>Rotation</strong></td><td>Hélice d'avion</td><td>Cercles concentriques, de centre le centre de rotation.</td></tr>
<tr><td><strong>Mouvement plan général</strong></td><td>Bielle d'un système bielle-manivelle</td><td>Courbes quelconques.</td></tr>
<tr><td><strong>Translation circulaire</strong></td><td>Balai d'essuie-glace en parallélogramme, nacelle de grande roue</td><td>Cercles non concentriques, de rayons identiques.</td></tr>
</tbody></table>
<div class="mini-anim" id="ca-mini">
<figure><svg viewBox="0 0 240 150" class="ca-m" data-m="tr" role="img" aria-label="Translation rectiligne"></svg><figcaption><strong>Translation rectiligne</strong></figcaption></figure>
<figure><svg viewBox="0 0 240 150" class="ca-m" data-m="ro" role="img" aria-label="Rotation"></svg><figcaption><strong>Rotation</strong></figcaption></figure>
<figure><svg viewBox="0 0 240 150" class="ca-m" data-m="pl" role="img" aria-label="Mouvement plan d'une bielle"></svg><figcaption><strong>Mouvement plan</strong> (bielle)</figcaption></figure>
<figure><svg viewBox="0 0 240 150" class="ca-m" data-m="tc" role="img" aria-label="Translation circulaire d'un balai en parallélogramme"></svg><figcaption><strong>Translation circulaire</strong></figcaption></figure>
</div>
<p class="simu-note">Dans chaque figure, deux points du solide laissent leur trace : droites parallèles, cercles
concentriques, courbes quelconques, cercles de même rayon.</p>
<h3>Jeu : quel est le mouvement ?</h3>{jeu}
"""))
    # ------------------------------------------------------------------ 5. solide
    s.append(course_section(6, "ca-solide", "Cinématique du solide", f"""
<p>Un solide est supposé géométriquement parfait, homogène et <strong>indéformable</strong>.</p>
<h3>Mouvement de translation rectiligne</h3>
<p>Tous les points du solide ont des trajectoires parallèles, qui sont des droites ; leurs vecteurs vitesse sont
identiques, de direction celle du mouvement, et leurs vecteurs accélération aussi :</p>
{formule(f"{V}A(1/0) = {V}B(1/0) &nbsp;&nbsp; et &nbsp;&nbsp; {G}A(1/0) = {G}B(1/0)")}
<h3>Mouvement de rotation</h3>
<p>Le solide (S1) tourne autour de O par rapport à R0. Son point M décrit un cercle de centre O et de rayon r = OM ; sa
position est repérée par l'angle θ, qui varie au cours du temps : {OM} = (r cos θ)·<span class=vec>x</span> + (r sin θ)·<span class=vec>y</span>.</p>
<div class="cours-split"><div>
{formule("ω = dθ/dt", "vitesse angulaire, en rad/s ; ω = θ / t si elle est constante et si θ = 0 à t = 0")}
{formule("ω = 2π·N / 60", "N en tr/min")}
</div><div>
{formule("V = r·ω", "V en m/s, r en m, ω en rad/s")}
{formule(f"{vec('Ω')}1/0 = ω·<span class=vec>z</span>", "vecteur rotation : porté par l'axe, positif sur (O, <span class=vec>z</span>) si ω &gt; 0, de norme |ω|")}
</div></div>
<p>Le vecteur vitesse de M est porté par la tangente en M à sa trajectoire : il est <strong>perpendiculaire au
rayon</strong>. Sa norme est proportionnelle à la distance du point à l'axe : c'est la <strong>répartition
triangulaire des vitesses</strong>. Il suffit de connaître la vitesse d'un point et la position de l'axe pour connaître
celle de tous les autres.</p>
<div class="simu" id="ca-helice"><h3>Répartition des vitesses sur une pale d'hélice</h3>
<div class="simu-grid"><label>Fréquence de rotation N <output class="ca-n"></output><input type="range" min="200" max="2400" step="50" value="1000" class="ca-nr"></label>
<label>Point étudié : distance à l'axe <output class="ca-r"></output><input type="range" min="0" max="1" step="0.01" value="1" class="ca-rr"></label>
<label><span class="small">Pale de 1 m (de l'axe O au bout A).</span></label></div>
<div class="simu-fig"><svg viewBox="0 0 760 300" role="img" aria-label="Pale d'hélice et vecteurs vitesse de ses points, proportionnels à la distance à l'axe"><g class="ca-h-monde"></g></svg></div>
<div class="simu-out"><div><span>ω = 2πN/60</span><b class="ca-w"></b></div><div><span>V au point étudié</span><b class="ca-vp"></b></div>
<div><span>V au bout de la pale</span><b class="ca-va"></b></div><div><span>en km/h (bout)</span><b class="ca-vkm"></b></div></div>
<p class="simu-note">Avec N = 1 000 tr/min et une pale de 1 m, le bout A va à 104,7 m/s, comme dans l'exemple du
chapitre ; à mi-longueur, la vitesse est moitié moindre.</p></div>
"""))
    # ------------------------------------------------------------------ 6. composition
    s.append(course_section(7, "ca-composition", "Composition des mouvements", f"""
<p>Soit un solide (3) en mouvement par rapport à un solide (2), lui-même en mouvement par rapport à un solide (1). Le
mouvement de (3) par rapport à (1) est le <strong>composé</strong> des deux mouvements précédents :
Mvt 3/1 = Mvt 3/2 + Mvt 2/1.</p>
<h3>Composition des vitesses en un point</h3>
<p>Pour un point A appartenant au solide (3) :</p>
{formule(f"{V}A(3/1) = {V}A(3/2) + {V}A(2/1)", "vitesse absolue = vitesse relative + vitesse d'entraînement")}
<p>De même pour les vitesses angulaires : {vec('Ω')}(3/1) = {vec('Ω')}(3/2) + {vec('Ω')}(2/1).</p>
<h3>Glissement, roulement, pivotement</h3>
<p>Soit A le point de contact entre deux solides (1) et (2), et (A, <span class=vec>n</span>, <span class=vec>t</span>, <span class=vec>w</span>) un repère orthonormé direct, <span class=vec>n</span>
normal au contact. La <strong>vitesse de glissement</strong> en A de (1) par rapport à (2) est la vitesse relative
{V}A(1/2) ; elle est contenue dans le plan tangent au contact. La vitesse angulaire ω<sub>r</sub>(1/2) autour de <span class=vec>w</span>
est la vitesse de <strong>roulement</strong>, ω<sub>p</sub>(1/2) autour de <span class=vec>n</span> la vitesse de
<strong>pivotement</strong>.</p>
<table class="t cours-t"><thead><tr><th></th><th>ω<sub>r</sub> = 0 ; ω<sub>p</sub> = 0</th><th>ω<sub>r</sub> = 0 ; ω<sub>p</sub> ≠ 0</th>
<th>ω<sub>r</sub> ≠ 0 ; ω<sub>p</sub> = 0</th><th>ω<sub>r</sub> ≠ 0 ; ω<sub>p</sub> ≠ 0</th></tr></thead><tbody>
<tr><th>{V}A(1/2) = <span class=vec>0</span></th><td>adhérence</td><td>pivotement</td><td>roulement</td><td>roulement avec pivotement</td></tr>
<tr><th>{V}A(1/2) ≠ <span class=vec>0</span></th><td>glissement</td><td>glissement avec pivotement</td><td>glissement avec roulement</td><td>glissement avec roulement et pivotement</td></tr>
</tbody></table>
<p>Ces combinaisons servent à formuler les hypothèses simplificatrices d'une étude de mécanique (une roue qui roule
sans glisser : V(A, roue/route) = <span class=vec>0</span>, comme pour le vélo de la section 2).</p>
<p>La construction graphique de la composition des vitesses est traitée dans le
<a href="?ex=cours-cinematique-graphique#cg-composition">cours 2, section 7</a>.</p>
"""))
    # ------------------------------------------------------------------ 8 à 10. MRU, MRUV, mouvement circulaire
    s.append(course_section(8, "ca-mru", "Mouvement rectiligne uniforme (MRU)", cm.mru(A)))
    s.append(course_section(9, "ca-mruv", "Mouvement rectiligne uniformément varié (MRUV)", cm.mruv(SIMU_MRUV)))
    essentiel = cartes([
        ("Référentiel", "Repère d'espace + repère de temps. Le mouvement dépend toujours du référentiel : on note Mvt 1/0."),
        ("Trajectoire", "Courbe décrite par un point dans un repère ; toujours préciser à quel solide le point appartient."),
        ("Vitesse", "Dérivée de la position (v = dx/dt) ; tangente à la trajectoire ; en m/s."),
        ("Accélération", "Dérivée de la vitesse ; Γt = dv/dt sur la tangente, Γn = −v²/R sur la normale extérieure."),
        ("MRU", "γ = 0 ; v constante ; x = v·t + x0. Graphe des espaces : une droite de pente v."),
        ("MRUV", "γ constante ; v = γt + v0 ; x = ½γt² + v0t + x0 ; v² − v0² = 2γ(x − x0)."),
        ("MCU", "θ = ωt + θ0 ; v = R·ω ; ω = 2πN/60 ; accélération R·ω², dirigée vers le centre."),
        ("Distance parcourue", "Aire sous le graphe des vitesses ; en MRUV : (v début + v fin) / 2 × durée.")])
    s.append(course_section(10, "ca-circulaire", "Mouvement circulaire (MC, MCU, MCUV)", cm.circulaire(A, SIMU_ROT, essentiel)))
    # ------------------------------------------------------------------ quiz
    quiz = [
        ("Un référentiel, c'est…", ["un repère d'espace seul", "un repère d'espace et un repère de temps", "le solide le plus lourd"], 1,
         "Il faut à la fois repérer les positions et les dates."),
        ("Un voyageur assis dans un train qui roule à 30 m/s. Sa vitesse par rapport au train est :", ["30 m/s", "nulle", "on ne peut pas savoir"], 1,
         "Par rapport au wagon, il n'a pas de mouvement."),
        ("La trajectoire d'un point de la jante d'une roue qui roule sur la route est :", ["un cercle", "une droite", "une cycloïde"], 2,
         "Par rapport à la route : arcs de cycloïde ; par rapport au cadre : un cercle."),
        ("Le vecteur vitesse d'un point est toujours…", ["dirigé vers le centre", "tangent à la trajectoire", "perpendiculaire à la trajectoire"], 1,
         "Direction : la tangente à la trajectoire au point considéré."),
        ("Une roue tourne à 600 tr/min. Sa vitesse angulaire vaut environ :", ["10 rad/s", "62,8 rad/s", "3 770 rad/s"], 1,
         "ω = 2π × 600 / 60 = 62,8 rad/s."),
        ("Un point est à 0,2 m de l'axe d'un solide qui tourne à 50 rad/s. Sa vitesse :", ["10 m/s", "250 m/s", "0,004 m/s"], 0,
         "V = r·ω = 0,2 × 50 = 10 m/s."),
        ("Dans un solide en translation, à un instant donné…", ["tous les points ont la même vitesse", "les vitesses sont proportionnelles à la distance à l'axe", "un seul point a une vitesse nulle"], 0,
         "Trajectoires parallèles, vitesses identiques."),
        ("Une voiture part de l'arrêt avec γ = 2 m/s². Sa vitesse après 5 s :", ["2,5 m/s", "10 m/s", "25 m/s"], 1,
         "v = γ·t + v0 = 2 × 5 + 0 = 10 m/s."),
        ("En rotation uniforme, l'accélération d'un point est…", ["nulle", "tangente à la trajectoire", "dirigée vers le centre"], 2,
         "Γt = 0 mais Γn = ω²·r ≠ 0, dirigée vers le centre."),
        ("V(A, 3/1) = V(A, 3/2) + V(A, 2/1) : V(A, 3/2) est la vitesse…", ["absolue", "relative", "d'entraînement"], 1,
         "Vitesse absolue = vitesse relative + vitesse d'entraînement."),
    ]
    s.append(quiz_section(11, "ca-quiz", quiz + cm.QUIZ, "caq"))
    return (course_head("Cours 1", "analytique", "Cinématique analytique",
                        "Décrire le mouvement par le calcul : référentiels, trajectoires, vitesses et accélérations, "
                        "analyse de mouvements, mouvements rectilignes uniforme et uniformément varié, mouvement "
                        "circulaire, composition des mouvements.",
                        ["Définir le mouvement d'un solide par rapport à un référentiel.",
                         "Exprimer et calculer vitesses et accélérations d'un point.",
                         "Définir un mouvement par son équation horaire ; reconnaître un mouvement uniforme ou "
                         "uniformément varié, rectiligne ou circulaire.",
                         "Exploiter les lois et les graphes de ces mouvements (MRU, MRUV, MCU, MCUV)."],
                        ["Concept de mouvement ; coordonnées d'un vecteur.", "Résolution d'équations et dérivation "
                         "d'une fonction.", "Repérage dans le plan (coordonnées cartésiennes et polaires)."])
            + f'<p class="c-top"><a href="?">{H} Accueil</a></p>' + course_nav(sections) + '<div class="cours">'
            + "".join(s) + '</div><div class="cours-foot"><a class="btn" href="?ex=cours-cinematique-graphique">Cours 2 : '
            f'cinématique graphique</a><a class="btn ghost" href="?">{H} Accueil</a></div>')


SIMU_MRUV = """<div class="simu" id="ca-mruv"><h3>Simulateur : x(t), v(t) et a(t)</h3>
<div class="simu-grid"><label>Position initiale x<sub>0</sub> <output class="ca-x0"></output><input type="range" min="-20" max="20" step="1" value="0" class="ca-x0r"></label>
<label>Vitesse initiale v<sub>0</sub> <output class="ca-v0"></output><input type="range" min="-10" max="20" step="0.5" value="4" class="ca-v0r"></label>
<label>Accélération γ <output class="ca-g"></output><input type="range" min="-4" max="4" step="0.25" value="1.5" class="ca-gr"></label></div>
<div class="simu-btns"><button type="button" class="btn ca-go">Lancer le mobile</button><button type="button" class="btn ghost" data-pre="u">Mouvement uniforme</button>
<button type="button" class="btn ghost" data-pre="a">Démarrage d'une voiture</button><button type="button" class="btn ghost" data-pre="f">Freinage</button></div>
<div class="simu-fig"><svg viewBox="0 0 760 360" role="img" aria-label="Le mobile sur son axe et les trois graphes x(t), v(t), a(t)"><g class="ca-g-monde"></g></svg></div>
<div class="simu-out"><div><span>Instant t</span><b class="ca-ot"></b></div><div><span>Position x</span><b class="ca-ox"></b></div>
<div><span>Vitesse v</span><b class="ca-ov"></b></div><div><span>Nature</span><b class="ca-on"></b></div></div>
<p class="simu-note">Graphes sur 10 s. La pente de x(t) est la vitesse ; la pente de v(t) est l'accélération. En
mouvement uniforme, x(t) est une droite ; en mouvement uniformément varié, une branche de parabole.</p></div>"""
SIMU_ROT = """<div class="simu" id="ca-rot"><h3>Le point P en rotation : V, Γn, Γt</h3>
<div class="simu-grid"><label>Vitesse angulaire initiale ω<sub>0</sub> <output class="ca-w0"></output><input type="range" min="0.2" max="3" step="0.1" value="1.2" class="ca-w0r"></label>
<label>Accélération angulaire θ'' <output class="ca-wp"></output><input type="range" min="-0.5" max="0.5" step="0.05" value="0.2" class="ca-wpr"></label>
<label>Rayon r : 1 m</label></div>
<div class="simu-btns"><button type="button" class="btn ca-go">Lancer</button><button type="button" class="btn ghost ca-raz">Recommencer</button></div>
<div class="simu-fig"><svg viewBox="0 0 760 330" role="img" aria-label="Point P sur un cercle avec sa vitesse, ses accélérations normale et tangentielle"><g class="ca-r-monde"></g></svg></div>
<div class="simu-out"><div><span>ω</span><b class="ca-ow"></b></div><div><span>V = r·ω</span><b class="ca-ovr"></b></div>
<div><span>|Γn| = ω²·r ; Γt = θ''·r</span><b class="ca-og"></b></div><div><span>Mouvement</span><b class="ca-onat"></b></div></div>
<p class="simu-note">Bleu : vitesse V ; vert : accélérations normale Γn (vers le centre) et tangentielle Γt, et leur
somme Γ en vert foncé. Quand ω s'annule en mouvement décéléré, le point s'arrête puis repart en sens inverse.</p></div>"""

JS = r"""
  /* ---------------------------------------------------------------- cours 1 : cinématique analytique */
  function initCoursAnalytique(root) {
    initCommun(root);
    var NS = "http://www.w3.org/2000/svg";
    function el(g, tag, at, txt) {
      var e = document.createElementNS(NS, tag);
      for (var k in at) e.setAttribute(k, at[k]);
      if (txt !== undefined) e.textContent = txt;
      g.appendChild(e); return e;
    }
    function fleche(g, x1, y1, x2, y2, c, w) {
      var dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
      if (L < 1) return;
      var ux = dx / L, uy = dy / L, h = Math.min(11, L * 0.5);
      el(g, "line", { x1: x1, y1: y1, x2: x2 - ux * h * 0.8, y2: y2 - uy * h * 0.8, stroke: c, "stroke-width": w || 3 });
      el(g, "polygon", { points: x2 + "," + y2 + " " + (x2 - ux * h - uy * h * 0.4) + "," + (y2 - uy * h + ux * h * 0.4) + " " + (x2 - ux * h + uy * h * 0.4) + "," + (y2 - uy * h - ux * h * 0.4), fill: c });
    }
    function q(s) { return root.querySelector(s); }
    function boutons(box, attr, f) {
      Array.prototype.forEach.call(box.querySelectorAll("[" + attr + "]"), function (b) {
        b.addEventListener("click", function () {
          Array.prototype.forEach.call(box.querySelectorAll("[" + attr + "]"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          f(b.getAttribute(attr));
        });
      });
    }

    // ---------- train et voyageur
    (function () {
      var box = q("#ca-train"); if (!box) return;
      var g = box.querySelector(".ca-tr-monde"), vue = 0, marche = 1, t = 0, trace = [];
      var V10 = 20, V21 = 1.5, K = 6;   // m/s ; px par m (le voyageur), le train défile en boucle
      boutons(box, "data-vue", function (v) { vue = +v; trace = []; });
      boutons(box, "data-marche", function (v) { marche = +v; trace = []; t = 0; });
      function dessin() {
        g.innerHTML = "";
        var xt = vue === 0 ? (t * V10 * 3) % 900 - 260 : 230;              // position du wagon à l'écran
        var xp = xt + 60 + ((marche * V21 * t * K) % 220 + 220) % 220;        // voyageur dans le wagon
        var sol = vue === 0 ? 0 : -(t * V10 * 3) % 80;
        el(g, "line", { x1: 0, y1: 170, x2: 760, y2: 170, stroke: "#1C2530", "stroke-width": 3 });
        for (var i = -1; i < 11; i++) el(g, "line", { x1: i * 80 + sol, y1: 170, x2: i * 80 + sol - 14, y2: 186, stroke: "#1C2530", "stroke-width": 1.5 });
        for (var j = 0; j < 4; j++) { var xp_ = ((j * 220 + 60 + sol * 3) % 880 + 880) % 880 - 60; el(g, "rect", { x: xp_, y: 110, width: 6, height: 60, fill: "#7A848C" }); }
        el(g, "rect", { x: xt, y: 70, width: 330, height: 86, rx: 8, fill: "#E9EDF1", stroke: "#1C2530", "stroke-width": 2 });
        for (var w = 0; w < 5; w++) el(g, "rect", { x: xt + 18 + w * 62, y: 84, width: 40, height: 26, fill: "#fff", stroke: "#1C2530" });
        el(g, "circle", { cx: xt + 60, cy: 160, r: 10, fill: "#1C2530" }); el(g, "circle", { cx: xt + 270, cy: 160, r: 10, fill: "#1C2530" });
        el(g, "text", { x: xt + 310, y: 64, "font-size": 15, "font-weight": 700 }, "1");
        // voyageur
        el(g, "circle", { cx: xp, cy: 118, r: 6, fill: "#B42318" });
        el(g, "line", { x1: xp, y1: 124, x2: xp, y2: 142, stroke: "#B42318", "stroke-width": 3 });
        el(g, "text", { x: xp + 8, y: 112, "font-size": 15, "font-weight": 700, fill: "#B42318" }, "2");
        // trajectoire du voyageur dans le repère d'observation : ses positions successives à l'écran
        if (trace.length && Math.abs(xp - trace[trace.length - 1]) > 40) trace = [];
        trace.push(xp); if (trace.length > 600) trace.shift();
        if (trace.length > 1) el(g, "line", { x1: Math.min.apply(null, trace), y1: 148, x2: Math.max.apply(null, trace), y2: 148, stroke: "#B42318", "stroke-width": 2.5, "stroke-dasharray": "6 4" });
        el(g, "text", { x: 12, y: 30, "font-size": 14, fill: "#B42318" }, "En rouge, en pointillés : la trajectoire du voyageur (2) dans ce repère.");
        el(g, "text", { x: 12, y: 50, "font-size": 14, fill: "#46525C" }, vue === 0 ? "Repère R0 lié à la voie (0)" : "Repère R1 lié au wagon (1) : c'est la voie qui défile");
        el(g, "text", { x: 700, y: 200, "font-size": 15, "font-weight": 700, "text-anchor": "end" }, "0");
        var v20 = V10 + marche * V21, v21 = marche * V21;
        box.querySelector(".ca-v21").textContent = fr(v21, 1) + " m/s";
        box.querySelector(".ca-v20").textContent = fr(v20, 1) + " m/s";
        box.querySelector(".ca-obs").textContent = vue === 0 ? "absolu (2/0)" : "relatif (2/1)";
      }
      var last = 0;
      animer(function (s) { if (RM && s - last < 0.5) return; t += Math.min(0.05, s - last); last = s; dessin(); });
    })();

    // ---------- roue de vélo
    (function () {
      var box = q("#ca-velo"); if (!box) return;
      var g = box.querySelector(".ca-v-monde"), x = 0, roule = false, R = 60, y0 = 200, traces = { A: [], B: [], C: [] };
      box.querySelector(".ca-go").addEventListener("click", function () { roule = !roule; this.textContent = roule ? "Arrêter" : "Rouler"; });
      box.querySelector(".ca-raz").addEventListener("click", function () { x = 0; traces = { A: [], B: [], C: [] }; dessin(); });
      function dessin() {
        g.innerHTML = "";
        var cx = 70 + x, cy = y0 - R, th = x / R;                 // roulement sans glissement : angle = distance / R
        var ax = cx - R * Math.sin(th), ay = cy + R * Math.cos(th);  // A part du contact avec la route
        var c = { A: [ax, ay], B: [cx, cy], C: [cx - 22, cy - 92] };
        if (box.querySelector(".ca-traces").checked) for (var k in c) traces[k].push(c[k]);
        el(g, "line", { x1: 0, y1: y0, x2: 760, y2: y0, stroke: "#1C2530", "stroke-width": 3 });
        el(g, "text", { x: 740, y: y0 + 22, "font-size": 15, "font-weight": 700 }, "0");
        var cols = { A: "#B42318", B: "#1F5FA8", C: "#1B7A43" };
        for (var k2 in traces) if (traces[k2].length > 1)
          el(g, "polyline", { points: traces[k2].map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" "), fill: "none", stroke: cols[k2], "stroke-width": 2, "stroke-dasharray": k2 === "A" ? "" : "5 4" });
        el(g, "circle", { cx: cx, cy: cy, r: R, fill: "none", stroke: "#1C2530", "stroke-width": 3 });
        for (var i = 0; i < 8; i++) { var a = th + i * Math.PI / 4; el(g, "line", { x1: cx, y1: cy, x2: cx - R * Math.sin(a), y2: cy + R * Math.cos(a), stroke: "#A5ADAA", "stroke-width": 1.2 }); }
        el(g, "line", { x1: cx, y1: cy, x2: cx - 22, y2: cy - 92, stroke: "#46525C", "stroke-width": 5 });
        el(g, "line", { x1: cx - 22, y1: cy - 92, x2: cx - 60, y2: cy - 98, stroke: "#46525C", "stroke-width": 5 });
        el(g, "text", { x: cx - 62, y: cy - 40, "font-size": 15, "font-weight": 700 }, "2");
        el(g, "text", { x: cx + R + 4, y: cy + 4, "font-size": 15, "font-weight": 700 }, "1");
        for (var k3 in c) { el(g, "circle", { cx: c[k3][0], cy: c[k3][1], r: 4.5, fill: cols[k3] }); el(g, "text", { x: c[k3][0] + 7, y: c[k3][1] - 7, "font-size": 15, "font-weight": 700, fill: cols[k3] }, k3); }
        el(g, "text", { x: 12, y: 22, "font-size": 13, fill: "#46525C" }, "T(A∈1/0) en rouge · T(B∈1/0) en bleu · T(C∈2/0) en vert");
      }
      var last = 0;
      animer(function (s) {
        var dt = Math.min(0.05, s - last); last = s;
        if (!roule) return;
        x += dt * 90; if (x > 600) { x = 0; traces = { A: [], B: [], C: [] }; }
        dessin();
      });
      dessin();
    })();

    // ---------- vecteurs position, vitesse, accélération
    (function () {
      var box = q("#ca-vect"); if (!box) return;
      var g = box.querySelector(".ca-vt-monde"), r = box.querySelector(".ca-tr"), O = [280, 175], K = 48;
      function P(t) { return [3 * Math.cos(t) + 1, 2 * Math.sin(t)]; }
      function ecr(p) { return [O[0] + p[0] * K, O[1] - p[1] * K]; }
      function dessin() {
        var t = +r.value; g.innerHTML = "";
        var pts = []; for (var u = 0; u <= 6.3; u += 0.05) { var e = ecr(P(u)); pts.push(e[0].toFixed(1) + "," + e[1].toFixed(1)); }
        el(g, "line", { x1: 20, y1: O[1], x2: 560, y2: O[1], stroke: "#46525C" }); el(g, "line", { x1: O[0], y1: 320, x2: O[0], y2: 20, stroke: "#46525C" });
        el(g, "text", { x: 548, y: O[1] - 6, "font-size": 14 }, "x0"); el(g, "text", { x: O[0] + 6, y: 30, "font-size": 14 }, "y0");
        el(g, "polyline", { points: pts.join(" "), fill: "none", stroke: "#1C2530", "stroke-width": 2, "stroke-dasharray": "6 4" });
        el(g, "text", { x: O[0] + 4 * K - 30, y: O[1] + 1.95 * K, "font-size": 14 }, "T M1/0");
        var p = P(t), v = [-3 * Math.sin(t), 2 * Math.cos(t)], a = [-3 * Math.cos(t), -2 * Math.sin(t)], m = ecr(p);
        fleche(g, O[0], O[1], m[0], m[1], "#B42318", 2.5);
        fleche(g, m[0], m[1], m[0] + v[0] * 30, m[1] - v[1] * 30, "#1F5FA8", 3.5);
        fleche(g, m[0], m[1], m[0] + a[0] * 22, m[1] - a[1] * 22, "#1B7A43", 3.5);
        el(g, "circle", { cx: m[0], cy: m[1], r: 5, fill: "#1C2530" });
        el(g, "text", { x: m[0] + 8, y: m[1] - 8, "font-size": 16, "font-weight": 700 }, "M");
        el(g, "text", { x: O[0] - 16, y: O[1] + 18, "font-size": 16, "font-weight": 700 }, "O");
        el(g, "text", { x: 590, y: 60, "font-size": 15, fill: "#B42318", "font-weight": 700 }, "OM : position");
        el(g, "text", { x: 590, y: 85, "font-size": 15, fill: "#1F5FA8", "font-weight": 700 }, "V : vitesse");
        el(g, "text", { x: 590, y: 110, "font-size": 15, fill: "#1B7A43", "font-weight": 700 }, "Γ : accélération");
        box.querySelector(".ca-t").textContent = fr(t, 2) + " s";
        box.querySelector(".ca-pos").textContent = fr(p[0], 2) + " ; " + fr(p[1], 2);
        box.querySelector(".ca-vit").textContent = fr(v[0], 2) + " ; " + fr(v[1], 2);
        box.querySelector(".ca-nv").textContent = fr(Math.hypot(v[0], v[1]), 2) + " m/s";
        box.querySelector(".ca-acc").textContent = fr(a[0], 2) + " ; " + fr(a[1], 2);
      }
      r.addEventListener("input", dessin);
      var last = 0;
      animer(function (s) { var dt = Math.min(0.05, s - last); last = s; if (box.querySelector(".ca-anim").checked) { r.value = ((+r.value + dt * 0.7) % 6.28).toFixed(3); dessin(); } });
      dessin();
    })();

    // ---------- quatre mouvements plans
    (function () {
      var figs = root.querySelectorAll(".ca-m"); if (!figs.length) return;
      var tr = [];
      Array.prototype.forEach.call(figs, function (f, i) { tr[i] = [[], []]; });
      function poly(g, pts, c) { if (pts.length > 1) el(g, "polyline", { points: pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" "), fill: "none", stroke: c, "stroke-width": 1.6, "stroke-dasharray": "4 3" }); }
      function forme(g, pts) { el(g, "polygon", { points: pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" "), fill: "#B8C4CF", stroke: "#1C2530", "stroke-width": 1.5 }); }
      animer(function (s) {
        var t = RM ? 1.2 : s;
        Array.prototype.forEach.call(figs, function (f, i) {
          f.innerHTML = ""; var m = f.getAttribute("data-m"), A, B, pts;
          if (m === "tr") {
            var x = 60 + 70 * (1 - Math.cos(t * 0.9));
            el(f, "line", { x1: 10, y1: 100, x2: 230, y2: 100, stroke: "#46525C", "stroke-width": 6 });
            pts = [[x - 30, 70], [x + 30, 70], [x + 30, 120], [x - 30, 120]]; A = [x - 20, 80]; B = [x + 20, 112];
          } else if (m === "ro") {
            var a = t * 1.3, c = [120, 75];
            pts = [[0, -8], [70, -4], [70, 4], [0, 8], [-70, 4], [-70, -4]].map(function (p) { return [c[0] + p[0] * Math.cos(a) - p[1] * Math.sin(a), c[1] + p[0] * Math.sin(a) + p[1] * Math.cos(a)]; });
            A = [c[0] + 62 * Math.cos(a), c[1] + 62 * Math.sin(a)]; B = [c[0] - 32 * Math.cos(a), c[1] - 32 * Math.sin(a)];
          } else if (m === "pl") {
            var b = t * 1.2, O = [55, 85], R = 26, L = 110;
            A = [O[0] + R * Math.cos(b), O[1] - R * Math.sin(b)];
            var Bx = A[0] + Math.sqrt(L * L - Math.pow(A[1] - O[1], 2)); B = [Bx, O[1]];
            el(f, "line", { x1: O[0], y1: O[1], x2: A[0], y2: A[1], stroke: "#46525C", "stroke-width": 4 });
            el(f, "rect", { x: Bx - 12, y: O[1] - 12, width: 24, height: 24, fill: "#E9EDF1", stroke: "#1C2530" });
            var u = [(B[0] - A[0]) / L, (B[1] - A[1]) / L], n = [-u[1] * 6, u[0] * 6];
            pts = [[A[0] + n[0], A[1] + n[1]], [B[0] + n[0], B[1] + n[1]], [B[0] - n[0], B[1] - n[1]], [A[0] - n[0], A[1] - n[1]]];
            A = [A[0] + u[0] * 30, A[1] + u[1] * 30]; B = [A[0] + u[0] * 45, A[1] + u[1] * 45];
          } else {
            var d = Math.sin(t * 1.1) * 0.9, p1 = [80, 135], p2 = [160, 135], l = 80;
            var q1 = [p1[0] + l * Math.sin(d), p1[1] - l * Math.cos(d)], q2 = [p2[0] + l * Math.sin(d), p2[1] - l * Math.cos(d)];
            el(f, "line", { x1: p1[0], y1: p1[1], x2: q1[0], y2: q1[1], stroke: "#46525C", "stroke-width": 3 });
            el(f, "line", { x1: p2[0], y1: p2[1], x2: q2[0], y2: q2[1], stroke: "#46525C", "stroke-width": 3 });
            pts = [[q1[0] - 20, q1[1] - 6], [q2[0] + 20, q2[1] - 6], [q2[0] + 20, q2[1] + 2], [q1[0] - 20, q1[1] + 2]];
            A = [q1[0] - 10, q1[1] - 2]; B = [q2[0] + 10, q2[1] - 2];
          }
          tr[i][0].push(A); tr[i][1].push(B);
          if (tr[i][0].length > 260) { tr[i][0].shift(); tr[i][1].shift(); }
          poly(f, tr[i][0], "#B42318"); poly(f, tr[i][1], "#1F5FA8");
          forme(f, pts);
          el(f, "circle", { cx: A[0], cy: A[1], r: 3.5, fill: "#B42318" }); el(f, "circle", { cx: B[0], cy: B[1], r: 3.5, fill: "#1F5FA8" });
        });
      });
    })();

    // ---------- hélice : répartition des vitesses
    (function () {
      var box = q("#ca-helice"); if (!box) return;
      var g = box.querySelector(".ca-h-monde"), nr = box.querySelector(".ca-nr"), rr = box.querySelector(".ca-rr");
      function dessin() {
        g.innerHTML = "";
        var N = +nr.value, w = 2 * Math.PI * N / 60, r = +rr.value, O = [120, 230], L = 560, K = 0.9;
        el(g, "line", { x1: O[0], y1: O[1], x2: O[0] + L, y2: O[1], stroke: "#1C2530", "stroke-width": 14, "stroke-linecap": "round", opacity: 0.25 });
        el(g, "circle", { cx: O[0], cy: O[1], r: 9, fill: "#fff", stroke: "#1C2530", "stroke-width": 2 });
        el(g, "text", { x: O[0] - 18, y: O[1] + 26, "font-size": 16, "font-weight": 700 }, "O");
        el(g, "text", { x: O[0] + L + 6, y: O[1] + 26, "font-size": 16, "font-weight": 700 }, "A");
        for (var i = 1; i <= 10; i++) { var x = O[0] + L * i / 10, v = w * i / 10; fleche(g, x, O[1], x, O[1] - v * K * 1.6, "#7A9CC6", 2); }
        el(g, "line", { x1: O[0], y1: O[1], x2: O[0] + L, y2: O[1] - w * K * 1.6, stroke: "#B26A00", "stroke-width": 1.5, "stroke-dasharray": "6 4" });
        var xp = O[0] + L * r, vp = w * r;
        fleche(g, xp, O[1], xp, O[1] - vp * K * 1.6, "#1F5FA8", 4);
        el(g, "circle", { cx: xp, cy: O[1], r: 6, fill: "#B42318" });
        el(g, "text", { x: xp + 8, y: O[1] - vp * K * 1.6 - 8, "font-size": 15, "font-weight": 700, fill: "#1F5FA8" }, fr(vp, 1) + " m/s");
        el(g, "text", { x: 140, y: 30, "font-size": 14, fill: "#B26A00" }, "droite de répartition : V proportionnelle à la distance à l'axe");
        box.querySelector(".ca-n").textContent = N + " tr/min";
        box.querySelector(".ca-r").textContent = fr(r, 2) + " m";
        box.querySelector(".ca-w").textContent = fr(w, 1) + " rad/s";
        box.querySelector(".ca-vp").textContent = fr(vp, 1) + " m/s";
        box.querySelector(".ca-va").textContent = fr(w, 1) + " m/s";
        box.querySelector(".ca-vkm").textContent = fr(w * 3.6, 0) + " km/h";
      }
      nr.addEventListener("input", dessin); rr.addEventListener("input", dessin); dessin();
    })();

    // ---------- mouvement rectiligne uniformément varié
    (function () {
      var box = q("#ca-mruv"); if (!box) return;
      var g = box.querySelector(".ca-g-monde"), x0r = box.querySelector(".ca-x0r"), v0r = box.querySelector(".ca-v0r"), gr = box.querySelector(".ca-gr");
      var t = 10, court = false;
      Array.prototype.forEach.call(box.querySelectorAll("[data-pre]"), function (b) {
        b.addEventListener("click", function () {
          var p = { u: [0, 6, 0], a: [0, 0, 2.5], f: [0, 20, -1.5] }[b.getAttribute("data-pre")];
          x0r.value = p[0]; v0r.value = p[1]; gr.value = p[2]; t = 10; dessin();
        });
      });
      box.querySelector(".ca-go").addEventListener("click", function () { t = 0; court = true; });
      [x0r, v0r, gr].forEach(function (r) { r.addEventListener("input", function () { t = 10; dessin(); }); });
      function graphe(x0, y0, w, h, f, ymin, ymax, titre, unite, c) {
        el(g, "rect", { x: x0, y: y0, width: w, height: h, fill: "#fff", stroke: "#A5ADAA" });
        var yz = y0 + h * ymax / (ymax - ymin);
        if (yz > y0 && yz < y0 + h) el(g, "line", { x1: x0, y1: yz, x2: x0 + w, y2: yz, stroke: "#46525C" });
        var pts = [];
        for (var u = 0; u <= 10.001; u += 0.1) pts.push((x0 + w * u / 10).toFixed(1) + "," + (y0 + h * (ymax - f(u)) / (ymax - ymin)).toFixed(1));
        el(g, "polyline", { points: pts.join(" "), fill: "none", stroke: c, "stroke-width": 2.5 });
        var xc = x0 + w * Math.min(t, 10) / 10;
        el(g, "line", { x1: xc, y1: y0, x2: xc, y2: y0 + h, stroke: "#B26A00", "stroke-dasharray": "4 3" });
        el(g, "text", { x: x0 + 4, y: y0 + 16, "font-size": 14, "font-weight": 700, fill: c }, titre);
        el(g, "text", { x: x0 + w - 4, y: y0 + h - 6, "font-size": 12, "text-anchor": "end" }, "t (s)");
        el(g, "text", { x: x0 + 4, y: y0 + h + 14, "font-size": 11, fill: "#46525C" }, fr(ymin, 0) + " à " + fr(ymax, 0) + " " + unite);
      }
      function dessin() {
        g.innerHTML = "";
        var x0 = +x0r.value, v0 = +v0r.value, ga = +gr.value;
        function X(u) { return 0.5 * ga * u * u + v0 * u + x0; }
        function Vt(u) { return ga * u + v0; }
        var xs = []; for (var u = 0; u <= 10; u += 0.5) xs.push(X(u));
        var xmin = Math.min(0, Math.min.apply(null, xs)), xmax = Math.max(10, Math.max.apply(null, xs));
        var vmin = Math.min(0, Vt(0), Vt(10)) - 1, vmax = Math.max(0, Vt(0), Vt(10)) + 1;
        // l'axe du mobile
        var tt = Math.min(t, 10), px = 30 + 700 * (X(tt) - xmin) / (xmax - xmin);
        el(g, "line", { x1: 30, y1: 40, x2: 730, y2: 40, stroke: "#1C2530", "stroke-width": 2 });
        var pz = 30 + 700 * (0 - xmin) / (xmax - xmin);
        el(g, "line", { x1: pz, y1: 32, x2: pz, y2: 48, stroke: "#1C2530", "stroke-width": 2 }); el(g, "text", { x: pz - 4, y: 64, "font-size": 13 }, "O");
        el(g, "rect", { x: px - 16, y: 22, width: 32, height: 16, rx: 4, fill: "#1F5FA8" });
        el(g, "text", { x: 734, y: 30, "font-size": 13 }, "x");
        graphe(30, 90, 220, 230, X, xmin, xmax, "x(t)", "m", "#B42318");
        graphe(270, 90, 220, 230, Vt, vmin, vmax, "v(t)", "m/s", "#1F5FA8");
        graphe(510, 90, 220, 230, function () { return ga; }, -5, 5, "a(t)", "m/s²", "#1B7A43");
        box.querySelector(".ca-x0").textContent = fr(x0, 0) + " m";
        box.querySelector(".ca-v0").textContent = fr(v0, 1) + " m/s";
        box.querySelector(".ca-g").textContent = fr(ga, 2) + " m/s²";
        box.querySelector(".ca-ot").textContent = fr(tt, 1) + " s";
        box.querySelector(".ca-ox").textContent = fr(X(tt), 1) + " m";
        box.querySelector(".ca-ov").textContent = fr(Vt(tt), 1) + " m/s";
        var v = Vt(tt);
        box.querySelector(".ca-on").textContent = ga === 0 ? "uniforme" : (v * ga > 0 ? "accéléré" : (v === 0 ? "arrêt" : "décéléré"));
      }
      var last = 0;
      animer(function (s) { var dt = Math.min(0.05, s - last); last = s; if (court) { t += dt * 2; if (t >= 10) { t = 10; court = false; } dessin(); } });
      dessin();
    })();

    // ---------- rotation du point : V, Γn, Γt
    (function () {
      var box = q("#ca-rot"); if (!box) return;
      var g = box.querySelector(".ca-r-monde"), w0r = box.querySelector(".ca-w0r"), wpr = box.querySelector(".ca-wpr");
      var th = 0.6, w = 1.2, court = false, C = [240, 165], R = 120;
      box.querySelector(".ca-go").addEventListener("click", function () { court = !court; this.textContent = court ? "Arrêter" : "Lancer"; });
      box.querySelector(".ca-raz").addEventListener("click", function () { th = 0.6; w = +w0r.value; dessin(); });
      w0r.addEventListener("input", function () { w = +w0r.value; dessin(); });
      wpr.addEventListener("input", dessin);
      function dessin() {
        g.innerHTML = "";
        var wp = +wpr.value, P = [C[0] + R * Math.cos(th), C[1] - R * Math.sin(th)];
        var n = [Math.cos(th), -Math.sin(th)], tg = [-Math.sin(th), -Math.cos(th)];
        el(g, "circle", { cx: C[0], cy: C[1], r: R, fill: "none", stroke: "#1C2530", "stroke-width": 2 });
        el(g, "line", { x1: C[0] - 150, y1: C[1], x2: C[0] + 160, y2: C[1], stroke: "#A5ADAA" }); el(g, "line", { x1: C[0], y1: C[1] + 150, x2: C[0], y2: C[1] - 155, stroke: "#A5ADAA" });
        el(g, "line", { x1: C[0], y1: C[1], x2: P[0], y2: P[1], stroke: "#46525C", "stroke-width": 1.5 });
        var V = w * 1, Gn = w * w * 1, Gt = wp * 1, kv = 38, kg = 26;
        fleche(g, P[0], P[1], P[0] + tg[0] * V * kv, P[1] + tg[1] * V * kv, "#1F5FA8", 4);
        fleche(g, P[0], P[1], P[0] - n[0] * Gn * kg, P[1] - n[1] * Gn * kg, "#1B7A43", 3);
        if (Math.abs(Gt) > 1e-6) fleche(g, P[0], P[1], P[0] + tg[0] * Gt * kg * 4, P[1] + tg[1] * Gt * kg * 4, "#4CAF50", 3);
        fleche(g, P[0], P[1], P[0] - n[0] * Gn * kg + tg[0] * Gt * kg * 4, P[1] - n[1] * Gn * kg + tg[1] * Gt * kg * 4, "#0B5A2E", 2);
        el(g, "circle", { cx: P[0], cy: P[1], r: 5, fill: "#1C2530" });
        el(g, "text", { x: P[0] + 8, y: P[1] + 18, "font-size": 16, "font-weight": 700 }, "P");
        el(g, "text", { x: C[0] - 18, y: C[1] + 18, "font-size": 16, "font-weight": 700 }, "O");
        el(g, "text", { x: 470, y: 60, "font-size": 15, fill: "#1F5FA8", "font-weight": 700 }, "V = r·ω (tangente)");
        el(g, "text", { x: 470, y: 85, "font-size": 15, fill: "#1B7A43", "font-weight": 700 }, "Γn = ω²·r (vers O)");
        el(g, "text", { x: 470, y: 110, "font-size": 15, fill: "#4CAF50", "font-weight": 700 }, "Γt = θ''·r (tangente ; Γt ×4)");
        el(g, "text", { x: 470, y: 135, "font-size": 15, fill: "#0B5A2E", "font-weight": 700 }, "Γ = Γn + Γt");
        box.querySelector(".ca-w0").textContent = fr(+w0r.value, 1) + " rad/s";
        box.querySelector(".ca-wp").textContent = fr(wp, 2) + " rad/s²";
        box.querySelector(".ca-ow").textContent = fr(w, 2) + " rad/s";
        box.querySelector(".ca-ovr").textContent = fr(Math.abs(V), 2) + " m/s";
        box.querySelector(".ca-og").textContent = fr(Gn, 2) + " ; " + fr(Gt, 2) + " m/s²";
        box.querySelector(".ca-onat").textContent = wp === 0 ? "uniforme" : (w * wp > 0 ? "accéléré" : "décéléré");
      }
      var last = 0;
      animer(function (s) {
        var dt = Math.min(0.05, s - last); last = s;
        if (!court) return;
        var wp = +wpr.value; w += wp * dt; th += w * dt;
        if (Math.abs(w) > 6) { w = +w0r.value; }
        dessin();
      });
      dessin();
    })();
    initLaboMouvements(root, el, fleche);
  }
"""

CSS = """
/* cours 1 */
.page-cours-cinematique-analytique .simu-fig svg text{font-family:var(--f-texte)}
"""
