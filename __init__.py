import datetime
import operator
import os
import sys
from collections import Counter
from random import randint

import flask_whooshalchemy as wa
import pygal
from flask import Flask, g
from flask import render_template, url_for, request, redirect, send_file
from flask_mail import Mail
from flask_security import Security, login_required, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
from flask_security import roles_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from pygal.style import Style
from sqlalchemy import desc
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.debug = False

if sys.platform == 'win32':
    # print('win32')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/dm.db'
    app.config['WHOOSH_BASE'] = 'whoosh_index'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/FlaskApp/dmworks/db/dm.db'
    app.config['WHOOSH_BASE'] = '/var/www/FlaskApp/dmworks/whoosh_index'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'super-secret007'
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_TOKEN_MAX_AGE'] = 60 * 30
app.config['SECURITY_TRACKABLE'] = True
# app.config['SECURITY_PASSWORD_SALT'] = 'something_super_secret_802jfkj__fd!'

# config to upload folder
UPLOAD_FOLDER = '/static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # limit up to 2Mb per file

# config for email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cs8112010033@gmail.com'
app.config['MAIL_PASSWORD'] = 'iamcsman121'

db = SQLAlchemy(app)

mail = Mail(app)


def getRandomIntFrom1toGiven(top):
    if top <= 1:
        return 1
    else:
        return randint(1, top)


def recordPostHistory(rt):
    id = -1  # anonymous, used for public
    if hasattr(current_user, 'id'):
        id = current_user.id

    if id == 3:  # 3 is Shuang Cai, no need to record myself. :)
        return

    now = datetime.datetime.now()
    ph = PostHistory.query.filter(PostHistory.user_id == id).filter(PostHistory.route == rt).all()
    flag = False  # True is not to record
    if ph.__len__() > 0:
        for p in ph:
            # date = datetime.datetime.strptime(p.date, "%Y-%m-%d %H:%M:%S.%f");
            diff = now - p.date
            diffmin = diff / datetime.timedelta(minutes=1)
            # print('diffmin', diffmin)
            if diffmin < 2:  # # record only when the time is longer than XX minutes.
                flag = True
                break
    if id == -1:
        flag = False  # record all public views.

    if not flag:
        posthis = PostHistory(user_id=id, route=rt, date=now)
        db.session.add(posthis)
        db.session.commit()


def recordSearchHistory(txt):
    id = current_user.id
    if id == 3:  # 3 is Shuang Cai, no need to record myself. :)
        return

    now = datetime.datetime.now()
    searchHis = SearchHistory(user_id=id, search_string=txt, date=now)
    db.session.add(searchHis)
    db.session.commit()


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    company = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email


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

# display how many in most search list
displayUpto = 50


@app.route('/')
def index():
    # recordPostHistory("/")
    mbpPost = Post.query.filter((Post.category == 'mbpst')).all()
    mbpstCt = mbpPost.__len__()
    rulePost = Post.query.filter((Post.category == 'mqarules')).all()
    ruleCt = rulePost.__len__()

    pyrfsPost = Post.query.filter((Post.category == 'pyrfs')).all()
    pyrfsCt = pyrfsPost.__len__()

    videoPost = Post.query.filter((Post.category == 'video')).all()
    videoCt = videoPost.__len__()

    faqPost = Post.query.filter(
        (Post.category == 'mqafaq') | (Post.category == 'mbpfaq') | (Post.category == 'iccapfaq') | (
            Post.category == 'wpefaq') | (Post.category == 'alfnafaq')).all()
    faqCt = faqPost.__len__()
    g.__setattr__('dombp', True)

    return render_template('index.html', num=getRandomIntFrom1toGiven(16), mbpstCt=mbpstCt, videoCt=videoCt,
                           ruleCt=ruleCt, faqCt=faqCt, pyrfsCt=pyrfsCt)


route_update_history = '/update_history'


@app.route(route_update_history)
def updateHis():
    # record view history
    recordPostHistory(route_update_history)
    return render_template('update_history.html')


#
# # test send email
# @app.route("/send_email")
# @login_required
# @roles_required('bumblebee')
# def send_email():
#     # msg = Message('Hello',
#     #               sender='cs8112010033@gmail.com',
#     #               recipients=['cs811201@gmail.com'])
#     # msg.body = "This is the email body"
#     # mail.send(msg)
#     return "Sent"


@app.route('/login')
def login():
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/mbpst')
# @login_required
def mbpst():
    recordPostHistory('/mbpst')
    return render_template('mbpst/Chap1/WhatIsMBPScript.html')


route_reqeust_login = '/requestlogin'


@app.route(route_reqeust_login)
def request_login():
    recordPostHistory(route_reqeust_login)
    return render_template('requestlogin.html')


# default to MBP FAQ list
@app.route('/faq')
# @roles_required('bumblebee')
@login_required
def faq():
    recordPostHistory('/faq')
    results = Post.query.filter(
        (Post.category == 'mbpfaq') | (Post.category == 'mqafaq') | (Post.category == 'iccapfaq') | (
            Post.category == 'wpefaq') | (Post.category == 'alfnafaq')).order_by(
        desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/faq_list.html', slist=results, func=getCategory)


# default to MBP FAQ list
@app.route('/mbpfaq')
# @roles_required('bumblebee')
@login_required
def mbpfaq():
    recordPostHistory('/mbpfaq')
    results = Post.query.filter(Post.category == 'mbpfaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/mbp/mbpfaqlist.html', slist=results, func=getCategory)


@app.route('/mqafaq')
@login_required
def mqafaq():
    recordPostHistory('/mqafaq')
    results = Post.query.filter(Post.category == 'mqafaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/mqa/mqafaqlist.html', slist=results, func=getCategory)


route_iccapfaq_list = "/iccapfaq"


@app.route(route_iccapfaq_list)
@login_required
def iccapfaq():
    recordPostHistory(route_iccapfaq_list)
    results = Post.query.filter(Post.category == 'iccapfaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/iccap/iccapfaqlist.html', slist=results, func=getCategory)


route_wpefaq_list = "/wpefaq"


@app.route(route_wpefaq_list)
@login_required
def wpefaq():
    recordPostHistory(route_wpefaq_list)
    results = Post.query.filter(Post.category == 'wpefaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/wpe/wpefaqlist.html', slist=results, func=getCategory)


route_alfnafaq_list = "/alfnafaq"


@app.route(route_alfnafaq_list)
@login_required
def alfnafaq():
    recordPostHistory(route_alfnafaq_list)
    results = Post.query.filter(Post.category == 'alfnafaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/alfna/alfnafaqlist.html', slist=results, func=getCategory)


# open blog to public
@app.route('/blog')
def blog():
    recordPostHistory('/blog')
    results = Post.query.filter(Post.category == 'blog').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('blog/blog_index.html', slist=results, func=getCategory)


route_blog_vth_algor = '/blog/vth_algor'


@app.route(route_blog_vth_algor)
def blog_vth_algor():
    recordPostHistory(route_blog_vth_algor)
    return render_template('blog/post/vth_algor.html')


route_blog_vth_near_gm = '/blog/vth_near_gm'


@app.route(route_blog_vth_near_gm)
def blog_vth_near_gm():
    recordPostHistory(route_blog_vth_near_gm)
    return render_template('blog/post/vth_near_gm.html')


route_blog_why_dm_servo = '/blog/why_dm_services'


@app.route(route_blog_why_dm_servo)
def blog_why_dm_servo():
    recordPostHistory(route_blog_why_dm_servo)
    return render_template('blog/post/why_dm_services.html')


route_blog_iccap_python = '/blog/iccap_python'


@app.route(route_blog_iccap_python)
def blog_iccap_python():
    recordPostHistory(route_blog_iccap_python)
    return render_template('blog/post/iccap_python.html')


route_blog_ftfmax = '/blog/ftfmax'


@app.route(route_blog_ftfmax)
def blog_ftfmax():
    recordPostHistory(route_blog_ftfmax)
    return render_template('blog/post/ftfmax.html')


route_blog_load_csv_in_mbp = '/blog/load_csv_in_mbp'


@app.route(route_blog_load_csv_in_mbp)
def blog_load_csv_in_mbp():
    recordPostHistory(route_blog_load_csv_in_mbp)
    return render_template('blog/post/load_csv_in_mbp.html')


route_blog_sram_modeling_mbp2017 = '/blog/sram_modeling_mbp2017'


@app.route(route_blog_sram_modeling_mbp2017)
def blog_sram_modeling_mbp2017():
    recordPostHistory(route_blog_sram_modeling_mbp2017)
    return render_template('blog/post/srammodeling.html')


route_blog_angelov_in_ads = '/blog/angelov_in_ads'


@app.route(route_blog_angelov_in_ads)
def blog_angelov_in_ads():
    recordPostHistory(route_blog_angelov_in_ads)
    return render_template('blog/post/angelov_in_ads.html')


route_blog_mbp_sram = '/blog/mbp_sram'


@app.route(route_blog_mbp_sram)
def blog_mbp_sram():
    recordPostHistory(route_blog_mbp_sram)
    return render_template('blog/post/mbp_sram.html')


route_blog_mbp_bsim4_flow = '/blog/mbp_bsim4_flow'


@app.route(route_blog_mbp_bsim4_flow)
def blog_mbp_bsim4_flow():
    recordPostHistory(route_blog_mbp_bsim4_flow)
    return render_template('blog/post/mbp_bsim4_flow.html')


route_blog_iccap_pyvisa_101 = '/blog/iccap_pyvisa_101'


@app.route(route_blog_iccap_pyvisa_101)
def blog_iccap_pyvisa_101():
    recordPostHistory(route_blog_iccap_pyvisa_101)
    return render_template('blog/post/pyvisa_01.html')


route_blog_mqa_pyrfs = '/blog/mqa_pyrfs'


@app.route(route_blog_mqa_pyrfs)
def blog_mqa_pyrfs():
    recordPostHistory(route_blog_mqa_pyrfs)
    return render_template('blog/post/mqa_pyrfs.html')


route_blog_mbp_extr_across_conditions = '/blog/mbp_extr_across_conditions'


@app.route(route_blog_mbp_extr_across_conditions)
def blog_mbp_extr_across_conditions():
    recordPostHistory(route_blog_mbp_extr_across_conditions)
    return render_template('blog/post/mbp_extr_across_conditions.html')


route_blog_iccap_ltspice = '/blog/iccap_ltspice'


@app.route(route_blog_iccap_ltspice)
def blog_iccap_ltspice():
    recordPostHistory(route_blog_iccap_ltspice)
    return render_template('blog/post/iccap_ltspice.html')


route_blog_iccap_ext_simulators = '/blog/iccap_ext_simulators'


@app.route(route_blog_iccap_ext_simulators)
def blog_iccap_ext_simulators():
    recordPostHistory(route_blog_iccap_ext_simulators)
    return render_template('blog/post/iccap_ext_simulators.html')


route_blog_iccap_python_q_l = '/blog/iccap_python_s_par'


@app.route(route_blog_iccap_python_q_l)
def blog_iccap_python_s_par():
    recordPostHistory(route_blog_iccap_python_q_l)
    return render_template('blog/post/iccap_python_Q_L.html')


# MQA rules

@app.route('/mqarules')
@login_required
def mqarules():
    recordPostHistory('/mqarules')
    return render_template('mqarules/mqarules_index.html', func=getCategory)


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


### Search Options ####
searchOptions = {'isopen': 0, 'doiccap': 1, 'dombp': 1, 'domqa': 1, 'doblog': 1, 'dovideo': 1, 'dowpe': 1, 'doalfna': 1}


def updateSearchOptions(isopen, doiccap, dombp, domqa, doblog, dovideo, dowpe, doalfna):
    global searchOptions
    searchOptions['isopen'] = 1 if isopen else 0
    searchOptions['doiccap'] = 1 if doiccap else 0
    searchOptions['dombp'] = 1 if dombp else 0
    searchOptions['domqa'] = 1 if domqa else 0
    searchOptions['doblog'] = 1 if doblog else 0
    searchOptions['dovideo'] = 1 if dovideo else 0
    searchOptions['dowpe'] = 1 if dowpe else 0
    searchOptions['doalfna'] = 1 if doalfna else 0

    return searchOptions


@app.context_processor
def inject_Search_Options():
    return searchOptions


### End -- Search Options ####

# example
# .filter(BlogPost.created >= two_days_ago)


@app.route('/search', methods=['POST'])
@login_required
def search():
    txt = request.form['search']
    recordSearchHistory(txt.strip())
    # add search option,
    isOpen = request.form.get('searchOptionFlag')

    doiccap = False
    dombp = False
    domqa = False
    dowpe = False
    doalfna = False
    dovideo = False
    doblog = False

    if (request.form.get('iccap') != None):
        doiccap = True
    if (request.form.get('wpe') != None):
        dowpe = True
    if (request.form.get('mbp') != None):
        dombp = True
    if (request.form.get('mqa') != None):
        domqa = True
    if (request.form.get('alfna') != None):
        doalfna = True
    if (request.form.get('video') != None):
        dovideo = True
    if (request.form.get('blog') != None):
        doblog = True

    if (isOpen.strip() == 'Closed'):
        isOpen = False
    else:
        isOpen = True

    # searchOptions -> inject_Search_Options()
    updateSearchOptions(isOpen, doiccap, dombp, domqa, doblog, dovideo, dowpe, doalfna)

    qer = Post.query.whoosh_search(txt)
    if not doiccap:
        qer = qer.filter(Post.category != 'iccapfaq')
    if not dombp:
        qer = qer.filter(Post.category != 'mbpst').filter(Post.category != 'mbpfaq')
    if not domqa:
        qer = qer.filter(Post.category != 'pyrfs').filter(Post.category != 'mqafaq').filter(Post.category != 'mqarules')
    if not doalfna:
        qer = qer.filter((Post.category != 'alfnafaq'))
    if not dowpe:
        qer = qer.filter((Post.category != 'wpefaq'))
    if not dovideo:
        qer = qer.filter((Post.category != 'video'))
    if not doblog:
        qer = qer.filter((Post.category != 'blog'))

    # results = qer.whoosh_search(txt).limit(displayUpto).all()

    results = qer.limit(displayUpto).all()
    category = ''
    global searchOptions
    category += 'ICCAP  |  ' if searchOptions['doiccap'] == 1 else ''
    category += 'MBP  |  ' if searchOptions['dombp'] == 1 else ''
    category += 'MQA  |  ' if searchOptions['domqa'] == 1 else ''
    category += 'Blog  |  ' if searchOptions['doblog'] == 1 else ''
    category += 'Video  |  ' if searchOptions['dovideo'] == 1 else ''
    category += 'WPE  |  ' if searchOptions['dowpe'] == 1 else ''
    category += 'ALFNA  |  ' if searchOptions['doalfna'] == 1 else ''

    return render_template('search_result.html', slist=results, searchfor=txt, myfunction=getCategory,
                           category=category)


@app.route('/about')
def about():
    recordPostHistory('/about')
    return render_template('about.html')


@app.route('/disclaimer')
def disclaimer():
    recordPostHistory('/disclaimer')
    return render_template('disclaimer.html')


#
# @app.route('/contact')
# def contact():
#     #recordPostHistory('/contact')
#     return render_template('contact.html')


@app.route('/add_user_kasdjfahviuner^sh&&*djfnkj__kdfj!!dfnl')
@login_required
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
        password = request.form['password'].strip()
        active = True
        username = request.form['username'].strip()
        company = request.form['company'].strip()
        now = datetime.datetime.now()
        user = User(email=email, password=password, active=active, username=username, confirmed_at=now, company=company)
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


@app.route('/mbpst/chap3.24')
@login_required
def mbpstchap3_24():
    recordPostHistory('/mbpst/chap3.24')
    return render_template('/mbpst/Chap3/Vth_gm.html')


@app.route('/mbpst/chap3.25')
@login_required
def mbpstchap3_25():
    recordPostHistory('/mbpst/chap3.25')
    return render_template('/mbpst/Chap3/IdealityFactor.html')


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


route_mbpst_api_MBP = '/mbpst/chap5.2/MBP'


@app.route(route_mbpst_api_MBP)
@login_required
def mbpstchap5_2_MBP():
    recordPostHistory(route_mbpst_api_MBP)
    return render_template('/mbpst/Chap5/MBP.html')


route_mbpst_api_data = '/mbpst/chap5.2/DATA'


@app.route(route_mbpst_api_data)
@login_required
def mbpstchap5_2_DATA():
    recordPostHistory(route_mbpst_api_data)
    return render_template('/mbpst/Chap5/DATA.html')


route_mbpst_api_table = '/mbpst/chap5.2/TABLE'


@app.route(route_mbpst_api_table)
@login_required
def mbpstchap5_2_TABLE():
    recordPostHistory(route_mbpst_api_table)
    return render_template('/mbpst/Chap5/TABLE.html')


route_mbpst_api_point = '/mbpst/chap5.2/POINT'


@app.route(route_mbpst_api_point)
@login_required
def mbpstchap5_2_POINT():
    recordPostHistory(route_mbpst_api_point)
    return render_template('/mbpst/Chap5/POINT.html')


route_mbpst_api_mbpdata = '/mbpst/chap5.2/MBPDATA'


@app.route(route_mbpst_api_mbpdata)
@login_required
def mbpstchap5_2_MBPDATA():
    recordPostHistory(route_mbpst_api_mbpdata)
    return render_template('/mbpst/Chap5/MBPDATA.html')


route_mbpst_api_mbpRF = '/mbpst/chap5.2/MBPRF'


@app.route(route_mbpst_api_mbpRF)
@login_required
def mbpstchap5_2_MBPRF():
    recordPostHistory(route_mbpst_api_mbpRF)
    return render_template('/mbpst/Chap5/MBPRF.html')


route_mbpst_api_mbpopt = '/mbpst/chap5.2/MBPOPT'


@app.route(route_mbpst_api_mbpopt)
@login_required
def mbpstchap5_2_MBPOPT():
    recordPostHistory(route_mbpst_api_mbpopt)
    return render_template('/mbpst/Chap5/MBPOPT.html')


route_mbpst_api_mbpopt_POPULATE_PARAM = '/mbpst/chap5.2/MBPOPT.POPULATE_PARAM'


@app.route(route_mbpst_api_mbpopt_POPULATE_PARAM)
@login_required
def mbpstchap5_2_MBPOPT_POPULATE_PARAM():
    recordPostHistory(route_mbpst_api_mbpopt_POPULATE_PARAM)
    return render_template('/mbpst/Chap5/MBPOPT.POPULATE_PARAM.html')


route_mbpst_api_PARAM = '/mbpst/chap5.2/Param'


@app.route(route_mbpst_api_PARAM)
@login_required
def mbpstchap5_2_PARAM():
    recordPostHistory(route_mbpst_api_PARAM)
    return render_template('/mbpst/Chap5/Param.html')


route_mbpst_api_cmd = '/mbpst/chap5.2/CMD'


@app.route(route_mbpst_api_cmd)
@login_required
def mbpstchap5_2_CMD():
    recordPostHistory(route_mbpst_api_cmd)
    return render_template('/mbpst/Chap5/CMD.html')


route_mbpst_api_pageplot = '/mbpst/chap5.2/PagePlot'


@app.route(route_mbpst_api_pageplot)
@login_required
def mbpstchap5_2_PagePlot():
    recordPostHistory(route_mbpst_api_pageplot)
    return render_template('/mbpst/Chap5/PagePlot.html')


route_mbpst_api_PageGroup = '/mbpst/chap5.2/PageGroup'


@app.route(route_mbpst_api_PageGroup)
@login_required
def mbpstchap5_2_PageGroup():
    recordPostHistory(route_mbpst_api_PageGroup)
    return render_template('/mbpst/Chap5/PageGroup.html')


route_mbpst_api_PlotCurve = '/mbpst/chap5.2/PlotCurve'


@app.route(route_mbpst_api_PlotCurve)
@login_required
def mbpstchap5_2_PlotCurve():
    recordPostHistory(route_mbpst_api_PlotCurve)
    return render_template('/mbpst/Chap5/PlotCurve.html')


route_mbpst_api_DataProvider = '/mbpst/chap5.2/DataProvider'


@app.route(route_mbpst_api_DataProvider)
@login_required
def mbpstchap5_2_DataProvider():
    recordPostHistory(route_mbpst_api_DataProvider)
    return render_template('/mbpst/Chap5/DataProvider.html')


route_mbpst_api_STR = '/mbpst/chap5.2/STR'


@app.route(route_mbpst_api_STR)
@login_required
def mbpstchap5_2_STR():
    recordPostHistory(route_mbpst_api_STR)
    return render_template('/mbpst/Chap5/STR.html')


route_mbpst_api_CMD_VARTABLE = '/mbpst/chap5.2/CMD.VARTABLE'


@app.route(route_mbpst_api_CMD_VARTABLE)
@login_required
def mbpstchap5_2_CMD_VARTABLE():
    recordPostHistory(route_mbpst_api_CMD_VARTABLE)
    return render_template('/mbpst/Chap5/CMD.VARTABLE.html')


route_mbpst_api_model = '/mbpst/chap5.2/Model'


@app.route(route_mbpst_api_model)
@login_required
def mbpstchap5_2_Model():
    recordPostHistory(route_mbpst_api_model)
    return render_template('/mbpst/Chap5/Model.html')


route_mbpst_api_mbpvar = '/mbpst/chap5.2/MBPVAR'


@app.route(route_mbpst_api_mbpvar)
@login_required
def mbpstchap5_2_MBPVAR():
    recordPostHistory(route_mbpst_api_mbpvar)
    return render_template('/mbpst/Chap5/MBPVAR.html')


route_mbpst_api_GraphDataSource = '/mbpst/chap5.2/GraphDataSource'


@app.route(route_mbpst_api_GraphDataSource)
@login_required
def mbpstchap5_2_GraphDataSource():
    recordPostHistory(route_mbpst_api_GraphDataSource)
    return render_template('/mbpst/Chap5/GraphDataSource.html')


route_mbpst_api_Math = '/mbpst/chap5.2/Math'


@app.route(route_mbpst_api_Math)
@login_required
def mbpstchap5_2_Math():
    recordPostHistory(route_mbpst_api_Math)
    return render_template('/mbpst/Chap5/Math.html')


route_mbpst_api_ScriptDialog = '/mbpst/chap5.2/ScriptDialog'


@app.route(route_mbpst_api_ScriptDialog)
@login_required
def mbpstchap5_2_ScriptDialog():
    recordPostHistory(route_mbpst_api_ScriptDialog)
    return render_template('/mbpst/Chap5/ScriptDialog.html')


#### MBP FAQ
@app.route('/mbpfaq/setgmindc')
@login_required
def mbpfaqSetgmindc():
    recordPostHistory('/mbpfaq/setgmindc')
    return render_template('/faq/mbp/setGminDC.html')


@app.route('/mbpfaq/scriptOptErrFuncTrick')
@login_required
def mbpfaqscriptOptErrFuncTrick():
    recordPostHistory('/mbpfaq/scriptOptErrFuncTrick')
    return render_template('/faq/mbp/scriptOptErrFuncTrick.html')


@app.route('/mbpfaq/optOptions')
@login_required
def mbpfaqoptOptions():
    recordPostHistory('/mbpfaq/optOptions')
    return render_template('/faq/mbp/optOptions.html')


route_changeIdlinDef = '/changeIdlinDef'


@app.route(route_changeIdlinDef)
@login_required
def mbpfaqchangeIdlinDef():
    recordPostHistory(route_changeIdlinDef)
    return render_template('/faq/mbp/changeIdlinDef.html')


route_mbpfaq_derivative = '/mbpfaq/derivative'


@app.route(route_mbpfaq_derivative)
@login_required
def mbpfaq_derivative():
    recordPostHistory(route_mbpfaq_derivative)
    return render_template('/faq/mbp/derivative.html')


route_mbpfaq_linefit = '/mbpfaq/linefit'


@app.route(route_mbpfaq_linefit)
@login_required
def mbpfaq_linefit():
    recordPostHistory(route_mbpfaq_linefit)
    return render_template('/faq/mbp/linefit.html')


route_mbpfaq_tinyNumbers = '/mbpfaq/tinyNumbers'


@app.route(route_mbpfaq_tinyNumbers)
@login_required
def mbpfaq_tinyNumbers():
    recordPostHistory(route_mbpfaq_tinyNumbers)
    return render_template('/faq/mbp/tinyNumbers.html')


route_mbpfaq_addInstParam = '/mbpfaq/addInstParam'


@app.route(route_mbpfaq_addInstParam)
@login_required
def mbpfaq_addInstParam():
    recordPostHistory(route_mbpfaq_addInstParam)
    return render_template('/faq/mbp/addInstParam.html')


route_mbpfaq_changeDefaultScript = '/mbpfaq/changeDefaultScript'


@app.route(route_mbpfaq_changeDefaultScript)
@login_required
def mbpfaq_changeDefaultScript():
    recordPostHistory(route_mbpfaq_changeDefaultScript)
    return render_template('/faq/mbp/changeDefaultScript.html')


route_mbpfaq_addFlow2Menu = '/mbpfaq/addFlow2Menu'


@app.route(route_mbpfaq_addFlow2Menu)
@login_required
def mbpfaq_addFlow2Menu():
    recordPostHistory(route_mbpfaq_addFlow2Menu)
    return render_template('/faq/mbp/addFlow2Menu.html')


route_mbpfaq_vthscaling4sides = '/mbpfaq/vthscaling4sides'


@app.route(route_mbpfaq_vthscaling4sides)
@login_required
def mbpfaq_vthscaling4sides():
    recordPostHistory(route_mbpfaq_vthscaling4sides)
    return render_template('/faq/mbp/vthscaling4sides.html')


route_mbpfaq_errorDataGrid = '/mbpfaq/errorDataGrid'


@app.route(route_mbpfaq_errorDataGrid)
@login_required
def mbpfaq_errorDataGrids():
    recordPostHistory(route_mbpfaq_errorDataGrid)
    return render_template('/faq/mbp/errorDataGrid.html')


route_mbpfaq_script_import_export = '/mbpfaq/script_import_export'


@app.route(route_mbpfaq_script_import_export)
@login_required
def mbpfaq_script_import_export():
    recordPostHistory(route_mbpfaq_script_import_export)
    return render_template('/faq/mbp/script_import_export.html')


route_mbpfaq_script_subckt_param = '/mbpfaq/script_subckt_param'


@app.route(route_mbpfaq_script_subckt_param)
@login_required
def mbpfaq_script_subckt_param():
    recordPostHistory(route_mbpfaq_script_subckt_param)
    return render_template('/faq/mbp/script_subckt_param.html')


route_mbpfaq_wleff = '/mbpfaq/weff_leff'


@app.route(route_mbpfaq_wleff)
@login_required
def mbpfaq_wleff():
    recordPostHistory(route_mbpfaq_wleff)
    return render_template('/faq/mbp/wleff.html')


route_mbpfaq_unused_param = '/mbpfaq/unused_param'


@app.route(route_mbpfaq_unused_param)
@login_required
def mbpfaq_unused_param():
    recordPostHistory(route_mbpfaq_unused_param)
    return render_template('/faq/mbp/unused_param.html')


route_mbpfaq_meascond = '/mbpfaq/meascond'


@app.route(route_mbpfaq_meascond)
@login_required
def mbpfaq_meascond():
    recordPostHistory(route_mbpfaq_meascond)
    return render_template('/faq/mbp/meascond.html')


route_mbpfaq_java_options = '/mbpfaq/javaoptions'


@app.route(route_mbpfaq_java_options)
@login_required
def mbpfaq_javaoptions():
    recordPostHistory(route_mbpfaq_java_options)
    return render_template('/faq/mbp/javaoptions.html')


route_mbpfaq_site_die = '/mbpfaq/site_die'


@app.route(route_mbpfaq_site_die)
@login_required
def mbpfaq_site_die():
    recordPostHistory(route_mbpfaq_site_die)
    return render_template('/faq/mbp/site_die.html')

route_mbpfaq_idletime = '/mbpfaq/idletime'


@app.route(route_mbpfaq_idletime)
@login_required
def mbpfaq_idletime():
    recordPostHistory(route_mbpfaq_idletime)
    return render_template('/faq/mbp/licenseidletime.html')

#### MQA FAQ
@app.route('/mqafaq/synchroVdVg')
@login_required
def mqafaqsynchroVdVg():
    recordPostHistory('/mqafaq/synchroVdVg')
    return render_template('/faq/mqa/synchroVdVg.html')


@app.route('/mqafaq/maxWaitTime')
@login_required
def mqafaqmaxWaitTime():
    recordPostHistory('/mqafaq/maxWaitTime')
    return render_template('/faq/mqa/maxWaitTime.html')


@app.route('/mqafaq/compareMode')
@login_required
def mqafaqcompareMode():
    recordPostHistory('/mqafaq/compareMode')
    return render_template('/faq/mqa/compareMode.html')


@app.route('/mqafaq/5TdeviceQA')
@login_required
def mqafaq5TdeviceQA():
    recordPostHistory('/mqafaq/5TdeviceQA')
    return render_template('/faq/mqa/5TdeviceQA.html')


@app.route('/mqafaq/CallMultiVerOfSim')
@login_required
def mqafaqCallMultiVerOfSim():
    recordPostHistory('/mqafaq/CallMultiVerOfSim')
    return render_template('/faq/mqa/CallMultiVerOfSim.html')


@app.route('/mqafaq/CheckNetlist')
@login_required
def mqafaqCheckNetlist():
    recordPostHistory('/mqafaq/CheckNetlist')
    return render_template('/faq/mqa/CheckNetlist.html')


route_mqafaq_cornerOnly = '/mqafaq/cornerOnly'


@app.route(route_mqafaq_cornerOnly)
@login_required
def mqafaqcornerOnly():
    recordPostHistory(route_mqafaq_cornerOnly)
    return render_template('/faq/mqa/cornerOnly.html')


route_mqafaq_redefinedparams = '/mqafaq/redefinedparams'


@app.route(route_mqafaq_redefinedparams)
@login_required
def mqafaqRedefinedparams():
    recordPostHistory(route_mqafaq_redefinedparams)
    return render_template('/faq/mqa/redefinedparams.html')


route_mqafaq_addPyrfs = '/mqafaq/addPyrfs'


@app.route(route_mqafaq_addPyrfs)
@login_required
def mqafaqaddPyrfs():
    recordPostHistory(route_mqafaq_addPyrfs)
    return render_template('/faq/mqa/addPyRFS.html')


route_mqafaq_internalspice3 = '/mqafaq/internalspice3'


@app.route(route_mqafaq_internalspice3)
@login_required
def mqafaqinternalspice3():
    recordPostHistory(route_mqafaq_internalspice3)
    return render_template('/faq/mqa/enableInternalSpice3.html')


route_mqafaq_2port = '/mqafaq/2port'


@app.route(route_mqafaq_2port)
@login_required
def mqafaq_2port():
    recordPostHistory(route_mqafaq_2port)
    return render_template('/faq/mqa/2portSY.html')


route_mqafaq_openoffice = '/mqafaq/openoffice'


@app.route(route_mqafaq_openoffice)
@login_required
def mqafaq_openoffice():
    recordPostHistory(route_mqafaq_openoffice)
    return render_template('/faq/mqa/openoffice.html')


route_mqafaq_TightLoopWithMeasData = '/mqafaq/TightLoopWithMeasData'


@app.route(route_mqafaq_TightLoopWithMeasData)
@login_required
def mqafaq_TightLoopWithMeasData():
    recordPostHistory(route_mqafaq_TightLoopWithMeasData)
    return render_template('/faq/mqa/TightLoopWithMeasData.html')


route_mqafaq_instNameMapping = '/mqafaq/instNameMapping'


@app.route(route_mqafaq_instNameMapping)
@login_required
def mqafaq_instNameMapping():
    recordPostHistory(route_mqafaq_instNameMapping)
    return render_template('/faq/mqa/instNameMapping.html')


route_mqafaq_meas1 = '/mqafaq/meas1'


@app.route(route_mqafaq_meas1)
@login_required
def mqafaq_meas1():
    recordPostHistory(route_mqafaq_meas1)
    return render_template('/faq/mqa/mea_qa.html')


route_mqafaq_meas2 = '/mqafaq/meas2'


@app.route(route_mqafaq_meas2)
@login_required
def mqafaq_meas2():
    recordPostHistory(route_mqafaq_meas2)
    return render_template('/faq/mqa/mea_acc.html')


route_mqafaq_meas3 = '/mqafaq/meas3'


@app.route(route_mqafaq_meas3)
@login_required
def mqafaq_meas3():
    recordPostHistory(route_mqafaq_meas3)
    return render_template('/faq/mqa/mea_idsat.html')


route_mqafaq_meas4 = '/mqafaq/meas4'


@app.route(route_mqafaq_meas4)
@login_required
def mqafaq_meas4():
    recordPostHistory(route_mqafaq_meas4)
    return render_template('/faq/mqa/mea_vth.html')


route_mqafaq_meas_misc1 = '/mqafaq/meas_misc1'


@app.route(route_mqafaq_meas_misc1)
@login_required
def mqafaq_meas_misc1():
    recordPostHistory(route_mqafaq_meas_misc1)
    return render_template('/faq/mqa/datablock.html')


route_mqafaq_slope = '/mqafaq/slope'


@app.route(route_mqafaq_slope)
@login_required
def mqafaq_slope1():
    recordPostHistory(route_mqafaq_slope)
    return render_template('/faq/mqa/slope.html')


route_download_bsim4_model_meas = '/mqafaq/meas/bsim4_model/download'


@app.route(route_download_bsim4_model_meas)
@login_required
def download_bsim4_model_meas():
    recordPostHistory(route_download_bsim4_model_meas)
    return send_file('static/faq/mqa/meas_acc/bsim4_model.l',
                     attachment_filename='bsim4_model.l', mimetype='text/rule', as_attachment=True)



route_mqafaq_helpfile = '/mqafaq/helpfile'


@app.route(route_mqafaq_helpfile)
@login_required
def mqafaq_helpfile():
    recordPostHistory(route_mqafaq_helpfile)
    return render_template('/faq/mqa/helpfile.html')


#### ICCAP FAQ ######

route_iccapfaq_saveInstToMDM = '/iccapfaq/saveInstToMDM'


@app.route(route_iccapfaq_saveInstToMDM)
@login_required
def iccapfaqsaveInstToMDM():
    recordPostHistory(route_iccapfaq_saveInstToMDM)
    return render_template('/faq/iccap/saveInstToMDM.html')


route_iccapfaq_link2ext = '/iccapfaq/link2ext'


@app.route(route_iccapfaq_link2ext)
@login_required
def iccapfaq_link2ext():
    recordPostHistory(route_iccapfaq_link2ext)
    return render_template('/faq/iccap/link2externalsim.html')


route_iccapfaq_link2ltspice = '/iccapfaq/link2ltspice'


@app.route(route_iccapfaq_link2ltspice)
@login_required
def iccapfaq_link2ltspice():
    recordPostHistory(route_iccapfaq_link2ltspice)
    return render_template('/faq/iccap/link2ltspice.html')


route_iccapfaq_link2ads = '/iccapfaq/link2ads'


@app.route(route_iccapfaq_link2ads)
@login_required
def iccapfaq_link2ads():
    recordPostHistory(route_iccapfaq_link2ads)
    return render_template('/faq/iccap/link2ads.html')


route_iccapfaq_link2spectre = '/iccapfaq/link2spectre'


@app.route(route_iccapfaq_link2spectre)
@login_required
def iccapfaq_link2spectre():
    recordPostHistory(route_iccapfaq_link2spectre)
    return render_template('/faq/iccap/link2spectre.html')


route_iccapfaq_llink2hspice = '/iccapfaq/link2hspice'


@app.route(route_iccapfaq_llink2hspice)
@login_required
def iccapfaq_link2hspice():
    recordPostHistory(route_iccapfaq_llink2hspice)
    return render_template('/faq/iccap/link2hspice.html')


route_iccapfaq_spice3 = '/iccapfaq/link2spice3'


@app.route(route_iccapfaq_spice3)
@login_required
def iccapfaq_link2spice3():
    recordPostHistory(route_iccapfaq_spice3)
    return render_template('/faq/iccap/link2spice3.html')


route_iccapfaq_link2pspice = '/iccapfaq/link2pspice'


@app.route(route_iccapfaq_link2pspice)
@login_required
def iccapfaq_link2pspice3():
    recordPostHistory(route_iccapfaq_link2pspice)
    return render_template('/faq/iccap/link2pspice.html')



route_iccapfaq_usersimfile = '/iccapfaq/usersimfile'


@app.route(route_iccapfaq_usersimfile)
@login_required
def iccapfaq_usersimfile():
    recordPostHistory(route_iccapfaq_usersimfile)
    return render_template('/faq/iccap/usersimfile.html')


route_iccapfaq_recentfiles = '/iccapfaq/recentfiles'


@app.route(route_iccapfaq_recentfiles)
@login_required
def iccapfaq_recentfiles():
    recordPostHistory(route_iccapfaq_recentfiles)
    return render_template('/faq/iccap/recentfiles.html')

### WPE FAQs ###

route_wpefaq_probecard = '/wpefaq/add_probecard'


@app.route(route_wpefaq_probecard)
@login_required
def wpefaq_addprobecard():
    recordPostHistory(route_wpefaq_probecard)
    return render_template('/faq/wpe/add_probecard.html')


### ALFNA FAQs ###
route_alfnafaq_40mhz = '/alfnafaq/40mhz'


@app.route(route_alfnafaq_40mhz)
@login_required
def alfnafaq_40mhz():
    recordPostHistory(route_alfnafaq_40mhz)
    return render_template('/faq/alfna/40mhz.html')


route_alfnafaq_system_noise_floor = '/alfnafaq/system_noise_floor'


@app.route(route_alfnafaq_system_noise_floor)
@login_required
def alfnafaq_system_noise_floor():
    recordPostHistory(route_alfnafaq_system_noise_floor)
    return render_template('/faq/alfna/system_noise_floor.html')


route_alfnafaq_rload_usage = '/alfnafaq/rload_usage'


@app.route(route_alfnafaq_rload_usage)
@login_required
def alfnafaq_rload_usage():
    recordPostHistory(route_alfnafaq_rload_usage)
    return render_template('/faq/alfna/rload_usage.html')


route_alfnafaq_setod = '/alfnafaq/setod'


@app.route(route_alfnafaq_setod)
@login_required
def alfnafaq_setod():
    recordPostHistory(route_alfnafaq_setod)
    return render_template('/faq/alfna/setod.html')


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


route_mqarules_vth_finfet = '/mqarules/vth_finfet'


@app.route(route_mqarules_vth_finfet)
@login_required
def mqarulesVthfinfet():
    recordPostHistory(route_mqarules_vth_finfet)
    return render_template('/mqarules/rules/vthcon_finfet.html')


route_mqarules_sweepFromNegaiveVgs = '/mqarules/sweepFromNegativeVgs'


@app.route(route_mqarules_sweepFromNegaiveVgs)
@login_required
def mqarulessweepFromNegaiveVgs():
    recordPostHistory(route_mqarules_sweepFromNegaiveVgs)
    return render_template('/mqarules/rules/sweepFromNegaiveVgs.html')


route_mqarules_synchro = '/mqarules/synchro'


@app.route(route_mqarules_synchro)
@login_required
def mqarulessynchro():
    recordPostHistory(route_mqarules_synchro)
    return render_template('/mqarules/rules/synchro.html')


route_mqarules_normalize = '/mqarules/normalize'


@app.route(route_mqarules_normalize)
@login_required
def mqarulesnormalize():
    recordPostHistory(route_mqarules_normalize)
    return render_template('/mqarules/rules/normalize.html')


route_mqarules_ideff = '/mqarules/ideff'


@app.route(route_mqarules_ideff)
@login_required
def mqarulesIdeff():
    recordPostHistory(route_mqarules_ideff)
    return render_template('/mqarules/rules/ideff.html')


route_mqarules_mis_hsp_mos = '/mqarules/misHspMos'


@app.route(route_mqarules_mis_hsp_mos)
@login_required
def mqarulesmismatch_hsp_mos():
    recordPostHistory(route_mqarules_mis_hsp_mos)
    return render_template('/mqarules/rules/mismatch_hsp_mos.html')


route_mqarules_mis_hsp_mos_finfet = '/mqarules/misHspMos_finfet'


@app.route(route_mqarules_mis_hsp_mos_finfet)
@login_required
def mqarulesmismatch_hsp_mos_finfet():
    recordPostHistory(route_mqarules_mis_hsp_mos_finfet)
    return render_template('/mqarules/rules/mismatch_hsp_mos_finfet.html')


route_mqarules_mis_spe_mos = '/mqarules/misSpeMos'


@app.route(route_mqarules_mis_spe_mos)
@login_required
def mqarulesmismatch_spe_mos():
    recordPostHistory(route_mqarules_mis_spe_mos)
    return render_template('/mqarules/rules/mismatch_spe_mos.html')


route_mqarules_symm = '/mqarules/symm'


@app.route(route_mqarules_symm)
@login_required
def mqarule_symm():
    recordPostHistory(route_mqarules_symm)
    return render_template('/mqarules/rules/symm.html')


route_mqarules_misR = '/mqarules/misR'


@app.route(route_mqarules_misR)
@login_required
def mqarule_misR():
    recordPostHistory(route_mqarules_misR)
    return render_template('/mqarules/rules/mismatch_hsp_res.html')


route_mqarules_wpe = '/mqarules/wpe'


@app.route(route_mqarules_wpe)
@login_required
def mqarule_wpe():
    recordPostHistory(route_mqarules_wpe)
    return render_template('/mqarules/rules/wpe.html')


route_mqarules_fn_spe_finfet = '/mqarules/fn_spe_finfet'


@app.route(route_mqarules_fn_spe_finfet)
@login_required
def mqarule_fn_spe_finfet():
    recordPostHistory(route_mqarules_fn_spe_finfet)
    return render_template('/mqarules/rules/fn_spe_finfet.html')


route_mqarules_dibl = '/mqarules/dibl'


@app.route(route_mqarules_dibl)
@login_required
def mqarule_dibl():
    recordPostHistory(route_mqarules_dibl)
    return render_template('/mqarules/rules/dibl.html')


route_mqarules_cgscgd = '/mqarules/cgscgd'


@app.route(route_mqarules_cgscgd)
@login_required
def mqarule_cgscgd():
    recordPostHistory(route_mqarules_cgscgd)
    return render_template('/mqarules/rules/cgscgd.html')


route_mqarules_cxy = '/mqarules/cxy'


@app.route(route_mqarules_cxy)
@login_required
def mqarule_cxy():
    recordPostHistory(route_mqarules_cxy)
    return render_template('/mqarules/rules/cxy.html')


route_mqarules_crss = '/mqarules/crss_ciss_coss'


@app.route(route_mqarules_crss)
@login_required
def mqarule_crss():
    recordPostHistory(route_mqarules_crss)
    return render_template('/mqarules/rules/crss.html')


route_mqarules_meas = '/mqarules/meas_qa'


@app.route(route_mqarules_meas)
@login_required
def mqarule_meas():
    recordPostHistory(route_mqarules_meas)
    return render_template('/mqarules/rules/meas_qa.html')


route_mqarules_vtgm = '/mqarules/vtgm'


@app.route(route_mqarules_vtgm)
@login_required
def mqarule_vtgm():
    recordPostHistory(route_mqarules_vtgm)
    return render_template('/mqarules/rules/vtgm.html')


route_mqarules_compdiff_a = '/mqarules/compdiff_a'


@app.route(route_mqarules_compdiff_a)
@login_required
def mqarule_compdiff_a():
    recordPostHistory(route_mqarules_compdiff_a)
    return render_template('/mqarules/rules/compdiff_a.html')


route_mqarules_select = '/mqarules/select'


@app.route(route_mqarules_select)
@login_required
def mqarule_select():
    recordPostHistory(route_mqarules_select)
    return render_template('/mqarules/rules/select.html')
#### Video Demos
route_video = '/video'


@app.route(route_video)
@login_required
def videoindex():
    recordPostHistory(route_video)
    return render_template('/video/video_index.html')


route_video_mqaHvsS = '/video/mqaHvsS'


@app.route(route_video_mqaHvsS)
@login_required
def videomqaHvsS():
    recordPostHistory(route_video_mqaHvsS)
    return render_template('/video/MQA_HvsS.html')


route_video_MQA_check_netlist = '/video/mqachecknetlist'


@app.route(route_video_MQA_check_netlist)
@login_required
def videomqachecknetlist():
    recordPostHistory(route_video_MQA_check_netlist)
    return render_template('/video/MQA_check_netlist.html')


route_video_MQA_NearVth = '/video/MQA_NearVth'


@app.route(route_video_MQA_NearVth)
@login_required
def videoMQA_NearVth():
    recordPostHistory(route_video_MQA_NearVth)
    return render_template('/video/MQA_NearVth.html')


route_video_MQA_SimVerComp = '/video/MQA_SimVerComp'


@app.route(route_video_MQA_SimVerComp)
@login_required
def videoMQA_SimVerComp():
    recordPostHistory(route_video_MQA_SimVerComp)
    return render_template('/video/MQA_SimVerComp.html')


route_video_MBP_check_netlist = '/video/MBP_check_netlist'


@app.route(route_video_MBP_check_netlist)
@login_required
def videoMBP_check_netlist():
    recordPostHistory(route_video_MBP_check_netlist)
    return render_template('/video/MBP_check_netlist.html')


route_video_MBP_tabs_sfloat = '/video/MBP_tabs_sfloat'


@app.route(route_video_MBP_tabs_sfloat)
@login_required
def videoMBP_tabs_sfloat():
    recordPostHistory(route_video_MBP_tabs_sfloat)
    return render_template('/video/MBP_tabs_sfloat.html')


route_video_MBP_comp_models = '/video/MBP_comp_models'


@app.route(route_video_MBP_comp_models)
@login_required
def videoMBP_comp_models():
    recordPostHistory(route_video_MBP_comp_models)
    return render_template('/video/MBP_comp_models.html')


route_video_MBP_pseudo_data = '/video/MBP_pseudo_data'


@app.route(route_video_MBP_pseudo_data)
@login_required
def videoMBP_pseudo_data():
    recordPostHistory(route_video_MBP_pseudo_data)
    return render_template('/video/MBP_pseudo_data.html')


route_video_MBP_multiDie_data = '/video/MBP_multiDie_data'


@app.route(route_video_MBP_multiDie_data)
@login_required
def videoMBP_multiDie_data():
    recordPostHistory(route_video_MBP_multiDie_data)
    return render_template('/video/MBP_multiDie_data.html')


route_video_MBP_export_pdf = '/video/MBP_export_pdf'


@app.route(route_video_MBP_export_pdf)
@login_required
def videoMBP_export_pdf():
    recordPostHistory(route_video_MBP_export_pdf)
    return render_template('/video/MBP_export_pdf.html')


route_video_MBP_set_gminDC = '/video/MBP_set_gminDC'


@app.route(route_video_MBP_set_gminDC)
@login_required
def videoMBP_set_gminDC():
    recordPostHistory(route_video_MBP_set_gminDC)
    return render_template('/video/MBP_set_gminDC.html')


route_video_MBP_bigger_RMS = '/video/MBP_bigger_RMS'


@app.route(route_video_MBP_bigger_RMS)
@login_required
def videoMBP_bigger_RMS():
    recordPostHistory(route_video_MBP_bigger_RMS)
    return render_template('/video/MBP_bigger_RMS.html')


route_video_MBP_sigNum_symbolSize = '/video/MBP_sigNum_symbolSize'


@app.route(route_video_MBP_sigNum_symbolSize)
@login_required
def videoMBP_sigNum_symbolSize():
    recordPostHistory(route_video_MBP_sigNum_symbolSize)
    return render_template('/video/MBP_sigNum_symbolSize.html')


route_video_MBP_RMS_algor = '/video/MBP_RMS_algor'


@app.route(route_video_MBP_RMS_algor)
@login_required
def videoMBP_RMS_algor():
    recordPostHistory(route_video_MBP_RMS_algor)
    return render_template('/video/MBP_RMS_algor.html')


route_video_MBP_Ion_Ioff = '/video/MBP_Ion_Ioff_Correlation'


@app.route(route_video_MBP_Ion_Ioff)
@login_required
def videoMBP_Ion_Ioff():
    recordPostHistory(route_video_MBP_Ion_Ioff)
    return render_template('/video/MBP_Ion_Ioff_correlation.html')


route_video_MBP_dIdsat_sa = '/video/MBP_dIdsat_by_SA'


@app.route(route_video_MBP_dIdsat_sa)
@login_required
def videoMBP_dIdsat_sa():
    recordPostHistory(route_video_MBP_dIdsat_sa)
    return render_template('/video/MBP_dIdsat_SA.html')


route_video_MBP_IV_T = '/video/MBP_IV_T'


@app.route(route_video_MBP_IV_T)
@login_required
def videoMBP_IV_T():
    recordPostHistory(route_video_MBP_IV_T)
    return render_template('/video/MBP_IV_diff_T.html')


route_video_MBP_diff_res = '/video/MBP_diff_res'


@app.route(route_video_MBP_diff_res)
@login_required
def videoMBP_diff_res():
    recordPostHistory(route_video_MBP_diff_res)
    return render_template('/video/MBP_use_diff_res.html')


route_video_ICCAP_OPEN_GUI = '/video/ICCAP_OPEN_GUI'


@app.route(route_video_ICCAP_OPEN_GUI)
def videoICCAP_OPEN_GUI():
    recordPostHistory(route_video_ICCAP_OPEN_GUI)
    return render_template('/video/ICCAP_open_gui.html')


route_video_iccap_bjt_modeling = '/video/iccap_bjt_modeling'


@app.route(route_video_iccap_bjt_modeling)
def videoiccap_bjt_modeling():
    recordPostHistory(route_video_iccap_bjt_modeling)
    return render_template('/video/ICCAP_bjt_modeling.html')


route_video_mbp_sram = '/video/mbp_sram'


@app.route(route_video_mbp_sram)
def videombp_sram():
    recordPostHistory(route_video_mbp_sram)
    return render_template('/video/MBP_sram.html')


route_video_MBP_recenter = '/video/MBP_recentering'
@app.route(route_video_MBP_recenter)
@login_required
def videoMBP_recenter():
    recordPostHistory(route_video_MBP_recenter)
    return render_template('/video/MBP_ReCentering.html')


######################



def getPostViewTimeById(uid):
    post = PostHistory.query.filter(PostHistory.id == uid).first()
    if type(post).__name__ == 'NoneType':
        return ''
    return post.date


def getPostIdByRoute(myroute):
    post = Post.query.filter(Post.route == myroute).first()
    if type(post).__name__ == 'NoneType':
        return -1
    return post.id


def getPostRouteById(pid):
    post = Post.query.filter(Post.id == pid).first()
    if type(post).__name__ == 'NoneType':
        return ''
    return post.route


def getPostTitleByRoute(myroute):
    post = Post.query.filter(Post.route == myroute).first()
    if type(post).__name__ == 'NoneType':
        return myroute
    return post.title


def getUserNameById(user_id):
    if int(user_id) == -1:
        return 'public'
    user = User.query.filter(User.id == user_id).first()
    return user.username


def getEmailById(user_id):
    if int(user_id) == -1:
        return ''
    user = User.query.filter(User.id == user_id).first()
    return user.email


def getCompanybyId(user_id):
    if int(user_id) == -1:
        return 'public'
    user = User.query.filter(User.id == user_id).first()
    return user.company


def getPostCategoryById(pid):
    post = Post.query.filter(Post.id == pid).first()
    if type(post).__name__ == 'NoneType':
        return ''
    return post.category


def getPostCategoryByRoute(route):
    post = Post.query.filter(Post.route == route).first()
    if type(post).__name__ == 'NoneType':
        if route == '/mbpst':
            return 'mbpst'
        elif route == '/video':
            return 'video'
        elif route == '/mbpfaq':
            return 'mbpfaq'
        elif route == '/mqafaq':
            return 'mqafaq'
        elif route == '/wpefaq':
            return 'wpefaq'
        elif route == '/blog':
            return 'blog'
        elif route == '/iccapfaq':
            return 'iccapfaq'
        elif route == '/pyrfs':
            return 'pyrfs'
        else:
            return ''
    return post.category


def getCategory(txt):
    if txt == 'mbpst':
        return "MBP Script Tutorial"
    elif txt == "mbpfaq":
        return "MBP FAQ"
    elif txt == "wpefaq":
        return "WPE FAQ"
    elif txt == "alfnafaq":
        return "ALFNA FAQ"
    elif txt == "video":
        return "Video Demos"
    elif txt == "mqarules":
        return "MQA Rules"
    elif txt == "mqafaq":
        return "MQA FAQ"
    elif txt == "iccapfaq":
        return "ICCAP FAQ"
    elif txt == "blog":
        return "Blog"
    elif txt == "pyrfs":
        return "PyRFS"

    return "Other"


#### dashboard  ####
route_dashboard = '/dashboard01.46738.99846kkli58010_odugjfkadj!jf.11'


@app.route(route_dashboard)
@roles_required('sunshine')
@login_required
def dashboard():
    # recordPostHistory(route_dashboard)
    # PostHistory.query.filter(PostHistory.user_id == id).filter(PostHistory.route == rt).all()
    iccapPost = Post.query.filter(Post.category == 'iccapfaq').all()
    iccap_ct = iccapPost.__len__() + 1

    service_ct = 1  # why DM services
    blogPost = Post.query.filter(Post.category == 'blog').all()
    blog_ct = blogPost.__len__()

    mbpPost = Post.query.filter((Post.category == 'mbpst') | (Post.category == 'mbpfaq')).all()
    mbp_ct = mbpPost.__len__()
    mqaPost = Post.query.filter((Post.category == 'mqafaq') | (Post.category == 'mqarules')).all()
    mqa_ct = mqaPost.__len__()
    wpePost = Post.query.filter((Post.category == 'wpefaq')).all()
    wpe_ct = wpePost.__len__()
    alfnaPost = Post.query.filter((Post.category == 'alfnafaq')).all()
    alfna_ct = alfnaPost.__len__()
    videoPost = Post.query.filter((Post.category == 'video')).all()
    video_ct = videoPost.__len__()

    users = User.query.all()
    user_ct = users.__len__() - 3  # except internal testing account
    searches = SearchHistory.query.all()
    search_ct = searches.__len__()

    postHis = PostHistory.query.order_by(desc(PostHistory.route)).all()

    ### for for post his rate
    routes = []
    for p in postHis:
        routes.append(p.route)

    rz = Counter(routes).items()
    sortedRt = reversed(sorted(rz, key=operator.itemgetter(1)))

    postTop = []
    tmp = 0
    for ii in sortedRt:
        title = getPostTitleByRoute(ii[0])
        if title == '':
            continue
        if title.__len__() >= 35:
            title = title[0:35] + '...'
        # route, title, count, category
        postTop.append((ii[0], title, ii[1], getCategory(getPostCategoryByRoute(ii[0]))))
        tmp += 1
        if tmp >= 20:
            break

    ### look for user info
    ids = []
    for p in postHis:
        ids.append(p.user_id)

    iz = Counter(ids).items()

    sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))  # user_id, count
    userHis = []  # user id, user name, email, count
    for ii in sortedIz:
        if ii[0] == 1 or ii[0] == 2 or ii[0] == 3:
            continue
        userHis.append((ii[0], getUserNameById(ii[0]), getEmailById(ii[0]), getCompanybyId(ii[0]), ii[1]))

    # search list

    searchList = SearchHistory.query.order_by(desc(SearchHistory.date)).limit(20).all()
    sList = []
    for item in searchList:
        # search text 0, date 1, userName 2, company 3, user_id 4,
        sList.append(
            (item.search_string, str(item.date)[:-10], getUserNameById(item.user_id), getCompanybyId(item.user_id),
             item.user_id))

    # latestViews
    postHis = PostHistory.query.order_by(desc(PostHistory.date)).all()
    if postHis.__len__() > 20:  # get the last 20 views.
        postHis = postHis[:20]

    latestViews = []
    for item in postHis:
        uid = item.user_id
        route = item.route
        title = getPostTitleByRoute(route)
        # route, date,title,userName, email, company, category, uid
        if title.__len__() > 30:
            title = title[:30] + '...'
        latestViews.append(
            (route, str(item.date)[:-10], title, getUserNameById(uid), getEmailById(uid), getCompanybyId(uid),
             getPostCategoryByRoute(route), uid))

    postHis = PostHistory.query.order_by(desc(PostHistory.date)).all()
    downloads = []
    for item in postHis:
        route = item.route
        uid = item.user_id
        if str(route).endswith('download'):
            # route 0, date 1, user name 2, email 3, company 4, uid 5
            downloads.append((route, item.date, getUserNameById(uid), getEmailById(uid), getCompanybyId(uid), uid))

    # get company count

    company_ct = 0
    companyHis = User.query.order_by(User.company).all()
    # company_ct = companyHis.__len__()

    ### for for post his rate
    companyList = []
    for p in companyHis:
        tmpcmp = p.company
        # if tmpcmp==None:
        #     tmpcmp='public'
        companyList.append(tmpcmp)

    rz = Counter(companyList).items()
    # print(type(rz))
    # print(rz)
    # sortedCompanyList = reversed(sorted(rz, key=operator.itemgetter(1)))
    sortedCompanyList = sorted(rz)
    company_ct = rz.__len__() - 1
    companListForDisplay = []
    companyIndex = 1
    for cmp in sortedCompanyList:
        # index, company name, count of a company
        companListForDisplay.append((companyIndex, cmp[0], cmp[1], viewCountTotalByCompany(cmp[0])))
        companyIndex = companyIndex + 1
    # summarize Public view #, too
    companListForDisplay.append((companyIndex, 'Public', 1, getViewCountByUserID(-1)))
    # total view #
    postHis = PostHistory.query.filter(PostHistory.user_id != 3).order_by(desc(PostHistory.date)).all()
    totalViewCount = postHis.__len__()

    return render_template('/dashboard.html', iccap_ct=iccap_ct, mbp_ct=mbp_ct, mqa_ct=mqa_ct, wpe_ct=wpe_ct,
                           alfna_ct=alfna_ct,
                           video_ct=video_ct, blog_ct=blog_ct, service_ct=service_ct,
                           user_ct=user_ct, search_ct=search_ct, postTop=postTop, userHis=userHis,
                           searchList=sList, getPostIdFunc=getPostIdByRoute, latestViews=latestViews,
                           downloads=downloads, company_ct=company_ct, companListForDisplay=companListForDisplay,
                           totalViewCount=totalViewCount)


def viewCountTotalByCompany(companyName):
    userHis = User.query.filter(User.company == companyName).all()
    totalCt = 0
    for p in userHis:
        viewCt = getViewCountByUserID(p.id)
        totalCt = totalCt + viewCt

    return totalCt


rount_from_company = '/fromCompany/<companyName>'


@app.route(rount_from_company)
@roles_required('sunshine')
@login_required
def dashboard_from_company(companyName):
    companyUsers = []
    userHis = User.query.filter(User.company == companyName).all()
    for p in userHis:
        # name, email, last login time, last login IP, view #, user.id
        companyUsers.append((p.username, p.email, p.last_login_at, p.last_login_ip, getViewCountByUserID(p.id), p.id))

    return render_template('/fromCompany.html', companyUsers=companyUsers, companyName=companyName)


def getViewCountByUserID(uid):
    UserHis = PostHistory.query.filter(PostHistory.user_id == uid).all()

    return UserHis.__len__()


route_dashboard_chart_view = '/chart_view_98adsfhrhwgijj!!kjfskvgahvg877awefjkjdfkagh0248_df83j'


@app.route(route_dashboard_chart_view)
@roles_required('sunshine')
@login_required
def dashboard_chart_view():
    iccapPost = Post.query.filter(Post.category == 'iccap').all()
    iccap_ct = iccapPost.__len__() + 1

    service_ct = 1  # why DM services
    blogPost = Post.query.filter(Post.category == 'blog').all()
    blog_ct = blogPost.__len__()

    mbpPost = Post.query.filter((Post.category == 'mbpst') | (Post.category == 'mbpfaq')).all()
    mbp_ct = mbpPost.__len__()
    mqaPost = Post.query.filter((Post.category == 'mqafaq') | (Post.category == 'mqarules')).all()
    mqa_ct = mqaPost.__len__()
    wpePost = Post.query.filter((Post.category == 'wpefaq')).all()
    wpe_ct = wpePost.__len__()
    alfnaPost = Post.query.filter((Post.category == 'alfnafaq')).all()
    alfna_ct = alfnaPost.__len__()
    videoPost = Post.query.filter((Post.category == 'video')).all()
    video_ct = videoPost.__len__()

    style_contents = Style(
        label_font_size=25,
        major_label_font_size=25,
        value_font_size=25,
        title_font_size=30

    )

    contents_chart = pygal.Bar(style=style_contents, print_values=True, show_legend=False, height=400)

    totalPostCount = mbp_ct + mqa_ct + iccap_ct + video_ct + blog_ct + wpe_ct + alfna_ct + service_ct
    contents_chart.title = 'Contents (total: ' + str(totalPostCount) + ' )'
    contents_chart.x_labels = ('MBP', 'MQA', 'ICCAP', 'Video', 'Blog', 'WPE', 'ALFNA', 'Service')
    contents_chart.add("", [mbp_ct, mqa_ct, iccap_ct, video_ct, blog_ct, wpe_ct, alfna_ct, service_ct])

    contents_graph = contents_chart.render_data_uri()

    # view count by User
    postHis = PostHistory.query.filter(PostHistory.user_id != 3).order_by(desc(PostHistory.date)).all()
    ### look for user info
    ids = []
    for p in postHis:
        ids.append(p.user_id)

    iz = Counter(ids).items()
    sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))  # user_id, count
    nameList = []
    countList = []
    for ii in sortedIz:
        uid = ii[0]
        if uid == 1 or uid == 2 or uid == 3:
            continue
        uid = ii[0]
        nameList.append(getUserNameById(uid))
        countList.append(ii[1])

    style_userView = Style(
        label_font_size=20,
        major_label_font_size=20,
        value_font_size=20,
        title_font_size=25

    )
    # height = 400, width = 1000, spacing = 20,
    userView_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False, x_label_rotation=-60)
    userView_chart.title = 'User View # (total: ' + str(postHis.__len__()) + ')'
    userView_chart.x_labels = nameList
    userView_chart.add("", countList)
    userView_graph = userView_chart.render_data_uri()

    # top 30 view title

    postHis = PostHistory.query.filter(PostHistory.user_id != 3).order_by((PostHistory.route)).all()

    ### for for post his rate
    routes = []
    for p in postHis:
        routes.append(p.route)

    rz = Counter(routes).items()  # route, count
    sortedRt = reversed(sorted(rz, key=operator.itemgetter(1)))  # sort by count

    titleList = []
    countTitleList = []
    postTop = []
    tmp = 0
    for ii in sortedRt:
        route = ii[0]
        title = getPostTitleByRoute(route)
        if title == '':
            continue
        if title.__len__() >= 35:
            title = title[:35] + '...'
        titleList.append(title)
        countTitleList.append(ii[1])
        tmp += 1
        if tmp >= 30:
            break

    topView_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False, x_label_rotation=-60)
    topView_chart.title = 'Top 30 Posts'
    topView_chart.x_labels = titleList
    topView_chart.add("", countTitleList)

    topView_graph = topView_chart.render_data_uri()

    # View count by Category

    postHisAll = PostHistory.query.order_by(PostHistory.route).all()
    cates = []
    for p in postHisAll:
        route = p.route
        cates.append(getCategory(getPostCategoryByRoute(route)))

    rz = Counter(cates).items()  # category, count
    sortedCates = reversed(sorted(rz, key=operator.itemgetter(1)))  # sort by count
    cateNameList = []
    cateCountList = []
    for ii in sortedCates:
        cateNameList.append(ii[0])
        cateCountList.append(ii[1])

    countByCategory_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False, x_label_rotation=-20)
    countByCategory_chart.title = 'View # by Category'
    countByCategory_chart.x_labels = cateNameList
    countByCategory_chart.add("", cateCountList)
    countByCategory_graph = countByCategory_chart.render_data_uri()

    # user # by Category
    tmp = []
    for p in postHisAll:
        route = p.route
        tmp.append(route)

    rz = Counter(tmp).items()  # route, count

    sortedRoute = reversed(sorted(rz, key=operator.itemgetter(1)))  # sort by count

    ucNames = []
    ucCounts = []
    tmp2 = {}
    for ss in sortedRoute:
        route = ss[0]
        ppp = PostHistory.query.filter(PostHistory.route == route).all()
        userList = []
        for p in ppp:
            uid = p.user_id
            userList.append(uid)

        uidCt = Counter(userList).items()  # uid,count

        cate = getCategory(getPostCategoryByRoute(route))
        if cate not in tmp2.keys():
            tmp2[cate] = uidCt.__len__()
        else:
            tmp2[cate] = tmp2[cate] + uidCt.__len__()

    for item in tmp2.items():
        ucNames.append(item[0])
        ucCounts.append(item[1])

    userCountByCategory_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False,
                                          x_label_rotation=-20)
    userCountByCategory_chart.title = 'User # by Category'
    userCountByCategory_chart.x_labels = ucNames
    userCountByCategory_chart.add("", ucCounts)
    userCountByCategory_graph = userCountByCategory_chart.render_data_uri()

    return render_template('/dashboard_chart_view.html', contents_graph=contents_graph, userView_graph=userView_graph,
                           topView_graph=topView_graph, countByCategory_graph=countByCategory_graph,
                           userCountByCategory_graph=userCountByCategory_graph)


route_recent_100_search = '/recent100SearchHis'


@app.route(route_recent_100_search)
@roles_required('sunshine')
@login_required
def recent100Search():
    # searchAll = SearchHistory.query.order_by(desc(SearchHistory.date)).limit(100).all()
    # sAll = []
    # for item in searchAll:
    #     sAll.append(item.search_string)
    #
    # iz = Counter(sAll).items()
    # sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))  # string, count
    # userHis = []  #
    # for ii in sortedIz:
    #     userHis.append((ii[0], ii[1]))
    # search list

    searchList = SearchHistory.query.order_by(desc(SearchHistory.date)).filter(SearchHistory.user_id != 3).all()
    # print('search:', searchList.__len__())
    if searchList.__len__() > 100:
        searchList = searchList[:100]
    sList = []
    for item in searchList:
        # search text 0, date 1, userName 2, company 3
        sList.append(
            (item.search_string, str(item.date)[:-10], getUserNameById(item.user_id), getCompanybyId(item.user_id)))

    return render_template('/recent100Searches.html', sList=sList)


route_page_view_his = '/page_view_his'


@app.route(route_page_view_his)
@roles_required('sunshine')
@login_required
def page_view_his():
    return render_template('/pageViewHis.html')


route_page_view_his_submit = '/page_view_his_submit'


@app.route(route_page_view_his_submit, methods=['POST'])
@roles_required('sunshine')
@login_required
def page_view_his_submit():
    route = request.form['route'].strip()
    if route.__len__() > 2:
        route = route[1:]
    return redirect(url_for('user_post_viewed_by_users', route=route))


# post viewed by users
route_post_viewed_by_users = '/viewerListFor/<path:route>'


@app.route(route_post_viewed_by_users)
@roles_required('sunshine')
@login_required
def user_post_viewed_by_users(route):
    route = '/' + route

    viewers = PostHistory.query.filter(PostHistory.route == route).all()
    vv = []
    for vi in viewers:
        uid = vi.user_id
        vv.append(uid)
    iz = Counter(vv).items()

    sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))  # uid, count
    userHis = []  # uid, user name, email, company, count
    for ii in sortedIz:
        if ii[0] == 1 or ii[0] == 2 or ii[0] == 3:
            continue
        userHis.append((ii[0], getUserNameById(ii[0]), getEmailById(ii[0]), getCompanybyId(ii[0]), ii[1]))

    return render_template('/viewerListFor.html', userHis=userHis, route=route, title=getPostTitleByRoute(route))


route_last_300_views = '/last_300_views'


@app.route(route_last_300_views)
@roles_required('sunshine')
@login_required
def last200views():
    # latestViews
    postHis = PostHistory.query.order_by(desc(PostHistory.date)).all()
    if postHis.__len__() > 300:  # get the last 200 views.
        postHis = postHis[:300]

    latestViews = []
    for item in postHis:
        uid = item.user_id
        route = item.route
        title = getPostTitleByRoute(route)
        # route, date,title,userName, email, company, category
        if title.__len__() > 30:
            title = title[:30] + '...'
        latestViews.append(
            (route, str(item.date)[:-10], title, getUserNameById(uid), getEmailById(uid), getCompanybyId(uid),
             getPostCategoryByRoute(route)))

    return render_template('/last300views.html', latestViews=latestViews)


# user history view
route_user_view_history = '/user_view_history/<uid>'


@app.route(route_user_view_history)
@roles_required('sunshine')
@login_required
def userViewHistory(uid):
    id = current_user.id
    flag = False
    if id == 3:  # only CS can view others
        flag = True
    else:  # view oneself.
        if id == uid:
            flag = True

    if flag:
        # print('uid', uid)

        uname = getUserNameById(uid)
        postHis = PostHistory.query.filter(PostHistory.user_id == uid).order_by(desc(PostHistory.date)).all()
        vl = []
        titleList = []
        cateList = []
        for v in postHis:
            route = v.route
            cateList.append(getCategory(getPostCategoryByRoute(route)))
            title = getPostTitleByRoute(route)
            if title.__len__() > 30:
                title = title[:29] + '...'

            titleList.append(title)
            date = getPostViewTimeById(v.id)
            if title != '':
                # title 1, route, 2, date 3, category 4
                vl.append((title, route, str(date)[:-10], getPostCategoryByRoute(route)))

        searchHis = SearchHistory.query.filter(SearchHistory.user_id == uid).order_by(SearchHistory.date).all()
        sList = []
        for v in searchHis:
            sList.append((v.search_string, str(v.date)[:-10]))

        style_userView = Style(
            label_font_size=20,
            major_label_font_size=20,
            value_font_size=20,
            title_font_size=25

        )

        # prepare title and count for Chart
        nameList = []
        countList = []
        iz = Counter(titleList).items()  # title, count

        sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))
        for ss in sortedIz:
            nameList.append(ss[0])
            countList.append(ss[1])

        userView_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False,
                                   x_label_rotation=-50)
        userView_chart.title = 'View # by Post : total( ' + str(postHis.__len__()) + ' )'
        userView_chart.x_labels = nameList
        userView_chart.add("", countList)
        userView_graph = userView_chart.render_data_uri()
        if vl.__len__() > 50:
            vl = vl[:50]  # only show recent up to 50

        # user view by Category
        cateNames = []
        cateCounts = []
        iz = Counter(cateList).items()  # category, count

        sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))
        # for ss in sortedIz:
        #     cateNames.append(ss[0])
        #     cateCounts.append(ss[1])

        # userViewByCat_chart = pygal.Bar(style=style_userView, print_values=True, show_legend=False,
        #                                 x_label_rotation=-30, height=500)
        # userViewByCat_chart.title = 'View # by Category'
        # userViewByCat_chart.x_labels = cateNames
        # userViewByCat_chart.add("", cateCounts)
        # userViewByCat_graph = userViewByCat_chart.render_data_uri()

        userViewByCat_chart = pygal.Pie(style=style_userView, print_values=True, show_legend=True,
                                        height=500)
        userViewByCat_chart.title = 'View # by Category'
        for ss in sortedIz:
            userViewByCat_chart.add(ss[0], ss[1])

        userViewByCat_graph = userViewByCat_chart.render_data_uri()

        # stackedLine for usage over time.
        ### line_chart = pygal.StackedLine(fill=True)
        ### line_chart.title = 'Browser usage evolution (in %)'
        ### line_chart.x_labels = ma##p(str, range(2002, 2013))
        ### line_chart.add('Firefox', [None, None, 0, 16.6, 25, 31, 36.4, 45.5, 46.3, 42.8, 37.1])
        ### line_chart.add('Chrome', [None, None, None, None, None, None, 0, 3.9, 10.8, 23.8, 35.3])
        ### line_chart.add('IE', [85.8, 84.6, 84.7, 74.5, 66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
        ### line_chart.add('Others', [14.2, 15.4, 15.3, 8.9, 9, 10.4, 8.9, 5.8, 6.7, 6.8, 7.5])
        ### line_chart.render()
        # 1. get all history
        # 2. get all dates
        # 3. sort history by app category, get count by each category
        # 4. loop by category, create a list A
        # 4.1 loop by date, for each date, get the count for current category, create a list of counts
        # 4.2 add the category + count list into the list A.
        userViewOverTime_chart = pygal.StackedLine(fill=True, x_label_rotation=-30, height=500)
        userViewOverTime_chart.title = 'View # Over Time by Category'

        #postHis = PostHistory.query.filter(PostHistory.user_id == uid).order_by(desc(PostHistory.date)).all()
        # get how many Category


        cateList = []
        dateList = []
        for v in postHis:
            route = v.route
            cateList.append(getCategory(getPostCategoryByRoute(route)))
            dateList.append(str(v.date)[:10])

        # iz = Counter(cateList).items()  # category, count
        cateNames = list(set(cateList))

        # for ss in iz:
        #     cateNames.append(ss[0])
        # get all the dates from Start to Current
        # dateCounts = []
        # idates = Counter(dateList).items()  # date, count
        datesForX = list(set(dateList))
        # for dd in idates:
        #     datesForX.append(dd[0])

        datesForX.sort()
        userViewOverTime_chart.x_labels = datesForX

        # 4.1 loop by date, for each date, get the count for current category, create a list of counts

        for cat in cateNames:
            numListInEachCat = []
            # loop by date, for each date, get the count for current category, create a list of counts

            for dd in datesForX:
                numListInEachCat.append(getNumberInACatOnADay(postHis, cat, dd))

            # 4.2 add the category + count list into the list A.
            userViewOverTime_chart.add(cat, numListInEachCat)

        userViewOverTime_graph = userViewOverTime_chart.render_data_uri()

        return render_template('/viewerHis.html', uname=uname, viewList=vl, searchList=sList,
                               userView_graph=userView_graph, userViewByCat_graph=userViewByCat_graph,
                               userViewOverTime_graph=userViewOverTime_graph)


def getNumberInACatOnADay(postHis, category, date):
    # postHis = PostHistory.query.filter((PostHistory.user_id == uid)).all()
    count = 0
    for v in postHis:
        route = v.route
        cat = getCategory(getPostCategoryByRoute(route))
        if (cat == category):
            dd = str(v.date)[:10]
            if dd == date:
                count = count + 1

    if count == 0:
        return None
    return count


## download files, all routes must end with 'download' for data analysis
route_download_ft_rule = '/mqarules/ft/ft_example/download'


@app.route(route_download_ft_rule)
@login_required
def download_ft_rule():
    recordPostHistory(route_download_ft_rule)
    return send_file('static/mqarules/ft/ft_example.rule', attachment_filename='ft_example.rule', mimetype='text/rule',
                     as_attachment=True)


route_download_fmax_rule = '/mqarules/fmax/fmax_example/download'


@app.route(route_download_fmax_rule)
@login_required
def download_fmax_rule():
    recordPostHistory(route_download_fmax_rule)
    return send_file('static/mqarules/fmax/fmax_example.rule', attachment_filename='fmax_example.rule',
                     mimetype='text/rule', as_attachment=True)


route_download_vth_finfet_rule = '/mqarules/vth_finfet/vth_FinFET/download'


@app.route(route_download_vth_finfet_rule)
@login_required
def download_vth_finfet_rule():
    recordPostHistory(route_download_vth_finfet_rule)
    return send_file('static/mqarules/vth_finfet/vth_FinFET.rule', attachment_filename='vth_FinFET.rule',
                     mimetype='text/rule', as_attachment=True)


route_download_sweepVgsNegative_rule = '/mqarules/sweepVgsNeg/Vth_DepletedMode/download'


@app.route(route_download_sweepVgsNegative_rule)
@login_required
def download_sweepVgsNegative_rule():
    recordPostHistory(route_download_sweepVgsNegative_rule)
    return send_file('static/mqarules/sweepVthfromNegative/Vth_DepletedMode.rule',
                     attachment_filename='Vth_DepletedMode.rule', mimetype='text/rule', as_attachment=True)


route_download_synchro_rule = '/mqarules/synchro/rule/download'


@app.route(route_download_synchro_rule)
@login_required
def download_synchro_rule():
    recordPostHistory(route_download_synchro_rule)
    return send_file('static/mqarules/synchro/SynchroSA_SB.rule',
                     attachment_filename='SynchroSA_SB.rule', mimetype='text/rule', as_attachment=True)


route_download_normalize_rule = '/mqarules/normalize/rule/download'


@app.route(route_download_normalize_rule)
@login_required
def download_normalize_rule():
    recordPostHistory(route_download_normalize_rule)
    return send_file('static/mqarules/normalize/Normalization_Example.rule',
                     attachment_filename='Normalization_Example.rule', mimetype='text/rule', as_attachment=True)


route_download_ideff_rule = '/mqarules/ideff/rule/download'


@app.route(route_download_ideff_rule)
@login_required
def download_ideff_rule():
    recordPostHistory(route_download_ideff_rule)
    return send_file('static/mqarules/ideff/Ideff.rule',
                     attachment_filename='Ideff.rule', mimetype='text/rule', as_attachment=True)


route_download_mismatch_hsp_mos_rule = '/mqarules/mismatch_hsp_mos/download'


@app.route(route_download_mismatch_hsp_mos_rule)
@login_required
def download_Mismatch_hsp_mos_rule():
    recordPostHistory(route_download_mismatch_hsp_mos_rule)
    return send_file('static/mqarules/mismatch_hsp_mos/Mismatch_hsp_mos.rule',
                     attachment_filename='Mismatch_hsp_mos.rule', mimetype='text/rule', as_attachment=True)


route_download_mismatch_hsp_mos_finfet_rule = '/mqarules/mismatch_hsp_mos_finfet/download'


@app.route(route_download_mismatch_hsp_mos_finfet_rule)
@login_required
def download_Mismatch_hsp_mos_finfet_rule():
    recordPostHistory(route_download_mismatch_hsp_mos_finfet_rule)
    return send_file('static/mqarules/mismatch_hsp_mos_finfet/Mismatch_hsp_mos_finfet.rule',
                     attachment_filename='Mismatch_hsp_mos_finfet.rule', mimetype='text/rule', as_attachment=True)


route_download_mismatch_hsp_model_lib = '/mqarules/mismatch_hsp_lib_finfet/download'


@app.route(route_download_mismatch_hsp_model_lib)
@login_required
def download_Mismatch_hsp_mos_finfet_lib():
    recordPostHistory(route_download_mismatch_hsp_model_lib)
    return send_file('static/mqarules/mismatch_hsp_mos_finfet/AcceliconMis.lib',
                     attachment_filename='AcceliconMis.lib', mimetype='text/lib', as_attachment=True)


route_download_mismatch_spe_mos_rule = '/mqarules/mismatch_spe_mos/download'


@app.route(route_download_mismatch_spe_mos_rule)
@login_required
def download_Mismatch_spe_mos_rule():
    recordPostHistory(route_download_mismatch_spe_mos_rule)
    return send_file('static/mqarules/mismatch_spe_mos/mismatch_spe_mos.rule',
                     attachment_filename='mismatch_spe_mos.rule', mimetype='text/rule', as_attachment=True)


route_download_symm_rule = '/mqarules/symm/download'


@app.route(route_download_symm_rule)
@login_required
def download_symm_rule():
    recordPostHistory(route_download_symm_rule)
    return send_file('static/mqarules/symm/symTest.rule',
                     attachment_filename='symTest.rule', mimetype='text/rule', as_attachment=True)


route_download_noise_spe_example = '/mqarules/fn_spe_finfet/download'


@app.route(route_download_noise_spe_example)
@login_required
def download_noise_spe_example():
    recordPostHistory(route_download_noise_spe_example)
    return send_file('static/mqarules/fn_spe_finfet/noise_example.rule',
                     attachment_filename='noise_example.rule', mimetype='text/rule', as_attachment=True)


route_download_mea_qa_rule = '/mqafaq/mea_qa1/download'


@app.route(route_download_mea_qa_rule)
@login_required
def download_meas_qa_rule():
    recordPostHistory(route_download_mea_qa_rule)
    return send_file('static/faq/mqa/meas_qa/meas_qa.rule', attachment_filename='meas_qa.rule', mimetype='text/rule',
                     as_attachment=True)


route_download_bsimcmg_model = '/mqarules/bsimcmg_model/download'


@app.route(route_download_bsimcmg_model)
@login_required
def download_bsimcmg_model():
    recordPostHistory(route_download_bsimcmg_model)
    return send_file('static/mqarules/fn_spe_finfet/model_bsimcmg.l',
                     attachment_filename='model_bsimcmg.l', mimetype='text/rule', as_attachment=True)


route_download_bsim3_model = '/mqarules/bsim3_model/download'


@app.route(route_download_bsim3_model)
@login_required
def download_bsim3_model():
    recordPostHistory(route_download_bsim3_model)
    return send_file('static/mqarules/cgscgd/bsim3.l',
                     attachment_filename='bsim3.l', mimetype='text/rule', as_attachment=True)


route_download_bsim4_model = '/mqarules/bsim4_model/download'


@app.route(route_download_bsim4_model)
@login_required
def download_bsim4_model():
    recordPostHistory(route_download_bsim4_model)
    return send_file('static/mqarules/cgscgd/bsim4.l',
                     attachment_filename='bsim4.l', mimetype='text/rule', as_attachment=True)


route_download_bsim6_model = '/mqarules/bsim6_model/download'


@app.route(route_download_bsim6_model)
@login_required
def download_bsim6_model():
    recordPostHistory(route_download_bsim6_model)
    return send_file('static/mqarules/cgscgd/bsim6.l',
                     attachment_filename='bsim6.l', mimetype='text/rule', as_attachment=True)


route_download_cgscgd_rule = '/mqarules/cgscgd/rule/download'


@app.route(route_download_cgscgd_rule)
@login_required
def download_cgscgd_rule():
    recordPostHistory(route_download_cgscgd_rule)
    return send_file('static/mqarules/cgscgd/CgsCgd.rule',
                     attachment_filename='CgsCgd.rule', mimetype='text/rule', as_attachment=True)


route_download_cxy_rule = '/mqarules/cxy/rule/download'


@app.route(route_download_cxy_rule)
@login_required
def download_cxy_rule():
    recordPostHistory(route_download_cxy_rule)
    return send_file('static/mqarules/cxy/Cxy.rule',
                     attachment_filename='Cxy.rule', mimetype='text/rule', as_attachment=True)


route_download_crss_rule = '/mqarules/crss_ciss_coss/rule/download'


@app.route(route_download_crss_rule)
@login_required
def download_crss_rule():
    recordPostHistory(route_download_crss_rule)
    return send_file('static/mqarules/crss/crss_ciss_coss.rule',
                     attachment_filename='crss_ciss_coss.rule', mimetype='text/rule', as_attachment=True)


route_download_compdiff_a_rule = '/mqarules/compdiff_a/rule/download'


@app.route(route_download_compdiff_a_rule)
@login_required
def download_compdiff_a_rule():
    recordPostHistory(route_download_compdiff_a_rule)
    return send_file('static/mqarules/compdiff_a/compDiff_meas_within_corners.zip',
                     attachment_filename='compDiff_meas_within_corners.zip', mimetype='application/zip',
                     as_attachment=True)


#### Script Zip files downloads

route_download_scriptZip_01 = '/scriptZip/01_ModelParameter/download'


@app.route(route_download_scriptZip_01)
@login_required
def download_scriptZip_01():
    recordPostHistory(route_download_scriptZip_01)
    return send_file('static/mbpst/scriptZip/01_ModelParameter.zip',
                     attachment_filename='01_ModelParameter.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_02 = '/scriptZip/02_IMV_Simple/download'


@app.route(route_download_scriptZip_02)
@login_required
def download_scriptZip_02():
    recordPostHistory(route_download_scriptZip_02)
    return send_file('static/mbpst/scriptZip/02_IMV_Simple.zip',
                     attachment_filename='02_IMV_Simple.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_03 = '/scriptZip/03_IMV_Idlin_Plot/download'


@app.route(route_download_scriptZip_03)
@login_required
def download_scriptZip_03():
    recordPostHistory(route_download_scriptZip_03)
    return send_file('static/mbpst/scriptZip/03_IMV_Idlin_Plot.zip',
                     attachment_filename='03_IMV_Idlin_Plot.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_04 = '/scriptZip/04_IMV_Ideff/download'


@app.route(route_download_scriptZip_04)
@login_required
def download_scriptZip_04():
    recordPostHistory(route_download_scriptZip_04)
    return send_file('static/mbpst/scriptZip/04_IMV_Ideff.zip',
                     attachment_filename='04_IMV_Ideff.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_05 = '/scriptZip/05_IMV_Vth/download'


@app.route(route_download_scriptZip_05)
@login_required
def download_scriptZip_05():
    recordPostHistory(route_download_scriptZip_05)
    return send_file('static/mbpst/scriptZip/05_IMV_Vth.zip',
                     attachment_filename='05_IMV_Vth.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_06 = '/scriptZip/06_IMV_GmNearVth/download'


@app.route(route_download_scriptZip_06)
@login_required
def download_scriptZip_06():
    recordPostHistory(route_download_scriptZip_06)
    return send_file('static/mbpst/scriptZip/06_IMV_GmNearVth.zip',
                     attachment_filename='06_IMV_GmNearVth.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_07 = '/scriptZip/07_IMV_IdsatT25/download'


@app.route(route_download_scriptZip_07)
@login_required
def download_scriptZip_07():
    recordPostHistory(route_download_scriptZip_07)
    return send_file('static/mbpst/scriptZip/07_IMV_IdsatT25.zip',
                     attachment_filename='07_IMV_IdsatT25.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_08 = '/scriptZip/08_IMV_Y2/download'


@app.route(route_download_scriptZip_08)
@login_required
def download_scriptZip_08():
    recordPostHistory(route_download_scriptZip_08)
    return send_file('static/mbpst/scriptZip/08_IMV_Y2.zip',
                     attachment_filename='08_IMV_Y2.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_09 = '/scriptZip/09_IMV_SASB_Synch/download'


@app.route(route_download_scriptZip_09)
@login_required
def download_scriptZip_09():
    recordPostHistory(route_download_scriptZip_09)
    return send_file('static/mbpst/scriptZip/09_IMV_SASB_Synch.zip',
                     attachment_filename='09_IMV_SASB_Synch.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_10 = '/scriptZip/10_IMV_Idsat_MaxSASB/download'


@app.route(route_download_scriptZip_10)
@login_required
def download_scriptZip_10():
    recordPostHistory(route_download_scriptZip_10)
    return send_file('static/mbpst/scriptZip/10_IMV_Idsat_MaxSASB.zip',
                     attachment_filename='10_IMV_Idsat_MaxSASB.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_11 = '/scriptZip/11_IMV_Vth_con_FinFET/download'


@app.route(route_download_scriptZip_11)
@login_required
def download_scriptZip_11():
    recordPostHistory(route_download_scriptZip_11)
    return send_file('static/mbpst/scriptZip/11_IMV_Vth_con_FinFET.zip',
                     attachment_filename='11_IMV_Vth_con_FinFET.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_12 = '/scriptZip/12_DATA_Attach/download'


@app.route(route_download_scriptZip_12)
@login_required
def download_scriptZip_12():
    recordPostHistory(route_download_scriptZip_12)
    return send_file('static/mbpst/scriptZip/12_DATA_Attach.zip',
                     attachment_filename='12_DATA_Attach.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_13 = '/scriptZip/13_Optimization/download'


@app.route(route_download_scriptZip_13)
@login_required
def download_scriptZip_13():
    recordPostHistory(route_download_scriptZip_13)
    return send_file('static/mbpst/scriptZip/13_Optimization.zip',
                     attachment_filename='13_Optimization.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_14 = '/scriptZip/14_FuncCall/download'


@app.route(route_download_scriptZip_14)
@login_required
def download_scriptZip_14():
    recordPostHistory(route_download_scriptZip_14)
    return send_file('static/mbpst/scriptZip/14_FuncCall.zip',
                     attachment_filename='14_FuncCall.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_15 = '/scriptZip/15_ReadWriteFile/download'


@app.route(route_download_scriptZip_15)
@login_required
def download_scriptZip_15():
    recordPostHistory(route_download_scriptZip_15)
    return send_file('static/mbpst/scriptZip/15_ReadWriteFile.zip',
                     attachment_filename='15_ReadWriteFile.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_16 = '/scriptZip/16_Hide_Columns/download'


@app.route(route_download_scriptZip_16)
@login_required
def download_scriptZip_16():
    recordPostHistory(route_download_scriptZip_16)
    return send_file('static/mbpst/scriptZip/16_Hide_Columns.zip',
                     attachment_filename='16_Hide_Columns.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_17 = '/scriptZip/17_AccessSim/download'


@app.route(route_download_scriptZip_17)
@login_required
def download_scriptZip_17():
    recordPostHistory(route_download_scriptZip_17)
    return send_file('static/mbpst/scriptZip/17_AccessSim.zip',
                     attachment_filename='17_AccessSim.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_18 = '/scriptZip/18_SidOverId2/download'


@app.route(route_download_scriptZip_18)
@login_required
def download_scriptZip_18():
    recordPostHistory(route_download_scriptZip_18)
    return send_file('static/mbpst/scriptZip/18_SidOverId2.zip',
                     attachment_filename='18_SidOverId2.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_19 = '/scriptZip/19_DataSparseness/download'


@app.route(route_download_scriptZip_19)
@login_required
def download_scriptZip_19():
    recordPostHistory(route_download_scriptZip_19)
    return send_file('static/mbpst/scriptZip/19_DataSparseness.zip',
                     attachment_filename='19_DataSparseness.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_20 = '/scriptZip/20_Flow/download'


@app.route(route_download_scriptZip_20)
@login_required
def download_scriptZip_20():
    recordPostHistory(route_download_scriptZip_20)
    return send_file('static/mbpst/scriptZip/20_Flow.zip',
                     attachment_filename='20_Flow.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_21 = '/scriptZip/21_Timer/download'


@app.route(route_download_scriptZip_21)
@login_required
def download_scriptZip_21():
    recordPostHistory(route_download_scriptZip_21)
    return send_file('static/mbpst/scriptZip/21_Timer.zip',
                     attachment_filename='21_Timer.zip', mimetype='application/zip', as_attachment=True)


route_download_scriptZip_22 = '/scriptZip/22_GlobalVar/download'


@app.route(route_download_scriptZip_22)
@login_required
def download_scriptZip_22():
    recordPostHistory(route_download_scriptZip_22)
    return send_file('static/mbpst/scriptZip/22_GlobalVar.zip',
                     attachment_filename='22_GlobalVar.zip', mimetype='application/zip', as_attachment=True)


route_download_blog_load_csv_in_mbp = '/blog/load_csv_in_mbp/download'


@login_required
@app.route(route_download_blog_load_csv_in_mbp)
def download_blog_load_csv_in_mbp():
    recordPostHistory(route_download_blog_load_csv_in_mbp)
    return send_file('static/blog/load_csv_in_mbp/nmos_IdVd.csv',
                     attachment_filename='nmos_IdVd.csv', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_idsat_table = '/pyrfs/idsat_table/download'


@login_required
@app.route(route_download_pyrfs_idsat_table)
def download_pyrfs_idsat_table():
    recordPostHistory(route_download_pyrfs_idsat_table)
    return send_file('static/pyrfs/chap02/01_idsat_table/idsat_table_01.xlsx',
                     attachment_filename='idsat_table_01.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_idsat_table_t = '/pyrfs/idsat_table_t/download'


@login_required
@app.route(route_download_pyrfs_idsat_table_t)
def download_pyrfs_idsat_table_t():
    recordPostHistory(route_download_pyrfs_idsat_table_t)
    return send_file('static/pyrfs/chap02/02_idsat_table_T/idsat_table.xlsx',
                     attachment_filename='idsat_table.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_gm_table_vbs = '/pyrfs/gm_table_vbs/download'


@login_required
@app.route(route_download_pyrfs_gm_table_vbs)
def download_pyrfs_gm_table_vbs():
    recordPostHistory(route_download_pyrfs_gm_table_vbs)
    return send_file('static/pyrfs/chap02/04_gm_table_vbs/gm_table_vbs.xlsx',
                     attachment_filename='gm_table_vbs.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_gm_table_t25 = '/pyrfs/gm_table_t25/download'


@login_required
@app.route(route_download_pyrfs_gm_table_t25)
def download_pyrfs_gm_table_t25():
    recordPostHistory(route_download_pyrfs_gm_table_t25)
    return send_file('static/pyrfs/chap02/05_gm_table_t25/gm_table_T25.xlsx',
                     attachment_filename='gm_table_T25.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_gm_table_sort_vbs = '/pyrfs/gm_table_sort_vbs/download'


@login_required
@app.route(route_download_pyrfs_gm_table_sort_vbs)
def download_pyrfs_gm_table_sort_vbs():
    recordPostHistory(route_download_pyrfs_gm_table_sort_vbs)
    return send_file('static/pyrfs/chap02/06_gm_table_sort_vbs/gm_table_sort_vbs.xlsx',
                     attachment_filename='gm_table_sort_vbs.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_manual = '/pyrfs/manual/download'


@login_required
@app.route(route_download_pyrfs_manual)
def download_pyrfs_manual():
    recordPostHistory(route_download_pyrfs_manual)
    return send_file('static/pyrfs/chap01/1.2_howto_guide_line/pyrfs_manual.pdf',
                     attachment_filename='pyrfs_manual.pdf', mimetype='application/pdf', as_attachment=True)


route_download_pyrfs_gm_table_vbs_label = '/pyrfs/gm_table_vbs_label/download'


@login_required
@app.route(route_download_pyrfs_gm_table_vbs_label)
def download_pyrfs_gm_table_vbs_label():
    recordPostHistory(route_download_pyrfs_gm_table_vbs_label)
    return send_file('static/pyrfs/chap02/07_gm_table_vbs_label/gm_table_vbs_label.xlsx',
                     attachment_filename='gm_table_vbs_label.xlsx', mimetype='text/plain', as_attachment=True)


route_download_pyrfs_idsat_table_merge_wl = '/pyrfs/idsat_table_merge_wl/download'


@login_required
@app.route(route_download_pyrfs_idsat_table_merge_wl)
def download_pyrfs_idsat_table_merge_wl():
    recordPostHistory(route_download_pyrfs_idsat_table_merge_wl)
    return send_file('static/pyrfs/chap02/08_idsat_table_merge_wl/idsat_table_merge_wl.xlsx',
                     attachment_filename='idsat_table_merge_wl.xlsx', mimetype='text/plain', as_attachment=True)


route_download_mqarule_wpe = '/mqarule/wpe/download'


@login_required
@app.route(route_download_mqarule_wpe)
def download_mqarule_wpe():
    recordPostHistory(route_download_mqarule_wpe)
    return send_file('static/mqarules/wpe/wpe.csv',
                     attachment_filename='wpe.csv', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_subckt_model = '/mbpfaq/subckt_model/download'


@login_required
@app.route(route_download_mbpfaq_subckt_model)
def download_mbpfaq_subckt_model():
    recordPostHistory(route_download_mbpfaq_subckt_model)
    return send_file('static/faq/mbp/script_subckt_param/subckt_test.l',
                     attachment_filename='subckt_test.l', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_weff_model = '/mbpfaq/weff_leff_model/download'


@login_required
@app.route(route_download_mbpfaq_weff_model)
def download_mbpfaq_weff_model():
    recordPostHistory(route_download_mbpfaq_weff_model)
    return send_file('static/faq/mbp/weff_leff/test.l',
                     attachment_filename='test.l', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_weff_data = '/mbpfaq/weff_leff_data/download'


@login_required
@app.route(route_download_mbpfaq_weff_data)
def download_mbpfaq_weff_data():
    recordPostHistory(route_download_mbpfaq_weff_data)
    return send_file('static/faq/mbp/weff_leff/test.mea',
                     attachment_filename='test.mea', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_weff_zip = '/mbpfaq/weff_leff_script_zip/download'


@login_required
@app.route(route_download_mbpfaq_weff_zip)
def download_mbpfaq_weff_zip():
    recordPostHistory(route_download_mbpfaq_weff_zip)
    return send_file('static/faq/mbp/weff_leff/imv.imv.Weff_Leff.zip',
                     attachment_filename='imv.imv.Weff_Leff.zip', mimetype='application/zip', as_attachment=True)


route_download_mbpfaq_meascond1 = '/mbpfaq/meascond1/download'


@login_required
@app.route(route_download_mbpfaq_meascond1)
def download_mbpfaq_meascond1():
    recordPostHistory(route_download_mbpfaq_meascond1)
    return send_file('static/faq/mbp/meascond/nmos_ids_vds_high_vgs.mdm',
                     attachment_filename='tnmos_ids_vds_high_vgs.mdm', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_meascond2 = '/mbpfaq/meascond2/download'


@login_required
@app.route(route_download_mbpfaq_meascond2)
def download_mbpfaq_meascond2():
    recordPostHistory(route_download_mbpfaq_meascond2)
    return send_file('static/faq/mbp/meascond/nmos_ids_vds_low_vgs.mdm',
                     attachment_filename='tnmos_ids_vds_low_vgs.mdm', mimetype='text/plain', as_attachment=True)


route_download_iccapfaq_ltspice3 = '/iccapfaq/ltspice3/download'


@login_required
@app.route(route_download_iccapfaq_ltspice3)
def download_iccapfaq_ltspice3():
    recordPostHistory(route_download_iccapfaq_ltspice3)
    return send_file('static/faq/iccap/link2ltspice/ltspice3.txt',
                     attachment_filename='ltspice3.txt', mimetype='text/plain', as_attachment=True)


route_download_iccapfaq_ltspice3_forblog = '/iccapfaq/blog/ltspice3/download'


@app.route(route_download_iccapfaq_ltspice3_forblog)
def download_iccapfaq_ltspice3_forblog():
    recordPostHistory(route_download_iccapfaq_ltspice3_forblog)
    return send_file('static/faq/iccap/link2ltspice/ltspice3.txt',
                     attachment_filename='ltspice3.txt', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_idvdvg_site11 = '/iccapfaq/idvdvg_site11/download'


@login_required
@app.route(route_download_mbpfaq_idvdvg_site11)
def download_mbpfaq_idvdvg_site11():
    recordPostHistory(route_download_mbpfaq_idvdvg_site11)
    return send_file('static/faq/mbp/site_die/idvdvg_site11.mdm',
                     attachment_filename='idvdvg_site11.mdm', mimetype='text/plain', as_attachment=True)


route_download_mbpfaq_idvdvg_site12 = '/iccapfaq/idvdvg_site12/download'


@login_required
@app.route(route_download_mbpfaq_idvdvg_site12)
def download_mbpfaq_idvdvg_site12():
    recordPostHistory(route_download_mbpfaq_idvdvg_site12)
    return send_file('static/faq/mbp/site_die/idvdvg_site12.mdm',
                     attachment_filename='idvdvg_site12.mdm', mimetype='text/plain', as_attachment=True)


route_download_mqafab_mea_data_zip = '/mqafaq/meas_example_data/download'


@login_required
@app.route(route_download_mqafab_mea_data_zip)
def download_mqafaq_mea_data():
    recordPostHistory(route_download_mqafab_mea_data_zip)
    return send_file('static/faq/mqa/meas_qa/example_mdm_data_files.zip',
                     attachment_filename='example_mdm_data_files.zip', mimetype='application/zip', as_attachment=True)


route_download_mqarule_vtgm = '/mqarules/vtgm/download'


@login_required
@app.route(route_download_mqarule_vtgm)
def download_mqarule_vtgm():
    recordPostHistory(route_download_mqarule_vtgm)
    return send_file('static/mqarules/vtgm/vth_gm.rule',
                     attachment_filename='vth_gm.rule', mimetype='text/plain', as_attachment=True)


route_download_bsim4_7_model = '/mqarules/vtgm/model/download'


@login_required
@app.route(route_download_bsim4_7_model)
def download_mqarule_vtgm_bsim4_7_model():
    recordPostHistory(route_download_bsim4_7_model)
    return send_file('static/mqarules/vtgm/bsim4.7.l',
                     attachment_filename='bsim4.7.l', mimetype='text/plain', as_attachment=True)


route_download_mbpst_IF_model = '/mbpst/idealityfactor/npnmodel/download'


@login_required
@app.route(route_download_mbpst_IF_model)
def download_mbpst_IF_model():
    recordPostHistory(route_download_mbpst_IF_model)
    return send_file('static/mbpst/Chap3/images/3.25/gp_model.l',
                     attachment_filename='gp_model.l', mimetype='text/plain', as_attachment=True)


route_download_mbpst_IF_data = '/mbpst/idealityfactor/data/download'


@login_required
@app.route(route_download_mbpst_IF_data)
def download_mbpst_IF_data():
    recordPostHistory(route_download_mbpst_IF_data)
    return send_file('static/mbpst/Chap3/images/3.25/data_area_1.0_areab_1.0_areac_1.0_T_25.0.mea',
                     attachment_filename='data_area_1.0_areab_1.0_areac_1.0_T_25.0.mea', mimetype='text/plain',
                     as_attachment=True)


route_download_mbpst_IF_zip = '/mbpst/idealityfactor/script/download'


@login_required
@app.route(route_download_mbpst_IF_zip)
def download_mbpst_idealityfactor_script():
    recordPostHistory(route_download_mbpst_IF_zip)
    return send_file('static/mbpst/Chap3/images/3.25/mbp_script.zip',
                     attachment_filename='mbp_script.zip', mimetype='application/zip', as_attachment=True)


### Upload a file
route_update_a_file = "/upload"


@app.route(route_update_a_file)
def upload():
    return render_template("/upload/upload.html")


### process a uploaded a file
route_process_updated_file = "/uploader"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(route_process_updated_file, methods=['POST'])
def uploader():
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        savePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(savePath)
        return 'file uploaded successfully' + savePath


# edit post
route_edit_post_entry = '/edit_post_entry'


@login_required
@roles_required('sunshine')
@app.route(route_edit_post_entry)
def route_edit_post_entry():
    return render_template('edit_post_entry.html')


route_edit_post = '/edit_post'


@login_required
@roles_required('sunshine')
@app.route(route_edit_post, methods=['POST'])
def route_edit_post():
    route = request.form['route']
    post = Post.query.filter(Post.route == route).first()

    return render_template('/edit_post.html', post=post)


route_edit_post_finish = '/edit_post_finish'


@login_required
@roles_required('sunshine')
@app.route(route_edit_post_finish, methods=['POST'])
def route_edit_post_finish():
    # update the database
    # only CS can add for now.
    if current_user.email != 'shuang_cai@keysight.com':
        return redirect(url_for('index'))

    title = request.form['title'].strip()
    abs = request.form['abs'].strip()
    category = request.form['category']
    content = request.form['content'].strip()
    now = datetime.datetime.now()
    route = request.form['route'].strip()

    post = Post.query.filter(Post.route == route).first()

    post.title = title
    post.abs = abs
    post.category = category
    post.content = content
    post.last_modify_date = now;

    db.session.commit()

    return redirect(route)


route_pyrfs = '/pyrfs'


@app.route(route_pyrfs)
def pyrfs():
    recordPostHistory(route_pyrfs)
    return render_template('pyrfs/chap01/PyRFS_Basics.html')


route_pyrfs_chap1_1 = '/pyrfs/chap1.1'


@app.route(route_pyrfs_chap1_1)
@login_required
def pyrfs_chap1_1():
    recordPostHistory(route_pyrfs_chap1_1)
    return render_template('pyrfs/chap01/PyRFS_Basics.html')


route_pyrfs_chap1_2 = '/pyrfs/chap1.2'


@app.route(route_pyrfs_chap1_2)
@login_required
def pyrfs_chap1_2():
    recordPostHistory(route_pyrfs_chap1_2)
    return render_template('pyrfs/chap01/guide_line.html')


route_pyrfs_chap1_3 = '/pyrfs/chap1.3'


@app.route(route_pyrfs_chap1_3)
@login_required
def pyrfs_chap1_3():
    recordPostHistory(route_pyrfs_chap1_3)
    return render_template('pyrfs/chap01/getStarted.html')


route_pyrfs_chap2 = '/pyrfs/chap2'


@app.route(route_pyrfs_chap2)
@login_required
def pyrfs_chap2():
    recordPostHistory(route_pyrfs_chap2)
    return render_template('pyrfs/chap02/agenda.html')


route_pyrfs_chap2_1 = '/pyrfs/chap2.a1'


@app.route(route_pyrfs_chap2_1)
@login_required
def pyrfs_chap2_1():
    recordPostHistory(route_pyrfs_chap2_1)
    return render_template('pyrfs/chap02/idsat_table.html')


route_pyrfs_chap2_2 = '/pyrfs/chap2.a2'


@app.route(route_pyrfs_chap2_2)
@login_required
def pyrfs_chap2_2():
    recordPostHistory(route_pyrfs_chap2_2)
    return render_template('pyrfs/chap02/idsat_table_t.html')


route_pyrfs_chap2_3 = '/pyrfs/chap2.a3'


@app.route(route_pyrfs_chap2_3)
@login_required
def pyrfs_chap2_3():
    recordPostHistory(route_pyrfs_chap2_3)
    return render_template('pyrfs/chap02/cond_target_list.html')


route_pyrfs_chap2_4 = '/pyrfs/chap2.a4'


@app.route(route_pyrfs_chap2_4)
@login_required
def pyrfs_chap2_4():
    recordPostHistory(route_pyrfs_chap2_4)
    return render_template('pyrfs/chap02/gm_table_vbs.html')


route_pyrfs_chap2_b1 = '/pyrfs/chap2.b1'


@app.route(route_pyrfs_chap2_b1)
@login_required
def pyrfs_chap2_b1():
    recordPostHistory(route_pyrfs_chap2_b1)
    return render_template('pyrfs/chap02/gm_table_t25.html')


route_pyrfs_chap2_b2 = '/pyrfs/chap2.b2'


@app.route(route_pyrfs_chap2_b2)
@login_required
def pyrfs_chap2_b2():
    recordPostHistory(route_pyrfs_chap2_b2)
    return render_template('pyrfs/chap02/gm_table_sort_vbs.html')


route_pyrfs_chap2_b3 = '/pyrfs/chap2.b3'


@app.route(route_pyrfs_chap2_b3)
@login_required
def pyrfs_chap2_b3():
    recordPostHistory(route_pyrfs_chap2_b3)
    return render_template('pyrfs/chap02/gm_table_vbs_label.html')


route_pyrfs_chap2_b4 = '/pyrfs/chap2.b4'


@app.route(route_pyrfs_chap2_b4)
@login_required
def pyrfs_chap2_b4():
    recordPostHistory(route_pyrfs_chap2_b4)
    return render_template('pyrfs/chap02/idsat_table_merge_wl.html')


route_pyrfs_chap2_b5 = '/pyrfs/chap2.b5'


@app.route(route_pyrfs_chap2_b5)
@login_required
def pyrfs_chap2_b5():
    recordPostHistory(route_pyrfs_chap2_b5)
    return render_template('pyrfs/chap02/sid_id2.html')


route_pyrfs_chap2_b6 = '/pyrfs/chap2.b6'


@app.route(route_pyrfs_chap2_b6)
@login_required
def pyrfs_chap2_b6():
    recordPostHistory(route_pyrfs_chap2_b6)
    return render_template('pyrfs/chap02/update_excel.html')


route_pyrfs_chap2_b7 = '/pyrfs/chap2.b7'


@app.route(route_pyrfs_chap2_b7)
@login_required
def pyrfs_chap2_b7():
    recordPostHistory(route_pyrfs_chap2_b7)
    return render_template('pyrfs/chap02/hidden.html')


route_pyrfs_chap2_c1 = '/pyrfs/chap2.c1'


@app.route(route_pyrfs_chap2_c1)
@login_required
def pyrfs_chap2_c1():
    recordPostHistory(route_pyrfs_chap2_c1)
    return render_template('pyrfs/chap02/tables.html')


route_pyrfs_chap2_c2 = '/pyrfs/chap2.c2'


@app.route(route_pyrfs_chap2_c2)
@login_required
def pyrfs_chap2_c2():
    recordPostHistory(route_pyrfs_chap2_c2)
    return render_template('pyrfs/chap02/sheets.html')


route_pyrfs_chap2_d1 = '/pyrfs/chap2.d1'


@app.route(route_pyrfs_chap2_d1)
@login_required
def pyrfs_chap2_d1():
    recordPostHistory(route_pyrfs_chap2_d1)
    return render_template('pyrfs/chap02/format.html')


route_pyrfs_chap2_d2 = '/pyrfs/chap2.d2'


@app.route(route_pyrfs_chap2_d2)
@login_required
def pyrfs_chap2_d2():
    recordPostHistory(route_pyrfs_chap2_d2)
    return render_template('pyrfs/chap02/vdr_format.html')


#########################
if __name__ == '__main__':
    app.run()
