#!/usr/bin/env python3
"""
Script de Backup Universal
Criado para fazer backups completos de diretórios com funcionalidades avançadas
"""

import os
import sys
import json
import tarfile
import zipfile
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import fnmatch
import shutil

class BackupUniversal:
    def __init__(self):
        # Definindo diretório base padrão para backup (agora é o root '/')
        self.area_trabalho = Path("/")

        # Diretório de backups (agora fixo em ~/backups)
        self.dir_backups = Path("~/backups").expanduser()
        self.dir_backups.mkdir(parents=True, exist_ok=True)

        # Arquivo de índice dos backups
        self.indice_backups = self.dir_backups / "indice_backups.json"

        # Padrões de exclusão padrão
        self.padroes_exclusao = [
            # Arquivos temporários
            '*.tmp', '*.temp', '*.log', '*.cache',
            # Node.js
            'node_modules', 'npm-debug.log', '.npm',
            # Python
            '__pycache__', '*.pyc', '.pytest_cache', 'venv', '.venv',
            # Git
            '.git',
            # IDEs
            '.vscode', '.idea', '*.swp', '*.swo',
            # Builds
            'build', 'dist', 'target',
            # OS
            '.DS_Store', 'Thumbs.db', '.Trash',
            # Grandes arquivos comuns
            '*.iso', '*.dmg', '*.img'
        ]
        
        # Padrões personalizados (adicionados pelo usuário)
        self.padroes_custom = []
        
        # Estatísticas do backup
        self.reset_stats()
        
    def reset_stats(self):
        """Reseta as estatísticas do backup"""
        self.total_arquivos = 0
        self.arquivos_excluidos = 0
        self.diretorios_excluidos = 0
        self.tamanho_original = 0

    def adicionar_padroes_exclusao(self, padroes_string):
        """Adiciona padrões customizados de exclusão"""
        if padroes_string:
            novos_padroes = [p.strip() for p in padroes_string.split(',') if p.strip()]
            self.padroes_custom.extend(novos_padroes)
            
    def _deve_excluir(self, caminho):
        """Verifica se um arquivo/diretório deve ser excluído"""
        nome = Path(caminho).name
        
        # Verifica padrões padrão
        for padrao in self.padroes_exclusao:
            if fnmatch.fnmatch(nome, padrao):
                return True
                
        # Verifica padrões customizados
        for padrao in self.padroes_custom:
            if fnmatch.fnmatch(nome, padrao):
                return True
                
        return False
        
    def _calcular_tamanho_diretorio(self, caminho):
        """Calcula o tamanho total de um diretório (apenas arquivos que não serão excluídos)"""
        tamanho_total = 0
        total_arquivos = 0
        
        for root, dirs, files in os.walk(caminho):
            # Remove diretórios excluídos da lista para não percorrê-los
            dirs[:] = [d for d in dirs if not self._deve_excluir(d)]
            
            for arquivo in files:
                if not self._deve_excluir(arquivo):
                    try:
                        caminho_arquivo = Path(root) / arquivo
                        tamanho_total += caminho_arquivo.stat().st_size
                        total_arquivos += 1
                    except (OSError, IOError):
                        continue
                        
        return tamanho_total, total_arquivos
        
    def _formatar_tamanho(self, bytes_size):
        """Formata tamanho em bytes para formato legível"""
        for unidade in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unidade}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
        
    def _calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula hash MD5 de um arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(caminho_arquivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception:
            return None
        return hash_md5.hexdigest()
        
    def _obter_info_diretorio(self, caminho):
        """Obtém informações sobre o diretório"""
        caminho = Path(caminho)
        if not caminho.exists():
            return None
            
        # Detecta tipo do diretório
        tipo_diretorio = "generico"
        if (caminho / "package.json").exists():
            tipo_diretorio = "nodejs"
        elif (caminho / "requirements.txt").exists() or (caminho / "setup.py").exists():
            tipo_diretorio = "python"
        elif (caminho / "pom.xml").exists():
            tipo_diretorio = "java"
        elif (caminho / ".git").exists():
            tipo_diretorio = "git"
            
        return {
            "nome": caminho.name,
            "caminho": str(caminho.absolute()),
            "tipo": tipo_diretorio,
            "ultima_modificacao": datetime.fromtimestamp(caminho.stat().st_mtime).isoformat()
        }
        
    def criar_backup(self, caminho_origem=None, nome_backup=None, compressao_maxima=False, silencioso=False, formato=None):
        """Cria backup de um diretório"""
        # Define caminho de origem
        if caminho_origem:
            caminho_origem = Path(caminho_origem).expanduser().resolve()
        else:
            caminho_origem = self.area_trabalho
            
        # Verifica se o diretório existe
        if not caminho_origem.exists():
            print(f"❌ Erro: Diretório '{caminho_origem}' não encontrado!")
            return False
            
        if not caminho_origem.is_dir():
            print(f"❌ Erro: '{caminho_origem}' não é um diretório!")
            return False
            
        # Obtém informações do diretório
        info_diretorio = self._obter_info_diretorio(caminho_origem)
        nome_diretorio = info_diretorio["nome"]
        
        print(f"\n📦 INICIANDO BACKUP")
        print("=" * 50)
        print(f"📁 Diretório: {caminho_origem}")
        print(f"🏷️  Tipo: {info_diretorio['tipo']}")
        
        # Calcula tamanho e número de arquivos
        print("📊 Calculando tamanho do backup...")
        self.tamanho_original, total_arquivos_estimado = self._calcular_tamanho_diretorio(caminho_origem)
        
        print(f"📈 Arquivos a processar: {total_arquivos_estimado:,}")
        print(f"📏 Tamanho estimado: {self._formatar_tamanho(self.tamanho_original)}")
        
        # Confirma se deve prosseguir
        if not silencioso:
            print(f"\n🤔 Deseja prosseguir com o backup de '{nome_diretorio}'?")
            if self.padroes_custom:
                print(f"🚫 Padrões de exclusão adicionais: {', '.join(self.padroes_custom)}")
            print("   Escolha o formato de compressão:")
            print("   [1] .tar.gz (Linux/macOS)")
            print("   [2] .zip (Windows)")
            print("      OBS: Para poder descompactar em um Windows")
            formato_opcao = input("   Digite 1 para .tar.gz ou 2 para .zip: ").strip()
            if formato_opcao == '1':
                formato = 'tar'
            elif formato_opcao == '2':
                formato = 'zip'
            else:
                print("❌ Opção inválida. Backup cancelado.")
                return False
            confirmacao = input("   Digite 's' para continuar ou qualquer tecla para cancelar: ").lower()
            if confirmacao != 's':
                print("❌ Backup cancelado pelo usuário.")
                return False
        else:
            if not formato:
                print("❌ O formato de backup deve ser especificado em modo silencioso.")
                return False
                
        # Define nome do arquivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if formato == 'tar':
            if nome_backup:
                nome_arquivo = f"{nome_backup}_{timestamp}.tar.gz"
            else:
                nome_arquivo = f"backup_{nome_diretorio}_{timestamp}.tar.gz"
        elif formato == 'zip':
            if nome_backup:
                nome_arquivo = f"{nome_backup}_{timestamp}.zip"
            else:
                nome_arquivo = f"backup_{nome_diretorio}_{timestamp}.zip"
        else:
            print("❌ Formato de backup inválido.")
            return False
        caminho_backup = self.dir_backups / nome_arquivo
        
        # Reset estatísticas
        self.reset_stats()
        
        try:
            print(f"\n⏳ Criando backup: {nome_arquivo}")
            if formato == 'tar':
                # Define compressão
                if compressao_maxima:
                    modo_tar = "w:gz"
                    compresslevel = 9
                    print("🗜️  Usando compressão máxima...")
                else:
                    modo_tar = "w:gz"
                    compresslevel = 6
                # Cria arquivo tar
                with tarfile.open(caminho_backup, modo_tar, compresslevel=compresslevel) as tar:
                    self._adicionar_arquivos_ao_tar(tar, caminho_origem, total_arquivos_estimado)
            elif formato == 'zip':
                print("🗜️  Compactando em formato ZIP...")
                with zipfile.ZipFile(caminho_backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9 if compressao_maxima else 6) as zipf:
                    self._adicionar_arquivos_ao_zip(zipf, caminho_origem, total_arquivos_estimado)
                
            # Calcula informações do backup
            tamanho_backup = caminho_backup.stat().st_size
            taxa_compressao = ((self.tamanho_original - tamanho_backup) / self.tamanho_original * 100) if self.tamanho_original > 0 else 0
            hash_backup = self._calcular_hash_arquivo(caminho_backup)
            
            # Registra no índice
            self._registrar_backup({
                "arquivo": nome_arquivo,
                "diretorio_origem": str(caminho_origem),
                "nome_diretorio": nome_diretorio,
                "data_criacao": datetime.now().isoformat(),
                "tamanho_original": self.tamanho_original,
                "tamanho_backup": tamanho_backup,
                "taxa_compressao": taxa_compressao,
                "total_arquivos": self.total_arquivos,
                "arquivos_excluidos": self.arquivos_excluidos,
                "diretorios_excluidos": self.diretorios_excluidos,
                "tipo_diretorio": info_diretorio["tipo"],
                "hash_md5": hash_backup,
                "compressao_maxima": compressao_maxima,
                "formato": formato
            })
            
            # Relatório final
            print(f"\n✅ BACKUP CONCLUÍDO COM SUCESSO!")
            print("=" * 50)
            print(f"📁 Arquivo: {nome_arquivo}")
            print(f"📊 Arquivos incluídos: {self.total_arquivos:,}")
            print(f"🚫 Itens excluídos: {self.arquivos_excluidos + self.diretorios_excluidos:,}")
            print(f"📏 Tamanho original: {self._formatar_tamanho(self.tamanho_original)}")
            print(f"🗜️  Tamanho backup: {self._formatar_tamanho(tamanho_backup)}")
            print(f"📉 Compressão: {taxa_compressao:.1f}%")
            print(f"🔒 Hash MD5: {hash_backup[:16]}...")
            print(f"💾 Localização: {caminho_backup}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            # Remove arquivo parcial se existir
            if caminho_backup.exists():
                try:
                    caminho_backup.unlink()
                except:
                    pass
            return False

    def _adicionar_arquivos_ao_zip(self, zipf, caminho_origem, total_estimado):
        """Adiciona arquivos ao zip com progresso"""
        contador = 0
        ultimo_relatorio = 0
        relatorio_intervalo = max(100, total_estimado // 50)
        print("📦 Compactando arquivos...")
        for root, dirs, files in os.walk(caminho_origem):
            dirs_originais = len(dirs)
            dirs[:] = [d for d in dirs if not self._deve_excluir(d)]
            self.diretorios_excluidos += (dirs_originais - len(dirs))
            for arquivo in files:
                if not self._deve_excluir(arquivo):
                    try:
                        caminho_arquivo = Path(root) / arquivo
                        caminho_relativo = caminho_arquivo.relative_to(caminho_origem.parent)
                        zipf.write(str(caminho_arquivo), arcname=str(caminho_relativo))
                        self.total_arquivos += 1
                        contador += 1
                        if contador - ultimo_relatorio >= relatorio_intervalo:
                            if total_estimado > 0:
                                progresso = (contador / total_estimado) * 100
                                print(f"   📦 Progresso: {contador:,}/{total_estimado:,} arquivos ({progresso:.1f}%)")
                            else:
                                print(f"   📦 Processados: {contador:,} arquivos")
                            ultimo_relatorio = contador
                    except Exception as e:
                        print(f"   ⚠️  Erro ao adicionar {arquivo}: {e}")
                        continue
            
    def _adicionar_arquivos_ao_tar(self, tar, caminho_origem, total_estimado):
        """Adiciona arquivos ao tar com progresso"""
        contador = 0
        ultimo_relatorio = 0
        relatorio_intervalo = max(100, total_estimado // 50)  # Relatório a cada 2%
        
        print("📦 Compactando arquivos...")
        
        for root, dirs, files in os.walk(caminho_origem):
            # Remove diretórios excluídos da lista
            dirs_originais = len(dirs)
            dirs[:] = [d for d in dirs if not self._deve_excluir(d)]
            self.diretorios_excluidos += (dirs_originais - len(dirs))
            
            for arquivo in files:
                if not self._deve_excluir(arquivo):
                    try:
                        caminho_arquivo = Path(root) / arquivo
                        # Calcula caminho relativo mantendo estrutura
                        caminho_relativo = caminho_arquivo.relative_to(caminho_origem.parent)
                        tar.add(str(caminho_arquivo), arcname=str(caminho_relativo))
                        self.total_arquivos += 1
                        contador += 1
                        
                        # Mostra progresso
                        if contador - ultimo_relatorio >= relatorio_intervalo:
                            if total_estimado > 0:
                                progresso = (contador / total_estimado) * 100
                                print(f"   📦 Progresso: {contador:,}/{total_estimado:,} arquivos ({progresso:.1f}%)")
                            else:
                                print(f"   📦 Processados: {contador:,} arquivos")
                            ultimo_relatorio = contador
                            
                    except Exception as e:
                        print(f"   ⚠️  Erro ao adicionar {arquivo}: {e}")
                        continue
                else:
                    self.arquivos_excluidos += 1
                    
    def _registrar_backup(self, info_backup):
        """Registra backup no índice"""
        try:
            if self.indice_backups.exists():
                with open(self.indice_backups, 'r', encoding='utf-8') as f:
                    backups = json.load(f)
            else:
                backups = []
                
            backups.append(info_backup)
            
            with open(self.indice_backups, 'w', encoding='utf-8') as f:
                json.dump(backups, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao registrar backup no índice: {e}")
            
    def listar_backups(self):
        """Lista todos os backups existentes"""
        print("\n📋 BACKUPS EXISTENTES")
        print("=" * 60)
        
        if not self.indice_backups.exists():
            print("📂 Nenhum backup encontrado ainda.")
            print(f"💡 Execute um backup primeiro com: python3 backup.py")
            return
            
        try:
            with open(self.indice_backups, 'r', encoding='utf-8') as f:
                backups = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao ler índice de backups: {e}")
            return
            
        if not backups:
            print("📂 Nenhum backup registrado.")
            return
            
        # Agrupa por diretório
        por_diretorio = {}
        for backup in backups:
            nome_dir = backup['nome_diretorio']
            if nome_dir not in por_diretorio:
                por_diretorio[nome_dir] = []
            por_diretorio[nome_dir].append(backup)
            
        # Lista backups agrupados
        for nome_diretorio, backups_dir in por_diretorio.items():
            print(f"\n📁 {nome_diretorio} ({len(backups_dir)} backups)")
            
            # Ordena por data (mais recente primeiro)
            backups_dir.sort(key=lambda x: x['data_criacao'], reverse=True)
            
            for i, backup in enumerate(backups_dir):
                data_criacao = datetime.fromisoformat(backup['data_criacao'])
                data_str = data_criacao.strftime('%d/%m/%Y %H:%M:%S')
                
                tamanho = self._formatar_tamanho(backup['tamanho_backup'])
                compressao = backup.get('taxa_compressao', 0)
                
                # Marca o mais recente
                marcador = "🟢 RECENTE" if i == 0 else "   "
                
                print(f"  {marcador} {backup['arquivo']}")
                print(f"      📅 {data_str}")
                print(f"      📊 {tamanho} (compressão: {compressao:.1f}%)")
                print(f"      🎯 Tipo: {backup.get('tipo_diretorio', 'generico')}")
                print(f"      📁 Origem: {backup.get('diretorio_origem', 'N/A')}")
                
        print(f"\n📊 Total: {len(backups)} backups")
        
    def limpar_backups_antigos(self, dias_manter=30, max_por_diretorio=5):
        """Remove backups antigos baseado em critérios"""
        print(f"\n🧹 LIMPANDO BACKUPS ANTIGOS")
        print(f"📋 Critérios:")
        print(f"   • Manter no máximo {max_por_diretorio} backups por diretório")
        print(f"   • Manter backups dos últimos {dias_manter} dias")
        print("=" * 50)
        
        if not self.indice_backups.exists():
            print("📂 Nenhum índice de backups encontrado.")
            return
            
        try:
            with open(self.indice_backups, 'r', encoding='utf-8') as f:
                backups = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao ler índice: {e}")
            return
            
        if not backups:
            print("📂 Nenhum backup para limpar.")
            return
            
        data_limite = datetime.now() - timedelta(days=dias_manter)
        backups_para_remover = []
        backups_mantidos = []
        
        # Agrupa por diretório
        por_diretorio = {}
        for backup in backups:
            nome_dir = backup['nome_diretorio']
            if nome_dir not in por_diretorio:
                por_diretorio[nome_dir] = []
            por_diretorio[nome_dir].append(backup)
            
        # Aplica critérios de limpeza
        total_removidos = 0
        tamanho_liberado = 0
        
        for nome_diretorio, backups_dir in por_diretorio.items():
            # Ordena por data (mais recente primeiro)
            backups_dir.sort(key=lambda x: x['data_criacao'], reverse=True)
            
            print(f"\n📁 Processando: {nome_diretorio}")
            
            for i, backup in enumerate(backups_dir):
                data_backup = datetime.fromisoformat(backup['data_criacao'])
                arquivo_backup = self.dir_backups / backup['arquivo']
                
                deve_remover = False
                motivo = ""
                
                # Critério 1: Mais de max_por_diretorio backups
                if i >= max_por_diretorio:
                    deve_remover = True
                    motivo = f"excede limite ({max_por_diretorio} por diretório)"
                    
                # Critério 2: Mais antigo que dias_manter
                elif data_backup < data_limite:
                    deve_remover = True
                    motivo = f"mais antigo que {dias_manter} dias"
                    
                if deve_remover:
                    if arquivo_backup.exists():
                        try:
                            tamanho_arquivo = arquivo_backup.stat().st_size
                            arquivo_backup.unlink()
                            backups_para_remover.append(backup)
                            total_removidos += 1
                            tamanho_liberado += tamanho_arquivo
                            
                            data_str = data_backup.strftime('%d/%m/%Y')
                            tamanho_str = self._formatar_tamanho(tamanho_arquivo)
                            print(f"   🗑️  Removido: {backup['arquivo']} ({data_str}, {tamanho_str}) - {motivo}")
                            
                        except Exception as e:
                            print(f"   ⚠️  Erro ao remover {backup['arquivo']}: {e}")
                            backups_mantidos.append(backup)
                    else:
                        backups_para_remover.append(backup)  # Remove do índice mesmo se arquivo não existe
                        print(f"   ⚠️  Arquivo {backup['arquivo']} não encontrado (removido do índice)")
                else:
                    backups_mantidos.append(backup)
                    
        # Atualiza índice
        if backups_para_remover:
            try:
                with open(self.indice_backups, 'w', encoding='utf-8') as f:
                    json.dump(backups_mantidos, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"❌ Erro ao atualizar índice: {e}")
                
        # Relatório final
        print(f"\n✅ LIMPEZA CONCLUÍDA")
        print("=" * 30)
        print(f"🗑️  Backups removidos: {total_removidos}")
        print(f"💾 Espaço liberado: {self._formatar_tamanho(tamanho_liberado)}")
        print(f"📁 Backups mantidos: {len(backups_mantidos)}")
        
    def restaurar_backup(self):
        """Interface interativa para restaurar backups"""
        print("\n🔄 RESTAURAÇÃO DE BACKUP")
        print("=" * 40)
        
        if not self.indice_backups.exists():
            print("📂 Nenhum backup encontrado para restaurar.")
            return
            
        try:
            with open(self.indice_backups, 'r', encoding='utf-8') as f:
                backups = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao ler índice: {e}")
            return
            
        if not backups:
            print("📂 Nenhum backup disponível.")
            return
            
        # Lista backups disponíveis
        print("Backups disponíveis:")
        backups_ordenados = sorted(backups, key=lambda x: x['data_criacao'], reverse=True)
        
        for i, backup in enumerate(backups_ordenados):
            data = datetime.fromisoformat(backup['data_criacao'])
            data_str = data.strftime('%d/%m/%Y %H:%M')
            tamanho = self._formatar_tamanho(backup['tamanho_backup'])
            
            print(f"  [{i+1}] {backup['nome_diretorio']} - {data_str} ({tamanho})")
            
        # Seleção do backup
        try:
            escolha = input(f"\nEscolha um backup (1-{len(backups_ordenados)}) ou 'c' para cancelar: ").strip()
            if escolha.lower() == 'c':
                print("❌ Restauração cancelada.")
                return
                
            indice = int(escolha) - 1
            if indice < 0 or indice >= len(backups_ordenados):
                print("❌ Opção inválida.")
                return
                
        except ValueError:
            print("❌ Opção inválida.")
            return
            
        backup_escolhido = backups_ordenados[indice]
        arquivo_backup = self.dir_backups / backup_escolhido['arquivo']
        
        if not arquivo_backup.exists():
            print(f"❌ Arquivo de backup não encontrado: {backup_escolhido['arquivo']}")
            return
            
        # Escolha do destino
        print(f"\n📁 Restaurando: {backup_escolhido['nome_diretorio']}")
        print(f"📂 Origem: {backup_escolhido.get('diretorio_origem', 'N/A')}")
        
        destino_default = Path.home() / "Área de trabalho" / "restauracao" / backup_escolhido['nome_diretorio']
        destino_str = input(f"Diretório de destino (Enter para {destino_default}): ").strip()
        
        if destino_str:
            destino = Path(destino_str).expanduser()
        else:
            destino = destino_default
            
        # Cria diretório de destino
        destino.mkdir(parents=True, exist_ok=True)
        
        # Confirma restauração
        print(f"\n🤔 Confirma restauração?")
        print(f"   📦 Backup: {backup_escolhido['arquivo']}")
        print(f"   📁 Destino: {destino}")
        confirmacao = input("   Digite 's' para confirmar: ").lower()
        
        if confirmacao != 's':
            print("❌ Restauração cancelada.")
            return
            
        # Executa restauração
        try:
            print(f"\n⏳ Extraindo backup...")
            with tarfile.open(arquivo_backup, 'r:gz') as tar:
                tar.extractall(path=destino.parent)
                
            print(f"✅ Backup restaurado com sucesso!")
            print(f"📁 Localização: {destino}")
            
        except Exception as e:
            print(f"❌ Erro durante restauração: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Script de backup universal de diretórios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:
  python3 backup.py                                    # Backup completo da Área de Trabalho
  python3 backup.py -d /home/user/documentos           # Backup de diretório específico
  python3 backup.py -d ./projetos --nome meus_projetos # Backup com nome personalizado
  python3 backup.py --compressao-maxima                # Backup com máxima compressão
  python3 backup.py --excluir "*.iso,Downloads,tmp"    # Excluir padrões específicos
  python3 backup.py --silencioso                       # Backup sem confirmações
  python3 backup.py --listar-backups                   # Lista backups existentes
  python3 backup.py --limpar-antigos                   # Remove backups antigos
  python3 backup.py --restaurar                        # Interface de restauração
        """
    )
    
    parser.add_argument('-d', '--diretorio', 
                       help='Caminho do diretório para backup (padrão: Área de Trabalho)')
    parser.add_argument('--nome', 
                       help='Nome personalizado para o backup')
    parser.add_argument('--compressao-maxima', action='store_true',
                       help='Usa compressão máxima (mais lento, mas menor arquivo)')
    parser.add_argument('--excluir',
                       help='Padrões adicionais para excluir (separados por vírgula)')
    parser.add_argument('--silencioso', action='store_true',
                       help='Executa backup sem pedir confirmação (obrigatório informar --formato)')
    parser.add_argument('--formato', choices=['tar', 'zip'],
                       help='Formato de compressão: "tar" para .tar.gz (Linux/macOS), "zip" para .zip (Windows)')
    parser.add_argument('--listar-backups', action='store_true',
                       help='Lista todos os backups existentes')
    parser.add_argument('--limpar-antigos', action='store_true',
                       help='Remove backups antigos (mantém últimos 5 ou dos últimos 30 dias)')
    parser.add_argument('--restaurar', action='store_true',
                       help='Interface interativa para restaurar backups')
    
    args = parser.parse_args()
    
    # Cria instância do backup
    backup = BackupUniversal()
    
    # Adiciona padrões de exclusão personalizados
    if args.excluir:
        backup.adicionar_padroes_exclusao(args.excluir)
        print(f"🚫 Padrões de exclusão adicionais: {args.excluir}")
        
    # Executa ação baseada nos argumentos
    if args.listar_backups:
        backup.listar_backups()
        
    elif args.limpar_antigos:
        backup.limpar_backups_antigos()
        
    elif args.restaurar:
        backup.restaurar_backup()
        
    else:
        # Executa backup
        sucesso = backup.criar_backup(
            caminho_origem=args.diretorio,
            nome_backup=args.nome,
            compressao_maxima=args.compressao_maxima,
            silencioso=args.silencioso,
            formato=args.formato
        )
        
        if sucesso:
            print("\n💡 DICAS:")
            print("   • Execute backups regularmente (semanal/quinzenal)")
            print("   • Use --limpar-antigos para manter espaço em disco")
            print("   • Teste restaurações periodicamente")
            print("   • Considere sincronizar a pasta 'backups' com nuvem")
            print("   • Use --excluir para personalizar padrões de exclusão")
        else:
            print("\n⚠️  Verifique se o diretório especificado existe e é acessível")


if __name__ == "__main__":
    main()
