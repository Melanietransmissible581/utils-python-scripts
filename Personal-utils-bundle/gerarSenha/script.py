#!/usr/bin/env python3
import random
import string
import argparse

def gerar_senha(tamanho=12, incluir_simbolos=True):
    """Gera uma senha aleatória"""
    caracteres = string.ascii_letters + string.digits
    
    if incluir_simbolos:
        caracteres += "!@#$%&*"
    
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return senha

def main():
    parser = argparse.ArgumentParser(description='Gerador de senhas aleatórias')
    parser.add_argument('-tamanho', '--tamanho', type=int, default=12, 
                       help='Tamanho da senha (padrão: 12)')
    parser.add_argument('-quantidade', '--quantidade', type=int, default=1,
                       help='Quantidade de senhas (padrão: 1)')
    parser.add_argument('-sem_simbolo', '--sem-simbolos', action='store_true',
                       help='Não incluir símbolos especiais')
    
    args = parser.parse_args()
    
    print(f"Gerando {args.quantidade} senha(s) de {args.tamanho} caracteres:")
    print("-" * 50)
    
    for i in range(args.quantidade):
        senha = gerar_senha(args.tamanho, not args.sem_simbolos)
        print(f"Senha {i+1}: {senha}")

if __name__ == "__main__":
    main()
