import pygame
import sys
import os
import random

# ── Configurações ────────────────────────────────────────────────────
LARGURA, ALTURA = 800, 500
FPS = 60
TITULO = "ConectaRun"

# Cores
BRANCO    = (255, 255, 255)
PRETO     = (0,   0,   0)
AZUL_ESC  = (15,  30,  80)
AZUL      = (30,  80, 180)
AZUL_CLA  = (100, 160, 240)
AMARELO   = (255, 210,  50)
VERMELHO  = (200,  40,  40)
VERDE     = (50,  200,  80)
CINZA     = (80,  80,  80)
LARANJA   = (230, 120,  20)
BRANCO_T  = (255, 255, 255, 180)

# ── Estados ──────────────────────────────────────────────────────────
MENU    = "menu"
JOGANDO = "jogando"
VITORIA = "vitoria"
DERROTA = "derrota"

# ── Funções utilitárias ──────────────────────────────────────────────
def desenhar_texto(surf, texto, tamanho, cor, x, y, centralizar=True):
    fonte = pygame.font.SysFont("Arial", tamanho, bold=True)
    superficie = fonte.render(texto, True, cor)
    rect = superficie.get_rect()
    if centralizar:
        rect.centerx = x
    else:
        rect.x = x
    rect.y = y
    surf.blit(superficie, rect)

def desenhar_texto_sombra(surf, texto, tamanho, cor, x, y, centralizar=True):
    desenhar_texto(surf, texto, tamanho, PRETO, x+2, y+2, centralizar)
    desenhar_texto(surf, texto, tamanho, cor, x, y, centralizar)

# ── Plataforma ───────────────────────────────────────────────────────
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura=18, cor=AZUL):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(cor)
        # Borda superior mais clara
        pygame.draw.rect(self.image, AZUL_CLA, (0, 0, largura, 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# ── Espinho (obstáculo) ───────────────────────────────────────────────
class Espinho(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Triângulo
        pygame.draw.polygon(self.image, VERMELHO, [(12, 0), (24, 24), (0, 24)])
        pygame.draw.polygon(self.image, AMARELO,  [(12, 4), (20, 22), (4, 22)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# ── Moeda ─────────────────────────────────────────────────────────────
class Moeda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, AMARELO, (10, 10), 10)
        pygame.draw.circle(self.image, LARANJA, (10, 10),  7)
        desenhar_texto(self.image, "$", 12, AMARELO, 10, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angulo = random.uniform(0, 360)

    def update(self):
        self.angulo += 3
        if self.angulo >= 360:
            self.angulo = 0

# ── Flag (objetivo final) ─────────────────────────────────────────────
class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.image, CINZA,  (12, 0, 4, 60))
        pygame.draw.polygon(self.image, VERDE, [(16, 4), (30, 14), (16, 24)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# ── Jogador ───────────────────────────────────────────────────────────
class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.largura  = 32
        self.altura   = 44
        self._desenhar()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x     = 0
        self.vel_y     = 0
        self.no_chao   = False
        self.vidas     = 3
        self.moedas    = 0
        self.invencivel = 0   # frames de invencibilidade após dano
        self.piscando  = False

    def _desenhar(self):
        self.image = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        # Corpo
        pygame.draw.rect(self.image, AZUL,     (6, 16, 20, 22), border_radius=4)
        # Cabeça
        pygame.draw.ellipse(self.image, (255, 200, 150), (6, 2, 20, 20))
        # Olhos
        pygame.draw.circle(self.image, PRETO, (12, 10), 3)
        pygame.draw.circle(self.image, PRETO, (20, 10), 3)
        pygame.draw.circle(self.image, BRANCO, (13, 9), 1)
        pygame.draw.circle(self.image, BRANCO, (21, 9), 1)
        # Pernas
        pygame.draw.rect(self.image, AZUL_ESC, (8,  36, 7, 8), border_radius=2)
        pygame.draw.rect(self.image, AZUL_ESC, (17, 36, 7, 8), border_radius=2)

    def update(self, plataformas):
        # Gravidade
        self.vel_y += 0.6
        if self.vel_y > 14:
            self.vel_y = 14

        # Movimento horizontal
        self.rect.x += self.vel_x
        self._colisao_horizontal(plataformas)

        # Movimento vertical
        self.rect.y += int(self.vel_y)
        self.no_chao = False
        self._colisao_vertical(plataformas)

        # Invencibilidade
        if self.invencivel > 0:
            self.invencivel -= 1
            self.piscando = (self.invencivel // 5) % 2 == 0
        else:
            self.piscando = False

    def _colisao_horizontal(self, plataformas):
        hits = pygame.sprite.spritecollide(self, plataformas, False)
        for hit in hits:
            if self.vel_x > 0:
                self.rect.right = hit.rect.left
            elif self.vel_x < 0:
                self.rect.left = hit.rect.right

    def _colisao_vertical(self, plataformas):
        hits = pygame.sprite.spritecollide(self, plataformas, False)
        for hit in hits:
            if self.vel_y > 0:
                self.rect.bottom = hit.rect.top
                self.no_chao = True
            elif self.vel_y < 0:
                self.rect.top = hit.rect.bottom
            self.vel_y = 0

    def pular(self):
        if self.no_chao:
            self.vel_y = -13

    def tomar_dano(self):
        if self.invencivel == 0:
            self.vidas -= 1
            self.invencivel = 80

    def draw(self, surf):
        if not self.piscando:
            surf.blit(self.image, self.rect)

# ── Inimigo patrulheiro ───────────────────────────────────────────────
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__()
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        self._desenhar()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel = 2
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir

    def _desenhar(self):
        pygame.draw.ellipse(self.image, VERMELHO,  (2, 2, 24, 24))
        pygame.draw.circle(self.image, PRETO, (9,  11), 4)
        pygame.draw.circle(self.image, PRETO, (19, 11), 4)
        pygame.draw.circle(self.image, BRANCO, (10, 10), 2)
        pygame.draw.circle(self.image, BRANCO, (20, 10), 2)
        pygame.draw.arc(self.image, PRETO, (6, 16, 16, 8), 3.14, 0, 2)

    def update(self):
        self.rect.x += self.vel
        if self.rect.right >= self.limite_dir or self.rect.left <= self.limite_esq:
            self.vel *= -1

# ── Câmera (scroll horizontal) ────────────────────────────────────────
class Camera:
    def __init__(self, largura_mundo):
        self.offset_x = 0
        self.largura_mundo = largura_mundo

    def aplicar(self, rect):
        return pygame.Rect(rect.x - self.offset_x, rect.y, rect.width, rect.height)

    def atualizar(self, jogador):
        alvo = jogador.rect.centerx - LARGURA // 2
        self.offset_x += (alvo - self.offset_x) * 0.1
        self.offset_x = max(0, min(self.offset_x, self.largura_mundo - LARGURA))

# ── Fundo com parallax ────────────────────────────────────────────────
def desenhar_fundo(surf, camera_offset):
    # Céu gradiente
    for i in range(ALTURA):
        t = i / ALTURA
        r = int(15  + t * 10)
        g = int(30  + t * 20)
        b = int(80  + t * 60)
        pygame.draw.line(surf, (r, g, b), (0, i), (LARGURA, i))

    # Nuvens (parallax lento)
    nuvens = [(100, 60), (280, 40), (450, 80), (620, 50), (780, 70),
              (950, 45), (1100, 65), (1300, 55)]
    for nx, ny in nuvens:
        cx = int((nx - camera_offset * 0.2) % (LARGURA + 200)) - 100
        pygame.draw.ellipse(surf, (200, 220, 255), (cx, ny, 90, 35))
        pygame.draw.ellipse(surf, (220, 235, 255), (cx+20, ny-15, 60, 30))

# ── Nível ─────────────────────────────────────────────────────────────
def criar_nivel():
    plataformas = pygame.sprite.Group()
    espinhos    = pygame.sprite.Group()
    moedas      = pygame.sprite.Group()
    inimigos    = pygame.sprite.Group()
    flags       = pygame.sprite.Group()

    # Chão principal (com buracos)
    segmentos_chao = [
        (0,   420, 350),
        (420, 420, 200),
        (680, 420, 300),
        (1040,420, 250),
        (1350,420, 400),
        (1820,420, 300),
    ]
    for x, y, larg in segmentos_chao:
        plataformas.add(Plataforma(x, y, larg))

    # Plataformas flutuantes
    plats = [
        (120, 320, 120), (300, 260, 100), (480, 300, 130),
        (660, 240, 100), (780, 180, 120), (920, 280, 100),
        (1050,200, 130), (1200,280, 100), (1330,150, 120),
        (1500,260, 130), (1650,200, 100), (1750,320, 120),
        (1900,260, 100), (2000,180, 130),
    ]
    for x, y, larg in plats:
        plataformas.add(Plataforma(x, y, larg, cor=AZUL_ESC))

    # Espinhos
    pos_espinhos = [
        370, 390, 640, 660, 1010, 1030, 1320, 1340, 1800,
    ]
    for x in pos_espinhos:
        espinhos.add(Espinho(x, 396))

    # Moedas
    pos_moedas = [
        (140,295),(200,295),(260,295),
        (480,270),(550,270),
        (790,150),(850,150),
        (1060,170),(1120,170),
        (1510,230),(1570,230),(1660,170),
        (1910,230),(1970,230),
    ]
    for x, y in pos_moedas:
        moedas.add(Moeda(x, y))

    # Inimigos
    inimigos_cfg = [
        (300, 392, 150, 420),
        (700, 392, 680, 790),
        (920, 250, 920,1020),
        (1200,250,1200,1330),
        (1660,170,1650,1750),
        (1910,230,1900,2000),
    ]
    for x, y, ei, ed in inimigos_cfg:
        inimigos.add(Inimigo(x, y, ei, ed))

    # Flag final
    flags.add(Flag(2050, 120))

    return plataformas, espinhos, moedas, inimigos, flags

LARGURA_MUNDO = 2200

# ── Jogo principal ────────────────────────────────────────────────────
def rodar_jogo(tela, clock):
    jogador = Jogador(60, 370)
    jogador_grupo = pygame.sprite.GroupSingle(jogador)

    plataformas, espinhos, moedas, inimigos, flags = criar_nivel()
    total_moedas = len(moedas)

    camera = Camera(LARGURA_MUNDO)

    while True:
        clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    jogador.pular()
                if evento.key == pygame.K_ESCAPE:
                    return MENU, jogador.moedas, total_moedas

        # Input contínuo
        teclas = pygame.key.get_pressed()
        jogador.vel_x = 0
        if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: jogador.vel_x = -5
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: jogador.vel_x =  5

        # Atualizar
        jogador.update(plataformas)
        inimigos.update()
        moedas.update()
        camera.atualizar(jogador)

        # Colisão moedas
        coletadas = pygame.sprite.spritecollide(jogador, moedas, True)
        jogador.moedas += len(coletadas)

        # Colisão inimigos
        if pygame.sprite.spritecollide(jogador, inimigos, False):
            jogador.tomar_dano()

        # Colisão espinhos
        if pygame.sprite.spritecollide(jogador, espinhos, False):
            jogador.tomar_dano()

        # Caiu no buraco
        if jogador.rect.top > ALTURA + 50:
            jogador.tomar_dano()
            jogador.rect.x = 60
            jogador.rect.y = 370
            jogador.vel_y = 0

        # Verificar vitória
        if pygame.sprite.spritecollide(jogador, flags, False):
            return VITORIA, jogador.moedas, total_moedas

        # Verificar derrota
        if jogador.vidas <= 0:
            return DERROTA, jogador.moedas, total_moedas

        # ── Desenhar ──────────────────────────────────────────────────
        desenhar_fundo(tela, camera.offset_x)

        # Plataformas
        for p in plataformas:
            tela.blit(p.image, camera.aplicar(p.rect))
        # Espinhos
        for e in espinhos:
            tela.blit(e.image, camera.aplicar(e.rect))
        # Moedas
        for m in moedas:
            tela.blit(m.image, camera.aplicar(m.rect))
        # Inimigos
        for i in inimigos:
            tela.blit(i.image, camera.aplicar(i.rect))
        # Flag
        for f in flags:
            tela.blit(f.image, camera.aplicar(f.rect))
        # Jogador
        jogador.draw(tela)

        # HUD
        _desenhar_hud(tela, jogador, total_moedas)

        pygame.display.flip()

def _desenhar_hud(tela, jogador, total_moedas):
    # Fundo HUD
    pygame.draw.rect(tela, AZUL_ESC, (0, 0, LARGURA, 40))
    pygame.draw.line(tela, AZUL, (0, 40), (LARGURA, 40), 2)

    # Vidas
    desenhar_texto(tela, "VIDAS:", 18, BRANCO, 10, 10, centralizar=False)
    for i in range(3):
        cor = VERMELHO if i < jogador.vidas else CINZA
        pygame.draw.circle(tela, cor, (100 + i * 28, 20), 10)

    # Moedas
    desenhar_texto(tela, f"MOEDAS: {jogador.moedas}/{total_moedas}", 18, AMARELO, 300, 10, centralizar=False)

    # Dica
    desenhar_texto(tela, "← → A D: Mover  |  SPACE/W/↑: Pular  |  ESC: Menu", 14, AZUL_CLA, LARGURA//2, 13)

# ── Tela de Menu ──────────────────────────────────────────────────────
def tela_menu(tela, clock):
    angulo = 0
    while True:
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return JOGANDO
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # Fundo
        for i in range(ALTURA):
            t = i / ALTURA
            r = int(5  + t * 15)
            g = int(10 + t * 30)
            b = int(40 + t * 80)
            pygame.draw.line(tela, (r, g, b), (0, i), (LARGURA, i))

        # Nuvens decorativas
        for nx, ny in [(100,80),(300,60),(550,90),(700,50)]:
            pygame.draw.ellipse(tela, (40,60,120), (nx, ny, 120, 45))
            pygame.draw.ellipse(tela, (50,70,140), (nx+25, ny-18, 80, 38))

        # Título
        desenhar_texto_sombra(tela, "CONECTA", 90, AMARELO, LARGURA//2, 80)
        desenhar_texto_sombra(tela, "RUN",     90, AZUL_CLA, LARGURA//2, 165)

        # Linha decorativa
        pygame.draw.line(tela, AZUL, (200, 270), (600, 270), 2)

        # Controles
        desenhar_texto(tela, "CONTROLES", 22, AMARELO, LARGURA//2, 290)
        controles = [
            ("← / A", "Mover para esquerda"),
            ("→ / D", "Mover para direita"),
            ("SPACE / W / ↑", "Pular"),
            ("ESC", "Voltar ao menu"),
        ]
        for idx, (tecla, desc) in enumerate(controles):
            y = 322 + idx * 28
            pygame.draw.rect(tela, AZUL_ESC, (180, y-2, 440, 24), border_radius=4)
            desenhar_texto(tela, f"{tecla}  —  {desc}", 17, BRANCO, LARGURA//2, y)

        # Objetivo
        pygame.draw.rect(tela, (20, 50, 100), (160, 440, 480, 30), border_radius=6)
        desenhar_texto(tela, "Objetivo: coletar moedas e chegar à bandeira verde!", 16, VERDE, LARGURA//2, 447)

        # Botão iniciar (piscante)
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            desenhar_texto_sombra(tela, "► PRESSIONE ENTER ou SPACE para jogar ◄", 20, AMARELO, LARGURA//2, 488)

        angulo += 1
        pygame.display.flip()

# ── Tela de Vitória ───────────────────────────────────────────────────
def tela_vitoria(tela, clock, moedas, total):
    timer = 0
    while True:
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return MENU

        for i in range(ALTURA):
            t = i / ALTURA
            pygame.draw.line(tela, (int(t*20), int(50+t*80), int(t*20)), (0,i),(LARGURA,i))

        # Fogos simples
        timer += 1
        for _ in range(6):
            if timer % 10 == 0:
                pass
            cx = random.randint(100, LARGURA-100)
            cy = random.randint(50, 200)
            pygame.draw.circle(tela, random.choice([AMARELO, VERDE, AZUL_CLA, BRANCO]),
                               (cx, cy), random.randint(2, 6))

        desenhar_texto_sombra(tela, "🏆 VOCÊ VENCEU!", 64, AMARELO, LARGURA//2, 120)
        desenhar_texto(tela, f"Moedas coletadas: {moedas} / {total}", 28, BRANCO, LARGURA//2, 220)

        estrelas = min(3, 1 + (moedas >= total//2) + (moedas == total))
        desenhar_texto(tela, "⭐" * estrelas + "☆" * (3-estrelas), 48, AMARELO, LARGURA//2, 270)

        if moedas == total:
            desenhar_texto(tela, "PERFEITO! Todas as moedas coletadas!", 22, VERDE, LARGURA//2, 340)

        if (pygame.time.get_ticks() // 600) % 2 == 0:
            desenhar_texto(tela, "ENTER / SPACE — Voltar ao Menu", 20, BRANCO, LARGURA//2, 420)

        pygame.display.flip()

# ── Tela de Derrota ───────────────────────────────────────────────────
def tela_derrota(tela, clock, moedas, total):
    while True:
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return MENU

        for i in range(ALTURA):
            t = i / ALTURA
            pygame.draw.line(tela, (int(30+t*20), 0, 0), (0,i),(LARGURA,i))

        desenhar_texto_sombra(tela, "💀 GAME OVER", 64, VERMELHO, LARGURA//2, 120)
        desenhar_texto(tela, f"Moedas coletadas: {moedas} / {total}", 28, BRANCO, LARGURA//2, 230)
        desenhar_texto(tela, "Você perdeu todas as vidas!", 24, AMARELO, LARGURA//2, 280)
        desenhar_texto(tela, "Dica: pule em cima dos inimigos para desviar!", 18, AZUL_CLA, LARGURA//2, 330)

        if (pygame.time.get_ticks() // 600) % 2 == 0:
            desenhar_texto(tela, "ENTER / SPACE — Tentar novamente", 20, BRANCO, LARGURA//2, 420)

        pygame.display.flip()

# ── Main Loop ─────────────────────────────────────────────────────────
def main():
    pygame.init()
    tela  = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)
    clock = pygame.time.Clock()

    estado = MENU
    moedas_finais = 0
    total_moedas  = 0

    while True:
        if estado == MENU:
            estado = tela_menu(tela, clock)

        elif estado == JOGANDO:
            resultado, moedas_finais, total_moedas = rodar_jogo(tela, clock)
            estado = resultado

        elif estado == VITORIA:
            estado = tela_vitoria(tela, clock, moedas_finais, total_moedas)

        elif estado == DERROTA:
            estado = tela_derrota(tela, clock, moedas_finais, total_moedas)

if __name__ == "__main__":
    main()