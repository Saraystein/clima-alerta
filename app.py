from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import time

app = Flask(__name__)

# ================== Função: Buscar Clima ==================

def buscar_clima(cidade):
    api_key = "fb019c1d1d18980deecce5e1e860f545"
    url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt"
    url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={api_key}&units=metric&lang=pt"

    resp_clima = requests.get(url_clima).json()
    resp_previsao = requests.get(url_previsao).json()

    if resp_clima.get("cod") != 200 or resp_previsao.get("cod") != "200":
        return None, None, None

    clima = {
        "cidade": resp_clima["name"],
        "pais": resp_clima["sys"]["country"],
        "temp": round(resp_clima["main"]["temp"]),
        "min": round(resp_clima["main"]["temp_min"]),
        "max": round(resp_clima["main"]["temp_max"]),
        "descricao": resp_clima["weather"][0]["description"].capitalize(),
        "icone": resp_clima["weather"][0]["icon"],
        "umidade": resp_clima["main"]["humidity"],
        "vento": resp_clima["wind"]["speed"]
    }

    dados_previsao = resp_previsao["list"]
    previsao_resumida = []
    dias_vistos = set()

    for item in dados_previsao:
        dia_iso = item["dt_txt"].split(" ")[0]
        if dia_iso not in dias_vistos:
            dias_vistos.add(dia_iso)
            dia_formatado = datetime.strptime(dia_iso, "%Y-%m-%d").strftime("%d/%m")
            previsao_resumida.append({
                "dia": dia_formatado,
                "icone": item["weather"][0]["icon"],
                "temp_min": item["main"]["temp_min"],
                "temp_max": item["main"]["temp_max"]
            })

    return clima, previsao_resumida, dados_previsao

# ================== Função: Buscar Notícias ==================

def buscar_noticias(cidade):
    chave = "5d392c40a9fb4e4f90404c42d613e30d"
    url = "https://newsapi.org/v2/everything"

    termos = f"{cidade} clima OR enchente OR seca OR meio ambiente OR poluição"
    params = {
        "q": termos,
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": chave
    }

    resposta = requests.get(url, params=params).json()
    return resposta.get("articles", [])

# ================== Rotas ==================

@app.route("/")
def index():
    cidade = request.args.get("cidade", "São Paulo")
    clima, previsao, dados_previsao = buscar_clima(cidade)

    if not clima:
        return render_template("index.html", erro=True)

    resposta = make_response(render_template("index.html", clima=clima, previsao=previsao, dadosPrevisao=dados_previsao))
    resposta.set_cookie("ultima_cidade", cidade)
    return resposta

@app.route("/noticias")
def noticias():
    cidade = request.args.get("cidade") or request.cookies.get("ultima_cidade") or "Brasil"

    termo_busca = f"clima OR meio ambiente OR poluição OR chuva {cidade}"
    chave = "5d392c40a9fb4e4f90404c42d613e30d"
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": termo_busca,
        "language": "pt",
        "sortBy": "publishedAt",
        "apiKey": chave,
        "pageSize": 10
    }

    resp = requests.get(url, params=params).json()
    artigos = resp.get("articles", [])

    response = render_template("noticias.html", cidade=cidade, artigos=artigos)
    resp_obj = app.make_response(response)
    resp_obj.set_cookie("ultima_cidade", cidade)

    return resp_obj

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/alerta", methods=["GET", "POST"])
def alerta():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        cidade = request.form.get("cidade")

        # Aqui os dados podem ser salvos em um arquivo ou banco
        with open("usuarios_alerta.txt", "a", encoding="utf-8") as f:
            f.write(f"{nome},{email},{cidade}\n")

        # Envia o e-mail de confirmação
        enviar_email_confirmacao(nome, email, cidade)

        return render_template("confirmacao.html", nome=nome, cidade=cidade)
    return render_template("alerta.html")

def enviar_email_confirmacao(nome, email, cidade):
    remetente = "climaticaconexao@gmail.com"        # <-- altere para seu e-mail real
    senha = "tcaz xuvo fywm jfnc"                       # <-- use app password se for Gmail
    destinatario = email

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Confirmação de Alerta Climático"

    corpo = f"Olá, {nome}!\n\nVocê se cadastrou para receber alertas do clima em {cidade}."
    msg.attach(MIMEText(corpo, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.send_message(msg)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# ================== Run ==================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway define essa variável
    app.run(debug=True, host="0.0.0.0", port=port)
