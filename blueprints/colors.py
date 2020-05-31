from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask.views import MethodView

from database import db


bp = Blueprint('colors', __name__)


class ColorsView(MethodView):
    def get(self):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM color'
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])


    def post(self):
        request_json = request.json
        name = request_json.get('name')
        hex = request_json.get('hex')
        print(name)
        print(type(name))
        if not name or not hex:
            return '', 400

        con = db.connection
        con.execute(
            'INSERT INTO color (name, hex) '
            'VALUES (?, ?)',
            (name, hex),
        )
        con.commit()

        cur = con.execute(
            'SELECT * '
            'FROM color '
            'WHERE hex = ?',
            (hex,),
        )
        result = cur.fetchone()
        print(result)
        return jsonify(dict(result)), 201
        #else:
        #    return '', 403

bp.add_url_rule('', view_func=ColorsView.as_view('colors'))
