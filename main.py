import os
import sys
import subprocess
import pygame

# Adiciona a pasta 'Telas' ao sys.path para garantir a resolução dos módulos importados pelo menu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TELAS_DIR = os.path.join(BASE_DIR, "Telas")
if TELAS_DIR not in sys.path:
    sys.path.insert(0, TELAS_DIR)

from menu import menu

def tela_escolha_nivel(tela, clock, nome_jogador):
    LARGURA, ALTURA = 1100, 650
    fonte_titulo = pygame.font.SysFont("arial", 60, bold=True)
    fonte_sub = pygame.font.SysFont("arial", 28, bold=True)
    fonte_opcoes = pygame.font.SysFont("arial", 26, bold=True)

    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)
    AMARELO = (255, 220, 0)
    AZUL = (0, 170, 255)
    VERDE = (0, 255, 120)
    CINZA = (25, 25, 40)
    BORDA_CINZA = (70, 70, 110)

    def fundo():
        for y in range(ALTURA):
            cor = (5, 5 + y // 20, 15 + y // 18)
            pygame.draw.line(tela, cor, (0, y), (LARGURA, y))

    def texto_estilizado(txt, fonte, cor, borda, sombra, x, y):
        render = fonte.render(txt, True, cor)
        borda_render = fonte.render(txt, True, borda)
        sombra_render = fonte.render(txt, True, sombra)
        tela.blit(sombra_render, (x + 4, y + 4))
        tela.blit(borda_render, (x + 2, y + 2))
        tela.blit(render, (x, y))

    escolha = None

    while escolha is None:
        clock.tick(60)
        fundo()

        # Barra Superior
        barra = pygame.Surface((LARGURA, 90), pygame.SRCALPHA)
        barra.fill((15, 15, 25, 220))
        tela.blit(barra, (0, 0))
        pygame.draw.line(tela, (60, 60, 90), (0, 90), (LARGURA, 90), 2)

        # Título
        titulo = "ESCOLHA O NÍVEL"
        largura_t = fonte_titulo.size(titulo)[0]
        texto_estilizado(titulo, fonte_titulo, AMARELO, PRETO, BRANCO, (LARGURA - largura_t) // 2, 90)

        # Boas-vindas ao Jogador
        texto_jogador = f"Bem-vindo(a), {nome_jogador}!"
        largura_j = fonte_sub.size(texto_jogador)[0]
        texto_estilizado(texto_jogador, fonte_sub, AZUL, PRETO, PRETO, (LARGURA - largura_j) // 2, 190)

        # Painel de Opções
        x_box = (LARGURA - 500) // 2

        # Opção 1: Nível 1
        pygame.draw.rect(tela, CINZA, (x_box, 260, 500, 65), border_radius=15)
        pygame.draw.rect(tela, BORDA_CINZA, (x_box, 260, 500, 65), 2, border_radius=15)
        texto_estilizado("1 - Nível 1 (Bateria Hero)", fonte_opcoes, VERDE, PRETO, PRETO, x_box + 30, 278)

        # Opção 2: Nível 2
        pygame.draw.rect(tela, CINZA, (x_box, 350, 500, 65), border_radius=15)
        pygame.draw.rect(tela, BORDA_CINZA, (x_box, 350, 500, 65), 2, border_radius=15)
        texto_estilizado("2 - Nível 2 (Partitura)", fonte_opcoes, AZUL, PRETO, PRETO, x_box + 30, 368)

        # Opção ESC: Sair
        pygame.draw.rect(tela, CINZA, (x_box, 440, 500, 65), border_radius=15)
        pygame.draw.rect(tela, BORDA_CINZA, (x_box, 440, 500, 65), 2, border_radius=15)
        texto_estilizado("ESC - Sair", fonte_opcoes, BRANCO, PRETO, PRETO, x_box + 30, 458)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    escolha = "nivel1"
                elif evento.key == pygame.K_2:
                    escolha = "nivel2"
                elif evento.key == pygame.K_ESCAPE:
                    escolha = "sair"

    return escolha

def main():
    # 1. Obter nome do jogador utilizando o menu de Telas/menu.py
    nome_jogador = menu()

    if not nome_jogador:
        return

    # 2. Inicializar contexto Pygame para a seleção de nível
    pygame.init()
    LARGURA, ALTURA = 1100, 650
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Drum Trainer PRO - Escolha o Nível")
    clock = pygame.time.Clock()

    # 3. Loop de Seleção de Nível
    while True:
        opcao = tela_escolha_nivel(tela, clock, nome_jogador)

        if opcao == "nivel1":
            path_nivel1 = os.path.join(TELAS_DIR, "jogonivel1.py")
            subprocess.run([sys.executable, path_nivel1], cwd=TELAS_DIR)
            # Restaura a tela após encerramento do nível
            pygame.init()
            tela = pygame.display.set_mode((LARGURA, ALTURA))
            pygame.display.set_caption("Drum Trainer PRO - Escolha o Nível")

        elif opcao == "nivel2":
            path_nivel2 = os.path.join(TELAS_DIR, "jogonivel2partitura.py")
            subprocess.run([sys.executable, path_nivel2], cwd=TELAS_DIR)
            # Restaura a tela após encerramento do nível
            pygame.init()
            tela = pygame.display.set_mode((LARGURA, ALTURA))
            pygame.display.set_caption("Drum Trainer PRO - Escolha o Nível")

        elif opcao == "sair":
            break

    pygame.quit()

if __name__ == "__main__":
    main()