import pygame
import sys

# =========================
# CORES
# =========================

BRANCO = (255,255,255)
PRETO = (0,0,0)

AZUL = (0,170,255)
VERDE = (0,255,120)
VERMELHO = (255,70,70)
LARANJA = (255,140,0)
AMARELO = (255,255,0)

# =========================
# FUNDO PADRONIZADO
# =========================

def fundo(tela, largura, altura):

    for y in range(altura):

        cor = (
            5,
            5 + y // 20,
            15 + y // 18
        )

        pygame.draw.line(
            tela,
            cor,
            (0, y),
            (largura, y)
        )

# =========================
# TELA DO GRÁFICO
# =========================

def tela_grafico_temporal(
        tela,
        clock,
        fonte,
        fonte_titulo,
        largura,
        altura,
        dados_tempo
    ):

    while True:

        clock.tick(60)

        # =========================
        # FUNDO
        # =========================

        fundo(tela, largura, altura)

        # EFEITO ESCURO CENTRAL
        overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        tela.blit(overlay, (0,0))

        # =========================
        # PAINEL PRINCIPAL
        # =========================

        painel = pygame.Rect(80, 110, 940, 470)

        pygame.draw.rect(
            tela,
            (12,18,30),
            painel,
            border_radius=30
        )

        pygame.draw.rect(
            tela,
            (0,170,255),
            painel,
            width=3,
            border_radius=30
        )

        # =========================
        # TÍTULO
        # =========================

        sombra = fonte_titulo.render(
            "PRECISAO TEMPORAL",
            True,
            (0,40,70)
        )

        titulo = fonte_titulo.render(
            "PRECISAO TEMPORAL",
            True,
            (0,170,255)
        )

        tela.blit(sombra, (165,42))
        tela.blit(titulo, (160,35))

        # =========================
        # SUBTÍTULO
        # =========================

        subtitulo = fonte.render(
            "Analise temporal da execucao musical",
            True,
            BRANCO
        )

        tela.blit(subtitulo, (340,130))

        # =========================
        # LINHA CENTRAL
        # =========================

        y_centro = 420

        pygame.draw.line(
            tela,
            (240,240,240),
            (170, y_centro),
            (930, y_centro),
            4
        )

        # TEXTO DA LINHA
        texto_linha = pygame.font.SysFont(
            "arial",
            12,
            bold=True
        ).render(
            "LINHA DE PRECISAO (0ms)",
            True,
            (180,180,180)
        )

        tela.blit(texto_linha, (830,385))

        # =========================
        # INSTRUMENTOS
        # =========================

        instrumentos = ["A", "D", "G", "K"]

        nomes = {
            "A": "BUMBO",
            "D": "CAIXA",
            "G": "TOM",
            "K": "PRATO"
        }

        x_inicial = 210
        espacamento = 170
        largura_barra = 90

        # =========================
        # BARRAS
        # =========================

        for i, inst in enumerate(instrumentos):

            dados = dados_tempo[inst]

            media = (
                sum(dados) / len(dados)
                if len(dados) > 0 else 0
            )

            altura_barra = abs(media) * 2

            altura_barra = min(altura_barra, 180)

            x = x_inicial + i * espacamento

            # =========================
            # CORES
            # =========================

            if media > 15:

                cor = (255,140,0)

            elif media < -15:

                cor = (255,70,70)

            else:

                cor = (0,255,120)

            # =========================
            # GLOW
            # =========================

            glow = pygame.Surface(
                (largura_barra + 30, altura_barra + 30),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                glow,
                (*cor, 80),
                (0,0,largura_barra + 30, altura_barra + 30),
                border_radius=18
            )

            if media >= 0:

                tela.blit(
                    glow,
                    (x - 15, y_centro - altura_barra - 15)
                )

            else:

                tela.blit(
                    glow,
                    (x - 15, y_centro - 15)
                )

            # =========================
            # BARRAS
            # =========================

            if media >= 0:

                pygame.draw.rect(
                    tela,
                    cor,
                    (
                        x,
                        y_centro - altura_barra,
                        largura_barra,
                        altura_barra
                    ),
                    border_radius=15
                )

            else:

                pygame.draw.rect(
                    tela,
                    cor,
                    (
                        x,
                        y_centro,
                        largura_barra,
                        altura_barra
                    ),
                    border_radius=15
                )

            # =========================
            # BORDA
            # =========================

            if media >= 0:

                pygame.draw.rect(
                    tela,
                    BRANCO,
                    (
                        x,
                        y_centro - altura_barra,
                        largura_barra,
                        altura_barra
                    ),
                    2,
                    border_radius=15
                )

            else:

                pygame.draw.rect(
                    tela,
                    BRANCO,
                    (
                        x,
                        y_centro,
                        largura_barra,
                        altura_barra
                    ),
                    2,
                    border_radius=15
                )

            # =========================
            # VALORES
            # =========================

            valor = fonte.render(
                f"{media:.1f}ms",
                True,
                BRANCO
            )

            if media >= 0:

                tela.blit(
                    valor,
                    (x - 5, y_centro - altura_barra - 45)
                )

            else:

                tela.blit(
                    valor,
                    (x - 5, y_centro + altura_barra + 10)
                )

            # =========================
            # NOME INSTRUMENTO
            # =========================

            nome = fonte.render(
                nomes[inst],
                True,
                BRANCO
            )

            tela.blit(
                nome,
                (x - 5, 520)
            )

        # =========================
        # LEGENDA
        # =========================

        fonte_legenda = pygame.font.SysFont(
            "arial",
            16,
            bold=True
        )

        # CAIXA LEGENDA

        pygame.draw.rect(
            tela,
            (15,15,25),
            (180,600,700,40),
            border_radius=12
        )

        pygame.draw.rect(
            tela,
            (70,70,90),
            (180,600,700,40),
            width=2,
            border_radius=12
        )

        legenda1 = fonte_legenda.render(
            "VERDE = PRECISO",
            True,
            (0,255,120)
        )

        legenda2 = fonte_legenda.render(
            "LARANJA = ATRASANDO",
            True,
            (255,140,0)
        )

        legenda3 = fonte_legenda.render(
            "VERMELHO = ADIANTANDO",
            True,
            (255,70,70)
        )

        tela.blit(legenda1, (210,610))
        tela.blit(legenda2, (390,610))
        tela.blit(legenda3, (620,610))



        # =========================
        # BOTÃO VOLTAR
        # =========================
        
        #retangulo em volta
        pygame.draw.rect(
            tela,
            (20,20,35),
            (16,600,130,45),
            border_radius=15
        )
        #borda azul no retangulo
        pygame.draw.rect(
            tela,
            (0,170,255),
            (16,600,130,45),
            width=2,
            border_radius=15
        )

        fonte_voltar = pygame.font.SysFont(
            "arial",
            24,
            bold=True
        )
        voltar = fonte_voltar.render(
            "ESC:Voltar",
            True,
            (255,140,0)
        )

        # TEXTO DA BORDA CIANO

        voltar_borda = fonte_voltar.render(
            "ESC:Voltar",
            True,
            (0,255,255)
        )

        # DESENHA A BORDA EM VOLTA

        tela.blit(voltar_borda, (18,600))  # esquerda
        tela.blit(voltar_borda, (22,600))  # direita
        tela.blit(voltar_borda, (20,598))  # cima
        tela.blit(voltar_borda, (20,602))  # baixo

        # DESENHA O TEXTO PRINCIPAL

        tela.blit(voltar, (20,600))

        pygame.display.flip()


        # =========================
        # EVENTOS
        # =========================

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    pygame.event.clear()

                    return
# =========================
# MENU DE DESEMPENHO
# =========================

def tela_desempenho(
        tela,
        clock,
        fonte,
        fonte_titulo,
        largura,
        altura,
        acertos_perfeitos,
        cedo,
        tarde,
        erros_tempo,
        dados_tempo
    ):

    while True:

        clock.tick(60)

        fundo(tela, largura, altura)

        # =========================
        # CALCULOS
        # =========================

        total = (
            acertos_perfeitos
            + cedo
            + tarde
            + erros_tempo
        )

        precisao = (
            (acertos_perfeitos / total) * 100
            if total > 0 else 0
        )

        if precisao > 80:

            avaliacao = "EXCELENTE"

        elif precisao > 60:

            avaliacao = "BOM"

        else:

            avaliacao = "PRECISA TREINAR"

        # =========================
        # TITULO
        # =========================

        titulo = fonte_titulo.render(
            "DESEMPENHO",
            True,
            AZUL
        )

        tela.blit(titulo, (260,50))

        # =========================
        # INFORMACOES
        # =========================

        tela.blit(
            fonte.render(
                f"Perfeitos: {acertos_perfeitos}",
                True,
                VERDE
            ),
            (100,220)
        )

        tela.blit(
            fonte.render(
                f"Cedo: {cedo}",
                True,
                AMARELO
            ),
            (100,280)
        )

        tela.blit(
            fonte.render(
                f"Tarde: {tarde}",
                True,
                LARANJA
            ),
            (100,340)
        )

        tela.blit(
            fonte.render(
                f"Erros: {erros_tempo}",
                True,
                VERMELHO
            ),
            (100,400)
        )

        tela.blit(
            fonte.render(
                f"Precisao: {precisao:.1f}%",
                True,
                BRANCO
            ),
            (100,480)
        )

        tela.blit(
            fonte.render(
                f"Avaliacao: {avaliacao}",
                True,
                AZUL
            ),
            (100,540)
        )

        # =========================
        # MENU LATERAL
        # =========================

        pygame.draw.rect(
            tela,
            (20,20,35),
            (700,180,300,300),
            border_radius=20
        )

        menu_titulo = fonte.render(
            "AVALIACOES",
            True,
            BRANCO
        )

        tela.blit(menu_titulo, (770,210))

        opcao1 = fonte.render(
            "1 - Precisao Temporal",
            True,
            AZUL
        )

        tela.blit(opcao1, (730,300))

        # futuras opcoes

        opcao2 = fonte.render(
            "2 - Ritmo",
            True,
            (120,120,120)
        )

        tela.blit(opcao2, (730,360))

        opcao3 = fonte.render(
            "3 - Evolucao",
            True,
            (120,120,120)
        )

        tela.blit(opcao3, (730,420))

        # =========================
        # VOLTAR
        # =========================

        voltar = fonte.render(
            "ESC para voltar",
            True,
            BRANCO
        )

        tela.blit(voltar, (80,620))

        pygame.display.flip()

        # =========================
        # EVENTOS
        # =========================

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:

                # VOLTAR

                if evento.key == pygame.K_ESCAPE:

                    pygame.event.clear()

                    return

                # GRAFICO TEMPORAL

                if evento.key == pygame.K_1:

                    tela_grafico_temporal(
                        tela,
                        clock,
                        fonte,
                        fonte_titulo,
                        largura,
                        altura,
                        dados_tempo
                    )