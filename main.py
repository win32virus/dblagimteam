from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/hello<name>')
def hello(name):
    return render_template('hello.html', name=name)


@app.route('/')
def index():
    return render_template('login_form.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up_form.html')

@app.route('/board_list')
def board_list():
    return render_template('board_list.html')

@app.route('/test', methods=['GET'])
def test():
    return request.args.get('user')


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
