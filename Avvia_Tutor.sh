#!/bin/bash
echo "Avvio del Tutor di Italiano..."
# Naviga nella cartella dello script
cd "$(dirname "$0")"
# Attiva l'ambiente virtuale
source .venv/bin/activate
python3 main.py