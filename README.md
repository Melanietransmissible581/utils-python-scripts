<div align="center">

# 🛠️ Utils Python Scripts

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/montezuma-p/utils-python-scripts/commits/main)
[![Platform](https://img.shields.io/badge/platform-linux-blue.svg)](https://github.com/montezuma-p/utils-python-scripts)
[![Tested On](https://img.shields.io/badge/tested%20on-arch%20linux-1793D1.svg)](https://archlinux.org/)

**Coleção de scripts Python para automação e otimização de sistemas de desenvolvimento**

[Funcionalidades](#-funcionalidades) • [Instalação](#-instalação) • [Documentação](#-documentação) • [Roadmap](#-roadmap) • [Contribuindo](#-contribuindo)

</div>

---

## 📋 Sobre o Projeto

**Utils Python Scripts** é uma coleção crescente de ferramentas Python desenvolvidas para automatizar tarefas comuns de gerenciamento de sistema e desenvolvimento. Esta é a **versão 1.0** do projeto, marcando o lançamento inicial com dois scripts essenciais para qualquer desenvolvedor.

Cada script é cuidadosamente desenvolvido com foco em:
- ✨ **Simplicidade de uso** - Interfaces intuitivas e documentadas
- 🔒 **Segurança** - Modos preview e confirmações antes de operações destrutivas
- 📚 **Documentação completa** - Cada script possui documentação técnica detalhada
- 🚀 **Performance** - Otimizado para lidar com grandes volumes de dados
- 🔧 **Extensibilidade** - Código modular e bem estruturado para futuras expansões

---

## 🎯 Funcionalidades

### 📦 Backup Script
Script de backup com suporte a múltiplos formatos e gerenciamento inteligente de versões.

**Características principais:**
- 🗜️ Compressão em múltiplos formatos (tar.gz, zip)
- 🎯 Exclusão inteligente de arquivos (node_modules, caches, builds)
- 📊 Estatísticas detalhadas e progresso em tempo real
- 🔐 Verificação de integridade com hash MD5
- 📑 Índice JSON para rastreamento de todos os backups
- 🧹 Limpeza automática de backups antigos
- 🔄 Sistema de restauração interativo
- 🎨 Detecção automática de tipo de projeto

```bash
# Exemplo de uso
python3 backup/script.py -d /projeto --formato tar
python3 backup/script.py --listar-backups
python3 backup/script.py --limpar-antigos
```

**[📖 Documentação Completa](backup/DOCUMENTACAO_TECNICA.md)**

---

### 🧹 Cleaning Script
Ferramenta de limpeza inteligente para liberar espaço em disco removendo arquivos desnecessários.

**Características principais:**
- 📦 Remoção de node_modules antigos (>30 dias)
- 🗂️ Limpeza de arquivos temporários (*.tmp, *.bak, etc.)
- 💾 Remoção de caches de build (.next, dist, __pycache__)
- 📋 Limpeza de logs antigos (>7 dias)
- 👁️ Modo preview seguro (mostra antes de remover)
- 📊 Relatórios detalhados com estimativa de espaço
- ⚡ Performance otimizada para grandes diretórios
- 🎯 Limpeza seletiva ou completa

```bash
# Exemplo de uso
python3 cleaning/script.py              # Modo preview
python3 cleaning/script.py --ex         # Executa limpeza
python3 cleaning/script.py --a-n        # Apenas node_modules
python3 cleaning/script.py --ex --c     # Limpeza completa
```

**[📖 Documentação Completa](cleaning/DOCUMENTACAO_TECNICA.md)**

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.6 ou superior
- Sistema operacional: **Linux** (testado em Arch-based)

> **📝 Nota:** Os scripts atuais foram desenvolvidos para Linux. Alguns paths (como `~/Área de trabalho`) podem precisar ser ajustados conforme sua configuração específica.

### Clone o Repositório

```bash
git clone https://github.com/montezuma-p/utils-python-scripts.git
cd utils-python-scripts
```

### Uso Imediato

Não há dependências externas! Todos os scripts utilizam apenas bibliotecas padrão do Python.

```bash
# Backup
python3 backup/script.py --help

# Limpeza
python3 cleaning/script.py --help
```

### Opcional: Adicionar ao PATH

Para executar os scripts de qualquer lugar:

```bash
# Linux/macOS
echo 'export PATH="$PATH:$HOME/utils-python-scripts/backup"' >> ~/.bashrc
echo 'export PATH="$PATH:$HOME/utils-python-scripts/cleaning"' >> ~/.bashrc
source ~/.bashrc

# Agora pode executar:
script.py --help
```

---

## 📚 Documentação

Cada script possui documentação técnica completa e detalhada:

| Script | Documentação |
|--------|-------------|
| **Backup** | [DOCUMENTACAO_TECNICA.md](backup/DOCUMENTACAO_TECNICA.md) | 
| **Cleaning** | [DOCUMENTACAO_TECNICA.md](cleaning/DOCUMENTACAO_TECNICA.md) | 

A documentação técnica cobre:
- 🏗️ Arquitetura e design do código
- 🔧 Explicação detalhada de cada componente
- 💡 Casos de uso práticos
- 🛠️ Sugestões de modificação e extensão
- ⚠️ Limitações conhecidas
- 📖 Boas práticas de uso

---
## 🛤️ Roadmap

### Próximos commits

#### 🎲 Personal Utils Bundle (Próximo Lançamento)
Pacote completo de utilitários para uso pessoal e diário.

> **🌍 Multiplataforma:** Ao contrário dos scripts v1.0, estes utilitários serão **100% multiplataforma** (Linux, macOS, Windows), usando apenas Python puro sem dependências de sistema operacional! Uma coleção de ferramentas individuais para tarefas cotidianas. Cada utilitário será independente e pode ser usado separadamente ou em conjunto.

---


#### 📊 System Monitor (Em Breve)
Script de monitoramento de sistema com outputs simplificados e legíveis.

Transformará comandos complexos de monitoramento em visualizações bonitas e fáceis de interpretar.

---

## 💻 Requisitos do Sistema

### Scripts v1.0 (Backup & Cleaning)

| Componente | Requisito Mínimo | Recomendado |
|------------|------------------|-------------|
| Python | 3.6+ | 3.9+ |
| RAM | 512 MB | 2 GB |
| Espaço em Disco | 100 MB | 1 GB |
| OS | **Linux** | Arch-based Linux |

> **⚠️ Nota sobre Compatibilidade:**  
> Os scripts atuais (Backup e Cleaning) foram desenvolvidos e testados em **Linux (Arch-based)**.  
> Devem funcionar em outras distribuições Linux, mas alguns **paths podem precisar de ajustes** conforme a configuração do usuário (ex: `~/Área de trabalho` vs `~/Desktop`).  
> Suporte para Windows e macOS não foi testado na v1.0.

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Este projeto está em constante evolução.

### Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/NovaFuncionalidade`)
5. **Abra** um Pull Request

### Diretrizes

- ✅ Mantenha o código limpo e documentado
- ✅ Adicione testes quando apropriado
- ✅ Atualize a documentação técnica
- ✅ Siga o estilo de código existente
- ✅ Use apenas bibliotecas padrão do Python (quando possível)

### Reportar Bugs

Encontrou um bug? Abra uma [issue](https://github.com/montezuma-p/utils-python-scripts/issues) com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs obtido
- Versão do Python e sistema operacional
- Logs de erro (se aplicável)

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Pedro Montezuma Loureiro**
- GitHub: [@montezuma-p](https://github.com/montezuma-p)
- Email: pedromontezumaloureiro@gmail.com

---

## 🌟 Agradecimentos

- Comunidade Python pela excelente linguagem e ecossistema
- Todos os contribuidores que ajudam a melhorar este projeto
- Você, por usar e apoiar este projeto! ⭐

---

## 📊 Estatísticas do Projeto

![GitHub stars](https://img.shields.io/github/stars/montezuma-p/utils-python-scripts?style=social)
![GitHub forks](https://img.shields.io/github/forks/montezuma-p/utils-python-scripts?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/montezuma-p/utils-python-scripts?style=social)

---

<div align="center">

**⭐ Se este projeto foi útil para você, considere dar uma estrela! ⭐**

**Desenvolvido com ❤️ para a comunidade de desenvolvedores**

[⬆ Voltar ao topo](#️-utils-python-scripts)

</div>
