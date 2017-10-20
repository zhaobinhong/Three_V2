# -*- coding:utf-8 -*-
import json
import random
import sqlite3

import requests
from flask import Flask, jsonify
from flask import render_template
from flask import request
# from flask_migrate import Migrate, MigrateCommand
# from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
db = SQLAlchemy(app)

# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)


# appkey 配置
appkey = 'appkey'

# 验签地址
VERIFY_GATEWAY = 'http://10.7.7.22:9090'


# 注册用户表
class Sign(db.Model):
    __tablename__ = 'sign'
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    password = db.Column(db.String, nullable=True)
    req_id = db.Column(db.String, unique=True)
    openid = db.Column(db.String, unique=True)
    appkey = db.Column(db.String)
    is_ok = db.Column(db.Boolean, default=False)
    # requests = db.relationship('Requests', backref='sign', lazy='dynamic')


# 商品表：
class Goods(db.Model):
    __tablename__ = 'goods'
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    g_name = db.Column(db.String, nullable=True)
    g_price = db.Column(db.String)


# 状态表
# 查询req_id , stauts 是否相等(判断是否为空)
class Requests(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    req_id = db.Column(db.String, default='')
    status = db.Column(db.Integer, default=0)
    # owner_id = db.Column(db.Integer, db.ForeignKey('sign.id'), default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('sign.id'))
    owner = db.relationship('Sign', backref=db.backref('requests', lazy='dynamic'))


# ODERTYPE = (


# ('0', "已支付"),
#     ('1', "待支付"),
#     ('2', "待收货"),
#     ('3', "已收货"),
# )


# 订单表
class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    # String :
    order_num = db.Column(db.String, unique=True)
    good_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    # 付款人
    drawee = db.Column(db.String)
    # 地址
    address = db.Column(db.String, unique=True)
    # 商品名称
    g_name = db.Column(db.String, nullable=True)
    # 商品价格
    g_price = db.Column(db.String)
    mobile = db.Column(db.String)
    # 商品状态
    g_type = db.Column(db.String)


# 推送回调
@app.route('/push/', methods=['POST'])
def push():
    data = {
        'type': 'refunds',
        'data': {
            "req_id": sum(),
            "appkey": appkey,
            "uri": "/api/passport/receive/",
            "orders": {
                "goods": {
                    "title": "袜子",
                    "amount": "1000.00",
                    "quantity": 1,
                },
                'users': {
                    "name": "姓名",
                    "mobile": "18918989110",
                    "address": "北京",
                },
                "orderid": "113030330",
                "created": "2017-02-01",
                "fee": "550.00",
                "discount": "300.00",
                "paymend": "250.00",
            }
        }
    }
    # data = json.dumps(json.loads(request.data))
    # print data
    resp = requests.post(url='http://10.7.7.22/api/passport/push/', json=request.form['data'])
    return resp.content


def sum():
    import hashlib
    m = hashlib.md5()
    a = random.uniform(10, 20)
    a = '%d' % a
    m.update(a)

    return m.hexdigest()


try:
    openID = Sign.query.order_by(Sign.id.desc()).first().openid
except Exception as e:
    openID = ''


# 回调fun
@app.route('/services/callback/<action>', methods=['POST'])
def get_app(action):
    resp = requests.post(VERIFY_GATEWAY + '/Verify', data=request.data)
    # print request.data
    # print resp.json()
    # request.stream

    sign = resp.json()
    # print sign

    try:
        dd = sign.get('source').decode('hex').decode('hex')
    except Exception as e:
        dd = sign.get('source').decode('hex')

    data = json.loads(dd)
    # print data

    key = data['data']['appkey']
    # data['data']['req_id'] = random.randint(1, 10000)

    if request.method == 'POST':
        if action == 'signin':
            if key == appkey:
                try:
                    st = Requests.query.filter_by(openid=data['data']['openid']).first()
                    s1 = Requests(req_id=data['data']['req_id'], openid=data['data']['openid'], status=2,
                                  owner=st.owner)
                    # st.status = 2

                    db.session.add(s1)
                    db.session.commit()

                    return jsonify({
                        "errors": 0,
                        "detail": "登录成功",
                    })
                except Exception as e:
                    return jsonify({
                        "errors": 1,
                        "detail": "数据写入失败" + e.message
                    })

            else:
                return jsonify({
                    "errors": 1,
                    "detail": "登录失败"
                })
        elif action == 'signup':
            if key == appkey:
                try:

                    owner = Sign(
                        name='x4s',
                        req_id=data['data']['req_id'],
                        openid=data['data']['openid'],
                        is_ok=True,
                        appkey=data['data']['appkey']
                    )

                    status = Requests(req_id=data['data']['req_id'], status=1, owner=owner)

                    db.session.add(owner)

                    db.session.add(status)
                    db.session.commit()

                    return jsonify({
                        "errors": 0,
                        "detail": "注册成功",
                    })
                except Exception as e:
                    return jsonify({
                        "errors": 1,
                        "detail": "数据写入失败" + e.message
                    })
            else:
                return jsonify({
                    "errors": 1,
                    "detail": "注册失败"
                })
        elif action == 'payment':
            if key == appkey:
                orIs = data['data']['errors']
                if (orIs == False):
                    return jsonify({
                        "errors": 0,
                        "detail": "支付成功"
                    })
                else:
                    return jsonify({
                        "errors": 1,
                        "detail": "支付失败"
                    })

            else:
                return jsonify({
                    "errors": 1,
                    "detail": "支付失败"
                })
        elif action == 'receive':
            if key == appkey:
                return jsonify({
                    "errors": 0,
                    "detail": "收货成功"
                })
            else:
                return jsonify({
                    "errors": 1,
                    "detail": "收货失败"
                })
        elif action == 'refunds':
            if key == appkey:
                return jsonify({
                    "errors": 0,
                    "detail": "退货成功"
                })
            else:
                return jsonify({
                    "errors": 1,
                    "detail": "退货失败"
                })
        else:
            return jsonify({
                "errors": 1,
                "detail": "request error"
            })


@app.route('/')
def hello_world():
    title = u'主页'
    data = r"http://www.bankeys.com"
    return render_template('index.html', title=title, data=data)


# 轮询接口（用户状态）fsagdsfg2356532
@app.route('/services/validate/<req_id>/')
def validate(req_id):
    # reqlist = Requests.query.filter_by(req_id=req_id).first()
    # req=Sign.query.filter_by(req_id=56532).first().req_id
    st = Requests.query.filter_by(req_id=req_id).first()

    if st:
        # print reqlist.is_ok
        if st.status > 0:
            status = jsonify({
                "errors": 0,
                "detail": "ok",
                "status": st.status
            })
        else:
            status = jsonify({
                "errors": 1,
                "detail": "error",
                "status": st.status
            })
    else:
        status = jsonify({
            "errors": 1,
            "detail": "没有数据"
        })
    return status


# 商品回调
@app.route('/services/product/<pk>')
def product(pk):
    good = Goods.query.filter_by(id=pk).first()
    print jsonify({
        'id': good.id,
        'g_name': good.g_name,
        'g_price': good.g_price
    })
    return jsonify({
        'id': good.id,
        'g_name': good.g_name,
        'g_price': good.g_price
    })


# 订单回调
@app.route('/services/orders/')
def orders():
    orders = Orders.query.all()
    data = {}
    for oder in orders:
        a = {
            'id': oder.id,
            'oder_num': oder.order_num,
            'good_id': oder.good_id,
            'drawee': oder.drawee,
            'address': oder.address
        }
        data[oder.id] = a

    return jsonify(data)


@app.route('/api/passport/signin/')
def qr(name=None):
    title = u'二维码登录'
    data = {
        "type": "signin",
        "data": {
            "req_id": sum(),
            "openid": openID,
            "appkey": appkey,
            "uri": "/api/passport/signin/"
        }
    }
    return render_template('qrlogin.html', name=name, title=title, data=json.dumps(data), req_id=data['data']['req_id'])


@app.route('/api/passport/signup/')
def reg():
    data = {
        "type": "signup",
        "data": {
            "req_id": sum(),
            "appkey": appkey,
            "uri": "/api/passport/signup/"
        }
    }
    title = u'注册'
    return render_template('reg.html', title=title, data=json.dumps(data), req_id=data['data']['req_id'])


# @app.route('/api/passport/list/')
# def goodList():
#     title = u'商品列表'
#     data = {}
#     goods = Goods.query.all()
#     for good in goods:
#         i = {
#             'id': good.id,
#             'g_name': good.g_name,
#             'g_price': good.g_price
#         }
#         data[good.id] = i
#
#     return render_template('goodslist.html', title=title, data=json.dumps(data))


@app.route('/api/passport/users/')
def userlist():
    title = u'用户列表'
    data = {}
    try:
        users = Sign.query.all()
        for u in users:
            i = {
                'id': u.id,
                'name': u.name,
                'req_id': u.req_id,
                'openid': u.openid,
                'appkey': appkey
            }
            data[u.id] = i
    except Exception as e:
        pass

    # print data

    return render_template('userlist.html', title=title, data=json.dumps(data))


@app.route('/api/passport/oderslist/')
def order():
    title = u'订单列表'
    data = {}
    oders = Orders.query.all()
    for o in oders:
        i = {
            'id': o.id,
            'order_num': o.order_num,
            'drawee': o.drawee,
            'address': o.address,
            'g_name': o.g_name,
            'g_price': o.g_price,
            'mobile': o.mobile,
            'g_type': o.g_type
        }
        data[o.id] = i

    return render_template('orderlist.html', title=title, data=json.dumps(data))


@app.route('/api/passport/payment/')
def pay():
    title = u'支付'
    loris = 'loris'
    # button 推
    data = {
        "type": "payment",
        "data": {
            "req_id": sum(),
            "openid": openID,
            "appkey": appkey,
            "uri": "/api/passport/payment/",
            'receive': loris,
            'orderid': str(random.randint(1, 9999999999)),
            'goods': {
                'title': 'iphone7',
                'amount': '6000.00',
            }

        }
    }

    return render_template('pay.html', title=title, data=json.dumps(data))


@app.route('/api/passport/receive/')
def tgoods():
    title = u'收货'
    data = {
        'type': 'receive',
        'data': {
            "req_id": sum(),
            "openid": openID,
            "appkey": appkey,
            "uri": "/api/passport/receive/",
            "orders": {
                "goods": {
                    "title": "袜子",
                    "amount": "1000.00",
                    "quantity": 1,
                },
                'users': {
                    "name": "姓名",
                    "mobile": "18918989110",
                    "address": "北京",
                },
                "orderid": "113030330",
                "created": "2017-02-01",
                "fee": "550.00",
                "discount": "300.00",
                "paymend": "250.00",
            }
        }
    }
    return render_template('tgoods.html', title=title, data=json.dumps(data))


@app.route('/api/passport/refunds/')
def rgoods():
    title = u'退货'
    data = {
        'type': 'refunds',
        'data': {
            "req_id": sum(),
            "openid": openID,
            "appkey": appkey,
            "uri": "/api/passport/receive/",
            "orders": {
                "goods": {
                    "title": "袜子",
                    "amount": "1000.00",
                    "quantity": 1,
                },
                'users': {
                    "name": "姓名",
                    "mobile": "18918989110",
                    "address": "北京",
                },
                "orderid": "113030330",
                "created": "2017-02-01",
                "fee": "550.00",
                "discount": "300.00",
                "paymend": "250.00",
            }
        }
    }
    return render_template('rgoods.html', title=title, data=json.dumps(data))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = connect_db()

    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()

# 程序运行
# server run


# if __name__ == '__main__':
#     app.run()


# test run

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=3000)
