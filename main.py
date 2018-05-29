from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

@app.route('/user')
def showUserName():
    return render_template('user.html', name=session['userName'])


@app.route('/post')
def postScreen():
    return render_template('post.html')

@app.route('/show')
def showScreen():
    return render_template('show.html')

@app.route('/')
def login_form() :
    return render_template('login_form.html')

@app.route('/login', methods=['POST'])
def login() :
    if request.method== 'POST' :
        session['userName']=request.form['userName']
        return redirect(url_for('showUserName'))
    else :
        return 'login failed'

app.secret_key='abcdefsdfasdffdf'

if __name__ == "__main__":
    app.run('0.0.0.0',7700)
