#!/usr/bin/env python3
"""
SCRIPT DE LIMPEZA DO SISTEMA
============================

Este script limpa arquivos desnecessários do sistema, node_modules antigos,
caches e arquivos temporários para liberar espaço em disco.

COMO USAR:
----------
1. Execução básica (modo seguro - apenas mostra o que seria removido):
   python3 sisclean

2. Execução com limpeza real:
   python3 sisclean --ex

3. Limpeza apenas de node_modules:
   python3 sisclean --a-n

4. Limpeza completa (inclui logs e caches do sistema):
   python3 sisclean --ex --c

5. Ver ajuda:
   python3 sisclean --help

AUTOR: Script criado para otimização do ambiente de desenvolvimento
DATA: 5 de setembro de 2025
"""

import os
import shutil
import argparse
import subprocess
from pathlib import Path
import time
from datetime import datetime

class LimpadorSistema:
    def __init__(self):
        # Diretório base (Área de trabalho)
        self.base_dir = Path.home() / "Área de trabalho"
        
        # Contadores para estatísticas
        self.total_liberado = 0
        self.arquivos_removidos = 0
        self.diretorios_removidos = 0
        
        # Lista de diretórios e arquivos para limpeza
        self.node_modules_dirs = []
        self.temp_files = []
        self.cache_dirs = []
        self.log_files = []
        
    def escanear_sistema(self):
        """Escaneia o sistema procurando arquivos para limpeza"""
        print("🔍 Escaneando sistema...")
        print(f"📁 Diretório base: {self.base_dir}")
        
        # Procura por node_modules
        self._encontrar_node_modules()
        
        # Procura por arquivos temporários
        self._encontrar_arquivos_temp()
        
        # Procura por caches
        self._encontrar_caches()
        
        # Procura por logs antigos
        self._encontrar_logs()
        
        print(f"✅ Escaneamento concluído!")
        
    def _encontrar_node_modules(self):
        """Encontra todos os diretórios node_modules"""
        print("   📦 Procurando node_modules...")
        
        for root, dirs, files in os.walk(self.base_dir):
            if 'node_modules' in dirs:
                node_modules_path = Path(root) / 'node_modules'
                
                # Verifica se tem mais de 30 dias ou se está em projeto inativo
                if self._is_old_or_inactive(node_modules_path):
                    size = self._get_dir_size(node_modules_path)
                    self.node_modules_dirs.append({
                        'path': node_modules_path,
                        'size': size,
                        'projeto': Path(root).name
                    })
    
    def _encontrar_arquivos_temp(self):
        """Encontra arquivos temporários"""
        print("   🗂️  Procurando arquivos temporários...")
        
        temp_patterns = [
            '**/*.tmp',
            '**/*.temp',
            '**/.DS_Store',
            '**/Thumbs.db',
            '**/*.log',
            '**/*.bak',
            '**/*.swp',
            '**/*~'
        ]
        
        for pattern in temp_patterns:
            for file_path in self.base_dir.rglob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    self.temp_files.append({
                        'path': file_path,
                        'size': size
                    })
    
    def _encontrar_caches(self):
        """Encontra diretórios de cache"""
        print("   💾 Procurando caches...")
        
        cache_dirs = [
            '.next',
            '.nuxt',
            'dist',
            'build',
            '.cache',
            '__pycache__',
            '.pytest_cache'
        ]
        
        for root, dirs, files in os.walk(self.base_dir):
            for cache_dir in cache_dirs:
                if cache_dir in dirs:
                    cache_path = Path(root) / cache_dir
                    size = self._get_dir_size(cache_path)
                    self.cache_dirs.append({
                        'path': cache_path,
                        'size': size,
                        'tipo': cache_dir
                    })
    
    def _encontrar_logs(self):
        """Encontra arquivos de log antigos"""
        print("   📋 Procurando logs antigos...")
        
        for log_file in self.base_dir.rglob('*.log'):
            if log_file.is_file():
                # Verifica se o log tem mais de 7 dias
                if self._is_old_file(log_file, days=7):
                    size = log_file.stat().st_size
                    self.log_files.append({
                        'path': log_file,
                        'size': size
                    })
    
    def _is_old_or_inactive(self, path, days=30):
        """Verifica se um diretório é antigo ou inativo"""
        try:
            # Verifica a data de modificação mais recente
            mtime = path.stat().st_mtime
            age_days = (time.time() - mtime) / (24 * 3600)
            return age_days > days
        except:
            return False
    
    def _is_old_file(self, file_path, days=7):
        """Verifica se um arquivo é antigo"""
        try:
            mtime = file_path.stat().st_mtime
            age_days = (time.time() - mtime) / (24 * 3600)
            return age_days > days
        except:
            return False
    
    def _get_dir_size(self, path):
        """Calcula o tamanho de um diretório"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
            return total_size
        except:
            return 0
    
    def _format_size(self, size_bytes):
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def mostrar_relatorio(self, d=False):
        """Mostra relatório do que será removido"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE LIMPEZA")
        print("="*60)
        
        total_estimado = 0
        
        # Node modules
        if self.node_modules_dirs:
            print(f"\n📦 NODE_MODULES ENCONTRADOS ({len(self.node_modules_dirs)}):")
            if d:
                # Mostra todos os d
                for item in self.node_modules_dirs:
                    size_str = self._format_size(item['size'])
                    print(f"   • {item['path']}")
                    print(f"     Projeto: {item['projeto']} | Tamanho: {size_str}")
                    total_estimado += item['size']
            else:
                # Mostra apenas os 10 maiores
                for item in self.node_modules_dirs[:10]:
                    size_str = self._format_size(item['size'])
                    print(f"   • {item['projeto']}: {size_str}")
                    total_estimado += item['size']
                
                if len(self.node_modules_dirs) > 10:
                    print(f"   ... e mais {len(self.node_modules_dirs) - 10} diretórios")
                    # Adiciona o tamanho dos restantes
                    for item in self.node_modules_dirs[10:]:
                        total_estimado += item['size']
        
        # Arquivos temporários
        if self.temp_files:
            temp_size = sum(item['size'] for item in self.temp_files)
            print(f"\n🗂️  ARQUIVOS TEMPORÁRIOS: {len(self.temp_files)} arquivos")
            if d:
                print("   Lista completa:")
                for item in self.temp_files:
                    size_str = self._format_size(item['size'])
                    print(f"   • {item['path']} ({size_str})")
            else:
                print(f"   Tamanho total: {self._format_size(temp_size)}")
            total_estimado += temp_size
        
        # Caches
        if self.cache_dirs:
            cache_size = sum(item['size'] for item in self.cache_dirs)
            print(f"\n💾 DIRETÓRIOS DE CACHE: {len(self.cache_dirs)} diretórios")
            if d:
                print("   Lista completa:")
                for item in self.cache_dirs:
                    size_str = self._format_size(item['size'])
                    print(f"   • {item['path']} [{item['tipo']}] ({size_str})")
            else:
                print(f"   Tamanho total: {self._format_size(cache_size)}")
            total_estimado += cache_size
        
        # Logs
        if self.log_files:
            log_size = sum(item['size'] for item in self.log_files)
            print(f"\n📋 LOGS ANTIGOS: {len(self.log_files)} arquivos")
            if d:
                print("   Lista completa:")
                for item in self.log_files:
                    size_str = self._format_size(item['size'])
                    mtime = datetime.fromtimestamp(item['path'].stat().st_mtime)
                    print(f"   • {item['path']} ({size_str}) - {mtime.strftime('%d/%m/%Y')}")
            else:
                print(f"   Tamanho total: {self._format_size(log_size)}")
            total_estimado += log_size
        
        print(f"\n💾 ESPAÇO TOTAL A SER LIBERADO: {self._format_size(total_estimado)}")
        print("="*60)
    
    def ex_limpeza(self, a_n=False, c=False):
        """Executa a limpeza dos arquivos"""
        print("\n🧹 INICIANDO LIMPEZA...")
        inicio = time.time()
        
        try:
            # Limpa node_modules
            if not a_n or a_n:
                self._limpar_node_modules()
            
            if not a_n:
                # Limpa arquivos temporários
                self._limpar_temp_files()
                
                # Limpa caches
                self._limpar_caches()
                
                # Se limpeza completa, limpa logs também
                if c:
                    self._limpar_logs()
            
            # Limpa lixeira do sistema (se possível)
            self._limpar_lixeira()
            
        except KeyboardInterrupt:
            print("\n⚠️  Limpeza interrompida pelo usuário!")
            return False
        
        fim = time.time()
        tempo_total = fim - inicio
        
        print(f"\n✅ LIMPEZA CONCLUÍDA!")
        print(f"⏱️  Tempo total: {tempo_total:.1f} segundos")
        print(f"💾 Espaço liberado: {self._format_size(self.total_liberado)}")
        print(f"📁 Diretórios removidos: {self.diretorios_removidos}")
        print(f"📄 Arquivos removidos: {self.arquivos_removidos}")
        
        return True
    
    def _limpar_node_modules(self):
        """Remove diretórios node_modules"""
        print("   📦 Removendo node_modules...")
        
        for item in self.node_modules_dirs:
            try:
                # Verifica se o diretório ainda existe antes de tentar remover
                if item['path'].exists():
                    print(f"      Removendo: {item['projeto']}/node_modules")
                    shutil.rmtree(item['path'])
                    self.total_liberado += item['size']
                    self.diretorios_removidos += 1
                else:
                    # Silenciosamente pula arquivos que já foram removidos
                    pass
            except Exception as e:
                print(f"      ⚠️  Pulando {item['path']}: arquivo não encontrado")
    
    def _limpar_temp_files(self):
        """Remove arquivos temporários"""
        print("   🗂️  Removendo arquivos temporários...")
        
        for item in self.temp_files:
            try:
                if item['path'].exists():
                    item['path'].unlink()
                    self.total_liberado += item['size']
                    self.arquivos_removidos += 1
            except Exception as e:
                # Silenciosamente pula arquivos que já foram removidos
                pass
    
    def _limpar_caches(self):
        """Remove diretórios de cache"""
        print("   💾 Removendo caches...")
        
        for item in self.cache_dirs:
            try:
                if item['path'].exists():
                    shutil.rmtree(item['path'])
                    self.total_liberado += item['size']
                    self.diretorios_removidos += 1
            except Exception as e:
                # Silenciosamente pula diretórios que já foram removidos
                pass
    
    def _limpar_logs(self):
        """Remove logs antigos"""
        print("   📋 Removendo logs antigos...")
        
        for item in self.log_files:
            try:
                if item['path'].exists():
                    item['path'].unlink()
                    self.total_liberado += item['size']
                    self.arquivos_removidos += 1
            except Exception as e:
                # Silenciosamente pula arquivos que já foram removidos
                pass
    
    def _limpar_lixeira(self):
        """Limpa a lixeira do sistema"""
        print("   🗑️  Limpando lixeira do sistema...")
        try:
            # Tenta limpar lixeira no Linux
            trash_dir = Path.home() / ".local/share/Trash"
            if trash_dir.exists():
                for item in trash_dir.rglob("*"):
                    if item.is_file():
                        try:
                            item.unlink()
                            self.arquivos_removidos += 1
                        except:
                            pass
        except Exception as e:
            print(f"      ⚠️  Não foi possível limpar lixeira: {e}")


def main():
    # Configuração dos argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description="Script de limpeza do sistema para desenvolvedores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:
   sisclean                     # Modo preview (não remove nada)
   sisclean --d          # Mostra lista detalhada dos arquivos
   sisclean --ex          # Executa limpeza real
   sisclean --a-n       # Remove apenas node_modules
   sisclean --ex --c  # Limpeza completa
        """
    )
    
    parser.add_argument(
        '--ex',
        action='store_true',
        help='Executa a limpeza real (sem esta opção apenas mostra o que seria removido)'
    )
    
    parser.add_argument(
        '--a-n',
        action='store_true',
        help='Remove apenas diretórios node_modules'
    )
    
    parser.add_argument(
        '--c',
        action='store_true',
        help='Executa limpeza completa (inclui logs do sistema)'
    )
    
    parser.add_argument(
        '--d',
        action='store_true',
        help='Mostra lista detalhada de todos os arquivos que serão removidos'
    )
    
    args = parser.parse_args()
    
    # Banner do script
    print("🧹" + "="*58 + "🧹")
    print("   SCRIPT DE LIMPEZA DO SISTEMA - AMBIENTE DE DEV")
    print("🧹" + "="*58 + "🧹")
    print(f"📅 Executado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    
    # Cria instância do limpador
    limpador = LimpadorSistema()
    
    # Escaneia o sistema
    limpador.escanear_sistema()
    
    # Mostra relatório
    limpador.mostrar_relatorio(d=args.d)
    
    # Se não for para ex, apenas mostra o preview
    if not args.ex:
        print(f"\n⚠️  MODO PREVIEW ATIVO!")
        print("   Para ex a limpeza real, use: --ex")
        print("   Exemplo: python3 sisclean --ex")
        return
    
    # Confirma antes de ex
    print(f"\n⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!")
    resposta = input("🤔 Tem certeza que deseja continuar? (sim/não): ")
    
    if resposta.lower() not in ['sim', 's', 'yes', 'y']:
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Executa a limpeza
    sucesso = limpador.ex_limpeza(
        a_n=args.a_n,
        c=args.c
    )
    
    if sucesso:
        print("\n🎉 Script executado com sucesso!")
        print("💡 Dica: Execute este script semanalmente para manter o sistema otimizado")
    else:
        print("\n❌ Script interrompido ou falhou!")


if __name__ == "__main__":
    main()
