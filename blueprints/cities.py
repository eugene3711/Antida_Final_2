from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask.views import MethodView

from database import db


bp = Blueprint('cities', __name__)


class CitiesView(MethodView):
    def get(self):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM city'
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])


    def post(self):
        request_json = request.json
        name = request_json.get('name')
        print(name)
        print(type(name))
        if not name:
            return '', 400

        con = db.connection
        con.execute(
            'INSERT INTO city (name) '
            'VALUES (?)',
            (name,),
        )
        con.commit()

        cur = con.execute(
            'SELECT * '
            'FROM city '
            'WHERE name = ?',
            (name,),
        )
        cities = cur.fetchall()
        return jsonify(dict(cities)), 201
        #else:
        #    return '', 403

bp.add_url_rule('', view_func=CitiesView.as_view('cities'))
