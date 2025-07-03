import pandas as pd
from pathlib import Path
import chardet
import openpyxl
from datetime import datetime, timedelta

# Função para ler arquivos Excel e converter para CSV
def converte_excel_para_csv(caminho_entrada, caminho_saida):
    # Lê o arquivo Excel
    df = pd.read_excel(caminho_entrada)
    
    # Converte para CSV
    df.to_csv(caminho_saida, index=False, encoding='utf-8-sig', sep=';')
    return df

# Função para converter de UTC para horário de Bauru
def converter_utc_para_bauru(valor):
    try:
        # Remove o " UTC" e faz parsing da hora (ex: "0300" -> 03:00)
        hora_utc = datetime.strptime(valor.replace(" UTC", ""), "%H%M")
        # Subtrai 3 horas para converter para UTC-3 (Bauru)
        hora_bauru = hora_utc - timedelta(hours=3)
        return hora_bauru.strftime("%H:%M")
    except Exception as e:
        print(f"Erro ao converter valor '{valor}': {e}")
        return None

# Chegar na raiz do projeto
raiz_projeto = Path(__file__).parent.parent.parent.parent
caminho_data_bruto = raiz_projeto / "data_bruto"
caminho_data = raiz_projeto / "data"

# Lista de anos para processar
anos = ['2022', '2023', '2024', '2025']

# Processa cada arquivo
for ano in anos:

 # Caminhos dos arquivos
    if(ano=='2025'):
         arquivo_entrada = caminho_data_bruto / "Chuva" / f"INMET_SE_SP_A705_BAURU_01-01-{ano}_A_31-05-{ano}.xlsx" # 2025 não possui ano completo
    else:
        arquivo_entrada = caminho_data_bruto / "Chuva" / f"INMET_SE_SP_A705_BAURU_01-01-{ano}_A_31-12-{ano}.xlsx"
        
    arquivo_saida_csv = caminho_data / "Chuva" / f"chuva_bauru_{ano}.csv"
    
    # Converte Excel para CSV
    df_chuva = converte_excel_para_csv(arquivo_entrada, arquivo_saida_csv)

    # Salva dados processados
    df_chuva.to_csv(arquivo_saida_csv, index=False, encoding='utf-8-sig', sep=';')

chuva_2022 = caminho_data / "Chuva" / "chuva_bauru_2022.csv"
chuva_2023 = caminho_data/ "Chuva" / "chuva_bauru_2023.csv"
chuva_2024 = caminho_data / "Chuva" / "chuva_bauru_2024.csv"
chuva_2025 = caminho_data / "Chuva" / "chuva_bauru_2025.csv"
chuva_2022_2025 = caminho_data / "Chuva" / "chuva_bauru_2022-2025.csv"

# Concatenar os datasets
chuva_files = [chuva_2022, chuva_2023 , chuva_2024 , chuva_2025]
chuva = pd.concat([pd.read_csv(f, sep=";") for f in chuva_files], ignore_index=True)

# Renomeia a coluna
chuva = chuva.rename(columns={'Hora UTC': 'hora'})

# Aplica a conversão na coluna
chuva['hora'] = chuva['hora'].apply(converter_utc_para_bauru)

chuva.to_csv(chuva_2022_2025, index=False, encoding="utf-8-sig", sep=";")
