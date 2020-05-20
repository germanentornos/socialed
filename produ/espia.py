import sys

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/oculto')
def espia():
    user_agent = request.headers.get('User-Agent')
    return '<p>Algunos datos de tu sistema... ;.)  %s</p>' % user_agent


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=8080)