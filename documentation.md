# Documentation - spectroPy_render - https://nid.morgandemus.fr/

## Table des matieres
1. Introduction
2. Parametres de generation
3. Guide d'utilisation professionnelle
4. Automatisation en ligne de commande (CLI)
5. References techniques

---

## Introduction

Cet outil genere des spectrogrammes haute resolution. Il utilise FFmpeg (filtre showspectrumpic) pour l'export final et librosa/matplotlib pour l'apercu interactif.

### Differences entre apercu et export
- **Apercu interactif** : Calcul rapide (60s max), navigation zoom/pan, modification temps reel
- **Export FFmpeg** : Qualite publication, audio complet, tous les parametres appliques

---

## Parametres de generation

### Taille (size)
**Format** : 1920x1080 (largeur x hauteur)

**Impact** :
- Resolution de l'image finale en pixels
- Une taille elevee permet de distinguer les harmoniques fines et les micro-structures temporelles
- Standard publication : 1920x1080 (Full HD) ou 3840x2160 (4K)

**Recommandations bioacoustiques** :
- Chants complexes : 1920x1080 minimum
- Analyse fine des harmoniques : 3840x2160
- Traitement par lots rapide : 1280x720

---

### Mode d'affichage
**Options** : combined | separate

**combined** : Superpose tous les canaux audio (mono ou stereo) en un seul spectrogramme
- Ideal pour : Analyse globale, publications, comparaison rapide
- Avantage : Visualisation compacte

**separate** : Affiche chaque canal sur une ligne distincte
- Ideal pour : Enregistrements stereo de paysages sonores, analyse comparative canal gauche/droite
- Avantage : Detection des differences spatiales (localisation des oiseaux)

---

### Palette de couleurs
**Options** : fiery | rainbow | intensity | magma | viridis | cool | plasma | green | blue

**Impact perceptuel** :
- **fiery** (recommandee) : Noir -> Rouge -> Jaune -> Blanc.
- **magma** : Noir -> Rouge -> Jaune -> Blanc.
- **viridis** : Violet -> Vert -> Jaune.
- **rainbow** : Arc-en-ciel complet.
- **intensity** : Noir -> Blanc.

**Correspondance FFmpeg -> Matplotlib** :
- fiery -> afmhot
- magma -> magma
- viridis -> viridis
- rainbow -> rainbow
- intensity -> gray

---

### Echelle d'intensite
**Options** : log | lin | sqrt | cbrt

**log** (decibels - RECOMMANDE) :
- Formule : dB = 20 x log10(amplitude)
- Avantage : Represente la perception auditive humaine et animale (echelle logarithmique)
- Plage dynamique : 120-150 dB typique
- Ideal pour : Chants d'oiseaux (large plage dynamique), ecoacoustique

**lin** (lineaire) :
- Affiche l'amplitude brute
- Utile pour : Analyse de signaux synthetiques, calibration

**sqrt** (racine carree) :
- Compression moderee de la dynamique
- Utile pour : Signaux avec pics tres eleves

**cbrt** (racine cubique) :
- Compression forte de la dynamique
- Utile pour : Visualiser simultanement sons tres forts et tres faibles

---

### Echelle de frequence
**Options** : log | lin

**log** (RECOMMANDE pour bioacoustique) :
- Axe Y en echelle logarithmique
- Avantage : Resolution adaptee a l'audition (octaves constantes)
- Visualise simultanement :
  - Basses frequences : Butor (50-200 Hz), Hibou (200-800 Hz)
  - Hautes frequences : Roitelet (8000-10000 Hz), Mesange (4000-8000 Hz)

**lin** (lineaire) :
- Axe Y en echelle lineaire
- Utile pour : Analyse de bandes frequentielles specifiques, comparaison d'harmoniques equidistantes
- Exemple : Etude des harmoniques d'un chant a 2000, 4000, 6000 Hz

---

### Fenetrage (FFT - Window Function)
**Options** : hann | blackman | hamming | rect | bartlett | flattop | welch | nuttall

**Concept** : Reduit les fuites spectrales (spectral leakage) lors de la transformee de Fourier (https://fr.wikipedia.org/wiki/Transformation_de_Fourier).

**hann** (RECOMMANDE) :
- Compromis optimal resolution/fuites
- Ideal pour : Chants d'oiseaux standards, harmoniques moderement separees
- Largeur de lobe principal : moyenne
- Attenuation des lobes secondaires : -31 dB

**blackman** :
- Meilleure attenuation des fuites (-58 dB)
- Ideal pour : Isoler des notes pures, harmoniques tres proches
- Inconvenient : Resolution frequentielle legerement reduite

**hamming** :
- Similaire a Hann mais premier lobe secondaire plus bas
- Utile pour : Telecommunications, traitement du signal

**rect** (rectangulaire) :
- Aucune fenetre (boite rectangulaire)
- Resolution maximale mais fuites importantes
- A eviter sauf pour signaux periodiques exacts

**flattop** :
- Mesure d'amplitude tres precise
- Utile pour : Calibration, metrologie acoustique

**Parametres FFT avances** (codes en dur) :
- n_fft = 2048 : Taille de la FFT (resolution frequentielle)
- hop_length = 512 : Chevauchement des fenetres (resolution temporelle)
- Rapport : 75% de chevauchement (standard)

---

### Gain
**Format** : 1.0 a 100.0 (multiplicateur)

**Impact** : Amplification du signal avant calcul du spectrogramme

**Utilisation** :
- Enregistrements faibles (oiseaux lointains) : 2.0 a 10.0
- Enregistrements normaux : 1.0
- Eviter la saturation : < 1.0 si clipping

**Attention !** : Le gain n'amplifie pas le rapport signal/bruit, il amplifie tout (signal + bruit).

---

### Frequence min/max (Hz)
**Format** : 0 (auto) ou valeur en Hz

**Frequence min** :
- Exemple : 1000 Hz pour ignorer le vent, les infrasons, le bruit de fond basse frequence
- Exemple : 500 Hz pour se concentrer sur les passereaux

**Frequence max** :
- Exemple : 12000 Hz pour la bande typique des passereaux (0.5-12 kHz)
- Exemple : 8000 Hz pour filtrer les ultrasons (chauves-souris, insectes)

**Bandes frequentielles par espece** (references) :
- Butor etoile : 50-500 Hz
- Hibou grand-duc : 200-2000 Hz
- Merle noir : 1000-8000 Hz
- Mesange bleue : 2000-10000 Hz
- Roitelet huppe : 6000-10000 Hz

---

### Plage dynamique (dB)
**Format** : 10 a 200 dBFS

**Concept** : Difference entre le signal le plus fort (0 dBFS) et le plus faible affiche.

**Recommandations** :
- **120 dB** (defaut) : Standard, bon compromis
- **150 dB** : Ecoacoustique, revele les chants faibles dans un paysage sonore complexe
- **80-100 dB** : Chants forts et proches, evite le bruit de fond

**Impact visuel** :
- Valeur elevee : Plus de details dans les sons faibles, mais plus de bruit de fond visible
- Valeur basse : Seuls les sons forts apparaissent, image plus "propre"

**dBFS** (decibels Full Scale) : 0 dBFS = niveau maximum numerique (saturation)

---

### Afficher la legende
**Options** : Oui | Non

**Oui** :
- Affiche les axes de temps (secondes) et frequence (Hz)
- Affiche la barre de couleur avec echelle en dB

**Non** :
- Image sans annotations

---

## Guide d'utilisation professionnelle

### Workflow d'analyse typique

1. **Chargement** : Selectionnez votre fichier audio (WAV, FLAC, MP3, OGG)
2. **Apercu rapide** : Les 60 premieres secondes s'affichent instantanement
3. **Reglage des parametres** :
   - Palette : fiery ou magma
   - Echelle frequence : log
   - Echelle intensite : log
   - Plage dynamique : 120-150 dB
   - Fenetrage : hann ou blackman
4. **Navigation** :
   - **Zoom** : Cliquez sur l'icone loupe et dessinez un rectangle
   - **Panoramique** : Cliquez sur l'icone croix et glissez
   - **Retour** : Cliquez sur l'icone maison
5. **Ecoute** : Cliquez sur Play pour ecouter l'audio complet
6. **Export** : Cliquez sur "Generer l'image finale" (barre de progression affichee)

### Optimisation par type d'analyse

#### Chants complexes (grives, merles, fauvettes)
- Taille : 1920x1080
- Palette : fiery
- Echelle frequence : log
- Plage dynamique : 120-150 dB
- Fenetrage : hann
- Frequence min : 500 Hz
- Frequence max : 12000 Hz

#### Chants aigus (roitelets, mesanges)
- Echelle frequence : log
- Frequence min : 2000 Hz
- Frequence max : 12000 Hz
- Palette : viridis (meilleur contraste hautes frequences)

#### Chants graves (butor, hiboux, poules d'eau)
- Echelle frequence : log
- Frequence min : 50 Hz
- Frequence max : 4000 Hz
- Plage dynamique : 150 dB (sons souvent faibles)

#### Paysages sonores (ecoacoustique)
- Mode : separate (si stereo)
- Palette : magma (perceptuellement uniforme)
- Plage dynamique : 150-180 dB
- Echelle intensite : log
- Taille : 3840x2160 (4K pour details)

#### Harmoniques fines (analyse spectrale)
- Fenetrage : blackman (meilleure separation)
- Taille : 3840x2160
- Echelle frequence : lin (si harmoniques equidistantes)
- Palette : intensity (niveaux de gris precis)

### Pieges a eviter

1. **Plage dynamique trop faible** (< 80 dB) : Perte d'informations sur les chants faibles
2. **Echelle lineaire en frequence** : Impossible de voir simultanement graves et aigus
3. **Fenetrage rectangulaire** : Fuites spectrales importantes, artefacts visuels
4. **Gain excessif** (> 10) : Saturation du spectrogramme, perte de details
5. **Pas de legende** : Image inutilisable ...

---

## Automatisation en ligne de commande (CLI)

### Syntaxe de base

python bioacoustics_spectrogram.py --input fichier.wav --output sortie.png [OPTIONS]

ou version courte :

python bioacoustics_spectrogram.py -i fichier.wav -o sortie.png [OPTIONS]

### Exemples concrets

#### Exemple 1 : Generation rapide (parametres par defaut)
python bioacoustics_spectrogram.py -i oiseau.wav -o spectrogramme.png

#### Exemple 2 : Configuration bioacoustique optimale
python bioacoustics_spectrogram.py -i chant_merle.wav -o merle_spectrogram.png --size 1920x1080 --color fiery --scale log --fscale log --win-func hann --drange 150 --start 500 --stop 12000 --legend

#### Exemple 3 : Analyse des hautes frequences (roitelets)
python bioacoustics_spectrogram.py -i roitelet.wav -o roitelet_HF.png --color viridis --fscale log --start 4000 --stop 12000 --drange 120

#### Exemple 4 : Ecoacoustique (paysage sonore complet)
python bioacoustics_spectrogram.py -i paysage_sonore.wav -o paysage_4K.png --size 3840x2160 --mode separate --color magma --drange 180 --win-func blackman

#### Exemple 5 : Traitement par lots (bash)
#!/bin/bash
# Script de generation en masse

for fichier in ./enregistrements/*.wav; do
    nom_base=$(basename "$fichier" .wav)
    python bioacoustics_spectrogram.py -i "$fichier" -o "./spectrogrammes/${nom_base}.png" --color fiery --fscale log --drange 150 --legend
    echo "Genere : ${nom_base}.png"
done

#### Exemple 6 : Pipeline complet avec FFmpeg natif
ffmpeg -i entree.wav -af "highpass=f=500, lowpass=f=12000" -f wav - | ffmpeg -i - -lavfi "showspectrumpic=size=1920x1080:color=fiery:scale=log:fscale=log:drange=150" -y sortie.png

### Toutes les options CLI disponibles

Options obligatoires :
  -i, --input TEXT          Fichier audio d'entree (WAV, FLAC, MP3, OGG)
  -o, --output TEXT         Fichier image de sortie (PNG)

Options de taille :
  --size TEXT               Resolution (defaut: 1920x1080)
                            Ex: 1280x720, 3840x2160

Options d'affichage :
  --mode TEXT               combined | separate (defaut: combined)
  --color TEXT              fiery | rainbow | intensity | magma | viridis | cool | plasma | green | blue (defaut: fiery)

Options d'echelle :
  --scale TEXT              log | lin | sqrt | cbrt (defaut: log)
  --fscale TEXT             log | lin (defaut: log)

Options de traitement :
  --win-func TEXT           hann | blackman | hamming | rect | bartlett | flattop | welch | nuttall (defaut: hann)
  --gain FLOAT              Amplification 0.1-100.0 (defaut: 1.0)

Options de frequence :
  --start INTEGER           Frequence min en Hz, 0=auto (defaut: 0)
  --stop INTEGER            Frequence max en Hz, 0=auto (defaut: 0)

Options de qualite :
  --drange INTEGER          Plage dynamique 10-200 dB (defaut: 120)

Options d'annotation :
  --legend                  Afficher la legende (defaut: active)
  --no-legend               Masquer la legende

Aide :
  --help                    Afficher cette aide et quitter

### Integration dans des scripts Python

import subprocess

def generer_spectrogramme(audio_file, output_file, **params):
    cmd = ["python", "bioacoustics_spectrogram.py", "-i", audio_file, "-o", output_file]
    for key, value in params.items():
        cmd.append(f"--{key.replace('_', '-')}")
        cmd.append(str(value))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Succes : {output_file}")
        return True
    else:
        print(f"Erreur : {result.stderr}")
        return False

# Utilisation
generer_spectrogramme("oiseau.wav", "oiseau.png", color="fiery", fscale="log", drange=150, start=500, stop=12000)

### Astuces CLI avancees

#### Parallelisation (multiprocessing)
sudo apt install parallel
ls *.wav | parallel -j 4 "python bioacoustics_spectrogram.py -i {} -o {.}.png --color fiery"

#### Integration avec des metadonnees
for fichier in 2024-05-15_06-30-00_*.wav; do
    date=$(echo "$fichier" | grep -oP '\d{4}-\d{2}-\d{2}')
    heure=$(echo "$fichier" | grep -oP '\d{2}-\d{2}-\d{2}')
    python bioacoustics_spectrogram.py -i "$fichier" -o "spectro_${date}_${heure}.png" --drange 150
done

---

## References techniques

### Documentation officielle

- FFmpeg showspectrumpic : https://ffmpeg.org/ffmpeg-filters.html#showspectrumpic
- CloudACM - Tutoriel FFmpeg : https://www.cloudacm.com/?p=3105
- librosa : https://librosa.org/doc/latest/
- Matplotlib : https://matplotlib.org/stable/contents.html

### Ressources bioacoustiques

- Cornell Lab of Ornithology : https://www.birds.cornell.edu/
- Xeno-canto (base de donnees chants d'oiseaux) : https://xeno-canto.org/

### Caracteristiques techniques

**Format d'entree supporte** :
- WAV (PCM, float32)
- FLAC (lossless)
- MP3 (MPEG-1/2 Layer 3)
- OGG Vorbis
- AIFF
- M4A/AAC

**Specifications de sortie** :
- Format : PNG (24-bit RGB)
- Resolution max : Limitee par la memoire RAM
- Espace colorimetrique : sRGB

**Performance** :
- Apercu : ~1-3 secondes (60s d'audio)
- Export complet : ~1-5x temps reel (depend de la duree et resolution)
- RAM requise : ~500 Mo pour 1920x1080

### Parametres FFT avances (codes en dur)

n_fft = 2048           # Taille de la fenetre FFT
hop_length = 512       # Pas entre les fenetres (75% overlap)
window = config.user   # Fonction de fenetrage (hann, blackman...)

Resolution frequentielle :
resolution_Hz = sample_rate / n_fft
Ex: 44100 / 2048 = 21.5 Hz/bin

Resolution temporelle :
resolution_s = hop_length / sample_rate
Ex: 512 / 44100 = 11.6 ms
