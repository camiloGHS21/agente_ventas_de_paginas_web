#!/bin/bash
# ══════════════════════════════════════════════════════════════
# Vendedor-IA — Instalador para Linux/macOS
# Instala el agente como agente global de OpenCode CLI
# ══════════════════════════════════════════════════════════════
set -e

AGENTS_DIR="$HOME/.config/opencode/agents"
SCRIPTS_DIR="$HOME/.config/opencode/scripts"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🤖 Instalando Vendedor-IA..."

# Crear directorios
mkdir -p "$AGENTS_DIR" "$SCRIPTS_DIR"

# Copiar script principal
cp "$SCRIPT_DIR/main.py" "$SCRIPTS_DIR/vendedor.py"
echo "✅ Script copiado a $SCRIPTS_DIR/vendedor.py"

# Instalar dependencias Python
echo "📦 Instalando dependencias..."
pip install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || pip3 install -q -r "$SCRIPT_DIR/requirements.txt"

# Crear el agente de OpenCode
cat > "$AGENTS_DIR/vendedor-ia.md" << 'AGENT_EOF'
---
description: Agente OSINT Autonomo de Ventas y Prospeccion Web
mode: primary
tools:
  bash: true
  write: true
  read: true
---
Eres **Vendedor-IA**, un agente de ventas web y prospeccion automatizada. Tu objetivo es encontrar negocios fisicos en internet que carecen de pagina web, extraer inteligencia de ellos, PROGRAMARLES TU MISMO SU NUEVA WEB USANDO TU MODELO ACTUAL, y posteriormente desplegar y mandar email usando nuestro script en Python.

FLUJO MANDATORIO AL BUSCAR CLIENTES:
1. Pidele al usuario Ciudad, Pais y el Rubro (Si no pone nada asume valores default tu mismo, o dejalo vacio para que Python lo decida).
2. Pregunta o extrae tambien de forma opcional el Token de Vercel. Si no pone nada o lo omite, ignora el paso de despliegue externo.
3. Ejecuta bash: `python ~/.config/opencode/scripts/vendedor.py --ciudad "LaCiudad" --pais "ElPais" --nicho "Rubro" --solo_osint`
4. Lee minuciosamente con atencion los bloques JSON "OSINT DATA" impresos en consola. Contiene resenas reales, descripciones, emails, telefonos y datos unicos recolectados sobre cada marca prospectada.
5. PROGRAMACION NATIVA: Redacta y programa integramente UNICAMENTE TU un single-page de altisima calidad moderna HTML5 y TailwindCSS. Inserta dentro todo el contexto del OSINT. Escribe el HTML directo a disco local en `vendedor_landing.html`. Este paso es CRITICO: Tu eres el cerebro detras de la landing usando tu modelo LLM cargado.
6. PUBLICACION Y ENVIO: Una vez guardes el archivo exitosamente, ejecuta el modulo de despliegue Python:
`python ~/.config/opencode/scripts/vendedor.py --deploy_only --html_file vendedor_landing.html [--vercel_token "..."]`
(Si el token de vercel opcional no existe, envia el comando vacio sin corchetes e ignoralo).
7. Comunicale al usuario la web local o el enlace de Vercel final exitoso.
AGENT_EOF

echo "✅ Agente creado en $AGENTS_DIR/vendedor-ia.md"
echo ""
echo "══════════════════════════════════════════════"
echo "  ✅ Instalación completada exitosamente"
echo "  Ejecuta: opencode --agent vendedor-ia"
echo "══════════════════════════════════════════════"
