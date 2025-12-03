import sys
import os
from typing import List, Dict, Tuple
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QFileDialog, 
                             QMessageBox, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QAction
import random
import time

class CalculoThread(QThread):
    """Thread separada para executar o cálculo pesado."""
    resultado_calculado = Signal(tuple)  # (custo, rota, tempo)
    erro_ocorrido = Signal(str)
    
    def __init__(self, otimizador, caminho_arquivo):
        super().__init__()
        self.otimizador = otimizador
        self.caminho_arquivo = caminho_arquivo
    
    def run(self):
        try:
            inicio = time.time()
            
            custo, rota = self.otimizador.calcular(self.caminho_arquivo)
            
            fim = time.time()
            tempo_execucao = fim - inicio
            
            self.resultado_calculado.emit((custo, rota, tempo_execucao))
            
        except Exception as e:
            self.erro_ocorrido.emit(str(e))

class OtimizadorRotas:
    def __init__(self):
        self.matriz = None
        self.pontos = None
        self.distancias = None
        self.num_linhas = 0
        self.num_colunas = 0
    
    def ler_arquivo(self, caminho: str) -> List[List[str]]:
        """Lê a matriz a partir de um arquivo de texto ou TSP."""
        extensao = os.path.splitext(caminho)[1].lower()
        
        if extensao == '.tsp':
            return self.ler_arquivo_tsp(caminho)
        else:
            return self.ler_matriz_txt(caminho)
    
    def ler_matriz_txt(self, caminho: str) -> List[List[str]]:
        """Lê a matriz a partir de um arquivo de texto no formato especificado."""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            linhas = [linha.strip() for linha in linhas if linha.strip()]
            
            if not linhas:
                raise ValueError("Arquivo vazio")
            
            # PRIMEIRA LINHA: número de linhas e colunas
            primeira_linha = linhas[0].split()
            if len(primeira_linha) < 2:
                raise ValueError("Formato inválido: primeira linha deve conter número de linhas e colunas")
            
            self.num_linhas = int(primeira_linha[0])
            self.num_colunas = int(primeira_linha[1])
            
            # Ler a matriz real (ignorando a primeira linha)
            self.matriz = []
            for i in range(1, self.num_linhas + 1):
                if i >= len(linhas):
                    raise ValueError(f"Linha {i} faltando no arquivo")
                
                linha_dados = linhas[i].split()
                if len(linha_dados) != self.num_colunas:
                    raise ValueError(f"Linha {i} tem número incorreto de colunas. Esperado: {self.num_colunas}, Encontrado: {len(linha_dados)}")
                
                self.matriz.append(linha_dados)
            
            return self.matriz
            
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo matriz: {str(e)}")
    
    def ler_arquivo_tsp(self, caminho: str) -> List[List[str]]:
        """Lê um arquivo TSP e converte para matriz."""
        try:
            with open(caminho, 'r') as f:
                linhas = f.readlines()
            
            dimensao = 0
            formato_peso = ""
            secao_pesos = False
            dados_pesos = []
            
            for linha in linhas:
                linha = linha.strip()
                
                if linha.startswith('DIMENSION'):
                    dimensao = int(linha.split(':')[1].strip())
                elif linha.startswith('EDGE_WEIGHT_FORMAT'):
                    formato_peso = linha.split(':')[1].strip()
                elif linha.startswith('EDGE_WEIGHT_SECTION'):
                    secao_pesos = True
                    continue
                elif linha.startswith('EOF') or linha.startswith('END'):
                    break
                elif secao_pesos and linha:
                    dados_pesos.extend([int(x) for x in linha.split() if x])
            
            if dimensao == 0:
                raise ValueError("Dimensão não especificada no arquivo TSP")
            
            if not dados_pesos:
                raise ValueError("Não foi possível ler dados de distância do arquivo TSP")
            
            # Construir matriz de distâncias completa
            self.distancias = self._construir_matriz_distancias(dimensao, dados_pesos, formato_peso)
            
            print(f"Arquivo TSP carregado: {dimensao} pontos")
            
            # Para arquivos TSP, criar pontos virtuais para compatibilidade
            self.pontos = {}
            for i in range(dimensao):
                if i == 0:
                    self.pontos['R'] = (0, 0)  # Ponto de origem
                else:
                    self.pontos[str(i)] = (i, 0)  # Demais pontos
            
            # Criar uma matriz visual simples para TSP
            self.matriz = [['0' for _ in range(min(dimensao, 10))] for _ in range(min(dimensao, 10))]
            self.matriz[0][0] = 'R'  # Apenas mostrar o ponto de origem
            
            self.num_linhas = len(self.matriz)
            self.num_colunas = len(self.matriz[0])
            
            return self.matriz
            
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo TSP: {str(e)}")
    
    def _construir_matriz_distancias(self, n: int, dados: List[int], formato: str) -> List[List[int]]:
        """Constrói a matriz de distâncias completa a partir dos dados."""
        matriz = [[0] * n for _ in range(n)]
        
        if formato == 'UPPER_ROW':
            idx = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if idx < len(dados):
                        matriz[i][j] = dados[idx]
                        matriz[j][i] = dados[idx]
                        idx += 1
        elif formato == 'FULL_MATRIX':
            idx = 0
            for i in range(n):
                for j in range(n):
                    if idx < len(dados):
                        matriz[i][j] = dados[idx]
                        idx += 1
        else:
            # Para outros formatos, assumir matriz completa por linha
            idx = 0
            for i in range(n):
                for j in range(n):
                    if i != j and idx < len(dados):
                        matriz[i][j] = dados[idx]
                        idx += 1
        
        return matriz
    
    def encontrar_pontos(self, matriz: List[List[str]]) -> Dict[str, Tuple[int, int]]:
        """Encontra todos os pontos relevantes."""
        # Para TSP, os pontos já foram criados no ler_arquivo_tsp
        if self.distancias is not None:
            return self.pontos
        
        # Para arquivos TXT, encontrar pontos na matriz
        self.pontos = {}
        for i, linha in enumerate(matriz):
            for j, valor in enumerate(linha):
                if valor != "0":
                    self.pontos[valor] = (i, j)
        return self.pontos
    
    def distancia(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
        """Calcula a distância entre dois pontos."""
        if self.distancias is not None:
            # Para TSP, usar a matriz de distâncias
            idx1 = self._coordenada_para_indice(p1)
            idx2 = self._coordenada_para_indice(p2)
            if idx1 is not None and idx2 is not None:
                return self.distancias[idx1][idx2]
        
        # Para arquivos TXT, usar distância Manhattan
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    def _coordenada_para_indice(self, coord: Tuple[int, int]) -> int:
        """Converte coordenada para índice na matriz de distâncias TSP."""
        if not self.pontos:
            return None
        
        for ponto, ponto_coord in self.pontos.items():
            if ponto_coord == coord:
                if ponto == 'R':
                    return 0
                else:
                    try:
                        return int(ponto)
                    except ValueError:
                        return ord(ponto.upper()) - ord('A') + 1
        return None
    
    def melhor_rota(self, pontos: Dict[str, Tuple[int, int]]) -> Tuple[int, List[str]]:
        """Encontra a melhor rota usando ALGORITMO GENÉTICO."""
        
        origem = 'R'
        entregas = [p for p in pontos.keys() if p != origem]
        
        if not entregas:
            return 0, [origem, origem]
        
        num_pontos = len(entregas)
        
        # ========== PARÂMETROS AJUSTADOS PARA COMPENSAR REMOÇÃO DO 2-OPT ==========
        if num_pontos <= 10:
            tamanho_pop = 150  # Aumentado de 100 para 150
            geracoes = 600     # Aumentado de 500 para 600
        elif num_pontos <= 30:
            tamanho_pop = 300  # Aumentado de 200 para 300
            geracoes = 1200    # Aumentado de 1000 para 1200
        elif num_pontos <= 100:
            tamanho_pop = 400  # Aumentado de 300 para 400
            geracoes = 1800    # Aumentado de 1500 para 1800
        else:
            tamanho_pop = 500  # Aumentado de 400 para 500
            geracoes = 2500    # Aumentado de 2000 para 2500
            
        # Taxas ajustadas para maior exploração
        taxa_mutacao = 0.35    # Aumentado de 0.2 para 0.35
        taxa_crossover = 0.9   # Aumentado de 0.85 para 0.9
        taxa_elitismo = 0.08   # REDUZIDO: 8% de elitismo (era ~10% implícito)
        tamanho_torneio = 7    # Aumentado de 5 para 7 (mais competição)

        # FUNÇÃO FITNESS
        def fitness(rota):
            custo = 0
            # Para TSP, usar índices numéricos
            if self.distancias is not None:
                atual = 0  # R é o índice 0
                for proximo in rota:
                    proximo_idx = int(proximo) if proximo != 'R' else 0
                    custo += self.distancias[atual][proximo_idx]
                    atual = proximo_idx
                # Voltar para origem
                custo += self.distancias[atual][0]
            else:
                # Para TXT
                atual = pontos[origem]
                for ponto in rota:
                    custo += self.distancia(atual, pontos[ponto])
                    atual = pontos[ponto]
                custo += self.distancia(atual, pontos[origem])
            return custo

        # ========== ALGORITMO GENÉTICO ==========
        
        def gerar_populacao_inicial():
            populacao = []
            for _ in range(tamanho_pop):
                individuo = entregas.copy()
                random.shuffle(individuo)
                populacao.append(individuo)
            return populacao

        def selecao_torneio(populacao, k=tamanho_torneio):
            """Seleção por torneio com tamanho ajustável."""
            competidores = random.sample(populacao, k)
            return min(competidores, key=fitness)

        def crossover_ox(pai1, pai2):
            """Crossover Order (OX) - Mantido mas será usado com mais frequência."""
            size = len(pai1)
            if size <= 2:
                return pai1.copy()
            
            start, end = sorted(random.sample(range(size), 2))
            filho = [None] * size
            filho[start:end] = pai1[start:end]
            
            pos = end
            for gene in pai2:
                if gene not in filho:
                    if pos >= size: pos = 0
                    filho[pos] = gene
                    pos += 1
            return filho

        def mutacao_troca(individuo):
            """Mutação por troca com taxa aumentada."""
            if random.random() < taxa_mutacao and len(individuo) >= 2:
                i, j = random.sample(range(len(individuo)), 2)
                individuo[i], individuo[j] = individuo[j], individuo[i]
            return individuo

        def mutacao_inversao(individuo):
            """Mutação por inversão com taxa aumentada."""
            if random.random() < taxa_mutacao and len(individuo) >= 2:
                i, j = sorted(random.sample(range(len(individuo)), 2))
                individuo[i:j] = reversed(individuo[i:j])
            return individuo

        def mutacao_scramble(individuo):
            """Nova mutação: embaralhamento de um segmento."""
            if random.random() < taxa_mutacao * 0.5 and len(individuo) >= 3:
                i, j = sorted(random.sample(range(len(individuo)), 2))
                segmento = individuo[i:j]
                random.shuffle(segmento)
                individuo[i:j] = segmento
            return individuo

        # ALGORITMO GENÉTICO PRINCIPAL
        populacao = gerar_populacao_inicial()
        melhor_global = min(populacao, key=fitness)
        melhor_fitness = fitness(melhor_global)
        
        print(f"Calculando rota para {num_pontos} pontos...")
        print(f"Melhor fitness inicial: {melhor_fitness}")
        print(f"Configuração AG: População={tamanho_pop}, Gerações={geracoes}")
        print(f"Taxas: Mutação={taxa_mutacao}, Crossover={taxa_crossover}, Elitismo={taxa_elitismo}")
        
        ultima_melhoria = 0
        historico_fitness = [melhor_fitness]
        
        for geracao in range(geracoes):
            nova_populacao = []
            
            # ELITISMO REDUZIDO PARA MANTER DIVERSIDADE
            populacao_ordenada = sorted(populacao, key=fitness)
            num_elite = max(1, int(tamanho_pop * taxa_elitismo))  # Apenas 1-8%
            nova_populacao.extend(populacao_ordenada[:num_elite])
            
            # GERAR NOVA POPULAÇÃO
            while len(nova_populacao) < tamanho_pop:
                # Seleção mais competitiva
                pai1 = selecao_torneio(populacao)
                pai2 = selecao_torneio(populacao)
                
                if random.random() < taxa_crossover:
                    filho = crossover_ox(pai1, pai2)
                else:
                    # Clonar o melhor dos dois pais (não apenas um)
                    filho = pai1 if fitness(pai1) < fitness(pai2) else pai2
                    filho = filho.copy()
                
                # APLICAR MÚLTIPLAS MUTAÇÕES COM PROBABILIDADES DIFERENTES
                # Chance maior de mutação para compensar falta de 2-opt
                if random.random() < 0.7:  # 70% de chance de mutação
                    tipo_mutacao = random.random()
                    if tipo_mutacao < 0.4:
                        filho = mutacao_troca(filho)
                    elif tipo_mutacao < 0.7:
                        filho = mutacao_inversao(filho)
                    else:
                        filho = mutacao_scramble(filho)
                
                # CRIAR ALGUNS INDIVÍDUOS ALEATÓRIOS PARA DIVERSIDADE
                if random.random() < 0.05 and len(nova_populacao) > tamanho_pop * 0.8:
                    individuo_aleatorio = entregas.copy()
                    random.shuffle(individuo_aleatorio)
                    nova_populacao.append(individuo_aleatorio)
                else:
                    nova_populacao.append(filho)
            
            populacao = nova_populacao
            
            # ATUALIZAR MELHOR GLOBAL
            melhor_atual = min(populacao, key=fitness)
            fitness_atual = fitness(melhor_atual)
            historico_fitness.append(fitness_atual)
            
            if fitness_atual < melhor_fitness:
                melhor_global = melhor_atual
                melhor_fitness = fitness_atual
                ultima_melhoria = geracao
                
                if geracao % 100 == 0:
                    print(f"Geração {geracao}: Fitness = {melhor_fitness}")
            
            # CRITÉRIO DE PARADA DINÂMICO - MAIS PERMISSIVO
            if num_pontos > 20:
                # Se não houve melhoria por muitas gerações, aplicar perturbação
                if geracao - ultima_melhoria > 400:  # Aumentado de 300 para 400
                    # Perturbar apenas parte da população
                    print(f"Aplicando perturbação controlada na geração {geracao}")
                    for i in range(num_elite + 1, len(populacao)):
                        if random.random() < 0.3:  # Apenas 30% da população
                            populacao[i] = mutacao_scramble(populacao[i].copy())
                    
                    # Reiniciar contador
                    ultima_melhoria = geracao
                
                # Parar se convergiu e passou do ponto de melhoria
                if geracao > 1000 and geracao - ultima_melhoria > 600:  # Mais tolerante
                    print(f"Convergência estabelecida na geração {geracao}")
                    break

        print(f"MELHOR FITNESS FINAL: {melhor_fitness}")
        
        # Converter rota para formato de saída
        if self.distancias is not None:
            rota_strings = ['R'] + [str(p) for p in melhor_global] + ['R']
        else:
            rota_strings = ['R'] + melhor_global + ['R']
            
        return melhor_fitness, rota_strings
    
    def calcular(self, caminho_arquivo: str) -> Tuple[int, List[str]]:
        """Método principal para calcular a rota ótima."""
        try:
            matriz = self.ler_arquivo(caminho_arquivo)
            pontos = self.encontrar_pontos(matriz)
            
            if "R" not in pontos:
                raise ValueError("Ponto de origem 'R' não encontrado.")
            
            return self.melhor_rota(pontos)
            
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo não encontrado.")
        except Exception as e:
            raise Exception(f"Erro durante o cálculo: {str(e)}")

class BotaoEpico(QPushButton):
    def __init__(self, texto, tipo="epico"):
        super().__init__(texto)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if tipo == "epico":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF3D00, stop:0.3 #FF6D00, stop:0.7 #FF9100, stop:1 #FFAB00);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 12px 20px;
                    margin: 2px;
                    letter-spacing: 0.5px;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6D00, stop:0.3 #FF9100, stop:0.7 #FFAB00, stop:1 #FFC400);
                    border: 2px solid #FFE082;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #DD2C00, stop:0.3 #FF3D00, stop:0.7 #FF6D00, stop:1 #FF9100);
                }
                QPushButton:disabled {
                    background: #424242;
                    color: #9E9E9E;
                    border: 1px solid #616161;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #01579B, stop:0.3 #0277BD, stop:0.7 #0288D1, stop:1 #039BE5);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 12px 20px;
                    margin: 2px;
                    letter-spacing: 0.5px;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0277BD, stop:0.3 #0288D1, stop:0.7 #039BE5, stop:1 #03A9F4);
                    border: 2px solid #81D4FA;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #014377, stop:0.3 #01579B, stop:0.7 #0277BD, stop:1 #0288D1);
                }
            """)

class AplicacaoOtimizadorEntrega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.otimizador = OtimizadorRotas()
        self.caminho_arquivo_atual = ""
        self.calculo_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('FLYFOOD • Otimizador de Rotas Inteligente')
        self.setFixedSize(1100, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background: #FFFFFF;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                color: #333333;
            }
            QLabel {
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        
        self.definir_icone_janela()
        
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)
        
        cabecalho = self.criar_cabecalho()
        layout.addWidget(cabecalho)
        
        secao_arquivo = self.criar_secao_arquivo()
        layout.addWidget(secao_arquivo)
        
        secao_tabela = self.criar_secao_tabela()
        layout.addWidget(secao_tabela)
        
        botoes_acao = self.criar_botoes_acao()
        layout.addWidget(botoes_acao)
        
        secao_resultados = self.criar_secao_resultados()
        layout.addWidget(secao_resultados)
        
        widget_central.setLayout(layout)
    
    def definir_icone_janela(self):
        try:
            caminho_icone = "imagens/flyfood icon.png"
            if os.path.exists(caminho_icone):
                self.setWindowIcon(QIcon(caminho_icone))
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
    
    def criar_cabecalho(self):
        widget_cabecalho = QWidget()
        widget_cabecalho.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF3D00, stop:0.5 #FF6D00, stop:1 #FF9100);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        titulo = QLabel("FLYFOOD")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 40px;
                font-weight: 900;
                letter-spacing: 2px;
                text-transform: uppercase;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                font-family: 'Roman SD', 'Arial', sans-serif;
            }
        """)
        
        subtitulo = QLabel("Sistema de Otimização de Rotas Inteligente")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 1px;
                opacity: 0.9;
                font-family: 'Times New Roman', sans-serif;
            }
        """)
        
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        widget_cabecalho.setLayout(layout)
        
        return widget_cabecalho
    
    def criar_secao_arquivo(self):
        widget_secao = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.rotulo_arquivo = QLabel("NENHUM ARQUIVO SELECIONADO")
        self.rotulo_arquivo.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 13px;
                padding: 14px 18px;
                background: #F8F9FA;
                border-radius: 8px;
                border: 1.5px dashed #CED4DA;
                font-weight: 600;
                letter-spacing: 0.5px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        self.rotulo_arquivo.setMinimumHeight(45)
        self.rotulo_arquivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        botao_carregar = BotaoEpico("CARREGAR ARQUIVO", "azul")
        botao_carregar.clicked.connect(self.carregar_arquivo)
        botao_carregar.setFixedWidth(180)
        
        layout.addWidget(self.rotulo_arquivo)
        layout.addWidget(botao_carregar)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def criar_secao_tabela(self):
        widget_secao = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        titulo = QLabel("MATRIZ DE ENTREGAS")
        titulo.setStyleSheet("""
            QLabel {
                color: #FF6D00;
                font-size: 16px;
                font-weight: 700;
                padding: 5px 0px;
                letter-spacing: 1px;
                font-family: 'Roman SD', sans-serif;
            }
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 15px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar:horizontal {
                background: #F5F5F5;
                height: 15px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #C0C0C0;
                border-radius: 7px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
        """)
        scroll_area.setMinimumHeight(200)
        scroll_area.setMaximumHeight(350)
        
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background: #FFFFFF;
                border: none;
                gridline-color: #F5F5F5;
                font-size: 12px;
                font-weight: 600;
                color: #333333;
                font-family: 'Segoe UI', sans-serif;
            }
            QTableWidget::item {
                color: #333333;
                padding: 8px;
                border: 1px solid #EEEEEE;
                text-align: center;
            }
            QTableWidget::item:selected {
                background: #FFF3E0;
                color: #E65100;
                font-weight: bold;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3949AB, stop:1 #5C6BC0);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            QTableCornerButton::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3949AB, stop:1 #5C6BC0);
                border: none;
            }
        """)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.tabela.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        table_layout.addWidget(self.tabela)
        scroll_area.setWidget(table_container)
        
        layout.addWidget(titulo)
        layout.addWidget(scroll_area)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def criar_botoes_acao(self):
        widget_secao = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.botao_calcular = BotaoEpico("CALCULAR ROTA OTIMIZADA", "epico")
        self.botao_calcular.clicked.connect(self.calcular_rota)
        self.botao_calcular.setEnabled(False)
        
        botao_limpar = BotaoEpico("LIMPAR RESULTADOS", "azul")
        botao_limpar.clicked.connect(self.limpar_resultados)
        
        layout.addWidget(self.botao_calcular)
        layout.addWidget(botao_limpar)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def criar_secao_resultados(self):
        widget_secao = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        titulo = QLabel("RESULTADOS DA OTIMIZAÇÃO")
        titulo.setStyleSheet("""
            QLabel {
                color: #FF6D00;
                font-size: 16px;
                font-weight: 700;
                padding: 5px 0px;
                letter-spacing: 1px;
                font-family: 'Roman SD', sans-serif;
            }
        """)
        
        container_principal = QWidget()
        container_principal.setStyleSheet("""
            QWidget {
                background: #F8F9FA;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                padding: 0px;
            }
        """)
        layout_principal = QVBoxLayout(container_principal)
        layout_principal.setContentsMargins(20, 15, 20, 15)
        layout_principal.setSpacing(15)
        
        container_rota = QWidget()
        container_rota.setStyleSheet("""
            QWidget {
                background: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
        """)
        layout_rota = QVBoxLayout(container_rota)
        layout_rota.setContentsMargins(15, 12, 15, 12)
        
        rotulo_rota = QLabel("ROTA OTIMIZADA")
        rotulo_rota.setStyleSheet("""
            QLabel {
                color: #FF6D00;
                font-size: 13px;
                font-weight: 700;
                padding-bottom: 5px;
                letter-spacing: 0.8px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.exibicao_rota = QLabel("A rota calculada será exibida aqui após o processamento")
        self.exibicao_rota.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 13px;
                font-weight: 600;
                padding: 12px;
                background: #FFFFFF;
                border-radius: 6px;
                border: 1px solid #E0E0E0;
                min-height: 20px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        self.exibicao_rota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exibicao_rota.setWordWrap(True)
        self.exibicao_rota.setMinimumHeight(45)
        
        layout_rota.addWidget(rotulo_rota)
        layout_rota.addWidget(self.exibicao_rota)
        
        container_metricas = QWidget()
        container_metricas.setMinimumHeight(100)
        layout_metricas = QHBoxLayout(container_metricas)
        layout_metricas.setContentsMargins(0, 0, 0, 0)
        layout_metricas.setSpacing(15)
        
        container_custo = QWidget()
        container_custo.setMinimumWidth(200)
        container_custo.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF3D00, stop:0.5 #FF6D00, stop:1 #FF9100);
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        layout_custo = QVBoxLayout(container_custo)
        layout_custo.setContentsMargins(15, 12, 15, 12)
        
        rotulo_custo = QLabel("CUSTO TOTAL")
        rotulo_custo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: 700;
                opacity: 0.9;
                letter-spacing: 0.8px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.exibicao_custo = QLabel("-")
        self.exibicao_custo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 900;
                padding: 5px 0px;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                font-family: 'Segoe UI', sans-serif;
                min-height: 30px;
            }
        """)
        self.exibicao_custo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exibicao_custo.setMinimumHeight(35)
        
        layout_custo.addWidget(rotulo_custo)
        layout_custo.addWidget(self.exibicao_custo)
        layout_custo.addStretch()
        
        container_tempo = QWidget()
        container_tempo.setMinimumWidth(200)
        container_tempo.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #01579B, stop:0.5 #0277BD, stop:1 #0288D1);
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        layout_tempo = QVBoxLayout(container_tempo)
        layout_tempo.setContentsMargins(15, 12, 15, 12)
        
        rotulo_tempo = QLabel("TEMPO DE EXECUÇÃO")
        rotulo_tempo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: 700;
                opacity: 0.9;
                letter-spacing: 0.8px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.exibicao_tempo = QLabel("-")
        self.exibicao_tempo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 900;
                padding: 5px 0px;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                font-family: 'Segoe UI', sans-serif;
                min-height: 30px;
            }
        """)
        self.exibicao_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exibicao_tempo.setMinimumHeight(35)
        
        layout_tempo.addWidget(rotulo_tempo)
        layout_tempo.addWidget(self.exibicao_tempo)
        layout_tempo.addStretch()
        
        layout_metricas.addWidget(container_custo)
        layout_metricas.addWidget(container_tempo)
        
        layout_principal.addWidget(container_rota)
        layout_principal.addWidget(container_metricas)
        
        layout.addWidget(titulo)
        layout.addWidget(container_principal)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def carregar_arquivo(self):
        try:
            caminho_arquivo, _ = QFileDialog.getOpenFileName(
                self, 
                "Selecionar arquivo", 
                "", 
                "Arquivos suportados (*.txt *.tsp)"
            )
            
            if caminho_arquivo:
                self.caminho_arquivo_atual = caminho_arquivo
                matriz = self.otimizador.ler_arquivo(caminho_arquivo)
                pontos = self.otimizador.encontrar_pontos(matriz)
                
                nome_arquivo = os.path.basename(caminho_arquivo)
                self.rotulo_arquivo.setText(f"ARQUIVO CARREGADO: {nome_arquivo}")
                self.popular_tabela()
                self.botao_calcular.setEnabled(True)
                self.limpar_resultados()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar arquivo:\n{str(e)}")
    
    def popular_tabela(self):
        if not self.otimizador.matriz:
            return
            
        linhas = len(self.otimizador.matriz)
        colunas = len(self.otimizador.matriz[0]) if linhas > 0 else 0
        
        self.tabela.setRowCount(linhas)
        self.tabela.setColumnCount(colunas)
        
        self.tabela.setHorizontalHeaderLabels([str(i) for i in range(colunas)])
        self.tabela.setVerticalHeaderLabels([str(i) for i in range(linhas)])
        
        for i, linha in enumerate(self.otimizador.matriz):
            for j, valor in enumerate(linha):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                if valor != "0":
                    if valor == "R":
                        item.setBackground(QColor(255, 61, 0))
                        item.setForeground(QColor(255, 255, 255))
                    else:
                        item.setBackground(QColor(2, 119, 189))
                        item.setForeground(QColor(255, 255, 255))
                    
                    fonte = QFont()
                    fonte.setBold(True)
                    fonte.setPointSize(11)
                    item.setFont(fonte)
                else:
                    item.setBackground(QColor(250, 250, 250))
                    item.setForeground(QColor(100, 100, 100))
                    fonte = QFont()
                    fonte.setPointSize(10)
                    item.setFont(fonte)
                
                self.tabela.setItem(i, j, item)
    
    def calcular_rota(self):
        """Inicia o cálculo em uma thread separada."""
        try:
            if not self.otimizador.matriz and not self.otimizador.distancias:
                raise ValueError("Arquivo não carregado")
            
            # Desabilitar botão durante o cálculo
            self.botao_calcular.setEnabled(False)
            self.exibicao_rota.setText("Calculando rota... Aguarde!")
            self.exibicao_custo.setText("...")
            self.exibicao_tempo.setText("...")
            
            # Criar e iniciar thread
            self.calculo_thread = CalculoThread(self.otimizador, self.caminho_arquivo_atual)
            self.calculo_thread.resultado_calculado.connect(self.mostrar_resultado)
            self.calculo_thread.erro_ocorrido.connect(self.mostrar_erro)
            self.calculo_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar cálculo:\n{str(e)}")
            self.botao_calcular.setEnabled(True)
    
    def mostrar_resultado(self, resultado):
        """Mostra o resultado do cálculo na interface."""
        custo, rota, tempo_execucao = resultado
        
        rota_formatada = " → ".join(rota)
        self.exibicao_rota.setText(rota_formatada)
        self.exibicao_custo.setText(f"{custo}")
        self.exibicao_tempo.setText(f"{tempo_execucao:.2f}s")
        
        # Reabilitar botão
        self.botao_calcular.setEnabled(True)
    
    def mostrar_erro(self, mensagem_erro):
        """Mostra erro ocorrido durante o cálculo."""
        QMessageBox.critical(self, "Erro no Cálculo", f"Erro durante o cálculo:\n{mensagem_erro}")
        self.botao_calcular.setEnabled(True)
        self.exibicao_rota.setText("Erro no cálculo. Verifique o console.")
    
    def limpar_resultados(self):
        self.exibicao_rota.setText("A rota calculada será exibida aqui após o processamento")
        self.exibicao_custo.setText("-")
        self.exibicao_tempo.setText("-")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    app.setStyleSheet("""
        QMessageBox {
            background: #FFFFFF;
            color: #333333;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            font-family: 'Segoe UI', sans-serif;
        }
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF3D00, stop:0.5 #FF6D00, stop:1 #FF9100);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
            min-width: 70px;
            font-family: 'Segoe UI', sans-serif;
        }
        QMessageBox QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF6D00, stop:0.5 #FF9100, stop:1 #FFAB00);
            border: 1px solid #FFE082;
        }
    """)
    
    janela = AplicacaoOtimizadorEntrega()
    janela.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
