import pygame
import serial
import random
import sys

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
fonte_grande = pygame.font.SysFont("arial",60)
fonte_combo = pygame.font.SysFont("arial",50)
fonte_media = pygame.font.SysFont("arial",28)
fonte_sub = pygame.font.SysFont("arial",22)

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

# MAPA DE TECLAS (ADICIONADO)
MAPA_TECLAS = {
    pygame.K_k: "K",  # Kick
    pygame.K_s: "B"   # Snare
}

# ===== PARTICULAS =====
particulas = []

for i in range(40):
    particulas.append([
        random.randint(0,LARGURA),
        random.randint(0,ALTURA),
        random.randint(1,3)
    ])

# ===== REINICIAR =====
def reiniciar_jogo():
    global notas,pontuacao,combo,vidas,velocidade,fila_toques

    notas = []
    pontuacao = 0
    combo = 0
    vidas = 3
    velocidade = 5
    fila_toques = []

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

# ===== MENU =====
def tela_menu():

    global estado

    while estado == "menu":

        tela.fill((10,10,20))

        # Título Nível 1
        sub_nivel = fonte_media.render("NÍVEL 1", True, AZUL_CLARO)
        tela.blit(sub_nivel, (LARGURA//2 - sub_nivel.get_width()//2, 35))

        titulo = fonte_grande.render("BATERIA HERO", True, BRANCO)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 70))

        # Objetivo Pedagógico
        obj_txt = fonte_sub.render("Objetivo: Aprender os primeiros ritmos da bateria", True, AZUL_CLARO)
        tela.blit(obj_txt, (LARGURA//2 - obj_txt.get_width()//2, 145))

        # Painel de Controles
        pygame.draw.rect(tela, CINZA, (150, 190, 400, 120), border_radius=12)
        pygame.draw.rect(tela, AZUL, (150, 190, 400, 120), 2, border_radius=12)

        txt_ctrl = fonte_sub.render("Controles (Teclado):", True, AZUL_CLARO)
        tela.blit(txt_ctrl, (170, 200))

        txt_kick = fonte_sub.render("• KICK (Bumbo)   ->  Tecla K", True, BRANCO)
        tela.blit(txt_kick, (180, 235))

        txt_snare = fonte_sub.render("• SNARE (Caixa)  ->  Tecla S", True, BRANCO)
        tela.blit(txt_snare, (180, 268))

        # Opções do Menu
        jogar = fonte_media.render("ENTER - Jogar", True, VERDE)
        tela.blit(jogar, (LARGURA//2 - jogar.get_width()//2, 340))

        dificuldade_txt = fonte_media.render("D - Dificuldade", True, BRANCO)
        tela.blit(dificuldade_txt, (LARGURA//2 - dificuldade_txt.get_width()//2, 390))

        sair = fonte_media.render("ESC - Sair", True, VERMELHO)
        tela.blit(sair, (LARGURA//2 - sair.get_width()//2, 440))

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

# ===== TELA DIFICULDADE =====
def tela_dificuldade():

    global estado,dificuldade

    while estado == "dificuldade":

        tela.fill((10,10,20))

        titulo = fonte_grande.render("DIFICULDADE",True,AZUL)
        tela.blit(titulo,(LARGURA//2 - titulo.get_width()//2,150))

        f = fonte.render("1 - Fácil",True,BRANCO)
        m = fonte.render("2 - Médio",True,BRANCO)
        d = fonte.render("3 - Difícil",True,BRANCO)

        tela.blit(f,(300,320))
        tela.blit(m,(300,360))
        tela.blit(d,(300,400))

        pygame.display.flip()

        for evento in pygame.event.get():

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

        # FUNDO
        for y in range(ALTURA):
            cor = (5,5+y//5,25+y//4)
            pygame.draw.line(tela,cor,(0,y),(LARGURA,y))

        # PARTICULAS
        for p in particulas:

            pygame.draw.circle(tela,(40,80,150),(p[0],p[1]),p[2])

            p[1] += 1

            if p[1] > ALTURA:
                p[0] = random.randint(0,LARGURA)
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
        pygame.draw.rect(tela,CINZA,(COLUNA_K-25,0,100,ALTURA))
        pygame.draw.rect(tela,AZUL,(COLUNA_K-25,0,100,ALTURA),3)

        pygame.draw.rect(tela,CINZA,(COLUNA_B-25,0,100,ALTURA))
        pygame.draw.rect(tela,AZUL,(COLUNA_B-25,0,100,ALTURA),3)

        # ===== CRIAR NOTAS =====
        contador += 1
        if contador >= spawn:
            criar_nota()
            contador = 0

        # ===== LINHA DE ACERTO =====
        pygame.draw.line(tela,(30,100,255),(0,LINHA_ACERTO),(LARGURA,LINHA_ACERTO),10)
        pygame.draw.line(tela,AZUL_CLARO,(0,LINHA_ACERTO),(LARGURA,LINHA_ACERTO),4)

        # ===== NOTAS =====
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

            cor = AZUL_CLARO if nota["estado"]=="normal" else VERMELHO

            pygame.draw.rect(tela,cor,(nota["x"],nota["y"],LARGURA_NOTA,ALTURA_NOTA),border_radius=6)

        # FEEDBACK
        if tempo_feedback > 0:
            txt = fonte_combo.render(texto_feedback,True,BRANCO)
            tela.blit(txt,(LARGURA//2 - txt.get_width()//2,200))
            tempo_feedback -= 1

        velocidade = 5 + pontuacao*0.01

        # ===== PADS =====
        raio_k = 30 + pad_k_anim
        raio_b = 30 + pad_b_anim

        pygame.draw.circle(tela,AZUL,(COLUNA_K+25,LINHA_ACERTO+70),raio_k)
        pygame.draw.circle(tela,PRETO,(COLUNA_K+25,LINHA_ACERTO+70),raio_k-6)

        pygame.draw.circle(tela,AZUL,(COLUNA_B+25,LINHA_ACERTO+70),raio_b)
        pygame.draw.circle(tela,PRETO,(COLUNA_B+25,LINHA_ACERTO+70),raio_b-6)

        if pad_k_anim > 0:
            pad_k_anim -= 1

        if pad_b_anim > 0:
            pad_b_anim -= 1

        tela.blit(fonte.render("KICK",True,BRANCO),(COLUNA_K-10,LINHA_ACERTO+110))
        tela.blit(fonte.render("SNARE",True,BRANCO),(COLUNA_B-10,LINHA_ACERTO+110))

        # ===== HUD =====
        pygame.draw.rect(tela,(15,15,30),(0,0,LARGURA,80))

        tela.blit(fonte.render(f"Pontos: {pontuacao}",True,BRANCO),(30,20))

        for i in range(vidas):
            pygame.draw.circle(tela,VERMELHO,(40+i*30,100),10)

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

        tela.fill((15,15,30))

        titulo = fonte_grande.render("GAME OVER",True,VERMELHO)
        tela.blit(titulo,(LARGURA//2 - titulo.get_width()//2,180))

        score = fonte.render(f"Pontuação final: {pontuacao}",True,BRANCO)
        tela.blit(score,(LARGURA//2 - score.get_width()//2,260))

        texto_r = fonte.render("R - Jogar novamente",True,BRANCO)
        tela.blit(texto_r,(LARGURA//2 - texto_r.get_width()//2,350))

        texto_esc = fonte.render("ESC - Sair",True,BRANCO)
        tela.blit(texto_esc,(LARGURA//2 - texto_esc.get_width()//2,400))

        pygame.display.flip()

pygame.quit()