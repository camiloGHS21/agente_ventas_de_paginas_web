#!/bin/bash
set -e

# 0. Configuracion de descarga remota (v13.0.2)
REPO_RAW="https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
CONFIG_DIR="$HOME/.config/opencode"
SCRIPTS_DIR="$CONFIG_DIR/scripts"

echo "🤖 Instalando Vendedor-IA (v13.0.2)..."

# 1. Crear directorios
mkdir -p "$CONFIG_DIR" "$SCRIPTS_DIR"

# 2. Descargar directamente a su destino (Sin staging local)
echo "â¬‡ï¸  Descargando componentes..."
curl -fsSL "$REPO_RAW/main.py" -o "$SCRIPTS_DIR/vendedor.py"
curl -fsSL "$REPO_RAW/prompt_vendedor.txt" -o "$CONFIG_DIR/prompt_vendedor.txt"
curl -fsSL "$REPO_RAW/opencode.json" -o "$CONFIG_DIR/opencode.json"
curl -fsSL "$REPO_RAW/requirements.txt" -o "$CONFIG_DIR/requirements.txt"

# 3. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -q -r "$CONFIG_DIR/requirements.txt" 2>/dev/null || pip3 install -q -r "$CONFIG_DIR/requirements.txt"

echo "✅ Instalación completada en $CONFIG_DIR"
echo "Ejecuta: opencode --agent find_create_web"
