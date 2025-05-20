from flask import Flask, render_template, request, make_response
import requests
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from datetime import datetime
import threading

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do Flask-Mail para utilizar o SMTP do Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")         # seu email: ex. seuemail@gmail.com
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")         # senha do app ou a senha configurada
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")   # padrão de remetente

mail = Mail(app)

# ================== Função: Obter Cidade ==================
def obter_cidade():
    return request.args.get("cidade") or request.cookies.get("ultima_cidade") or "Brasil"

# ================== Função: Buscar Clima ==================
def buscar_clima(cidade):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt"
        url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={api_key}&units=metric&lang=pt"

        r_clima = requests.get(url_clima, timeout=10)
        r_previsao = requests.get(url_previsao, timeout=10)
        r_clima.raise_for_status()
        r_previsao.raise_for_status()

        resp_clima = r_clima.json()
        resp_previsao = r_previsao.json()

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

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar clima: {e}")
        return None, None, None

# ================== Função: Buscar Notícias ==================
def buscar_noticias(cidade):
    try:
        news_key = os.getenv("NEWSAPI_KEY")
        url = "https://newsapi.org/v2/everything"
        termos = f"{cidade} clima OR enchente OR seca OR meio ambiente OR poluição"
        params = {
            "q": termos,
            "language": "pt",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": news_key
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("articles", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar notícias: {e}")
        return []

# ================== Função: Envio Assíncrono de E-mails ==================
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

def enviar_email_confirmacao(nome, email, cidade):
    assunto = "Confirmação de Alerta Climático"
    corpo = f"Olá, {nome}!\n\nVocê se cadastrou para receber alertas do clima em {cidade}."
    msg = Message(subject=assunto, recipients=[email], body=corpo)
    # Dispara o envio do e-mail em uma thread separada para não bloquear a resposta
    threading.Thread(target=send_async_email, args=(app, msg), daemon=True).start()

# ================== Rotas ==================
@app.route("/")
def index():
    cidade = request.args.get("cidade") or "São Paulo"
    clima, previsao, dados_previsao = buscar_clima(cidade)
    if not clima:
        return render_template("index.html", erro=True)
    resposta = make_response(render_template("index.html", clima=clima, previsao=previsao, dadosPrevisao=dados_previsao))
    resposta.set_cookie("ultima_cidade", cidade)
    return resposta

@app.route("/noticias")
def noticias():
    cidade = obter_cidade()
    artigos = buscar_noticias(cidade)
    resposta = make_response(render_template("noticias.html", cidade=cidade, artigos=artigos))
    resposta.set_cookie("ultima_cidade", cidade)
    return resposta

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/alerta", methods=["GET", "POST"])
def alerta():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        cidade = request.form.get("cidade")

        # Armazena os dados do usuário em um arquivo para alertas
        with open("usuarios_alerta.txt", "a", encoding="utf-8") as f:
            f.write(f"{nome},{email},{cidade}\n")

        # Envia o e-mail de confirmação de forma assíncrona
        enviar_email_confirmacao(nome, email, cidade)
        return render_template("confirmacao.html", nome=nome, cidade=cidade)
    return render_template("alerta.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
