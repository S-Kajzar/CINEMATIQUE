# Cinématique : cours, atelier de construction et activités interactifs

Construction reprise du dépôt « Chaîne fonctionnelle » (lui-même issu du dépôt « Résistance des matériaux ») : une
page autonome (un seul fichier HTML, aucune dépendance externe, utilisable hors ligne), publiée par GitHub Pages depuis
`index.html`. Le cours d'origine est scindé en une **partie analytique** et une **partie résolution graphique** ;
chaque exercice de la séquence graphique devient une **activité unique**, faite dans un **atelier de construction**
qui vérifie les tracés. L'accueil mène à :

| Adresse | Contenu |
|---|---|
| `index.html` | accueil, en cartes illustrées à mots-clés : les cours (pastilles Analytique / Graphique), l'atelier de construction, les activités de cinématique analytique (« En cours d'édition »), les activités de résolution graphique, les études de cas (« En cours d'édition ») |
| `?ex=cours-cinematique-analytique` | Cours 1 — Cinématique analytique : référentiel, train et voyageur animés, trajectoires (roue de vélo), vecteurs position, vitesse et accélération, mouvements plans, rotation et répartition des vitesses, composition des mouvements, mouvement rectiligne uniforme et uniformément varié, rotation du point (V, Γn, Γt), jeu, quiz |
| `?ex=cours-cinematique-graphique` | Cours 2 — Cinématique graphique : mouvements et trajectoires (pièce animée, deux jeux), vecteur vitesse et échelle, mécanisme plan, équiprojectivité, CIR et composition des vitesses construits pas à pas, bielle-manivelle vivante, choix de la méthode, quiz |
| `?ex=atelier-libre` | atelier de construction sur une feuille quadrillée A4, sans correction |
| `?ex=arbre-transmission` | Activité 2.1 — Arbre de transmission : rotation, V = R·ω, découverte de l'équiprojectivité |
| `?ex=embiellage-moto` | Activité 2.2 — Embiellage de moto (moteur en V) : équiprojectivité |
| `?ex=pompe-petrole` | Activité 2.3 — Pompe à pétrole brut : équiprojectivité, répartition des vitesses, débit |
| `?ex=ellipsographe` | Activité 2.4 — Ellipsographe : translations, CIR |
| `?ex=portail-vis` | Activité 2.5 — Portail à vis : CIR, vitesse angulaire, position fermée, tours du moteur |
| `?ex=chargeur-bobcat` | Activité 2.6 — Chargeur Bobcat S185 : CIR, composition des vitesses, équiprojectivité, condition de sécurité |
| `?ex=suspension-vtt` | Activité 2.7 — Suspension du VTT Vario Bomba (trois documents réponses) : CIR, équiprojectivité, composition |

Chaque activité propose le mode entraînement ou le mode examen, avec sa note pondérée par la durée de ses parties.
Corrections apportées aux contenus d'origine et décisions : [`NOTE-DE-LIVRAISON.md`](NOTE-DE-LIVRAISON.md).

## L'atelier de construction

Chaque partie d'une activité a sa **feuille** (document réponse, en millimètres, à l'échelle de l'énoncé), collée en
haut de l'écran à côté des questions. Outils du papier : règle (**droite**, **segment**), équerre
(**perpendiculaire**, **parallèle**, **projeté** orthogonal), **compas** (cercle, report de longueur), **vecteur**
(nommé, longueur réglable au millimètre), **mesure** (distance et angle), **texte**, **gomme** ; accrochage aux points,
extrémités et intersections ; annuler/rétablir, zoom, quadrillage, plein écran (feuille et questions), clavier
(flèches et Entrée), impression du document réponse vierge à taille réelle.

Les éléments qu'une question demande de construire (un vecteur, un support, un point comme un CIR, une trajectoire)
sont vérifiés en continu : l'atelier écrit « juste », « faux » ou rien dans le champ masqué que lit le moteur du
gabarit, si bien que validation, modes, notes, récapitulatif et impression restent ceux du gabarit. Une fois la
question corrigée, sa construction attendue se superpose en rouge à la feuille.

## Ajouter une activité

Décrire le mécanisme dans `src/mecanismes.py` (une `Feuille` : figure, points nommés, axes ; vitesses attendues par les
fonctions de `src/geometrie.py`), puis l'activité dans `src/activites.py` (parties, questions `Q`, `ETQ` et `TRACE`,
éléments attendus `IT_VE`, `IT_DIR`, `IT_PT`, `IT_CI` et leurs corrections), et l'ajouter à `ACTIVITES`. Une activité
`"partie": "analytique"`, sans feuille (`meca`), se range dans la rubrique analytique et remplace la carte « En cours
d'édition ». La carte apparaît d'elle-même sur l'accueil ; sa vignette vient de `outils/captures.js`.

## Régénérer la page

La page est produite par un script, à partir du gabarit (`src/gabarit-exercice-interactif.html`, copie conforme de
celui du dépôt Chaîne fonctionnelle, recopié sans modification de son style ni de ses moteurs) et du contenu décrit
dans `src/`.

```sh
bash outils/preparer-images.sh Sequence-Cinematique-Graphique.pdf  # seulement si les fonds ou photos changent (poppler, ImageMagick 6)
python3 src/generer.py                                              # écrit index.html
NODE_PATH=$(npm root -g) node outils/captures.js                   # vignettes de l'accueil, puis :
bash outils/preparer-images.sh && python3 src/generer.py
```

## Tester

```sh
node --test tests/correction.test.js                          # moteur de correction, éléments attendus, cinématique des réponses
NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js # accueil, cours, atelier, entraînement, examen, 7 activités à 20/20
```

## Organisation

| Chemin | Rôle |
|---|---|
| `src/gabarit-exercice-interactif.html` | gabarit de référence (charte, moteurs de correction et d'application), repris du dépôt Chaîne fonctionnelle |
| `src/generer.py` | accueil, aiguillage, rendu des questions et des parties, documents, assemblage |
| `src/atelier.py`, `src/atelier/` | atelier de construction : feuilles, barre d'outils, éléments attendus, corrections (Python) ; moteur (`atelier.js`), style (`atelier.css`, `figure.css`) |
| `src/geometrie.py` | géométrie plane et méthodes graphiques calculées (rotation, équiprojectivité, CIR, composition) |
| `src/mecanismes.py` | les sept mécanismes : feuilles redessinées ou fonds calés, échelles, vitesses attendues |
| `src/activites.py` | les sept activités : énoncés, données, questions, corrections détaillées |
| `src/cours_commun.py`, `src/cours_analytique.py`, `src/cours_graphique.py` | cours : éléments communs (quiz, jeux, cartes), cours 1 et cours 2 (contenu, figures SVG, simulateurs) |
| `src/medias.py` | images intégrées en data URI |
| `src/images/originaux/` | fonds de documents réponses et photos extraits de la séquence (300 dpi), captures des vignettes |
| `src/images/` | images réduites et quantifiées, intégrées dans la page |
| `outils/preparer-images.sh` | extraction depuis le PDF de la séquence, réduction, vignettes et montage d'accueil |
| `outils/captures.js` | vignettes photographiées dans la page (Playwright) |
| `tests/` | tests Node et Playwright |
| `.github/workflows/static.yml` | publication GitHub Pages (déclenchée sur la branche `main`) |
