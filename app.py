from flask import Flask, render_template, request, redirect, url_for
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

@app.route("/")
def index():
    cidade = request.args.get("cidade", "São Paulo")
    clima, previsao, dados_previsao = buscar_clima(cidade)
    if not clima:
        return render_template("index.html", erro=True)
    return render_template("index.html", clima=clima, previsao=previsao, dadosPrevisao=dados_previsao)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/noticias")
def noticias():
    return render_template("noticias.html")

@app.route("/alerta")
def alerta():
    return render_template("alerta.html")

if __name__ == "__main__":
    app.run(debug=True)
