# 🤖 Vendedor-IA — Agente Autónomo OSINT de Prospección Web

> **Motor:** Nominatim + DuckDuckGo | **100% Gratuito** | **Sin API Keys**

Vendedor-IA es un agente autónomo que busca negocios locales que **no tienen página web**, extrae inteligencia OSINT sobre ellos y genera automáticamente propuestas de sitios web usando IA.

---

## ✨ Características

| Funcionalidad | Descripción |
|---|---|
| 🔍 **Descubrimiento Dual** | Nominatim (OSM) + DuckDuckGo como fallback |
| 🕵️ **OSINT Multi-Capa** | Extracción de emails, teléfonos, redes sociales, reseñas |
| 📊 **Lead Scoring** | Puntuación 0-100 para priorizar prospectos |
| 🎨 **Generación Nativa** | OpenCode genera la web con tu modelo LLM favorito |
| 🚀 **Deploy a Vercel** | Publicación automática vía REST API (opcional) |
| 📧 **Email sin contraseña** | Abre Gmail pre-rellenado en el navegador |
| 📁 **Persistencia JSON** | Guarda resultados OSINT en `resultados_osint/` |
| 🎨 **CLI con colores** | Interfaz de terminal moderna y legible |

## 📋 Requisitos

- **Python** 3.8+
- **OpenCode CLI** (para modo agente nativo)
- **pip** (gestor de paquetes Python)

## 🚀 Instalación

### Windows (PowerShell)

```powershell
cd agente_ventas_ai
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Linux / macOS

```bash
cd agente_ventas_ai
pip install -r requirements.txt
chmod +x install.sh
./install.sh
```

### Solo dependencias (sin OpenCode)

```bash
pip install -r requirements.txt
```

## 🎮 Uso

### Modo 1: Agente OpenCode (Recomendado)

Ejecuta el agente desde OpenCode CLI. El modelo LLM que tengas seleccionado (DeepSeek, Gemini, etc.) será quien genere las páginas web.

```bash
opencode --agent vendedor-ia
```

Luego simplemente dile: *"Busca prospectos en Bogotá, Colombia"*

### Modo 2: Script directo (Solo OSINT)

```bash
# Interactivo (te pregunta todo paso a paso)
python main.py

# Con argumentos
python main.py --ciudad "Miami" --pais "USA" --nicho "restaurant"

# Solo OSINT sin generación
python main.py --ciudad "Bogota" --pais "Colombia" --nicho "cafe" --solo_osint
```

### Modo 3: Deploy de un HTML existente

```bash
# Solo deploy a Vercel
python main.py --deploy_only --html_file landing.html --vercel_token "tk_..."

# Sin Vercel (solo local)
python main.py --deploy_only --html_file landing.html
```

## 📂 Estructura del Proyecto

```
agente_ventas_ai/
├── main.py              # Script principal del agente
├── requirements.txt     # Dependencias Python
├── install.ps1          # Instalador Windows (OpenCode)
├── install.sh           # Instalador Linux/macOS (OpenCode)
├── README.md            # Esta documentación
├── resultados_osint/    # JSONs con datos OSINT (auto-generado)
└── lead_sites/          # HTMLs generados (auto-generado)
```

## ⚙️ Argumentos CLI

| Argumento | Descripción | Default |
|---|---|---|
| `--ciudad` | Ciudad donde buscar | Miami |
| `--pais` | País de búsqueda | USA |
| `--nicho` | Tipo de negocio | restaurant |
| `--vercel_token` | Token API de Vercel | *(omitido)* |
| `--solo_osint` | Solo ejecuta OSINT | `false` |
| `--deploy_only` | Solo despliega un HTML | `false` |
| `--html_file` | HTML para deploy_only | *(requerido con deploy_only)* |
| `--limite` | Máximo de negocios | 25 |
| `--version` | Muestra la versión | — |

## 🔧 APIs Gratuitas Utilizadas

| API | Uso | Límite |
|---|---|---|
| **Nominatim** (OSM) | Geocodificación y búsqueda de POIs | 1 req/seg |
| **DuckDuckGo** | Búsqueda web, OSINT, fallback | Sin límite duro |
| **Vercel** *(opcional)* | Deploy de sitios estáticos | Plan gratuito |

> ⚠️ **No se requiere ninguna API Key.** Todo funciona out-of-the-box.

## 📊 Sistema de Scoring

Cada lead recibe una puntuación de 0-100:

| Criterio | Puntos |
|---|---|
| Base | +50 |
| Sin sitio web | +30 |
| Ya tiene sitio web | -40 |
| Email encontrado | +10 |
| Redes sociales activas | +5 |
| Teléfono encontrado | +5 |

Leads con score < 30 son automáticamente descartados.

## 📜 Licencia

Uso personal y educativo. Las APIs utilizadas tienen sus propios términos de servicio.
