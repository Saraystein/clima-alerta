import time
import schedule
import requests
import smtplib
from email.mime.text import MIMEText

# CONFIGURAÇÕES
API_KEY = 'fb019c1d1d18980deecce5e1e860f545'
EMAIL_REMETENTE = 'climaticaconexao@gmail.com'
SENHA = 'tcaz xuvo fywm jfnc'

def carregar_usuarios():
    with open('usuarios_alerta.txt', 'r') as f:
        linhas = f.readlines()
    return [linha.strip().split(',') for linha in linhas]

def buscar_clima(cidade):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br&units=metric'
    resp = requests.get(url)
    if resp.status_code == 200:
        dados = resp.json()
        return {
            'temp': dados['main']['temp'],
            'descricao': dados['weather'][0]['description']
        }
    return None

def enviar_email(destinatario, assunto, mensagem):
    msg = MIMEText(mensagem)
    msg['Subject'] = assunto
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA)
        smtp.send_message(msg)

def checar_alertas():
    usuarios = carregar_usuarios()
    for nome, email, cidade in usuarios:
        clima = buscar_clima(cidade)
        if not clima:
            continue

        # Email padrão por hora
        msg = f"Olá {nome},\n\nAtualização do clima em {cidade}:\nTemperatura: {clima['temp']}°C\nCondição: {clima['descricao']}."
        enviar_email(email, f"Clima em {cidade}", msg)

        # Alerta imediato
        temp = clima['temp']
        descricao = clima['descricao'].lower()
        if temp > 35 or temp < 20 or 'chuva' in descricao or 'rain' in descricao or 'storm' in descricao:
            alerta = f"⚠️ Alerta de clima em {cidade}!\nTemperatura: {temp}°C\nCondição: {descricao}"
            enviar_email(email, f"⚠️ Alerta em {cidade}", alerta)

# Execução
if __name__ == "__main__":
    checar_alertas()  # Executa uma vez ao iniciar
    schedule.every().hour.do(checar_alertas)

    print("⏳ Sistema de alertas rodando...")

    while True:
        schedule.run_pending()
        time.sleep(60)
