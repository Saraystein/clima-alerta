from flask import Flask, render_template, request, session
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secreto"

# APIs
OPENWEATHER_API_KEY = "fb019c1d1d18980deecce5e1e860f545"
NEWS_API_KEY = "5d392c40a9fb4e4f90404c42d613e30d"

@app.route("/")
def index():
    cidade = request.args.get("cidade", "São Paulo")
    session["cidade_atual"] = cidade

    # URLs da previsão do tempo
    url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt"
    url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt"

    resposta_clima = requests.get(url_clima).json()
    resposta_previsao = requests.get(url_previsao).json()

    if resposta_clima.get("cod") != 200 or resposta_previsao.get("cod") != "200":
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

    # Organizar a previsão
    agrupado = defaultdict(list)
    for item in resposta_previsao["list"]:
        dia = item["dt_txt"].split()[0]
        agrupado[dia].append(item)

    previsao_por_dia = []
    hoje = datetime.now().date()

    for i in range(5):  # hoje + 4 dias
        dia_atual = hoje + timedelta(days=i)
        dia_str = dia_atual.strftime("%Y-%m-%d")

        blocos = agrupado.get(dia_str)
        if blocos:
            temperaturas = [b["main"]["temp"] for b in blocos]
            icones = [b["weather"][0]["icon"] for b in blocos]
            icone_mais_comum = max(set(icones), key=icones.count)

            previsao_por_dia.append({
                "dia": dia_atual.strftime("%d/%m"),
                "temp_max": max(temperaturas),
                "temp_min": min(temperaturas),
                "icone": icone_mais_comum
            })

    dados_previsao = resposta_previsao["list"]

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
    cidade = session.get("cidade_atual", "São Paulo")
    termo_busca = f"clima {cidade}"

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": termo_busca,
        "language": "pt",
        "apiKey": NEWS_API_KEY,
        "pageSize": 10,
        "sortBy": "publishedAt"
    }

    resposta = requests.get(url, params=params).json()
    noticias = resposta.get("articles", [])

    return render_template("noticias.html", cidade=cidade, noticias=noticias)

if __name__ == "__main__":
    app.run(debug=True)
