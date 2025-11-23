import sys
import os
from typing import List, Dict, Tuple
import itertools
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QFileDialog, 
                             QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QAction

class OtimizadorRotas:
    def __init__(self):
        self.matriz = None
        self.pontos = None
    
    def ler_matriz(self, caminho: str) -> List[List[str]]:
        """Lê a matriz a partir de um arquivo de texto."""
        with open(caminho, 'r') as f:
            linhas = int(f.readline().split()[0])
            self.matriz = [f.readline().split() for _ in range(linhas)]
        return self.matriz
    
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
        """Calcula a distância de Manhattan entre dois pontos."""
        return sum(abs(a - b) for a, b in zip(p1, p2))
    
    def melhor_rota(self, pontos: Dict[str, Tuple[int, int]]) -> Tuple[int, List[str]]:
        """Encontra a melhor rota de entregas (problema do Caixeiro Viajante)."""
        origem = pontos["R"]
        entregas = [p for p in pontos.keys() if p != "R"]
        
        melhor_custo = float("inf")
        melhor_ordem = None
        
        for perm in itertools.permutations(entregas):
            custo = 0
            atual = origem
            
            for p in perm:
                custo += self.distancia(atual, pontos[p])
                atual = pontos[p]
            
            custo += self.distancia(atual, origem)
            
            if custo < melhor_custo:
                melhor_custo = custo
                melhor_ordem = perm
        
        return melhor_custo, ["R"] + list(melhor_ordem) + ["R"]
    
    def calcular(self, caminho_arquivo: str) -> Tuple[int, List[str]]:
        """Método principal para calcular a rota ótima."""
        try:
            matriz = self.ler_matriz(caminho_arquivo)
            pontos = self.encontrar_pontos(matriz)
            
            if "R" not in pontos:
                raise ValueError("Ponto de origem 'R' não encontrado na matriz.")
            
            return self.melhor_rota(pontos)
            
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo não encontrado.")
        except Exception as e:
            raise Exception(f"Erro durante o cálculo: {str(e)}")

class BotaoModerno(QPushButton):
    def __init__(self, texto, icone=None):
        super().__init__(texto)
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF6D00;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #E55C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        if icone:
            self.setIcon(icone)

class AplicacaoOtimizadorEntrega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.otimizador = OtimizadorRotas()
        self.caminho_arquivo_atual = ""
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('FlyFood')
        self.setFixedSize(800, 700)
        self.setStyleSheet("background-color: #F5F5F5;")
        
        # Definir o ícone da janela
        self.definir_icone_janela()
        
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        cabecalho = self.criar_cabecalho()
        layout.addWidget(cabecalho)
        
        secao_arquivo = self.criar_secao_arquivo()
        layout.addWidget(secao_arquivo)
        
        secao_tabela = self.criar_secao_tabela()
        layout.addWidget(secao_tabela)
        
        self.botao_calcular = BotaoModerno("📊 Calcular Melhor Rota")
        self.botao_calcular.clicked.connect(self.calcular_rota)
        self.botao_calcular.setEnabled(False)
        layout.addWidget(self.botao_calcular)
        
        secao_resultados = self.criar_secao_resultados()
        layout.addWidget(secao_resultados)
        
        widget_central.setLayout(layout)
    
    def definir_icone_janela(self):
        """Define o ícone da janela a partir de um arquivo de imagem."""
        try:
            # Tenta carregar o ícone do arquivo
            caminho_icone = "flyfood icon.png"
            if os.path.exists(caminho_icone):
                self.setWindowIcon(QIcon(caminho_icone))
                
            else:
                print(f"Arquivo de ícone não encontrado: {caminho_icone}")
                print("Certifique-se de que 'flyfood icon.png' está na mesma pasta do programa")
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
    
    def criar_cabecalho(self):
        widget_cabecalho = QWidget()
        widget_cabecalho.setStyleSheet("""
            QWidget {
                background-color: #1565C0;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        titulo = QLabel("🚚 Otimizador de Rotas de Entrega")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        subtitulo = QLabel("Encontre a rota mais eficiente para suas entregas")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 14px;
                padding: 5px;
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
        
        self.rotulo_arquivo = QLabel("Nenhum arquivo carregado")
        self.rotulo_arquivo.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
                border: 2px dashed #ddd;
            }
        """)
        self.rotulo_arquivo.setMinimumHeight(40)
        
        botao_carregar = BotaoModerno("📁 Carregar Matriz")
        botao_carregar.clicked.connect(self.carregar_matriz)
        
        layout.addWidget(self.rotulo_arquivo, 4)
        layout.addWidget(botao_carregar, 1)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def criar_secao_tabela(self):
        widget_secao = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        titulo = QLabel("Matriz de Entregas")
        titulo.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0px;
            }
        """)
        
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                gridline-color: #e0e0e0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #1565C0;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(titulo)
        layout.addWidget(self.tabela)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def criar_secao_resultados(self):
        widget_secao = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        titulo = QLabel("Resultados da Otimização")
        titulo.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0px;
            }
        """)
        
        self.exibicao_rota = QLabel("Rota será exibida aqui...")
        self.exibicao_rota.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #1565C0;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                min-height: 30px;
            }
        """)
        self.exibicao_rota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.exibicao_custo = QLabel("Custo total: -")
        self.exibicao_custo.setStyleSheet("""
            QLabel {
                color: #FF6D00;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                border: 2px solid #FF6D00;
            }
        """)
        self.exibicao_custo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(titulo)
        layout.addWidget(self.exibicao_rota)
        layout.addWidget(self.exibicao_custo)
        widget_secao.setLayout(layout)
        
        return widget_secao
    
    def carregar_matriz(self):
        try:
            caminho_arquivo, _ = QFileDialog.getOpenFileName(
                self, 
                "Selecionar arquivo da matriz", 
                "", 
                "Arquivos de texto (*.txt)"
            )
            
            if caminho_arquivo:
                self.caminho_arquivo_atual = caminho_arquivo
                self.otimizador.ler_matriz(caminho_arquivo)
                self.otimizador.encontrar_pontos(self.otimizador.matriz)
                
                nome_arquivo = os.path.basename(caminho_arquivo)
                self.rotulo_arquivo.setText(f"Arquivo carregado: {nome_arquivo}")
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
                    item.setBackground(QColor(21, 101, 192))
                    item.setForeground(QColor(128, 128, 128))
                    fonte = QFont()
                    fonte.setBold(True)
                    fonte.setPointSize(12)
                    item.setFont(fonte)
                else:
                    item.setBackground(QColor(255, 255, 255))
                    item.setForeground(QColor(128, 128, 128))
                    fonte = QFont()
                    fonte.setPointSize(11)
                    item.setFont(fonte)
                
                self.tabela.setItem(i, j, item)
    
    def calcular_rota(self):
        import time 
        try:
            if not self.otimizador.matriz or not self.otimizador.pontos:
                raise ValueError("Matriz não carregada")
            inicio = time.time()
            custo, rota = self.otimizador.calcular(self.caminho_arquivo_atual)
            fim = time.time()
            tempo_execucao = fim - inicio 
          
            rota_formatada = " → ".join(rota)
            self.exibicao_rota.setText(f"📍 {rota_formatada}")
            self.exibicao_custo.setText(f"💰 Custo Total: {custo}\n⌚ Tempo: {tempo_execucao: .6f} s")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular rota:\n{str(e)}")
    
    def limpar_resultados(self):
        self.exibicao_rota.setText("Rota será exibida aqui...")
        self.exibicao_custo.setText("Custo total: -")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    janela = AplicacaoOtimizadorEntrega()
    janela.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
