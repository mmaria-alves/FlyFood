<p align="center">
  <img src="imagens/flyfood icon.png" alt="FlyFood Logo" width="200"/>
</p>

<h1 align="center">🚚 FlyFood – Otimizador de Rotas de Entrega</h1>



# 📋 Sobre o Projeto
O FlyFood é uma empresa de entregas rápidas utilizando drones e que, contém uma aplicação inteligente de otimização de rotas de entrega desenvolvida para resolver o problema do Caixeiro Viajante (TSP - Traveling Salesman Problem) aplicado ao contexto de entregas. O sistema calcula a rota mais eficiente entre múltiplos pontos de entrega, minimizando o custo total do percurso.

# 🎯 Funcionalidades Principais
📊 Leitura de Matrizes: Carrega matrizes de entrega a partir de arquivos de texto

🧮 Algoritmo de Otimização: Implementa o algoritmo do Caixeiro Viajante para encontrar a rota ótima

🎨 Interface Moderna: GUI intuitiva e responsiva com design contemporâneo

📈 Visualização de Resultados: Exibe a rota calculada e o custo total de forma clara

💾 Gerenciamento de Arquivos: Sistema integrado para carregamento de dados



# 📦 Instalação e Dependências 
• Python 3.8 ou superior

• Sistema operacional: Windows, Linux ou macOS

# •  Bibliotecas Necessárias
Framework GUI

![PySide6](https://img.shields.io/badge/PySide6-Qt%20for%20Python-green?style=for-the-badge&logo=qt)   | pip install PySide6 

Bibliotecas padrão (já incluídas no Python)

![sys](https://img.shields.io/badge/sys-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)     | import sys

![os](https://img.shields.io/badge/os-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)       | import os 

![typing](https://img.shields.io/badge/typing-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python) | from typing import List, Dict, Tuple

![itertools](https://img.shields.io/badge/itertools-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python) | import itertools 

![time](https://img.shields.io/badge/time-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)  | import time


# Fluxo de Uso
Carregar Matriz: Clique em "📁 Carregar Matriz" e selecione seu arquivo

Visualizar Dados: A matriz será exibida na tabela com destaque colorido

Calcular Rota: Clique em "📊 Calcular Melhor Rota"

Analisar Resultados: Veja a rota ótima e custo total calculados


# 🧮 Algoritmo Implementado
Problema do Caixeiro Viajante (TSP)
→ O FlyFood resolve o TSP usando força bruta com permutações, considerando:

→ Distância Manhattan: |x1-x2| + |y1-y2|

→ Ponto fixo de origem: Sempre inicia e termina em 'R'

→ Otimização completa: Testa todas as permutações possíveis

Complexidade

→ Tempo: O(n!) para n pontos de entrega

→ Espaço: O(n²) para armazenar a matriz

Nota: Ideal para até ~10 pontos de entrega devido à complexidade fatorial.


# 📚 Artigo do Projeto
🔗 Leia o artigo completo sobre o desenvolvimento do FlyFood:(link será adicionado posteriormente) 


# 📞 Suporte

Se tiver dúvidas, sugestões ou encontrar algum problema, fale com a gente:

 [![Email](https://img.shields.io/badge/Email-Contato%20FlyFood-red?style=for-the-badge&logo=gmail)](mailto:flyfood.com.br@gmail.com)

 ## 💻 Projeto realizado por

[Laura](https://github.com/mlcordeiro) • [Maria Eduarda](https://github.com/mmaria-alves)  • [Ana Clara](https://github.com/eianaxz) • [Filipe](https://github.com/nilipe)








