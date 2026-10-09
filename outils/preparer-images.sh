#!/usr/bin/env bash
# Prépare les images intégrées dans la page (poppler-utils et ImageMagick 6 requis).
#   1. extrait, de la séquence « Cinématique graphique » (PDF fourni, non conservé dans le dépôt), les fonds des
#      documents réponses qui ne sont pas redessinés (chargeur Bobcat, suspension du VTT) et les photos de
#      présentation, dans src/images/originaux/ (rendu à 300 dpi : 1 mm = 11,811 px) ;
#   2. les réduit et les quantifie dans src/images/ (PNG 8 bits ou JPEG), intégrés en data URI par src/generer.py.
# Les coordonnées des points relevées sur ces fonds sont dans src/mecanismes.py (pixels des pages à 300 dpi).
# Usage : bash outils/preparer-images.sh chemin/vers/Sequence-Cinematique-Graphique.pdf
#         (sans argument : seule l'étape 2 est refaite, à partir de src/images/originaux)
set -euo pipefail
cd "$(dirname "$0")/.."
ORIG=src/images/originaux
OUT=src/images
mkdir -p "$ORIG" "$OUT"

if [ $# -ge 1 ]; then
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  for p in 5 7 8 17 18 19 21 22; do
    pdftoppm -r 300 -png -f "$p" -l "$p" "$1" "$TMP/p$p"
  done
  page() { ls "$TMP"/p"$1"-*.png; }
  # fonds de documents réponses : recadrés ; le cadre « Résultat » et les mentions déjà données par la page
  # (échelle, cadre « Question 8 ») sont blanchis ; le VTT est remis à l'endroit (dessin tourné d'un quart de tour)
  convert "$(page 17)" -crop 2030x3000+230+280 +repage -fill white \
    -draw "rectangle 1130,0 2030,330" -draw "rectangle 0,0 900,110" "$ORIG/fond-bobcat.png"
  convert "$(page 19)" -crop 1830x2680+380+330 +repage -fill white -draw "rectangle 0,2040 220,2680" \
    -rotate 90 "$ORIG/fond-vtt-1.png"
  convert "$(page 21)" -crop 1670x2230+480+420 +repage -fill white -draw "rectangle 0,1880 110,2230" \
    -rotate 90 "$ORIG/fond-vtt-2.png"
  convert "$(page 22)" -crop 1670x2260+480+700 +repage -fill white -draw "rectangle 0,1670 120,2260" \
    -rotate 90 "$ORIG/fond-vtt-3.png"
  # photos et dessins de présentation
  convert "$(page 5)" -crop 730x490+1600+390 +repage "$ORIG/photo-arbre.png"
  convert "$(page 7)" -crop 640x1080+1680+290 +repage "$ORIG/photo-embiellage.png"
  convert "$(page 8)" -crop 1310x1050+1005+365 +repage "$ORIG/photo-pompe.png"
  convert "$(page 18)" -crop 1000x700+235+655 +repage "$ORIG/photo-vtt.png"
  convert "$(page 18)" -crop 1010x780+1250+640 +repage "$ORIG/photo-vtt-suspension.png"
fi

# fonds : niveaux de gris, 16 teintes (traits fins d'un dessin technique)
for f in "$ORIG"/fond-*.png; do
  convert "$f" -colorspace Gray -resize 50% -colors 16 -strip "PNG8:$OUT/$(basename "$f")"
done
# dessins de présentation en niveaux de gris, photos en JPEG
for b in photo-embiellage photo-pompe photo-vtt-suspension; do
  convert "$ORIG/$b.png" -colorspace Gray -resize '900x900>' -colors 32 -strip "PNG8:$OUT/$b.png"
done
for b in photo-arbre photo-vtt; do
  convert "$ORIG/$b.png" -resize '720x720>' -quality 80 -strip "$OUT/$b.jpg"
done
ls -l "$OUT" | grep -E "fond-|photo-"
