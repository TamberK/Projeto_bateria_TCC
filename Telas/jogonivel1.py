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
pygame.display.set_caption("Bateria Educacional - Módulo 1")

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

# ===== EFEITO DE FUNDO PADRONIZADO (MENU, DIFICULDADE E GAME OVER) =====
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

# ===== POSIÇÕES DO JOGO (CAIXA NA ESQUERDA, BUMBO NA DIREITA) =====
COLUNA_B = 220  # Caixa (Esquerda)
COLUNA_K = 420  # Bumbo (Direita)

LARGURA_NOTA = 50
ALTURA_NOTA = 20

LINHA_ACERTO = 450

# ===== ESTADO DO JOGO =====
estado = "menu"

# ===== VARIÁVEIS DO JOGO =====
notas = []
pontuacao = 0
combo = 0
vidas = 3
velocidade = 5.0

pad_k_anim = 0
pad_b_anim = 0

dificuldade = 1

# ===== CONFIGURAÇÕES DE DIFICULDADE (PARÂMETROS SEPARADOS) =====
CONFIG_DIFICULDADE = {
    1: {"spawn": 55, "vel_base": 5.0, "vel_max": 7.5, "vidas": 3},
    2: {"spawn": 35, "vel_base": 5.5, "vel_max": 9.0, "vidas": 5},
    3: {"spawn": 25, "vel_base": 6.0, "vel_max": 11.0, "vidas": 10}
}

# ===== PADRÕES RÍTMICOS PARA O NÍVEL MÉDIO (SIMPLES - SEM SIMULTÂNEOS) =====
PADROES_MEDIO = [
    # Padrão 1: CAIXA, BUMBO, CAIXA, BUMBO
    ["B", "K", "B", "K"],
    # Padrão 2: BUMBO, BUMBO, CAIXA, BUMBO
    ["K", "K", "B", "K"],
    # Padrão 3: CAIXA, CAIXA, BUMBO, CAIXA
    ["B", "B", "K", "B"],
    # Padrão 4: BUMBO, CAIXA, CAIXA, BUMBO
    ["K", "B", "B", "K"],
    # Padrão 5: CAIXA, BUMBO, BUMBO, CAIXA
    ["B", "K", "K", "B"],
    # Padrão 6: BUMBO, CAIXA, BUMBO, BUMBO
    ["K", "B", "K", "K"],
    # Padrão 7: CAIXA, BUMBO, CAIXA, CAIXA
    ["B", "K", "B", "B"]
]

# ===== PADRÕES RÍTMICOS PARA O NÍVEL DIFÍCIL (VARIADOS - COM SIMULTÂNEOS) =====
PADROES_DIFICIL = [
    # Padrão 1: CAIXA, CAIXA, BUMBO, CAIXA
    ["B", "B", "K", "B"],
    # Padrão 2: BUMBO, BUMBO, CAIXA, CAIXA
    ["K", "K", "B", "B"],
    # Padrão 3: BUMBO, CAIXA, BUMBO, CAIXA
    ["K", "B", "K", "B"],
    # Padrão 4: CAIXA, BUMBO, CAIXA, BUMBO
    ["B", "K", "B", "K"],
    # Padrão 5: BUMBO+CAIXA (simultâneo), CAIXA, BUMBO, CAIXA
    ["KB", "B", "K", "B"],
    # Padrão 6: BUMBO, CAIXA, BUMBO+CAIXA (simultâneo), CAIXA
    ["K", "B", "KB", "B"]
]

padrao_medio_atual = []
padrao_medio_index = 0

padrao_dificil_atual = []
padrao_dificil_index = 0

# JANELA TEMPORAL DE INPUTS (SUPORTE A TOQUES SIMULTÂNEOS TECLADO/ARDUINO - 120ms)
historico_toques = []

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

# ===== REINICIAR JOGO =====
def reiniciar_jogo():
    global notas, pontuacao, combo, vidas, velocidade, historico_toques
    global padrao_medio_atual, padrao_medio_index, padrao_dificil_atual, padrao_dificil_index

    notas = []
    pontuacao = 0
    combo = 0
    vidas = CONFIG_DIFICULDADE[dificuldade]["vidas"]
    velocidade = CONFIG_DIFICULDADE[dificuldade]["vel_base"]
    historico_toques = []
    padrao_medio_atual = []
    padrao_medio_index = 0
    padrao_dificil_atual = []
    padrao_dificil_index = 0

# ===== CRIAR NOTA =====
def criar_nota():
    global padrao_medio_atual, padrao_medio_index, padrao_dificil_atual, padrao_dificil_index

    if dificuldade == 1:
        # FÁCIL: notas aleatórias simples
        tipo = random.choice(["K", "B"])
        notas.append({
            "tipo": tipo,
            "x": COLUNA_K if tipo == "K" else COLUNA_B,
            "y": -ALTURA_NOTA,
            "estado": "normal",
            "tempo_erro": 15
        })

    elif dificuldade == 2:
        # MÉDIO: pequenos padrões rítmicos simples (sem notas simultâneas)
        if not padrao_medio_atual or padrao_medio_index >= len(padrao_medio_atual):
            padrao_medio_atual = random.choice(PADROES_MEDIO)
            padrao_medio_index = 0

        item = padrao_medio_atual[padrao_medio_index]
        padrao_medio_index += 1

        notas.append({
            "tipo": item,
            "x": COLUNA_K if item == "K" else COLUNA_B,
            "y": -ALTURA_NOTA,
            "estado": "normal",
            "tempo_erro": 15
        })

    elif dificuldade == 3:
        # DIFÍCIL: sequência estruturada em padrões rítmicos (com simultâneos)
        if not padrao_dificil_atual or padrao_dificil_index >= len(padrao_dificil_atual):
            padrao_dificil_atual = random.choice(PADROES_DIFICIL)
            padrao_dificil_index = 0

        item = padrao_dificil_atual[padrao_dificil_index]
        padrao_dificil_index += 1

        if item == "KB":
            # Toque simultâneo: BUMBO + CAIXA na mesma altura temporal
            notas.append({
                "tipo": "K",
                "x": COLUNA_K,
                "y": -ALTURA_NOTA,
                "estado": "normal",
                "tempo_erro": 15
            })
            notas.append({
                "tipo": "B",
                "x": COLUNA_B,
                "y": -ALTURA_NOTA,
                "estado": "normal",
                "tempo_erro": 15
            })
        else:
            notas.append({
                "tipo": item,
                "x": COLUNA_K if item == "K" else COLUNA_B,
                "y": -ALTURA_NOTA,
                "estado": "normal",
                "tempo_erro": 15
            })

# ===== MENU INICIAL DO MÓDULO 1 =====
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
        sub_nivel = "MÓDULO 1: BATERIA HERO"
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
        texto_estilizado("• CAIXA   ->   Tecla S", fonte_media, BRANCO, PRETO, PRETO, x_box + 100, 205)
        texto_estilizado("• BUMBO   ->   Tecla K", fonte_media, BRANCO, PRETO, PRETO, x_box + 100, 240)

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
        texto_estilizado("1 - Fácil (Notas Aleatórias / Lento)", fonte_media, cor_f, PRETO, PRETO, x_box + 30, 156)

        # MÉDIO
        cor_m = AMARELO if dificuldade == 2 else BRANCO
        pygame.draw.rect(tela, (35, 35, 20) if dificuldade == 2 else (20, 20, 35), (x_box, 220, 460, 60), border_radius=12)
        pygame.draw.rect(tela, AMARELO if dificuldade == 2 else (60, 60, 90), (x_box, 220, 460, 60), 2, border_radius=12)
        texto_estilizado("2 - Médio (Exercício Contínuo)", fonte_media, cor_m, PRETO, PRETO, x_box + 30, 236)

        # DIFÍCIL
        cor_d = VERMELHO if dificuldade == 3 else BRANCO
        pygame.draw.rect(tela, (40, 20, 20) if dificuldade == 3 else (20, 20, 35), (x_box, 300, 460, 60), border_radius=12)
        pygame.draw.rect(tela, VERMELHO if dificuldade == 3 else (60, 60, 90), (x_box, 300, 460, 60), 2, border_radius=12)
        texto_estilizado("3 - Difícil (Padrões Rítmicos)", fonte_media, cor_d, PRETO, PRETO, x_box + 30, 316)

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

# ===== TELA DE GAME OVER (PADRONIZADA E COM BOTÃO VOLTAR ÀS DIFICULDADES) =====
def tela_gameover():
    global estado, rodando
    tempo = 0

    while estado == "gameover":
        clock.tick(60)
        tempo += 0.05
        fundo()

        # BARRA SUPERIOR
        barra = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
        barra.fill((15, 15, 25, 220))
        tela.blit(barra, (0, 0))
        pygame.draw.line(tela, (60, 60, 90), (0, 80), (LARGURA, 80), 2)

        # TÍTULO ANIMADO - GAME OVER
        deslocamento_y = int(math.sin(tempo) * 6)
        titulo = "GAME OVER"
        largura_t = fonte_grande.size(titulo)[0]
        texto_estilizado(titulo, fonte_grande, VERMELHO, PRETO, BRANCO, (LARGURA - largura_t) // 2, 15 + deslocamento_y)

        x_box = (LARGURA - 460) // 2

        # PAINEL DA PONTUAÇÃO FINAL
        pygame.draw.rect(tela, (20, 20, 35), (x_box, 130, 460, 95), border_radius=15)
        pygame.draw.rect(tela, AZUL, (x_box, 130, 460, 95), 2, border_radius=15)

        txt_score_lbl = "PONTUAÇÃO FINAL"
        largura_sl = fonte_sub.size(txt_score_lbl)[0]
        texto_estilizado(txt_score_lbl, fonte_sub, AZUL_CLARO, PRETO, PRETO, (LARGURA - largura_sl) // 2, 142)

        txt_score_val = str(pontuacao)
        largura_sv = fonte_combo.size(txt_score_val)[0]
        texto_estilizado(txt_score_val, fonte_combo, AMARELO, PRETO, PRETO, (LARGURA - largura_sv) // 2, 170)

        # RETÂNGULOS DOS BOTÕES (SUPORTE A CLIQUE DE MOUSE E TECLADO)
        rect_r = pygame.Rect(x_box, 245, 460, 55)
        rect_d = pygame.Rect(x_box, 315, 460, 55)
        rect_esc = pygame.Rect(x_box, 385, 460, 55)

        # BOTÃO R - JOGAR NOVAMENTE
        pygame.draw.rect(tela, (20, 25, 35), rect_r, border_radius=12)
        pygame.draw.rect(tela, (50, 180, 90), rect_r, 2, border_radius=12)
        txt_r = "R - Jogar Novamente"
        largura_r = fonte_media.size(txt_r)[0]
        texto_estilizado(txt_r, fonte_media, VERDE, PRETO, PRETO, (LARGURA - largura_r) // 2, 259)

        # BOTÃO D - VOLTAR ÀS DIFICULDADES
        pygame.draw.rect(tela, (20, 20, 35), rect_d, border_radius=12)
        pygame.draw.rect(tela, AMARELO, rect_d, 2, border_radius=12)
        txt_d = "D - Voltar às Dificuldades"
        largura_d = fonte_media.size(txt_d)[0]
        texto_estilizado(txt_d, fonte_media, AMARELO, PRETO, PRETO, (LARGURA - largura_d) // 2, 329)

        # BOTÃO ESC - SAIR
        pygame.draw.rect(tela, (25, 20, 25), rect_esc, border_radius=12)
        pygame.draw.rect(tela, (180, 60, 60), rect_esc, 2, border_radius=12)
        txt_esc = "ESC - Sair"
        largura_esc = fonte_media.size(txt_esc)[0]
        texto_estilizado(txt_esc, fonte_media, VERMELHO, PRETO, PRETO, (LARGURA - largura_esc) // 2, 399)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar_jogo()
                    estado = "jogo"

                if evento.key == pygame.K_d:
                    estado = "dificuldade"

                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    pos = evento.pos
                    if rect_r.collidepoint(pos):
                        reiniciar_jogo()
                        estado = "jogo"
                    elif rect_d.collidepoint(pos):
                        estado = "dificuldade"
                    elif rect_esc.collidepoint(pos):
                        pygame.quit()
                        sys.exit()

# ===== LOOP PRINCIPAL =====
rodando = True
contador = 0

while rodando:

    clock.tick(60)

    if estado == "menu":
        tela_menu()

    if estado == "dificuldade":
        tela_dificuldade()

    if estado == "gameover":
        tela_gameover()

    if estado == "jogo":

        config_dif = CONFIG_DIFICULDADE[dificuldade]
        spawn = config_dif["spawn"]
        
        # Controle de velocidade com limite máximo por dificuldade
        velocidade = min(config_dif["vel_max"], config_dif["vel_base"] + pontuacao * 0.008)

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

        agora = pygame.time.get_ticks()

        # LEITURA DE EVENTOS (TECLADO)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key in MAPA_TECLAS:
                    historico_toques.append({"tipo": MAPA_TECLAS[evento.key], "tempo": agora, "usado": False})

        # LEITURA ARDUINO
        if arduino and arduino.in_waiting > 0:
            dado = arduino.readline().decode().strip()
            if dado in ["K", "B"]:
                historico_toques.append({"tipo": dado, "tempo": agora, "usado": False})

        # MANTER APENAS INPUTS DENTRO DA JANELA TEMPORAL (120ms PARA SUPORTE A SIMULTÂNEOS)
        historico_toques = [h for h in historico_toques if agora - h["tempo"] <= 120]

        # ===== COLUNAS (CAIXA NA ESQUERDA, BUMBO NA DIREITA) =====
        pygame.draw.rect(tela, CINZA, (COLUNA_B - 25, 0, 100, ALTURA))
        pygame.draw.rect(tela, AZUL, (COLUNA_B - 25, 0, 100, ALTURA), 3)

        pygame.draw.rect(tela, CINZA, (COLUNA_K - 25, 0, 100, ALTURA))
        pygame.draw.rect(tela, AZUL, (COLUNA_K - 25, 0, 100, ALTURA), 3)

        # ===== CRIAR NOTAS =====
        contador += 1
        if contador >= spawn:
            criar_nota()
            contador = 0

        # ===== LINHA DE ACERTO =====
        pygame.draw.line(tela, (30, 100, 255), (0, LINHA_ACERTO), (LARGURA, LINHA_ACERTO), 10)
        pygame.draw.line(tela, AZUL_CLARO, (0, LINHA_ACERTO), (LARGURA, LINHA_ACERTO), 4)

        # ===== ATUALIZAR E AVALIAR NOTAS =====
        for nota in notas[:]:

            if nota["estado"] == "normal":

                nota["y"] += velocidade

                # Verificar se há toque válido correspondente no histórico ativo
                toque_valido = None
                for h in historico_toques:
                    if not h["usado"] and h["tipo"] == nota["tipo"]:
                        toque_valido = h
                        break

                if toque_valido and abs(nota["y"] - LINHA_ACERTO) < 40:

                    distancia = abs(nota["y"] - LINHA_ACERTO)

                    if distancia < 10:
                        pontuacao += 20 + combo
                        combo += 1
                    elif distancia < 25:
                        pontuacao += 10 + combo
                        combo += 1
                    else:
                        pontuacao += 5
                        combo = 0

                    if nota["tipo"] == "K":
                        pad_k_anim = 10
                    else:
                        pad_b_anim = 10

                    toque_valido["usado"] = True
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

        # ===== PADS (ESQUERDA: CAIXA, DIREITA: BUMBO) =====
        raio_k = 30 + pad_k_anim
        raio_b = 30 + pad_b_anim

        pygame.draw.circle(tela, AZUL, (COLUNA_B + 25, LINHA_ACERTO + 70), raio_b)
        pygame.draw.circle(tela, PRETO, (COLUNA_B + 25, LINHA_ACERTO + 70), raio_b - 6)

        pygame.draw.circle(tela, AZUL, (COLUNA_K + 25, LINHA_ACERTO + 70), raio_k)
        pygame.draw.circle(tela, PRETO, (COLUNA_K + 25, LINHA_ACERTO + 70), raio_k - 6)

        if pad_k_anim > 0:
            pad_k_anim -= 1

        if pad_b_anim > 0:
            pad_b_anim -= 1

        # NORMAS VISUAIS DE IDENTIFICAÇÃO DOS INSTRUMENTOS
        tela.blit(fonte.render("CAIXA", True, BRANCO), (COLUNA_B - 10, LINHA_ACERTO + 110))
        tela.blit(fonte.render("BUMBO", True, BRANCO), (COLUNA_K - 15, LINHA_ACERTO + 110))

        # ===== HUD (INDICADORES DE VIDAS ORGANIZADOS EM 2 LINHAS DE 5) =====
        pygame.draw.rect(tela, (15, 15, 30), (0, 0, LARGURA, 80))

        tela.blit(fonte.render(f"Pontos: {pontuacao}", True, BRANCO), (30, 20))

        for i in range(vidas):
            linha = i // 5
            coluna = i % 5
            x = 40 + coluna * 30
            y = 100 + linha * 25
            pygame.draw.circle(tela, VERMELHO, (x, y), 10)

        pygame.display.flip()

        if vidas <= 0:
            estado = "gameover"

pygame.quit()