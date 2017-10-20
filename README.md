## 第三方登录（demo）
用Python2.7 、flask框架 写的第三方登录平台

结构如下：

```
.
├── README.md
├── Makefile
├── manage.py
├── static
│   ├── css
│   │   └── style.css
│   └──  js
│       ├── jquery.js
│       └── jquery.qrcode.min.js
│
├── templates
│   ├── footer.html
│   ├── goodslist.html
│   ├── header.html
│   ├── index.html
│   ├── orderlist.html
│   ├── pay.html
│   ├── qrlogin.html
│   ├── reg.html
│   ├── rgoods.html
│   ├── tgoods.html
│   └── userlist.html
│
├── requirements.txt
├── schema.sql
├── server.py
├── three.py
└── tests.py
```


#### 数据库操作
```
<首次操作>

1、初始化：
$ python manage.py db init

2、数据迁移，自动创建迁移代码
$ Python manage.py db migrate

3、更新数据库
$ python manage.py db upgrde

<后续操作>

$ python manage.py db migrate -m 'log'

$ python manage.py db upgrde

```

#### 数据库回滚
```
# 获取 History ID
$ python manager.py db history

# 回滚到某个 history
$ python manager.py db downgrade <history_id>

```

#### 项目启动

```
启动：
$ Python manage.py runserver

开发模式:
$ python manage.py dev

debug模式:
$ python manage.py runserver --debug

指定端口启动：
$ python manage.py runserver --port=8888
$ python manage.py runserver --debug --port=8888

```
