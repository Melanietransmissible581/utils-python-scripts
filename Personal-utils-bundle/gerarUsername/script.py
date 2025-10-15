#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerador de Username usando API do Gemini
Script simples para terminal - KISS principle
"""

import os
from google import genai
from google.genai import types    
import sys

# Verificar se a chave da API está configurada
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ ERRO: Variável GEMINI_API_KEY não encontrada!")
    print("Configure com: export GEMINI_API_KEY='sua_chave_aqui'")
    sys.exit(1)

# Configurar cliente com a chave
client = genai.Client(api_key=api_key)
model = "gemini-2.5-flash"


def menuInicial():
    """Mostra menu e pega a opção do usuário"""
    print("--- GERADOR DE USERNAME (COM IA!) ---")
    print()
    print("1. Com nome base")
    print("2. Com nome aleatório")
    print()

    while True:
        escolha = input("Escolha uma opção (1 ou 2):").strip()

        if escolha == "1":
            return 1
        if escolha == "2":
            return 2
        else:
            print("Opção inválida. Tente 1 ou 2")
            print()

def pegaNome():
    """Pega o nome que o usário escolheu"""
    while True:
        nome = input("Qual o nome?").strip()

        if nome:
            return nome
        else:
            print("Nome não pode estar vazio!!")
            

def promptGemini(tipo, nome=None):
    """Gera o prompt para o gemini baseado na escolha"""

    if tipo == 1:
        prompt = f"""Gere um username criativo e estiloso baseado no nome '{nome}'.
        Inclua símbolos especiais, números e letras variadas.
        Deve ser único e memóravel.
        
        Exemplos de simbolos:
          '<>', '[]', '()', '=>', '::', '++', '--', '&&', '||',
          '#', '$', '%', '^', '&', '*', '`', '~', '!', '?',
          '//', '/*', '*/', 'λ', 'Σ', 'Π', '∆', '∫', 'ƒ', '∞',
          '☣', '☢', '💀', '☠', 'root@'.
        
        Exemplo de letras variadas:
        Z '⅄ 'X 'M 'Λ '∩ '⊥ 'S 'ᴚ 'Q 'Ԁ 'O 'N 'W '˥ 'K 'ſ 'I 'H '⅁ 'Ⅎ 'Ǝ 'ᗡ 'Ɔ 'ᙠ '∀
        🅰, 🅱, 🅲, 🅳, 🅴, 🅵, 🅶, 🅷, 🅸, 🅹, 🅺, 🅻, 🅼, 🅽, 🅾, 🅿, 🆀, 🆁, 🆂, 🆃, 🆄, 🆅, 🆆, 🆇, 🆈, 🆉

        Exemplo de trabalho:
        nome = montezuma
        Você DEVE embaralhar (mon/te/zu/ma):
        temazumon
        Você DEVE adicionar letras variadas:
        𝖒𝖔𝖓𝖙𝖊𝖟𝖚𝖒𝖆
        Você DEVE incluir símbolos:
        monλezu<>

        resultado:
        "::t3zu_mαn0n::", "λ(𝖟𝖚𝖒𝖆)++𝖒𝖔𝖓𝖙𝖊", "root@m0n_zμmΔ!", "Σ(∀zμmøntem)∞","ɱαzυ => ʍɔnʇǝ"

        VOCÊ DEVE ME DEVOLVER APENAS O USERNAME GERADO E NADA MAIS"""
    
    else:
        prompt = """Gere um username completamente aleatório e estiloso.
        Inclua símbolos especiais, números e letras variadas.
        Deve ser único, criativo e ter entre 8-15 caracteres.
        Pode ser inspirado em palavras cool, tecnologia, gaming, etc.
        
        VOCÊ DEVE ME DEVOLVER APENAS O USERNAME GERADO E NADA MAIS"""
    
    return prompt

def chamarGemini(prompt):
    """Chama a API"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )

        username = response.text.strip()
        return username

    except Exception as e:
        print(f"Erro ao chamar API: {e}")
        return None

def exibirResultado(username):
    """Mostra o username"""

    if username:
        print("\n" + "="*40)
        print(f"Username gerado: {username}")
        print("="*40 + "\n")
    else:
        print("Não foi possivel gerar username")

    while True:
        continuar = input("Gerar outro? (s/n): ").strip().lower()

        if continuar in ['s', 'sim', 'y', 'yes']:
            return True
        elif continuar in ['n', 'nao', 'não', 'no']:
            return False
        else:
            print("Digite sim ou nao")




# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que conecta todas as funcionalidades"""
    
    print("🚀 Bem-vindo ao Gerador de Username com IA!")
    print()
    
    while True:
        try:
            # 1. Mostrar menu e capturar opção
            opcao = menuInicial()
            
            # 2. Capturar nome base se necessário
            if opcao == 1:
                nome = pegaNome()
            else:
                nome = None
                
            # 3. Gerar prompt apropriado
            prompt = promptGemini(opcao, nome)
            
            # 4. Chamar API do Gemini
            print("⏳ Gerando username com IA...")
            username = chamarGemini(prompt)
            
            # 5. Exibir resultado e perguntar se continua
            if not exibirResultado(username):
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrompido pelo usuário!")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            continuar = input("Tentar novamente? (s/n): ").strip().lower()
            if continuar not in ['s', 'sim', 'y', 'yes']:
                break
    
    print("👋 Obrigado por usar o gerador! Até mais!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
