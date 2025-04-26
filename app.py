from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    cidade = request.args.get("cidade", "São Paulo")
    print("Cidade buscada:", cidade)

    API_KEY = "fb019c1d1d18980deecce5e1e860f545"

    url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt"
    url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={API_KEY}&units=metric&lang=pt"

    resposta_clima = requests.get(url_clima).json()
    resposta_previsao = requests.get(url_previsao).json()

    if resposta_clima.get("cod") != 200 or resposta_previsao.get("cod") != "200":
        print("Erro:", resposta_clima.get("message"), resposta_previsao.get("message"))
        return render_template("index.html", erro=True)

    clima = {
        "cidade": resposta_clima["name"],
        "pais": resposta_clima["sys"]["country"],
        "temp": resposta_clima["main"]["temp"],
        "max": resposta_clima["main"]["temp_max"],
        "min": resposta_clima["main"]["temp_min"],
        "umidade": resposta_clima["main"]["humidity"],
        "vento": resposta_clima["wind"]["speed"] * 3.6,
        "descricao": resposta_clima["weather"][0]["description"].capitalize(),
        "icone": resposta_clima["weather"][0]["icon"]
    }

    agrupado = defaultdict(list)
    for item in resposta_previsao["list"]:
        dia = item["dt_txt"].split()[0]
        agrupado[dia].append(item)

    previsao_por_dia = []
    for dia, blocos in agrupado.items():
        temperaturas = [b["main"]["temp"] for b in blocos]
        icones = [b["weather"][0]["icon"] for b in blocos]
        icone_mais_comum = max(set(icones), key=icones.count)
        previsao_por_dia.append({
            "dia": datetime.strptime(dia, "%Y-%m-%d").strftime("%d/%m"),
            "temp_max": max(temperaturas),
            "temp_min": min(temperaturas),
            "icone": icone_mais_comum
        })

    dados_previsao = resposta_previsao["list"][:8]

    return render_template(
        "index.html",
        clima=clima,
        previsao=previsao_por_dia,
        dadosPrevisao=dados_previsao,
        erro=False
    )

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/noticias")
def noticias():
    return render_template("noticias.html")

if __name__ == "__main__":
    app.run(debug=True)
