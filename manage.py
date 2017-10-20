# -*- coding:utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from three import *

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# 数据库操作
# python three.py db migrate
# python three.py db upgrade

@manager.command
def dev():
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve(open_url=True, port=3000)


if __name__ == '__main__':
    manager.run()
    dev()
