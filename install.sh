#!/bash
{ # Bloque para prevenir ejecucion parcial

set -e

install_agents() {
    local VERSION="53.0.0"
    local RAND=$RANDOM
    local REPO_RAW="https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
    local CONFIG_DIR="$HOME/.config/opencode"
    local SCRIPTS_DIR="$CONFIG_DIR/scripts"
    local SKILLS_DIR="$HOME/.agents/skills"

    echo "🤖 Iniciando instalador Universal (v$VERSION)..."

    # 1. Preparar directorios
    mkdir -p "$CONFIG_DIR" "$SCRIPTS_DIR"
    mkdir -p "$SKILLS_DIR/gsap" "$SKILLS_DIR/refero-design" "$SKILLS_DIR/caveman"

    # 2. Descarga de componentes
    echo "[>] Descargando componentes desde el repositorio..."
    
    # 2.1 AGENTES (Scripts)
    curl -fsSL "$REPO_RAW/vendedor.py?v=$RAND" -o "$SCRIPTS_DIR/vendedor.py"
    curl -fsSL "$REPO_RAW/dev.py?v=$RAND" -o "$SCRIPTS_DIR/dev.py"
    curl -fsSL "$REPO_RAW/scripts/auth_google.py?v=$RAND" -o "$SCRIPTS_DIR/auth_google.py"
    
    # 2.2 CONFIG Y PROMPTS
    curl -fsSL "$REPO_RAW/opencode.json?v=$RAND" -o "$CONFIG_DIR/opencode.json"
    curl -fsSL "$REPO_RAW/prompt_vendedor.txt?v=$RAND" -o "$CONFIG_DIR/prompt_vendedor.txt"
    curl -fsSL "$REPO_RAW/prompt_dev.txt?v=$RAND" -o "$CONFIG_DIR/prompt_dev.txt"
    curl -fsSL "$REPO_RAW/prompt_devPlan.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devPlan.txt"
    curl -fsSL "$REPO_RAW/prompt_devDesign.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devDesign.txt"
    curl -fsSL "$REPO_RAW/prompt_devOps.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devOps.txt"
    curl -fsSL "$REPO_RAW/prompt_devTest.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devTest.txt"
    curl -fsSL "$REPO_RAW/prompt_devRefactor.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devRefactor.txt"
    curl -fsSL "$REPO_RAW/prompt_devCopy.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devCopy.txt"
    curl -fsSL "$REPO_RAW/prompt_ceo.txt?v=$RAND" -o "$CONFIG_DIR/prompt_ceo.txt"
    curl -fsSL "$REPO_RAW/prompt_devSocial.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devSocial.txt"
    curl -fsSL "$REPO_RAW/prompt_devAI.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devAI.txt"
    curl -fsSL "$REPO_RAW/prompt_devMoney.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devMoney.txt"
    curl -fsSL "$REPO_RAW/prompt_devBack.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devBack.txt"
    curl -fsSL "$REPO_RAW/prompt_devDocs.txt?v=$RAND" -o "$CONFIG_DIR/prompt_devDocs.txt"
    
    if [ ! -f "$CONFIG_DIR/config_auth.json" ]; then
        cat << 'EOF' > "$CONFIG_DIR/config_auth.json"
{
  "google": {
    "client_id": "TU_CLIENT_ID",
    "client_secret": "TU_CLIENT_SECRET"
  },
  "meta": {
    "app_id": "TU_APP_ID",
    "app_secret": "TU_APP_SECRET"
  }
}
EOF
    fi

    # 2.3 SKILLS
    echo "[>] Instalando Skills (Refero)..."
    curl -fsSL "$REPO_RAW/.agents/skills/refero-design/SKILL.md?v=$RAND" -o "$SKILLS_DIR/refero-design/SKILL.md"

    # 3. Dependencias
    echo "[>] Verificando dependencias Python..."
    pip install -q duckduckgo_search requests google-auth-oauthlib google-auth-httplib2 google-api-python-client 2>/dev/null || pip3 install -q duckduckgo_search requests google-auth-oauthlib google-auth-httplib2 google-api-python-client 2>/dev/null

    echo -e "\n✅ ¡Instalacion exitosa! (v$VERSION)"
    echo "Usa 'opencode --agent ceo' para empezar."
}

install_agents

} # Fin del bloque
