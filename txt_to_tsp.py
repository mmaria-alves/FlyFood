import string

def matriz_para_tsplib(caminho_txt, caminho_tsp, nome="instancia_matriz"):
    with open(caminho_txt, 'r') as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]

    # Lê dimensões
    nlin, ncol = map(int, linhas[0].split())

    # Lê matriz (cada linha é separada por espaço)
    matriz = [linha.split() for linha in linhas[1:]]

    pontos = {}  # {letra: (x, y)}

    for i in range(nlin):
        for j in range(ncol):
            valor = matriz[i][j]
            if valor != "0":
                pontos[valor] = (j + 1, nlin - i)  # x=j+1, y invertido p/ coordenadas mais intuitivas

    # Ordena: R primeiro, depois letras em ordem alfabética
    chaves = ['R'] + sorted([p for p in pontos.keys() if p in string.ascii_uppercase and p != 'R'])
    coords = [pontos[c] for c in chaves]

    # Cria arquivo TSPLIB
    with open(caminho_tsp, 'w') as f:
        f.write(f"NAME: {nome}\n")
        f.write("TYPE: TSP\n")
        f.write("COMMENT: Convertido de matriz com pontos R e letras\n")
        f.write(f"DIMENSION: {len(coords)}\n")
        f.write("EDGE_WEIGHT_TYPE: MAN_2D\n")
        f.write("NODE_COORD_SECTION\n")

        for i, (x, y) in enumerate(coords, start=1):
            f.write(f"{i} {x} {y}\n")

        f.write("EOF\n")

    print(f"✅ Arquivo TSPLIB salvo em: {caminho_tsp}")
    print("Pontos convertidos:")
    for i, c in enumerate(chaves, start=1):
        print(f"{i}: {c} -> {coords[i-1]}")


#matriz_para_tsplib("lalalala.txt", "lalatsp.tsp")
