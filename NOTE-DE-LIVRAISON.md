# Note de livraison — Cinématique : cours, atelier de construction et activités interactifs

## Construction reprise du dépôt « Chaîne fonctionnelle »

**Sources** : le chapitre « Cinématique » (13 pages : généralités, cinématique du solide, cinématique du point) et la
séquence « Cinématique graphique » (23 pages : cours en sept parties et sept exercices avec leurs documents réponses),
fournis en PDF. Les PDF ne sont pas versionnés : `outils/preparer-images.sh` en extrait les fonds et photos utiles dans
`src/images/originaux/`.

**Dépôt non modifié** : Chaîne fonctionnelle, consulté pour la construction (générateur, gabarit, accueil, pastilles,
étiquettes, tests). Son gabarit est copié tel quel dans `src/gabarit-exercice-interactif.html` (fichier identique,
vérifié octet par octet) ; le générateur n'en remplace que les entrées réservées au sujet, chaque remplacement étant
vérifié : `CONSEIL_MIN` (lue dans `window.__CONSEIL_MIN__`), `DECOR` et `DR_NAMES` (vides : les tracés se font dans
l'atelier), le texte de la fenêtre « Imprimer les DR », le libellé « Diagramme validé » (devenu « Réponses
validées ») et le décompte « n case(s) juste(s) » (devenu « n réponse(s) juste(s) », qui convient aux étiquettes comme
aux constructions).

**Accueil** (`index.html`), sur le modèle de Chaîne fonctionnelle : en-tête et montage d'illustration (quatre feuilles
corrigées : ellipsographe, embiellage, pompe, chargeur), puis les rubriques **Les cours** (Cours 1, pastille verte
Analytique ; Cours 2, pastille bleue Graphique), **L'atelier de construction**, **Activités de cinématique
analytique** (une carte « En cours d'édition »), **Activités de résolution graphique** (sept cartes) et **Études de
cas** (une carte « En cours d'édition »). La logique de numérotation reste celle des dépôts précédents : le premier
chiffre d'une activité donne sa partie (1 analytique, 2 graphique). Toutes les cartes ont la même taille, une
vignette photographiée dans la page (`outils/captures.js`), 3 à 5 mots-clés et un bouton (test navigateur).

## Le cours scindé : partie analytique, partie résolution graphique

- **Cours 1 — Cinématique analytique** (`?ex=cours-cinematique-analytique`) : chapitre « Cinématique », parties A
  (généralités), B.I, B.II, B.IV (cinématique du solide : translation, rotation, composition) et C (cinématique du
  point). Neuf sections, figures redessinées en SVG et animées : axe du temps ; train et voyageur, vus depuis la voie
  ou depuis le wagon, avec la trajectoire du voyageur dans chaque repère et V(2/0) = V(2/1) + V(1/0) ; roue de vélo
  qui roule sans glisser (cycloïde du point de la jante, droites du moyeu et du guidon) ; point M sur sa trajectoire
  avec ses vecteurs position, vitesse et accélération ; quatre mouvements plans animés et un jeu de classement ;
  répartition des vitesses sur une pale d'hélice (N et position réglables, 104,7 m/s au bout pour 1 000 tr/min, comme
  dans le chapitre) ; simulateur du mouvement rectiligne uniformément varié (x(t), v(t), a(t), trois situations
  types) ; rotation du point avec V, Γn, Γt et Γ. Cartes « L'essentiel à retenir », quiz de 10 questions.
- **Cours 2 — Cinématique graphique** (`?ex=cours-cinematique-graphique`) : séquence, parties 1 à 7, et partie B.III
  du chapitre (mouvement plan, équiprojectivité, CIR), qui y est regroupée. Dix sections : carte des relations entre
  accélération, effort, vitesse, géométrie et matériaux ; la pièce de la séquence animée dans les cinq mouvements,
  avec les trajectoires et vitesses de trois de ses points, et les deux jeux qui remplacent le tableau à compléter
  (nature des trajectoires, direction des vitesses) ; vecteur vitesse et convertisseur d'échelle ; mécanisme plan,
  translation, rotation, solide indéformable ; **équiprojectivité** (7 étapes), **CIR** (5 étapes) et
  **composition des vitesses** (5 étapes) construits pas à pas sur la feuille de l'atelier ; bielle-manivelle
  vivante (angle réglable : vitesses de A et B, CIR, champ des vitesses, points morts, translation instantanée) ;
  tableau « Choisir sa méthode » renvoyant aux activités ; quiz de 10 questions.
- Les blancs de la séquence (polycopié à compléter) sont complétés dans le cours : les trois types de mouvement, la
  définition des vecteurs équipollents, les propriétés de la translation, ‖V‖ = ω × R et ses unités, les définitions
  encadrées de l'équiprojectivité et du CIR, les trois mouvements de la composition et sa relation.

## L'atelier de construction graphique

Environnement de construction commun aux activités, au cours 2 (démonstrations) et à l'atelier libre
(`src/atelier/atelier.js`, sans dépendance) :
- **Feuille en millimètres**, à l'échelle du document réponse ; échelle des vitesses écrite sur la feuille ; zoom
  (boutons, Ctrl + molette, deux doigts), déplacement, quadrillage, plein écran (la feuille et les questions de la
  partie), impression du **document réponse vierge à taille réelle** (SVG en mm, pour travailler aussi sur papier).
- **Outils du papier** : point, droite, segment, vecteur ; perpendiculaire, parallèle, projeté orthogonal ; cercle et
  compas (report de longueur) ; mesure (distance, angle) ; texte ; gomme ; annuler/rétablir ; quatre couleurs.
  Accrochage aux points de la figure, aux extrémités, aux intersections et sur les tracés. Un vecteur se nomme
  (suggestions) et sa longueur se règle au millimètre.
- **Clavier** : raccourcis des outils, flèches pour déplacer un curseur (Maj : pas fin), Entrée pour poser un point,
  Échap pour annuler l'étape, Suppr, Ctrl+Z / Ctrl+Y.
- **Vérification** : chaque élément qu'une question demande de construire est décrit (vecteur, support, point,
  trajectoire) et comparé en continu aux tracés : vecteur d'origine sur le point à 1,5 mm près, direction à 3°,
  longueur à 6 % (8 % pour les vitesses obtenues après plusieurs constructions) ; support passant par le point à
  3° près ; CIR à 4 % de sa distance aux points qui le construisent (2 mm au moins). Un tracé nommé ne compte que pour
  l'élément du même nom. Sous l'énoncé, chaque élément affiche « à construire » ou « tracé repéré » (sans dire s'il est
  juste). Le verdict est écrit dans le champ masqué que lit le moteur du gabarit (mécanisme « fast-q » : un point par
  élément) ; le bouton « Valider ma construction » signale ce qui manque avant de valider. Après correction, la
  construction attendue (tracés d'aide en orange, résultat en rouge) se superpose à la feuille, et chaque élément faux
  dit pourquoi (direction, longueur, distance du point, non tracé). En examen, rien n'est corrigé avant la remise.

## Les activités : un exercice = une activité unique

Les sept exercices de la séquence deviennent les activités 2.1 à 2.7, chacune avec ses deux modes, son chronomètre,
sa note pondérée et son récapitulatif. Questions et numérotation (Q1, Q2…) sont celles de la séquence ; une question
d'origine qui demande plusieurs choses est découpée en a), b)… Trois sortes de réponses : **constructions** vérifiées
par l'atelier, **valeurs** avec unité (moteur du gabarit : la valeur juste sans unité vaut la moitié des points ;
tolérances de 1 à 2 % pour un calcul, 5 à 8 % pour une lecture sur le tracé), **étiquettes** à glisser (nature des
mouvements, comparaison de vitesses, conclusion : moteur d'étiquettes de Chaîne fonctionnelle). Les relations de
composition se saisissent (moteur « chasles » du gabarit, qui accepte toute relation juste ; bouton « ∈ »). Un dossier
technique DT1 (méthodes graphiques et mode d'emploi de l'atelier) et, quand la séquence fournit une photo, un dossier
de présentation DP1 accompagnent chaque activité. Les valeurs attendues sont calculées par les méthodes du cours
(`src/geometrie.py`) et vérifiées par les tests (équiprojectivité, CIR, composition).

| Activité | Feuille | Résultats principaux |
|---|---|---|
| 2.1 Arbre de transmission | redessinée, 1:1 | V(A) = V(B) = 5,24 m/s ; V(C) = 2,62 m/s ; projections égales |
| 2.2 Embiellage de moto | redessinée, 1:2 | V(B) = 30,6 m/s ; V(C∈2/0) ≈ 31,3 m/s ; V(D∈3/0) ≈ 16,4 m/s |
| 2.3 Pompe à pétrole | redessinée, 1:40 | V(B) = 0,895 m/s ; V(C) ≈ 0,54 m/s ; V(E) ≈ 0,79 m/s ; q ≈ 6,2 L/s |
| 2.4 Ellipsographe | redessinée | I2/0 ; V(M) ≈ 5,9 cm/s ; V(B) ≈ 2,5 cm/s |
| 2.5 Portail à vis | redessinée, 1:10 | V(C) = 0,06 m/s ; V(B) ≈ 0,079 m/s ; V(M) ≈ 0,24 m/s ; ω ≈ 0,159 rad/s ; ≈ 308 tours du moteur |
| 2.6 Chargeur Bobcat S185 | fond d'origine calé | V(C∈5/4) = 0,181 m/s ; V(C∈5/0) ≈ 0,20 m/s ; V(H∈1/0) ≈ 0,76 m/s ≤ 1,2 m/s |
| 2.7 Suspension du VTT | trois fonds d'origine | V(F) ≈ 16,5 m/s ; V(D) ≈ 19,6 m/s (puis 20 donnés) ; V(C) ≈ 14,2 m/s (puis 15 donnés) ; V(C∈S4/S5) ≈ 10,6 m/s ≤ 15 m/s |

**Feuilles** : les schémas cinématiques (arbre, embiellage, pompe, ellipsographe, portail) sont redessinés en SVG avec
la géométrie relevée sur les pages rendues à 300 dpi (`src/mecanismes.py`), ce qui donne des tracés nets à tout zoom et
des réponses exactes ; les dessins d'ensemble du chargeur et du VTT restent en fond (niveaux de gris), leurs points
étant calés au pixel. Le dessin du VTT, tourné d'un quart de tour sur les pages, est remis à l'endroit ; la pompe
aussi (balancier horizontal, câble vertical). La feuille du chargeur reçoit une marge au-dessus du dessin, celle du VTT
une marge à gauche, pour que les vecteurs longs (V(H∈1/0), V(G∈S1/S0)) y tiennent ; les cadres « Résultat » et
« Question 8 » des documents réponses sont blanchis, la question y répondant dans la page.

## Corrections et décisions

- **Arbre de transmission** : l'énoncé place « les dentures A, B et C sur la roue (4) et la denture D sur la roue (1) »,
  alors que la figure et les questions mettent A et B sur la roue (4) et C sur la roue (1), sans point D : l'énoncé
  suit la figure. « Ø1 = 50 mm et Ø2 = 100 mm » devient Ø1 (roue 1) et Ø4 (roue 4). Point B relevé à −60°.
- **Embiellage** : le schéma n'a pas d'échelle de longueur ; il est redessiné à l'échelle 1:2 (AB = 39 mm), avec des
  bielles de 133 mm (rapport bielle/manivelle de 3,41, relevé sur le schéma), cylindres en V à 90°, manivelle à 65° de
  l'axe du cylindre de droite. La cote « 83 mm » du schéma, que n'utilise aucune question, n'est pas reprise.
- **Pompe** : A, D et l'angle de la manivelle relevés sur la figure 2 (échelle 1:40) ; B et C calculés avec les
  longueurs données (AB, BC, CD) ; E est le point où le câble, vertical, quitte la tête (DE horizontal). Sens de
  rotation de la manivelle lu sur la figure (horaire). La question 7 (« compléter q = V × … ») devient une question à
  étiquettes suivie du calcul du débit (m³/s ou L/s acceptés).
- **Ellipsographe** : AB = BM = 52 mm, barre à 50° (relevés sur le schéma, qui n'a pas d'échelle de longueur).
- **Portail à vis** : cotes relevées à l'échelle 1:10 ; le pignon de 90 dents est sur l'arbre du moteur et la roue de
  270 dents sur la vis (lu sur le schéma) : le moteur fait trois tours par tour de vis. À la fermeture, l'écrou se
  rapproche du moteur. La position fermée suit la droite « position portail fermé ».
- **Chargeur** : le cadre du document réponse est titré « Question 8 » alors qu'il répond à la question 10 : la
  page pose la question 10. « Quel est la nature » devient « Quelle est la nature ».
- **VTT** : les renvois « DR page 21, 23, 24 » deviennent les documents réponses 1, 2 et 3 de l'activité, une partie
  chacun ; les « échelles de tracé conseillées » deviennent les échelles des feuilles (1 cm pour 6, 5 et 3 m/s), pour
  que les tracés soient vérifiables. Les valeurs imposées (20 m/s, puis 15 m/s) sont rappelées en tête des parties 2
  et 3, comme dans la séquence ; le calcul donne 19,6 et 14,2 m/s.
- **Chapitre** : « Si v = a, le mouvement se fait à vitesses constantes » devient « si v est constante, le mouvement
  se fait à vitesse constante » ; « la position du point P » (dans la partie sur le point M) devient M ;
  ω = θ / t est précisé (rotation uniforme, θ0 = 0) à côté de ω = dθ/dt ; « Mouvement déccéléré » est corrigé.
- **Séquence** : « le référentiel choisit », « peut-être différent », « mouvement verticale de va et vient »,
  « à un diamètre », « Echelle » sont corrigés ; le CIR est présenté en général (I1/0) puis sur l'exemple (I2/0).
- En-têtes « Nom / Prénom / Date », logo de l'établissement et pieds de page des documents d'origine ne sont pas
  repris (le champ « Nom et prénom » du gabarit les remplace) ; aucune mention de diplôme ou d'épreuve (test).

## Points signalés sans modification

- **À vérifier** : les photos de l'arbre de transmission et du VTT, et les dessins du chargeur Bobcat et de la
  suspension, viennent de la séquence fournie (documentation de constructeurs) ; leur publication suppose d'en avoir
  le droit.
- Les activités de cinématique analytique et les études de cas sont annoncées « En cours d'édition » : les documents
  fournis n'en contiennent pas. Le générateur les accueille déjà (activité sans feuille, `"partie": "analytique"`).
- Poids : `index.html` 2,1 Mio (1,5 Mio d'images).

## Vérifications effectuées

- `node --test tests/correction.test.js` : 8 tests — gabarit identique à celui du dépôt Chaîne fonctionnelle
  (empreinte SHA-256) ; configuration (7 activités, une feuille par partie, barème) ;
  chaque élément à construire a son champ, corrigé « juste » seulement ; éléments attendus dans leur feuille et partant
  d'un point de la figure ; cinématique des réponses (équiprojectivité de l'embiellage, CIR de l'ellipsographe,
  composition du VTT) ; valeurs avec et sans unité, hors tolérance, autres unités acceptées ; étiquettes (la bonne
  seule acceptée de sa liste) ; relations de composition justes et fausses.
- `tests/navigateur.test.js` (Playwright, Chromium) : 15 parcours, tous réussis — accueil (12 cartes illustrées de
  même taille, rubriques, téléphone, aucune mention de diplôme) ; adresse inconnue ; cours 1 (train, vélo, vecteurs,
  hélice, MRUV, rotation, jeu, quiz 10/10) ; cours 2 (trois démonstrations pas à pas, bielle-manivelle, jeux, échelle,
  quiz) ; atelier libre (accrochage, perpendiculaire, parallèle, projeté, compas, mesure, texte, gomme,
  annuler/rétablir, clavier, zoom, plein écran, document vierge) ; arbre de transmission construit à l'outil en
  entraînement jusqu'à 20/20 ; ellipsographe en examen (CIR construit à l'équerre, rien de corrigé avant la remise,
  corrections superposées ensuite) ; pour chacune des sept activités, solution complète → 20/20 ; téléphone et
  impression.
- Aucune erreur JavaScript dans aucun parcours.
