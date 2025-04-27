"""Conversor de datas entre calendário Gregoriano e Hijri."""

from flask import Flask, render_template, request

app = Flask(__name__)


def gregorian_to_hijri(year, month, day):
    """Converte uma data Gregoriana para Hijri."""
    jd = (
        (1461 * (year + 4800 + (month - 14) // 12)) // 4
        + (367 * (month - 2 - 12 * ((month - 14) // 12))) // 12
        - (3 * ((year + 4900 + (month - 14) // 12) // 100)) // 4
        + day - 32075
    )
    l_aux = jd - 1948440 + 10632
    n = (l_aux - 1) // 10631
    l_aux = l_aux - 10631 * n + 354
    j = (
        ((10985 - l_aux) // 5316) * ((50 * l_aux) // 17719)
        + (l_aux // 5670) * ((43 * l_aux) // 15238)
    )
    l_aux = (
        l_aux
        - ((30 - j) // 15) * ((17719 * j) // 50)
        - (j // 16) * ((15238 * j) // 43)
        + 29
    )
    month = (24 * l_aux) // 709
    day = l_aux - (709 * month) // 24
    year = 30 * n + j - 30
    return year, month, day


def hijri_to_gregorian(year, month, day):
    """Converte uma data Hijri para Gregoriana."""
    jd = (
        (11 * year + 3) // 30
        + 354 * year
        + 30 * month
        - (month - 1) // 2
        + day
        + 1948440
        - 385
    )
    l_aux = jd + 68569
    n = (4 * l_aux) // 146097
    l_aux = l_aux - (146097 * n + 3) // 4
    i = (4000 * (l_aux + 1)) // 1461001
    l_aux = l_aux - (1461 * i) // 4 + 31
    j = (80 * l_aux) // 2447
    day = l_aux - (2447 * j) // 80
    l_aux = j // 11
    month = j + 2 - 12 * l_aux
    year = 100 * (n - 49) + i + l_aux
    return year, month, day


@app.route('/calendario_isla', methods=['GET', 'POST'])
def conversor_calendario():
    """Página inicial do conversor de datas."""
    if request.method == 'POST':
        # Pegar dados do formulário
        g_year = int(request.form['gregorian_year'])
        g_month = int(request.form['gregorian_month'])
        g_day = int(request.form['gregorian_day'])

        # Conversão para Hijri
        hijri_date = gregorian_to_hijri(g_year, g_month, g_day)

        return render_template(
            'calendario_isla.html',
            g_year=g_year,
            g_month=g_month,
            g_day=g_day,
            hijri_date=hijri_date
        )

    # Exibição inicial da página
    return render_template('calendario_isla.html')


if __name__ == '__main__':
    app.run(debug=True)
