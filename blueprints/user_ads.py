from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask.views import MethodView
import sqlite3
from database import db

import datetime


bp = Blueprint('user_ads', __name__)


class UserAdsView(MethodView):
    def get(self, user_id):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE seller_id = ?',
            (user_id,),
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])

    def post(self):
        seller_id = session['user_id']
        #ad
        request_json = request.json
        title = request_json.get('title')
        tags = request_json.get('tags')
        car = request_json.get('car')
        date = datetime.datetime.now()
        #car
        make = car.get('make')
        model = car.get('model')
        colors = car.get('colors')
        mileage = car.get('mileage')
        num_owners = car.get('num_owners')
        if not num_owners:
            num_owners = 1
        reg_number = car.get('reg_number')
        images = car.get('images')
        #image
        img_title = images.get('title')
        url = images.get('url')

        if not title or not tags or not car:
            return 'Not enough user data', 400

        if not make or not model or not colors or not mileage or not reg_number or images:
            return 'Not enough car data', 400

        if not img_title or not url:
            return 'Not enough image data', 400

        con = db.connection

        try:
            cur = con.execute(
                'INSERT INTO car (make, model, mileage, num_owners, reg_number) '
                'VALUES (?, ?, ?, ?, ?)',
                (make, model, mileage, num_owners, reg_number),
            )
            con.commit()
            car_id = cur.lastrowid
        except sqlite3.IntegrityError:
            return '', 409


        try:
            con.execute(
                'INSERT INTO ad (title, date, seller_id, car_id) '
                'VALUES (?, ?, ?, ?)',
                (title, date, seller_id, car_id),
            )
            con.commit()
        except sqlite3.IntegrityError:
            return '', 409

        try:
            con.execute(
                'INSERT INTO image (title, url, car_id) '
                'VALUES (?, ?, ?, ?)',
                (img_title, url, car_id),
            )
            con.commit()
        except sqlite3.IntegrityError:
            return '', 409


        # add seller info if seller too
        # id = print(cur.lastrowid)

        cur = con.execute(
            'SELECT * '
            'FROM ad JOIN car on ad.car_id = car.id JOIN image i on car.id = i.car_id '
            'WHERE car.id = ?',
            (car_id,),
        )
        all_data = dict(cur.fetchall())

        return all_data, 201


bp.add_url_rule('<int:user_id>/ads', view_func=UserAdsView.as_view('user_ads'))
#bp.add_url_rule('ads', view_func=UserAdsView.as_view('user_ads'))