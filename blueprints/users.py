import sqlite3

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)
from flask.views import MethodView
from werkzeug.security import generate_password_hash

from database import db

bp = Blueprint('users', __name__)

class UsersView(MethodView):
    def get(self):
        if session['user_id']:
            con = db.connection
            cur = con.execute(
                'SELECT account.id, s.phone '
                'FROM account JOIN seller s on account.id = s.user_id'
            )
            rows = cur.fetchall()
            return jsonify([dict(row) for row in rows])
        else:
            return '', 403
    def post(self):
        request_json = request.json
        email = request_json.get('email')
        password = request_json.get('password')
        first_name = request_json.get('first_name')
        last_name = request_json.get('last_name')
        if request_json.get('is_seller').lower() == "true":
            is_seller = True
        else:
            is_seller = False

        if is_seller:
            phone = request_json.get('phone')
            zip_code = request_json.get('zip_code')
            city_id = request_json.get('city_id')
            street = request_json.get('street')
            home = request_json.get('home')
        if not email or not password or not first_name or not last_name:
            return 'Not enough user data', 400

        if is_seller:
            if not phone or not zip_code or not city_id or not street or not home:
                return 'Not enough seller data', 400

        password_hash = generate_password_hash(password)

        con = db.connection

        try:
            cur = con.execute(
                'INSERT INTO account (email, password, first_name, last_name, is_seller) '
                'VALUES (?, ?, ?, ?, ?)',
                (email, password_hash, first_name, last_name, is_seller),
            )
            con.commit()
            user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            return f"{e}", 409
        except Exception as e:
            return f"{e}", 409
        if is_seller:

            try:
                con.execute(
                    'INSERT INTO seller (phone, zip_code, city_id, street, home, user_id) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (phone, zip_code, city_id, street, home, user_id),
                )
                con.commit()
            except sqlite3.IntegrityError as e:
                return f"{e}", 409
            except Exception as e:
                return f"{e}", 409

        cur = con.execute(
            'SELECT * '
            'FROM account JOIN seller ON account.id = seller.user_id '
            'WHERE account.id = ? ',
            (user_id,),
        )
        all_data = [dict(row) for row in cur.fetchall()]

        return all_data, 201


class UserView(MethodView):
    def get(self, user_id):

        try:
            u_id = session['user_id']
        except Exception as e:
            return '', 403

        con = db.connection
        cur = con.execute(
            'SELECT account.id, account.email, account.first_name, account.last_name, account.is_seller, '
            'seller.phone, seller.zip_code, seller.city_id, seller.street, seller.home '
            'FROM account JOIN seller ON account.id = seller.user_id '
            'WHERE account.id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404
        user_info = dict(user)

        return jsonify(user_info), 200


    def patch(self, user_id):
        try:
            u_id = session['user_id']
        except Exception as e:
            return '', 403

        request_json = request.json

        if not request_json:
            return '', 400

        con = db.connection

        cur = con.execute(
            'SELECT id, email '
            'FROM account '
            'WHERE id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404

        params = ','.join(f'{key} = ?' for key in request_json)
        query = f'UPDATE account SET {params} WHERE id = ?'
        try:
            con.execute(query, (*request_json.values(), user_id))
        except Exception as e:
            return f'Error {e}', 400

        con.commit()
        return '', 200


bp.add_url_rule('', view_func=UsersView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UserView.as_view('user'))
