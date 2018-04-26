from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/')
def main():
    return "hell, world"


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'GET':
        user_id = request.args.get('id')
        user_pw = request.args.get('pw')
    elif request.method == 'POST':
        user_id = request.form['id']
        user_pw = request.form['pw']

    if user_id is None or user_pw is None:
        return "id or pw error"
    else:
        result = {'user_id': user_id, 'user_pw': user_pw}
        return json.dumps(result)


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
