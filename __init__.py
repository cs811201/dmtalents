import datetime
import sys

import flask_whooshalchemy as wa
from flask import Flask
from flask import render_template, url_for, request, redirect
from flask_security import Security, login_required, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True

if sys.platform == 'win32':
    print('win32')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/dm.db'
    app.config['WHOOSH_BASE'] = 'whoosh_index'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/FlaskApp/dmworks/db/dm.db'
    app.config['WHOOSH_BASE'] = '/var/www/FlaskApp/dmworks/whoosh_index'

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'super-secret007'
app.config['SECURITY_REGISTERABLE'] = True

db = SQLAlchemy(app)

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
    route = db.Column(db.String(128))


# record who and when viewed what
class PostHistory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    route = db.Column(db.String(128))
    date = db.Column(db.DateTime())


# record who and when searched for what
class SearchHistory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    search_string = db.Column(db.String(255))
    date = db.Column(db.DateTime())


wa.whoosh_index(app, Post)

# Post.query.whoosh_search(request.args.get('query')).all()

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Post)
security = Security(app, user_datastore)


def getCategory(txt):
    if txt == 'mbpst':
        return "MBP Script Tutorial"
    elif txt == "mbpfaq":
        return "MBP FAQ"
    elif txt == "mqarules":
        return "MQA Rules"
    elif txt == "mqafaq":
        return "MQA FAQ"
    elif txt == "blog":
        return "Blog"

    return "Not Categorized."


def recordPostHistory(rt):
    id = current_user.id
    now = datetime.datetime.now()
    ph = PostHistory.query.filter(PostHistory.user_id == id).filter(PostHistory.route == rt).all()
    flag = False
    if ph.__len__() > 0:
        for p in ph:
            # date = datetime.datetime.strptime(p.date, "%Y-%m-%d %H:%M:%S.%f");
            diff = now - p.date
            diffmin = diff / datetime.timedelta(minutes=1)
            # print('diffmin', diffmin)
            if diffmin < 30:  # 30 minutes
                flag = True
                break
    if not flag:  # record only when the time is longer than 30 minutes.
        posthis = PostHistory(user_id=id, route=rt, date=now)
        db.session.add(posthis)
        db.session.commit()


def recordSearchHistory(txt):
    id = current_user.id
    now = datetime.datetime.now()
    searchHis = SearchHistory(user_id=id, search_string=txt, date=now)
    db.session.add(searchHis)
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    return redirect(url_for('logout'))


@app.route('/mbpst')
@login_required
# @roles_required('bumblebee')
def mbpst():
    recordPostHistory('/mbpst')
    return render_template('mbpst/Chap1/WhatIsMBPScript.html')


# default to MBP FAQ list
@app.route('/mbpfaq')
# @roles_required('bumblebee')
@login_required
def mbpfaq():
    recordPostHistory('/mbpfaq')
    results = Post.query.filter(Post.category == 'mbpfaq').all()
    return render_template('faq/mbp/mbpfaqlist.html', slist=results, func=getCategory)


@app.route('/mqafaq')
@login_required
def mqafaq():
    recordPostHistory('/mqafaq')
    results = Post.query.filter(Post.category == 'mqafaq').all()
    return render_template('faq/mqa/mqafaqlist.html', slist=results, func=getCategory)


@app.route('/blog')
@login_required
def blog():
    recordPostHistory('/blog')
    results = Post.query.filter(Post.category == 'blog').all()
    return render_template('blog/blog_index.html', slist=results, func=getCategory)


@app.route('/mqarules')
@login_required
def mqarules():
    recordPostHistory('/mqarules')
    results = Post.query.filter(Post.category == 'mqarules').all()
    return render_template('mqarules/mqarules_index.html', slist=results, func=getCategory)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    # only CS can add for now.
    if current_user.email != 'shuang_cai@keysight.com':
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('add_post.html')
    if request.method == 'POST':
        title = request.form['title'].strip()
        abs = request.form['abs'].strip()
        category = request.form['category']
        content = request.form['content'].strip()
        now = datetime.datetime.now()
        route = request.form['route'].strip()
        user_id = current_user.get_id()
        post = Post(title=title, abs=abs, category=category, author_id=user_id, content=content, create_date=now,
                    route=route)

        db.session.add(post)
        db.session.commit()
        return render_template('post_added.html', newpost=post)


# example
# .filter(BlogPost.created >= two_days_ago)
@app.route('/search', methods=['POST'])
@login_required
def search():
    txt = request.form['search']
    recordSearchHistory(txt)
    results = Post.query.whoosh_search(txt).all()
    return render_template('search_result.html', slist=results, searchfor=txt, myfunction=getCategory)


@app.route('/about')
def about():
    recordPostHistory('/about')
    return render_template('about.html')


@app.route('/contact')
def contact():
    recordPostHistory('/contact')
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


# MBP Script Tutorial Chapters
@app.route('/mbpst/chap1.1')
@login_required
def mbpstchap1_1():
    recordPostHistory('/mbpst/chap1.1')
    return render_template('/mbpst/Chap1/WhatIsMBPScript.html')


@app.route('/mbpst/chap1.2')
@login_required
def mbpstchap1_2():
    recordPostHistory('/mbpst/chap1.2')
    return render_template('/mbpst/Chap1/GetStarted.html')


@app.route('/mbpst/chap2.1.1')
@login_required
def mbpstchap2_1_1():
    recordPostHistory('/mbpst/chap2.1.1')
    return render_template('/mbpst/Chap2/IMVTargets.html')


@app.route('/mbpst/chap2.1.2')
@login_required
def mbpstchap2_1_2():
    recordPostHistory('/mbpst/chap2.1.2')
    return render_template('/mbpst/Chap2/IMVPlots.html')


@app.route('/mbpst/chap2.1.3')
@login_required
def mbpstchap2_1_3():
    recordPostHistory('/mbpst/chap2.1.3')
    return render_template('/mbpst/Chap2/IMVConst.html')


@app.route('/mbpst/chap2.2')
@login_required
def mbpstchap2_2():
    recordPostHistory('/mbpst/chap2.2')
    return render_template('/mbpst/Chap2/DP.html')


@app.route('/mbpst/chap2.3.1')
@login_required
def mbpstchap2_3_1():
    recordPostHistory('/mbpst/chap2.3.1')
    return render_template('/mbpst/Chap2/HowFlowWorks.html')


@app.route('/mbpst/chap2.3.2')
@login_required
def mbpstchap2_3_2():
    recordPostHistory('/mbpst/chap2.3.2')
    return render_template('/mbpst/Chap2/DefineANewFlow.html')


@app.route('/mbpst/chap3.1')
@login_required
def mbpstchap3_1():
    recordPostHistory('/mbpst/chap3.1')
    return render_template('/mbpst/Chap3/DefineIdeff.html')


@app.route('/mbpst/chap3.2')
@login_required
def mbpstchap3_2():
    recordPostHistory('/mbpst/chap3.2')
    return render_template('/mbpst/Chap3/DefineVth.html')


@app.route('/mbpst/chap3.3')
@login_required
def mbpstchap3_3():
    recordPostHistory('/mbpst/chap3.3')
    return render_template('/mbpst/Chap3/DefineGmNearVth.html')


@app.route('/mbpst/chap3.4')
@login_required
def mbpstchap3_4():
    recordPostHistory('/mbpst/chap3.4')
    return render_template('/mbpst/Chap3/SelectData.html')


@app.route('/mbpst/chap3.5')
@login_required
def mbpstchap3_5():
    recordPostHistory('/mbpst/chap3.5')
    return render_template('/mbpst/Chap3/DefineTargetWithT25.html')


@app.route('/mbpst/chap3.6')
@login_required
def mbpstchap3_6():
    recordPostHistory('/mbpst/chap3.6')
    return render_template('/mbpst/Chap3/DataTransformation.html')


@app.route('/mbpst/chap3.7')
@login_required
def mbpstchap3_7():
    recordPostHistory('/mbpst/chap3.7')
    return render_template('/mbpst/Chap3/SynchronizeSAAndSB.html')


@app.route('/mbpst/chap3.8')
@login_required
def mbpstchap3_8():
    recordPostHistory('/mbpst/chap3.8')
    return render_template('/mbpst/Chap3/DisplayTargetOnY2.html')


@app.route('/mbpst/chap3.9')
@login_required
def mbpstchap3_9():
    recordPostHistory('/mbpst/chap3.9')
    return render_template('/mbpst/Chap3/IdsatNormalizedToMaxSASB.html')


@app.route('/mbpst/chap3.10')
@login_required
def mbpstchap3_10():
    recordPostHistory('/mbpst/chap3.10')
    return render_template('/mbpst/Chap3/FinFETVthcon.html')


@app.route('/mbpst/chap3.11')
@login_required
def mbpstchap3_11():
    recordPostHistory('/mbpst/chap3.11')
    return render_template('/mbpst/Chap3/AutorunWhenLoading.html')


@app.route('/mbpst/chap3.12')
@login_required
def mbpstchap3_12():
    recordPostHistory('/mbpst/chap3.12')
    return render_template('/mbpst/Chap3/RunOpt.html')


@app.route('/mbpst/chap3.13')
@login_required
def mbpstchap3_13():
    recordPostHistory('/mbpst/chap3.13')
    return render_template('/mbpst/Chap3/ArrangePlots.html')


@app.route('/mbpst/chap3.14')
@login_required
def mbpstchap3_14():
    recordPostHistory('/mbpst/chap3.14')
    return render_template('/mbpst/Chap3/CopyIMVtoAnotherPrj.html')


@app.route('/mbpst/chap3.15')
@login_required
def mbpstchap3_15():
    recordPostHistory('/mbpst/chap3.15')
    return render_template('/mbpst/Chap3/CallFuncFromAnotherFile.html')


@app.route('/mbpst/chap3.16')
@login_required
def mbpstchap3_16():
    recordPostHistory('/mbpst/chap3.16')
    return render_template('/mbpst/Chap3/ReadWriteFile.html')


@app.route('/mbpst/chap3.17')
@login_required
def mbpstchap3_17():
    recordPostHistory('/mbpst/chap3.17')
    return render_template('/mbpst/Chap3/HideExtraCol.html')


@app.route('/mbpst/chap3.18')
@login_required
def mbpstchap3_18():
    recordPostHistory('/mbpst/chap3.18')
    return render_template('/mbpst/Chap3/AccessSim.html')


@app.route('/mbpst/chap3.19')
@login_required
def mbpstchap3_19():
    recordPostHistory('/mbpst/chap3.19')
    return render_template('/mbpst/Chap3/SidOverId2.html')


@app.route('/mbpst/chap3.20')
@login_required
def mbpstchap3_20():
    recordPostHistory('/mbpst/chap3.20')
    return render_template('/mbpst/Chap3/DataSparseness.html')


@app.route('/mbpst/chap3.21')
@login_required
def mbpstchap3_21():
    recordPostHistory('/mbpst/chap3.21')
    return render_template('/mbpst/Chap3/RegionSelection.html')


@app.route('/mbpst/chap3.22')
@login_required
def mbpstchap3_22():
    recordPostHistory('/mbpst/chap3.22')
    return render_template('/mbpst/Chap3/Timer.html')


@app.route('/mbpst/chap3.23')
@login_required
def mbpstchap3_23():
    recordPostHistory('/mbpst/chap3.23')
    return render_template('/mbpst/Chap3/GlobalVar.html')


@app.route('/mbpst/chap4.1')
@login_required
def mbpstchap4_1():
    recordPostHistory('/mbpst/chap4.1')
    return render_template('/mbpst/Chap4/SimpleDebugging.html')


@app.route('/mbpst/chap4.2')
@login_required
def mbpstchap4_2():
    recordPostHistory('/mbpst/chap4.2')
    return render_template('/mbpst/Chap4/AdvancedDebugging.html')


@app.route('/mbpst/chap5.1')
@login_required
def mbpstchap5_1():
    recordPostHistory('/mbpst/chap5.1')
    return render_template('/mbpst/Chap5/BuiltInJavaAlgorithm.html')


@app.route('/mbpst/chap5.2')
@login_required
def mbpstchap5_2():
    recordPostHistory('/mbpst/chap5.2')
    return render_template('/mbpst/Chap5/APIs.html')


@app.route('/mbpst/chap5.2.1')
@login_required
def mbpstchap5_2_1():
    recordPostHistory('/mbpst/chap5.2.1')
    return render_template('/mbpst/Chap5/MBP.html')


#### MBP FAQ
@app.route('/mbpfaq/setgmindc')
@login_required
def mbpfaqSetgmindc():
    recordPostHistory('/mbpfaq/setgmindc')
    return render_template('/faq/mbp/setGminDC.html')


#### MQA FAQ


#### MQA Rules
@app.route('/mqarules/ft')
@login_required
def mqarulesFt():
    recordPostHistory('/mqarules/ft')
    return render_template('/mqarules/rules/ft.html')


@app.route('/mqarules/fmax')
@login_required
def mqarulesFmax():
    recordPostHistory('/mqarules/fmax')
    return render_template('/mqarules/rules/fmax.html')


if __name__ == '__main__':
    app.run()
