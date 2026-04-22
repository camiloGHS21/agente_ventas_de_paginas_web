# Universal Agent Installer (v45.0.0)
$ErrorActionPreference = "Stop"

function Install-Agents {
    $VERSION = "45.0.0"
    $RAND = Get-Random
    $REPO_RAW = "https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
    $configDir = "$env:USERPROFILE\.config\opencode"
    $scriptsDir = "$configDir\scripts"
    $SkillsDir = "$env:USERPROFILE\.agents\skills"

    Write-Host "[*] Iniciando instalador Universal (v$VERSION)..." -ForegroundColor Cyan

    # 1. Preparar directorios
    $dirs = @($scriptsDir, "$SkillsDir\gsap", "$SkillsDir\refero-design", "$SkillsDir\caveman")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    }

    # 2. Descarga de componentes
    Write-Host "[>] Descargando componentes desde el repositorio..." -ForegroundColor Yellow
    
    # 2.1 AGENTES (Scripts)
    Invoke-WebRequest -Uri "$REPO_RAW/main.py?v=$RAND" -OutFile "$scriptsDir\vendedor.py" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/dev.py?v=$RAND" -OutFile "$scriptsDir\dev.py" -UseBasicParsing
    
    # 2.2 CONFIG Y PROMPTS
    Invoke-WebRequest -Uri "$REPO_RAW/opencode.json?v=$RAND" -OutFile "$configDir\opencode.json" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_vendedor.txt?v=$RAND" -OutFile "$configDir\prompt_vendedor.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_dev.txt?v=$RAND" -OutFile "$configDir\prompt_dev.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devPlan.txt?v=$RAND" -OutFile "$configDir\prompt_devPlan.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devDesign.txt?v=$RAND" -OutFile "$configDir\prompt_devDesign.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devOps.txt?v=$RAND" -OutFile "$configDir\prompt_devOps.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devTest.txt?v=$RAND" -OutFile "$configDir\prompt_devTest.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devRefactor.txt?v=$RAND" -OutFile "$configDir\prompt_devRefactor.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devCopy.txt?v=$RAND" -OutFile "$configDir\prompt_devCopy.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_ceo.txt?v=$RAND" -OutFile "$configDir\prompt_ceo.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devBack.txt?v=$RAND" -OutFile "$configDir\prompt_devBack.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devDocs.txt?v=$RAND" -OutFile "$configDir\prompt_devDocs.txt" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/prompt_devSocial.txt?v=$RAND" -OutFile "$configDir\prompt_devSocial.txt" -UseBasicParsing

    # 2.3 SKILLS
    Write-Host "[>] Instalando Skills (Caveman, Refero, GSAP)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "$REPO_RAW/.agents/skills/gsap/SKILL.md?v=$RAND" -OutFile "$SkillsDir\gsap\SKILL.md" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/.agents/skills/refero-design/SKILL.md?v=$RAND" -OutFile "$SkillsDir\refero-design\SKILL.md" -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO_RAW/.agents/skills/caveman/SKILL.md?v=$RAND" -OutFile "$SkillsDir\caveman\SKILL.md" -UseBasicParsing

    # 3. Dependencias
    Write-Host "[>] Verificando dependencias Python..." -ForegroundColor Yellow
    pip install -q duckduckgo_search requests 2>$null

    Write-Host "`n[DONE] Instalacion Exitosa v$VERSION" -ForegroundColor Green
    Write-Host "Agente Vendedor: opencode --agent vendedor"
    Write-Host "Agente DevPlan: opencode --agent devPlan"
    Write-Host "Agente DevDesign: opencode --agent devDesign"
    Write-Host "Agente DevOps: opencode --agent devOps"
    Write-Host "Agente DevTest: opencode --agent devTest"
    Write-Host "Agente DevRefactor: opencode --agent devRefactor"
    Write-Host "Agente DevCopy: opencode --agent devCopy"
    Write-Host "Agente CEO: opencode --agent ceo"
    Write-Host "Agente DevBack: opencode --agent devBack"
    Write-Host "Agente DevDocs: opencode --agent devDocs"
    Write-Host "Agente DevSocial: opencode --agent devSocial"
    Write-Host "Agente Dev: opencode --agent dev"
}

try {
    Install-Agents
} catch {
    Write-Host "[-] Error: $($_.Exception.Message)" -ForegroundColor Red
}
