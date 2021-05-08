from flask import Blueprint

'''建立主藍圖'''

main = Blueprint('main', __name__)

from . import views #防止循環匯入