import re

entrada = 'mapa_acidentes_ otimizado.html'  # ou .vue
saida = 'MapaBauru_limpo.html'

with open(entrada, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Expressão regular para encontrar blocos como:
# var marker_xxx = L.marker([...], {}).addTo(marker_cluster_xxx);
regex = re.compile(
    r'var marker_[a-z0-9]+ =\s*L\.marker\(\s*(\[[^\]]+\])\s*,\s*\{\s*\}\s*\)\.addTo\((marker_cluster_[a-z0-9]+)\);\s*',
    re.IGNORECASE
)

# Substituição para deixar direto em uma linha, com markerCluster
novo_conteudo = regex.sub(lambda m: f'L.marker({m.group(1)}).addTo(markerCluster);\n', conteudo)

# Opcional: remover linhas completamente em branco (não só as entre marcadores)
linhas = novo_conteudo.splitlines()
linhas_limpas = [linha for linha in linhas if linha.strip() != '']
novo_conteudo_final = '\n'.join(linhas_limpas)

# Escreve o resultado no novo arquivo
with open(saida, 'w', encoding='utf-8') as f:
    f.write(novo_conteudo_final)

print(f'Marcadores padronizados e limpos com sucesso! Arquivo salvo em: {saida}')
