
# 实例化认证蓝图，并将视图函数与路由绑定到该蓝图
from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import views
