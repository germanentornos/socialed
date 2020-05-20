# este codigo controla los errores de campos faltantes
from flask import render_template


def process_missingFields(campos, next_page):
    """
    :param campos: Lista de Campos que faltan
    :param next_page: ruta al pulsar botón continuar
    :return: plantilla generada
    """
    return render_template("missingFields.html", inputs=campos, next=next_page)