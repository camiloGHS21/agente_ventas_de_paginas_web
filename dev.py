#!/usr/bin/env python3
"""
DEV-ENGINE v1.0 - Investigador de Viabilidad de Ideas
Motor: DuckDuckGo Search
"""
import sys
import argparse
import time
from duckduckgo_search import DDGS

def investigar_idea(idea):
    print(f"\n[?] INVESTIGANDO IDEA: {idea}")
    print("-" * 50)
    
    with DDGS() as ddgs:
        # 1. Buscar competencia
        print("[*] Buscando competencia existente...")
        results = ddgs.text(f"competitors for {idea}", max_results=5)
        for r in results:
            print(f"  - {r['title']}\n    {r['href']}")
        
        # 2. Buscar tendencias de mercado
        print("\n[*] Analizando tendencias y viabilidad...")
        trends = ddgs.text(f"market viability and trends for {idea}", max_results=5)
        for r in trends:
            print(f"  - {r['body'][:200]}...")
            
    print("\n[!] INVESTIGACIÓN FINALIZADA.")
    print("AI Agent: Ahora analiza estos datos para definir la arquitectura. project complete.")

def main():
    parser = argparse.ArgumentParser(description='Investigador de Ideas Dev')
    parser.add_argument('--idea', type=str, required=True, help='La propuesta/idea a investigar')
    args = parser.parse_args()
    investigar_idea(args.idea)

if __name__ == "__main__":
    main()
