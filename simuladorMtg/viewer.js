// ─── State ───
let replays = [];
let currentReplay = null;
let currentFrame = 0;
let isPlaying = false;
let playInterval = null;
let speed = 3;
let cardsData = {};
let panelOpen = null;

// ─── Init ───
loadCardsData();
loadReplayList();

async function loadCardsData() {
    try {
        const r = await fetch('/api/cards');
        cardsData = await r.json();
    } catch(e) { console.warn('Card data unavailable'); }
}

async function loadReplayList() {
    try {
        const r = await fetch('/api/replays');
        const d = await r.json();
        if (d.replays) replays = d.replays;
    } catch(e) {}
}

// ─── Panel ───
function togglePanel(type) {
    const panel = document.getElementById('sidePanel');
    // Se não passou type ou já está aberto com o mesmo type, fecha
    if (!type || panelOpen === type) {
        panel.classList.remove('open');
        panelOpen = null;
        return;
    }
    panelOpen = type;
    panel.classList.add('open');

    const title = document.getElementById('spTitle');
    const content = document.getElementById('spContent');

    if (type === 'sim') {
        title.textContent = 'Nova Simulacao';
        content.innerHTML = `
            <div class="sim-form-group">
                <label>Deck A</label>
                <select id="deckASelect"></select>
            </div>
            <div class="sim-form-group">
                <label>Deck B</label>
                <select id="deckBSelect"></select>
            </div>
            <div class="sim-form-group">
                <label>Partidas</label>
                <input type="number" id="matchCount" value="5" min="1" max="50">
            </div>
            <button class="sim-go-btn" onclick="runSimulation()">SIMULAR</button>
            <div id="simResult" style="margin-top:12px;"></div>
        `;
        loadDeckSelects();
    } else if (type === 'play') {
        title.textContent = 'Jogar Contra IA';
        content.innerHTML = `
            <div class="sim-form-group">
                <label>Seu Deck</label>
                <select id="playPlayerDeck"></select>
            </div>
            <div class="sim-form-group">
                <label>Deck do Oponente</label>
                <select id="playOpponentDeck"></select>
            </div>
            <button class="sim-go-btn" onclick="startInteractiveGame()">INICIAR JOGO</button>
            <div id="playGameArea" style="margin-top:16px;display:none;">
                <div style="background:var(--bg-card);padding:12px;border-radius:6px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <div><strong>Você:</strong> <span id="playPlayerLife">20</span> vida</div>
                        <div><strong>Oponente:</strong> <span id="playOppLife">20</span> vida</div>
                    </div>
                    <div style="text-align:center;font-size:11px;color:var(--text-dim);">
                        Turno <span id="playTurn">1</span> - <span id="playPhase">Untap</span>
                    </div>
                </div>
                <div id="playHand" style="margin-bottom:12px;"></div>
                <div id="playBattlefield" style="margin-bottom:12px;"></div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button class="sim-action-btn" onclick="playAction('play_land', {})" style="background:var(--green);">Jogar Terreno</button>
                    <button class="sim-action-btn" onclick="playAction('cast_spell', {})" style="background:var(--blue);">Conjurar Magia</button>
                    <button class="sim-action-btn" onclick="playAction('attack', {})" style="background:var(--red);">Atacar</button>
                    <button class="sim-action-btn" onclick="playAction('end_turn', {})" style="background:var(--gold);">Encerrar Turno</button>
                </div>
                <div id="playLog" style="margin-top:12px;max-height:200px;overflow-y:auto;font-size:10px;color:var(--text-dim);"></div>
            </div>
        `;
        loadPlayDeckSelects();
    } else if (type === 'import') {
        title.textContent = 'Importar Deck';
        content.innerHTML = `
            <div class="sim-form-group">
                <label>Nome do Deck</label>
                <input type="text" id="importDeckName" placeholder="Ex: Jund Midrange">
            </div>
            <div class="sim-form-group">
                <label>Formato</label>
                <select id="importFormat">
                    <option value="arena">MTG Arena (copiar/colar)</option>
                    <option value="simple">Simples (4 Lightning Bolt)</option>
                </select>
            </div>
            <div class="sim-form-group">
                <label>Lista de Cartas</label>
                <textarea id="importDeckText" rows="12" placeholder="4 Lightning Bolt (M21) 123&#10;4 Goblin Guide&#10;20 Mountain&#10;&#10;Ou cole a lista exportada do MTG Arena..." style="width:100%;padding:8px;background:var(--bg-card);border:1px solid var(--border);border-radius:4px;color:var(--text);font-size:11px;font-family:monospace;resize:vertical;"></textarea>
            </div>
            <button class="sim-go-btn" onclick="importDeck()">IMPORTAR DECK</button>
            <div id="importResult" style="margin-top:12px;"></div>
            <div id="customDecksList" style="margin-top:16px;"></div>
        `;
        loadCustomDecksList();
    } else if (type === 'learning') {
        title.textContent = 'Sistema de Aprendizado';
        content.innerHTML = `
            <div style="padding:12px;">
                <h4 style="color:var(--gold);margin-bottom:12px;">🧠 Aprendizado por Reforço</h4>

                <div style="background:var(--bg-card);padding:12px;border-radius:8px;margin-bottom:16px;">
                    <h5 style="color:var(--gold);margin-bottom:8px;">Jogar e Aprender</h5>
                    <p style="font-size:10px;color:var(--text-dim);margin-bottom:12px;">
                        Selecione os decks e jogue. O sistema aprende com suas jogadas!
                    </p>
                    <div class="sim-form-group">
                        <label>Seu Deck</label>
                        <select id="learningPlayerDeck"></select>
                    </div>
                    <div class="sim-form-group">
                        <label>Deck do Oponente</label>
                        <select id="learningOpponentDeck"></select>
                    </div>
                    <button class="sim-go-btn" onclick="startLearningGame()" style="width:100%;">INICIAR JOGO</button>

                    <div id="learningGameArea" style="margin-top:16px;display:none;">
                        <div style="background:var(--bg-dark);padding:10px;border-radius:6px;margin-bottom:10px;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                                <div><strong>Você:</strong> <span id="learningPlayerLife">20</span> vida</div>
                                <div><strong>Oponente:</strong> <span id="learningOppLife">20</span> vida</div>
                            </div>
                            <div style="text-align:center;font-size:10px;color:var(--text-dim);">
                                Turno <span id="learningTurn">1</span> - <span id="learningPhase">Untap</span>
                            </div>
                        </div>
                        <div id="learningHand" style="margin-bottom:10px;"></div>
                        <div id="learningBattlefield" style="margin-bottom:10px;"></div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;">
                            <button class="sim-action-btn" onclick="learningAction('play_land', {})" style="background:var(--green);font-size:10px;color:white;">Jogar Terreno</button>
                            <button class="sim-action-btn" onclick="learningAction('cast_spell', {})" style="background:var(--blue);font-size:10px;color:white;">Conjurar Magia</button>
                            <button class="sim-action-btn" onclick="learningAction('attack', {})" style="background:var(--red);font-size:10px;color:white;">Atacar</button>
                            <button class="sim-action-btn" onclick="learningAction('end_turn', {})" style="background:var(--gold);font-size:10px;color:white;">Encerrar Turno</button>
                        </div>
                        <div id="learningLog" style="margin-top:10px;max-height:150px;overflow-y:auto;font-size:9px;color:var(--text-dim);"></div>
                    </div>
                </div>

                <h5 style="color:var(--gold);margin-bottom:8px;">Estatísticas do Modelo</h5>
                <div id="learningStats" style="background:var(--bg-card);padding:12px;border-radius:8px;margin-bottom:16px;">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11px;">
                        <div><strong>Partidas:</strong> <span id="statGames">0</span></div>
                        <div><strong>Recompensa Total:</strong> <span id="statReward">0</span></div>
                        <div><strong>Média/Partida:</strong> <span id="statAvg">0</span></div>
                        <div><strong>Memória:</strong> <span id="statMemory">0</span></div>
                        <div><strong>Q-Table:</strong> <span id="statQTable">0</span></div>
                        <div><strong>Epsilon:</strong> <span id="statEpsilon">0</span></div>
                    </div>
                </div>

                <div style="display:flex;gap:8px;margin-bottom:12px;">
                    <button class="sim-go-btn" onclick="loadLearningStats()" style="flex:1;font-size:11px;padding:8px;">ATUALIZAR</button>
                </div>

                <div style="background:var(--bg-card);padding:12px;border-radius:8px;margin-bottom:16px;">
                    <h5 style="color:var(--gold);margin-bottom:8px;font-size:12px;">Treinamento</h5>
                    <div class="sim-form-group">
                        <label>Batch Size</label>
                        <input type="number" id="trainBatchSize" value="32" min="1" max="256">
                    </div>
                    <button class="sim-go-btn" onclick="trainModel()" style="width:100%;font-size:11px;padding:8px;">TREINAR MODELO</button>
                    <div id="trainResult" style="margin-top:8px;font-size:11px;"></div>
                </div>

                <div style="background:var(--bg-card);padding:12px;border-radius:8px;">
                    <h5 style="color:var(--gold);margin-bottom:8px;font-size:12px;">Como Funciona</h5>
                    <ul style="font-size:10px;color:var(--text-dim);padding-left:16px;line-height:1.6;">
                        <li>Jogue partidas com seus decks</li>
                        <li>O sistema grava suas decisões</li>
                        <li>Aprende quais jogadas levam à vitória</li>
                        <li>Melhora a IA conforme você joga</li>
                    </ul>
                </div>
            </div>
        `;
        loadLearningStats();
        loadLearningDeckSelects();
    } else {
        title.textContent = 'Replays Salvos';
        renderReplayList(content);
    }
}

async function loadDeckSelects() {
    try {
        const r = await fetch('/api/decks');
        const d = await r.json();
        const a = document.getElementById('deckASelect');
        const b = document.getElementById('deckBSelect');
        // Decks built-in
        d.decks.forEach((name, i) => {
            a.innerHTML += `<option value="${name}">${name}</option>`;
            b.innerHTML += `<option value="${name}" ${i===1?'selected':''}>${name}</option>`;
        });
        // Decks customizados
        if (d.custom_decks) {
            d.custom_decks.forEach(name => {
                a.innerHTML += `<option value="${name}">★ ${name}</option>`;
                b.innerHTML += `<option value="${name}">★ ${name}</option>`;
            });
        }
        // Decks Modern
        if (d.modern_decks) {
            d.modern_decks.forEach(name => {
                a.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
                b.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
            });
        }
    } catch(e) { console.error('Erro ao carregar decks:', e); }
}

async function importDeck() {
    const name = document.getElementById('importDeckName').value.trim();
    const text = document.getElementById('importDeckText').value;
    const format = document.getElementById('importFormat').value;

    if (!name) { alert('Digite um nome para o deck!'); return; }
    if (!text) { alert('Cole a lista de cartas!'); return; }

    document.getElementById('importResult').innerHTML = '<p style="color:var(--gold);">Importando...</p>';

    try {
        const r = await fetch('/api/import-deck', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({name: name, text: text})
        });
        const d = await r.json();

        if (d.success) {
            let html = `<div style="padding:10px;background:rgba(46,204,113,0.1);border:1px solid var(--life-green);border-radius:6px;">`;
            html += `<div style="color:var(--life-green);font-weight:700;">Deck importado com sucesso!</div>`;
            html += `<div style="font-size:11px;color:var(--text-dim);margin-top:4px;">`;
            html += `Cartas: ${d.card_count} | Terrenos: ${d.land_count}`;
            html += `</div>`;
            if (d.missing_cards && d.missing_cards.length > 0) {
                html += `<div style="font-size:10px;color:var(--life-red);margin-top:4px;">`;
                html += `Cartas nao encontradas: ${d.missing_cards.join(', ')}`;
                html += `</div>`;
            }
            html += `</div>`;
            document.getElementById('importResult').innerHTML = html;

            // Limpa o textarea
            document.getElementById('importDeckText').value = '';

            // Atualiza lista de decks customizados
            loadCustomDecksList();
        } else {
            document.getElementById('importResult').innerHTML = `<p style="color:var(--life-red);">Erro: ${d.error}</p>`;
        }
    } catch(e) {
        document.getElementById('importResult').innerHTML = '<p style="color:var(--life-red);">Erro ao importar deck</p>';
    }
}

async function loadCustomDecksList() {
    try {
        const r = await fetch('/api/custom-decks');
        const d = await r.json();
        const container = document.getElementById('customDecksList');

        if (!d.decks || d.decks.length === 0) {
            container.innerHTML = '<p style="color:var(--text-dim);font-size:11px;">Nenhum deck customizado salvo.</p>';
            return;
        }

        let html = '<div style="border-top:1px solid var(--border);padding-top:12px;">';
        html += '<label style="font-size:10px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;">Decks Salvos</label>';
        d.decks.forEach(deck => {
            html += `<div class="replay-entry" style="display:flex;justify-content:space-between;align-items:center;">`;
            html += `<div><div class="re-title">${deck.name}</div>`;
            html += `<div class="re-meta">${(deck.cards || []).length} tipos de cartas | ${deck.land_count || 0} terrenos</div></div>`;
            html += `<button onclick="deleteCustomDeck('${deck.filename}')" style="background:var(--life-red);border:none;color:#fff;padding:4px 8px;border-radius:3px;cursor:pointer;font-size:10px;">Excluir</button>`;
            html += `</div>`;
        });
        html += '</div>';
        container.innerHTML = html;
    } catch(e) { console.error('Erro ao carregar decks customizados:', e); }
}

async function deleteCustomDeck(filename) {
    if (!confirm('Tem certeza que deseja excluir este deck?')) return;

    try {
        const r = await fetch('/api/delete-deck', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({filename: filename})
        });
        const d = await r.json();

        if (d.success) {
            loadCustomDecksList();
        } else {
            alert('Erro ao excluir deck: ' + d.error);
        }
    } catch(e) {
        alert('Erro ao excluir deck');
    }
}

// ─── Learning System ───
async function loadLearningStats() {
    try {
        const r = await fetch('/api/learning/stats');
        const stats = await r.json();

        document.getElementById('statGames').textContent = stats.games_played || 0;
        document.getElementById('statReward').textContent = (stats.total_reward || 0).toFixed(2);
        document.getElementById('statAvg').textContent = (stats.average_reward || 0).toFixed(2);
        document.getElementById('statMemory').textContent = stats.memory_size || 0;
        document.getElementById('statQTable').textContent = stats.q_table_size || 0;
        document.getElementById('statEpsilon').textContent = (stats.epsilon || 0).toFixed(3);
    } catch(e) {
        console.error('Erro ao carregar estatísticas:', e);
    }
}

async function trainModel() {
    const batchSize = parseInt(document.getElementById('trainBatchSize').value);
    const resultDiv = document.getElementById('trainResult');

    resultDiv.innerHTML = '<p style="color:var(--gold);">Treinando...</p>';

    try {
        const r = await fetch('/api/learning/train', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({batch_size: batchSize})
        });
        const d = await r.json();

        if (d.success) {
            resultDiv.innerHTML = `
                <div style="color:var(--life-green);">
                    ✓ Treinamento concluído!<br>
                    <span style="font-size:10px;">Estatísticas atualizadas.</span>
                </div>
            `;
            loadLearningStats();
        } else {
            resultDiv.innerHTML = `<p style="color:var(--life-red);">Erro: ${d.error}</p>`;
        }
    } catch(e) {
        resultDiv.innerHTML = '<p style="color:var(--life-red);">Erro ao treinar modelo</p>';
    }
}

async function runSimulation() {
    const deckA = document.getElementById('deckASelect').value;
    const deckB = document.getElementById('deckBSelect').value;
    const matches = parseInt(document.getElementById('matchCount').value);
    if (deckA === deckB) { alert('Selecione decks diferentes!'); return; }

    document.getElementById('simResult').innerHTML = '<p style="color:var(--gold);">Simulando...</p>';
    try {
        const r = await fetch('/api/simulate', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({deck_a:deckA, deck_b:deckB, matches:matches})
        });
        const d = await r.json();
        if (d.success) {
            const pctA = ((d.deck_a_wins/d.matches)*100).toFixed(0);
            const pctB = ((d.deck_b_wins/d.matches)*100).toFixed(0);
            const winner = d.deck_a_wins >= d.deck_b_wins ? d.deck_a : d.deck_b;
            document.getElementById('simResult').innerHTML = `
                <div style="text-align:center;padding:8px;background:rgba(200,164,78,0.1);border-radius:6px;border:1px solid var(--gold-dark);">
                    <div style="font-family:'Cinzel',serif;color:var(--gold);font-size:14px;">${winner}</div>
                    <div style="font-size:11px;color:var(--text-dim);margin:4px 0;">vence com ${Math.max(pctA,pctB)}% win rate</div>
                    <div style="display:flex;gap:4px;margin-top:6px;">
                        <div style="flex:${pctA};background:var(--life-green);height:16px;border-radius:3px;display:flex;align-items:center;padding:0 4px;font-size:9px;font-weight:700;">${d.deck_a} ${pctA}%</div>
                        <div style="flex:${pctB};background:var(--life-red);height:16px;border-radius:3px;display:flex;align-items:center;padding:0 4px;font-size:9px;font-weight:700;justify-content:flex-end;">${pctB}% ${d.deck_b}</div>
                    </div>
                    <button onclick="togglePanel('replays')" style="margin-top:10px;padding:6px 16px;background:var(--gold);color:#000;border:none;border-radius:4px;cursor:pointer;font-weight:700;font-size:12px;">Ver Replays (${matches})</button>
                </div>
            `;
            // Recarrega a lista de replays
            await loadReplayList();
            console.log('Replays carregados:', replays.length);
        }
    } catch(e) {
        document.getElementById('simResult').innerHTML = '<p style="color:var(--life-red);">Erro na simulacao</p>';
    }
}

function renderReplayList(container) {
    console.log('Renderizando lista de replays:', replays.length);
    if (!replays.length) {
        container.innerHTML = '<p style="color:var(--text-dim);font-size:12px;">Nenhum replay encontrado. Rode uma simulação primeiro.</p>';
        return;
    }
    container.innerHTML = replays.map((r, i) => `
        <div class="replay-entry" onclick="loadReplay(${i})">
            <div class="re-title">${r.deck_a} vs ${r.deck_b}</div>
            <div class="re-meta">#${r.match_number} | ${r.turns} turnos | Winner: ${r.winner}</div>
        </div>
    `).join('');
}

async function loadReplay(idx) {
    const r = replays[idx];
    if (!r) { console.error('Replay não encontrado no índice', idx); return; }
    try {
        console.log('Carregando replay:', r.filename);
        const resp = await fetch(`/replays/${r.filename}`);
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        console.log('Replay carregado:', data.frames?.length, 'frames');
        currentReplay = data;
        currentFrame = 0;
        // Fecha o painel
        document.getElementById('sidePanel').classList.remove('open');
        panelOpen = null;
        // Renderiza o primeiro frame
        renderFrame();
        console.log('Frame renderizado com sucesso');
    } catch(e) {
        console.error('Erro ao carregar replay:', e);
        alert('Erro ao carregar replay: ' + e.message);
    }
}

// ─── Render Frame ───
function renderFrame() {
    try {
        if (!currentReplay) { console.warn('Nenhum replay carregado'); return; }
        if (!currentReplay.frames || !currentReplay.frames[currentFrame]) {
            console.warn('Frame não encontrado:', currentFrame);
            return;
        }
        const frame = currentReplay.frames[currentFrame];
        console.log('Renderizando frame', currentFrame, '- Turno', frame.turn, '- Fase', frame.phase);

        // Turn & Phase
        document.getElementById('turnBadge').textContent = `Turno ${frame.turn}`;
        updatePhaseDots(frame.phase);

        // Frame info
        document.getElementById('frameInfo').textContent = `${currentFrame+1} / ${currentReplay.frames.length}`;

        // Players
        renderPlayer(1, frame.player1, frame.active_player === 0, true, frame.phase, frame.active_player === 0);
        renderPlayer(2, frame.player2, frame.active_player === 1, false, frame.phase, frame.active_player === 1);

        // Log
        const log = document.getElementById('gameLog');
        log.innerHTML = (frame.log || []).map(l => `<p>${l}</p>`).join('');
        log.scrollTop = log.scrollHeight;

        // Buttons
        document.getElementById('btnFirst').disabled = currentFrame === 0;
        document.getElementById('btnPrev').disabled = currentFrame === 0;
        document.getElementById('btnLast').disabled = currentFrame === (currentReplay.frames.length - 1);
        document.getElementById('btnNext').disabled = currentFrame === (currentReplay.frames.length - 1);
    } catch(e) {
        console.error('Erro ao renderizar frame:', e);
    }
}

function renderPlayer(num, data, isActive, isSelf, phase, isCurrentPlayer) {
    const prefix = `p${num}`;

    // Life
    const lifeEl = document.getElementById(`${prefix}Life`);
    lifeEl.textContent = data.life;
    lifeEl.className = 'life-circle ' + (data.life >= 15 ? 'high' : data.life >= 8 ? 'mid' : 'low');

    // Name
    document.getElementById(`${prefix}Name`).textContent = data.name;

    // Active
    document.getElementById(`${prefix}Active`).className = 'active-indicator' + (isActive ? ' active' : '');

    // Library
    document.getElementById(`${prefix}Lib`).textContent = data.library_count;

    // Player Phases
    updatePlayerPhases(prefix, phase, isCurrentPlayer);

    // Battlefield
    const creatures = (data.battlefield || []).filter(c => c.type === 'CREATURE');
    const lands = (data.battlefield || []).filter(c => c.is_land);
    const other = (data.battlefield || []).filter(c => !c.is_land && c.type !== 'CREATURE');

    renderBfRow(`${prefix}Creatures`, creatures, 8);
    renderBfRow(`${prefix}Lands`, lands.concat(other), 8);

    // Graveyard & Exile
    renderSideZone(`${prefix}Graveyard`, `${prefix}GraveCount`, data.graveyard || [], 'graveyard');
    renderSideZone(`${prefix}Exile`, `${prefix}ExileCount`, data.exile || [], 'exile');

    // Hand
    if (isSelf) {
        renderSelfHand(data, isActive);
    } else {
        renderOppHand(data);
    }
}

function updatePlayerPhases(prefix, phase, isCurrentPlayer) {
    const phases = ['untap','upkeep','draw','main1','combat','main2','end'];
    const phaseMap = {
        'untap': 'untap', 'upkeep': 'upkeep', 'draw': 'draw',
        'pre_combat_main': 'main1', 'main1': 'main1', 'precombat_main': 'main1',
        'combat': 'combat', 'combat_begin': 'combat', 'declare_attackers': 'combat',
        'declare_blockers': 'combat', 'combat_damage': 'combat',
        'first_strike_damage': 'combat', 'damage': 'combat', 'combat_end': 'combat',
        'post_combat_main': 'main2', 'main2': 'main2', 'postcombat_main': 'main2',
        'end': 'end', 'cleanup': 'end', 'start': 'untap', 'beginning': 'untap'
    };
    const currentPhase = phaseMap[phase] || 'main1';
    const currentIndex = phases.indexOf(currentPhase);

    const container = document.getElementById(`${prefix}Phases`);
    if (!container) return;

    const steps = container.querySelectorAll('.player-phase-step');
    steps.forEach((step, i) => {
        step.classList.remove('past', 'active', 'future');
        if (!isCurrentPlayer) {
            step.classList.add('future');
        } else if (i < currentIndex) {
            step.classList.add('past');
        } else if (i === currentIndex) {
            step.classList.add('active');
        } else {
            step.classList.add('future');
        }
    });
}

function renderSideZone(contentId, countId, cards, zoneType) {
    const contentEl = document.getElementById(contentId);
    const countEl = document.getElementById(countId);
    countEl.textContent = cards.length;

    if (cards.length === 0) {
        contentEl.innerHTML = '<div style="padding:4px;font-size:8px;color:var(--text-dim);text-align:center;">Vazio</div>';
        return;
    }

    contentEl.innerHTML = cards.map(c => {
        const safeName = c.name.replace(/'/g, "\\'");
        return `<div class="sz-card ${zoneType}"
                    onmouseenter="showTooltip(event,'${safeName}')"
                    onmouseleave="hideTooltip()"
                    onmousemove="moveTooltip(event)">
            ${c.name}
        </div>`;
    }).reverse().join('');
}

function renderBfRow(elementId, cards, maxSlots) {
    const el = document.getElementById(elementId);
    let html = '';
    for (let i = 0; i < Math.max(cards.length, maxSlots); i++) {
        if (i < cards.length) {
            const c = cards[i];
            const tappedClass = c.tapped ? ' tapped' : '';
            const imgFile = getCardImage(c.name);
            let statsHtml = '';
            if (c.power !== null && c.toughness !== null) {
                statsHtml = `<span class="co-stats">${c.power}/${c.toughness}</span>`;
            }
            html += `<div class="card-slot">
                <div class="card-in-play${tappedClass}" data-card-name="${c.name}"
                     onmouseenter="showTooltip(event,'${c.name.replace(/'/g,"\\'")}')"
                     onmouseleave="hideTooltip()" onmousemove="moveTooltip(event)">
                    ${imgFile ? `<img class="card-art" src="${imgFile}" alt="${c.name}" onerror="this.style.display='none'">` : ''}
                    <div class="card-overlay">
                        <div class="co-name">${c.name}</div>
                        ${statsHtml}
                    </div>
                </div>
            </div>`;
        } else {
            html += `<div class="card-slot empty"></div>`;
        }
    }
    el.innerHTML = html;
}

function renderSelfHand(data, isActive) {
    const el = document.getElementById('selfHandCards');
    if (isActive && data.hand_cards && data.hand_cards.length > 0) {
        el.innerHTML = data.hand_cards.map(c => {
            const imgFile = getCardImage(c.name);
            return `<div class="hand-card" data-card-name="${c.name}"
                        onmouseenter="showTooltip(event,'${c.name.replace(/'/g,"\\'")}')"
                        onmouseleave="hideTooltip()" onmousemove="moveTooltip(event)">
                ${imgFile ? `<img src="${imgFile}" alt="${c.name}" onerror="this.parentElement.innerHTML='<div style=\\'display:flex;align-items:center;justify-content:center;height:100%;font-size:7px;text-align:center;padding:2px;\\'>${c.name}</div>'">` :
                `<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:7px;text-align:center;padding:2px;background:var(--bg-card);">${c.name}</div>`}
            </div>`;
        }).join('');
    } else {
        el.innerHTML = '';
        for (let i = 0; i < (data.hand_count || 0); i++) {
            el.innerHTML += `<div class="hand-card-back"><div class="cb-pattern"></div></div>`;
        }
    }
}

function renderOppHand(data) {
    const el = document.getElementById('oppHand');
    let html = '<div class="hand-cards">';
    for (let i = 0; i < (data.hand_count || 0); i++) {
        html += `<div class="hand-card-back" style="width:35px;height:48px;"><div class="cb-pattern" style="width:24px;height:36px;"></div></div>`;
    }
    html += '</div>';
    el.innerHTML = html;
}

function getCardImage(cardName) {
    for (const [id, data] of Object.entries(cardsData)) {
        if (data.name && data.name.toLowerCase() === cardName.toLowerCase()) {
            if (data.local_images && data.local_images.art_crop) {
                return `/card-images/${data.local_images.art_crop}`;
            }
        }
    }
    return null;
}

// ─── Phase Timeline ───
function updatePhaseDots(phase) {
    const phases = ['untap','upkeep','draw','main1','combat','main2','end'];
    const phaseMap = {
        'untap': 'ph-untap', 'upkeep': 'ph-upkeep', 'draw': 'ph-draw',
        'pre_combat_main': 'ph-main1', 'main1': 'ph-main1', 'precombat_main': 'ph-main1',
        'combat': 'ph-combat', 'combat_begin': 'ph-combat', 'declare_attackers': 'ph-combat',
        'declare_blockers': 'ph-combat', 'combat_damage': 'ph-combat',
        'first_strike_damage': 'ph-combat', 'damage': 'ph-combat', 'combat_end': 'ph-combat',
        'post_combat_main': 'ph-main2', 'main2': 'ph-main2', 'postcombat_main': 'ph-main2',
        'end': 'ph-end', 'cleanup': 'ph-end', 'start': 'ph-untap', 'beginning': 'ph-untap'
    };
    const activeId = phaseMap[phase] || 'ph-main1';
    const activeIndex = phases.findIndex(p => `ph-${p}` === activeId);

    phases.forEach((p, i) => {
        const step = document.getElementById(`ph-${p}`);
        if (step) {
            step.classList.remove('past', 'active', 'future');
            if (i < activeIndex) {
                step.classList.add('past');
            } else if (i === activeIndex) {
                step.classList.add('active');
            } else {
                step.classList.add('future');
            }
        }
    });
}

// ─── Tooltip ───
function showTooltip(e, cardName) {
    const tip = document.getElementById('cardTooltip');
    let found = null;
    for (const [id, data] of Object.entries(cardsData)) {
        if (data.name && data.name.toLowerCase() === cardName.toLowerCase()) { found = data; break; }
    }
    if (!found) {
        for (const [id, data] of Object.entries(cardsData)) {
            if (data.name && data.name.toLowerCase().includes(cardName.toLowerCase())) { found = data; break; }
        }
    }

    if (found) {
        const img = found.local_images ? found.local_images.normal : null;
        if (img) {
            tip.innerHTML = `<img src="/card-images/${img}" alt="${found.name}" onerror="this.parentElement.innerHTML='<div class=\\'ct-fallback\\'><div class=\\'ct-name\\'>${found.name}</div><div class=\\'ct-type\\'>${found.type_line||''}</div><div class=\\'ct-text\\'>${found.oracle_text||''}</div></div>'">`;
        } else {
            tip.innerHTML = `<div class="ct-fallback"><div class="ct-name">${found.name}</div><div class="ct-type">${found.type_line||''}</div><div class="ct-text">${found.oracle_text||''}</div>${found.power?`<div class="ct-stats">${found.power}/${found.toughness}</div>`:''}</div>`;
        }
    } else {
        tip.innerHTML = `<div class="ct-fallback"><div class="ct-name">${cardName}</div></div>`;
    }
    tip.classList.add('show');
    moveTooltip(e);
}

function hideTooltip() {
    document.getElementById('cardTooltip').classList.remove('show');
}

function moveTooltip(e) {
    const tip = document.getElementById('cardTooltip');
    let x = e.clientX + 15;
    let y = e.clientY - 100;
    if (x + 240 > window.innerWidth) x = e.clientX - 255;
    if (y < 10) y = 10;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
}

// ─── Controls ───
function goFirst() { currentFrame = 0; renderFrame(); }
function goPrev() { if (currentFrame > 0) { currentFrame--; renderFrame(); } }
function goNext() { if (currentReplay && currentFrame < currentReplay.frames.length - 1) { currentFrame++; renderFrame(); } }
function goLast() { if (currentReplay) { currentFrame = currentReplay.frames.length - 1; renderFrame(); } }

// ─── Interactive Game ───
let interactiveGameId = null;
let interactiveState = null;

async function loadPlayDeckSelects() {
    console.log('Carregando decks para jogar...');
    try {
        const r = await fetch('/api/decks');
        const d = await r.json();
        console.log('Decks recebidos:', d);
        const playerSelect = document.getElementById('playPlayerDeck');
        const oppSelect = document.getElementById('playOpponentDeck');

        if (!playerSelect || !oppSelect) {
            console.error('Selects não encontrados');
            return;
        }

        // Limpa selects
        playerSelect.innerHTML = '';
        oppSelect.innerHTML = '';

        // Decks built-in
        d.decks.forEach(name => {
            playerSelect.innerHTML += `<option value="${name}">${name}</option>`;
            oppSelect.innerHTML += `<option value="${name}">${name}</option>`;
        });

        // Decks customizados
        if (d.custom_decks) {
            d.custom_decks.forEach(name => {
                playerSelect.innerHTML += `<option value="${name}">★ ${name}</option>`;
                oppSelect.innerHTML += `<option value="${name}">★ ${name}</option>`;
            });
        }

        // Decks Modern
        if (d.modern_decks) {
            d.modern_decks.forEach(name => {
                playerSelect.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
                oppSelect.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
            });
        }

        console.log('Decks carregados com sucesso');
    } catch(e) {
        console.error('Erro ao carregar decks:', e);
    }
}

async function startInteractiveGame() {
    const playerDeck = document.getElementById('playPlayerDeck').value;
    const opponentDeck = document.getElementById('playOpponentDeck').value;

    if (!playerDeck || !opponentDeck) {
        alert('Selecione ambos os decks');
        return;
    }

    try {
        const r = await fetch('/api/interactive/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_deck: playerDeck,
                opponent_deck: opponentDeck
            })
        });

        const data = await r.json();

        if (data.success) {
            interactiveGameId = data.game_id;
            interactiveState = data.state;
            document.getElementById('playGameArea').style.display = 'block';
            updateInteractiveUI();
            addPlayLog('Jogo iniciado! Você começa.');
        } else {
            alert('Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch(e) {
        console.error('Erro ao iniciar jogo:', e);
        alert('Erro ao iniciar jogo');
    }
}

async function playAction(action, params) {
    if (!interactiveGameId) {
        alert('Inicie um jogo primeiro');
        return;
    }

    try {
        const r = await fetch('/api/interactive/action', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                game_id: interactiveGameId,
                action: action,
                params: params
            })
        });

        const data = await r.json();

        if (data.success) {
            interactiveState = data.state;
            updateInteractiveUI();

            if (data.result && data.result.message) {
                addPlayLog(data.result.message);
            }

            if (data.game_over) {
                addPlayLog(`Jogo acabou! Vencedor: ${data.winner}`);
                interactiveGameId = null;
            }
        } else {
            alert('Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch(e) {
        console.error('Erro ao jogar:', e);
    }
}

function updateInteractiveUI() {
    if (!interactiveState) return;

    document.getElementById('playPlayerLife').textContent = interactiveState.player1.life;
    document.getElementById('playOppLife').textContent = interactiveState.player2.life;
    document.getElementById('playTurn').textContent = interactiveState.turn;
    document.getElementById('playPhase').textContent = interactiveState.phase;

    // Atualiza mão
    const handDiv = document.getElementById('playHand');
    handDiv.innerHTML = '<strong>Sua Mão:</strong><br>';
    interactiveState.player1.hand.forEach((card, i) => {
        handDiv.innerHTML += `<span style="display:inline-block;padding:4px 8px;margin:2px;background:var(--bg-card);border-radius:4px;font-size:10px;">${card}</span>`;
    });

    // Atualiza battlefield
    const bfDiv = document.getElementById('playBattlefield');
    bfDiv.innerHTML = '<strong>Seu Campo:</strong><br>';
    interactiveState.player1.battlefield.forEach(card => {
        bfDiv.innerHTML += `<span style="display:inline-block;padding:4px 8px;margin:2px;background:var(--green);border-radius:4px;font-size:10px;">${card}</span>`;
    });
}

function addPlayLog(message) {
    const logDiv = document.getElementById('playLog');
    logDiv.innerHTML += `<div>${message}</div>`;
    logDiv.scrollTop = logDiv.scrollHeight;
}

function togglePlay() {
    isPlaying = !isPlaying;
    document.getElementById('btnPlay').innerHTML = isPlaying ? '&#x23F8; Pause' : '&#x25B6; Play';
    if (isPlaying) {
        playInterval = setInterval(() => {
            if (currentReplay && currentFrame < currentReplay.frames.length - 1) {
                currentFrame++;
                renderFrame();
            } else { togglePlay(); }
        }, 2000 / speed);
    } else { clearInterval(playInterval); }
}

document.getElementById('speedSlider').addEventListener('input', (e) => {
    speed = parseFloat(e.target.value);
    document.getElementById('speedLabel').textContent = (speed % 1 === 0 ? speed : speed.toFixed(1)) + 'x';
    if (isPlaying) { clearInterval(playInterval); togglePlay(); togglePlay(); }
});

document.addEventListener('keydown', (e) => {
    if (!currentReplay) return;
    switch(e.key) {
        case 'ArrowLeft': goPrev(); break;
        case 'ArrowRight': goNext(); break;
        case ' ': e.preventDefault(); togglePlay(); break;
        case 'Home': goFirst(); break;
        case 'End': goLast(); break;
    }
});

// ─── Learning Game ───
let learningGameId = null;
let learningState = null;

async function loadLearningDeckSelects() {
    console.log('Carregando decks para aprendizado...');

    // Aguarda um pouco para garantir que o DOM foi atualizado
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
        const r = await fetch('/api/decks');
        const d = await r.json();
        console.log('Decks recebidos:', d);

        const playerSelect = document.getElementById('learningPlayerDeck');
        const oppSelect = document.getElementById('learningOpponentDeck');

        console.log('Player select:', playerSelect);
        console.log('Opponent select:', oppSelect);

        if (!playerSelect || !oppSelect) {
            console.error('Selects não encontrados!');
            console.log('Elementos na página:', document.querySelectorAll('select').length);
            return;
        }

        // Limpa selects
        playerSelect.innerHTML = '';
        oppSelect.innerHTML = '';

        // Decks built-in
        d.decks.forEach(name => {
            playerSelect.innerHTML += `<option value="${name}">${name}</option>`;
            oppSelect.innerHTML += `<option value="${name}">${name}</option>`;
        });

        // Decks customizados
        if (d.custom_decks) {
            d.custom_decks.forEach(name => {
                playerSelect.innerHTML += `<option value="${name}">★ ${name}</option>`;
                oppSelect.innerHTML += `<option value="${name}">★ ${name}</option>`;
            });
        }

        // Decks Modern
        if (d.modern_decks) {
            d.modern_decks.forEach(name => {
                playerSelect.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
                oppSelect.innerHTML += `<option value="${name}">⚡ ${name} (Modern)</option>`;
            });
        }

        console.log('Decks carregados! Player tem', playerSelect.options.length, 'opções');
    } catch(e) {
        console.error('Erro ao carregar decks:', e);
    }
}

async function startLearningGame() {
    console.log('Iniciando jogo de aprendizado...');

    const playerDeck = document.getElementById('learningPlayerDeck').value;
    const opponentDeck = document.getElementById('learningOpponentDeck').value;

    console.log('Player deck:', playerDeck);
    console.log('Opponent deck:', opponentDeck);

    if (!playerDeck || !opponentDeck) {
        console.error('Decks não selecionados');
        alert('Selecione ambos os decks');
        return;
    }

    try {
        console.log('Enviando requisição para /api/interactive/start...');
        const r = await fetch('/api/interactive/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                player_deck: playerDeck,
                opponent_deck: opponentDeck
            })
        });

        console.log('Resposta recebida, status:', r.status);
        const data = await r.json();
        console.log('Dados recebidos:', data);

        if (data.success) {
            console.log('Jogo iniciado com sucesso! Game ID:', data.game_id);
            learningGameId = data.game_id;
            learningState = data.state;
            document.getElementById('learningGameArea').style.display = 'block';
            updateLearningUI();
            addLearningLog('Jogo iniciado! Você começa.');
        } else {
            console.error('Erro na resposta:', data.error);
            alert('Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch(e) {
        console.error('Erro ao iniciar jogo:', e);
        alert('Erro ao iniciar jogo: ' + e.message);
    }
}

async function learningAction(action, params) {
    console.log('Ação:', action, 'Params:', params);

    if (!learningGameId) {
        console.error('Jogo não iniciado');
        alert('Inicie um jogo primeiro');
        return;
    }

    try {
        console.log('Enviando ação para /api/interactive/action...');
        const r = await fetch('/api/interactive/action', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                game_id: learningGameId,
                action: action,
                params: params
            })
        });

        console.log('Resposta recebida, status:', r.status);
        const data = await r.json();
        console.log('Dados recebidos:', data);

        if (data.success) {
            console.log('Ação processada com sucesso');
            learningState = data.state;
            updateLearningUI();

            if (data.result && data.result.message) {
                addLearningLog(data.result.message);
            }

            if (data.game_over) {
                addLearningLog(`Jogo acabou! Vencedor: ${data.winner}`);
                learningGameId = null;
                // Atualiza estatísticas
                loadLearningStats();
            }
        } else {
            console.error('Erro na resposta:', data.error);
            alert('Erro: ' + (data.error || 'Erro desconhecido'));
        }
    } catch(e) {
        console.error('Erro ao jogar:', e);
        alert('Erro ao jogar: ' + e.message);
    }
}

function updateLearningUI() {
    console.log('Atualizando UI de aprendizado...');
    console.log('Estado:', learningState);

    if (!learningState) {
        console.error('Estado não disponível');
        return;
    }

    document.getElementById('learningPlayerLife').textContent = learningState.player1.life;
    document.getElementById('learningOppLife').textContent = learningState.player2.life;
    document.getElementById('learningTurn').textContent = learningState.turn;
    document.getElementById('learningPhase').textContent = learningState.phase;

    console.log('Mão do jogador:', learningState.player1.hand);
    console.log('Mão do oponente:', learningState.player2.hand_count);

    // Atualiza mão
    const handDiv = document.getElementById('learningHand');
    handDiv.innerHTML = '<strong>Sua Mão (' + learningState.player1.hand.length + ' cartas):</strong><br>';
    learningState.player1.hand.forEach((card, i) => {
        console.log('Carta', i, ':', card);
        handDiv.innerHTML += `<span style="display:inline-block;padding:3px 6px;margin:2px;background:var(--bg-card);border-radius:3px;font-size:9px;">${card}</span>`;
    });

    // Atualiza mão do oponente (apenas quantidade)
    const oppHandDiv = document.createElement('div');
    oppHandDiv.innerHTML = `<strong>Mão do Oponente:</strong> ${learningState.player2.hand_count} cartas`;
    handDiv.appendChild(oppHandDiv);

    // Atualiza battlefield
    const bfDiv = document.getElementById('learningBattlefield');
    bfDiv.innerHTML = '<strong>Seu Campo (' + learningState.player1.battlefield.length + ' cartas):</strong><br>';
    learningState.player1.battlefield.forEach(card => {
        bfDiv.innerHTML += `<span style="display:inline-block;padding:3px 6px;margin:2px;background:var(--green);border-radius:3px;font-size:9px;">${card}</span>`;
    });

    console.log('UI atualizada!');
}

function addLearningLog(message) {
    const logDiv = document.getElementById('learningLog');
    logDiv.innerHTML += `<div>${message}</div>`;
    logDiv.scrollTop = logDiv.scrollHeight;
}
