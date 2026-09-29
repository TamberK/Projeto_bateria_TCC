import pygame
import serial
import random

# ===== SERIAL =====
arduino = None
try:
    arduino = serial.Serial("COM3",9600)
    arduino.timeout = 0.01
except:
    print("Arduino não conectado")

# ===== PYGAME =====
pygame.init()

LARGURA = 700
ALTURA = 600

tela = pygame.display.set_mode((LARGURA,ALTURA))
pygame.display.set_caption("Bateria Educacional")

clock = pygame.time.Clock()

fonte = pygame.font.SysFont("arial",36)
fonte_grande = pygame.font.SysFont("arial",70)
fonte_combo = pygame.font.SysFont("arial",50)

# ===== CORES =====
BRANCO = (255,255,255)
PRETO = (10,10,18)
AZUL = (0,140,255)
AZUL_CLARO = (80,180,255)
VERDE = (0,220,120)
VERMELHO = (220,60,60)
CINZA = (35,35,50)

# ===== POSIÇÕES =====
COLUNA_K = 220
COLUNA_B = 420

LARGURA_NOTA = 50
ALTURA_NOTA = 20

LINHA_ACERTO = 450

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

# ===== REINICIAR =====
def reiniciar_jogo():
    global notas,pontuacao,combo,vidas,velocidade

    notas = []
    pontuacao = 0
    combo = 0
    vidas = 3
    velocidade = 5

# ===== CRIAR NOTA =====
def criar_nota():

    tipo = random.choice(["K","B"])

    if tipo == "K":
        x = COLUNA_K
    else:
        x = COLUNA_B

    notas.append({
        "tipo":tipo,
        "x":x,
        "y":-ALTURA_NOTA,
        "estado":"normal",
        "tempo_erro":15
    })

# ===== LOOP =====
rodando = True
contador = 0

while rodando:

    clock.tick(60)

    # ===== FUNDO GRADIENTE =====
    for y in range(ALTURA):
        cor = (5,5+y//5,25+y//4)
        pygame.draw.line(tela,cor,(0,y),(LARGURA,y))

    # ===== EVENTOS =====
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # ===== COLUNAS =====
    pygame.draw.rect(tela,CINZA,(COLUNA_K-25,0,100,ALTURA))
    pygame.draw.rect(tela,AZUL,(COLUNA_K-25,0,100,ALTURA),2)

    pygame.draw.rect(tela,CINZA,(COLUNA_B-25,0,100,ALTURA))
    pygame.draw.rect(tela,AZUL,(COLUNA_B-25,0,100,ALTURA),2)

    # ===== CRIAR NOTAS =====
    contador += 1
    if contador >= 45:
        criar_nota()
        contador = 0

    # ===== LER ARDUINO =====
    toque = None

    if arduino and arduino.in_waiting > 0:
        toque = arduino.readline().decode().strip()

    # ===== LINHA DE ACERTO COM GLOW =====
    pygame.draw.line(tela,(30,100,255),(0,LINHA_ACERTO),(LARGURA,LINHA_ACERTO),8)
    pygame.draw.line(tela,AZUL_CLARO,(0,LINHA_ACERTO),(LARGURA,LINHA_ACERTO),3)

    # ===== ATUALIZAR NOTAS =====
    for nota in notas[:]:

        if nota["estado"] == "normal":

            nota["y"] += velocidade

            if toque == nota["tipo"]:

                distancia = abs(nota["y"]-LINHA_ACERTO)

                if distancia < 10:
                    pontuacao += 20+combo
                    combo += 1
                    texto_feedback = "PERFECT"

                elif distancia < 25:
                    pontuacao += 10+combo
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

                pontuacao = max(0,pontuacao-5)
                combo = 0
                vidas -= 1

        else:

            nota["tempo_erro"] -= 1

            if nota["tempo_erro"] <= 0:
                notas.remove(nota)
                continue

        if nota["estado"] == "erro":
            cor = VERMELHO
        else:
            cor = AZUL_CLARO

        # ===== BRILHO =====
        pygame.draw.rect(
            tela,
            (20,20,20),
            (nota["x"]-4,nota["y"]-4,LARGURA_NOTA+8,ALTURA_NOTA+8),
            border_radius=8
        )

        # ===== NOTA =====
        pygame.draw.rect(
            tela,
            cor,
            (nota["x"],nota["y"],LARGURA_NOTA,ALTURA_NOTA),
            border_radius=6
        )

        pygame.draw.rect(
            tela,
            BRANCO,
            (nota["x"],nota["y"],LARGURA_NOTA,ALTURA_NOTA),
            2,
            border_radius=6
        )

    # ===== VELOCIDADE =====
    velocidade = 5 + pontuacao*0.01

    # ===== PADS ANIMADOS =====
    raio_k = 30 + pad_k_anim
    raio_b = 30 + pad_b_anim

    pygame.draw.circle(tela,AZUL,(COLUNA_K+25,LINHA_ACERTO+70),raio_k)
    pygame.draw.circle(tela,PRETO,(COLUNA_K+25,LINHA_ACERTO+70),raio_k-5)

    pygame.draw.circle(tela,AZUL,(COLUNA_B+25,LINHA_ACERTO+70),raio_b)
    pygame.draw.circle(tela,PRETO,(COLUNA_B+25,LINHA_ACERTO+70),raio_b-5)

    if pad_k_anim > 0:
        pad_k_anim -= 1

    if pad_b_anim > 0:
        pad_b_anim -= 1

    tela.blit(fonte.render("KICK",True,BRANCO),(COLUNA_K-10,LINHA_ACERTO+110))
    tela.blit(fonte.render("SNARE",True,BRANCO),(COLUNA_B-10,LINHA_ACERTO+110))

    # ===== FEEDBACK =====
    if tempo_feedback > 0:

        feedback = fonte_grande.render(texto_feedback,True,VERDE)

        tela.blit(
            feedback,
            (LARGURA//2 - feedback.get_width()//2,200)
        )

        tempo_feedback -= 1

    # ===== COMBO GRANDE =====
    if combo >= 5:

        combo_txt = fonte_combo.render(f"COMBO x{combo}",True,AZUL_CLARO)

        tela.blit(
            combo_txt,
            (LARGURA//2 - combo_txt.get_width()//2,120)
        )

    # ===== HUD =====
    pygame.draw.rect(tela,(15,15,30),(0,0,LARGURA,80))

    tela.blit(fonte.render(f"Pontos: {pontuacao}",True,BRANCO),(30,20))

    # ===== VIDAS =====
    for i in range(vidas):
        pygame.draw.circle(tela,VERMELHO,(40+i*30,100),10)

    # ===== GAME OVER =====
    if vidas <= 0:

        game_over = True

        while game_over:

            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    game_over = False
                    rodando = False

                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_r:
                        reiniciar_jogo()
                        game_over = False

                    if evento.key == pygame.K_ESCAPE:
                        game_over = False
                        rodando = False

            tela.fill((15,15,30))

            titulo = fonte_grande.render("GAME OVER",True,VERMELHO)
            tela.blit(titulo,(LARGURA//2 - titulo.get_width()//2,180))

            score = fonte.render(f"Pontuação final: {pontuacao}",True,BRANCO)
            tela.blit(score,(LARGURA//2 - score.get_width()//2,250))

            pygame.draw.rect(tela,(40,120,40),(200,320,300,50),border_radius=10)
            texto_r = fonte.render("R - Jogar novamente",True,BRANCO)
            tela.blit(texto_r,(LARGURA//2 - texto_r.get_width()//2,335))

            pygame.draw.rect(tela,(120,40,40),(200,390,300,50),border_radius=10)
            texto_esc = fonte.render("ESC - Sair",True,BRANCO)
            tela.blit(texto_esc,(LARGURA//2 - texto_esc.get_width()//2,405))

            pygame.display.flip()

    pygame.display.flip()

pygame.quit()