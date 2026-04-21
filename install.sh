#!/bin/bash
set -e

# 0. Configuracion de descarga remota (v13.0.0)
REPO_RAW="https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
REQUIRED_FILES=("main.py" "opencode.json" "prompt_vendedor.txt" "requirements.txt")

# Detectar si estamos en un pipe o ejecucion local
if [[ "$0" == "bash" || "$0" == "sh" || "$0" == "/bin/bash" ]]; then
    SCRIPT_DIR=$(pwd)
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        echo "â¬‡ï¸  Descargando $file desde GitHub..."
        curl -fsSL "$REPO_RAW/$file" -o "$SCRIPT_DIR/$file"
    fi
done

CONFIG_DIR="$HOME/.config/opencode"
SCRIPTS_DIR="$CONFIG_DIR/scripts"

echo "🤖 Instalando Vendedor-IA (v13.0.1)..."

# 1. Crear directorios
mkdir -p "$CONFIG_DIR" "$SCRIPTS_DIR"

# 2. Copiar archivos EXACTAMENTE como estan
cp "$SCRIPT_DIR/main.py" "$SCRIPTS_DIR/vendedor.py"
cp "$SCRIPT_DIR/prompt_vendedor.txt" "$CONFIG_DIR/prompt_vendedor.txt"
cp "$SCRIPT_DIR/opencode.json" "$CONFIG_DIR/opencode.json"

# 3. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || pip3 install -q -r "$SCRIPT_DIR/requirements.txt"

echo "✅ Instalación completada en $CONFIG_DIR"
echo "Ejecuta: opencode --agent find_create_web"
