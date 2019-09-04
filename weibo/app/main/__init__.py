
from flask import Blueprint

# 实例化蓝图main
main = Blueprint("main", __name__)

# 导入视图函数、异常处理函数
from . import views, errors
