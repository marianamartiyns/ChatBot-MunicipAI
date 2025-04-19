
import json
import os

# Caminho do arquivo
CAMINHO_JSON = os.path.abspath("backend/data/houer.json")

# Carrega o conteúdo do JSON
with open(CAMINHO_JSON, encoding="utf-8") as f:
    dados = json.load(f)

def consultar_houer(pergunta: str) -> str:
    pergunta = pergunta.lower()

    if "missão" in pergunta:
        return f"Missão da Houer: {dados['empresa']['missao']}"
    if "visão" in pergunta:
        return f"Visão da Houer: {dados['empresa']['visao']}"
    if "propósito" in pergunta:
        return f"Propósito da Houer: {dados['empresa']['proposito']}"
    if "valores" in pergunta:
        return "Valores da Houer: " + ", ".join(dados["empresa"]["valores"])
    if "certificações" in pergunta or "certificacao" in pergunta:
        return "Certificações da Houer: " + ", ".join(dados["empresa"].get("certificacoes", []))
    if "serviços" in pergunta or "atua" in pergunta or "oferece" in pergunta:
        return "A Houer oferece serviços como: " + ", ".join([s["nome"] for s in dados["servicos"]])
    if "empresas do grupo" in pergunta or "subsidiárias" or "subsidiarias" in pergunta or "outras empresas" in pergunta:
        return "Empresas do Grupo Houer:\n" + "\n".join([
            f"- {e['nome']}: {e['descricao']}" for e in dados["empresas_do_grupo"]
        ])
    if "engenharia" in pergunta:
        return "🏗️ Houer Engenharia: " + dados["empresas_do_grupo"][1]["descricao"]
    if "tecnologia" in pergunta:
        return "💻 Houer Tecnologia: " + dados["empresas_do_grupo"][2]["descricao"]
    if "concessões" in pergunta:
        return "📑 Houer Concessões: " + dados["empresas_do_grupo"][0]["descricao"]
    if "cultura" in pergunta or "ética" in pergunta or "integridade" in pergunta:
        return "Cultura e Ética Houer: " + dados["cultura"]["etica_integridade"]
    if "compliance" in pergunta or "governança" in pergunta:
        return "Compliance Houer: " + dados["cultura"]["compliance"]
    if "escritórios" in pergunta or "localizações" in pergunta:
        return "Escritórios da Houer: " + ", ".join(dados["escritorios"])
    if "contato" in pergunta or "telefone" in pergunta or "email" in pergunta:
        c = dados["contato"]
        return f"Telefone: {c['telefone']} | ✉️ Email: {c['email']}"
    if "endereç" in pergunta:
        return "Endereço: " + dados["contato"]["endereco"]
    if "áreas de atuação" in pergunta or "atua em quais áreas" in pergunta or "segmentos" in pergunta:
        return "Áreas de Atuação: " + ", ".join(dados["areas_atuacao"])

    # 🔁 Fallback inteligente — descrição geral
    if "houer" in pergunta or "empresa" in pergunta or "quem são vocês" in pergunta or "o que fazem" in pergunta:
        return (
            f"A Houer é um grupo especializado em infraestrutura, com foco em concessões, engenharia e tecnologia. "
            f"Ela atua em diversas áreas como: {', '.join(dados['areas_atuacao'][:4])}... "
            f"Sua missão é: *{dados['empresa']['missao']}*."
        )

    return "Não encontrei essa informação nos dados institucionais da Houer."


