from flask import Flask, render_template

app = Flask(__name__)


@app.route('/<name>')
def hello(name):
    return render_template('hello.html', name=name)


@app.route('/')
def index():
    return "hello, world"

if __name__ == '__main__':
    app.run('0.0.0.0',5000)
