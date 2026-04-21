# Vendedor-IA Professional Installer (v14.0.0)
$ErrorActionPreference = "Stop"

function Install-Vendedor {
    $REPO_RAW = "https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
    $configDir = "$env:USERPROFILE\.config\opencode"
    $scriptsDir = "$configDir\scripts"
    $SkillsDir = "$configDir\.agents\skills"

    Write-Host "🤖 Iniciando instalador profesional Vendedor-IA (v19.0.0)..." -ForegroundColor Cyan

    # 1. Preparar directorios
    if (-not (Test-Path $scriptsDir)) { New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null }
    if (!(Test-Path "$SkillsDir\frontend-design")) { New-Item -Path "$SkillsDir\frontend-design" -ItemType Directory -Force }
    if (!(Test-Path "$SkillsDir\gsap")) { New-Item -Path "$SkillsDir\gsap" -ItemType Directory -Force }

    # 2. Descarga Directa
    Write-Host "â¬‡ï¸  Descargando componentes..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "$REPO_RAW/main.py" -OutFile "$scriptsDir\vendedor.py" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_vendedor.txt" -OutFile "$configDir\prompt_vendedor.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/opencode.json" -OutFile "$configDir\opencode.json" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/requirements.txt" -OutFile "$configDir\requirements.txt" -UseBasicParsing

    # 2.1 Descargar Skills
    Write-Host "🎨 Instalando Elite Skills..." -ForegroundColor Yellow
    Invoke-RestMethod -Uri "$REPO_RAW/.agents/skills/frontend-design/SKILL.md" -OutFile "$SkillsDir\frontend-design\SKILL.md"
    Invoke-RestMethod -Uri "$REPO_RAW/.agents/skills/frontend-design/LICENSE.txt" -OutFile "$SkillsDir\frontend-design\LICENSE.txt"
    Invoke-RestMethod -Uri "$REPO_RAW/.agents/skills/gsap/SKILL.md" -OutFile "$SkillsDir\gsap\SKILL.md"

    # 3. Dependencias
    Write-Host "📦 Instalando dependencias Python..." -ForegroundColor Yellow
    pip install -q -r "$configDir\requirements.txt" 2>$null

    Write-Host "✅ Instalado correctamente en $configDir" -ForegroundColor Green
    Write-Host "Ejecuta: opencode --agent find_create_web" -ForegroundColor White
}

# Ejecutar instalador
try {
    Install-Vendedor
} catch {
    Write-Error "❌ Error durante la instalacion: $_"
}
