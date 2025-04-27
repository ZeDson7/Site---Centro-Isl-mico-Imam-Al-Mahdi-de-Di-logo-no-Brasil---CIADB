"""
Módulo para exibir um calendário com suporte ao calendário Hijri e funcionalidades relacionadas ao Alcorão.
"""

import os
import random
import calendar  # Importação padrão
from flask import Flask, render_template, request, send_file  # Importação de terceiros
from calendario_isla import gregorian_to_hijri  # Importação local

app = Flask(__name__)

# Configuração do diretório para armazenar os arquivos do Alcorão
ALCORAO_ASSETS = "assets"
os.makedirs(ALCORAO_ASSETS, exist_ok=True)


# Carregar o texto do Alcorão
def carregar_alcorao_texto():
    """
    Carrega o texto do Alcorão a partir de um arquivo.
    """
    texto_path = os.path.join(ALCORAO_ASSETS, "alcoraoSamir.txt")
    if os.path.exists(texto_path):
        with open(texto_path, "r", encoding="utf-8") as f:
            return f.readlines()
    return []


# Função para buscar uma frase aleatória de até 7 linhas
def buscar_frase_alcorao():
    """
    Busca uma frase aleatória de até 7 linhas do texto do Alcorão.
    """
    linhas = carregar_alcorao_texto()
    if not linhas:
        return "O texto do Alcorão não está disponível."

    # Escolher uma linha inicial aleatória
    inicio = random.randint(0, len(linhas) - 1)
    frase = []

    # Ler até 7 linhas a partir da linha inicial
    for i in range(inicio, min(inicio + 7, len(linhas))):
        frase.append(linhas[i].strip())
        if len(frase) == 7:  # Limitar a 7 linhas
            break

    # Adicionar "..." no final
    return " ".join(frase) + " ..."


@app.route('/calendario', methods=['GET'])
def calendario():
    """
    Rota principal para exibir o calendário.
    Pega o ano e o mês da URL (ou usa valores padrão) e gera os dias do mês.
    Também converte as datas para o calendário Hijri.
    """
    # Pega o ano e mês da URL (ou usa valores padrão)
    year = int(request.args.get('year', 2025))
    month = int(request.args.get('month', 1))

    # Criação do calendário
    cal = calendar.Calendar()
    days = list(cal.itermonthdays(year, month))
    weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

    # Conversão para Hijri
    hijri_dates = [
        gregorian_to_hijri(year, month, day) if day != 0 else None
        for day in days
    ]

    return render_template(
        'calendario.html',
        year=year,
        month=month,
        days=days,
        weekdays=weekdays,
        hijri_dates=hijri_dates
    )


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
    else:
        return "O arquivo de texto do Alcorão não foi encontrado.", 404


@app.route('/alcorao/pdf')
def alcorao_pdf():
    """
    Rota para baixar o PDF do Alcorão.
    """
    pdf_path = os.path.join(ALCORAO_ASSETS, "alcoraoSamir.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return "O arquivo PDF do Alcorão não foi encontrado.", 404


if __name__ == '__main__':
    app.run(debug=True)