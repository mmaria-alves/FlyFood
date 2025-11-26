import sys
import os
from typing import List, Dict, Tuple
import itertools
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QFileDialog, 
                             QMessageBox, QHeaderView, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QAction
import random

class OtimizadorRotas:
    def __init__(self):
        self.matriz = None
        self.pontos = None
        self.distancias = None  # Matriz de distâncias para TSP
    
    def ler_arquivo(self, caminho: str) -> List[List[str]]:
        """Lê a matriz a partir de um arquivo de texto ou TSP."""
        extensao = os.path.splitext(caminho)[1].lower()
        
        if extensao == '.tsp':
            return self.ler_arquivo_tsp(caminho)
        else:
            return self.ler_matriz_txt(caminho)
    
    def ler_matriz_txt(self, caminho: str) -> List[List[str]]:
        """Lê a matriz a partir de um arquivo de texto."""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            # Remover linhas vazias e espaços em branco
            linhas = [linha.strip() for linha in linhas if linha.strip()]
            
            # Verificar se o arquivo começa com número de linhas (formato antigo)
            if linhas[0].isdigit():
                # Formato antigo: primeira linha é o número de linhas
                num_linhas = int(linhas[0])
                self.matriz = []
                for i in range(1, min(num_linhas + 1, len(linhas))):
                    linha_dados = linhas[i].split()
                    self.matriz.append(linha_dados)
            else:
                # Formato novo: matriz direta
                self.matriz = []
                for linha in linhas:
                    linha_dados = linha.split()
                    self.matriz.append(linha_dados)
            
            return self.matriz
            
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo matriz: {str(e)}")
    
    def ler_arquivo_tsp(self, caminho: str) -> List[List[str]]:
        """Lê um arquivo TSP e converte para matriz."""
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
                # Coletar todos os números da seção de pesos
                dados_pesos.extend([int(x) for x in linha.split() if x])
        
        if dimensao == 0:
            raise ValueError("Dimensão não especificada no arquivo TSP")
        
        if not dados_pesos:
            raise ValueError("Não foi possível ler dados de distância do arquivo TSP")
        
        # Construir matriz de distâncias completa
        self.distancias = self._construir_matriz_distancias(dimensao, dados_pesos, formato_peso)
        
        # Criar matriz visual para exibição (apenas para mostrar na interface)
        # Para arquivos TSP, criamos uma matriz onde 'R' é o ponto 0 e os demais são numerados
        self.matriz = self._criar_matriz_visual(dimensao)
        
        return self.matriz
    
    def _construir_matriz_distancias(self, n: int, dados: List[int], formato: str) -> List[List[int]]:
        """Constrói a matriz de distâncias completa a partir dos dados."""
        matriz = [[0] * n for _ in range(n)]
        
        if formato == 'UPPER_ROW':
            # Formato UPPER_ROW: apenas a parte superior direita (sem diagonal)
            idx = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if idx < len(dados):
                        matriz[i][j] = dados[idx]
                        matriz[j][i] = dados[idx]  # Matriz simétrica
                        idx += 1
        else:
            # Para outros formats, assumir matriz completa
            idx = 0
            for i in range(n):
                for j in range(n):
                    if i != j and idx < len(dados):
                        matriz[i][j] = dados[idx]
                        idx += 1
        
        return matriz
    
    def _criar_matriz_visual(self, n: int) -> List[List[str]]:
        """Cria uma matriz visual para exibição na interface."""
        # Criar uma matriz quadrada grande o suficiente para acomodar todos os pontos
        tamanho = max(n, 10)  # Mínimo de 10x10 para boa visualização
        matriz = [['0' for _ in range(tamanho)] for _ in range(tamanho)]
        
        # Distribuir os pontos na matriz
        for i in range(n):
            linha = i % tamanho
            coluna = i % tamanho
            if i == 0:
                matriz[linha][coluna] = 'R'  # Ponto de origem
            else:
                matriz[linha][coluna] = str(i)  # Demais pontos
        
        return matriz
    
    def encontrar_pontos(self, matriz: List[List[str]]) -> Dict[str, Tuple[int, int]]:
        """Encontra todos os pontos relevantes da matriz."""
        self.pontos = {
            valor: (i, j)
            for i, linha in enumerate(matriz)
            for j, valor in enumerate(linha)
            if valor != "0"
        }
        return self.pontos
    
    def distancia(self, p1: Tuple[int, ...], p2: Tuple[int, ...]) -> int:
        """Calcula a distância entre dois pontos."""
        # Se temos matriz de distâncias TSP, usar ela
        if self.distancias is not None:
            # Converter coordenadas da matriz visual para índices da matriz de distâncias
            idx1 = self._coordenada_para_indice(p1)
            idx2 = self._coordenada_para_indice(p2)
            if idx1 is not None and idx2 is not None:
                return self.distancias[idx1][idx2]
        
        # Fallback para distância Manhattan (para arquivos txt)
        return sum(abs(a - b) for a, b in zip(p1, p2))
    
    def _coordenada_para_indice(self, coord: Tuple[int, int]) -> int:
        """Converte coordenada da matriz visual para índice na matriz de distâncias TSP."""
        if not self.pontos:
            return None
        
        # Encontrar qual ponto corresponde a estas coordenadas
        for ponto, ponto_coord in self.pontos.items():
            if ponto_coord == coord:
                if ponto == 'R':
                    return 0
                else:
                    try:
                        return int(ponto)
                    except ValueError:
                        # Se não for número, usar mapeamento alfabético
                        return ord(ponto) - ord('A') + 1
        return None
    
    def melhor_rota(self, pontos: Dict[str, Tuple[int, int]]) -> Tuple[int, List[str]]:
        """Encontra a melhor rota usando algoritmo genético."""
        # Para arquivos TXT, não usar matriz de distâncias TSP
        if self.distancias is not None:
            # Converter pontos para índices numéricos (para TSP)
            indices_pontos = {}
            for ponto, coord in pontos.items():
                if ponto == 'R':
                    indices_pontos[0] = coord
                else:
                    try:
                        indices_pontos[int(ponto)] = coord
                    except ValueError:
                        # Se for letra, converter para número
                        indices_pontos[ord(ponto) - ord('A') + 1] = coord
            
            origem = 0
            entregas = [i for i in indices_pontos.keys() if i != origem]
        else:
            # Para arquivos TXT, usar os pontos diretamente
            origem = pontos["R"]
            entregas = [p for p in pontos.keys() if p != "R"]
            indices_pontos = pontos  # Usar o dicionário de pontos diretamente

        # Parâmetros do Algoritmo Genético
        tamanho_pop = 100
        geracoes = 500
        taxa_mutacao = 0.15
        elitismo = True

        # Função fitness
        def fitness(rota):
            custo = 0
            if self.distancias is not None:
                # Para TSP: usar índices numéricos
                atual = origem
                for proximo in rota:
                    custo += self.distancia(indices_pontos[atual], indices_pontos[proximo])
                    atual = proximo
                # Voltar para a origem
                custo += self.distancia(indices_pontos[atual], indices_pontos[origem])
            else:
                # Para TXT: usar pontos diretamente
                atual = origem
                for ponto in rota:
                    custo += self.distancia(atual, pontos[ponto])
                    atual = pontos[ponto]
                # Voltar para a origem
                custo += self.distancia(atual, origem)
            return custo

        # Geração da população inicial
        def gerar_populacao_inicial():
            populacao = []
            for _ in range(tamanho_pop):
                individuo = entregas.copy()
                random.shuffle(individuo)
                populacao.append(individuo)
            return populacao

        # Seleção por torneio
        def selecao_torneio(populacao):
            tamanho_torneio = 3
            competidores = random.sample(populacao, tamanho_torneio)
            return min(competidores, key=fitness)

        # Crossover OX (Order Crossover)
        def crossover_ox(pai1, pai2):
            size = len(pai1)
            start, end = sorted(random.sample(range(size), 2))
            
            filho = [None] * size
            filho[start:end] = pai1[start:end]
            
            pos = end
            for gene in pai2:
                if gene not in filho:
                    if pos >= size:
                        pos = 0
                    filho[pos] = gene
                    pos += 1
            return filho

        # Mutação por troca
        def mutacao_troca(individuo):
            if random.random() < taxa_mutacao:
                i, j = random.sample(range(len(individuo)), 2)
                individuo[i], individuo[j] = individuo[j], individuo[i]
            return individuo

        # Mutação por inversão
        def mutacao_inversao(individuo):
            if random.random() < taxa_mutacao:
                i, j = sorted(random.sample(range(len(individuo)), 2))
                individuo[i:j] = reversed(individuo[i:j])
            return individuo

        # Algoritmo Genético principal
        populacao = gerar_populacao_inicial()
        melhor_global = min(populacao, key=fitness)
        melhor_fitness = fitness(melhor_global)

        for geracao in range(geracoes):
            nova_populacao = []
            
            # Elitismo
            if elitismo:
                nova_populacao.append(melhor_global)
            
            # Preencher o resto da população
            while len(nova_populacao) < tamanho_pop:
                pai1 = selecao_torneio(populacao)
                pai2 = selecao_torneio(populacao)
                
                # Crossover
                if random.random() < 0.8:  # 80% de chance de crossover
                    filho = crossover_ox(pai1, pai2)
                else:
                    filho = pai1.copy() if random.random() < 0.5 else pai2.copy()
                
                # Mutação
                if random.random() < 0.5:
                    filho = mutacao_troca(filho)
                else:
                    filho = mutacao_inversao(filho)
                
                nova_populacao.append(filho)
            
            populacao = nova_populacao
            
            # Atualizar melhor global
            melhor_atual = min(populacao, key=fitness)
            fitness_atual = fitness(melhor_atual)
            
            if fitness_atual < melhor_fitness:
                melhor_global = melhor_atual
                melhor_fitness = fitness_atual

        # Converter rota de volta para formato de string
        if self.distancias is not None:
            # Para TSP: converter índices numéricos de volta para strings
            rota_strings = ['R'] + [str(p) for p in melhor_global] + ['R']
        else:
            # Para TXT: já temos strings
            rota_strings = ['R'] + melhor_global + ['R']
            
        return melhor_fitness, rota_strings
    
    def calcular(self, caminho_arquivo: str) -> Tuple[int, List[str]]:
        """Método principal para calcular a rota ótima."""
        try:
            matriz = self.ler_arquivo(caminho_arquivo)
            pontos = self.encontrar_pontos(matriz)
            
            if "R" not in pontos:
                raise ValueError("Ponto de origem 'R' não encontrado na matriz.")
            
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
        else:  # azul
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
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('FLYFOOD • Otimizador de Rotas Inteligente')
        self.setFixedSize(1100, 800)  # Aumentei a altura para caber tudo
        
        # Configurar fonte global - FUNDO BRANCO
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
        
        # Definir o ícone da janela
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
        """Define o ícone da janela a partir de um arquivo de imagem."""
        try:
            caminho_icone = "flyfood icon.png"
            if os.path.exists(caminho_icone):
                self.setWindowIcon(QIcon(caminho_icone))
            else:
                print(f"Arquivo de ícone não encontrado: {caminho_icone}")
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
        botao_carregar.setFixedWidth(180)  # Largura ajustada
        
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
        
        # Container da tabela com scroll
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
        
        # Widget container para a tabela
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
        
        # Configurar a tabela para ter scroll interno
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
        
        # Container principal para resultados
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
        
        # Rota
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
        
        # Métricas - Container com mais espaço
        container_metricas = QWidget()
        container_metricas.setMinimumHeight(100)  # Altura mínima garantida
        layout_metricas = QHBoxLayout(container_metricas)
        layout_metricas.setContentsMargins(0, 0, 0, 0)
        layout_metricas.setSpacing(15)
        
        # Custo - Container maior
        container_custo = QWidget()
        container_custo.setMinimumWidth(200)  # Largura mínima garantida
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
        self.exibicao_custo.setMinimumHeight(35)  # Altura mínima para o valor
        
        layout_custo.addWidget(rotulo_custo)
        layout_custo.addWidget(self.exibicao_custo)
        layout_custo.addStretch()
        
        # Tempo - Container maior
        container_tempo = QWidget()
        container_tempo.setMinimumWidth(200)  # Largura mínima garantida
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
        self.exibicao_tempo.setMinimumHeight(35)  # Altura mínima para o valor
        
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
                self.otimizador.ler_arquivo(caminho_arquivo)
                self.otimizador.encontrar_pontos(self.otimizador.matriz)
                
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
                        # Ponto de origem - laranja
                        item.setBackground(QColor(255, 61, 0))
                        item.setForeground(QColor(255, 255, 255))
                    else:
                        # Pontos de entrega - azul
                        item.setBackground(QColor(2, 119, 189))
                        item.setForeground(QColor(255, 255, 255))
                    
                    fonte = QFont()
                    fonte.setBold(True)
                    fonte.setPointSize(11)
                    item.setFont(fonte)
                else:
                    # Células vazias
                    item.setBackground(QColor(250, 250, 250))
                    item.setForeground(QColor(100, 100, 100))
                    fonte = QFont()
                    fonte.setPointSize(10)
                    item.setFont(fonte)
                
                self.tabela.setItem(i, j, item)
    
    def calcular_rota(self):
        import time 
        try:
            if not self.otimizador.matriz or not self.otimizador.pontos:
                raise ValueError("Arquivo não carregado")
            
            inicio = time.time()
            custo, rota = self.otimizador.calcular(self.caminho_arquivo_atual)
            fim = time.time()
            tempo_execucao = fim - inicio 
          
            rota_formatada = " → ".join(rota)
            self.exibicao_rota.setText(rota_formatada)
            self.exibicao_custo.setText(f"{custo}")
            self.exibicao_tempo.setText(f"{tempo_execucao:.4f}s")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular rota:\n{str(e)}")
    
    def limpar_resultados(self):
        self.exibicao_rota.setText("A rota calculada será exibida aqui após o processamento")
        self.exibicao_custo.setText("-")
        self.exibicao_tempo.setText("-")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Definir estilo geral da aplicação
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
    