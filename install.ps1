# 0. Configuracion de descarga remota (v13.0.2)
$REPO_RAW = "https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
$configDir = "$env:USERPROFILE\.config\opencode"
$scriptsDir = "$configDir\scripts"

Write-Host "🤖 Instalando Vendedor-IA (v13.0.2)..."

# 1. Crear directorios
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null

# 2. Descargar directamente a su destino
Write-Host "â¬‡ï¸  Descargando componentes..."
Invoke-WebRequest -Uri "$REPO_RAW/main.py" -OutFile "$scriptsDir\vendedor.py" -UseBasicParsing
Invoke-WebRequest -Uri "$REPO_RAW/prompt_vendedor.txt" -OutFile "$configDir\prompt_vendedor.txt" -UseBasicParsing
Invoke-WebRequest -Uri "$REPO_RAW/opencode.json" -OutFile "$configDir\opencode.json" -UseBasicParsing
Invoke-WebRequest -Uri "$REPO_RAW/requirements.txt" -OutFile "$configDir\requirements.txt" -UseBasicParsing

# 3. Instalar dependencias
Write-Host "📦 Instalando dependencias..."
pip install -q -r "$configDir\requirements.txt" 2>$null

Write-Host "✅ Instalado correctamente en $configDir"
Write-Host "Ejecuta: opencode --agent find_create_web"
