import pygame
import sys
import math
import random
import serial
from menu import menu
from scores import salvar_score, carregar_scores

pygame.init()

#Configuração serial
try:
    serial_port = serial.Serial('COM3', 9600)
    arduino_conectado = True
except:
    serial_port = None
    arduino_conectado = False

# MENU
nome_jogador = menu()

LARGURA, ALTURA = 1100, 650
tela = pygame.display.set_mode((LARGURA,ALTURA))
pygame.display.set_caption("Drum Trainer PRO")

clock = pygame.time.Clock()

# FONTES
fonte = pygame.font.SysFont("arial",26, bold=True)
fonte_titulo = pygame.font.SysFont("arial",70, bold=True)

#ESCOLHER MODO
def escolher_modo():
    while True:
        tela.fill((0,0,0))

        titulo = fonte_titulo.render("ESCOLHA O MODO", True, (255,255,255))
        tela.blit(titulo, (250,150))

        op1 = fonte.render("1 - Teclado", True, (0,255,120))
        op2 = fonte.render("2 - Bateria (Arduino)", True, (0,170,255))

        tela.blit(op1, (450,320))
        tela.blit(op2, (450,370))

        if not arduino_conectado:
            aviso = fonte.render("Arduino não conectado!", True, (255,0,0))
            tela.blit(aviso, (400,450))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "teclado"
                if evento.key == pygame.K_2:
                    if arduino_conectado:
                        return "arduino"

modo_entrada = escolher_modo()

# CORES
CORES = {
    "A": (0,170,255),
    "D": (255,220,0),
    "G": (170,0,255),
    "K": (255,120,0)
}

BRANCO = (255,255,255)
PRETO = (0,0,0)
VERMELHO = (255,70,70)

feedback_texto = ""
feedback_timer = 0
erros_consecutivos = 0
score_salvo = False

# FUNDO
def fundo():
    for y in range(ALTURA):
        cor = (5, 5 + y//20, 15 + y//18)
        pygame.draw.line(tela, cor, (0,y), (LARGURA,y))

# PARTITURA
BASE = 200
ESPACO = 34
linhas = [BASE+i*ESPACO for i in range(5)]

Y_POS = {
    "A": linhas[0] - 5,
    "D": linhas[1],
    "G": linhas[2] + 5,
    "K": linhas[4] + 10
}

LINHA_EXEC = 400

# PADS
pads = {
    "A": {"x":420, "y":580, "anim":0},
    "D": {"x":570, "y":580, "anim":0},
    "G": {"x":720, "y":580, "anim":0},
    "K": {"x":870, "y":580, "anim":0}
}

# VARIÁVEIS
notas = []
score = 0
combo = 0
erros = 0
max_erros = 10

velocidade = 4
spawn = 60
contador = 0

game_over_flag = False

# NOTA ALEATÓRIA
def criar_nota():
    inst = random.choice(list(CORES.keys()))
    notas.append({
        "inst":inst,
        "x":LARGURA,
        "y":Y_POS[inst],
        "status": "normal"
    })

# DESENHAR NOTA
def desenhar_nota(x,y,inst,status):
    if status == "acerto":
        cor = (0,255,120)
    elif status == "erro":
        cor = (255,70,70)
    else:
        cor = CORES[inst]

    pygame.draw.circle(tela, cor, (int(x),int(y)), 11)

    if inst == "A":
        pygame.draw.circle(tela, PRETO, (int(x),int(y)), 5)
    elif inst == "D":
        pygame.draw.line(tela, PRETO, (x-8,y),(x+8,y),3)
    elif inst == "G":
        pygame.draw.line(tela, PRETO, (x-8,y-8),(x+8,y+8),3)
        pygame.draw.line(tela, PRETO, (x+8,y-8),(x-8,y+8),3)
    elif inst == "K":
        pygame.draw.circle(tela, PRETO, (int(x),int(y)), 3)

# PADS
def desenhar_pads():
    for inst, pad in pads.items():
        raio = 35 + pad["anim"]

        pygame.draw.circle(tela,(0,0,0),(pad["x"]+6,pad["y"]+6),raio)
        pygame.draw.circle(tela,CORES[inst],(pad["x"],pad["y"]),raio)
        pygame.draw.circle(tela,(230,230,230),(pad["x"],pad["y"]),raio-10)

        if inst == "A":
            pygame.draw.circle(tela, PRETO, (pad["x"],pad["y"]), 6)
        elif inst == "D":
            pygame.draw.line(tela, PRETO, (pad["x"]-10,pad["y"]), (pad["x"]+10,pad["y"]), 4)
        elif inst == "G":
            pygame.draw.line(tela, PRETO, (pad["x"]-10,pad["y"]-10),(pad["x"]+10,pad["y"]+10),4)
            pygame.draw.line(tela, PRETO, (pad["x"]+10,pad["y"]-10),(pad["x"]-10,pad["y"]+10),4)
        elif inst == "K":
            pygame.draw.circle(tela, PRETO, (pad["x"],pad["y"]), 3)

        if pad["anim"] > 0:
            pad["anim"] -= 2

# HUD
def desenhar_hud():
    barra = pygame.Surface((LARGURA,90), pygame.SRCALPHA)
    barra.fill((15,15,25,220))
    tela.blit(barra,(0,0))

    pygame.draw.line(tela,(60,60,90),(0,90),(LARGURA,90),2)

    tela.blit(fonte.render("SCORE:",True,(255,220,0)),(20,25))
    tela.blit(fonte.render(str(score),True,BRANCO),(130,25))

    tela.blit(fonte.render("COMBO:",True,(255,220,0)),(260,25))
    tela.blit(fonte.render(str(combo),True,BRANCO),(380,25))

    tela.blit(fonte.render("ERROS:",True,(255,220,0)),(500,25))
    tela.blit(fonte.render(f"{erros}/{max_erros}",True,BRANCO),(620,25))

# FEEDBACK FINAL COM BORDA DUPLA
def desenhar_feedback():
    if feedback_timer > 0:

        if feedback_texto == "BOM":
            cor = (0,255,120)
        elif feedback_texto == "EXCELENTE":
            cor = (255,140,0)
        elif feedback_texto == "INCRIVEL":
            cor = (255,215,0)

            # efeito brilho
            for _ in range(8):
                pygame.draw.circle(
                    tela,
                    (255,215,0),
                    (LARGURA - 150 + random.randint(-40,40),
                     60 + random.randint(-25,25)),
                    random.randint(2,5)
                )
        elif feedback_texto == "PESSIMO":
            cor = (255,0,0)
        else:
            cor = VERMELHO

        texto = fonte.render(feedback_texto, True, cor)

        x = LARGURA - texto.get_width() - 30
        y = 30

        # borda branca
        sombra_branca = fonte.render(feedback_texto, True, BRANCO)
        tela.blit(sombra_branca, (x+3,y+3))

        # borda preta
        sombra_preta = fonte.render(feedback_texto, True, PRETO)
        tela.blit(sombra_preta, (x+2,y+2))

        # texto principal
        tela.blit(texto, (x,y))
#TELA FINAL
def tela_final():
    tempo = 0
    anim_tempo = 0

    while True:
        clock.tick(60)
        fundo()

        tempo += 0.05
        anim_tempo += 1

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return "reiniciar"
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # BARRA SUPERIOR
        barra = pygame.Surface((LARGURA,90), pygame.SRCALPHA)
        barra.fill((15,15,25,220))
        tela.blit(barra,(0,0))
        pygame.draw.line(tela,(60,60,90),(0,90),(LARGURA,90),2)

        # FUNÇÃO DE TEXTO ESTILIZADO (igual menu)
        def texto_estilizado(txt, fonte, cor, borda, sombra, x, y):
            render = fonte.render(txt, True, cor)
            borda_render = fonte.render(txt, True, borda)
            sombra_render = fonte.render(txt, True, sombra)

            tela.blit(sombra_render, (x+4, y+4))
            tela.blit(borda_render, (x+2, y+2))
            tela.blit(render, (x, y))

        # TÍTULO COM ANIMAÇÃO (igual menu)
        deslocamento_y = int(math.sin(tempo) * 8)
        titulo = "GAME OVER"
        largura = fonte_titulo.size(titulo)[0]
        x_titulo = (LARGURA - largura) // 2

        texto_estilizado(
            titulo,
            fonte_titulo,
            VERMELHO,
            PRETO,
            BRANCO,
            x_titulo,
            90 + deslocamento_y
        )

        # INFORMAÇÕES DO JOGADOR
        centro_x = LARGURA // 2

        texto_estilizado(
            f"Jogador: {nome_jogador}",
            fonte,
            BRANCO,
            PRETO,
            PRETO,
            centro_x - 150,
            260
        )

        texto_estilizado(
            f"Score: {score}",
            fonte,
            (255,220,0),
            PRETO,
            PRETO,
            centro_x - 150,
            300
        )

        # CONTROLES
        texto_estilizado(
            "Pressione R para jogar novamente",
            fonte,
            (0,255,120),
            PRETO,
            PRETO,
            centro_x - 220,
            360
        )

        texto_estilizado(
            "ESC para sair",
            fonte,
            BRANCO,
            PRETO,
            PRETO,
            centro_x - 100,
            400
        )

        # RANKING IGUAL AO MENU (com animação)
        scores = carregar_scores()

        x_base = 780
        y_base = 180

        texto_estilizado("RANKING", fonte, (0,170,255), BRANCO, PRETO, x_base, y_base)

        for i, s in enumerate(scores[:5]):

            delay = i * 12
            progresso = max(0, min(1, (anim_tempo - delay) / 20))

            x_final = x_base
            x_inicial = LARGURA + 100
            x = x_inicial + (x_final - x_inicial) * progresso

            y = y_base + 50 + i * 30

            if i == 0:
                cor = (255,215,0)
                texto = f"👑 1. {s['nome']} - {s['score']}"
            elif i == 1:
                cor = (192,192,192)
                texto = f"2. {s['nome']} - {s['score']}"
            elif i == 2:
                cor = (205,127,50)
                texto = f"3. {s['nome']} - {s['score']}"
            else:
                cor = BRANCO
                texto = f"{i+1}. {s['nome']} - {s['score']}"

            texto_estilizado(
                texto,
                pygame.font.SysFont("arial", 22, bold=True),
                cor,
                PRETO,
                PRETO,
                int(x),
                y
            )

        pygame.display.flip()

# LOOP (continua igual)
rodando = True

while rodando:

    clock.tick(60)
    fundo()

    toque = None

    #CONTROLE POR MODO ESCOLHIDO
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if modo_entrada == "teclado":
             if evento.type == pygame.KEYDOWN:
                 if evento.key == pygame.K_a: toque = "A"
                 if evento.key == pygame.K_d: toque = "D"
                 if evento.key == pygame.K_g: toque = "G"
                 if evento.key == pygame.K_k: toque = "K"
                
    if modo_entrada == "arduino" and arduino_conectado:
        if serial_port.in_waiting > 0:
            dado = serial_port.readline().decode().strip()

            if dado in ["A","D","G","K"]:
                toque = dado

    if not game_over_flag:

        contador += 1
        if contador >= spawn:
            criar_nota()
            contador = 0

        nota_alvo = min(notas, key=lambda n: abs(n["x"] - LINHA_EXEC)) if notas else None

        for nota in notas[:]:
            nota["x"] -= velocidade
            dist = abs(nota["x"]-LINHA_EXEC)

            if nota["status"] == "normal":

                if toque and nota == nota_alvo and dist < 40:

                    pads[nota["inst"]]["anim"] = 8

                    if toque == nota["inst"]:
                        score += 100
                        combo += 1
                        erros_consecutivos = 0
                        nota["status"] = "acerto"

                        if combo % 5 == 0:
                            velocidade += 0.3
                            spawn = max(30, spawn - 2)

                        if combo < 5:
                            feedback_texto = "BOM"
                        elif combo < 10:
                            feedback_texto = "EXCELENTE"
                        else:
                            feedback_texto = "INCRIVEL"

                    else:
                        combo = 0
                        erros += 1
                        erros_consecutivos += 1
                        nota["status"] = "erro"
                        feedback_texto = "PESSIMO" if erros_consecutivos >= 3 else "ERROU"

                    feedback_timer = 30

                elif nota["x"] < LINHA_EXEC - 40:
                    erros += 1
                    combo = 0
                    erros_consecutivos += 1
                    nota["status"] = "erro"
                    feedback_texto = "PESSIMO" if erros_consecutivos >= 3 else "ERROU"
                    feedback_timer = 30

            if nota["x"] < -50:
                notas.remove(nota)

        if erros >= max_erros:
            game_over_flag = True

    else:
        if not score_salvo:
            salvar_score(nome_jogador, score)
            score_salvo = True

        resultado = tela_final()

        if resultado == "reiniciar":
            notas.clear()
            score = 0
            combo = 0
            erros = 0
            contador = 0
            velocidade = 4
            spawn = 60
            game_over_flag = False
            score_salvo = False
            erros_consecutivos = 0

    for y in linhas:
        pygame.draw.line(tela,(70,70,100),(0,y),(LARGURA,y),2)

    pygame.draw.line(tela,(0,170,255),(LINHA_EXEC,0),(LINHA_EXEC,ALTURA),3)

    for nota in notas:
        desenhar_nota(nota["x"],nota["y"],nota["inst"],nota["status"])

    desenhar_hud()
    desenhar_pads()
    desenhar_feedback()

    if feedback_timer > 0:
        feedback_timer -= 1

    pygame.display.flip()

pygame.quit()
sys.exit()