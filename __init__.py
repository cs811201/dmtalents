import datetime
import operator
import os
import sys
from collections import Counter

import flask_whooshalchemy as wa
from flask import Flask
from flask import render_template, url_for, request, redirect, send_file
from flask_mail import Mail
from flask_security import Security, login_required, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
from flask_security import roles_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from csutil import *

app = Flask(__name__)
app.debug = False

if sys.platform == 'win32':
    # print('win32')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/dm.db'
    app.config['WHOOSH_BASE'] = 'whoosh_index'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/FlaskApp/dmworks/db/dm.db'
    app.config['WHOOSH_BASE'] = '/var/www/FlaskApp/dmworks/whoosh_index'

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'super-secret007'
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_TOKEN_MAX_AGE'] = 60 * 30
app.config['SECURITY_TRACKABLE'] = True
# app.config['SECURITY_PASSWORD_SALT'] = 'something_super_secret_802jfkj__fd!'



# config for email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cs8112010033@gmail.com'
app.config['MAIL_PASSWORD'] = 'iamcsman121'

db = SQLAlchemy(app)

mail = Mail(app)


def recordPostHistory(rt):
    id = current_user.id
    if id == 3:  # 3 is Shuang Cai, no need to record myself. :)
        return

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
    mbpPost = Post.query.filter((Post.category == 'mbpst')).all()
    mbpstCt = mbpPost.__len__()
    rulePost = Post.query.filter((Post.category == 'mqarules')).all()
    ruleCt = rulePost.__len__()

    videoPost = Post.query.filter((Post.category == 'video')).all()
    videoCt = videoPost.__len__()

    faqPost = Post.query.filter((Post.category == 'mqafaq') | (Post.category == 'mbpfaq')).all()
    faqCt = faqPost.__len__()

    return render_template('index.html', num=getRandomIntFrom1toGiven(8), mbpstCt=mbpstCt, videoCt=videoCt,
                           ruleCt=ruleCt, faqCt=faqCt)


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
@login_required
def mbpst():
    recordPostHistory('/mbpst')
    return render_template('mbpst/Chap1/WhatIsMBPScript.html')


# default to MBP FAQ list
@app.route('/faq')
# @roles_required('bumblebee')
@login_required
def faq():
    # recordPostHistory('/faq')
    results = Post.query.filter((Post.category == 'mbpfaq') | (Post.category == 'mqafaq')).order_by(
        desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/faq_list.html', slist=results, func=getCategory)


# default to MBP FAQ list
@app.route('/mbpfaq')
# @roles_required('bumblebee')
@login_required
def mbpfaq():
    # recordPostHistory('/mbpfaq')
    results = Post.query.filter(Post.category == 'mbpfaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/mbp/mbpfaqlist.html', slist=results, func=getCategory)


@app.route('/mqafaq')
@login_required
def mqafaq():
    # recordPostHistory('/mqafaq')
    results = Post.query.filter(Post.category == 'mqafaq').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('faq/mqa/mqafaqlist.html', slist=results, func=getCategory)


@app.route('/blog')
@login_required
def blog():
    recordPostHistory('/blog')
    results = Post.query.filter(Post.category == 'blog').order_by(desc(Post.create_date)).limit(displayUpto).all()
    return render_template('blog/blog_index.html', slist=results, func=getCategory)


@app.route('/mqarules')
@login_required
def mqarules():
    # recordPostHistory('/mqarules')
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


# example
# .filter(BlogPost.created >= two_days_ago)
@app.route('/search', methods=['POST'])
@login_required
def search():
    txt = request.form['search']
    recordSearchHistory(txt.strip())
    results = Post.query.whoosh_search(txt).limit(displayUpto).all()
    return render_template('search_result.html', slist=results, searchfor=txt, myfunction=getCategory)


@app.route('/about')
def about():
    # recordPostHistory('/about')
    return render_template('about.html')


@app.route('/disclaimer')
def disclaimer():
    # recordPostHistory('/disclaimer')
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


def getPostViewTimeById(uid):
    post = PostHistory.query.filter(PostHistory.id == uid).first()
    if type(post).__name__ == 'NoneType':
        return ''
    return post.date


def getPostTitleByRoute(myroute):
    post = Post.query.filter(Post.route == myroute).first()
    if type(post).__name__ == 'NoneType':
        return ''
    return post.title


def getUserNameById(user_id):
    user = User.query.filter(User.id == user_id).first()
    return user.username


def getEmailById(user_id):
    user = User.query.filter(User.id == user_id).first()
    return user.email


def getCompanybyId(user_id):
    user = User.query.filter(User.id == user_id).first()
    return user.company


#### dashboard  ####
route_dashboard = '/dashboard01.46738.99846kkli58010_odugjfkadj!jf.11'


@app.route(route_dashboard)
@roles_required('sunshine')
@login_required
def dashboard():
    # recordPostHistory(route_dashboard)
    # PostHistory.query.filter(PostHistory.user_id == id).filter(PostHistory.route == rt).all()
    iccapPost = Post.query.filter(Post.category == 'iccap').all()
    iccap_ct = iccapPost.__len__()
    mbpPost = Post.query.filter((Post.category == 'mbpst') | (Post.category == 'mbpfaq')).all()
    mbp_ct = mbpPost.__len__()
    mqaPost = Post.query.filter((Post.category == 'mqafaq') | (Post.category == 'mqarules')).all()
    mqa_ct = mqaPost.__len__()
    wpePost = Post.query.filter((Post.category == 'wpe')).all()
    wpe_ct = wpePost.__len__()
    alfnaPost = Post.query.filter((Post.category == 'alfna')).all()
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
        postTop.append((ii[0], getPostTitleByRoute(str(ii[0])), ii[1]))
        tmp += 1
        if tmp >= 10:
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

    searchList = SearchHistory.query.order_by(desc(SearchHistory.date)).limit(10).all();
    sList = []
    for item in searchList:
        sList.append(item.search_string)

    return render_template('/dashboard.html', iccap_ct=iccap_ct, mbp_ct=mbp_ct, mqa_ct=mqa_ct, wpe_ct=wpe_ct,
                           alfna_ct=alfna_ct,
                           video_ct=video_ct,
                           user_ct=user_ct, search_ct=search_ct, postTop=postTop, userHis=userHis,
                           searchList=sList)


route_recent_100_search = '/recent100SearchHis'


@app.route(route_recent_100_search)
@roles_required('sunshine')
@login_required
def recent100Search():
    searchAll = SearchHistory.query.order_by(desc(SearchHistory.date)).limit(100).all();
    sAll = []
    for item in searchAll:
        sAll.append(item.search_string)

    iz = Counter(sAll).items()
    sortedIz = reversed(sorted(iz, key=operator.itemgetter(1)))  # string, count
    userHis = []  #
    for ii in sortedIz:
        userHis.append((ii[0], ii[1]))

    return render_template('/recent100Searches.html', slist=userHis)


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
        uname = getUserNameById(uid)
        postHis = PostHistory.query.filter(PostHistory.user_id == uid).order_by(PostHistory.route).all()
        vl = []
        for v in postHis:
            route = v.route
            title = getPostTitleByRoute(route)
            date = getPostViewTimeById(v.id)
            if title != '':
                vl.append((title, route, date.ctime()))
        searchHis = SearchHistory.query.filter(SearchHistory.user_id == uid).order_by(SearchHistory.date).all()
        sList = []
        for v in searchHis:
            sList.append(v.search_string)

        return render_template('/viewerHis.html', uname=uname, viewList=vl, searchList=sList)


## download files
route_download_ft_rule = '/mqarules/ft/ft_example'


@app.route(route_download_ft_rule)
@login_required
def download_ft_rule():
    recordPostHistory(route_download_ft_rule)
    return send_file('static/mqarules/ft/ft_example.rule', attachment_filename='ft_example.rule')


route_download_fmax_rule = '/mqarules/fmax/fmax_example'


@app.route(route_download_fmax_rule)
@login_required
def download_fmax_rule():
    recordPostHistory(route_download_fmax_rule)
    return send_file('static/mqarules/fmax/fmax_example.rule', attachment_filename='ft_example.rule')


route_download_vth_finfet_rule = '/mqarules/vth_finfet/vth_FinFET'


@app.route(route_download_vth_finfet_rule)
@login_required
def download_vth_finfet_rule():
    recordPostHistory(route_download_vth_finfet_rule)
    return send_file('static/mqarules/vth_finfet/vth_FinFET.rule', attachment_filename='vth_FinFET.rule')


if __name__ == '__main__':
    app.run()
