# Documentation - spectroPy_render - https://nid.morgandemus.fr/

## Table des matières
1. Introduction
2. GNU/Linux & Windows & MacOS
3. Paramètres de génération
4. Guide d'utilisation 
5. CLI
6. References techniques

---

## Introduction

Cet outil génère des spectrogrammes haute résolution avec une interface détaillée afin de paramétrer à votre guise.
Il utilise FFmpeg (filtre showspectrumpic) pour l'export final et librosa/matplotlib pour l'apercu interactif.

### Différences entre prévisualisation et export
- **Aperçu interactif** : Calcul rapide (60 secondes par défaut), navigation sur le spectrogramme, modification temps reel du paramétrage.
- **Export FFmpeg** : Qualité de publication, audio complet, tous les parametres appliqués.

---

## GNU/Linux & Windows & MacOS

Initialement conçu et pensé sur système GNU/Linux (Debian), l'avantage du langage Python3 est de permettre une exécution multi-plateforme.
Il est donc très important de respecter les dépendances du programme afin de l'utiliser convenablement :

### Ce qu'il vous faut :
- **Python3** : https://www.python.org/downloads/
- **FFmpeg** : https://www.ffmpeg.org/
- **Commande PIP** : pip install PyQt6 matplotlib librosa sounddevice numpy scipy

(Note : Sur Linux il sera nécessaire d'ajouter libportaudio2 pour le son et les libxcb-* pour l'affichage, le script run.sh s'occupe de cela)

---

## Parametres de génération (par défaut)

### Taille (size)
**Format** : 1920x1080 (largeur x hauteur)

**Memento des résolutions** :
- Par défaut : 1920x1080
- Analyse fine : 3840x2160 (permet de distinguer les harmoniques fines et les micro-structures temporelles)
- Traitement rapide : 1280x720

---

### Mode d'affichage
**Options** : combined | separate

**combined** : Superpose tous les canaux audio (mono ou stereo) en un seul spectrogramme

**separate** : Affiche chaque canal sur une ligne distincte

---

### Palette de couleurs
**Options** : fiery | rainbow | intensity | magma | viridis | cool | plasma | green | blue

**Impact perceptuel** :
- **fiery** : Noir -> Rouge -> Jaune -> Blanc.
- **magma** : Noir -> Rouge -> Jaune -> Blanc.
- **viridis** : Violet -> Vert -> Jaune.
- **rainbow** : Arc-en-ciel.
- **intensity** : Noir -> Blanc.

**(dev) Table de correspondance FFmpeg -> Matplotlib** :
- fiery -> afmhot
- magma -> magma
- viridis -> viridis
- rainbow -> rainbow
- intensity -> gray

---

### Échelle d'intensité
**Options** : log | lin | sqrt | cbrt

**log** (decibels - RECOMMANDÉ) :
- Formule : dB = 20 x log10(amplitude)
- Plage dynamique : 120-150 dB typique

**lin** (lineaire) :
- Affiche l'amplitude brute (utile pour l'analyse de signaux synthétiques et la calibration)

**sqrt** (racine carrée) :
- Compression modérée de la dynamique (dans le cas de pics très élevés)

**cbrt** (racine cubique) :
- Compression forte de la dynamique (visualiser simultanement des sons très forts et très faibles)

---

### Échelle de fréquence
**Options** : log | lin

**log** :
- Axe Y en échelle logarithmique

**lin** (lineaire) :
- Axe Y en échelle lineaire

---

### Fenêtrage (FFT - Window Function)
**Options** : hann | blackman | hamming | rect | bartlett | flattop | welch | nuttall

**Concept** : Réduit les fuites spectrales (spectral leakage) lors de la transformée de Fourier.
(https://fr.wikipedia.org/wiki/Transformation_de_Fourier)

**hann** (RECOMMANDÉE) :
- Compromis optimal résolution/fuites
- Largeur de lobe principal : moyenne
- Attenuation des lobes secondaires : -31 dB

**blackman** :
- Meilleure atténuation des fuites (-58 dB)
- Pour isoler des notes pures, harmoniques très proches mais résolution frequentielle légèrement réduite

**hamming** :
- Similaire à Hann mais premier lobe secondaire plus bas

**rect** (rectangulaire) :
- Aucune fenetre (boite rectangulaire)
- Résolution maximale mais fuites importantes (à éviter sans maîtrise de l'intérêt)

**flattop** :
- Mesure d'amplitude très précise

**Parametres FFT avances** (codes en dur) :
- n_fft = 2048 : Taille de la FFT (résolution fréquentielle)
- hop_length = 512 : Chevauchement des fenêtres (résolution temporelle)
- Rapport : 75% de chevauchement (standard)

---

### Gain
**Format** : 1.0 a 100.0 (multiplicateur)

**Attention !** : Le gain n'amplifie pas le rapport signal/bruit, il amplifie tout (signal + bruit).

---

### Fréquence min/max (Hz)
**Format** : 0 (auto) ou valeur en Hz

**Fréquence min** :
- Exemple : 1000 Hz pour ignorer le vent, les infrasons, le bruit de fond basse fréquence
- Exemple : 500 Hz pour se concentrer sur les passereaux

**Frequence max** :
- Exemple : 12000 Hz pour la bande typique des passereaux (0.5-12 kHz)
- Exemple : 8000 Hz pour filtrer les ultrasons (chauves-souris, insectes)

**Bandes fréquentielles par espèces** : https://nid.morgandemus.fr/articles/ornitho_frequency_table.html

---

### Plage dynamique (dB)
**Format** : 10 a 200 dBFS

**dBFS** (decibels Full Scale) : 0 dBFS = niveau maximum numérique (saturation)

---

### Afficher la légende
**Options** : Oui | Non

**Oui** :
- Affiche les axes de temps (secondes) et fréquences (Hz)
- Affiche la barre de couleur avec échelle en dB

**Non** :
- Image sans annotations

---

## Guide d'utilisation

### Exemple d'utilisation basique

1. **Chargement** : Votre fichier audio (WAV, FLAC, MP3, OGG)
2. **Aperçu rapide** : Les 60 premieres secondes s'affichent (paramétrable suivant les ressources de votre ordinateur)
3. **Réglage des paramètres** :
   - Palette : fiery ou magma
   - Échelle fréquence : log
   - Échelle intensité : log
   - Plage dynamique : 120-150 dB
   - Fenêtrage : hann ou blackman
4. **Ecoute** : Cliquez sur Play pour écouter l'audio
5. **Export** : Cliquez sur "Generer l'image finale"

### Exemples par type d'analyse

#### Chants complexes (grives, merles, fauvettes)
- Taille : 1920x1080
- Palette : intensity
- Échelle fréquence : log
- Plage dynamique : 120-150 dB
- Fenêtrage : hann
- Fréquence min : 500 Hz
- Fréquence max : 12000 Hz

#### Chants aigus (roitelets, mesanges)
- Échelle fréquence : log
- Fréquence min : 2000 Hz
- Fréquence max : 12000 Hz
- Palette : intensity (meilleur contraste hautes fréquences)

#### Chants graves (butor, hiboux, poules d'eau)
- Échelle fréquence : log
- Fréquence min : 50 Hz
- Fréquence max : 4000 Hz
- Plage dynamique : 150 dB (sons souvent faibles)

#### Paysages sonores (écoacoustique)
- Mode : separate (si stereo)
- Palette : magma (perceptuellement uniforme)
- Plage dynamique : 150-180 dB
- Échelle intensité : log
- Taille : 3840x2160

#### Harmoniques fines (analyse spectrale)
- Fenêtrage : blackman (meilleure separation)
- Taille : 3840x2160
- Échelle fréquence : lin (si harmoniques equidistantes)
- Palette : intensity (niveaux de gris precis)

### Pièges a éviter

1. **Plage dynamique trop faible** (< 80 dB) : Perte d'informations sur les chants faibles
2. **Échelle lineaire en fréquence** : Impossible de voir simultanement graves et aigus
3. **Fenêtrage rectangulaire** : Fuites spectrales importantes, artefacts visuels
4. **Gain excessif** (> 10) : Saturation du spectrogramme, perte de détails
5. **Pas de legende** : Image purement esthétique

---

## Automatisation en ligne de commande (CLI) (pour développeur)

### Syntaxe de base

python spectroPy_render.py --input fichier.wav --output sortie.png [OPTIONS]

également possible avec :

python spectroPy_render.py -i fichier.wav -o sortie.png [OPTIONS]

### Exemples

#### Exemple 1 : Génération rapide (parametres par defaut)
python spectroPy_render.py -i oiseau.wav -o spectrogramme.png

#### Exemple 2 : Configuration bioacoustique optimale
python spectroPy_render.py -i chant_merle.wav -o merle_spectrogram.png --size 1920x1080 --color intensity --scale log --fscale log --win-func hann --drange 150 --start 500 --stop 12000 --legend

#### Exemple 3 : Analyse des hautes fréquences
python spectroPy_render.py -i roitelet.wav -o roitelet_HF.png --color viridis --fscale log --start 4000 --stop 12000 --drange 120

#### Exemple 4 : Écoacoustique
python spectroPy_render.py -i paysage_sonore.wav -o paysage_4K.png --size 3840x2160 --mode separate --color magma --drange 180 --win-func blackman

#### Exemple 5 : Traitement par lots (bash)
#!/bin/bash
# Script de generation en masse

for fichier in ./enregistrements/*.wav; do
    nom_base=$(basename "$fichier" .wav)
    python spectroPy_render.py -i "$fichier" -o "./spectrogrammes/${nom_base}.png" --color intensity --fscale log --drange 150 --legend
    echo "Creation : ${nom_base}.png"
done

#### Exemple 6 : Pipeline complet avec FFmpeg natif
ffmpeg -i entree.wav -af "highpass=f=500, lowpass=f=12000" -f wav - | ffmpeg -i - -lavfi "showspectrumpic=size=1920x1080:color=fiery:scale=log:fscale=log:drange=150" -y sortie.png

### Toutes les options CLI disponibles

Options obligatoires :
  -i, --input TEXT          Fichier audio d'entrée (WAV, FLAC, MP3, OGG)
  -o, --output TEXT         Fichier image de sortie (PNG)

Options de taille :
  --size TEXT               Résolution (défaut: 1920x1080)
                            Ex: 1280x720, 3840x2160

Options d'affichage :
  --mode TEXT               combined | separate (defaut: combined)
  --color TEXT              fiery | rainbow | intensity | magma | viridis | cool | plasma | green | blue (defaut: fiery)

Options d'échelle :
  --scale TEXT              log | lin | sqrt | cbrt (defaut: log)
  --fscale TEXT             log | lin (defaut: log)

Options de traitement :
  --win-func TEXT           hann | blackman | hamming | rect | bartlett | flattop | welch | nuttall (defaut: hann)
  --gain FLOAT              Amplification 0.1-100.0 (defaut: 1.0)

Options de fréquence :
  --start INTEGER           Fréquence min en Hz, 0=auto (defaut: 0)
  --stop INTEGER            Fréquence max en Hz, 0=auto (defaut: 0)

Options de qualité :
  --drange INTEGER          Plage dynamique 10-200 dB (defaut: 120)

Options d'annotation :
  --legend                  Afficher la légende (defaut: active)
  --no-legend               Masquer la légende

Aide :
  --help                    Afficher cette aide et quitter
  
---

## Réferences techniques

### Documentation officielle

- FFmpeg showspectrumpic : https://ffmpeg.org/ffmpeg-filters.html#showspectrumpic
- CloudACM - Tutoriel FFmpeg : https://www.cloudacm.com/?p=3105
- librosa : https://librosa.org/doc/latest/
- Matplotlib : https://matplotlib.org/stable/contents.html

### Ressources bioacoustiques

- Cornell Lab of Ornithology : https://www.birds.cornell.edu/
- Xeno-canto (base de donnees chants d'oiseaux) : https://xeno-canto.org/

### Caractéristiques techniques supplémentaires

**Format d'entrée** :
- WAV (PCM, float32)
- FLAC (lossless)
- MP3 (MPEG-1/2 Layer 3)
- OGG Vorbis
- AIFF
- M4A/AAC

**Specifications de sortie** :
- Format : PNG (24-bit RGB)
- Resolution max : Limitée par la memoire RAM
- Espace colorimétrique : sRGB
