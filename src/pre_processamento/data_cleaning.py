import pandas as pd
from pathlib import Path

# Chegar na raiz do projeto
raiz_projeto = Path(__file__).parent.parent.parent
caminho_data = raiz_projeto / "data"

# Carregar os datasets
sinistros = pd.read_csv(caminho_data / "sinistros_2022-2025_bauru.csv", sep=";")
pessoas = pd.read_csv(caminho_data / "pessoas_2022-2025_bauru.csv", sep=";")
veiculos = pd.read_csv(caminho_data / "veiculos_2022-2025_bauru.csv", sep=";")

# SINISTROS

# Tratar numero_logradouro e indicadores
sinistros['numero_logradouro'] = sinistros['numero_logradouro'].fillna("S/N")

# Tratar colunas tp_veiculo_* e gravidade_* (valores vazios = 0, pois indicam ausência)
for col in [col for col in sinistros.columns if col.startswith('tp_veiculo_') or col.startswith('gravidade_')]:
    sinistros[col] = sinistros[col].fillna(0).astype(int)

# Tratar colunas tp_sinistro_* (valores vazios = "N" para indicar não aplicável)
for col in [col for col in sinistros.columns if col.startswith('tp_sinistro_')]:
    sinistros[col] = sinistros[col].fillna("N")

# PESSOAS

#Tratar data_obito, profissao e tipo_veiculo_vitima
pessoas['profissao'] = pessoas['profissao'].fillna("NAO INFORMADO")
pessoas['tipo_veiculo_vitima'] = pessoas['tipo_veiculo_vitima'].fillna("NAO INFORMADO")

# VEICULOS

# 3. Veiculos: Tratar ano_fab, ano_modelo e cor_veiculo
veiculos['ano_fab'] = veiculos['ano_fab'].fillna(0).astype(int)  # Valor sentinela para anos
veiculos['ano_modelo'] = veiculos['ano_modelo'].fillna(0).astype(int)
veiculos['cor_veiculo'] = veiculos['cor_veiculo'].fillna("NAO INFORMADA")

# Salvar os datasets limpos
try:
    sinistros.to_csv(caminho_data / "sinistros_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    pessoas.to_csv(caminho_data / "pessoas_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    veiculos.to_csv(caminho_data / "veiculos_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
    print("Limpeza concluída! Arquivos salvos com sucesso.")
except PermissionError:
    print("Erro de permissão ao salvar os arquivos. Tente salvar em outro diretório ou execute como administrador.")