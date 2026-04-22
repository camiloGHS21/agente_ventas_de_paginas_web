#!/usr/bin/env python3
import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

# Relajar la validación de scopes para evitar errores por 'openid'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Configuración
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config_auth.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

# Permisos requeridos
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/business.manage' # Para futuras integraciones social/GMB
]

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CONFIG_PATH):
                print(f"[!] Error: No se encuentra {CONFIG_PATH}")
                return None
            
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            # Crear el formato que Google espera
            client_config = {
                "installed": {
                    "client_id": config["google"]["client_id"],
                    "client_secret": config["google"]["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

def send_email(to, subject, body):
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        send_message = service.users().messages().send(
            userId="me",
            body={'raw': raw_message}
        ).execute()
        
        print(f"[+] Correo enviado exitosamente (ID: {send_message['id']})")
        return True
    except Exception as e:
        print(f"[-] Error enviando correo: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Google OAuth Utility for Agents")
    parser.add_argument("--login", action="store_true", help="Forzar login inicial")
    parser.add_argument("--send_email", nargs=3, metavar=('TO', 'SUBJECT', 'BODY'), help="Enviar un correo")
    
    args = parser.parse_args()
    
    if args.login:
        creds = get_credentials()
        if creds: print("[+] Login exitoso.")
    
    if args.send_email:
        send_email(args.send_email[0], args.send_email[1], args.send_email[2])
