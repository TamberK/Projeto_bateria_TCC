import json
import os

ARQUIVO_SCORE = "scores.json"

def salvar_score(nome, pontos):
    dados = []

    if os.path.exists(ARQUIVO_SCORE):
        with open(ARQUIVO_SCORE, "r") as f:
            dados = json.load(f)

    dados.append({"nome": nome, "score": pontos})

    dados = sorted(dados, key=lambda x: x["score"], reverse=True)[:10]

    with open(ARQUIVO_SCORE, "w") as f:
        json.dump(dados, f, indent=4)

def carregar_scores():
    if os.path.exists(ARQUIVO_SCORE):
        with open(ARQUIVO_SCORE, "r") as f:
            return json.load(f)
    return []