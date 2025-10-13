# Documentação Técnica - Script de Backup Universal

## 1. Visão Geral

O Script de Backup Universal é uma ferramenta desenvolvida em Python 3 para realizar backups completos e inteligentes de diretórios do sistema. A solução implementa funcionalidades avançadas como compressão adaptativa, filtragem de arquivos, rastreamento de backups e gerenciamento automático de versões antigas.

## 2. Arquitetura do Sistema

### 2.1 Estrutura de Classes

O script é construído em torno de uma única classe principal chamada `BackupUniversal`, que encapsula toda a lógica de backup. Esta abordagem orientada a objetos permite manter o estado interno (estatísticas, configurações) e facilita a extensão futura do código.

A classe mantém atributos de instância que definem o comportamento do backup, incluindo o diretório de destino dos backups (fixado em `~/backups`), padrões de exclusão predefinidos e personalizados, além de contadores estatísticos para monitoramento do processo.

### 2.2 Módulos e Dependências

O script utiliza exclusivamente bibliotecas da biblioteca padrão do Python, garantindo portabilidade e ausência de dependências externas. Os módulos importados incluem:

- **os, sys, pathlib.Path**: Manipulação de sistema de arquivos e caminhos multiplataforma
- **json**: Persistência do índice de backups em formato estruturado
- **tarfile, zipfile**: Compressão em múltiplos formatos (tar.gz e zip)
- **hashlib**: Geração de checksums MD5 para verificação de integridade
- **argparse**: Interface de linha de comando robusta e autodocumentada
- **datetime, timedelta**: Gerenciamento de timestamps e políticas de retenção
- **fnmatch**: Correspondência de padrões estilo glob para exclusão de arquivos
- **shutil**: Operações de alto nível em arquivos (importado mas não utilizado ativamente)

## 3. Componentes Principais

### 3.1 Sistema de Exclusão Inteligente

O método `_deve_excluir` implementa um sistema de filtragem baseado em padrões glob. O script mantém dois conjuntos de padrões: padrões predefinidos (incluindo artefatos de build, caches de IDEs, arquivos temporários e repositórios Git) e padrões personalizados adicionados pelo usuário.

A exclusão opera no nível de nome de arquivo ou diretório, utilizando `fnmatch.fnmatch` para correspondência de padrões. Esta abordagem permite sintaxes como `*.tmp`, `__pycache__` ou `node_modules`, proporcionando flexibilidade sem complexidade regex.

Durante a travessia de diretórios com `os.walk`, o script modifica a lista de diretórios in-place para evitar a descida em pastas excluídas, otimizando significativamente o tempo de processamento em projetos grandes.

### 3.2 Cálculo de Tamanho e Estatísticas

O método `_calcular_tamanho_diretorio` realiza uma pré-análise completa do diretório antes de iniciar o backup. Esta etapa calcula o tamanho total dos dados a serem copiados e o número de arquivos, respeitando as regras de exclusão.

A implementação percorre recursivamente a árvore de diretórios, acumulando tamanhos apenas de arquivos que não serão excluídos. Exceções de IO são silenciosamente capturadas para lidar com arquivos inacessíveis sem interromper o processo.

Os resultados são formatados por `_formatar_tamanho`, que converte bytes em unidades legíveis (B, KB, MB, GB, TB, PB) usando divisões sucessivas por 1024, mantendo uma casa decimal de precisão.

### 3.3 Detecção Automática de Tipo de Projeto

O método `_obter_info_diretorio` implementa heurísticas para classificar automaticamente o tipo de projeto baseando-se em arquivos marcadores. A presença de `package.json` identifica projetos Node.js, `requirements.txt` ou `setup.py` indicam projetos Python, `pom.xml` sinaliza projetos Java, e a pasta `.git` marca repositórios Git.

Esta classificação é armazenada nos metadados do backup e pode ser utilizada para aplicar políticas de backup diferenciadas ou para organização visual na listagem de backups.

### 3.4 Processo de Criação de Backup

O método `criar_backup` orquestra todo o fluxo de backup, desde validação inicial até o relatório final. O processo segue estas etapas:

**Validação e Preparação**: O caminho de origem é resolvido e validado quanto à existência e tipo (deve ser um diretório). Informações do diretório são coletadas, incluindo nome, tipo e timestamp de última modificação.

**Análise Pré-Backup**: O sistema calcula o tamanho total e número de arquivos, apresentando estas informações ao usuário. Em modo interativo (não silencioso), o usuário é questionado sobre a escolha do formato de compressão (tar.gz ou zip) e deve confirmar explicitamente a operação.

**Nomenclatura de Arquivos**: O nome do arquivo de backup é gerado combinando um prefixo (personalizado ou padrão baseado no nome do diretório), um timestamp no formato `YYYYMMDD_HHMMSS` e a extensão apropriada (.tar.gz ou .zip).

**Compressão**: Dependendo do formato escolhido, o script utiliza diferentes estratégias. Para tar.gz, o modo de compressão é sempre gzip, com nível de compressão variando entre 6 (padrão) e 9 (máximo). Para zip, utiliza-se `ZIP_DEFLATED` com compresslevel configurável.

**Registro de Metadados**: Após conclusão bem-sucedida, o backup é registrado no arquivo JSON de índice (`indice_backups.json`), incluindo informações como tamanhos original e comprimido, taxa de compressão, contagem de arquivos, hash MD5 e timestamp.

### 3.5 Adição de Arquivos aos Arquivos Comprimidos

Os métodos `_adicionar_arquivos_ao_tar` e `_adicionar_arquivos_ao_zip` implementam a lógica de travessia e adição de arquivos aos arquivos comprimidos. Ambos compartilham estrutura similar:

Utilizam `os.walk` para travessia recursiva, modificando a lista de diretórios in-place para excluir pastas indesejadas. Para cada arquivo não excluído, calculam o caminho relativo apropriado e adicionam o arquivo ao arquivo comprimido.

Um sistema de progresso em tempo real informa o usuário a cada intervalo calculado (aproximadamente 2% do total de arquivos), mostrando contagem absoluta e percentual. Erros durante adição de arquivos individuais são capturados e reportados, mas não interrompem o processo completo.

A principal diferença entre os métodos está na API utilizada: `tar.add()` para arquivos tar e `zipf.write()` para arquivos zip, cada um com suas particularidades de arcname e compressão.

### 3.6 Sistema de Índice JSON

O arquivo `indice_backups.json` funciona como um banco de dados simples armazenando metadados de todos os backups criados. Cada entrada contém:

- Nome do arquivo de backup e diretório de origem
- Timestamps de criação e última modificação
- Estatísticas de tamanho (original, comprimido, taxa de compressão)
- Contadores de arquivos incluídos e excluídos
- Tipo de projeto detectado
- Hash MD5 para verificação de integridade
- Flags de configuração (compressão máxima, formato)

O método `_registrar_backup` gerencia este índice, carregando o JSON existente, adicionando a nova entrada e salvando atomicamente. O uso de `ensure_ascii=False` permite caracteres Unicode nos metadados.

### 3.7 Listagem de Backups

O método `listar_backups` apresenta uma visão organizada dos backups existentes. Os backups são agrupados por diretório de origem e ordenados cronologicamente (mais recente primeiro) dentro de cada grupo.

A implementação utiliza um dicionário para agrupar backups por nome de diretório, permitindo visualização consolidada. O backup mais recente de cada grupo é marcado visualmente com um indicador especial.

Cada backup exibe data/hora de criação formatada, tamanho do arquivo comprimido com taxa de compressão, tipo de projeto e caminho completo de origem. O relatório final apresenta a contagem total de backups registrados.

### 3.8 Limpeza de Backups Antigos

O método `limpar_backups_antigos` implementa uma política de retenção baseada em dois critérios combinados: idade máxima (padrão 30 dias) e quantidade máxima por diretório (padrão 5 backups).

A lógica de limpeza opera por diretório, ordenando os backups de cada grupo cronologicamente. Os backups mais recentes são sempre preservados até o limite especificado. Backups excedentes ou anteriores à data limite são marcados para remoção.

Durante a remoção, o script tenta excluir o arquivo físico e acumula estatísticas de espaço liberado. Casos de arquivos já ausentes são tratados graciosamente, removendo apenas a entrada do índice. O índice JSON é atualizado apenas se houver remoções efetivas.

O relatório final apresenta número de backups removidos, espaço em disco liberado e contagem de backups mantidos, fornecendo visibilidade clara da operação de limpeza.

### 3.9 Restauração de Backups

O método `restaurar_backup` fornece uma interface interativa para extração de backups. O processo começa listando todos os backups disponíveis em ordem cronológica reversa, exibindo nome do diretório, data/hora e tamanho.

O usuário seleciona um backup por número e especifica o diretório de destino. Um destino padrão é sugerido (estrutura em `~/Área de trabalho/restauracao/`), mas pode ser sobrescrito.

Antes da extração, uma confirmação explícita é solicitada, mostrando claramente o arquivo de origem e o destino. A extração utiliza `tarfile.extractall()`, que preserva permissões, timestamps e estrutura de diretórios.

**Nota Técnica**: A implementação atual assume formato tar.gz para restauração. Backups em formato zip requerem tratamento especial não implementado na versão atual.

## 4. Interface de Linha de Comando

### 4.1 Arquitetura do Parser

O script utiliza `argparse` para criar uma interface de linha de comando completa e autodocumentada. O parser é configurado com `RawDescriptionHelpFormatter` para preservar a formatação do texto de ajuda, especialmente útil na seção de exemplos.

### 4.2 Argumentos Disponíveis

**-d, --diretorio**: Especifica o caminho do diretório para backup. Aceita caminhos absolutos ou relativos, com expansão automática de til (`~`). Na ausência deste argumento, o comportamento padrão tenta fazer backup do diretório raiz (`/`), o que geralmente requer privilégios elevados.

**--nome**: Define um nome personalizado para o arquivo de backup. Este nome é prefixado ao timestamp automático. Útil para backups temáticos ou categorizados.

**--compressao-maxima**: Flag booleana que ativa compressão nível 9 (máximo). Resulta em arquivos menores ao custo de maior tempo de processamento e uso de CPU. Recomendado para backups arquivísticos ou com bandwidth limitado.

**--excluir**: Aceita string com padrões de exclusão separados por vírgula. Estes padrões são adicionados à lista padrão, não a substituem. Sintaxe segue padrões glob do fnmatch.

**--silencioso**: Elimina todas as confirmações interativas, executando o backup automaticamente. Quando este flag está ativo, o argumento `--formato` torna-se obrigatório.

**--formato**: Especifica o formato de compressão: `tar` para arquivos .tar.gz (ideal para Linux/macOS) ou `zip` para arquivos .zip (melhor compatibilidade com Windows). Obrigatório em modo silencioso.

**--listar-backups**: Exibe listagem formatada de todos os backups registrados e termina. Não realiza operação de backup.

**--limpar-antigos**: Executa apenas a rotina de limpeza de backups antigos conforme política de retenção e termina.

**--restaurar**: Inicia interface interativa de restauração e termina.

### 4.3 Fluxo de Execução do Main

A função `main()` instancia a classe `BackupUniversal`, processa argumentos de linha de comando e despacha para a operação apropriada. A lógica de despacho verifica flags de operação especial (listar, limpar, restaurar) antes de executar um backup padrão.

Após backup bem-sucedido, o script apresenta dicas de boas práticas, incluindo frequência recomendada, uso de limpeza automática, testes de restauração e sincronização com nuvem.

## 5. Tratamento de Erros e Robustez

### 5.1 Estratégias de Recuperação

O script implementa tratamento de exceções em múltiplos níveis. Operações de IO em arquivos individuais são envolvidas em blocos try-except, permitindo que o processo continue mesmo se alguns arquivos forem inacessíveis.

Durante criação de backup, se ocorrer erro após iniciar a compressão, o script tenta remover o arquivo parcial para evitar arquivos corrompidos no diretório de backups.

### 5.2 Validações de Entrada

Todas as operações validam a existência e tipo dos caminhos antes de prosseguir. Mensagens de erro descritivas são apresentadas com emoji indicador de problema, facilitando diagnóstico rápido.

O modo silencioso inclui validação adicional para garantir que o formato seja especificado, prevenindo falhas em ambiente automatizado.

### 5.3 Lidando com Arquivos Problemáticos

Ao calcular tamanhos de diretório, exceções `OSError` e `IOError` são capturadas silenciosamente. Esta abordagem permite processar diretórios com arquivos bloqueados, links simbólicos quebrados ou permissões insuficientes.

Durante adição de arquivos ao arquivo comprimido, erros são reportados com mensagem de aviso incluindo o nome do arquivo problemático, mas o processo continua para os demais arquivos.

## 6. Aspectos de Performance

### 6.1 Otimização de Travessia

A modificação in-place da lista de diretórios em `os.walk` evita travessia de subárvores excluídas, resultando em economia significativa de tempo e IO em projetos com grandes dependências (como `node_modules` com milhares de arquivos).

### 6.2 Feedback de Progresso

O sistema de progresso calcula intervalos dinâmicos baseados no total de arquivos estimado, apresentando atualizações a aproximadamente cada 2% de progresso. Isso equilibra informação útil ao usuário sem gerar saída excessiva.

O cálculo de intervalo usa `max(100, total_estimado // 50)` para garantir um mínimo de 100 arquivos entre relatórios, evitando spam em diretórios pequenos.

### 6.3 Considerações sobre Hash MD5

O cálculo de hash MD5 processa o arquivo em chunks de 4096 bytes, equilibrando uso de memória e performance. Esta abordagem permite hashear arquivos grandes sem carregar todo o conteúdo em memória.

**Nota de Segurança**: MD5 é usado aqui apenas para verificação de integridade de dados, não para segurança criptográfica. Para aplicações que requerem garantias criptográficas, considere migrar para SHA-256.

## 7. Estrutura de Dados do Índice

### 7.1 Esquema de Metadados

Cada entrada no índice JSON segue esta estrutura:

```python
{
    "arquivo": "nome_do_backup.tar.gz",
    "diretorio_origem": "/caminho/completo/origem",
    "nome_diretorio": "nome_da_pasta"
}
```

Os campos numéricos incluem `tamanho_original`, `tamanho_backup` (ambos em bytes), `taxa_compressao` (percentual), `total_arquivos`, `arquivos_excluidos` e `diretorios_excluidos`.

Campos temporais utilizam formato ISO 8601 (`data_criacao`), garantindo parsing e comparação confiáveis. Campos booleanos incluem `compressao_maxima` e o campo string `formato` indica o tipo de arquivo (`tar` ou `zip`).

### 7.2 Evolução do Esquema

O uso de `backup.get('campo', valor_padrao)` em várias partes do código demonstra compatibilidade retroativa. Campos adicionados em versões posteriores não quebram a leitura de índices antigos.

Para adicionar novos campos ao esquema, basta incluí-los no dicionário passado para `_registrar_backup` e usar acesso com `.get()` ao ler, fornecendo valores padrão sensatos.

## 8. Casos de Uso

### 8.1 Backup Automatizado com Cron

O modo silencioso foi projetado especificamente para integração com cron ou systemd timers. Exemplo de entrada crontab para backup semanal:

```bash
0 2 * * 0 /usr/bin/python3 /caminho/script.py -d /home/user/projetos --silencioso --formato tar
```

Combine com `--limpar-antigos` em tarefa mensal para gerenciamento automático de retenção.

### 8.2 Backup Pré-Deploy

Desenvolvedores podem integrar o script em pipelines de CI/CD para criar snapshots antes de deployments. O hash MD5 registrado permite verificação de integridade do backup.

### 8.3 Migração de Sistemas

Use o script para criar backups portáveis de ambientes de desenvolvimento. Backups em formato zip garantem máxima compatibilidade ao migrar entre sistemas operacionais diferentes.

### 8.4 Arquivamento de Projetos

Para projetos finalizados, use compressão máxima para arquivamento de longo prazo. O tipo de projeto detectado ajuda na organização de múltiplos arquivos.

## 9. Sugestões de Modificação

### 9.1 Implementação de Backup Incremental

Atualmente o script realiza apenas backups completos. Para adicionar backups incrementais:

1. Armazene timestamps de última modificação de arquivos no índice
2. Durante backup, compare timestamps e inclua apenas arquivos modificados
3. Adicione campo de referência ao backup completo anterior
4. Implemente lógica de restauração que combine backup completo com incrementais

Esta modificação reduziria significativamente tempo e espaço para backups frequentes de grandes volumes de dados.

### 9.2 Suporte a Backup Diferencial

Similar ao incremental, mas sempre comparando com o último backup completo. Requer:

1. Marcação explícita de backups como "completo" ou "diferencial"
2. Lógica para identificar o último backup completo
3. Restauração em dois passos: completo + diferencial

O diferencial simplifica a restauração comparado ao incremental (apenas dois arquivos) mantendo boa economia de espaço.

### 9.3 Compressão com Outros Algoritmos

Para adicionar suporte a formatos como .7z ou .tar.bz2:

1. Adicione opção ao argumento `--formato`
2. Implemente métodos auxiliares `_adicionar_arquivos_ao_7z` ou similares
3. Atualize lógica de nomenclatura de arquivos
4. Modifique `restaurar_backup` para detectar e extrair múltiplos formatos

Algoritmos como LZMA (7z) oferecem compressão superior ao gzip em muitos casos.

### 9.4 Criptografia de Backups

Para backups contendo dados sensíveis, adicione criptografia:

1. Integre biblioteca como `cryptography` (requer dependência externa)
2. Adicione argumento `--criptografar` com opção de senha
3. Criptografe o arquivo comprimido após criação
4. Armazene indicador de criptografia nos metadados
5. Solicite senha durante restauração de backups criptografados

Use algoritmos modernos como AES-256-GCM para segurança adequada.

### 9.5 Verificação de Integridade Automática

Implemente verificação periódica de backups:

1. Adicione comando `--verificar` que testa integridade de arquivos comprimidos
2. Recalcule hash MD5 e compare com valor registrado
3. Tente listar conteúdo do arquivo sem extrair
4. Marque backups corrompidos no índice
5. Notifique usuário de problemas detectados

Esta funcionalidade aumenta confiabilidade em backups de longo prazo.

### 9.6 Backup Remoto e Sincronização

Estenda o script para suportar destinos remotos:

1. Adicione suporte para protocolos como SSH/SCP ou rsync
2. Implemente upload automático após criação de backup local
3. Adicione metadados de localização remota ao índice
4. Implemente sincronização bidirecional com verificação de checksums

Integração com serviços de nuvem (S3, Google Cloud Storage) também é possível via suas SDKs.

### 9.7 Interface Gráfica

Para usuários não técnicos, desenvolva GUI:

1. Use biblioteca como Tkinter (incluída) ou PyQt
2. Crie assistente com seleção visual de diretórios
3. Mostre barra de progresso gráfica durante backup
4. Implemente navegador visual do índice de backups
5. Adicione agendador integrado de backups recorrentes

A lógica de backend existente pode ser reutilizada quase integralmente.

### 9.8 Notificações e Logging

Melhore observabilidade com sistema de notificações:

1. Integre módulo `logging` do Python para logs estruturados
2. Adicione níveis de verbosidade configuráveis
3. Implemente notificações desktop via `notify-send` (Linux) ou equivalentes
4. Envie emails com relatórios de backup via SMTP
5. Adicione webhook para integração com sistemas de monitoramento

Mantenha compatibilidade com saída atual para scripts dependentes.

### 9.9 Exclusões Baseadas em Tamanho

Adicione capacidade de excluir arquivos por tamanho:

1. Adicione argumento `--tamanho-maximo` com valor em MB
2. Durante travessia, verifique tamanho antes de adicionar arquivo
3. Registre arquivos excluídos por tamanho separadamente nas estatísticas
4. Considere implementar exclusão de tipos mime específicos

Útil para evitar inclusão acidental de arquivos ISO, VMs ou dumps de banco de dados.

### 9.10 Paralelização da Compressão

Para grandes volumes de dados em sistemas multicore:

1. Use módulo `multiprocessing` ou `concurrent.futures`
2. Divida arquivos em lotes processados em paralelo
3. Combine resultados em arquivo final ou crie múltiplos volumes
4. Adicione flag `--threads` para controlar paralelismo

Esta modificação requer cuidado com ordem de arquivos e sincronização.

## 10. Boas Práticas e Recomendações

### 10.1 Frequência de Backup

Para dados críticos, estabeleça rotina de backup diária ou semanal. Use cron ou Task Scheduler para automação. A regra 3-2-1 recomenda: 3 cópias dos dados, em 2 mídias diferentes, com 1 cópia offsite.

### 10.2 Testes de Restauração

Realize testes periódicos de restauração para validar integridade dos backups. Um backup não testado é potencialmente inútil. Agende testes trimestrais em ambiente não-produtivo.

### 10.3 Monitoramento de Espaço

Configure alertas de espaço em disco no diretório de backups. Execute `--limpar-antigos` regularmente ou configure política mais agressiva se necessário.

### 10.4 Documentação de Exclusões

Documente padrões de exclusão personalizados específicos do projeto. Mantenha lista em arquivo README ou comentário no script de automação.

### 10.5 Versionamento do Script

Se modificar o script, mantenha controle de versão (git). Incremente versão nos metadados de backup para rastreabilidade. Considere campo `script_version` no índice JSON.

## 11. Limitações Conhecidas

### 11.1 Escalabilidade em Sistemas de Arquivos Grandes

O cálculo pré-backup de tamanho percorre toda a árvore de diretórios, o que pode levar minutos em sistemas de arquivos com milhões de arquivos. Para estes cenários, considere adicionar flag `--sem-pre-calculo`.

### 11.2 Restauração de Backups ZIP

A implementação atual de `restaurar_backup` assume formato tar.gz. Backups criados em formato zip requerem extração manual ou modificação do método para detectar e extrair ambos os formatos.

### 11.3 Links Simbólicos

O comportamento com links simbólicos segue o padrão de `tar.add()` e `zipf.write()`, que por padrão seguem os links. Isso pode resultar em duplicação de dados ou loops infinitos. Considere adicionar flag `--preservar-links`.

### 11.4 Compatibilidade de Sistema Operacional

**Este script foi desenvolvido e testado exclusivamente em Linux (Arch-based).**

- **Linux**: Funcional em distribuições Arch-based. Deve funcionar em outras distros, mas paths específicos (como `~/backups`) podem precisar ajuste
- **Windows/macOS**: Não testado. Atributos de permissão Unix podem não ser preservados corretamente. O formato zip oferece melhor compatibilidade teórica, mas não há garantias sem testes

**Paths Específicos do Usuário**: O diretório padrão assume estrutura típica de Linux. Usuários com configurações diferentes precisarão modificar o caminho ou especificar via argumento `-d`.

### 11.5 Arquivos Abertos e Bloqueados

Arquivos atualmente abertos ou bloqueados por outros processos podem falhar ao serem lidos. O script captura estes erros e continua, mas os arquivos problemáticos não serão incluídos no backup.

## 12. Considerações de Segurança

### 12.1 Privilégios de Execução

Execute o script com privilégios mínimos necessários. Evite executar como root/administrador a menos que seja absolutamente necessário. Configure permissões 700 no diretório de backups para proteger contra acesso não autorizado.

### 12.2 Conteúdo Sensível

Backups podem conter dados sensíveis (credenciais, chaves, dados pessoais). Considere implementar criptografia ou armazenar backups em volumes criptografados.

### 12.3 Validação de Entrada

O script não sanitiza completamente nomes de arquivo ou caminhos. Evite executar com entradas não confiáveis ou adicione validação rigorosa para ambientes multi-usuário.

### 12.4 Integridade Criptográfica

Hash MD5 não é resistente a ataques deliberados. Para ambientes onde integridade criptográfica é crítica, implemente SHA-256 ou superior.

## 13. Glossário Técnico

**Glob Pattern**: Sintaxe de correspondência de padrões usando caracteres curinga como `*` (qualquer sequência) e `?` (qualquer caractere único).

**Checksum/Hash**: Valor calculado que identifica unicamente um arquivo, usado para verificar integridade.

**Taxa de Compressão**: Percentual de redução de tamanho calculado como `(tamanho_original - tamanho_comprimido) / tamanho_original * 100`.

**Arcname**: Nome do arquivo dentro do arquivo comprimido, geralmente um caminho relativo que preserva estrutura de diretórios.

**In-place Modification**: Modificação de uma estrutura de dados (lista) durante iteração sobre ela, técnica usada para poda de diretórios em `os.walk`.

**Metadata/Metadados**: Dados sobre dados, como timestamp de criação, tamanho de arquivo, tipo de projeto.

**Atomicidade**: Propriedade de operação que completa inteiramente ou falha completamente, sem estados intermediários inconsistentes.

---

**Versão da Documentação**: 1.0  
**Data**: Outubro de 2025  
**Compatibilidade**: Python 3.6+  
**Sistema Operacional**: Linux (testado em Arch-based, deve funcionar em outras distros)  
**Nota**: Alguns paths podem precisar ajuste dependendo da configuração do usuário  
**Licença**: [MIT License](../LICENSE)
