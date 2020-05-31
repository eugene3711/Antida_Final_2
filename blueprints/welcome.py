from flask import (
    Blueprint,
    request,
    session,
)
from database import db
import sqlite3

bp = Blueprint('welcome', __name__)


@bp.route('/')
def welcome():
    try:
        con = db.connection
        cur = con.execute(
            'SELECT first_name, last_name '
            'FROM user '
            'WHERE id = ?',
            (session['user_id'],),
        )
        user = dict(cur.fetchone())
        print(user['username'])
        call = user['username']
    except sqlite3.Error as e:
        print(f"Ошибка базы данных {e}")
        all = "Stranger!"
    except Exception as e:
        print(f"Ошибка {e}")
        call = "Stranger!"
    return f"Welcome {call}"
