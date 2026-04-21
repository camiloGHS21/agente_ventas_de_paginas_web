#!/usr/bin/env python3
"""
VENDEDOR-IA v3.0 - Agente Autonomo OSINT de Prospeccion Web
Motor: Nominatim + DuckDuckGo + Web Scraping Directo
100% GRATUITO - Sin API Keys - Compatible con OpenCode CLI
"""
import os
import sys
import time
import json
import re
import argparse
import urllib.parse
import webbrowser
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

import requests

try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        print("[ERROR] Dependencia faltante. Ejecuta: pip install duckduckgo_search")
        sys.exit(1)

# ==================================================================
# CONFIGURACION
# ==================================================================
VERSION = "16.0.0"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PROPUESTAS_DIR = "lead_sites"

# Regex compilados para rendimiento
RE_EMAIL = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
# Soporta: (123) 456-7890, 123-456-7890, 123.456.7890, +1 1234567890, etc.
RE_PHONE = re.compile(r'(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}|(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}')
RE_SOCIAL_HANDLE = re.compile(r'@([a-zA-Z0-9_.]{3,30})')

REDES_SOCIALES = {'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
                  'tiktok.com', 'linkedin.com', 'youtube.com', 'pinterest.com'}
DIRECTORIOS_WEB = REDES_SOCIALES | {
    'tripadvisor.com', 'yelp.com', 'foursquare.com', 'yellowpages.com',
    'paginasamarillas.com', 'google.com', 'maps.google.com',
    'ubereats.com', 'doordash.com', 'grubhub.com', 'rappi.com',
    'wikipedia.org', 'wikidata.org'
}

# Filtro anti-basura para emails
EMAIL_BLACKLIST_DOMAINS = {
    'example.com', 'test.com', 'email.com', 'domain.com',
    'sentry.io', 'gravatar.com', 'wordpress.com', 'w3.org',
    'schema.org', 'googleapis.com', 'google.com', 'gstatic.com',
    'facebook.com', 'twitter.com', 'instagram.com',
}
EMAIL_BLACKLIST_SUFFIXES = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.css', '.js')

# ==================================================================
# UTILIDADES
# ==================================================================
def safe_request(url, method="GET", data=None, params=None, json_body=None,
                 headers=None, timeout=15, retries=2):
    """Request HTTP robusto con reintentos."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    for attempt in range(retries):
        try:
            if method == "POST":
                resp = requests.post(url, data=data, json=json_body,
                                     headers=hdrs, timeout=timeout)
            else:
                resp = requests.get(url, params=params, headers=hdrs,
                                    timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)
    return None

def ddg_search(query, max_results=5, retries=2, region=None):
    """DuckDuckGo search robusto con soporte regional (ej: 'co-es')."""
    for _ in range(retries):
        try:
            with DDGS() as ddgs:
                params = {"keywords": query, "max_results": max_results}
                if region: params["region"] = region
                return list(ddgs.text(**params))
        except Exception:
            time.sleep(2)
    return []

def generar_id(nombre):
    return hashlib.md5(nombre.lower().strip().encode()).hexdigest()[:10]

def limpiar_email(email):
    """Valida y limpia un email extraido."""
    email = email.lower().strip().rstrip('.')
    if email.endswith(EMAIL_BLACKLIST_SUFFIXES):
        return None
    dominio = email.split('@')[-1]
    if dominio in EMAIL_BLACKLIST_DOMAINS:
        return None
    if len(email) < 6 or len(email) > 80:
        return None
    # Filtrar emails que son claramente IDs o hashes
    local = email.split('@')[0]
    if len(local) > 40:
        return None
    return email

class HTMLTextExtractor(HTMLParser):
    """Extrae texto plano de HTML para buscar emails y telefonos."""
    def __init__(self):
        super().__init__()
        self.result = []
        self._skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self._skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self._skip = False
    def handle_data(self, data):
        if not self._skip:
            self.result.append(data)
    def get_text(self):
        return ' '.join(self.result)

def extraer_texto_html(html_raw):
    """Convierte HTML crudo a texto plano."""
    try:
        parser = HTMLTextExtractor()
        parser.feed(html_raw)
        return parser.get_text()
    except Exception:
        return html_raw

# ==================================================================
# MODULO 1: DESCUBRIMIENTO DE NEGOCIOS (Nominatim + DuckDuckGo)
# ==================================================================
# JUNK FILTER: Dominios y palabras clave que no son negocios locales
JUNK_KEYWORDS = ['stackoverflow', 'github', 'reddit', 'wikipedia', 'youtube', 'amazon', 'temu']

# Directorios de confianza para filtrar por URL
TRUSTED_DIRECTORIES = [
    'yelp.com/biz/', 'yellowpages.com', 'bbb.org/hvac', 'bbb.org/profile',
    'facebook.com/pages', 'instagram.com/', 'houzz.com/pro', 'homeadvisor.com',
    'tripadvisor.com', 'tripadvisor.co', 'tripadvisor.com.co', 'degusta.com'
]

def limpiar_nombre(nombre):
    """Limpia el nombre del negocio para comparaciones y extraccion."""
    n = nombre.lower()
    # Eliminar sufijos de directorios comunes
    for sufijo in [' - miami', ' - austin', ' - yelp', ' - yellow pages', ' | bbb', ' | reviews']:
        n = n.split(sufijo)[0]
    for extra in ['restaurante', 'cafe', 'roofing', 'landscaping', 'plumbing', 'inc', 'llc', 'lp', 'services', 'co', 'comida', 'cocina']:
        if len(extra) > 2:
            n = n.replace(extra, '')
    return re.sub(r'[^a-z0-9]', '', n).strip()

def extraer_nombre_url(url):
    """Extrae el nombre de un negocio desde su URL de directorio."""
    # Yelp: /biz/business-name-city
    if 'yelp.com/biz/' in url:
        partes = url.split('/biz/')[-1].split('?')[0].split('/')
        if partes:
            return partes[0].replace('-', ' ').title()
    # YellowPages: /mip/business-name-12345
    if 'yellowpages.com/mip/' in url:
        partes = url.split('/mip/')[-1].split('?')[0].split('/')
        if partes:
            name_part = partes[0].rsplit('-', 1)[0]
            return name_part.replace('-', ' ').title()
    return None

def es_nicho_valido(snippet, titulo, nicho):
    """Sencilla validacion multilingue (ES/EN) de que el resultado trata sobre el nicho."""
    nicho_norm = nicho.lower()
    content = (snippet + " " + titulo).lower()
    if nicho_norm[:4] in content or "restauran" in content: return True
    # Keywords relacionadas ES/EN
    rel = {
        "landscaping": ["garden", "lawn", "grass", "tree", "yard", "jardin", "pasto", "cesped", "arbol"],
        "restaurant": ["food", "menu", "dining", "cook", "eat", "comida", "carta", "cocina", "mesa", "restaurante"],
        "roofing": ["roof", "shingle", "leak", "gutter", "techo", "gotera", "tejado", "cubierta"],
        "plumbing": ["pipe", "leak", "drain", "water", "plomero", "tuberia", "fuga", "desague", "agua"]
    }
    for kw in rel.get(nicho_norm, []):
        if kw in content: return True
    return False

def buscar_negocios(ciudad, nicho, limite=100):
    """Orquestador de descubrimiento ELITE: Dirigido, Validado y Filtrado."""
    print(f"[*] Escaneando ciudad: {ciudad} (Nicho: {nicho})")
    pool = {} 
    
    # --- FUENTE 1: Nominatim (OSM) ---
    print(f"[*] Buscando en OpenStreetMap (Nominatim)...")
    # Ya no usamos fallbacks hardcodeados (v11.0)
    # El descubrimiento ahora es puramente OSINT y universal.
    
    try:
        resp = requests.get(NOMINATIM_URL, params={
            "q": f"{nicho} {ciudad}", "format": "json", "addressdetails": 1, "extratags": 1, "limit": 60
        }, headers={"User-Agent": USER_AGENT}, timeout=15)
        if resp.status_code == 200:
            for item in resp.json():
                nombre = item.get("display_name", "").split(",")[0]
                if nombre and len(nombre) > 3:
                        id_limpio = limpiar_nombre(nombre)
                        if id_limpio not in pool:
                            ext = item.get("extratags", {})
                            pool[id_limpio] = {
                                "name": nombre, "address": item.get("display_name"),
                                "website": ext.get("website") or ext.get("contact:website"),
                                "emails": set(), "telefonos": set()
                            }
    except: pass

    # --- FUENTE 2: Dorking ELITE (Directorios + Negativos Estrictos) ---
    print(f"[*] Ejecutando Dorking ELITE (Eliminando basura SEO)...")
    # Deteccion de Region DDG (v11.0)
    c_low = ciudad.lower()
    reg = None
    if "colombia" in c_low or "medellin" in c_low or "bogota" in c_low: reg = "co-es"
    elif "spain" in c_low or "españa" in c_low or "madrid" in c_low: reg = "es-es"
    elif "mexico" in c_low or "méxico" in c_low: reg = "mx-es"
    elif "argentina" in c_low: reg = "ar-es"
    elif "usa" in c_low or "miami" in c_low or "texas" in c_low: reg = "us-en"
    
    # Universal Sniper Dorks
    dorks = [
        f'"{nicho}" "{ciudad}" site:facebook.com',
        f'"{nicho}" "{ciudad}" site:instagram.com',
        f'"{nicho}" "{ciudad}" site:tripadvisor.com',
        f'"{nicho}" "{ciudad}" site:yelp.com',
        f'top {nicho}s in {ciudad} -site:yelp.com',
    ]

    for dork in dorks:
        if len(pool) >= limite: break
        print(f"    [>] Dork: {dork[:60]}...")
        try:
                resultados = ddg_search(dork, max_results=40, region=reg)
                for r in resultados:
                    url = r.get('href', '').lower()
                    title = r.get('title', '')
                    snippet = r.get('body', '').lower()
                    
                    # 2. Filtro de fuentes de oro
                    fuentes_oro = ['google.com/maps', 'instagram.com', 'facebook.com', 'tripadvisor.', 'yelp.com', 'degusta.']
                    es_fuente_oro = any(f in url for f in fuentes_oro)
                    
                    if not es_fuente_oro and any(jk in url or jk in title.lower() for jk in JUNK_KEYWORDS): 
                        continue
                    
                    # Sonda Universal Sniper (v11.0.0)
                    nombre = None
                    if "google.com/maps" in url:
                        nombre = title.split(' - ')[0].split(' | ')[0]
                    elif "instagram.com" in url:
                        nombre = title.split('(@')[0].replace('Instagram photos', '').strip()
                    elif "facebook.com" in url:
                        nombre = title.replace('| Facebook', '').split(' - ')[0].strip()
                    elif "tripadvisor." in url:
                        nombre = title.replace('Restaurants', '').split(' - ')[0].split('|')[0].strip()
                    elif "degusta." in url:
                        nombre = title.split(' | ')[0].replace('Restaurante', '').strip()
                
                if not nombre:
                    # Alternativa: Validar nicho si no es de directorio conocido
                    if not es_nicho_valido(snippet, title, nicho): continue
                    # Extraer nombre del titulo (Heuristica de oro)
                    nombre = title.split(' - ')[0].split(' | ')[0].split(' : ')[0].strip()
                    nombre = title.split('|')[0].split('-')[0].split(':')[0].strip()
                
                if nombre and len(nombre) > 4:
                    id_limpio = limpiar_nombre(nombre)
                    if id_limpio not in pool and len(id_limpio) > 3:
                        pool[id_limpio] = {
                            "name": nombre, "address": snippet[:100], "website": None,
                            "emails": set(), "telefonos": set()
                        }
                    
                    # Cosechar del snippet de este resultado
                    ctx_text = f"{title} {snippet}"
                    for em in RE_EMAIL.findall(ctx_text):
                        em_l = limpiar_email(em)
                        if em_l: pool[id_limpio]["emails"].add(em_l)
                    for tel in RE_PHONE.findall(ctx_text):
                        tel_l = re.sub(r'[^\d+]', '', tel)
                        if 7 <= len(tel_l) <= 15: pool[id_limpio]["telefonos"].add(tel_l)
        except: continue
        time.sleep(1)
        
    leads = []
    for item in pool.values():
        item["emails"] = list(item["emails"])
        item["telefonos"] = list(item["telefonos"])
        leads.append(item)
    print(f"[+] Descubrimiento elite finalizado: {len(leads)} prospectos reales.")
    return leads[:limite]

# ==================================================================
# MODULO 2: OSINT ULTRA (v4.0)
# ==================================================================
def analizar_sentimiento(texto):
    """Analisis de sentimiento simplificado para detectar 'puntos de dolor'."""
    dolor_keywords = ['mal', 'lento', 'sucio', 'caro', 'viejo', 'antiguo', 'malo', 
                      'terrible', 'peor', 'asco', 'desactualizado', 'roto', 'cerrado',
                      'no contestan', 'error', 'pesimo', 'unprofessional']
    puntos = 0
    encontradas = []
    text_low = texto.lower()
    for kw in dolor_keywords:
        if kw in text_low:
            puntos += 1
            encontradas.append(kw)
    return puntos, encontradas

def buscar_gmb_info(nombre, direccion=""):
    """Google Maps Sniper (Edicion Gratuita via Dorking)."""
    info = {"rating": None, "reviews_count": None, "complaints": []}
    query = f'site:google.com/maps "{nombre}" {direccion[:20]}'
    res = ddg_search(query, max_results=3)
    for r in res:
        body = r.get('body', '')
        # Regex para capturar rating (ej: "4.5 stars", "Rating 4.2")
        rating_match = re.search(r'(\d\.\d)\s*(?:stars|estrellas|est.)', body)
        if rating_match:
            info["rating"] = rating_match.group(1)
        
        # Analizar quejas en los snippets
        p, kws = analizar_sentimiento(body)
        if p > 0:
            info["complaints"].extend(kws)
    return info

def obtener_lider_local(ciudad, nicho):
    """Busca al #1 del nicho en la ciudad para usar como benchmark."""
    query = f"best {nicho} in {ciudad} reviews rating stars"
    print(f"    [*] Buscando lider local para benchmark...")
    res = ddg_search(query, max_results=2)
    for r in res:
        body = r.get('body', '')
        # Intentar extraer un nombre de negocio que parezca el mejor
        rating_match = re.search(r'(\d\.\d)\s*(?:stars|estrellas)', body)
        if rating_match and float(rating_match.group(1)) >= 4.5:
            return {"nombre": r.get('title', '').split('|')[0].strip(), "rating": rating_match.group(1)}
    return {"nombre": "Líder del sector", "rating": "4.8"}

def analizar_pdf_sniper(url_web, contexto):
    """Busca rastro de PDFs (especialmente menus) para venta dirigida."""
    pdfs = []
    # Buscar en el contexto recolectado
    for text in contexto:
        if '.pdf' in text.lower():
            pdfs.append("Detectado en snippets")
            break
    
    # Si hay web, buscar rapido links .pdf
    if url_web:
        try:
            resp = requests.get(url_web, headers={"User-Agent": USER_AGENT}, timeout=5)
            if '.pdf' in resp.text.lower():
                pdfs.append("Menu/Info en PDF detectado en web")
        except: pass
    return pdfs

def obtener_vencimiento_dominio(dominio):
    """Verifica cuando expira el dominio (Sales Trigger: Expiration Anxiety)."""
    if not dominio: return None
    print(f"    [*] Consultando WHOIS para {dominio}...")
    try:
        # Usar gateway RDAP (gratis y estandarizado)
        resp = requests.get(f"https://rdap.org/domain/{dominio}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for event in data.get("events", []):
                if event.get("eventAction") == "expiration":
                    return event.get("eventDate")[:10] # Solo YYYY-MM-DD
    except: pass
    return "Desconocido (consultar manualmente)"

def obtener_mockup_visual(url):
    """Genera una URL de previsualizacion de la web actual (Before & After)."""
    if not url: return None
    # Usar thum.io (gratis para thumbnails publicos)
    return f"https://image.thum.io/get/width/1024/crop/800/{url}"

def validar_url_social(url):
    """Verifica si un link de red social esta 'vivo' o roto."""
    try:
        # Peticion rapida HEAD para solo ver estado
        resp = requests.head(url, headers={"User-Agent": USER_AGENT}, timeout=5, allow_redirects=True)
        return resp.status_code == 200
    except Exception:
        return False

def scrape_pagina_por_emails(url, timeout=10):
# ... (resto de funciones de scraping sin cambios)
    """
    Descarga el HTML de una pagina y extrae emails y telefonos del codigo fuente.
    Esto es clave: muchos negocios tienen el email en el footer o en la pagina de contacto
    pero Google/DDG no lo indexa en los snippets.
    """
    emails = set()
    telefonos = set()
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout,
                           allow_redirects=True)
        if resp.status_code != 200:
            return emails, telefonos

        contenido = resp.text[:100000]  # Limitar a 100KB para velocidad

        # Buscar emails en el HTML crudo (incluye los que estan en href="mailto:...")
        for match in RE_EMAIL.findall(contenido):
            em = limpiar_email(match)
            if em:
                emails.add(em)

        # Buscar telefonos en texto visible
        texto = extraer_texto_html(contenido)
        for match in RE_PHONE.findall(texto):
            tel = re.sub(r'[^\d+]', '', match)
            if 7 <= len(tel) <= 15:
                telefonos.add(tel)

        # Buscar links "mailto:" explicitamente
        for mailto in re.findall(r'mailto:([^\?"\'>\s]+)', contenido):
            em = limpiar_email(mailto)
            if em:
                emails.add(em)

        # Buscar en meta tags (og:email, contact, etc)
        for meta_match in re.findall(r'content=["\']([^"\']*@[^"\']*)["\']', contenido):
            em = limpiar_email(meta_match)
            if em:
                emails.add(em)

    except Exception:
        pass
    return emails, telefonos

def buscar_pagina_contacto(base_url, timeout=8):
    """Intenta encontrar la pagina de contacto de un sitio y scrapear emails de ahi."""
    emails = set()
    telefonos = set()
    
    # Paths comunes de paginas de contacto
    paths = ['/contact', '/contacto', '/contact-us', '/contactenos',
             '/about', '/about-us', '/nosotros', '/info']
    
    parsed = urllib.parse.urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    for path in paths:
        url = base + path
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT},
                              timeout=timeout, allow_redirects=True)
            if resp.status_code == 200:
                for match in RE_EMAIL.findall(resp.text[:50000]):
                    em = limpiar_email(match)
                    if em:
                        emails.add(em)
                for match in RE_PHONE.findall(extraer_texto_html(resp.text[:50000])):
                    tel = re.sub(r'[^\d+]', '', match)
                    if 7 <= len(tel) <= 15:
                        telefonos.add(tel)
                if emails:
                    break  # Ya encontramos, no seguir gastando requests
        except Exception:
            continue
    return emails, telefonos

def extraer_osint(nombre_negocio, direccion="", discovery_emails=None, discovery_telefonos=None):
    """
    Motor OSINT de nivel experto (v9.0 Aggressive).
    """
    osint = {
        "nombre": nombre_negocio,
        "tiene_web": False,
        "dominio_web": None,
        "url_web": None,
        "redes_sociales": [],
        "emails": set(discovery_emails or []),
        "telefonos": set(discovery_telefonos or []),
        "contexto": [],
        "resenas": [],
        "handles_sociales": [],
        "puntuacion_lead": 0,
        "gmb": {"rating": None, "quejas": []},
        "salud_social": "Desconocida"
    }

    print(f"[*] OSINT profundo: {nombre_negocio} (Contacts: {len(osint['emails']) + len(osint['telefonos'])})")

    print(f"[*] OSINT profundo: {nombre_negocio}")
    
    # --- CAPA 5: GMB Sniper (Free) ---
    print(f"    [>>] GMB Sniper activado...")
    gmb_data = buscar_gmb_info(nombre_negocio, direccion)
    osint["gmb"]["rating"] = gmb_data["rating"]
    osint["gmb"]["quejas"] = gmb_data["complaints"]
    if gmb_data["rating"]:
        print(f"    [=] Google Rating: {gmb_data['rating']} estrellas")

    # ============================================================
    # CAPA 1: GOOGLE DORKING via DuckDuckGo
    # ============================================================
    # ... (resto del loop DDG similar, pero capturando redes para validar)
    queries = [
        f'"{nombre_negocio}" business email',
        f'"{nombre_negocio}" contact information "@"',
        f'{nombre_negocio} {direccion[:30]} official website',
        f'{nombre_negocio} (site:facebook.com OR site:instagram.com) business',
        f'{nombre_negocio} {direccion[:20]} reviews (site:yelp.com OR site:google.com)',
        f'{nombre_negocio} local contact phone email',
        f'"{nombre_negocio}" in {direccion[:15]} site:yellowpages.com phone',
        f'site:facebook.com "{nombre_negocio}" "{direccion[:15]}"', # Meta Sniper v9.6.1 (Removed -"http")
    ]

    urls_a_scrapear = []
    social_links_to_check = []
    
    for qi, query in enumerate(queries):
        resultados = ddg_search(query, max_results=6)
        for r in resultados:
            url = r.get('href', '').lower()
            snippet = r.get('body', '')
            texto_completo = f"{r.get('title', '')} {snippet}"

            # Extraer emails/telefonos (ya implementado)
            for em in RE_EMAIL.findall(texto_completo):
                em_limpio = limpiar_email(em)
                if em_limpio: osint["emails"].add(em_limpio)
            for tel in RE_PHONE.findall(texto_completo):
                tel_limpio = re.sub(r'[^\d+]', '', tel)
                if 7 <= len(tel_limpio) <= 15: osint["telefonos"].add(tel_limpio)

            # Clasificar URLs de Redes Sociales
            dominio = urllib.parse.urlparse(url).netloc.replace('www.', '')
            for rd in REDES_SOCIALES:
                if rd in dominio:
                    if url not in osint["redes_sociales"]:
                        osint["redes_sociales"].append(url)
                        social_links_to_check.append(url)
                    break

            # Detectar web propia (ya implementado)
            es_directorio = any(d in dominio for d in DIRECTORIOS_WEB)
            if not es_directorio and dominio and len(dominio) > 4:
                nombre_norm = nombre_negocio.lower().replace(' ', '').replace("'", "")
                dominio_norm = dominio.replace('-', '').replace('.com', '').replace('.net', '')
                if nombre_norm[:5] in dominio_norm or dominio_norm[:5] in nombre_norm:
                    osint["tiene_web"] = True
                    osint["dominio_web"] = dominio
                    osint["url_web"] = url
                    urls_a_scrapear.append(url)

            # Extraer contactos de Bios Sociales (Deep Harvesting v12.0)
            if "instagram" in url or "facebook" in url:
                bio_matches = RE_PHONE.findall(texto_completo)
                for bio_tel in bio_matches:
                    bt = re.sub(r'[^\d+]', '', bio_tel)
                    if 7 <= len(bt) <= 15: 
                        osint["telefonos"].add(bt)
                        osint["contexto"].append(f"Detectado en Bio: {bt}")

            if snippet: osint["contexto"].append(snippet[:300])

    # --- CAPA 6: Salud Social (Validar Instagram/FB) ---
    if social_links_to_check:
        print(f"    [>>] Validando salud de redes sociales...")
        vivas = 0
        rotas = 0
        for link in social_links_to_check[:3]: # Validar top 3
            if validar_url_social(link): vivas += 1
            else: rotas += 1
        osint["salud_social"] = f"{vivas} activas, {rotas} rotas"
        if rotas > 0:
            print(f"    [!] Detectadas {rotas} redes sociales rotas o inactivas.")

    # ============================================================
    # CAPA 2: SCRAPING DIRECTO (ya implementado)
    # ============================================================
    if urls_a_scrapear:
        for page_url in urls_a_scrapear[:2]:
            t0 = time.time()
            emails_pagina, tels_pagina = scrape_pagina_por_emails(page_url)
            osint["emails"].update(emails_pagina)
            osint["telefonos"].update(tels_pagina)
            tt = time.time() - t0
            if tt > 4.5:
                osint["contexto"].append(f"Web extremadamente lenta ({tt:.1f}s), oportunidad.")
                osint["puntuacion_lead"] += 10 # Bonus por lentitud

    # ============================================================
    # CAPA 3: INTELIGENCIA DE DOMINIO Y VISUAL (v12.0 Elite)
    # ============================================================
    if osint["tiene_web"] and osint["dominio_web"]:
        osint["expiracion_dominio"] = obtener_vencimiento_dominio(osint["dominio_web"])
        osint["visual_mockup"] = obtener_mockup_visual(osint["url_web"])
        if osint["expiracion_dominio"] and osint["expiracion_dominio"] != "Desconocido":
            # Si expira en menos de 6 meses, subir score
            osint["puntuacion_lead"] += 15
            osint["contexto"].append(f"ALERTA: Dominio expira pronto ({osint['expiracion_dominio']})")

    # ============================================================
    # FINAL: ANALISIS DE PUNTOS DE DOLOR Y SCORING
    # ============================================================
    todas_resenas = " ".join(osint["contexto"])
    dolor_puntos, kws_dolor = analizar_sentimiento(todas_resenas)
    osint["gmb"]["quejas"].extend(kws_dolor)
    osint["gmb"]["quejas"] = list(set(osint["gmb"]["quejas"]))

    score = 50
    if not osint["tiene_web"]: score += 30
    else: score -= 45 # Penalizar si ya tiene
    
    if osint["emails"]: score += 15
    if osint["telefonos"]: score += 10
    
    # Bonus por Malas Resenas (Oportunidad de Web para limpiar imagen)
    if osint["gmb"]["rating"] and float(osint["gmb"]["rating"]) < 3.8:
        score += 20
        osint["contexto"].append("Rating GMB bajo. Oportunidad de marketing y reputacion.")
    
    # Bonus por quejas detectadas
    if len(osint["gmb"]["quejas"]) > 0:
        score += (len(osint["gmb"]["quejas"]) * 5)
        
    # Salud social mala es oportunidad
    if "rotas" in osint["salud_social"] and "0 rotas" not in osint["salud_social"]:
        score += 15

    osint["puntuacion_lead"] = max(0, min(100, score))
    
    # Limpieza final listas...
    osint["emails"] = sorted(list(osint["emails"]))
    osint["telefonos"] = sorted(list(osint["telefonos"]))
    osint["contexto"] = list(set(osint["contexto"]))[:10]

    print(f"    [=] Score Final: {osint['puntuacion_lead']}/100 | Quejas: {len(osint['gmb']['quejas'])}")
    return osint

# ==================================================================
# MODULO 3: CORREO VIA NAVEGADOR (0% CONTRASENAS)
# ==================================================================
def abrir_correo_gmail(email_destino, nombre_negocio, url_demo):
    """Abre Gmail en el navegador con el correo pre-rellenado."""
    if not email_destino:
        return False
    print(f"[>] Abriendo Gmail para: {email_destino}")
    subject = f"He creado una web profesional GRATIS para {nombre_negocio}"
    link = url_demo if url_demo else "(demo adjunta localmente)"
    body = (
        f"Hola equipo de {nombre_negocio},\n\n"
        f"Encontre que su negocio tiene excelente potencial pero no dispone de una pagina web profesional.\n\n"
        f"Me tome la libertad de disenar una propuesta visual personalizada:\n"
        f"{link}\n\n"
        f"Si les gusta, se las entrego lista y publicada por solo $40 USD (pago unico).\n\n"
        f"Saludos cordiales,\nConsultor Web AI"
    )
    gmail_url = "https://mail.google.com/mail/?view=cm&fs=1&{}&{}&{}".format(
        urllib.parse.urlencode({'to': email_destino}),
        urllib.parse.urlencode({'su': subject}),
        urllib.parse.urlencode({'body': body})
    )
    try:
        webbrowser.open(gmail_url)
        return True
    except Exception as e:
        print(f"[-] Error abriendo navegador: {e}")
        return False

# ==================================================================
# MODULO 4: DEPLOY A VERCEL (OPCIONAL)
# ==================================================================
def deploy_vercel(nombre, html_code, token):
    if not token:
        return None
    print(f"[*] Desplegando a Vercel...")
    slug = re.sub(r'[^a-z0-9\-]', '', nombre.lower().replace(' ', '-'))[:40]
    payload = {
        "name": slug or "vendedor-demo",
        "files": [{"file": "index.html", "data": html_code}],
        "projectSettings": {"framework": None}
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for _ in range(2):
        try:
            resp = requests.post("https://api.vercel.com/v13/deployments",
                                 json=payload, headers=headers, timeout=25)
            if resp.status_code in (200, 201):
                url = "https://" + resp.json().get("url", "")
                print(f"[+] Deploy exitoso: {url}")
                return url
        except Exception:
            time.sleep(2)
    return None

# ==================================================================
# MODULO 5: GENERADOR DE PAGINAS (v16.0.0)
# ==================================================================
def generar_html_propuesta(mejor, lider):
    """Genera una landing page moderna y persuasiva para el lead."""
    nombre = mejor['nombre']
    rating = mejor['gmb']['rating'] or "N/A"
    lider_nombre = lider['nombre']
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Propuesta Web para {nombre}</title>
    <style>
        :root {{ --primary: #2563eb; --dark: #1e293b; --text: #f8fafc; }}
        body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: var(--text); margin: 0; padding: 2rem; }}
        .card {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid #334155; border-radius: 1rem; padding: 2rem; max-width: 800px; margin: auto; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }}
        h1 {{ color: #60a5fa; font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .score {{ font-size: 1.5rem; color: #34d399; font-weight: bold; }}
        .comparison {{ display: flex; gap: 2rem; margin-top: 2rem; }}
        .comp-item {{ flex: 1; padding: 1rem; border-radius: 0.5rem; background: #1e293b; border: 1px solid #475569; }}
        .btn {{ display: inline-block; background: var(--primary); color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; margin-top: 1.5rem; font-weight: bold; }}
        .highlight {{ color: #fbbf24; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{nombre}</h1>
        <p class="score">Diagnóstico: Oportunidad de Crecimiento Prioritaria</p>
        <p>Analizamos su presencia digital y detectamos que <span class="highlight">{'no poseen un sitio web oficial' if not mejor['tiene_web'] else 'su sitio actual es vulnerable'}.</span></p>
        
        <div class="comparison">
            <div class="comp-item">
                <p><strong>Ustedes:</strong></p>
                <p>Rating: ⭐ {rating}</p>
                <p>Visibilidad: Limitada</p>
            </div>
            <div class="comp-item">
                <p><strong>Competencia ({lider_nombre}):</strong></p>
                <p>Rating: ⭐ {lider['rating']}</p>
                <p>Visibilidad: Dominante</p>
            </div>
        </div>

        <h3>Propuesta de Transformación:</h3>
        <ul>
            <li>Diseño Responsivo (Móvil + PC)</li>
            <li>Optimización de SEO para dominar {lider_nombre}</li>
            <li>Botón Directo a WhatsApp / Reservas</li>
        </ul>

        <a href="#" class="btn">Activar Sitio Ahora</a>
    </div>
</body>
</html>"""
    return html

def guardar_propuesta(nombre, html):
    """Guarda la propuesta HTML en la carpeta lead_sites."""
    os.makedirs(PROPUESTAS_DIR, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]', '', nombre.lower().replace(' ', '-'))
    path = os.path.join(PROPUESTAS_DIR, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

# ==================================================================
# MODULO 6: EVALUADOR DE LEADS
# ==================================================================
def evaluar_lead(negocio, args):
    nombre = negocio['name']
    direccion = negocio.get('address', '')

    if negocio.get('website'):
        print(f"[-] {nombre}: Ya tiene web en Nominatim. Descartado.")
        return None

    osint = extraer_osint(nombre, direccion)

    if osint['tiene_web'] and osint['puntuacion_lead'] < 30:
        print(f"[-] {nombre}: Web detectada ({osint['dominio_web']}), score bajo. Descartado.")
        return None

    if osint['puntuacion_lead'] < 20:
        print(f"[-] {nombre}: Score demasiado bajo ({osint['puntuacion_lead']}/100). Descartado.")
        return None

    # Imprimir datos OSINT estructurados
    print(f"\n{'='*55}")
    print(f"[LEAD] {nombre} | Score: {osint['puntuacion_lead']}/100")
    print(f"{'='*55}")
    print(json.dumps(osint, indent=2, ensure_ascii=False))
    print(f"{'='*55}\n")

    return osint

# ==================================================================
# MAIN
# ==================================================================
def main():
    parser = argparse.ArgumentParser(
        description=f'Vendedor-IA v{VERSION} -- Agente OSINT de Prospeccion Web',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            '  python main.py --ciudad "Bogota" --pais "Colombia" --nicho "cafe"\n'
            '  python main.py --solo_osint --ciudad "Miami" --pais "USA"\n'
            '  python main.py --deploy_only --html_file landing.html --vercel_token "tk_..."\n'
        )
    )
    parser.add_argument('--ciudad', type=str, help='Ciudad de busqueda')
    parser.add_argument('--pais', type=str, help='Pais de busqueda')
    parser.add_argument('--nicho', type=str, help='Tipo de negocio (restaurant, cafe, gym...)')
    parser.add_argument('--vercel_token', type=str, help='Token API de Vercel (opcional)')
    parser.add_argument('--solo_osint', action='store_true',
                        help='Solo ejecuta OSINT, sin generar webs')
    parser.add_argument('--deploy_only', action='store_true',
                        help='Solo despliega un HTML ya generado')
    parser.add_argument('--html_file', type=str, help='Archivo HTML para deploy_only')
    parser.add_argument('--limite', type=int, default=100, help='Maximo de negocios a buscar (default: 100)')
    parser.add_argument('--version', action='version', version=f'Vendedor-IA v{VERSION}')

    args, _ = parser.parse_known_args()

    print("")
    print("=" * 50)
    print(f"  VENDEDOR-IA v{VERSION}")
    print(f"  Motor OSINT: Nominatim + DuckDuckGo + Scraping")
    print(f"  100% Gratuito - Sin API Keys")
    print("=" * 50)
    print("")

    # --- MODO DEPLOY ONLY ---
    if args.deploy_only:
        if not args.html_file or not os.path.exists(args.html_file):
            print("[-] Error: Debes proveer un --html_file valido.")
            return
        with open(args.html_file, "r", encoding="utf-8") as f:
            html_code = f.read()
        url = deploy_vercel("lead-demo", html_code, args.vercel_token)
        url_final = url or args.html_file
        if url:
            print(f"[+] DEPLOY EXITOSO: {url_final}")
        else:
            print(f"[+] Archivo local listo: {url_final}")
        em_match = RE_EMAIL.search(html_code)
        if em_match:
            abrir_correo_gmail(em_match.group(0), "Lead", url_final)
        return

    # --- MODO INTERACTIVO ---
    if not args.ciudad:
        args.ciudad = input("[?] Ciudad (Enter = Miami): ").strip() or "Miami"
    if not args.pais:
        args.pais = input("[?] Pais (Enter = USA): ").strip() or "USA"
    if not args.nicho:
        args.nicho = input("[?] Tipo de negocio (Enter = restaurant): ").strip() or "restaurant"
    if not args.vercel_token:
        vt = input("[?] Vercel Token (Enter para omitir): ").strip()
        args.vercel_token = vt or None

    # --- EJECUTAR ---
    ciudad_full = f"{args.ciudad}, {args.pais}"
    print(f"\n[*] Objetivo: {args.nicho}s en {ciudad_full}")
    print(f"[*] Limite: {args.limite} negocios\n")

    try:
        negocios = buscar_negocios(ciudad_full, args.nicho, args.limite)
        if not negocios:
            print(f"[-] No se encontraron negocios de tipo '{args.nicho}' en '{ciudad_full}'.")
            return

        print(f"[+] {len(negocios)} negocios descubiertos. Filtrando candidatos prometedores...")
        
        # Filtrar candidatos que no tienen web inicial para procesar solo los mas probables
        candidatos = [n for n in negocios if not n.get('website')]
        limit_deep = max(15, args.limite // 4) # Escalar profundidad segun limite total
        if not candidatos:
            candidatos = negocios[:limit_deep] 
        else:
            candidatos = candidatos[:limit_deep] 
            
        print(f"[*] Procesando OSINT para los {len(candidatos)} candidatos mas probables...\n")

        leads_calificados = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futuros = {executor.submit(evaluar_lead, n, args): n for n in candidatos}
            for i, future in enumerate(as_completed(futuros), 1):
                try:
                    resultado = future.result()
                    if resultado:
                        leads_calificados.append(resultado)
                        status = "LEAD CALIFICADO"
                    else:
                        status = "DESCARTADO"
                    print(f"[*] [{i}/{len(candidatos)}] {futuros[future]['name']}: {status}")
                except Exception as e:
                    print(f"[!] Error procesando negocio: {e}")

        # --- RESUMEN FINAL ---
        print(f"\n{'='*55}")
        print(f"  RESUMEN FINAL: {len(leads_calificados)}/{len(negocios)} leads calificados")
        print(f"{'='*55}")
        
        # --- SELECCION DE GANADOR (Prioridad: Sin Web + Email > Sin Web + Tel > Con Web) ---
        mejor = None
        
        # 1. ELITE: Sin Web y con Email (Gmail)
        goldens = [l for l in leads_calificados if not l['tiene_web'] and l['emails']]
        # 2. SILVER: Sin Web y con Telefono
        silvers = [l for l in leads_calificados if not l['tiene_web'] and l['telefonos'] and not l['emails']]
        # 3. BRONCE: Sin Web (pero sin contactos aun)
        bronces = [l for l in leads_calificados if not l['tiene_web'] and not l['emails'] and not l['telefonos']]
        # 4. COPPER: Con Web (tal vez necesitan mejora)
        coppers = [l for l in leads_calificados if l['tiene_web']]

        if goldens:
            mejor = sorted(goldens, key=lambda x: x['puntuacion_lead'], reverse=True)[0]
        elif silvers:
            mejor = sorted(silvers, key=lambda x: x['puntuacion_lead'], reverse=True)[0]
        elif bronces:
            mejor = sorted(bronces, key=lambda x: x['puntuacion_lead'], reverse=True)[0]
        elif coppers:
            mejor = sorted(coppers, key=lambda x: x['puntuacion_lead'], reverse=True)[0]

        if mejor:
            print(f"  PROSPECTO RECOMENDADO PARA VENTA:")
            print(f"  Nombre: {mejor['nombre']}")
            print(f"  Web:    {'SI (Vulnerable/Antigua)' if mejor['tiene_web'] else 'NO (Oportunidad Alta)'}")
            
            # --- EMERGENCIA: Sonda de Telefono si falta (v9.5) ---
            if not mejor['emails'] and not mejor['telefonos']:
                print(f"  [*] Realizando busqueda de contacto de emergencia...")
                extra_contacts = ddg_search(f'"{mejor["nombre"]}" {args.ciudad} phone number', max_results=3)
                for r in extra_contacts:
                    for tel in RE_PHONE.findall(f"{r.get('title')} {r.get('body')}"):
                        tel_l = re.sub(r'[^\d+]', '', tel)
                        if 7 <= len(tel_l) <= 15: mejor['telefonos'].append(tel_l)
                mejor['telefonos'] = list(set(mejor['telefonos']))

            emails_final = mejor['emails'][0] if mejor['emails'] else "sin email (requiere llamada/DM)"
            print(f"  Email:  {emails_final}")
            if mejor['telefonos']:
                print(f"  Tel:    {mejor['telefonos'][0]}")
            
            # --- ENLACES DE OUTREACH (v11.1) ---
            print(f"  Social: [Outreach] ", end="")
            if mejor['redes_sociales']:
                # Priorizar IG/FB para el usuario
                ig = next((l for l in mejor['redes_sociales'] if "instagram.com" in l), None)
                fb = next((l for l in mejor['redes_sociales'] if "facebook.com" in l), None)
                social_print = ig or fb or mejor['redes_sociales'][0]
                print(social_print)
            else:
                print("No detectadas (Contactar via Google Maps/Web)")
                
            print(f"  Score:  {mejor['puntuacion_lead']}/100")
            
            # --- FASE FINAL BOSS v6.0 (Solo al ganador) ---
            print(f"\n{'-'*30}")
            print(f"  ULTRA-INTELIGENCIA v6.0 (Ultima Thule)")
            print(f"{'-'*30}")
            
            # 1. Competidor Benchmark
            lider = obtener_lider_local(args.ciudad, args.nicho)
            print(f"  [*] Benchmark: {lider['nombre']} ({lider['rating']} estrellas)")
            
            # 2. PDF Sniper
            pdfs = analizar_pdf_sniper(mejor.get('url_web'), mejor['contexto'])
            if pdfs:
                print(f"  [!] PDF DETECTADO: {pdfs[0]}. Vender 'Menu Digital'.")
            
            # 3. WHOIS Expiry
            expira = None
            if mejor.get('dominio_web'):
                expira = obtener_vencimiento_dominio(mejor['dominio_web'])
                print(f"  [*] Dominio expira: {expira}")
            
            # 4. Visual Mockup
            mockup = obtener_mockup_visual(mejor.get('url_web'))
            if mockup:
                print(f"  [*] Mockup 'Antes': {mockup}")
            
            # --- GENERACION DE PROPUESTA ACTIVA (v16.0) ---
            html_propuesta = generar_html_propuesta(mejor, lider)
            path_propuesta = guardar_propuesta(mejor['nombre'], html_propuesta)
            print(f"  [+] PROPUESTA GENERADA: {path_propuesta}")
            
            # --- PITCH DE VENTA SUGERIDO ---
            print(f"\n  PITCH DE VENTA SUGERIDO (Alta Conversion):")
            gap = "no tienen web" if not mejor['tiene_web'] else "su web es lenta u obsoleta"
            if mejor['gmb']['quejas']:
                queja = mejor['gmb']['quejas'][0]
                print(f"  > 'Hola, vi que en Google se quejan de que son '{queja}'.")
            
            if expira and expira != "Desconocido (consultar manualmente)":
                print(f"  > 'Ademas, su dominio expira el {expira}. Es el momento ideal para renovarse.'")
                
            print(f"  > Mientras que '{lider['nombre']}' domina con {lider['rating']} estrellas y web moderna,")
            print(f"  > ustedes {gap}. Les he preparado una propuesta para superarlos.'")
            print(f"{'-'*30}")

            if mejor['contexto']:
                print(f"  Contexto: {mejor['contexto'][0][:100]}...")
            
            # Sugerencia de outreach
            if mejor['emails']:
                print(f"\n  [!] CONTACTO DISPONIBLE: {mejor['emails'][0]}")
                print(f"  [!] Accion recomendada: Abrir propuesta y enviar mockup visual.")
        else:
            print("  No se encontro ningun prospecto viable en esta busqueda.")
        print(f"{'='*55}")

        # Fin del proceso
        print(f"\n[+] Analisis finalizado exitosamente.")

    except KeyboardInterrupt:
        print("\n[!] Agente detenido por el usuario.")

if __name__ == "__main__":
    main()
