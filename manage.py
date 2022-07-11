from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import datetime


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = "S3cr3t K3Y"
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def index():
    posts = Posts.query.all()
    return render_template("index.html", params=params, posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        entry = Contact(name=name, email=email, phone=str(phone), message=message)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from ' + name,
        #                   sender=email,
        #                   recipients=[params['gmail_user']],
        #                   body=message + "\n" + phone
        #                   )

    user_data = Contact.query.all()
    for user in user_data:
        print(user.name)
    return render_template("contact.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin":
            # set the session variable
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/dashboard")
def dashboard():
    if "user" in session and session['user'] == "admin":
        posts = Posts.query.all()
        return render_template("dashboard.html", posts=posts)
    else:
        return redirect(url_for('login'))


@app.route("/insert-post", methods=['POST'])
def insert_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        img_file = request.form['img_file']
        date_posted = datetime.datetime.utcnow()

        details = Posts(title=title, content=content, img_file=img_file, date_posted=date_posted)
        db.session.add(details)
        db.session.commit()

        flash("Blog Post Inserted Successfully")

        return redirect(url_for('dashboard'))


@app.route("/update-post", methods=['GET', 'POST'])
def update_post():
    if request.method == 'POST':
        details = Posts.query.get(request.form.get('sno'))

        details.title = request.form['title']
        details.content = request.form['content']
        details.img_file = request.form['img_file']

        db.session.commit()
        flash("Blog Post Updated Successfully")

        return redirect(url_for('dashboard'))


@app.route("/delete-post/<sno>/")
def delete_post(sno):
    details = Posts.query.get(sno)
    db.session.delete(details)
    db.session.commit()
    flash("Blog Post Deleted Successfully")

    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
