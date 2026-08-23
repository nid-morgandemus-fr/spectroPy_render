#!/bin/bash
# ==============================================================================
# Script de lancement automatique pour spectroPy_render
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_SCRIPT="$SCRIPT_DIR/spectroPy_render.py"

echo -e "${BLUE}🎵 spectroPy_render${NC}"
echo "=========================================="

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Erreur : spectroPy_render.py introuvable dans :${NC}"
    echo "   $SCRIPT_DIR"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Erreur : python3 n'est pas installé.${NC}"
    echo "   sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Vérifier python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installation de python3-venv...${NC}"
    sudo apt update && sudo apt install -y python3-venv python3-full
fi

# 🔧 VÉRIFICATION DES DÉPENDANCES SYSTÈME POUR PYQT6
echo -e "${BLUE}🔍 Vérification des dépendances système Qt...${NC}"
MISSING_DEPS=()

# Liste des bibliothèques xcb nécessaires pour PyQt6 sur Linux
REQUIRED_LIBS=(
    "libxcb-cursor0"
    "libxcb-xinerama0"
    "libxcb-icccm4"
    "libxcb-image0"
    "libxcb-keysyms1"
    "libxcb-randr0"
    "libxcb-render-util0"
    "libxcb-shape0"
    "libxcb-xfixes0"
    "libxkbcommon-x11-0"
)

for lib in "${REQUIRED_LIBS[@]}"; do
    if ! dpkg -l "$lib" &> /dev/null; then
        MISSING_DEPS+=("$lib")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Bibliothèques manquantes détectées :${NC}"
    printf '   - %s\n' "${MISSING_DEPS[@]}"
    echo -e "${BLUE}📦 Installation en cours...${NC}"
    sudo apt update
    sudo apt install -y "${MISSING_DEPS[@]}"
    echo -e "${GREEN}✅ Dépendances système installées.${NC}"
else
    echo -e "${GREEN}✅ Dépendances système OK.${NC}"
fi

# Vérifier FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  FFmpeg n'est pas installé.${NC}"
    echo -e "${YELLOW}   sudo apt install ffmpeg${NC}"
    echo ""
fi

# Créer le venv
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Venv créé.${NC}"
else
    echo -e "${GREEN}✅ Environnement virtuel détecté.${NC}"
fi

# Activer et installer
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip

echo -e "${BLUE}📚 Vérification des dépendances Python...${NC}"
pip install --quiet PyQt6 matplotlib librosa sounddevice
echo -e "${GREEN}✅ Dépendances Python installées.${NC}"

# Lancer
echo -e "${GREEN}🚀 Lancement du programme...${NC}"
echo ""
python "$PYTHON_SCRIPT" "$@"

deactivate 2>/dev/null || true
