# Sistema de Geolocalização e Análise de Acidentes de Trânsito para Emissão de Alertas em Bauru

## Visão Geral

Este projeto tem como objetivo desenvolver um **Sistema de Geolocalização e Análise de Acidentes de Trânsito** para a cidade de Bauru, São Paulo, com foco na emissão de alertas para prevenção de acidentes. O sistema utiliza dados de sinistros (acidentes de trânsito) entre 2022 e 2025, coletados no site do INFOSIGA (https://www.infosiga.sp.gov.br), fornecidos em três datasets:

1. **sinistros_2022-2025_bauru.csv**: Contém informações sobre os acidentes, como data, local, tipo de veículo, gravidade e tipo de sinistro.
2. **pessoas_2022-2025_bauru.csv**: Detalha as pessoas envolvidas nos acidentes, incluindo idade, sexo, profissão, tipo de vítima e informações sobre óbitos.
3. **veiculos_2022-2025_bauru.csv**: Registra os veículos envolvidos, com dados como ano de fabricação, modelo e cor.

O projeto está em desenvolvimento, com ênfase inicial na **limpeza e padronização dos dados** para garantir consistência e confiabilidade nas análises futuras, que incluirão geolocalização (usando latitude e longitude) e geração de alertas baseados em padrões de acidentes. A limpeza de dados é realizada em Python usando a biblioteca Pandas, e os datasets limpos são preparados para integração com ferramentas como Power BI para visualização.

## Progresso Atual

Até o momento, o projeto focou na **limpeza de dados** para tratar valores ausentes, inconsistências e padronizações nos três datasets. Um script de limpeza (`data_cleaning.py`) foi desenvolvido e iterativamente atualizado para aplicar regras específicas de tratamento, garantindo que os dados estejam prontos para análises geográficas e estatísticas. As regras de limpeza são detalhadas abaixo.

## Regras de Limpeza de Dados

As seguintes regras foram estabelecidas para tratar valores ausentes, padronizar termos e garantir consistência nos datasets. Cada regra é aplicada no script `data_cleaning.py` e reflete decisões tomadas com base no contexto dos dados e nas necessidades do sistema.

### 1. Dataset: `sinistros_2022-2025_bauru.csv`

- **numero_logradouro**:
  - Valores vazios são preenchidos com `"S/N"` (sem número), indicando que o sinistro ocorreu em um trecho sem número específico.
- **hora_sinistro**:
  - Valores vazios são preenchidos com `"99:99"`, um valor sentinela que indica horário não informado. Este valor é inválido para horas reais (que vão de 00:00 a 23:59), evitando confusão com sinistros que ocorreram à meia-noite.
- **logradouro**:
  - Valores vazios são preenchidos com `"NAO DISPONIVEL"`, indicando que o local do sinistro não foi registrado.
- **latitude** e **longitude**:
  - Valores vazios são preenchidos com `-9999`, um valor sentinela numérico que indica coordenadas não informadas. Este valor é improvável de representar uma localização real em Bauru.
- **tp_veiculo_** (ex.: `tp_veiculo_motocicleta`, `tp_veiculo_automovel`)**:
  - Representam a **quantidade** de veículos do tipo correspondente envolvidos no sinistro (ex.: `tp_veiculo_motocicleta = 2` indica duas motocicletas).
  - Valores vazios são preenchidos com `0`, indicando que nenhum veículo daquele tipo esteve envolvido.
  - Convertidos para tipo inteiro (`int`).
- **gravidade_* (ex.: `gravidade_leve`, `gravidade_fatal`)**:
  - Representam a **quantidade** de pessoas com o nível de gravidade correspondente (ex.: `gravidade_leve = 2` indica duas pessoas com lesões leves).
  - Valores vazios são preenchidos com `0`, indicando que não houve pessoas com aquela gravidade.
  - Convertidos para tipo inteiro (`int`).
- **tp_sinistro_** (ex.: `tp_sinistro_atropelamento`, `tp_sinistro_colisao_frontal`)**:
  - Valores vazios são preenchidos com `"N"`, indicando que o tipo de sinistro não se aplica ao acidente.

### 2. Dataset: `pessoas_2022-2025_bauru.csv`

- **data_obito**:
  - Valores vazios (indicando ausência de óbito) são preenchidos com `"1900-01-01"`, uma data sentinela válida que mantém o formato de data e é improvável de ocorrer nos dados (sinistros de 2022-2025).
- **ano_obito**, **mes_obito**, **dia_obito**:
  - Valores vazios são preenchidos com `-1`, um valor sentinela numérico que indica ausência de óbito.
  - Convertidos para tipo inteiro (`int`).
- **ano_mes_obito**:
  - Valores vazios são preenchidos com `"1900/01"`, um valor sentinela que mantém o formato `"YYYY/MM"` e é consistente com `data_obito`.
- **idade**:
  - Valores vazios são preenchidos com `-1`, indicando idade não informada.
  - Convertida para tipo inteiro (`int`).
- **tipo_vitima**:
  - Valores vazios são preenchidos com `"NAO DISPONIVEL"`, indicando que o tipo de vítima não foi registrado.
- **profissao**:
  - Valores vazios são preenchidos com `"NAO DISPONIVEL"`.
  - Valores `"NÃO INFORMADO"` (com acento) são substituídos por `"NAO DISPONIVEL"`.
- **tipo_veiculo_vitima**:
  - Valores vazios são preenchidos com `"NAO DISPONIVEL"`, indicando que o tipo de veículo da vítima não foi informado.

### 3. Dataset: `veiculos_2022-2025_bauru.csv`

- **ano_fab** e **ano_modelo**:
  - Valores vazios ou `0` são preenchidos com `-1`, um valor sentinela que indica ano não informado.
  - Convertidos para tipo inteiro (`int`).
- **cor_veiculo**:
  - Valores vazios são preenchidos com `"NAO DISPONIVEL"`.

### 4. Padronização dos Termos:

- Todos os valores `"NAO INFORMADO"` e `"NÃO INFORMADO"` em colunas categóricas são substituídos por `"NAO DISPONIVEL"`.
