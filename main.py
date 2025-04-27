"""
Módulo para exibir um calendário com suporte ao calendário Hijri e
funcionalidades relacionadas ao Alcorão.
"""

import os
import random
import calendar
import requests
import logging
from flask import Flask, render_template, request, send_file, jsonify
from calendario_isla import gregorian_to_hijri
from mensagens import obter_mensagem
from datetime import datetime


# Configuração do Flask
app = Flask(__name__)

# Configuração do diretório para armazenar os arquivos do Alcorão
ALCORAO_ASSETS = "assets"
os.makedirs(ALCORAO_ASSETS, exist_ok=True)

CAMINHO_ALCORAO = os.path.join(os.path.dirname(__file__), 'static', 'assets', 'alcoraoSamir.txt')
with open(CAMINHO_ALCORAO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()


# Funções auxiliares
def carregar_alcorao_texto():
    """
    Carrega o texto do Alcorão a partir de um arquivo.
    """
    texto_path = os.path.join(os.path.dirname(__file__), "static", "assets", "alcoraoSamir.txt")
    if os.path.exists(texto_path):
        with open(texto_path, "r", encoding="utf-8") as f:
            return f.readlines()
    return []


def buscar_frase_alcorao():
    """
    Busca uma frase aleatória de até 12 linhas do texto do Alcorão,
    começando pela linha que contém a palavra 'SURATA'.
    """
    linhas = carregar_alcorao_texto()
    if not linhas:
        return "O texto do Alcorão não está disponível."

    # Encontrar todos os índices onde aparece 'SURATA'
    indices_surata = [i for i, linha in enumerate(linhas) if "SURATA" in linha.upper()]
    if not indices_surata:
        return "Não foi encontrada uma referência a 'SURATA' no texto do Alcorão."

    # Escolher aleatoriamente um dos índices encontrados
    inicio = random.choice(indices_surata)
    fim = min(inicio + 16, len(linhas))  # Agora pega até 12 linhas
    trecho = [linhas[j].strip() for j in range(inicio, fim)]

    if trecho:
        trecho[-1] = trecho[-1] + " ..."
        return " ".join(trecho)
    else:
        return "Não foi possível extrair a frase do Alcorão."


def get_prayer_times(city, country, day, month, year, method=7):
    date_str = f"{day:02d}-{month:02d}-{year}"
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}&date={date_str}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == 200:
            return data["data"]["timings"]
    except Exception as e:
        logging.error(f"Erro ao buscar horários de oração: {e}")
    return None


def get_prayer_times_by_coords(latitude, longitude, day, month, year, method=7):
    date_str = f"{day:02d}-{month:02d}-{year}"
    url = f"https://api.aladhan.com/v1/timings/{date_str}?latitude={latitude}&longitude={longitude}&method={method}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == 200:
            return data["data"]["timings"]
    except Exception as e:
        logging.error(f"Erro ao buscar horários de oração: {e}")
    return None


# Rotas do Flask
@app.route('/')
def index():
    hoje = datetime.today()
    return render_template(
        'index.html',
        current_year=hoje.year,
        current_month=hoje.month
    )


@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    """
    Exibe o calendário com suporte ao calendário Hijri.
    """
    year = int(request.args.get('year', 2025))
    month = int(request.args.get('month', 1))

    cal = calendar.Calendar()
    days = list(cal.itermonthdays(year, month))
    weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

    hijri_dates = [
        gregorian_to_hijri(year, month, day) if day != 0 else None
        for day in days
    ]

    mensagem_oracoes = ""
    if request.method == "POST":
        city = request.form.get("city")
        country = request.form.get("country")
        method = int(request.form.get("method", 7))
        if city and country:
            prayer_times = get_prayer_times(city, country, 1, month, year, method)
            if prayer_times:
                mensagem_oracoes = (
                    f"Fajr: {prayer_times['Fajr']} | Nascer do Sol: {prayer_times['Sunrise']}<br>"
                    f"Dhuhr: {prayer_times['Dhuhr']} | Asr: {prayer_times['Asr']}<br>"
                    f"Pôr do Sol: {prayer_times['Sunset']} | Maghrib: {prayer_times['Maghrib']}<br>"
                    f"Isha: {prayer_times['Isha']}"
                )
            else:
                mensagem_oracoes = "Não foi possível obter os horários de oração para essa cidade/país."

    return render_template(
        'calendario.html',
        year=year,
        month=month,
        days=days,
        weekdays=weekdays,
        hijri_dates=hijri_dates,
        mensagem_oracoes=mensagem_oracoes
    )


@app.route('/calendario/detalhe')
def calendario_detalhe():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    method = int(request.args.get('method', 7))

    hijri = gregorian_to_hijri(year, month, day)
    is_ramadan = hijri and hijri[1] == 9

    data = {}
    if latitude and longitude:
        prayer_times = get_prayer_times_by_coords(latitude, longitude, day, month, year, method)
        if prayer_times:
            data['horarios'] = (
                f"Fajr: {prayer_times['Fajr']} | Nascer do Sol: {prayer_times['Sunrise']} | "
                f"Dhuhr: {prayer_times['Dhuhr']} | Asr: {prayer_times['Asr']} | "
                f"Pôr do Sol: {prayer_times['Sunset']} | Maghrib: {prayer_times['Maghrib']} | "
                f"Isha: {prayer_times['Isha']}"
            )
        else:
            data['aviso'] = "Não foi possível obter os horários de oração para sua localização."
    else:
        data['aviso'] = "Permita o acesso à localização para ver os horários das orações."

    hijri = gregorian_to_hijri(year, month, day)
    is_ramadan = hijri and hijri[1] == 9

    if is_ramadan:
        data['mensagem_ramadan'] = obter_mensagem(hijri[2])
    else:
        data['frase'] = buscar_frase_alcorao()

    return jsonify(data)


@app.route('/alcorao')
def alcorao_home():
    """
    Página principal do Alcorão.
    Exibe uma frase aleatória do texto do Alcorão.
    """
    frase = buscar_frase_alcorao()
    return render_template('alcorao.html', frase=frase)


@app.route('/alcorao/texto')
def alcorao_texto():
    """
    Rota para baixar o texto do Alcorão.
    """
    texto_path = os.path.join(ALCORAO_ASSETS, "alcoraoSamir.txt")
    if os.path.exists(texto_path):
        return send_file(texto_path, as_attachment=True)
    return "O arquivo de texto do Alcorão não foi encontrado.", 404


@app.route('/alcorao/pdf')
def alcorao_pdf():
    """
    Rota para baixar o PDF do Alcorão.
    """
    pdf_path = os.path.join(ALCORAO_ASSETS, "alcoraoSamir.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "O arquivo PDF do Alcorão não foi encontrado.", 404


@app.route('/frase_alcorao')
def frase_alcorao():
    return jsonify(frase=buscar_frase_alcorao())


# Execução do aplicativo
if __name__ == '__main__':
    app.run(debug=True)