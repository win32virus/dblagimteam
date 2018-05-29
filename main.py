#-*-coding:utf-8
from flask import Flask, request, render_template, session, redirect, url_for
import pymysql
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
conn = pymysql.connect(host='localhost', user='root', password='epdlxjqpdltmxlavm12',
                       db='hanaman', charset='utf8', autocommit=True, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()


@app.route('/')
def main():
    if 'user_id' in session:
        return render_template('board_list.html')
    else:
        return render_template('login.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/map')
def map_test():
    return render_template('map.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['id']
    user_pw = request.form['pw']
    query = "select user_id, user_name, user_email, user_phone from user where " \
            "user_id = %s and user_pw = password(%s)"

    if user_id is None or user_pw is None:
        return redirect(url_for('main'))
    else:
        cur.execute(query, (user_id, user_pw))
        row = cur.fetchone()
        if row is not None:
            session['user_id'] = row['user_id']
            session['user_name'] = row['user_name']
            session['user_email'] = row['user_email']
            session['user_phone'] = row['user_phone']
    return redirect(url_for('main'))


@app.route('/sign_up', methods=['POST'])
def create_user():
    user_id = request.form['id']
    user_pw = request.form['pw']
    user_name = request.form['name']
    user_email = request.form['email']
    user_phone = request.form['phone']
    result = {}
    if user_id is None or user_pw is None or user_name is None or user_email is None or user_phone is None:
        result = {'result': 'value error'}
    else:
        check_query = "select idx from user where user_id = %s"
        cur.execute(check_query, (user_id,))
        row = cur.fetchone()
        print(row)
        if row is not None:
            result = {'result': 'already existed'}
            return json.dumps(result)
        query = "insert into user(user_id, user_pw, user_name, user_email, user_phone) " \
                "values(%s, password(%s), %s, %s, %s)"
        query_result = cur.execute(query, (user_id, user_pw, user_name, user_email, user_phone))
        result = {'result': query_result}
    return json.dumps(result)


@app.route('/post/<int:pid>', methods=['GET'])
def get_post(pid):
    post_idx = pid
    query = "select idx, post_title, post_contents, post_writer, post_requester, post_goods_type, post_rental_status, "\
            "post_rental_duration, post_rental_price from post where idx=%s"
    cur.execute(query, (int(post_idx)))
    query_result = cur.fetchone()
    result = {'result': query_result}
    return json.dumps(result)


@app.route('/post', methods=['POST'])
def create_post():
    post_title = request.form['title']  # string
    post_contents = request.form['contents']  # string
    post_writer = request.form['writer']  # int
    post_goods_type = request.form['goods_type']  # int
    post_rental_duration = request.form['duration']  # per day, int
    post_rental_price = request.form['price']  # won, int
    query = "insert into post(post_title, post_contents, post_writer, post_goods_type, post_rental_duration," \
            "post_rental_duration, post_rental_price) values(%s, %s, %s, %s, %s, %s, %s)"
    query_result = cur.execute(query, (post_title, post_contents, int(post_writer), int(post_goods_type),
                                       int(post_rental_duration), int(post_rental_price)))
    result = {'result': query_result}
    return json.dumps(result)


@app.route('/search/<string:coordinate>', methods=['GET'])
def search_post(coordinate):
    try:
        query = "select idx from post where ST_Distance(post_geom, POINT({0})) < 10".format(coordinate)
        cur.execute(query)
    except:
        result = {'result': 'query error'}
        return json.dumps(result)
    else:
        query_result = cur.fetchone()
        result = {'result': query_result}
        return json.dumps(result)


if __name__ == '__main__':
    app.run('0.0.0.0', 8888)
