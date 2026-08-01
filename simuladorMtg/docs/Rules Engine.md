O banco de dados apenas armazena informações. O "cérebro" do simulador é um motor que interpreta essas informações.

Por exemplo:

Jogador conjura Lightning Bolt

↓

Evento:
CAST_SPELL

↓

Stack.push(Bolt)

↓

Prioridade

↓

Resposta?

↓

Resolve

↓

Dano

↓

State Based Actions

↓

Triggers

↓

Prioridade novamente

Esse fluxo é o que faz um simulador agir como uma partida real.

Minha sugestão para o seu projeto

Como você já demonstrou interesse em criar um simulador de partidas de Modern e trabalhar com interações complexas, eu estruturaria tudo em um projeto com:

Banco PostgreSQL para cartas, mecânicas, regras e metadados.
Backend em Node.js + TypeScript para o motor de regras.
Prisma ORM para acesso ao banco.
JSON para representar habilidades e efeitos de cada carta.
IA (como um modelo de linguagem) apenas para interpretar textos muito complexos de cartas ou explicar jogadas, nunca para decidir as regras da partida. As decisões da partida devem ficar no motor determinístico.

Esse modelo permite adicionar novas coleções e mecânicas sem precisar reescrever todo o sistema, tornando o simulador escalável e confiável.