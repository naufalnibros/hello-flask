from flask import Flask, render_template, request, escape, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import json, hashlib, socket

app = Flask(__name__)
app.secret_key                                  = 'D@D@#G#$V'
app.config['SQLALCHEMY_DATABASE_URI']           = 'mysql+pymysql://root:root@localhost/challenge_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']    = False

db = SQLAlchemy(app)

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(50))
    password    = db.Column(db.Text)
    created_at  = db.Column(db.Text)

class UserLog(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_ip     = db.Column(db.Text)
    created_at  = db.Column(db.Text)

class Messages(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    message     = db.Column(db.Text)
    created_at  = db.Column(db.Text)


def ValidasiLogin(Form):
    if Form:
        ip_address    = socket.gethostbyname(socket.gethostname())
        hash_password = hashlib.sha1(Form['password'])
        hash_password = hash_password.hexdigest()
        DataUser = User.query.filter_by(username=Form['username'], password=hash_password).first()
        if DataUser:
            session['user']         = {'username': DataUser.username, 'id': DataUser.id}
            AddLog                  = UserLog(user_id=DataUser.id, user_ip=ip_address, created_at=datetime.now())
            db.session.add(AddLog)
            db.session.commit()
            return {'error': False, 'username' : DataUser.username, 'message' : 'Berhasil Login'}
        else:
            return {'error': True, 'message' : 'Gagal Login'}

@app.route("/")
def index():
    session.pop('user', None)
    return render_template("index.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    validasi = ValidasiLogin(request.form)
    if request.method == 'POST':
        if validasi['error'] == False:
            return redirect(url_for('dashboard'))
        return render_template("login.html", message="Username dan Password yang Anda Masukkan Salah")
    return render_template("login.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username       = request.form['username']
        password       = hashlib.sha1(request.form['password']).hexdigest()
        created_at     = datetime.now()

        AddUser = User(username=username, password=password, created_at=created_at)
        db.session.add(AddUser)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template("register.html")

@app.route("/dashboard", methods=['POST', 'GET'])
def dashboard():
    if 'user' not in session:
        return render_template("login.html", message="Anda Belum Login")

    DataUser = {
        'id': escape(session['user']['id']),
        'username' : escape(session['user']['username'])
    }

    if request.method == 'POST':
        created_at      = datetime.now()
        AddMessage      = Messages(user_id=DataUser['id'], message=request.form['message'], created_at=created_at)
        db.session.add(AddMessage)
        db.session.commit()

    ModelsMessage = db.session.query(Messages, User).outerjoin(User, User.id == Messages.user_id).order_by(desc(Messages.id)).all()
    return render_template("dashboard.html", data_user=DataUser, messages=ModelsMessage)

@app.route("/history_user")
def history_user():
    Models = db.session.query(UserLog, User).outerjoin(User, User.id == UserLog.user_id).order_by(desc(UserLog.id)).all()
    return render_template('user-log.html', history_user=Models)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
