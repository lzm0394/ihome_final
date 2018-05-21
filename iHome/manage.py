# _*_ coding:utf-8 _*_
""""
create by lu
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from Logic import creat_app, db, models

create_time = '2018/4/27 17:19'

app = creat_app('DevelopmentConfig')
manager = Manager(app)
# 添加迁移文件
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
