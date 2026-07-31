# MTG Match Simulator - Roadmap Completo

## 🎯 Visão Geral
Simulador completo de partidas MTG com IA aprendendo por reforço, usando dados reais de competição.

---

## ✅ FASE 1: Base (CONCLUÍDA)

### 1.1 Motor de Regras
- [x] Fases do turno (untap, upkeep, draw, main, combat, end)
- [x] Sistema de combate (ataque, bloqueio, dano)
- [x] State-Based Actions (SBAs)
- [x] Pool de mana
- [x] Compra de cartas
- [x] Dano direto e ganho de vida

### 1.2 Base de Cartas
- [x] 6.325 cartas do Scryfall
- [x] Imagens das cartas
- [x] Terrenos não-básicos (100+ mapeados)
- [x] Parseamento de texto

### 1.3 Efeitos de Cartas
- [x] Ad Nauseam
- [x] Angel's Grace
- [x] Phyrexian Unlife
- [x] Thassa's Oracle (condição de vitória)
- [x] Preordain, Profane Tutor
- [x] Pact/Force of Negation
- [x] Path to Exile
- [x] Lotus Bloom
- [x] Sleight of Hand, Spoils of the Vault

### 1.4 Interface
- [x] Viewer HTML com replay
- [x] Importação de decks (MTG Arena format)
- [x] Visualização de cemitério e exílio
- [x] Controles de velocidade

### 1.5 Aprendizado
- [x] Q-Learning por reforço
- [x] Memória de replay
- [x] API para treinar
- [x] Interface web

---

## 🚀 FASE 2: Expansão de Dados (EM ANDAMENTO)

### 2.1 MTGJSON Integration
- [x] Módulo criado (`mtgjson_integration.py`)
- [ ] Baixar AllPrintings.json (200MB+)
- [ ] Extrair dados completos (rulings, legalities)
- [ ] Filtrar cartas Modern legais
- [ ] Integrar com cards_db.py

### 2.2 Decklists de Competição
- [ ] MTGGoldfish scraper
- [ ] MTGTop8 scraper
- [ ] MTGO logs parser
- [ ] Database de decks (top 100 decks por archtype)

### 2.3 Validação
- [ ] Comparar simulação com logs reais
- [ ] Ajustar probabilidades
- [ ] Validar decisões da IA

---

## 🔧 FASE 3: Motor de Regras Completo

### 3.1 Stack Completo
- [ ] Sistema de prioridades
- [ ] Respostas em cadeia
- [ ] Counter spells
- [ ] Instant speed interactions

### 3.2 Triggered Abilities
- [ ] ETB (Enter the Battlefield)
- [ ] ATK triggers
- [ ] Death triggers
- [ ] Upkeep/End step triggers

### 3.3 Keyword Actions
- [ ] Scry
- [ ] Surveil
- [ ] Explore
- [ ] Cascade
- [ ] Convoke
- [ ] Delve
- [ ] Etc.

### 3.4 Regras de Torneio
- [ ] Mulligan (London mulligan)
- [ ] Time limits
- [ ] Sideboarding
- [ ] Match structure (best of 3)

---

## 🧠 FASE 4: IA Avançada

### 4.1 Deep Learning
- [ ] Neural network para avaliação de estado
- [ ] Reinforcement learning avançado (PPO, A3C)
- [ ] Self-play para treinamento
- [ ] Transfer learning entre decks

### 4.2 Avaliação de Estado
- [ ] Função de avaliação complexa
- [ ] Considerar card advantage
- [ ] Considerar tempo (tempo de mana)
- [ ] Considerar ameaças do oponente

### 4.3 Tomada de Decisão
- [ ] MCTS (Monte Carlo Tree Search)
- [ ] Simulações internas
- [ ] Avaliação de riscos
- [ ] Bluffing e mind games

---

## 📊 FASE 5: Análise e Estatísticas

### 5.1 Matchup Analysis
- [ ] Simular todos os matchups (50 decks x 50 decks)
- [ ] Calcular win rates
- [ ] Identificar decks broken
- [ ] Sugerir sideboard

### 5.2 Meta Analysis
- [ ] Tracking de popularidade
- [ ] Detecção de trends
- [ ] Previsão de meta
- [ ] Sugestão de decks para torneios

### 5.3 Visualização
- [ ] Dashboard com gráficos
- [ ] Heatmaps de matchups
- [ ] Timeline de meta evolution
- [ ] Export de relatórios

---

## 🎮 FASE 6: Funcionalidades Extras

### 6.1 Draft Simulator
- [ ] Simular booster draft
- [ ] IA para pick decisions
- [ ] Avaliação de deck pool
- [ ] Treino de draft

### 6.2 Deck Builder
- [ ] Sugestão de cartas
- [ ] Análise de curva de mana
- [ ] Detecção de sinergias
- [ ] Teste contra meta

### 6.3 Training Mode
- [ ] Jogar contra IA
- [ ] Aprender mecânicas
- [ ] Simular situações específicas
- [ ] Feedback em tempo real

---

## 📦 Entregáveis

### Curto Prazo (1-2 meses)
1. MTGJSON completo integrado
2. 100+ decklists Modern
3. Motor de regras com stack completo
4. IA treinada com 10.000 partidas

### Médio Prazo (3-6 meses)
1. Todos os formatos (Modern, Legacy, Vintage)
2. Draft simulator funcional
3. Meta analysis dashboard
4. 1 milhão de partidas simuladas

### Longo Prazo (6-12 meses)
1. IA nível competitivo
2. Self-play avançado
3. Previsão de meta precisa
4. Ferramenta profissional usada por players

---

## 🛠️ Tecnologias

### Backend
- Python 3.11+
- NumPy (cálculos)
- TensorFlow/PyTorch (deep learning)
- SQLite (database)

### Frontend
- HTML5 + CSS3
- JavaScript (vanilla)
- D3.js (gráficos)
- Chart.js (visualizações)

### Dados
- MTGJSON (cartas)
- Scryfall (imagens)
- MTGGoldfish (decklists)
- MTGTop8 (resultados)

---

## 📈 Métricas de Sucesso

1. **Precisão**: Simulação bate com logs reais em 95%+
2. **Performance**: 1000 partidas/segundo
3. **IA**: Win rate > 60% contra players humanos
4. **Dados**: 10.000+ decklists coletadas
5. **Uso**: Ferramenta usada por 100+ players

---

## 🎯 Próximo Passo Imediato

**Baixar e integrar MTGJSON completo:**
```bash
cd simuladorMtg
python mtgjson_integration.py
```

Isso vai:
1. Baixar 200MB+ de dados
2. Extrair todas as cartas
3. Filtrar Modern legais
4. Salvar em `mtgjson_data/modern_cards.json`

Depois integrar com o sistema atual!
