from flask import Flask, request, render_template
import pymysql
import json

app = Flask(__name__)
conn = pymysql.connect(host='localhost', user='root', password='epdlxjqpdltmxlavm12', db='hanaman', charset='utf8', autocommit=True)
cur = conn.cursor()


@app.route('/')
def main():
    return render_template('login.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'GET':
        user_id = request.args.get('id')
        user_pw = request.args.get('pw')
        query = "select * from user where user_id = '{0}' and user_pw = '{1}'".format(user_id, user_pw)

        if user_id is None or user_pw is None:
            return "id or pw error"

    elif request.method == 'POST':
        user_id = request.form['id']
        user_pw = request.form['pw']
        user_name = request.form['name']
        user_email = request.form['email']
        user_phone = request.form['phone']

        if user_id is None or user_pw is None or user_name is None or user_email is None or user_phone is None:
            return "Error"

        dup_check_query = "select user_id from user where user_id = '{0}'".format(user_id)
        dup_result = cur.execute(dup_check_query)
        if dup_result >= 1:
            return "already exist"

        query = "insert into user(user_id, user_pw, user_name, user_email, user_phone) values('{0}', '{1}', '{2}'," \
                "'{3}', '{4}')".format(user_id, user_pw, user_name, user_email, user_phone)
    query_result = cur.execute(query)
    result = {'result': query_result, 'query': query}
    return json.dumps(result)


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
