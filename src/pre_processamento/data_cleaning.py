import pandas as pd
from pathlib import Path

# Chegar na raiz do projeto
raiz_projeto = Path(__file__).parent.parent.parent
caminho_data = raiz_projeto / "data"

# Carregar os datasets
sinistros = pd.read_csv(caminho_data / "sinistros_2022-2025_bauru.csv", sep=";")
pessoas = pd.read_csv(caminho_data / "pessoas_2022-2025_bauru.csv", sep=";")
veiculos = pd.read_csv(caminho_data / "veiculos_2022-2025_bauru.csv", sep=";")

# Ajuste do nome da coluna tipo_vitima
pessoas = pessoas.rename(columns={'tipo_de vítima': 'tipo_vitima'})

# Função para padronizar NAO DISPONIVEL
def padronizar_nao_disponivel(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].replace(['NAO INFORMADO', 'NÃO INFORMADO'], 'NAO DISPONIVEL')
    return df

# SINISTROS

# Tratar numero_logradouro e indicadores
sinistros['numero_logradouro'] = sinistros['numero_logradouro'].fillna("S/N")
sinistros['hora_sinistro'] = sinistros['hora_sinistro'].fillna("99:99")
sinistros['logradouro'] = sinistros['logradouro'].fillna("NAO DISPONIVEL")
sinistros['latitude'] = sinistros['latitude'].fillna(-9999)
sinistros['longitude'] = sinistros['longitude'].fillna(-9999)

# Tratar colunas tp_veiculo_* e gravidade_* (valores vazios = 0, pois indicam ausência)
for col in [col for col in sinistros.columns if col.startswith('tp_veiculo_') or col.startswith('gravidade_')]:
    sinistros[col] = sinistros[col].fillna(0).astype(float).astype(int)

# Tratar colunas tp_sinistro_* (valores vazios = "N" para indicar não aplicável)
for col in [col for col in sinistros.columns if col.startswith('tp_sinistro_')]:
    sinistros[col] = sinistros[col].fillna("N")

# Padronizar NAO DISPONIVEL em sinistros
sinistros = padronizar_nao_disponivel(sinistros)

# PESSOAS

# Tratar colunas de óbito, idade, tipo_vitima, profissao e tipo_veiculo_vitima
pessoas['data_obito'] = pessoas['data_obito'].fillna("1900-01-01")
pessoas['ano_obito'] = pessoas['ano_obito'].fillna(-1).astype(int)
pessoas['mes_obito'] = pessoas['mes_obito'].fillna(-1).astype(int)
pessoas['dia_obito'] = pessoas['dia_obito'].fillna(-1).astype(int)
pessoas['ano_mes_obito'] = pessoas['ano_mes_obito'].fillna("1900/01")
pessoas['idade'] = pessoas['idade'].fillna(-1).astype(int)
pessoas['tipo_vitima'] = pessoas['tipo_vitima'].fillna("NAO DISPONIVEL")
pessoas['profissao'] = pessoas['profissao'].fillna("NAO DISPONIVEL")
pessoas['tipo_veiculo_vitima'] = pessoas['tipo_veiculo_vitima'].fillna("NAO DISPONIVEL")

# Padronizar NAO DISPONIVEL em pessoas
pessoas = padronizar_nao_disponivel(pessoas)

# VEICULOS

# Veiculos: Tratar ano_fab, ano_modelo e cor_veiculo
veiculos['ano_fab'] = veiculos['ano_fab'].fillna(0).astype(int)  # Valor sentinela para anos
veiculos['ano_modelo'] = veiculos['ano_modelo'].fillna(0).astype(int)
veiculos['cor_veiculo'] = veiculos['cor_veiculo'].fillna("NAO DISPONIVEL")

# Padronizar cores em cor_veiculo
cor_map = {
    'AMARELA': 'AMARELO',
    'Amarelo': 'AMARELO',
    'BRANCA': 'BRANCO',
    'Branco': 'BRANCO',
    'VERMELHA': 'VERMELHO',
    'Vermelho': 'VERMELHO'
}
veiculos['cor_veiculo'] = veiculos['cor_veiculo'].replace(cor_map)

# Padronizar NAO DISPONIVEL em veiculos
veiculos = padronizar_nao_disponivel(veiculos)

# Salvar os datasets limpos
try:
    sinistros.to_csv(caminho_data / "sinistros_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    pessoas.to_csv(caminho_data / "pessoas_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    veiculos.to_csv(caminho_data / "veiculos_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    print("Limpeza concluída! Arquivos salvos com sucesso.")
except PermissionError:
    print("Erro de permissão ao salvar os arquivos. Tente salvar em outro diretório ou execute como administrador.")