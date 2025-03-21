import os
import pandas as pd
import chardet

# Função para detectar a codificação de um arquivo
def detectar_encoding(arquivo_path):
    with open(arquivo_path, 'rb') as file:
        resultado = chardet.detect(file.read())
        return resultado['encoding']

# Função para detectar o separador mais provável
def detectar_separador(arquivo_path, encoding, skiprows=8):
    with open(arquivo_path, 'r', encoding=encoding) as file:
        # Pula as primeiras 8 linhas (cabeçalho)
        for _ in range(skiprows):
            next(file)
        # Lê a primeira linha de dados
        primeira_linha = next(file).strip()
        # Conta ocorrências de possíveis separadores
        separadores = {',': primeira_linha.count(','), 
                       ';': primeira_linha.count(';'), 
                       '\t': primeira_linha.count('\t')}
        # Retorna o separador com mais ocorrências
        return max(separadores, key=separadores.get)

# Define o caminho da pasta principal
pasta_principal = "Dados"

# Loop através dos anos de 2001 a 2024
for ano in range(2001, 2025):
    pasta_ano = os.path.join(pasta_principal, str(ano))
    
    if os.path.exists(pasta_ano):
        for arquivo in os.listdir(pasta_ano):
            if arquivo.endswith('.CSV'):
                caminho_arquivo = os.path.join(pasta_ano, arquivo)
                
                try:
                    # Detecta a codificação
                    encoding_original = detectar_encoding(caminho_arquivo)
                    print(f"Detectada codificação {encoding_original} para {arquivo} do ano {ano}")
                    
                    # Detecta o separador
                    separador = detectar_separador(caminho_arquivo, encoding_original)
                    print(f"Detectado separador '{separador}' para {arquivo}")
                    
                    # Lê o arquivo CSV
                    df = pd.read_csv(
                        caminho_arquivo,
                        skiprows=8,  # Pula as 8 primeiras linhas
                        encoding=encoding_original,
                        sep=separador,
                        engine='python',  # Mais flexível para arquivos mal formatados
                        on_bad_lines='skip'  # Pula linhas com número errado de colunas
                    )
                    
                    # Salva o arquivo com separador ; e codificação UTF-8
                    df.to_csv(caminho_arquivo, sep=';', index=False, encoding='utf-8')
                    
                    print(f"Arquivo {arquivo} do ano {ano} processado com sucesso!")
                    
                except Exception as e:
                    print(f"Erro ao processar {arquivo} do ano {ano}: {str(e)}")

print("Processamento concluído!")