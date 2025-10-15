import matplotlib.pyplot as plt

# Quantidade de pontos de entrega em cada matriz
# (troca esses valores conforme tuas matrizes)
pontos = [3, 4, 5, 4, 7, 10, 11]

# Tempos de execução medidos do teu programa (em segundos)
# (substitui pelos teus valores reais)
tempos = [0.000567, 0.000561, 0.001868, 0.000738, 0.035456, 33.12566, 36.82044]

# Criação do gráfico
plt.style.use('seaborn-v0_8-whitegrid')

# Criação do gráfico
plt.figure(figsize=(8, 5), dpi=120)
plt.plot(
    pontos, tempos,
    marker='o',
    color='#1565C0',         # azul forte (mesma cor da tua interface PySide6)
    linewidth=2.5,
    markersize=8,
    markerfacecolor='#FF6D00',  # laranja nos marcadores
    markeredgecolor='black'
)

# Personalização dos eixos e título
plt.title('Tempo de Execução x Número de Pontos de Entrega', fontsize=15, fontweight='bold')
plt.xlabel('Número de Pontos de Entrega', fontsize=13)
plt.ylabel('Tempo de Execução (s)', fontsize=13)
plt.grid(True, linestyle='--', alpha=0.6)

# Deixa o gráfico mais "limpo" e equilibrado
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()


# Mostra o gráfico
plt.savefig('grafico_tempo_execucao.png', dpi=300)

plt.show()
