import pandas as pd
from pathlib import Path
import chardet

# Função para filtrar a cidade de bauru
def seleciona_bauru(df):
    df_bauru = pd.DataFrame(df)
    df_bauru = df_bauru[df_bauru["municipio"] == "BAURU"]
    return df_bauru
    

# Função para detectar a codificação de um arquivo
def detectar_encoding(arquivo_path):
    with open(arquivo_path, 'rb') as file:
        resultado = chardet.detect(file.read())
        return resultado['encoding']
    
# Detecta o separador
def detecta_separador(caminho, encoding):
    with open(caminho, 'r', encoding=encoding) as file:
        # Lê a primeira linha de dados
        primeira_linha = next(file).strip()
        # Conta ocorrências de possíveis separadores
        separadores = {',': primeira_linha.count(','), 
                       ';': primeira_linha.count(';'), 
                       '\t': primeira_linha.count('\t')}
        # Retorna o separador com mais ocorrências
        return max(separadores, key=separadores.get)

# Função para ler arquivos na codificação certa
def leitura_csv(caminho):
    # Detecta a codificação do arquivo
    encoding_original = detectar_encoding(caminho)
    separador = detecta_separador(caminho, encoding_original)
    return pd.read_csv(caminho, encoding=encoding_original, sep=separador)
        

# Chegar na raiz do projeto
raiz_projeto = Path(__file__).parent.parent.parent
caminho_data_bruto = raiz_projeto / "data_bruto"
caminho_data = raiz_projeto / "data"

# Leitura dos arquivos
df_sinistros_2022_r = leitura_csv(caminho_data_bruto / "sinistros_2022-2025.csv")
df_pessoas_2022_r = leitura_csv(caminho_data_bruto / "pessoas_2022-2025.csv")

df_sinistros_2022 = seleciona_bauru(df_sinistros_2022_r)
df_pessoas_2022 = seleciona_bauru(df_pessoas_2022_r)

df_sinistros_2022.to_csv(caminho_data / "sinistros_2022-2025_bauru.csv", index=False, encoding="utf-8-sig", sep=";")
df_pessoas_2022.to_csv(caminho_data / "pessoas_2022-2025_bauru.csv", index=False, encoding="utf-8", sep=";")
