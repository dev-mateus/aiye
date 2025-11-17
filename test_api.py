#!/usr/bin/env python3
"""
Script de teste para a API Umbanda QA

Uso:
    python test_api.py

Requisitos:
    - Backend rodando em http://localhost:8000
    - requests library: pip install requests
"""

import requests
import json
import time
from typing import Optional

API_URL = "http://localhost:8000"


def test_health() -> bool:
    """Testa health check do backend"""
    try:
        response = requests.get(f"{API_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está online!")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao backend em http://localhost:8000")
        print("   Certifique-se que uvicorn está rodando:")
        print("   uvicorn backend.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar saúde: {e}")
        return False


def test_ask(question: str, verbose: bool = False) -> Optional[dict]:
    """Testa endpoint /ask"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📝 Pergunta: {question}")
            print(f"⏱️  Latência: {elapsed:.2f}s")
            print(f"📊 Status: OK")
            
            if verbose:
                print(f"\n💬 Resposta:")
                print(f"   {data['answer'][:200]}...")
                print(f"\n📚 Fontes ({len(data['sources'])} found):")
                for src in data['sources']:
                    print(f"   - {src['title']} (pág. {src['page_start']}-{src['page_end']})")
                print(f"\n🔍 Meta:")
                for k, v in data['meta'].items():
                    print(f"   {k}: {v}")
            
            return data
        
        elif response.status_code == 400:
            error = response.json()
            print(f"❌ Erro 400: {error.get('detail', 'Bad request')}")
            return None
        
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout ao questionar: {question}")
        return None
    except Exception as e:
        print(f"❌ Erro ao questionar: {e}")
        return None


def test_invalid_question():
    """Testa pergunta inválida"""
    print("\n" + "="*70)
    print("Teste 4: Pergunta inválida (< 3 caracteres)")
    print("="*70)
    test_ask("Oi")  # Deve falhar


def main():
    """Suite de testes"""
    print("\n" + "="*70)
    print("🧪 TESTE DA API UMBANDA QA")
    print("="*70)
    
    # Teste 1: Health check
    print("\n" + "="*70)
    print("Teste 1: Health Check")
    print("="*70)
    if not test_health():
        print("\n⚠️  Backend não está disponível. Abortar testes.")
        return
    
    # Teste 2: Pergunta simples (sem PDFs)
    print("\n" + "="*70)
    print("Teste 2: Pergunta sem PDFs (resultado vazio)")
    print("="*70)
    test_ask("O que é Umbanda?", verbose=True)
    
    # Teste 3: Múltiplas perguntas
    print("\n" + "="*70)
    print("Teste 3: Múltiplas perguntas")
    print("="*70)
    questions = [
        "Quem são os Orixás?",
        "Como é uma sessão de Umbanda?",
        "Qual a diferença entre Umbanda e Candomblé?",
    ]
    
    for q in questions:
        test_ask(q)
        time.sleep(0.5)  # Pequeno delay entre requisições
    
    # Teste 4: Pergunta inválida
    test_invalid_question()
    
    # Resumo
    print("\n" + "="*70)
    print("✅ TESTES CONCLUÍDOS")
    print("="*70)
    print("\nPróximos passos:")
    print("1. Colocar PDFs em backend/data/pdfs/")
    print("2. Executar: python backend/ingest.py")
    print("3. Testar novamente com PDFs ingeridos")
    print("4. Abrir frontend em http://localhost:5173")


if __name__ == "__main__":
    main()
