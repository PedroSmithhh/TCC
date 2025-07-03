import pandas as pd
from pathlib import Path
import chardet
import openpyxl
from datetime import datetime, timedelta

# Função para ler arquivos Excel e converter para CSV
def converte_excel_para_csv(caminho_entrada, caminho_saida):
    # Lê o arquivo Excel
    df = pd.read_excel(caminho_entrada, decimal=',', thousands='.')

    df['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'] = (
    df['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
    .astype(str)
    .str.replace(',', '.', regex=False)
    .astype(float)
)
    
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
chuva_2022_2025_teste = caminho_data / "Chuva" / "chuva_bauru_2022-2025_teste.csv"

lista_df = []

# Concatenar os datasets
chuva_files = [chuva_2022, chuva_2023 , chuva_2024 , chuva_2025]
for f in chuva_files:
    df = pd.read_csv(f, sep=";", # converte a coluna de precipitação diretamente para float
        converters={
            'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 
                lambda x: float(x.replace(',', '.')) if isinstance(x, str) and x.strip() else 0.0
        },)
    df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y')  # força formato brasileiro
    df['Hora UTC'] = df['Hora UTC'].astype(str)
    lista_df.append(df)

chuva = pd.concat(lista_df, ignore_index=True)

chuva.to_csv(chuva_2022_2025_teste, index=False, encoding="utf-8-sig", sep=";")

# Renomeia a coluna
chuva = chuva.rename(columns={'Hora UTC': 'hora'})

# Monta um datetime em UTC a partir de Data + hora
#    - remove o " UTC" de 'hora'
#    - combina Data e hora num formato reconhecido por pandas
chuva['datetime_utc'] = pd.to_datetime(
    chuva['Data'] + ' ' + chuva['hora'].str.replace(' UTC', ''),
    format='%d/%m/%Y %H%M'
)

# Converte para UTC−3 (Bauru) subtraindo 3 horas
chuva['datetime_brt'] = chuva['datetime_utc'] - pd.Timedelta(hours=3)

# Atualiza as colunas Data e hora no formato desejado
chuva['Data'] = chuva['datetime_brt'].dt.strftime('%d/%m/%Y')
chuva['hora'] = chuva['datetime_brt'].dt.strftime('%H:%M')

# Remove colunas intermediárias e salva o CSV
chuva = chuva.drop(columns=['datetime_utc', 'datetime_brt'])

# Salva o csv
chuva.to_csv(chuva_2022_2025, index=False, encoding="utf-8-sig", sep=";")
