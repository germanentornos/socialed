# -*- coding: iso-8859-15 -*-
from flask import Flask, request, render_template, session, redirect, url_for
import os.path
from os import listdir
import json
from time import time
import sys

from flask import Flask, session
from flask import Flask, request

from produ.templates.python import process_missingFields

app = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/home', methods=['GET'])
def home():
    return app.send_static_file('home.html')


@app.route('/login', methods=['GET'])
def login():
    return app.send_static_file('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    return app.send_static_file('signup.html')


@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
    missing = []
    fields = ['email', 'passwd', 'login_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/login")

    return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<title> Acceso - SocialED </title>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '</head>' \
           '<body> <div id ="container">' \
           '<a href="/"> SocialED </a> | <a href="home"> Inicio </a> | <a href="login"> Acceso </a> | <a href="signup"> Registro </a>' \
           '<h1>Data from Form: Login</h1>' \
           '<form><label>email: ' + request.form['email'] + \
           '</label><br><label>passwd: ' + request.form['passwd'] + \
           '</label></form></div></body>' \
           '</html>'


@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
    missing = []
    fields = ['nickname', 'email', 'passwd', 'confirm', 'signup_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/signup")

    return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<title> Registro - SocialED </title>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '</head>' \
           '<body> <div id ="container">' \
           '<a href="/"> SocialED </a> | <a href="home"> Inicio </a> | <a href="login"> Acceso </a> | <a href="signup"> Registro </a>' \
           '<h1>Data from Form: Sign Up</h1>' \
           '<form><label>Nickame: ' + request.form['nickname'] + \
           '</label><br><label>email: ' + request.form['email'] + \
           '</label><br><label>passwd: ' + request.form['passwd'] + \
           '</label><br><label>confirm: ' + request.form['confirm'] + \
           '</label></form></div></body>' \
           '</html>'


@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
    missing = []
    fields = ['message', 'last', 'post_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/home")

    return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<title> Inicio - SocialED </title>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '</head>' \
           '<body> <div id="container">' \
           '<a href="/"> SocialED </a> | <a href="home"> Inicio </a> | <a href="login"> Acceso </a> | <a href="signup"> Registro </a>' \
           '<h1>Hola internauta, qué tal estás?</h1>' \
           '<form action="processHome" method="post" name="home"> ' \
           '<label for="message">Escribe algo...</label><div class="inputs">' \
           '<input id="message" maxlength="128" name="message" size="80" type="text" required="true" value=""/>' \
           '<input id="last" type="hidden" name="last" required="true" value="' + request.form['last'] + '<br>' + \
           request.form['message'] + '">' \
                                     '</div>' \
                                     '<div class="inputs">' \
                                     '<input id="post_submit" name="post_submit" type="submit" value="Post!"/>' \
                                     '<br><br>Escritos anteriores: <br>' + request.form['last'] + '<br>' + request.form[
               'message'] + \
           '</form>' \
           '</div></div>' \
           '</body>' \
           '</html>'


def process_error(message, next_page):
    """

    :param message:
    :param next_page:
    :return:
    """
    return render_template("error.html", error_message=message, next=next_page)

def load_user(email, passwd):
    """
    Carga datos usuario (identified by email) del directorio data.
    Busca un archivo de nombre el email del usuario
    :param email: user id
    :param passwd: password
    :return: pagina home si existe el usuario y es correcto el pass
    """
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if not os.path.isfile(file_path):
        return process_error("User not found / No existe un usuario con ese nombre", url_for("login"))
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['password'] != passwd:
        return process_error("Incorrect password / la clave no es correcta", url_for("login"))
    session['user_name'] = data['user_name']
    session['messages'] = data['messages']
    session['password'] = passwd
    session['email'] = email
    session['friends'] = data['friends']
    return redirect(url_for("home"))


def save_current_user():
    datos = {
        "user_name": session["user_name"],
        "password": session['password'],
        "messages": session['messages'],  # lista de tuplas (time_stamp, mensaje)
        "email": session['email'],
        "friends": session['friends']
    }
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'w') as f:
        json.dump(datos, f)


def create_user_file(name, email, passwd, passwd_confirmation):
    """
    Crea el fichero (en directorio /data). El nombre será el email.
    Si el fichero ya existe, error.
    Si no coincide el pass con la confirmación, error.
    :param name: Nombre o apodo del usuario
    :param email: correo
    :param passwd: password
    :param passwd_confirmation: debe coincidir con pass
    :return: Si no hay errores, dirección al usuario a home.
    """

    directory = os.path.join(SITE_ROOT, "data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if os.path.isfile(file_path):
        return process_error(
            "The email is already used, you must select a different email / Ya existe un usuario con ese nombre",
            url_for("signup"))
    if passwd != passwd_confirmation:
        return process_error("Your password and confirmation password do not match / Las claves no coinciden",
                             url_for("signup"))
    datos = {
        "user_name": name,
        "password": passwd,
        "messages": [],
        "friends": []
    }
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['user_name'] = name
    session['password'] = passwd
    session['messages'] = []
    session['friends'] = []
    session['email'] = email
    return redirect(url_for("home"))


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=8001)
