<p align="center">
  <img src="imagens/flyfood icon.png" alt="FlyFood Logo" width="200"/>
</p>

<h1 align="center">🚁 FlyFood – Otimizador de Rotas de Entrega por Drones</h1>

<p align="center">
  <em>Aplicação de Algoritmos Genéticos ao Problema do Caixeiro Viajante</em>
</p>

---

## 📋 Sobre o Projeto
Com o crescimento acelerado dos centros urbanos e a demanda crescente por entregas rápidas e eficiemtes, a logística moderna enfrenta desafios cada vez mais complexos na otimização de rotas de distribuição. Nesse contexto, o projeto **FlyFood** propõe uma solução inovadora ao aplicar **Algoritmos Genéticos (AGs)** na otimização de rotas de entrega por drones, abordando o clássico **Problema do Caixeiro Viajante (TSP)**. Esse trabalho integra conceitos fundamentais de **otimização computacional**, **estrutura de dados** e **análise de algoritmos**, transformando conhecimento teórico em uma ferramenta tecnológica com potencial de aplicação prática em sistemas logísticos inteligentes.

---

# 🎯 Funcionalidades Principais
📊 **Leitura de Dados** - Carrega instâncias do TSP a partir de arquivos de texto estruturados

🧬 **Algoritmo Genético** - Implementa otimização por AGs para a solução do Problema do Caixeiro Viajante (TSP)

🎨 **Interface Gráfica** - GUI desenvolvida para interação intuitiva e responsiva com design contemporâneo

📈 **Visualização de Resultados** - Apresenta a rota otimizada e custo total calculado pelo algoritmo

💾 **Gerenciamento de Instâncias** - Sistema de carregamento de matrizes de distâncias e coordenadas das cidades

---

## 📦 Instalação e Dependências 

### Requisitos do Sistema
- **Python** 3.8 ou superior
- **Sistema operacional:** Windows, Linux ou macOS

### Bibliotecas Necessárias

#### Framework GUI
![PySide6](https://img.shields.io/badge/PySide6-Qt%20for%20Python-green?style=for-the-badge&logo=qt)
```bash
pip install PySide6
```

#### Bibliotecas Padrão Python
![sys](https://img.shields.io/badge/sys-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)
![os](https://img.shields.io/badge/os-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)
![typing](https://img.shields.io/badge/typing-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)
![random](https://img.shields.io/badge/random-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)
![time](https://img.shields.io/badge/time-Python%20Stdlib-lightgrey?style=for-the-badge&logo=python)

---


## 🚀 Fluxo de Uso

1. **Carregar Matriz** → Clique em "📁 Carregar Matriz" e selecione seu arquivo
2. **Visualizar Dados** → A matriz de distâncias será exibida na tabela com destaque Visualizar
3. **Calcular Rota** → Clique em "📊 Calcular Melhor Rota" para executar o algoritmo Genético
4. **Analisar Resultados** → Visualize a rota ótima encontrada, seu custo total calculado e outras informaçoes relacionadas

---

## 🧬 Algoritmo Implementado

### Algoritmos Genéticos aplicados ao TSP

O **FlyFood** utiliza Algoritmos Genéticos com as seguintes características: 

✅ **Operador de Cruzamento:** Order Crossover (OX) que preserva a ordem relativa dos elementos

✅ **Avaliação de Aptidão:** Minimização da distância total percorrida na rota

✅ **Seleção:** Estratégias evolutivas para convergência à solução ótima

✅ **Validação:** Testes realizados na instância **brazil58** da TSPLib (58 cidades brasileiras)

### Complexidade Computacional
- **Espaço:** O(n²) para armazenar a matriz de distância
- **Escalabilidade:** Adequado para instâncias de médio a grande porte

> **Nota:** O uso de Algoritmos Genéticos permite encontrar soluções de alta qualidade em tempo computacional viável, mesmo para instâncias complexas do TSP.

---

## 📊 Resultados

Os testes realizados comprovaram que o algoritmo é capaz de identificar corretamente a melhor rota da instância **brazil58**, demonstrando:

- ✓ Convergência eficiente para soluções ótimas ou próximas do ótimo
- ✓ Robustez na preservação da ordem de visita às cidades
- ✓ Aplicabilidade prática em cenários de logística urbana

---

## 📚 Documentação Acadêmica

🔗 **Artigo completo sobre o desenvolvimento do FlyFood:**  
*(Link será adicionado posteriormente)*

---


# 📞 Suporte

Se tiver dúvidas, sugestões ou encontrar algum problema, fale com a gente:

 [![Email](https://img.shields.io/badge/Email-Contato%20FlyFood-red?style=for-the-badge&logo=gmail)](mailto:flyfood.com.br@gmail.com)

---

 ## 💻 Desenvolvedores

[Ana Clara](https://github.com/eianaxz) • [Maria Eduarda](https://github.com/mmaria-alves)  • [Laura](https://github.com/mlcordeiro) • [Filipe](https://github.com/nilipe)

---

<p align="center">
  <em>Desenvolvido como projeto acadêmico de otimização e algoritmos</em>
</p>
