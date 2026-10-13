#!/usr/bin/env bash
# Prépare les images intégrées dans la page (poppler-utils et ImageMagick 6 requis).
#   1. extrait, de la séquence « Cinématique graphique » (PDF fourni, non conservé dans le dépôt), les fonds des
#      documents réponses qui ne sont pas redessinés (chargeur Bobcat, suspension du VTT) et les photos de
#      présentation, dans src/images/originaux/ (rendu à 300 dpi : 1 mm = 11,811 px) ; de la séquence « Cinématique
#      analytique », les dessins et la photo des activités analytiques (imprimante 3D, vanne d'air, AGV, transmission) ;
#   2. les réduit et les quantifie dans src/images/ (PNG 8 bits ou JPEG), intégrés en data URI par src/generer.py ;
#   3. compose les vignettes des cartes de l'accueil : l'image de chaque activité (photo, ou dessin d'origine quand la
#      séquence n'a pas de photo), et le montage d'illustration de l'accueil.
# Les coordonnées des points relevées sur ces fonds sont dans src/mecanismes.py (pixels des pages à 300 dpi).
# Usage : bash outils/preparer-images.sh [Sequence-Cinematique-Graphique.pdf|-] [Sequence-Cinematique-Analytique.pdf]
#         (« - » ou rien à la place d'un PDF : ses images ne sont pas extraites ; sans argument, seule l'étape 2 est
#         refaite, à partir de src/images/originaux)
set -euo pipefail
cd "$(dirname "$0")/.."
ORIG=src/images/originaux
OUT=src/images
mkdir -p "$ORIG" "$OUT"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
if [ $# -ge 1 ] && [ "$1" != "-" ]; then
  for p in 5 7 8 11 13 17 18 19 21 22; do
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
  # dessins d'origine des exercices sans photo (images de leurs cartes et de leur page d'accueil)
  convert "$(page 11)" -crop 1500x1460+930+1750 +repage -fuzz 5% -trim +repage "$ORIG/dessin-ellipsographe.png"
  convert "$(page 13)" -crop 2090x2160+200+370 +repage -fill white -draw "rectangle 950,10 1900,210" -fuzz 5% -trim +repage \
    "$ORIG/dessin-portail.png"
  convert "$(page 17)" -crop 2040x1780+230+1550 +repage -fuzz 5% -trim +repage "$ORIG/dessin-bobcat.png"
fi
if [ $# -ge 2 ]; then
  for p in 11 12 13 16; do
    pdftoppm -r 300 -png -f "$p" -l "$p" "$2" "$TMP/a$p"
  done
  pagea() { ls "$TMP"/a"$1"-*.png; }
  # schéma de l'axe x de l'imprimante, dessin et schéma de la vanne, photo de l'AGV (sans la ligne du logo placée
  # sous la photo), transmission par courroie
  convert "$(pagea 11)" -crop 960x560+1430+320 +repage "$ORIG/photo-imprimante.png"
  convert "$(pagea 12)" -crop 980x1160+1410+395 +repage "$ORIG/photo-vanne.png"
  convert "$(pagea 13)" -crop 1150x350+1160+455 +repage "$ORIG/photo-agv.png"
  convert "$(pagea 16)" -crop 1020x1000+1255+2220 +repage "$ORIG/photo-transmission.png"
fi

# fonds : niveaux de gris, 16 teintes (traits fins d'un dessin technique)
for f in "$ORIG"/fond-*.png; do
  convert "$f" -colorspace Gray -resize 50% -colors 16 -strip "PNG8:$OUT/$(basename "$f")"
done
# dessins de présentation en niveaux de gris, photos en JPEG
for b in photo-embiellage photo-pompe photo-vtt-suspension photo-imprimante photo-vanne photo-transmission \
         dessin-ellipsographe dessin-portail dessin-bobcat; do
  [ -e "$ORIG/$b.png" ] || continue
  trait=""
  case "$b" in dessin-*) trait="-morphology Erode Disk:1.5" ;; esac  # traits fins des dessins, épaissis avant réduction
  convert "$ORIG/$b.png" -colorspace Gray $trait -resize '900x900>' -colors 32 -strip "PNG8:$OUT/$b.png"
done
for b in photo-arbre photo-vtt photo-agv; do
  [ -e "$ORIG/$b.png" ] || continue
  convert "$ORIG/$b.png" -resize '720x720>' -quality 80 -strip "$OUT/$b.jpg"
done
# vignettes des cartes de l'accueil (480 × 270) : cours, atelier et rubriques à venir, à partir des captures
# d'outils/captures.js ; activités, à partir de leur image (photo ou dessin d'origine), entière, sur fond blanc
for f in "$ORIG"/carte-*.png; do
  [ -e "$f" ] || continue
  convert "$f" -resize '480x270^' -gravity center -extent 480x270 -colors 128 -strip "PNG8:$OUT/$(basename "$f")"
done
carte() {  # carte <activité> <image d'origine> ; les traits fins des dessins sont épaissis avant réduction
  [ -e "$ORIG/$2.png" ] || return 0
  local trait=""
  case "$2" in dessin-*) trait="-morphology Erode Disk:2.5" ;; esac
  convert "$ORIG/$2.png" $trait -resize '452x246' -background white -gravity center -extent 480x270 -colors 128 -strip \
    "PNG8:$OUT/carte-$1.png"
}
carte arbre-transmission photo-arbre; carte embiellage-moto photo-embiellage; carte pompe-petrole photo-pompe
carte ellipsographe dessin-ellipsographe; carte portail-vis dessin-portail; carte chargeur-bobcat dessin-bobcat
carte suspension-vtt photo-vtt; carte imprimante-3d photo-imprimante; carte vanne-admission photo-vanne
carte agv photo-agv; carte moteur-electrique photo-transmission
# montage d'illustration de l'accueil : six systèmes étudiés
if [ -e "$ORIG/photo-agv.png" ]; then
  montage "$ORIG"/photo-agv.png "$ORIG"/photo-imprimante.png "$ORIG"/photo-pompe.png "$ORIG"/photo-vtt.png \
    "$ORIG"/photo-vanne.png "$ORIG"/dessin-bobcat.png -tile 3x2 -geometry 300x190+8+6 -background white miff:- |
    convert - -trim -bordercolor white -border 6 -colors 160 -strip "PNG8:$OUT/accueil.png"
fi
ls -l "$OUT" | grep -E "fond-|photo-|dessin-|carte-|accueil"
