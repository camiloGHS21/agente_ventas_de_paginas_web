# 0. Configuracion de descarga remota (v13.0.1)
# Detectar directorio de trabajo (v13.0.1)
$workDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$REPO_RAW = "https://raw.githubusercontent.com/camiloGHS21/agente_ventas_de_paginas_web/master"
$requiredFiles = @("main.py", "opencode.json", "prompt_vendedor.txt", "requirements.txt")

foreach ($file in $requiredFiles) {
    if (-not (Test-Path "$workDir\$file")) {
        Write-Host "â¬‡ï¸  Descargando $file desde GitHub..."
        Invoke-WebRequest -Uri "$REPO_RAW/$file" -OutFile "$workDir\$file" -UseBasicParsing
    }
}

$configDir = "$env:USERPROFILE\.config\opencode"
$scriptsDir = "$configDir\scripts"

New-Item -ItemType Directory -Force -Path $configDir | Out-Null
New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null

# 1. Copiar archivos EXACTAMENTE como estan
Copy-Item -Path "$workDir\main.py" -Destination "$scriptsDir\vendedor.py" -Force
Copy-Item -Path "$workDir\prompt_vendedor.txt" -Destination "$configDir\prompt_vendedor.txt" -Force
Copy-Item -Path "$workDir\opencode.json" -Destination "$configDir\opencode.json" -Force

# 2. Instalar dependencias
Write-Host "Instalando dependencias..."
pip install -q -r "$workDir\requirements.txt" 2>$null

Write-Host "✅ Instalado correctamente en $configDir"
Write-Host "Ejecuta: opencode --agent find_create_web"
