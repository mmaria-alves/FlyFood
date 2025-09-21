import itertools

def ler_matriz(matriz):
    with open(matriz, 'r') as f:
        dimensoes = f.readline().split()    # Lê a primeira linha para obter as dimensões
        linhas = int(dimensoes[0])
        
        matriz = []
        for _ in range(linhas):     # Lê a matriz
            linha = f.readline().split()
            matriz.append(linha)
    
    return matriz

def encontrar_pontos(matriz):
    pontos = {}
    for i, linha in enumerate(matriz):
        for j, valor in enumerate(linha):
            if valor != "0":
                pontos[valor] = (i, j)
    return pontos

def distancia(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def melhor_rota(pontos):
    origem = pontos["R"]
    entregas = [p for p in pontos.keys() if p != "R"]

    melhor_custo = float("inf")
    melhor_ordem = None

    for perm in itertools.permutations(entregas):
        custo = 0
        atual = origem

        for p in perm:
            custo += distancia(atual, pontos[p])
            atual = pontos[p]

        custo += distancia(atual, origem)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_ordem = perm

    return melhor_custo, ["R"] + list(melhor_ordem) + ["R"]

if __name__ == '__main__':
    matriz = ler_matriz('matriz.txt')
    pontos = encontrar_pontos(matriz)
    custo, rota = melhor_rota(pontos)

    print("\nMelhor rota:", " -> ".join(rota))
    print(f"Custo total: {custo}")
