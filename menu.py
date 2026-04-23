import pygame
from scores import carregar_scores
import math

pygame.init()

LARGURA, ALTURA = 1100, 650
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Drum Trainer PRO - Menu")

fonte = pygame.font.SysFont("arial", 28, bold=True)
fonte_titulo = pygame.font.SysFont("arial", 80, bold=True)
fonte_ranking = pygame.font.SysFont("arial", 22, bold=True)

BRANCO = (255,255,255)
PRETO = (0,0,0)
AMARELO = (255,220,0)
VERDE = (0,255,120)
AZUL = (0,170,255)

OURO = (255,215,0)
PRATA = (192,192,192)
BRONZE = (205,127,50)

clock = pygame.time.Clock()

# FUNDO
def fundo():
    for y in range(ALTURA):
        cor = (5, 5 + y//20, 15 + y//18)
        pygame.draw.line(tela, cor, (0,y), (LARGURA,y))

# TEXTO ESTILIZADO
def texto_estilizado(txt, fonte, cor, borda, sombra, x, y):
    render = fonte.render(txt, True, cor)
    borda_render = fonte.render(txt, True, borda)
    sombra_render = fonte.render(txt, True, sombra)

    tela.blit(sombra_render, (x+4, y+4))
    tela.blit(borda_render, (x+2, y+2))
    tela.blit(render, (x, y))

# RANKING ORGANIZADO
def desenhar_ranking(anim_tempo):
    scores = carregar_scores()

    x_base = 780  # lado direito fixo
    y_base = 180

    texto_estilizado("RANKING", fonte, AZUL, BRANCO, PRETO, x_base, y_base)

    for i, s in enumerate(scores[:5]):

        delay = i * 12
        progresso = max(0, min(1, (anim_tempo - delay) / 20))

        x_final = x_base
        x_inicial = LARGURA + 100
        x = x_inicial + (x_final - x_inicial) * progresso

        y = y_base + 50 + i * 30

        if i == 0:
            cor = OURO
            texto = f"👑 1. {s['nome']} - {s['score']}"
        elif i == 1:
            cor = PRATA
            texto = f"2. {s['nome']} - {s['score']}"
        elif i == 2:
            cor = BRONZE
            texto = f"3. {s['nome']} - {s['score']}"
        else:
            cor = BRANCO
            texto = f"{i+1}. {s['nome']} - {s['score']}"

        texto_estilizado(texto, fonte_ranking, cor, PRETO, PRETO, int(x), y)

# MENU
def menu():
    nome = ""
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
                exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and nome != "":
                    return nome
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    nome += evento.unicode

        # BARRA SUPERIOR
        barra = pygame.Surface((LARGURA,90), pygame.SRCALPHA)
        barra.fill((15,15,25,220))
        tela.blit(barra,(0,0))
        pygame.draw.line(tela,(60,60,90),(0,90),(LARGURA,90),2)

        # TÍTULO CENTRAL
        deslocamento_y = int(math.sin(tempo) * 8)
        titulo = "DRUM TRAINER PRO"
        largura = fonte_titulo.size(titulo)[0]
        x_titulo = (LARGURA - largura) // 2

        texto_estilizado(titulo, fonte_titulo, AMARELO, PRETO, BRANCO,
                         x_titulo, 90 + deslocamento_y)

        # BLOCO CENTRAL (INPUT + TEXTOS)
        centro_x = LARGURA // 2

        # TEXTO
        texto_estilizado("Digite seu nome:", fonte, BRANCO, PRETO, PRETO,
                         centro_x - 140, 260)

        # CAIXA INPUT
        largura_box = 400
        altura_box = 50
        x_box = centro_x - largura_box // 2

        pygame.draw.rect(tela, (30,30,50),
                         (x_box, 300, largura_box, altura_box),
                         border_radius=12)

        pygame.draw.rect(tela, (80,80,120),
                         (x_box, 300, largura_box, altura_box),
                         2, border_radius=12)

        texto_estilizado(nome, fonte, VERDE, PRETO, PRETO,
                         x_box + 10, 310)

        # ENTER
        texto_estilizado("Pressione ENTER para começar",
                         fonte,
                         AMARELO,
                         PRETO,
                         PRETO,
                         centro_x - 210,
                         380)

        # RANKING (lado direito, separado)
        desenhar_ranking(anim_tempo)

        pygame.display.flip()