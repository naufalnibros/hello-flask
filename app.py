from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, hashlib, socket

app = Flask(__name__)
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
    user_id     = db.Column(db.Integer)
    user_ip     = db.Column(db.Text)
    created_at  = db.Column(db.Text)

class Messages(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer)
    message     = db.Column(db.Text)
    created_at  = db.Column(db.Text)


def ValidasiLogin(Form):
    if Form:
        ip_address    = socket.gethostbyname(socket.gethostname())
        hash_password = hashlib.sha1(Form['password'])
        hash_password = hash_password.hexdigest()
        DataUser = User.query.filter_by(username=Form['username'], password=hash_password).first()
        if DataUser:
            AddLog = UserLog(user_id=DataUser.id, user_ip=ip_address, created_at=datetime.now())
            return {'username' : DataUser.username, 'created_at' : DataUser.password}
        else:
            return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    validasi = ValidasiLogin(request.form)
    if request.method == 'POST':
        return validasi['username']
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


if __name__ == '__main__':
    app.run(debug=True)
