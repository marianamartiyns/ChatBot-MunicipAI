import json
import os
import unicodedata
import re

# Caminho do arquivo
CAMINHO_JSON = os.path.abspath("backend/data/houer.json")

# Carrega o conteúdo do JSON
with open(CAMINHO_JSON, encoding="utf-8") as f:
    dados = json.load(f)

# Função auxiliar de normalização
def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.lower().strip()

# Função principal
def consultar_houer(pergunta: str) -> str:
    pergunta_norm = normalizar_texto(pergunta)

    if "missao" in pergunta_norm:
        return f"Missão da Houer: {dados['empresa']['missao']}"
    if "visao" in pergunta_norm:
        return f"Visão da Houer: {dados['empresa']['visao']}"
    if "proposito" in pergunta_norm:
        return f"Propósito da Houer: {dados['empresa']['proposito']}"
    if "valores" in pergunta_norm:
        return "Valores da Houer: " + ", ".join(dados["empresa"]["valores"])
    if "certificacao" in pergunta_norm or "certificacoes" in pergunta_norm:
        return "Certificações da Houer: " + ", ".join(dados["empresa"].get("certificacoes", []))
    
    if any(p in pergunta_norm for p in ["servico", "atua", "oferece"]):
        return "A Houer oferece serviços como: " + ", ".join([s["nome"] for s in dados["servicos"]])

    # Verificar se a pergunta corresponde a algum serviço específico
    for servico in dados["servicos"]:
        nome_normalizado = normalizar_texto(servico["nome"])
        if nome_normalizado in pergunta_norm:
            return f"{servico['nome']}: {servico['descricao']}"

    if any(p in pergunta_norm for p in ["empresas do grupo", "subsidiaria", "outras empresas"]):
        return "Empresas do Grupo Houer:\n" + "\n".join([
            f"- {e['nome']}: {e['descricao']}" for e in dados["empresas_do_grupo"]
        ])
    if "engenharia" in pergunta_norm:
        return "🏗️ Houer Engenharia: " + dados["empresas_do_grupo"][1]["descricao"]
    if "tecnologia" in pergunta_norm:
        return "💻 Houer Tecnologia: " + dados["empresas_do_grupo"][2]["descricao"]
    if "concessao" in pergunta_norm:
        return "📑 Houer Concessões: " + dados["empresas_do_grupo"][0]["descricao"]
    
    if any(p in pergunta_norm for p in ["cultura", "etica", "integridade"]):
        return "Cultura e Ética Houer: " + dados["cultura"]["etica_integridade"]
    if "compliance" in pergunta_norm or "governanca" in pergunta_norm:
        return "Compliance Houer: " + dados["cultura"]["compliance"]
    
    if any(p in pergunta_norm for p in ["escritorio", "localizacao", "unidade"]):
        return "Escritórios da Houer: " + ", ".join(dados["escritorios"])
    if any(p in pergunta_norm for p in ["contato", "telefone", "email"]):
        c = dados["contato"]
        return f"Telefone: {c['telefone']} | ✉️ Email: {c['email']}"
    if "endereco" in pergunta_norm:
        return "Endereço: " + dados["contato"]["endereco"]
    
    if any(p in pergunta_norm for p in ["area de atuacao", "atua em quais areas", "segmento"]):
        return "Áreas de Atuação: " + ", ".join(dados["areas_atuacao"])
    
    if "parceiro" in pergunta_norm:
        return "Alguns dos parceiros estratégicos da Houer incluem: " + ", ".join(dados["parceiros"])
    
    if "linkedin" in pergunta_norm:
        return "LinkedIn oficial da Houer: " + dados["redes_sociais"]["linkedin"]
    if "instagram" in pergunta_norm:
        return "Instagram oficial da Houer: " + dados["redes_sociais"]["instagram"]

    # 🔁 Fallback inteligente
    if any(p in pergunta_norm for p in ["houer", "empresa", "quem sao voces", "o que fazem"]):
        return (
            f"A Houer é um grupo especializado em infraestrutura, com foco em concessões, engenharia e tecnologia. "
            f"Ela atua em diversas áreas como: {', '.join(dados['areas_atuacao'][:4])}... "
            f"Sua missão é: *{dados['empresa']['missao']}*."
        )

    return "Não encontrei essa informação nos dados institucionais da Houer."
