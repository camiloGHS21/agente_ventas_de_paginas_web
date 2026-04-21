#!/bin/bash
set -e

CONFIG_DIR="$HOME/.config/opencode"
SCRIPTS_DIR="$CONFIG_DIR/scripts"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🤖 Instalando Vendedor-IA (v12.5.0)..."

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
