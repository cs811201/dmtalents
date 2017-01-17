import datetime

import flask_whooshalchemy as wa
from flask import Flask
from flask import render_template, url_for, request, redirect
from flask_security import Security, login_required, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/dm.db'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['WHOOSE_BASE'] = 'whoosh'

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Post(db.Model):
    __searchable__ = ['title', 'abs', 'content']
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), unique=True)
    author_id = db.Column(db.Integer)
    abs = db.Column(db.String())
    content = db.Column(db.Text())
    create_date = db.Column(db.DateTime())
    category = db.Column(db.String(128))
    last_modify_date = db.Column(db.DateTime())


wa.whoosh_index(app, Post)

# Post.query.whoosh_search(request.args.get('query')).all()

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Post)
security = Security(app, user_datastore)


@app.route('/')
def index():
    # myUser = User.query.all()
    return render_template('index.html')


@app.route('/mbpst')
@login_required
def mbpst():
    return render_template('mbpst.html')


@app.route('/faq')
@login_required
def mbpfaq():
    return render_template('faq.html')


@app.route('/mqarules')
@login_required
def mqarules():
    return render_template('mqarules.html')


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    print(request.method)
    if request.method == 'GET':
        return render_template('add_post.html')
    if request.method == 'POST':
        title = request.form['title']
        abs = request.form['abs']
        category = request.form['category']
        content = request.form['content']
        now = datetime.datetime.now()

        user_id = current_user.get_id()
        post = Post(title=title, abs=abs, category=category, author_id=user_id, content=content, create_date=now)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/add_user_kasdjfahviuner^sh&&*djfnkj__kdfj!!dfnl')
def goAddUser():
    users = User.query.all()
    return render_template('add_user.html', userList=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    admin = request.form['admin']
    if admin != 'bluesunflowerseeds!':
        print('Admin password is wrong!')
        return redirect(url_for('index'))

    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        password = request.form['password']
        active = True
        username = request.form['username']
        now = datetime.datetime.now()
        user = User(email=email, password=password, active=active, username=username, confirmed_at=now)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        print("User ", email, " exists!")


if __name__ == '__main__':
    app.run()
