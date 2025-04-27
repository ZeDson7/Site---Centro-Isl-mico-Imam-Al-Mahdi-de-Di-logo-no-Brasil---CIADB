"""
Módulo para exibir um calendário com suporte ao calendário Hijri.
"""

import calendar  # Importação padrão
from flask import Flask, render_template, request  # Importação de terceiros
from calendario_isla import gregorian_to_hijri  # Importação local

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)