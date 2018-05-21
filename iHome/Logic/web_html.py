# _*_ coding:utf-8 _*_
""""
create by lu
"""
from flask_wtf.csrf import generate_csrf

create_time = '2018/4/28 11:48'

from flask import Blueprint, current_app, make_response

html_hand = Blueprint('html', __name__)


@html_hand.route('/<re(".*"):file_name>')
def get_html_file(file_name):
    if not file_name:
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    response = make_response(current_app.send_static_file(file_name))
    response.set_cookie("csrf_token", generate_csrf())

    return response
