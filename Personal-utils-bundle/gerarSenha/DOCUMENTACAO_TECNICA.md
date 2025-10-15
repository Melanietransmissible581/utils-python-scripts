# Documentação Técnica - Gerador de Senhas Aleatórias

## 1. Visão Geral

O Gerador de Senhas Aleatórias é uma ferramenta Python 3 desenvolvida para criar senhas seguras e personalizáveis através de linha de comando. O script implementa geração criptograficamente robusta de senhas alfanuméricas com opção de inclusão de símbolos especiais, permitindo controle granular sobre tamanho e quantidade de senhas geradas.

## 2. Arquitetura do Sistema

### 2.1 Estrutura Funcional

O script adota uma arquitetura funcional simples, sem classes, organizando a lógica em duas funções principais: `gerar_senha` para a lógica de geração e `main` para interface de linha de comando. Esta abordagem minimalista é apropriada dado o escopo focado da ferramenta.

A ausência de estado persistente ou complexidade de objetos justifica a escolha de implementação funcional sobre orientada a objetos. Cada invocação do script é completamente independente, sem necessidade de manutenção de contexto entre execuções.

### 2.2 Dependências e Módulos

O script utiliza exclusivamente bibliotecas da biblioteca padrão do Python, garantindo portabilidade total e ausência de requisitos de instalação:

- **random**: Geração de números pseudoaleatórios para seleção de caracteres. O módulo fornece o método `choice` que implementa seleção uniforme de elementos de uma sequência.
- **string**: Constantes predefinidas de conjuntos de caracteres (letras maiúsculas/minúsculas, dígitos). Estas constantes são independentes de locale e garantem comportamento consistente entre sistemas.
- **argparse**: Construção de interface de linha de comando autodocumentada com parsing robusto de argumentos e geração automática de mensagens de ajuda.

### 2.3 Segurança Criptográfica

**Nota Importante sobre Segurança**: A implementação atual utiliza o módulo `random`, que gera números pseudoaleatórios baseados no algoritmo Mersenne Twister. Este gerador **NÃO é criptograficamente seguro** e não deve ser usado para geração de senhas em contextos de alta segurança.

Para aplicações que requerem senhas criptograficamente seguras, o script deveria ser modificado para utilizar o módulo `secrets` (disponível desde Python 3.6), que fornece geração de números aleatórios apropriada para gerenciamento de segredos.

## 3. Componentes Principais

### 3.1 Função de Geração de Senha

O método `gerar_senha` implementa a lógica central de geração. A função aceita dois parâmetros que definem as características da senha resultante.

#### 3.1.1 Parâmetros de Configuração

**tamanho**: Parâmetro inteiro que define o comprimento da senha gerada em caracteres. O valor padrão é 12, que representa um equilíbrio entre segurança adequada e memorabilidade razoável. Senhas de 12 caracteres com composição alfanumérica fornecem espaço de busca de aproximadamente 62^12 combinações (≈3.2 × 10^21), oferecendo resistência substancial contra ataques de força bruta.

**incluir_simbolos**: Parâmetro booleano que controla inclusão de caracteres especiais. Quando `True` (padrão), adiciona símbolos ao conjunto de caracteres disponíveis, expandindo o espaço de possibilidades e aumentando a entropia. O conjunto de símbolos utilizado é limitado a "!@#$%&*", priorizando compatibilidade com sistemas que podem rejeitar símbolos menos comuns.

#### 3.1.2 Construção do Conjunto de Caracteres

A construção do alfabeto de geração utiliza constantes do módulo `string`:

- `string.ascii_letters`: Combinação de `ascii_lowercase` e `ascii_uppercase`, fornecendo as 52 letras do alfabeto inglês (a-z, A-Z)
- `string.digits`: Os 10 dígitos decimais (0-9)

O alfabeto base contém portanto 62 caracteres (52 letras + 10 dígitos). Quando símbolos são incluídos, 7 caracteres adicionais são concatenados, totalizando 69 caracteres possíveis.

A decisão de usar concatenação de strings para construir o alfabeto, em vez de estruturas mais complexas, prioriza legibilidade e simplicidade. Para senhas de até centenas de caracteres, o overhead de string é negligenciável.

#### 3.1.3 Algoritmo de Geração

A geração utiliza list comprehension combinada com `random.choice`:

```python
senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
```

Este padrão itera `tamanho` vezes, selecionando uniformemente um caractere aleatório do alfabeto em cada iteração. Os caracteres selecionados são acumulados em uma lista implícita pela comprehension e então unidos em uma string única via `str.join`.

**Distribuição de Probabilidade**: Cada caractere do alfabeto tem probabilidade igual de ser selecionado em cada posição. Para um alfabeto de 62 caracteres, cada caractere tem probabilidade 1/62 ≈ 1.6% de aparecer em qualquer posição específica. Esta distribuição uniforme é crucial para maximizar entropia.

**Independência de Posições**: Cada seleção é independente das anteriores. Isso significa que o mesmo caractere pode aparecer múltiplas vezes consecutivas (embora estatisticamente improvável). Alguns sistemas de geração de senha implementam garantias de diversidade (pelo menos um símbolo, pelo menos uma maiúscula, etc.), mas esta implementação prioriza aleatoriedade pura.

#### 3.1.4 Análise de Entropia

A entropia de uma senha gerada pode ser calculada como:

$$H = L \times \log_2(N)$$

Onde $L$ é o comprimento da senha e $N$ é o tamanho do alfabeto. Para os parâmetros padrão:

- Sem símbolos: $H = 12 \times \log_2(62) \approx 71.6$ bits
- Com símbolos: $H = 12 \times \log_2(69) \approx 74.5$ bits

Senhas com 70+ bits de entropia são consideradas resistentes contra ataques práticos de força bruta, mesmo considerando recursos computacionais significativos.

### 3.2 Função Principal (main)

A função `main` orquestra a interface de linha de comando e coordena múltiplas gerações de senha conforme solicitado pelo usuário.

#### 3.2.1 Configuração do Parser de Argumentos

O parser é configurado com descrição concisa (`'Gerador de senhas aleatórias'`) que aparece no texto de ajuda. A criação utiliza a classe `ArgumentParser` do módulo `argparse`, que fornece parsing robusto e mensagens de erro amigáveis.

**Argumento -tamanho / --tamanho**: Aceita valores inteiros (`type=int`) com padrão de 12 caracteres. A especificação de tipo garante conversão automática e validação, rejeitando valores não-numéricos com mensagem de erro apropriada. O texto de ajuda documenta claramente o comportamento padrão.

A convenção de nomenclatura bilíngue (`-tamanho` como forma curta e `--tamanho` como forma longa) diverge do padrão Unix típico de usar letra única para forma curta. Esta escolha prioriza clareza para usuários falantes de português sobre convenção tradicional.

**Argumento -quantidade / --quantidade**: Permite geração de múltiplas senhas em uma única invocação. O padrão de 1 senha cobre o caso de uso comum, enquanto valores maiores suportam cenários de provisionamento em massa (criação de múltiplas contas, geração de lotes para distribuição, etc.).

A geração de múltiplas senhas ocorre sequencialmente, sem reutilização de estado entre iterações. Cada senha é independentemente aleatória, mesmo quando geradas na mesma invocação.

**Flag -sem_simbolo / --sem-simbolos**: Implementado como `action='store_true'`, criando flag booleano que é `False` por padrão. A semântica negativa (flag para *remover* um recurso, não adicionar) reflete que inclusão de símbolos é comportamento padrão recomendado.

O nome do argumento usa hífen na versão longa (`--sem-simbolos`) mas underscore na versão armazenada (`args.sem_simbolos`). Esta transformação é tratada automaticamente pelo argparse, que substitui hífens por underscores nos nomes de atributos.

#### 3.2.2 Processamento de Argumentos

Após configuração, `parser.parse_args()` processa os argumentos da linha de comando. Este método examina `sys.argv`, realiza validações de tipo e formato, e retorna objeto namespace contendo os valores parseados.

Se argumentos inválidos são fornecidos (tipo incorreto, argumento desconhecido, etc.), o argparse automaticamente imprime mensagem de erro e termina com código de saída 2, seguindo convenções Unix para erros de uso.

#### 3.2.3 Apresentação de Resultados

O script apresenta um cabeçalho informativo antes das senhas:

```python
print(f"Gerando {args.quantidade} senha(s) de {args.tamanho} caracteres:")
print("-" * 50)
```

Esta separação visual clara distingue informações sobre a operação das senhas propriamente ditas, facilitando parsing por scripts que invocam o gerador.

O loop de geração utiliza `range(args.quantidade)` para controlar iterações. Cada senha é numerada sequencialmente começando de 1 (não 0), refletindo convenção humana em vez de indexação de programação:

```python
for i in range(args.quantidade):
    senha = gerar_senha(args.tamanho, not args.sem_simbolos)
    print(f"Senha {i+1}: {senha}")
```

A lógica `not args.sem_simbolos` inverte a semântica negativa do flag, convertendo "sem símbolos" em "incluir símbolos" para passar ao gerador. Esta transformação encapsula a inversão em um único ponto, mantendo a função `gerar_senha` com semântica positiva mais intuitiva.

#### 3.2.4 Formato de Saída

A saída estruturada facilita processamento automatizado. Cada senha aparece em linha própria com prefixo identificador consistente ("Senha N: "). Scripts que invocam o gerador podem extrair senhas usando expressões regulares simples ou processamento linha por linha.

Para uso interativo, o formato é claro e permite seleção fácil de senhas individuais com mouse. A linha separadora visual ajuda usuários a identificar rapidamente onde começam os resultados.

## 4. Interface de Linha de Comando

### 4.1 Sintaxe Geral

```bash
./script.py [-tamanho TAMANHO] [-quantidade QUANTIDADE] [-sem_simbolo]
```

Todos os argumentos são opcionais, com o script utilizando valores padrão razoáveis quando omitidos. Esta abordagem de defaults sensatos permite uso rápido sem necessidade de especificar opções em casos comuns.

### 4.2 Exemplos de Uso

**Geração Básica (padrões)**:
```bash
./script.py
# Gera 1 senha de 12 caracteres com símbolos
```

**Senha Longa para Segurança Máxima**:
```bash
./script.py -tamanho 20
# Gera senha de 20 caracteres (~119 bits de entropia)
```

**Múltiplas Senhas**:
```bash
./script.py -quantidade 5
# Gera 5 senhas diferentes de 12 caracteres cada
```

**Senha Alfanumérica Pura**:
```bash
./script.py -sem_simbolo
# Remove símbolos especiais, usando apenas letras e números
```

**Configuração Customizada Completa**:
```bash
./script.py -tamanho 16 -quantidade 3 -sem_simbolo
# Gera 3 senhas alfanuméricas de 16 caracteres cada
```

### 4.3 Mensagem de Ajuda

O argparse gera automaticamente documentação acessível via `-h` ou `--help`:

```bash
./script.py --help
```

Esta mensagem lista todos os argumentos disponíveis com suas descrições, valores padrão e tipos esperados. A geração automática garante que a documentação permanece sincronizada com a implementação real.

## 5. Casos de Uso

### 5.1 Geração de Senhas Pessoais

Usuários finais podem utilizar o script para criar senhas fortes ao cadastrar-se em serviços online. A execução interativa e saída clara facilitam copiar e colar a senha gerada em formulários web.

Recomenda-se uso de gerenciador de senhas para armazenar as senhas geradas, pois senhas aleatórias de 12+ caracteres são impraticáveis de memorizar para a maioria das pessoas.

### 5.2 Provisionamento de Credenciais

Administradores de sistema podem usar o script em processos de provisionamento automatizado:

```bash
# Gerar senhas temporárias para 10 novas contas
./script.py -quantidade 10 -tamanho 16 > senhas_temporarias.txt
```

As senhas podem ser distribuídas aos usuários com instruções de redefinição no primeiro login.

### 5.3 Integração com Scripts de Automação

O formato de saída previsível permite integração em pipelines de automação:

```bash
# Extrair apenas a senha (primeira linha após cabeçalho)
SENHA=$(./script.py | tail -1 | cut -d' ' -f3)
echo "Nova senha: $SENHA"
```

Para múltiplas senhas, ferramentas como `awk` ou `sed` podem extrair e processar cada senha individualmente.

### 5.4 Geração de Tokens e Chaves

O gerador pode criar strings aleatórias para tokens de API, chaves de sessão temporárias ou identificadores únicos:

```bash
# Gerar token de API de 32 caracteres
./script.py -tamanho 32 -sem_simbolo
```

**Nota**: Para tokens criptográficos reais, utilize o módulo `secrets` em vez de `random`.

### 5.5 Testes de Força de Senha

Desenvolvedores podem usar o script para gerar senhas de teste ao desenvolver validadores de força de senha, garantindo variedade nos casos de teste.

## 6. Aspectos de Segurança

### 6.1 Limitações do Gerador Pseudoaleatório

O módulo `random` do Python implementa o algoritmo Mersenne Twister, um gerador de números pseudoaleatórios (PRNG) de alta qualidade estatística. No entanto, este algoritmo **não é adequado para uso criptográfico** por várias razões:

**Previsibilidade**: Dado suficientes outputs do gerador (624 números de 32 bits), o estado interno pode ser reconstruído, permitindo prever todos os valores futuros. Para um atacante que observa senhas geradas sequencialmente, isso representa vulnerabilidade crítica.

**Estado Determinístico**: O gerador é inicializado com um seed determinístico baseado no tempo do sistema. Atacantes que conhecem aproximadamente quando a senha foi gerada podem realizar ataques de força bruta sobre possíveis seeds.

**Falta de Garantias Criptográficas**: O Mersenne Twister foi projetado para simulações Monte Carlo e outras aplicações que requerem aleatoriedade estatística, não garantias de imprevisibilidade contra atacantes adversariais.

### 6.2 Recomendações para Melhorias de Segurança

Para uso em produção ou contextos de segurança real, o script deveria ser modificado para utilizar `secrets.choice` em vez de `random.choice`:

```python
import secrets

def gerar_senha(tamanho=12, incluir_simbolos=True):
    """Gera uma senha criptograficamente segura"""
    caracteres = string.ascii_letters + string.digits
    
    if incluir_simbolos:
        caracteres += "!@#$%&*"
    
    senha = ''.join(secrets.choice(caracteres) for _ in range(tamanho))
    return senha
```

Esta mudança simples fornece garantias criptográficas apropriadas sem alterar a interface ou comportamento observável do script.

### 6.3 Força de Senha e Tamanho do Alfabeto

A limitação do conjunto de símbolos especiais a apenas 7 caracteres é compromisso entre segurança e compatibilidade. Alguns sistemas rejeitam símbolos menos comuns, causando frustração ao usuário.

O conjunto "!@#$%&*" foi escolhido por ser aceito pela vasta maioria de formulários web e sistemas de autenticação. Para ambientes onde maior entropia é crítica, considere expandir o conjunto:

```python
caracteres += string.punctuation  # Todos os símbolos ASCII
```

Esta mudança aumentaria o alfabeto para ~94 caracteres, adicionando aproximadamente 0.6 bits de entropia por caractere.

### 6.4 Validação de Entrada

A implementação atual confia no argparse para validação básica de tipos, mas não implementa validações de razoabilidade:

- Tamanhos extremamente grandes (ex: 1000000 caracteres) são aceitos, podendo causar uso excessivo de memória
- Tamanhos zero ou negativos são aceitos, resultando em senhas vazias
- Quantidades massivas (ex: 1000000 senhas) são aceitas, potencialmente causando saída incontrolável

Para robustez adicional, considere adicionar validações:

```python
parser.add_argument('-tamanho', '--tamanho', type=int, default=12, 
                   help='Tamanho da senha (padrão: 12)',
                   choices=range(4, 129))  # Limita entre 4 e 128

# Ou validação manual:
if args.tamanho < 4:
    parser.error("Tamanho mínimo recomendado é 4 caracteres")
if args.tamanho > 128:
    parser.error("Tamanho máximo suportado é 128 caracteres")
```

### 6.5 Considerações sobre Diversidade Garantida

Alguns sistemas de senha requerem que senhas contenham pelo menos um caractere de cada categoria (maiúscula, minúscula, dígito, símbolo). A implementação atual não garante essa diversidade.

É estatisticamente possível (embora improvável) gerar uma senha de 12 caracteres contendo apenas letras, mesmo quando dígitos estão disponíveis. A probabilidade de uma senha de 12 caracteres não conter nenhum dígito é:

$$P(\text{sem dígitos}) = \left(\frac{52}{62}\right)^{12} \approx 11.8\%$$

Para sistemas que rejeitam senhas sem diversidade, considere implementar regeneração até que todos os requisitos sejam satisfeitos:

```python
def gerar_senha_com_requisitos(tamanho=12, incluir_simbolos=True):
    while True:
        senha = gerar_senha(tamanho, incluir_simbolos)
        tem_maiuscula = any(c.isupper() for c in senha)
        tem_minuscula = any(c.islower() for c in senha)
        tem_digito = any(c.isdigit() for c in senha)
        
        if tem_maiuscula and tem_minuscula and tem_digito:
            if not incluir_simbolos or any(c in "!@#$%&*" for c in senha):
                return senha
```

## 7. Aspectos de Performance

### 7.1 Complexidade Computacional

A geração de uma única senha tem complexidade temporal $O(n)$ onde $n$ é o tamanho da senha. Cada caractere requer uma seleção aleatória, que é operação de tempo constante $O(1)$, e a concatenação final via `join` é linear no número de caracteres.

Para parâmetros típicos (senhas de 12-20 caracteres), o tempo de execução é dominado não pela geração propriamente dita, mas pelo overhead de inicialização do interpretador Python e parsing de argumentos. O tempo de geração pura é sub-milissegundo.

### 7.2 Uso de Memória

O uso de memória é proporcional ao número e tamanho das senhas geradas simultaneamente. Cada senha é representada como string Python, que tem overhead de aproximadamente 50 bytes além do conteúdo dos caracteres.

Para geração de milhares de senhas, considere implementar processamento stream (gerar e imprimir uma por vez) em vez de acumular todas em memória:

```python
# Implementação atual já é eficiente - não acumula senhas
for i in range(args.quantidade):
    senha = gerar_senha(args.tamanho, not args.sem_simbolos)
    print(f"Senha {i+1}: {senha}")  # Imprime imediatamente
```

A implementação atual já segue este padrão eficiente, tornando-a adequada para geração de grandes quantidades sem preocupações de memória.

### 7.3 Otimização do Gerador Aleatório

Para aplicações que geram milhões de senhas, a eficiência do gerador aleatório torna-se relevante. O `random.choice` tem overhead de chamada de função Python para cada caractere.

Uma otimização possível utiliza `random.choices` (plural), disponível desde Python 3.6, que gera múltiplas seleções em uma única chamada:

```python
senha = ''.join(random.choices(caracteres, k=tamanho))
```

Essa mudança simples pode oferecer speedup de 20-30% para gerações em massa, embora a diferença seja imperceptível em uso interativo típico.

## 8. Extensões e Melhorias Futuras

### 8.1 Configuração de Conjunto de Símbolos Customizado

Permitir ao usuário especificar quais símbolos incluir via argumento de linha de comando:

```python
parser.add_argument('--simbolos', type=str, default="!@#$%&*",
                   help='Símbolos especiais a incluir')
```

Esta flexibilidade permite adaptação a requisitos específicos de sistemas sem modificar código.

### 8.2 Modo de Geração Pronunciável

Implementar modo que gera senhas mais fáceis de memorizar usando padrões silábicos:

```python
def gerar_senha_pronunciavel(tamanho=12):
    # Alternância entre consoantes e vogais
    consoantes = "bcdfghjklmnpqrstvwxz"
    vogais = "aeiou"
    # Implementação omitida por brevidade
```

Senhas pronunciáveis sacrificam alguma entropia mas facilitam memorização para contextos onde gerenciadores de senha não estão disponíveis.

### 8.3 Exportação em Múltiplos Formatos

Adicionar opções de formato de saída (JSON, CSV, etc.) para integração mais fácil com sistemas externos:

```python
parser.add_argument('--formato', choices=['texto', 'json', 'csv'],
                   default='texto')
```

### 8.4 Validação contra Lista de Senhas Comuns

Verificar senhas geradas contra banco de dados de senhas comprometidas (como o arquivo RockYou) e regenerar se houver match:

```python
SENHAS_COMUNS = carregar_lista_senhas_comuns()

def gerar_senha_segura(tamanho=12, incluir_simbolos=True):
    while True:
        senha = gerar_senha(tamanho, incluir_simbolos)
        if senha not in SENHAS_COMUNS:
            return senha
```

Embora altamente improvável com senhas aleatórias longas, esta verificação adiciona camada extra de garantia.

### 8.5 Estimativa Visual de Força

Exibir estimativa de tempo para quebra da senha junto com o resultado:

```python
def estimar_tempo_quebra(senha):
    entropia = len(senha) * log2(tamanho_alfabeto)
    # Assumindo 10^9 tentativas/segundo
    segundos = 2**entropia / 1e9 / 2  # Dividido por 2 para tempo médio
    # Formatar em unidades legíveis
```

Esta visualização ajuda usuários a compreender o nível de segurança da senha gerada.

### 8.6 Modo Interativo com Regeneração

Implementar loop interativo permitindo ao usuário regenerar até ficar satisfeito:

```python
while True:
    senha = gerar_senha(tamanho, incluir_simbolos)
    print(f"Senha gerada: {senha}")
    resposta = input("Aceitar? (s/n/q para sair): ")
    if resposta.lower() == 's':
        break
    elif resposta.lower() == 'q':
        sys.exit(0)
```

### 8.7 Integração com Clipboard

Copiar automaticamente a senha para área de transferência:

```python
import pyperclip  # Requer instalação de pacote externo

senha = gerar_senha(args.tamanho, not args.sem_simbolos)
pyperclip.copy(senha)
print(f"Senha copiada para área de transferência: {senha}")
```

Esta funcionalidade reduz risco de exposição visual da senha e facilita uso imediato.

### 8.8 Passphrases com Palavras Aleatórias

Implementar geração de passphrases usando dicionário de palavras:

```python
def gerar_passphrase(num_palavras=4, separador='-'):
    # Carregar lista de palavras (ex: arquivo /usr/share/dict/words)
    palavras = carregar_dicionario()
    palavras_selecionadas = random.sample(palavras, num_palavras)
    return separador.join(palavras_selecionadas)
```

Passphrases como "correct-horse-battery-staple" são mais fáceis de memorizar que sequências aleatórias, mantendo boa segurança.

## 9. Boas Práticas de Uso

### 9.1 Comprimento Recomendado

Para diferentes contextos de segurança:

- **Baixo risco** (contas de teste, serviços não-críticos): 8-10 caracteres
- **Risco moderado** (contas pessoais padrão): 12-14 caracteres
- **Alto risco** (contas financeiras, administrativas): 16-20 caracteres
- **Segurança máxima** (chaves mestras, credenciais raiz): 24+ caracteres

### 9.2 Uso com Gerenciadores de Senha

O script é ideal para integração com gerenciadores de senha como KeePass, 1Password ou Bitwarden:

1. Gere senha forte usando o script
2. Armazene imediatamente no gerenciador
3. Configure gerenciador para copiar para clipboard ao acessar
4. Nunca tente memorizar senhas aleatórias longas

### 9.3 Rotação Regular

Estabeleça política de rotação baseada em sensibilidade:

- Contas críticas: a cada 90 dias
- Contas padrão: a cada 180 dias
- Contas de baixo risco: anualmente

Use o script para gerar novas senhas durante rotações programadas.

### 9.4 Evitar Reutilização

Nunca reutilize senhas entre serviços. Use o script para gerar senha única para cada conta. Gerenciadores de senha tornam isso prático ao eliminar necessidade de memorização.

### 9.5 Backup de Senhas

Mantenha backup seguro de senhas críticas:

- Exporte regularmente do gerenciador de senhas
- Armazene cópia criptografada offline (USB criptografado)
- Considere compartilhamento seguro com pessoa de confiança para recuperação de emergência

## 10. Troubleshooting

### 10.1 Problema: Script não executa

**Sintoma**: Erro "Permission denied" ao executar `./script.py`

**Solução**: Tornar o script executável:
```bash
chmod +x script.py
```

**Alternativa**: Executar explicitamente via Python:
```bash
python3 script.py [argumentos]
```

### 10.2 Problema: Caracteres não exibem corretamente

**Sintoma**: Símbolos aparecem como "?" ou caracteres estranhos no terminal

**Solução**: Configurar terminal para codificação UTF-8:
```bash
export LANG=pt_BR.UTF-8
export LC_ALL=pt_BR.UTF-8
```

### 10.3 Problema: Senha rejeitada por sistema

**Sintoma**: Serviço web rejeita senha gerada com símbolos

**Solução**: Regenerar sem símbolos:
```bash
./script.py -sem_simbolo
```

Ou considere expandir conjunto de símbolos aceitos se souber quais o sistema permite.

### 10.4 Problema: Erro ao importar módulos

**Sintoma**: "ModuleNotFoundError: No module named 'string'"

**Solução**: Este erro não deveria ocorrer com instalação padrão do Python. Verifique integridade da instalação:
```bash
python3 -c "import string, random, argparse"
```

Se o erro persistir, reinstale Python 3.

## 11. Conformidade e Regulamentação

### 11.1 NIST Guidelines

O script gera senhas em conformidade com diretrizes NIST SP 800-63B quando usadas com parâmetros apropriados:

- Suporte para comprimento mínimo de 8 caracteres (recomendado: 12+)
- Suporte para todos os caracteres ASCII imprimíveis
- Sem restrições arbitrárias de composição

### 11.2 Requisitos Comuns de Sistemas

Muitos sistemas corporativos impõem políticas como:

- "Pelo menos uma maiúscula, uma minúscula, um dígito, um símbolo"
- "Não pode conter mais de 2 caracteres repetidos consecutivamente"

O script atual não garante atendimento automático a esses requisitos. Para contextos corporativos, considere implementar modo de conformidade que regenera até satisfazer políticas específicas.

## 12. Conclusão

O Gerador de Senhas Aleatórias fornece ferramenta simples, portátil e eficaz para criação de senhas fortes via linha de comando. A implementação minimalista usando apenas biblioteca padrão garante funcionamento universal em qualquer ambiente Python 3.

Para casos de uso pessoais e de baixo risco, o script é adequado como está. Para aplicações de segurança crítica, implemente as melhorias sugeridas na Seção 6.2, particularmente a migração para o módulo `secrets`.

A arquitetura funcional simples facilita compreensão e modificação, tornando o script excelente base para customização conforme necessidades específicas de usuários e organizações.
