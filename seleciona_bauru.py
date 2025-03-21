import os

def deletar_arquivos_sem_palavra_no_nome(diretorio, palavra_chave):
    for pasta_atual, subpastas, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if palavra_chave not in arquivo:  # Verifica se a palavra-chave está no nome do arquivo
                caminho_completo = os.path.join(pasta_atual, arquivo)
                try:
                    os.remove(caminho_completo)
                    print(f"Arquivo deletado: {caminho_completo}")
                except Exception as e:
                    print(f"Erro ao deletar o arquivo {caminho_completo}: {e}")

# Define o diretório inicial (pasta 'dados' dentro da pasta 'tcc')
diretorio_inicial = os.path.join(os.path.dirname(__file__), 'dados')
palavra_chave = 'BAURU'

# Executa a função
deletar_arquivos_sem_palavra_no_nome(diretorio_inicial, palavra_chave)