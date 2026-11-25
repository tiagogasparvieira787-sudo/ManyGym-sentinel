# ManyGym Sentinel

Monitorização automática dos repositórios GitHub da ManyGym: deteção de
alterações, revisão técnica assistida por IA e publicação de relatórios em
canais do Discord.

## Objetivo

O Sentinel pretende:

1. Detetar alterações nos repositórios GitHub da ManyGym.
2. Recolher commits e diferenças entre versões.
3. Enviar o código relevante para um modelo de IA.
4. Analisar erros, regressões e inconsistências arquiteturais.
5. Comparar alterações com a documentação técnica.
6. Publicar relatórios em canais específicos do Discord.

O projeto é independente da ManyGym e nunca altera os repositórios
analisados.

## Estado atual

Nesta fase existe apenas o esqueleto do projeto:

- pacote Python instalável em `src/sentinel/`;
- configuração centralizada, com variáveis do GitHub opcionais;
- testes da configuração.

Ainda não estão implementados o cliente GitHub, o cliente de IA, o envio para
o Discord nem GitHub Actions. O sistema de estado entre execuções também não
foi decidido.

## Estrutura

```text
.
├── prompts/                 # prompts de revisão (ainda vazios)
├── src/sentinel/
│   ├── __init__.py
│   ├── config.py            # leitura e validação da configuração
│   └── main.py              # ponto de entrada (ainda vazio)
├── tests/
│   └── test_config.py
├── .env.example             # modelo de variáveis de ambiente
├── pyproject.toml
└── README.md
```

## Requisitos

- Python 3.11 ou superior.
- Git.

Não existem dependências de runtime. A única dependência de desenvolvimento é
`pytest`, declarada no extra `dev`.

## Instalação

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

O modo editável (`-e`) faz com que `sentinel` seja importável a partir de
qualquer diretório enquanto o ambiente virtual estiver ativo.

## Configuração

A aplicação lê variáveis do ambiente do processo. Não carrega ficheiros
`.env` automaticamente, para evitar dependências adicionais.

Para preparar a configuração local:

```bash
cp .env.example .env
# editar .env com valores reais (o ficheiro é ignorado pelo Git)
set -a
source .env
set +a
```

Variáveis atualmente suportadas:

| Variável       | Obrigatória | Descrição |
|----------------|-------------|-----------|
| `GITHUB_TOKEN` | Não         | Token GitHub com acesso de leitura aos repositórios monitorizados. |
| `GITHUB_REPOS` | Não         | Lista `owner/name` separada por vírgulas. |

As variáveis do GitHub ainda não são obrigatórias porque a integração com o
GitHub não está implementada. Quando for necessária, `load_config()` continua
a funcionar sem elas e a validação é feita explicitamente através de
`config.require_github()`.

## Testes

```bash
pytest
```

Os testes não fazem chamadas de rede e não precisam de credenciais reais.
Também é possível validar a importação do pacote:

```bash
python -c "from sentinel import config"
```

## Segurança

- Nenhum token, chave ou webhook deve ser escrito no código ou commitado.
- Configuração real em `.env` (ignorado pelo Git) ou em GitHub Secrets.
- Usar tokens do GitHub apenas com permissões de leitura.
- O Sentinel nunca escreve nos repositórios analisados.
- O token do GitHub não aparece na representação dos objetos de configuração
  nem nas mensagens de erro.
- As respostas da IA são sempre tratadas como sugestões, nunca como verdades
  absolutas.

## Âmbito

Não fazem parte desta fase: GitHub API, IA, Discord, GitHub Actions,
persistência de estado e relatórios semanais. Cada uma destas peças só será
adicionada quando for autorizada.
