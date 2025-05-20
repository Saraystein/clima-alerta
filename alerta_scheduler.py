import time
import schedule
import requests
import threading
from flask import Flask, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração do Flask-Mail para usar o SMTP do Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")       # Ex.: climaticaconexao@gmail.com
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")       # Senha de aplicativo gerada pelo Google
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

# CONFIGURAÇÕES
API_KEY = os.getenv("OPENWEATHER_API_KEY", "fb019c1d1d18980deecce5e1e860f545")

def carregar_usuarios():
    """
    Lê o arquivo 'usuarios_alerta.txt' e retorna uma lista de [nome, email, cidade].
    Cada linha deve ter o formato: Nome,email,cidade
    """
    try:
        with open('usuarios_alerta.txt', 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        return [linha.strip().split(',') for linha in linhas if linha.strip()]
    except FileNotFoundError:
        return []

def buscar_clima(cidade):
    """
    Consulta a API do OpenWeather e retorna um dicionário com a temperatura 
    e a descrição do clima para a cidade informada.
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br&units=metric'
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            return {
                'temp': dados['main']['temp'],
                'descricao': dados['weather'][0]['description']
            }
    except Exception as e:
        print(f"Erro ao buscar clima para {cidade}: {e}")
    return None

def send_async_email(app, msg):
    """
    Envia o e-mail de forma assíncrona utilizando o application context.
    """
    with app.app_context():
        try:
            mail.send(msg)
            print(f"E-mail enviado para {msg.recipients[0]}")
        except Exception as e:
            print(f"Erro ao enviar e-mail para {msg.recipients[0]}: {e}")

def enviar_email_update(nome, email, cidade, clima):
    """
    Envia um e-mail de atualização normal com o template de update.
    É necessário criar o template 'alert_email_update.html' na pasta templates.
    """
    with app.app_context():
        html = render_template(
            'alert_email_update.html',
            nome=nome,
            cidade=cidade,
            temp=clima['temp'],
            descricao=clima['descricao']
        )
        assunto = f"Atualização de Clima em {cidade}"
        msg = Message(subject=assunto, recipients=[email], html=html)
    threading.Thread(target=send_async_email, args=(app, msg), daemon=True).start()

def enviar_email_extremo(nome, email, cidade, clima):
    """
    Envia um e-mail de alerta extremo com base em condições climáticas específicas.
    É necessário criar o template 'alert_email_extremo.html' na pasta templates.
    """
    with app.app_context():
        temp = clima['temp']
        descricao = clima['descricao'].lower()
        alerta_text = ""
        # Mensagens personalizadas conforme a condição:
        if temp <= 20:
            alerta_text = "Tempo extremamente frio! Use várias camadas de roupas, mantenha-se aquecido e fique atento a geadas."
        elif temp >= 30:
            alerta_text = "Calor extremo! Lembre-se de se hidratar, use roupas leves e evite exposição prolongada ao sol."
        elif "chuva" in descricao:
            alerta_text = "Chuva intensa! Não esqueça seu guarda-chuva e redobre os cuidados com enchentes."
        elif "tempestade" in descricao or "storm" in descricao:
            alerta_text = "Tempestade em andamento! Procure abrigo seguro e evite áreas abertas."
        elif "neve" in descricao:
            alerta_text = "Condições de neve detectadas! Use calçados adequados e tenha cuidado com superfícies escorregadias."
        else:
            alerta_text = "Condições climáticas extremas detectadas. Fique atento e tome as medidas necessárias."

        html = render_template(
            'alert_email_extremo.html',
            nome=nome,
            cidade=cidade,
            temp=temp,
            descricao=clima['descricao'],
            alerta_text=alerta_text
        )
        assunto = f"⚠️ Alerta Climático Extremo em {cidade}"
        msg = Message(subject=assunto, recipients=[email], html=html)
    threading.Thread(target=send_async_email, args=(app, msg), daemon=True).start()

def is_extreme(clima):
    """
    Retorna True se as condições climáticas forem consideradas extremas.
    Aqui, definimos como extremas: temperatura <= -10, temperatura >= 35
    ou se a descrição contém palavras-chaves como 'chuva', 'tempestade', 'neve' ou 'storm'.
    """
    temp = clima['temp']
    descricao = clima['descricao'].lower()
    return (temp <= 20 or temp >= 30 or 
            "chuva" in descricao or 
            "tempestade" in descricao or 
            "neve" in descricao or
            "storm" in descricao)

def checar_alertas():
    """
    Para cada usuário cadastrado, busca o clima e:
      1. Envia um e-mail de atualização normal.
      2. Se as condições forem extremas, envia um alerta adicional.
    """
    usuarios = carregar_usuarios()
    for nome, email, cidade in usuarios:
        clima = buscar_clima(cidade)
        if not clima:
            continue
        # Envia a atualização normal sempre
        enviar_email_update(nome, email, cidade, clima)
        # Se as condições forem extremas, envia alerta extra
        if is_extreme(clima):
            enviar_email_extremo(nome, email, cidade, clima)

if __name__ == "__main__":
    # Executa a verificação de alertas imediatamente
    checar_alertas()

    # Agenda a verificação para executar a cada hora
    schedule.every().hour.do(checar_alertas)

    print("⏳ Sistema de alertas rodando...")
    while True:
        schedule.run_pending()
        time.sleep(60)
