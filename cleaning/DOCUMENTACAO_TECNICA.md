# Documentação Técnica - Script de Limpeza do Sistema

## 1. Visão Geral

O Script de Limpeza do Sistema é uma ferramenta Python 3 desenvolvida para automatizar a remoção de arquivos desnecessários em ambientes de desenvolvimento. O script identifica e remove de forma inteligente diretórios node_modules antigos, arquivos temporários, caches de build e logs obsoletos, liberando espaço em disco significativo.

## 2. Arquitetura do Sistema

### 2.1 Estrutura de Classes

O script é construído em torno da classe `LimpadorSistema`, que encapsula toda a lógica de escaneamento e limpeza. Esta abordagem orientada a objetos facilita a manutenção do estado interno (contadores, listas de arquivos) e permite futuras extensões modulares.

A classe mantém quatro atributos principais de instância que armazenam os resultados do escaneamento: listas de diretórios node_modules, arquivos temporários, diretórios de cache e arquivos de log. Adicionalmente, três contadores rastreiam estatísticas da operação: espaço total liberado, número de arquivos removidos e número de diretórios removidos.

### 2.2 Dependências e Módulos

O script utiliza exclusivamente bibliotecas da biblioteca padrão do Python, garantindo portabilidade total sem necessidade de instalação de pacotes externos:

- **os, shutil**: Operações de baixo nível no sistema de arquivos, incluindo remoção recursiva de diretórios
- **pathlib.Path**: Manipulação moderna e multiplataforma de caminhos de arquivos
- **argparse**: Construção de interface de linha de comando autodocumentada
- **subprocess**: Importado mas não utilizado ativamente na versão atual (reservado para futuras integrações)
- **time, datetime**: Gerenciamento de timestamps para identificação de arquivos antigos e medição de performance

### 2.3 Diretório Base de Operação

O script opera a partir de um diretório base definido no construtor da classe como `Path.home() / "Área de trabalho"`. Esta escolha assume estrutura típica de sistemas Linux em português brasileiro. Para adaptação a outros sistemas ou idiomas, este caminho deve ser modificado.

A travessia recursiva de diretórios utiliza `os.walk`, que fornece controle granular sobre a navegação da árvore de arquivos. Esta abordagem é mais eficiente que alternativas como `Path.rglob` para travessias com filtragem complexa.

## 3. Componentes Principais

### 3.1 Sistema de Escaneamento

O método `escanear_sistema` orquestra o processo de descoberta de arquivos candidatos à remoção. Este método delega para quatro métodos especializados, cada um responsável por identificar um tipo específico de alvo.

A arquitetura de escaneamento é deliberadamente separada da execução de limpeza. Esta separação permite o modo preview, onde o usuário visualiza o que seria removido antes de confirmar a operação. Este padrão de design aumenta significativamente a segurança do script.

#### 3.1.1 Detecção de node_modules

O método `_encontrar_node_modules` implementa busca por diretórios node_modules durante a travessia do sistema de arquivos. Para cada ocorrência encontrada, o método verifica se o diretório atende aos critérios de remoção utilizando `_is_old_or_inactive`.

A verificação de idade baseia-se no timestamp de última modificação (mtime) do diretório. Um node_modules é considerado candidato à remoção se não foi modificado nos últimos 30 dias. Este critério assume que projetos ativos regularmente reinstalam ou atualizam dependências.

Cada entrada identificada é armazenada como dicionário contendo três campos: o caminho completo (path), o tamanho calculado em bytes (size) e o nome do projeto pai (projeto). Esta estrutura permite geração de relatórios informativos posteriores.

#### 3.1.2 Identificação de Arquivos Temporários

O método `_encontrar_arquivos_temp` utiliza padrões glob para localizar arquivos temporários comuns. A lista de padrões inclui extensões típicas de arquivos temporários e artefatos de editores e sistemas operacionais.

Os padrões implementados cobrem:
- Arquivos temporários explícitos (*.tmp, *.temp)
- Arquivos de backup de editores (*.bak, *.swp, *~)
- Metadados de sistemas operacionais (.DS_Store do macOS, Thumbs.db do Windows)
- Arquivos de log genéricos (*.log)

A utilização de `rglob` com padrões glob fornece sintaxe expressiva e performance adequada para buscas recursivas. Cada arquivo encontrado é validado com `is_file()` para evitar inclusão acidental de diretórios.

#### 3.1.3 Localização de Caches

O método `_encontrar_caches` busca diretórios de cache específicos de frameworks e ferramentas populares. A lista hardcoded de nomes de cache reflete as ferramentas mais comuns em ambientes de desenvolvimento web e Python.

Os caches detectados incluem:
- Frameworks JavaScript (.next do Next.js, .nuxt do Nuxt.js)
- Outputs de build (dist, build)
- Caches genéricos (.cache)
- Caches Python (__pycache__, .pytest_cache)

Esta abordagem baseada em lista conhecida é menos flexível que detecção baseada em heurísticas, mas oferece maior precisão e segurança. Adicionar suporte a novos caches requer simplesmente expandir a lista `cache_dirs`.

#### 3.1.4 Busca de Logs Antigos

O método `_encontrar_logs` identifica arquivos de log com mais de 7 dias de idade. A busca utiliza `rglob('*.log')` para localizar todos os arquivos com extensão .log recursivamente.

O critério temporal de 7 dias é mais agressivo que os 30 dias usados para node_modules. Esta diferença reflete a natureza descartável de logs em ambientes de desenvolvimento versus o custo de reinstalar dependências.

A verificação de idade é implementada em `_is_old_file`, que calcula a diferença entre o timestamp atual e o mtime do arquivo. Erros durante acesso ao arquivo (permissões, arquivo removido entre escaneamento e verificação) são silenciosamente capturados, retornando False para manter a operação robusta.

### 3.2 Cálculo de Tamanho

O método `_get_dir_size` implementa cálculo recursivo do tamanho de diretórios. A implementação utiliza `os.walk` para travessia eficiente e acumula tamanhos individuais de arquivos usando `os.path.getsize`.

A abordagem de acumulação individual é necessária porque diretórios em sistemas Unix-like não possuem tamanho próprio significativo - o tamanho reportado é apenas da entrada de diretório, não do conteúdo. O método percorre toda a subárvore somando cada arquivo.

Exceções durante acesso a arquivos individuais são capturadas silenciosamente. Esta estratégia permite calcular tamanhos aproximados mesmo em diretórios com alguns arquivos inacessíveis, evitando falha completa da operação por um único arquivo problemático.

A performance deste método pode ser significativa em diretórios com milhões de arquivos (node_modules complexos). Para otimização futura, considere implementar cache de tamanhos ou cálculo paralelo.

### 3.3 Formatação de Tamanhos

O método `_format_size` converte valores em bytes para formato legível ao usuário. A implementação utiliza divisões sucessivas por 1024 (não 1000) para conformidade com unidades binárias tradicionais (KiB, MiB, etc.), embora exiba rótulos simplificados (KB, MB).

A iteração através de unidades progressivamente maiores termina quando o valor se torna menor que 1024, garantindo escolha da unidade mais apropriada. Para valores extremamente grandes, a função suporta até terabytes, retornando petabytes como caso final.

A formatação inclui uma casa decimal de precisão, balanceando legibilidade e informação útil. Para contextos onde precisão maior é necessária, considere parametrizar o número de casas decimais.

### 3.4 Sistema de Relatórios

O método `mostrar_relatorio` gera visualização estruturada dos resultados do escaneamento. O relatório é dividido em seções correspondentes aos diferentes tipos de alvos, cada uma mostrando contagem de itens e tamanho total.

O parâmetro booleano `d` (detalhado) controla o nível de verbosidade. No modo padrão (não detalhado), o relatório apresenta apenas estatísticas agregadas e os 10 maiores node_modules encontrados. No modo detalhado, lista completa de todos os itens em todas as categorias.

Esta dualidade de apresentação é importante para usabilidade. Ambientes com centenas ou milhares de itens candidatos tornariam relatório completo ilegível. O modo resumido fornece visão geral rápida, enquanto o detalhado permite auditoria completa antes de operações destrutivas.

O cálculo de espaço total agregado percorre todas as listas de candidatos somando os tamanhos individuais. Este valor é exibido de forma destacada ao final do relatório, fornecendo estimativa clara do benefício da operação.

### 3.5 Execução de Limpeza

O método `ex_limpeza` coordena a remoção efetiva dos arquivos identificados. A execução é precedida por medição de tempo usando `time.time()` para fornecer estatísticas de performance ao usuário.

A ordem de limpeza segue priorização lógica: node_modules primeiro (normalmente maiores e mais lentos), seguido por arquivos temporários, caches e finalmente logs. Esta ordenação garante que mesmo interrupções parciais liberem o máximo de espaço possível.

O método aceita dois parâmetros booleanos que modificam o comportamento:
- `a_n` (apenas node_modules): Quando True, pula limpeza de outros tipos de arquivo
- `c` (completo): Quando True, inclui remoção de logs na operação

A captura de `KeyboardInterrupt` permite cancelamento gracioso via Ctrl+C, importante para operações longas onde o usuário pode mudar de ideia ao observar o progresso.

#### 3.5.1 Remoção de node_modules

O método `_limpar_node_modules` implementa remoção dos diretórios node_modules identificados. A implementação utiliza `shutil.rmtree` para remoção recursiva eficiente de árvores de diretório completas.

Antes de cada remoção, o método verifica se o diretório ainda existe usando `path.exists()`. Esta verificação previne erros em cenários onde múltiplos node_modules foram removidos por processo externo ou onde links simbólicos apontam para o mesmo local.

Exceções durante remoção são capturadas e reportadas com mensagem informativa, mas não interrompem o processo global. Esta robustez é crucial pois frequentemente alguns node_modules contêm arquivos bloqueados ou com permissões problemáticas.

Os contadores de estatísticas são atualizados após cada remoção bem-sucedida. O tamanho liberado é acumulado usando o valor pré-calculado durante escaneamento, evitando necessidade de recálculo.

#### 3.5.2 Remoção de Arquivos Temporários

O método `_limpar_temp_files` remove arquivos temporários individuais. A operação utiliza `Path.unlink()`, método apropriado para remoção de arquivos únicos (não diretórios).

A verificação de existência pré-remoção é especialmente importante aqui, pois arquivos temporários podem ser removidos automaticamente por outros processos. A captura silenciosa de exceções previne falhas por arquivos já removidos.

A natureza de remoção de muitos arquivos pequenos torna esta operação potencialmente lenta em alguns sistemas de arquivos. Para grandes quantidades de arquivos, considere implementação paralela ou uso de chamadas em lote do sistema operacional.

#### 3.5.3 Remoção de Caches

O método `_limpar_caches` remove diretórios de cache usando mesma estratégia de `_limpar_node_modules`. A escolha de usar `shutil.rmtree` é apropriada pois caches geralmente contêm múltiplos arquivos organizados em estrutura de diretórios.

Caches de build podem conter milhares de arquivos pequenos, tornando a remoção potencialmente lenta. O método reporta progressão por diretório, não por arquivo, mantendo saída gerenciável mesmo em operações longas.

#### 3.5.4 Remoção de Logs

O método `_limpar_logs` remove arquivos de log antigos identificados. Similar à remoção de temporários, utiliza `unlink()` para remoção individual de arquivos.

A inclusão de logs na limpeza é condicional ao flag `c` (completo), refletindo que logs podem ter valor diagnóstico mesmo após vários dias. Em ambientes de produção, logs tipicamente têm políticas de retenção mais sofisticadas.

#### 3.5.5 Limpeza da Lixeira

O método `_limpar_lixeira` tenta remover conteúdo da lixeira do sistema. A implementação atual suporta apenas estrutura de lixeira do Linux (`.local/share/Trash`).

Esta funcionalidade é oportunística - falhas são capturadas e reportadas mas não impedem conclusão da operação principal. A lógica de lixeira varia significativamente entre sistemas operacionais, tornando suporte universal complexo.

A remoção de itens da lixeira é recursiva, removendo todos os arquivos encontrados. Diretórios não são explicitamente removidos, assumindo que ficam vazios após remoção dos arquivos contidos.

### 3.6 Interface de Linha de Comando

A função `main` implementa ponto de entrada do script e configuração da interface CLI usando `argparse`. O parser é configurado com `RawDescriptionHelpFormatter` para preservar formatação manual da seção de exemplos.

#### 3.6.1 Argumentos Disponíveis

**--ex (executar)**: Flag booleana que ativa modo de execução real. Na ausência deste flag, o script opera em modo preview seguro, mostrando apenas o que seria removido sem efetuar mudanças. Este padrão de default seguro previne remoções acidentais.

**--a-n (apenas node_modules)**: Limita a operação exclusivamente a remoção de diretórios node_modules. Útil quando o usuário deseja liberar espaço rapidamente focando no tipo de arquivo que geralmente consome mais espaço.

**--c (completo)**: Ativa limpeza completa incluindo logs do sistema. Por padrão, logs não são removidos devido ao seu potencial valor diagnóstico. Este flag permite ao usuário decidir explicitamente incluí-los.

**--d (detalhado)**: Ativa modo de relatório detalhado mostrando lista completa de todos os arquivos candidatos à remoção. Essencial para auditoria completa antes de operações em ambientes críticos.

#### 3.6.2 Fluxo de Execução

O fluxo de execução segue sequência bem definida:

1. Banner informativo é exibido com timestamp de execução
2. Instância de `LimpadorSistema` é criada
3. Escaneamento do sistema é executado
4. Relatório é exibido (nível de detalhe conforme flag --d)
5. Se não for modo de execução (--ex ausente), termina com mensagem de preview
6. Se for modo execução, solicita confirmação explícita do usuário
7. Aguarda resposta afirmativa (sim/s/yes/y)
8. Executa limpeza com parâmetros apropriados
9. Exibe estatísticas finais de conclusão

A confirmação explícita é implementada via `input()`, pausando execução até que o usuário forneça resposta. Esta barreira adicional de segurança é crucial dado o caráter irreversível das operações de remoção.

## 4. Aspectos de Segurança

### 4.1 Modo Preview Padrão

A decisão de design de tornar modo preview o comportamento padrão (requerendo flag --ex para execução real) é fundamentalmente uma escolha de segurança. Scripts de limpeza têm potencial destrutivo significativo, e operação acidental pode resultar em perda de trabalho.

O modo preview permite ao usuário validar completamente o que seria removido antes de comprometer-se com a operação. Esta abordagem é especialmente importante em primeira execução ou em ambientes desconhecidos.

### 4.2 Confirmação Dupla

A combinação de flag explícito (--ex) e confirmação interativa (prompt sim/não) cria duas barreiras de segurança. Mesmo que o usuário execute acidentalmente com --ex, ainda tem oportunidade de cancelar ao revisar o relatório.

A verificação de resposta aceita múltiplas variantes ('sim', 's', 'yes', 'y') para acomodar diferentes idiomas e preferências de usuário. Qualquer outra resposta resulta em cancelamento seguro.

### 4.3 Tratamento de Erros Silencioso

A captura silenciosa de exceções durante remoções individuais é uma faca de dois gumes. Por um lado, permite que a operação continue mesmo quando alguns itens não podem ser removidos. Por outro, pode mascarar problemas legítimos.

A implementação atual favorece robustez sobre visibilidade completa de erros. Para ambientes onde auditoria completa é necessária, considere adicionar modo verbose que registra todas as exceções capturadas.

### 4.4 Validação de Existência

As verificações `exists()` antes de cada remoção previnem erros mas também introduzem race condition teórica. Entre a verificação e a remoção, outro processo poderia remover o item. O tratamento de exceção posterior captura este cenário.

Esta abordagem TOCTOU (Time-of-check to time-of-use) é aceitável neste contexto pois o pior resultado é uma exceção capturada, não comportamento inseguro.

## 5. Aspectos de Performance

### 5.1 Travessia de Sistema de Arquivos

A operação mais custosa do script é a travessia inicial do sistema de arquivos durante escaneamento. Em diretórios grandes (dezenas de milhares de arquivos), esta fase pode levar minutos.

A implementação usa `os.walk` que é implementado em C e otimizado, mas ainda requer acesso a metadados de cada entrada de diretório. Em sistemas com muitos arquivos pequenos, o overhead de chamadas de sistema domina o tempo de execução.

### 5.2 Cálculo de Tamanhos

O cálculo de tamanho de cada node_modules encontrado adiciona overhead significativo. Para um node_modules típico com milhares de arquivos, o cálculo pode levar segundos.

Para melhorar performance, considere:
- Cálculo paralelo de múltiplos diretórios simultaneamente
- Cache de tamanhos baseado em mtime do diretório
- Estimativa baseada em contagem de arquivos em vez de soma exata

### 5.3 Remoção de Diretórios Grandes

A remoção de grandes árvores de diretórios com `shutil.rmtree` é relativamente eficiente, mas ainda limitada por latência de sistema de arquivos. Em SSDs modernos, a operação é geralmente I/O bound. Em HDDs tradicionais, busca de disco domina o tempo.

## 6. Limitações Conhecidas

### 6.1 Diretório Base Hardcoded

O diretório base é definido como `Path.home() / "Área de trabalho"`, assumindo estrutura específica de sistema Linux em português. Usuários com configurações diferentes precisam modificar o código fonte.

Solução futura deveria permitir especificação de diretório base via argumento de linha de comando ou arquivo de configuração.

### 6.2 Critérios de Idade Fixos

Os limites de idade (30 dias para node_modules, 7 dias para logs) são hardcoded no código. Diferentes usuários ou contextos podem requerer políticas diferentes.

Implementação de argumentos de linha de comando para estes valores aumentaria flexibilidade sem complexidade excessiva.

### 6.3 Lista de Caches Estática

A detecção de caches baseia-se em lista hardcoded de nomes conhecidos. Novos frameworks ou ferramentas requerem atualização do código fonte.

Sistema de configuração baseado em arquivo permitiria aos usuários adicionar seus próprios padrões sem modificar o script.

### 6.4 Compatibilidade de Sistema Operacional

**Este script foi desenvolvido e testado exclusivamente em Linux (Arch-based).**

Várias suposições são específicas de Linux:
- **Diretório base**: `Path.home() / "Área de trabalho"` assume nomenclatura em português brasileiro
- **Estrutura de lixeira**: `.local/share/Trash` é específica de Linux
- **Paths e convenções**: Estrutura típica de sistema Unix-like

**Compatibilidade com outras distros Linux**: Deve funcionar, mas o path `"Área de trabalho"` pode precisar ser ajustado para `"Desktop"` ou outro nome dependendo do idioma do sistema.

**Windows e macOS**: Não testados. Funcionamento não garantido sem adaptações significativas:
- macOS usa `.Trash` em vez de `.local/share/Trash`
- Windows usa Recycle Bin com estrutura completamente diferente
- Convenções de path são diferentes

Para suporte multiplataforma futuro, será necessário detecção de plataforma e lógica condicional apropriada.

## 7. Casos de Uso

### 7.1 Limpeza Semanal de Desenvolvimento

Desenvolvedores frontend frequentemente acumulam múltiplos projetos com node_modules instalados. Execução semanal do script libera gigabytes de espaço de projetos inativos.

Recomendação: Executar com --a-n para remoção rápida de node_modules, reinstalando dependências quando retomar trabalho em projeto específico.

### 7.2 Preparação para Backup

Antes de criar backups, executar o script remove arquivos regeneráveis (caches, builds, node_modules), reduzindo significativamente tamanho e tempo de backup.

Recomendação: Executar com flags completos (--ex --c) para limpeza máxima antes de backup.

### 7.3 Recuperação de Espaço Emergencial

Quando disco está quase cheio, o script fornece maneira rápida de liberar espaço significativo sem remover dados de trabalho efetivos.

Recomendação: Primeiro executar sem --ex para estimar espaço recuperável, depois executar com --ex se necessário.

### 7.4 Auditoria de Uso de Disco

Mesmo em modo preview, o script fornece visão útil de onde espaço está sendo consumido por arquivos temporários e caches.

Recomendação: Executar com --d para lista completa detalhada, permitindo identificação de projetos problemáticos.

## 8. Sugestões de Modificação

### 8.1 Configuração via Arquivo

Implementar sistema de configuração baseado em arquivo YAML ou JSON permitindo personalização de:
- Diretório base de operação
- Critérios de idade para diferentes tipos de arquivo
- Listas de padrões para detecção (caches, temporários)
- Exclusões (diretórios ou projetos específicos a nunca tocar)

Estrutura sugerida:
```python
# config.yaml
base_directory: ~/Área de trabalho
age_thresholds:
  node_modules: 30
  logs: 7
  temp_files: 1
custom_patterns:
  - pattern: "*.bak"
    age_days: 14
```

### 8.2 Modo Dry-run Melhorado

Expandir modo preview para simular exatamente o que seria feito, incluindo:
- Lista ordenada de operações
- Estimativa de tempo baseada em experiências anteriores
- Simulação de erros prováveis (permissões, arquivos bloqueados)

### 8.3 Logging Estruturado

Implementar logging apropriado usando módulo `logging` com:
- Níveis de log configuráveis (DEBUG, INFO, WARNING, ERROR)
- Saída para arquivo além de console
- Formato estruturado (JSON) para processamento automatizado
- Rotação automática de logs do próprio script

### 8.4 Paralelização

Implementar processamento paralelo para operações independentes:
- Cálculo de tamanhos de múltiplos diretórios simultaneamente
- Remoção paralela de node_modules não relacionados
- Utilizar `concurrent.futures.ProcessPoolExecutor` para CPU-bound ou `ThreadPoolExecutor` para I/O-bound

Cuidado com saturação de I/O em discos mecânicos - paralelização pode piorar performance em HDDs.

### 8.5 Detecção Inteligente de Projetos Ativos

Implementar heurísticas mais sofisticadas para determinar se projeto está ativo:
- Verificar se diretório está em repositório git com commits recentes
- Detectar arquivos de IDE recentemente acessados
- Integrar com histórico de shell para ver comandos recentes no diretório
- Verificar processos rodando que possam estar usando o diretório

### 8.6 Restauração de Emergência

Implementar sistema de backup temporário antes de remoção:
- Mover para diretório temporário em vez de deletar diretamente
- Manter por período configurável (ex: 24 horas)
- Fornecer comando de restauração em caso de remoção acidental
- Limpeza automática de backups temporários após período

### 8.7 Interface Web

Desenvolver interface web simples usando Flask ou FastAPI:
- Dashboard mostrando estatísticas de uso de disco
- Visualização interativa de resultados de escaneamento
- Seleção granular de itens para remoção
- Histórico de operações anteriores
- Agendamento de limpezas automáticas

### 8.8 Integração com Git

Adicionar inteligência específica de git:
- Detectar repositórios git e oferecer `git clean`
- Identificar branches locais não pushados (não remover estes)
- Oferecer remoção de branches mergidos
- Limpeza de arquivos ignorados pelo gitignore

### 8.9 Análise de Duplicatas

Expandir para detectar arquivos duplicados:
- Calcular checksums de arquivos
- Identificar duplicatas exatas
- Reportar potencial economia de espaço com deduplicação
- Oferecer substituição por hard links ou symlinks

### 8.10 Métricas e Tendências

Implementar coleta de métricas ao longo do tempo:
- Registrar estatísticas de cada execução
- Mostrar tendências de acumulação de lixo
- Identificar projetos que geram mais desperdício
- Sugerir frequência ótima de limpeza baseada em padrões de uso

## 9. Boas Práticas de Uso

### 9.1 Execução Regular

Execute o script semanalmente em modo preview para monitorar acumulação de arquivos desnecessários. Execução mensal com limpeza efetiva mantém espaço sob controle sem intervenção constante.

### 9.2 Auditoria Antes de Limpeza

Sempre revise relatório cuidadosamente antes de confirmar limpeza. Preste atenção especial a projetos que você sabe estar ativos - idade de node_modules pode não refletir atividade real se você não reinstalou dependências recentemente.

### 9.3 Backup Antes de Limpeza Agressiva

Para primeira execução ou limpeza completa com --c, considere criar backup de diretórios importantes. Embora o script seja conservador, melhor prevenir que remediar.

### 9.4 Teste em Ambiente Seguro

Em primeira execução, teste em diretório com projetos não críticos. Valide comportamento antes de executar em área de trabalho principal.

### 9.5 Documente Exclusões Necessárias

Se há diretórios específicos que nunca devem ser tocados, documente-os e considere implementar sistema de exclusão. Enquanto isso, simplesmente não confirme limpeza de itens críticos no modo interativo.

## 10. Troubleshooting Comum

### 10.1 "PermissionError" Durante Remoção

Alguns arquivos em node_modules podem ter permissões restritas. Execute script com sudo se apropriado, ou corrija permissões manualmente antes de executar limpeza.

### 10.2 Operação Muito Lenta

Em diretórios extremamente grandes, escaneamento pode levar muito tempo. Considere executar script em subdiretórios específicos modificando diretório base temporariamente.

### 10.3 Espaço Não Liberado Como Esperado

Verifique se há processos mantendo arquivos abertos. Em Linux, use `lsof` para identificar. Feche aplicações que possam estar usando arquivos antes de executar limpeza.

### 10.4 Caracteres Especiais em Nomes

Arquivos com caracteres especiais ou Unicode em nomes podem causar problemas. Configure locale apropriado do sistema antes de executar.

## 11. Glossário Técnico

**mtime (modification time)**: Timestamp de última modificação de arquivo ou diretório, usado para determinar idade.

**shutil.rmtree**: Função Python para remoção recursiva de árvore de diretórios completa, equivalente a `rm -rf` no Unix.

**glob pattern**: Sintaxe de correspondência de padrões usando curingas como `*` e `**` para busca recursiva.

**dry-run/preview**: Modo de operação que simula ações sem executá-las efetivamente, para validação antes de operações destrutivas.

**race condition (TOCTOU)**: Situação onde estado verifica entre verificação e uso pode mudar, potencialmente causando comportamento inesperado.

---

**Versão da Documentação**: 1.0  
**Data**: Outubro de 2025  
**Compatibilidade**: Python 3.6+  
**Sistema Operacional**: Linux (testado em Arch-based, deve funcionar em outras distros)  
**Nota**: Alguns paths podem precisar ajuste dependendo da configuração do usuário  
**Licença**: [MIT License](../LICENSE)
