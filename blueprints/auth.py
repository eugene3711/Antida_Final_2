from flask import (
    Blueprint,
    request,
    session,
)
from werkzeug.security import check_password_hash

from database import db



bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    request_json = request.json
    email = request_json.get('email')
    password = request_json.get('password')

    if not email or not password:
        return '', 400

    con = db.connection
    cur = con.execute(
        'SELECT email, password, id '
        'FROM account '
        'WHERE email = ?',
        (email,),
    )
    user = cur.fetchone()

    if user is None:
        return '', 403

    if not check_password_hash(user['password'], password):
        return '', 403

    print(user['id'])
    print(session)
    session['user_id'] = user['id']
    return '', 200


@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return '', 200
