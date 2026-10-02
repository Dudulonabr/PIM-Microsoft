# PIM Microsoft — Sistema de Gestão de Chamados de TI

Projeto acadêmico desenvolvido em **Python** para simular a triagem, priorização, acompanhamento e análise de chamados internos de TI.

## Visão geral

O sistema aplica regras de negócio para transformar informações como **impacto**, **urgência** e **tipo do incidente** em uma pontuação de prioridade. A partir dessa pontuação, o chamado recebe uma classificação e um SLA correspondente.

## Principais funcionalidades

- Cadastro manual de chamados
- Geração automática de ID
- Classificação por impacto, urgência e tipo
- Cálculo automático de score e prioridade
- Definição de SLA por prioridade
- Persistência em arquivo JSON
- Atualização de status
- Busca, filtros e ordenação
- Dashboard com indicadores
- Simulação de carga com dados fictícios
- Relatório textual

## Regras de prioridade

| Prioridade | SLA |
| --- | --- |
| Baixa | 72h |
| Média | 24h |
| Alta | 8h |
| Crítica | 1h |

## Tecnologias e conceitos

- Python
- JSON
- Dataclasses
- Condicionais e estruturas de repetição
- Funções e tratamento de exceções
- Persistência de dados
- Regras de negócio
- Separação de responsabilidades

## Estrutura atual

```text
PIM-Microsoft/
├── Codigo.PY
└── chamados_microsoft.json
```

## Como executar

1. Tenha o Python instalado.
2. Clone o repositório.
3. Entre na pasta do projeto.
4. Execute:

```bash
python Codigo.PY
```

O arquivo `chamados_microsoft.json` mantém os dados entre as execuções.

## Contexto acadêmico

Projeto desenvolvido como parte do **PIM**, aplicando lógica de programação em um cenário de suporte e gestão de TI.

## Autor

**Eduardo Lona**  
Estudante de Análise e Desenvolvimento de Sistemas e Engenharia de Software.
