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
        page = request.args.get('page')
        if page is None:
            page = 1
        else:
            page = int(page)
        query = "select post.idx, post_title, user.user_name," \
                "rental_status.status_name, goods_type.type_name, post_rental_price from post " \
                "left join user on post_writer=user.idx " \
                "left join goods_type on post_goods_type=goods_type.idx " \
                "left join rental_status on post_rental_status=rental_status.idx where post_rental_status=1 " \
                "limit {0},{1}".format(10*(page-1), 10*(page-1)+10)
        cur.execute(query)
        query_result = cur.fetchall()
        return render_template('board_list.html', result=query_result)
    else:
        return render_template('login.html')


@app.route('/myinfo')
def myinfo():
    if 'user_id' in session:
        page = request.args.get('page')
        if page is None:
            page = 1
        else:
            page = int(page)

        query = "select post.idx, post_title, user.user_name, " \
                "rental_status.status_name, goods_type.type_name, post_rental_price from post " \
                "left join user on post_writer=user.idx " \
                "left join goods_type on post_goods_type=goods_type.idx " \
                "left join rental_status on post_rental_status=rental_status.idx where post_writer=%s "
        limit = "limit {0},{1} ".format(10*(page-1), 10*(page-1)+10)
        cur.execute(query + limit, int(session['user_idx']))
        query_result = cur.fetchall()

        return render_template('myinfo.html', result=query_result, user_info=session)
    else:
        return render_template('login.html')


@app.route('/post')
def postScreen():
    return render_template('post.html')


@app.route('/show')
def showScreen():
    return render_template('show.html')


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
    query = "select idx, user_id, user_name, user_email, user_phone from user where " \
            "user_id = %s and user_pw = password(%s)"

    if user_id is None or user_pw is None:
        return redirect(url_for('main'))
    else:
        cur.execute(query, (user_id, user_pw))
        row = cur.fetchone()
        if row is not None:
            session['user_idx'] = row['idx']
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
    error = ""
    if user_id is None or user_pw is None or user_name is None or user_email is None or user_phone is None:
        error = "value error"
    else:
        check_query = "select idx from user where user_id = %s"
        cur.execute(check_query, (user_id,))
        row = cur.fetchone()
        if row is not None:
            error = "already existed"
        else:
            query = "insert into user(user_id, user_pw, user_name, user_email, user_phone) " \
                    "values(%s, password(%s), %s, %s, %s)"
            query_result = cur.execute(query, (user_id, user_pw, user_name, user_email, user_phone))
            error = "Join Success"

    return render_template('login.html', error=error)


@app.route('/post/<int:pid>', methods=['GET'])
def get_post(pid):
    post_idx = pid
    query = "select post.idx, post_title, post_contents, user.user_name, user.idx, post_rental_status," \
            "goods_type.type_name, rental_status.status_name, post_rental_duration, post_rental_price, " \
            "ST_X(post_geom) as x, ST_Y(post_geom) as y from post " \
            "join user on post_writer=user.idx " \
            "join goods_type on post_goods_type=goods_type.idx " \
            "join rental_status on post_rental_status=rental_status.idx " \
            "where post.idx=%s"
    cur.execute(query, (int(post_idx)))
    query_result = cur.fetchone()
    if session['user_idx'] == query_result['user.idx']:
        query_result['mypost'] = 1
    else:
        query_result['mypost'] = 0
    return render_template('show.html', result=query_result)


@app.route('/post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('main'))

    post_title = request.form['title']  # string
    post_contents = request.form['contents']  # string
    post_goods_type = request.form['goods_type']  # int
    post_rental_duration = request.form['duration']  # per day, int
    post_rental_price = request.form['price']  # won, int
    post_geom = request.form['geom']
    post_writer = session['user_idx']

    query = "insert into post(post_title, post_contents, post_writer, post_goods_type, post_rental_duration," \
            "post_rental_status, post_rental_price, post_geom) " \
            "values(%s, %s, %s, %s, %s, 1, %s, POINT({0}))".format(post_geom)
    cur.execute(query, (post_title, post_contents, int(post_writer), int(post_goods_type),
                        int(post_rental_duration), int(post_rental_price)))
    return redirect(url_for('main'))


@app.route('/request/<int:pid>', methods=['GET'])
def rent_request(pid):
    if 'user_id' not in session:
        return redirect(url_for('main'))
    requester = session['user_idx']
    post_idx = pid
    query = "update post set post_requester=%s, post_rental_status=2 where idx=%s"
    cur.execute(query, (int(requester), int(post_idx)))
    return redirect(url_for('main'))


@app.route('/check_requester/<int:pid>', methods=['GET'])
def check_requester(pid):
    if 'user_id' not in session:
        return redirect(url_for('main'))
    query = "select user.user_id, user.user_name, user.user_email, user.user_phone from post " \
            "join user on post_requester=user.idx " \
            "where post.idx=%s"
    cur.execute(query, (int(pid)))
    query_result = cur.fetchone()
    query_result['post.idx'] = pid
    return render_template('check_requester.html', user_info=query_result)


@app.route('/to_rent/<int:pid>', methods=['GET'])
def to_rent(pid):
    if 'user_id' not in session:
        return redirect(url_for('main'))
    query = "update post set post_rental_status=3 where idx=%s"
    cur.execute(query, int(pid))
    return redirect(url_for('main'))


@app.route('/rent_done/<int:pid>', methods=['GET'])
def rent_done(pid):
    if 'user_id' not in session:
        return redirect(url_for('main'))
    query = "update post set post_rental_status=4 where idx=%s"
    cur.execute(query, int(pid))
    return redirect(url_for('main'))


@app.route('/search', methods=['GET'])
def search_post():
    if 'user_id' not in session:
        return redirect(url_for('main'))
    page = request.args.get('page')
    geom = request.args.get('geom')
    keyword = request.args.get('keyword')
    bit = request.args.get('bit')
    error=""
    if page is None:
        page = 1
    else:
        page = int(page)
    if bit == '1':
        _bit = "or"
    elif bit == '2':
        _bit = "and"
    else:
        _bit = "or"
    if keyword == "" and geom == "":
        error = "검색 키워드 혹은 좌표를 찍어주세요"
        return render_template('board_list.html', error=error)
    try:
        query = "select post.idx, post_title, user.user_name," \
                "rental_status.status_name, goods_type.type_name, post_rental_price from post " \
                "left join user on post_writer=user.idx " \
                "left join goods_type on post_goods_type=goods_type.idx " \
                "left join rental_status on post_rental_status=rental_status.idx " \
                "where post_rental_status=1 and post_title like '%{0}%' ".format(keyword)
        coord_search = " ST_Distance(post_geom, POINT({0})) < 200 ".format(geom)
        limit = " limit {0},{1}".format(10*(page-1), 10*(page-1)+10)

        if geom != "":
            query += _bit + coord_search
        query += limit

        # query = "select idx from post where ST_Distance(post_geom, POINT({0})) < 10".format(coordinate)
        print(query)
        cur.execute(query)
    except:
        error = 'query error'
        return render_template('board_list.html', error=error)
    else:
        query_result = cur.fetchall()
        return render_template('board_list.html', result=query_result)


if __name__ == '__main__':
    app.run('0.0.0.0', 8888)
