import os
import json
import requests
from duckduckgo_search import DDGS

# Configuración NICHOS v24.0 (Refero Style)
NICHE_CONFIG = {
    "RESTAURANTE": {
        "font": "'Playfair Display', serif", "primary": "#eab308",
        "topic": "luxury restaurant food gourmet", "tagline": "gastronomía de clase mundial",
        "soul": "border-left: 4px solid var(--primary); padding-left: 2rem;"
    },
    "GYM": {
        "font": "'Oswald', sans-serif", "primary": "#ef4444",
        "topic": "modern fitness gym bodybuilding", "tagline": "rendimiento máximo y fitness",
        "soul": "text-shadow: 0 0 20px rgba(239, 68, 68, 0.3); letter-spacing: 0.1em;"
    },
    "SPA": {
        "font": "'Montserrat', sans-serif", "primary": "#f472b6",
        "topic": "wellness spa beauty relax", "tagline": "bienestar y cuidado personal",
        "soul": "border-radius: 4rem 1rem; overflow: hidden;"
    },
    "TECH": {
        "font": "'Syne', sans-serif", "primary": "#3b82f6",
        "topic": "cutting edge technology digital software", "tagline": "innovación y transformación digital",
        "soul": "background: radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%);"
    },
    "PROFESSIONAL": {
        "font": "'EB Garamond', serif", "primary": "#1e3a8a",
        "topic": "executive office corporate law", "tagline": "excelencia y consultoría estratégica",
        "soul": "border-top: 1px solid rgba(255,255,255,0.1); padding-top: 3rem;"
    },
    "MEDICAL": {
        "font": "'Inter', sans-serif", "primary": "#0ea5e9",
        "topic": "modern medical clinic hospital health", "tagline": "salud y atención especializada",
        "soul": "box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(14, 165, 233, 0.1);"
    },
    "GENERAL": {
        "font": "'Inter', sans-serif", "primary": "#a8a29e",
        "topic": "business success professional lifestyle", "tagline": "excelencia y liderazgo empresarial",
        "soul": "border-bottom: 2px solid var(--primary); width: fit-content;"
    }
}

def buscar_imagenes_pro(query, limit=5):
    """Busca imágenes reales usando DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=limit)
            return [r['image'] for r in results if r.get('image')]
    except Exception as e:
        print(f"[-] Error buscando imágenes: {e}")
        return []

def generar_css_premium(nicho):
    """Genera framework CSS (Refero.design Style)."""
    conf = NICHE_CONFIG.get(nicho, NICHE_CONFIG["GENERAL"])
    return f"""
:root {{
  --primary: {conf['primary']}; --bg: #0c0a09; --text: #fafaf9; --card-bg: rgba(23, 21, 20, 0.8);
  --font-main: {conf['font']}; --transition: 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  --tracking-tight: -0.02em; --tracking-wide: 0.05em; --tracking-caps: 0.1em;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; overflow-x: hidden; line-height: 1.6; -webkit-font-smoothing: antialiased; }}
h1, h2, h3 {{ font-family: var(--font-main); letter-spacing: var(--tracking-tight); line-height: 1.1; text-transform: uppercase; }}
.caps {{ text-transform: uppercase; letter-spacing: var(--tracking-caps); font-weight: 800; font-size: 0.75rem; color: var(--primary); }}
.small {{ font-size: 0.85rem; opacity: 0.6; letter-spacing: var(--tracking-wide); }}
img {{ max-width: 100%; height: auto; border-radius: 1.5rem; transition: var(--transition); }}
img:hover {{ filter: brightness(1.1); transform: scale(1.02); }}
.container {{ max-width: 1300px; margin: 0 auto; padding: 0 2.5rem; }}
nav {{ position: fixed; top: 0; width: 100%; padding: 2rem 0; z-index: 1000; backdrop-filter: blur(20px); background: rgba(12,10,9,0.4); border-bottom: 1px solid rgba(255,255,255,0.03); }}
nav .content {{ display: flex; justify-content: space-between; align-items: center; }}
nav .links {{ display: flex; gap: 3rem; }}
nav a {{ color: var(--text); text-decoration: none; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: var(--tracking-caps); opacity: 0.6; }}
nav a:hover {{ opacity: 1; color: var(--primary); }}
.hero {{ min-height: 90vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 10rem 2rem 6rem; }}
.hero h1 {{ font-size: clamp(3rem, 10vw, 8rem); margin-bottom: 2.5rem; font-weight: 900; }}
.soul-box {{ {conf['soul']} }}
.grid-auto {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 3rem; padding: 6rem 0; }}
.card {{ background: var(--card-bg); padding: 3.5rem; border-radius: 2rem; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 1.5rem; }}
@media (max-width: 768px) {{ .hero {{ text-align: left; align-items: flex-start; }} nav .links {{ display: none; }} }}
"""

def scaffold_react_project(mejor, lider, nicho):
    """Crea proyecto React Multi-Página v25.0 (Bespoke Images)."""
    conf = NICHE_CONFIG.get(nicho, NICHE_CONFIG["GENERAL"])
    safe_name = "".join(c for c in mejor['nombre'] if c.isalnum()).lower()
    base_path = f"lead_sites/{safe_name}_v25"
    
    for d in ["src/components", "src/pages", "src/styles", "public"]:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)

    # Buscar Imagenes Reales
    print(f"[*] Buscando imágenes PRO para {nicho}...")
    pics = buscar_imagenes_pro(f"{mejor['nombre']} {conf['topic']}", limit=10)
    img_hero = pics[0] if pics else "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=1200"

    with open(os.path.join(base_path, "package.json"), "w") as f:
        json.dump({{
            "name": f"proposal-{{safe_name}}", "private": True, "version": "25.0.0", "type": "module",
            "scripts": {{ "dev": "vite", "build": "vite build" }},
            "dependencies": {{ "react": "^18.2.0", "react-dom": "^18.2.0", "react-router-dom": "^6.11.0" }},
            "devDependencies": {{ "@vitejs/plugin-react": "^4.0.0", "vite": "^4.3.0" }}
        }}, f, indent=2)

    with open(os.path.join(base_path, "src/main.jsx"), "w") as f:
        f.write("import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport { BrowserRouter } from 'react-router-dom';\nimport App from './App.jsx';\nimport './styles/index.css';\n\nReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>);")

    with open(os.path.join(base_path, "src/styles/index.css"), "w") as f:
        f.write(generar_css_premium(nicho))

    with open(os.path.join(base_path, "src/components/Navbar.jsx"), "w") as f:
        f.write(f"""import React from 'react';\nimport {{ Link }} from 'react-router-dom';\nexport default function Navbar() {{ return (<nav><div className="container content"><Link to="/" style={{{{ fontSize: '1.5rem', fontWeight: 800 }}}}>{mejor['nombre']}</Link><div className="links"><Link to="/">Inicio</Link><Link to="/menu">{'Carta' if nicho=='RESTAURANTE' else 'Servicios'}</Link><Link to="/gallery">Galeria</Link></div></div></nav>); }}""")

    with open(os.path.join(base_path, "src/pages/Home.jsx"), "w") as f:
        f.write(f"""import React, {{ useEffect }} from 'react';\nexport default function Home() {{ useEffect(() => {{ gsap.from(".hero-content > *", {{ opacity: 0, y: 50, duration: 1.5, stagger: 0.2 }}); }}, []); return (<div className="hero"><div className="container hero-content"><p className="caps">Refero x Caveman v25</p><h1>{mejor['nombre']}</h1><div className="soul-box"><p className="small">{conf['tagline']}</p></div><img src="{img_hero}" style={{{{ marginTop: '3rem', width: '100%', height: '500px', objectFit: 'cover' }}}} /></div></div>); }}""")

    with open(os.path.join(base_path, "src/pages/Gallery.jsx"), "w") as f:
        gallery_grid = "".join([f'<img className="gallery-img" src="{p}" style={{{{ height: "300px", objectFit: "cover" }}}} />' for p in pics[1:7]])
        f.write(f"""import React from 'react'; export default function Gallery() {{ return (<div style={{{{ padding: '10rem 0' }}}}><div className="container"><h2 style={{{{ textAlign: 'center', marginBottom: '4rem' }}}}>Nuestro Trabajo</h2><div className="grid-auto">{gallery_grid}</div></div></div>); }}""")

    with open(os.path.join(base_path, "src/App.jsx"), "w") as f:
        f.write("import React from 'react';\nimport { Routes, Route } from 'react-router-dom';\nimport Navbar from './components/Navbar';\nimport Home from './pages/Home';\nimport Gallery from './pages/Gallery';\nexport default function App() { return (<><Navbar /><Routes><Route path='/' element={<Home />} /><Route path='/menu' element={<Home />} /><Route path='/gallery' element={<Gallery />} /></Routes></>); }")

    with open(os.path.join(base_path, "index.html"), "w") as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'/><title>{mejor['nombre']}</title><script src='https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js'></script></head><body><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>")

    print(f"✅ Propuesta generada en: {base_path}")
    return base_path
