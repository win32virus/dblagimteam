from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)


@app.route('/')
def index():
    return "hello, world"

@app.route('/test',methods=['GET'])
def test():
    return request.args.get('user')

if __name__ == '__main__':
    app.run('0.0.0.0',5000)
