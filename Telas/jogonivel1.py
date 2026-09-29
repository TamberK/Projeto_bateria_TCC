import pygame
import serial
import random
import sys
import math

# ===== SERIAL =====
arduino = None
try:
    arduino = serial.Serial("COM3", 9600)
    arduino.timeout = 0.01
except:
    print("Arduino não conectado")

# ===== PYGAME =====
pygame.init()

LARGURA = 700
ALTURA = 600

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bateria Educacional - Nível 1")

clock = pygame.time.Clock()

# ===== FONTES =====
fonte = pygame.font.SysFont("arial", 36)
fonte_grande = pygame.font.SysFont("arial", 56, bold=True)
fonte_titulo = pygame.font.SysFont("arial", 38, bold=True)
fonte_combo = pygame.font.SysFont("arial", 50, bold=True)
fonte_media = pygame.font.SysFont("arial", 24, bold=True)
fonte_sub = pygame.font.SysFont("arial", 20, bold=True)

# ===== CORES =====
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 170, 255)
AZUL_CLARO = (80, 180, 255)
VERDE = (0, 255, 120)
VERMELHO = (255, 70, 70)
AMARELO = (255, 220, 0)
CINZA = (35, 35, 50)

# ===== EFEITO DE FUNDO PADRONIZADO (MENU E DIFICULDADE) =====
def fundo():
    for y in range(ALTURA):
        cor = (5, 5 + y // 20, 15 + y // 18)
        pygame.draw.line(tela, cor, (0, y), (LARGURA, y))

# ===== TEXTO ESTILIZADO (SOMBRA E BORDA) =====
def texto_estilizado(txt, fonte_ref, cor, borda, sombra, x, y):
    render = fonte_ref.render(txt, True, cor)
    borda_render = fonte_ref.render(txt, True, borda)
    sombra_render = fonte_ref.render(txt, True, sombra)

    tela.blit(sombra_render, (x + 4, y + 4))
    tela.blit(borda_render, (x + 2, y + 2))
    tela.blit(render, (x, y))

# ===== POSIÇÕES DO JOGO =====
COLUNA_K = 220
COLUNA_B = 420

LARGURA_NOTA = 50
ALTURA_NOTA = 20

LINHA_ACERTO = 450

# ===== ESTADO DO JOGO =====
estado = "menu"

# ===== VARIÁVEIS =====
notas = []
pontuacao = 0
combo = 0
vidas = 3
velocidade = 5

texto_feedback = ""
tempo_feedback = 0

pad_k_anim = 0
pad_b_anim = 0

dificuldade = 1

# FILA DE INPUTS
fila_toques = []

# MAPA DE TECLAS (MANTIDO)
MAPA_TECLAS = {
    pygame.K_k: "K",  # Bumbo (Kick)
    pygame.K_s: "B"   # Caixa (Snare)
}

# ===== PARTÍCULAS DO JOGO =====
particulas = []
for i in range(40):
    particulas.append([
        random.randint(0, LARGURA),
        random.randint(0, ALTURA),
        random.randint(1, 3)
    ])

# ===== REINICIAR =====
def reiniciar_jogo():
    global notas, pontuacao, combo, vidas, velocidade, fila_toques

    notas = []
    pontuacao = 0
    combo = 0
    vidas = 3
    velocidade = 5
    fila_toques = []

# ===== CRIAR NOTA =====
def criar_nota():
    tipo = random.choice(["K", "B"])
    x = COLUNA_K if tipo == "K" else COLUNA_B

    notas.append({
        "tipo": tipo,
        "x": x,
        "y": -ALTURA_NOTA,
        "estado": "normal",
        "tempo_erro": 15
    })

# ===== MENU INICIAL DO NÍVEL 1 =====
def tela_menu():
    global estado
    tempo = 0

    while estado == "menu":
        clock.tick(60)
        tempo += 0.05
        fundo()

        # BARRA SUPERIOR
        barra = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
        barra.fill((15, 15, 25, 220))
        tela.blit(barra, (0, 0))
        pygame.draw.line(tela, (60, 60, 90), (0, 80), (LARGURA, 80), 2)

        # TÍTULO CENTRAL ANIMADO
        deslocamento_y = int(math.sin(tempo) * 6)
        sub_nivel = "NÍVEL 1: BATERIA HERO"
        largura_s = fonte_titulo.size(sub_nivel)[0]
        texto_estilizado(sub_nivel, fonte_titulo, AMARELO, PRETO, BRANCO, (LARGURA - largura_s) // 2, 20 + deslocamento_y)

        # SUBTÍTULO / OBJETIVO PEDAGÓGICO
        obj_txt = "Objetivo: Aprender os primeiros ritmos da bateria"
        largura_o = fonte_sub.size(obj_txt)[0]
        texto_estilizado(obj_txt, fonte_sub, AZUL_CLARO, PRETO, PRETO, (LARGURA - largura_o) // 2, 105)

        # PAINEL DE CONTROLES
        x_box = (LARGURA - 460) // 2
        pygame.draw.rect(tela, (20, 20, 35), (x_box, 150, 460, 130), border_radius=15)
        pygame.draw.rect(tela, AZUL, (x_box, 150, 460, 130), 2, border_radius=15)

        texto_estilizado("CONTROLES DO TECLADO", fonte_media, AZUL, PRETO, PRETO, x_box + 105, 162)
        texto_estilizado("• BUMBO   ->   Tecla K", fonte_media, BRANCO, PRETO, PRETO, x_box + 100, 205)
        texto_estilizado("• CAIXA   ->   Tecla S", fonte_media, BRANCO, PRETO, PRETO, x_box + 100, 240)

        # BOTÕES / OPÇÕES DO MENU
        # ENTER - INICIAR
        pygame.draw.rect(tela, (20, 25, 35), (x_box, 305, 460, 50), border_radius=12)
        pygame.draw.rect(tela, (50, 180, 90), (x_box, 305, 460, 50), 2, border_radius=12)
        txt_enter = "ENTER - Iniciar Jogo"
        largura_e = fonte_media.size(txt_enter)[0]
        texto_estilizado(txt_enter, fonte_media, VERDE, PRETO, PRETO, (LARGURA - largura_e) // 2, 317)

        # D - DIFICULDADE
        pygame.draw.rect(tela, (20, 20, 35), (x_box, 370, 460, 50), border_radius=12)
        pygame.draw.rect(tela, (60, 60, 90), (x_box, 370, 460, 50), 2, border_radius=12)
        txt_dif = "D - Escolher Dificuldade"
        largura_d = fonte_media.size(txt_dif)[0]
        texto_estilizado(txt_dif, fonte_media, AMARELO, PRETO, PRETO, (LARGURA - largura_d) // 2, 382)

        # ESC - SAIR
        pygame.draw.rect(tela, (25, 20, 25), (x_box, 435, 460, 50), border_radius=12)
        pygame.draw.rect(tela, (180, 60, 60), (x_box, 435, 460, 50), 2, border_radius=12)
        txt_sair = "ESC - Sair"
        largura_sair = fonte_media.size(txt_sair)[0]
        texto_estilizado(txt_sair, fonte_media, VERMELHO, PRETO, PRETO, (LARGURA - largura_sair) // 2, 447)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    reiniciar_jogo()
                    estado = "jogo"
                if evento.key == pygame.K_d:
                    estado = "dificuldade"
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# ===== TELA DE SELEÇÃO DE DIFICULDADE =====
def tela_dificuldade():
    global estado, dificuldade
    tempo = 0

    while estado == "dificuldade":
        clock.tick(60)
        tempo += 0.05
        fundo()

        # BARRA SUPERIOR
        barra = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
        barra.fill((15, 15, 25, 220))
        tela.blit(barra, (0, 0))
        pygame.draw.line(tela, (60, 60, 90), (0, 80), (LARGURA, 80), 2)

        # TÍTULO ANIMADO
        deslocamento_y = int(math.sin(tempo) * 6)
        titulo = "SELEÇÃO DE DIFICULDADE"
        largura_t = fonte_titulo.size(titulo)[0]
        texto_estilizado(titulo, fonte_titulo, AZUL, PRETO, BRANCO, (LARGURA - largura_t) // 2, 20 + deslocamento_y)

        x_box = (LARGURA - 460) // 2

        # FÁCIL
        cor_f = VERDE if dificuldade == 1 else BRANCO
        pygame.draw.rect(tela, (20, 35, 25) if dificuldade == 1 else (20, 20, 35), (x_box, 140, 460, 60), border_radius=12)
        pygame.draw.rect(tela, VERDE if dificuldade == 1 else (60, 60, 90), (x_box, 140, 460, 60), 2, border_radius=12)
        texto_estilizado("1 - Fácil (Velocidade Lenta)", fonte_media, cor_f, PRETO, PRETO, x_box + 40, 156)

        # MÉDIO
        cor_m = AMARELO if dificuldade == 2 else BRANCO
        pygame.draw.rect(tela, (35, 35, 20) if dificuldade == 2 else (20, 20, 35), (x_box, 220, 460, 60), border_radius=12)
        pygame.draw.rect(tela, AMARELO if dificuldade == 2 else (60, 60, 90), (x_box, 220, 460, 60), 2, border_radius=12)
        texto_estilizado("2 - Médio (Velocidade Normal)", fonte_media, cor_m, PRETO, PRETO, x_box + 40, 236)

        # DIFÍCIL
        cor_d = VERMELHO if dificuldade == 3 else BRANCO
        pygame.draw.rect(tela, (40, 20, 20) if dificuldade == 3 else (20, 20, 35), (x_box, 300, 460, 60), border_radius=12)
        pygame.draw.rect(tela, VERMELHO if dificuldade == 3 else (60, 60, 90), (x_box, 300, 460, 60), 2, border_radius=12)
        texto_estilizado("3 - Difícil (Velocidade Rápida)", fonte_media, cor_d, PRETO, PRETO, x_box + 40, 316)

        # INSTRUÇÃO / VOLTAR
        txt_info = "Pressione 1, 2 ou 3 para selecionar a dificuldade"
        largura_i = fonte_sub.size(txt_info)[0]
        texto_estilizado(txt_info, fonte_sub, AZUL_CLARO, PRETO, PRETO, (LARGURA - largura_i) // 2, 400)

        txt_esc = "ESC - Voltar ao Menu"
        largura_esc = fonte_sub.size(txt_esc)[0]
        texto_estilizado(txt_esc, fonte_sub, BRANCO, PRETO, PRETO, (LARGURA - largura_esc) // 2, 440)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    dificuldade = 1
                    reiniciar_jogo()
                    estado = "jogo"

                if evento.key == pygame.K_2:
                    dificuldade = 2
                    reiniciar_jogo()
                    estado = "jogo"

                if evento.key == pygame.K_3:
                    dificuldade = 3
                    reiniciar_jogo()
                    estado = "jogo"

                if evento.key == pygame.K_ESCAPE:
                    estado = "menu"

# ===== LOOP PRINCIPAL =====
rodando = True
contador = 0

while rodando:

    clock.tick(60)

    if estado == "menu":
        tela_menu()

    if estado == "dificuldade":
        tela_dificuldade()

    if estado == "jogo":

        if dificuldade == 1:
            spawn = 55
        elif dificuldade == 2:
            spawn = 40
        else:
            spawn = 25

        # FUNDO AZUL ANIMADO DO JOGO (PRESERVADO INTACTO)
        for y in range(ALTURA):
            cor = (5, 5 + y // 5, 25 + y // 4)
            pygame.draw.line(tela, cor, (0, y), (LARGURA, y))

        # PARTÍCULAS DO JOGO (PRESERVADAS INTACTAS)
        for p in particulas:
            pygame.draw.circle(tela, (40, 80, 150), (p[0], p[1]), p[2])
            p[1] += 1
            if p[1] > ALTURA:
                p[0] = random.randint(0, LARGURA)
                p[1] = 0

        # EVENTOS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key in MAPA_TECLAS:
                    fila_toques.append(MAPA_TECLAS[evento.key])

        # ARDUINO
        if arduino and arduino.in_waiting > 0:
            fila_toques.append(arduino.readline().decode().strip())

        # USAR FILA
        toque = fila_toques.pop(0) if fila_toques else None

        # ===== COLUNAS =====
        pygame.draw.rect(tela, CINZA, (COLUNA_K - 25, 0, 100, ALTURA))
        pygame.draw.rect(tela, AZUL, (COLUNA_K - 25, 0, 100, ALTURA), 3)

        pygame.draw.rect(tela, CINZA, (COLUNA_B - 25, 0, 100, ALTURA))
        pygame.draw.rect(tela, AZUL, (COLUNA_B - 25, 0, 100, ALTURA), 3)

        # ===== CRIAR NOTAS =====
        contador += 1
        if contador >= spawn:
            criar_nota()
            contador = 0

        # ===== LINHA DE ACERTO =====
        pygame.draw.line(tela, (30, 100, 255), (0, LINHA_ACERTO), (LARGURA, LINHA_ACERTO), 10)
        pygame.draw.line(tela, AZUL_CLARO, (0, LINHA_ACERTO), (LARGURA, LINHA_ACERTO), 4)

        # ===== NOTAS =====
        for nota in notas[:]:

            if nota["estado"] == "normal":

                nota["y"] += velocidade

                if toque == nota["tipo"]:

                    distancia = abs(nota["y"] - LINHA_ACERTO)

                    if distancia < 10:
                        pontuacao += 20 + combo
                        combo += 1
                        texto_feedback = "PERFECT"

                    elif distancia < 25:
                        pontuacao += 10 + combo
                        combo += 1
                        texto_feedback = "GOOD"

                    elif distancia < 40:
                        pontuacao += 5
                        combo = 0
                        texto_feedback = "OK"

                    else:
                        texto_feedback = ""

                    if distancia < 40:

                        tempo_feedback = 30

                        if nota["tipo"] == "K":
                            pad_k_anim = 10
                        else:
                            pad_b_anim = 10

                        notas.remove(nota)
                        continue

                if nota["y"] > LINHA_ACERTO + 40:

                    nota["estado"] = "erro"

                    pontuacao = max(0, pontuacao - 5)
                    combo = 0
                    vidas -= 1

            else:

                nota["tempo_erro"] -= 1

                if nota["tempo_erro"] <= 0:
                    notas.remove(nota)
                    continue

            cor = AZUL_CLARO if nota["estado"] == "normal" else VERMELHO

            pygame.draw.rect(tela, cor, (nota["x"], nota["y"], LARGURA_NOTA, ALTURA_NOTA), border_radius=6)

        # FEEDBACK
        if tempo_feedback > 0:
            txt = fonte_combo.render(texto_feedback, True, BRANCO)
            tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 200))
            tempo_feedback -= 1

        velocidade = 5 + pontuacao * 0.01

        # ===== PADS =====
        raio_k = 30 + pad_k_anim
        raio_b = 30 + pad_b_anim

        pygame.draw.circle(tela, AZUL, (COLUNA_K + 25, LINHA_ACERTO + 70), raio_k)
        pygame.draw.circle(tela, PRETO, (COLUNA_K + 25, LINHA_ACERTO + 70), raio_k - 6)

        pygame.draw.circle(tela, AZUL, (COLUNA_B + 25, LINHA_ACERTO + 70), raio_b)
        pygame.draw.circle(tela, PRETO, (COLUNA_B + 25, LINHA_ACERTO + 70), raio_b - 6)

        if pad_k_anim > 0:
            pad_k_anim -= 1

        if pad_b_anim > 0:
            pad_b_anim -= 1

        # TRADUÇÃO VISUAL DOS INSTRUMENTOS
        tela.blit(fonte.render("BUMBO", True, BRANCO), (COLUNA_K - 15, LINHA_ACERTO + 110))
        tela.blit(fonte.render("CAIXA", True, BRANCO), (COLUNA_B - 10, LINHA_ACERTO + 110))

        # ===== HUD =====
        pygame.draw.rect(tela, (15, 15, 30), (0, 0, LARGURA, 80))

        tela.blit(fonte.render(f"Pontos: {pontuacao}", True, BRANCO), (30, 20))

        for i in range(vidas):
            pygame.draw.circle(tela, VERMELHO, (40 + i * 30, 100), 10)

        pygame.display.flip()

        if vidas <= 0:
            estado = "gameover"

    if estado == "gameover":

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_r:
                    reiniciar_jogo()
                    estado = "jogo"

                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        tela.fill((15, 15, 30))

        titulo = fonte_grande.render("GAME OVER", True, VERMELHO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 180))

        score = fonte.render(f"Pontuação final: {pontuacao}", True, BRANCO)
        tela.blit(score, (LARGURA // 2 - score.get_width() // 2, 260))

        texto_r = fonte.render("R - Jogar novamente", True, BRANCO)
        tela.blit(texto_r, (LARGURA // 2 - texto_r.get_width() // 2, 350))

        texto_esc = fonte.render("ESC - Sair", True, BRANCO)
        tela.blit(texto_esc, (LARGURA // 2 - texto_esc.get_width() // 2, 400))

        pygame.display.flip()

pygame.quit()