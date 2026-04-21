#!/bin/bash
{ # Bloque para prevenir ejecucion parcial

set -e

install_vendedor() {
    local REPO_RAW="https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
    local CONFIG_DIR="$HOME/.config/opencode"
    local SCRIPTS_DIR="$CONFIG_DIR/scripts"
    local VERSION="14.0.0"

    echo "🤖 Iniciando instalador profesional Vendedor-IA ($VERSION)..."

    # 1. Preparar entorno
    mkdir -p "$CONFIG_DIR" "$SCRIPTS_DIR"

    # 2. Descarga Directa (Patron Industrial)
    echo "â¬‡ï¸  Descargando componentes de OpenCode..."
    
    # Descargar cada archivo de forma segura
    curl -fsSL "$REPO_RAW/main.py" -o "$SCRIPTS_DIR/vendedor.py"
    curl -fsSL "$REPO_RAW/prompt_vendedor.txt" -o "$CONFIG_DIR/prompt_vendedor.txt"
    curl -fsSL "$REPO_RAW/opencode.json" -o "$CONFIG_DIR/opencode.json"
    curl -fsSL "$REPO_RAW/requirements.txt" -o "$CONFIG_DIR/requirements.txt"

    # 3. Dependencias
    echo "📦 Sincronizando dependencias Python..."
    pip install -q -r "$CONFIG_DIR/requirements.txt" 2>/dev/null || pip3 install -q -r "$CONFIG_DIR/requirements.txt"

    echo "✅ ¡Instalacion exitosa! Agente registrado como: @find_create_web"
    echo "Directorio: $CONFIG_DIR"
    echo "Comando: opencode --agent find_create_web"
}

install_vendedor

} # Fin del bloque
