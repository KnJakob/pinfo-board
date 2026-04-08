#!/bin/bash

cd "pinfo"

uv sync

echo "🚀 Starte Color-of-the-Day App mit uv..."

# --server.address 0.0.0.0 macht die App im Tailscale-Netzwerk sichtbar
# --server.headless true schaltet das automatische Öffnen des Browsers aus
uv run streamlit run main.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true
