# ConectaRun 🎮

Jogo de plataforma 2D desenvolvido em Python com Pygame.
Atividade Prática — Linguagem de Programação Aplicada — UNINTER 2026

## Controles
| Tecla         | Ação                  |
|---------------|-----------------------|
| ← / A         | Mover para esquerda   |
| → / D         | Mover para direita    |
| SPACE / W / ↑ | Pular                 |
| ESC           | Voltar ao menu        |

## Objetivo
- Chegue até a **bandeira verde** no final da fase
- Colete o máximo de **moedas** no caminho
- Desvie dos **inimigos** (bolinhas vermelhas) e **espinhos**
- Você tem **3 vidas** — não as perca todas!

## Como rodar (desenvolvimento)
```bash
pip install pygame
python main.py
```

## Como compilar para Windows (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```
O `.exe` ficará na pasta `dist/`.
Copie a pasta `assets/` para dentro de `dist/` antes de zipar.

## Estrutura
```
conectarun/
├── main.py
├── requirements.txt
├── README.md
└── assets/
    ├── images/
    └── sounds/
```

## Aluno
Arthur Harysson Matos Silva — RU: 5226465
CST em Análise e Desenvolvimento de Sistemas — UNINTER 2026