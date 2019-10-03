# import required modules
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
# acces configuration file
with open('config.json', 'r') as c:
    params = json.load(c)["params"]
# intitiating the app
app = Flask(__name__)
# SMTP setup
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app)

# connect to with
local_server = True
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

# Contact class model for Contact-model
db = SQLAlchemy(app)


class Contact(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80),  nullable=False)
    Email = db.Column(db.String(120),  nullable=False)
    Subject = db.Column(db.String(120),  nullable=False)
    Message = db.Column(db.String(120),  nullable=False)

# defining the routes
@app.route("/")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/services")
def services():
    return render_template('services.html')


@app.route("/logout")
def logout():
    session.pop('user_check')
    return redirect('/')


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if ('user' in session and session['user'] == params['admin_user']):
        return render_template('dashboard.html')
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['user_check'] = username
            contact = Contact.query.all()
            #contact = Contact.query().order_by(Contact.c.ID.desc()).limit(5)
            return render_template('dashboard.html', contact=contact)
    return render_template('admin.html')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        entry = Contact(Name=name, Email=email,
                        Subject=subject, Message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from Pet hospital',
                          sender=email,
                          recipients=[params['gmail_user']],
                          body=message)
    return render_template('contact.html', params=params)


if __name__ == '__main__':
    app.secret_key = 'super - secret - key'
    app.run(debug=True)
