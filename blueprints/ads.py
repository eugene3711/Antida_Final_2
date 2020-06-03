from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask.views import MethodView
import datetime
import sqlite3
from database import db


bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):

        params = {
            "seller_id" : request.args.get("seller_id"),
            #"tags" : request.args.get("tags"),
            "make" : request.args.get("make"),
            "model" : request.args.get("model")
        }
        params = {key: value for key, value in params.items() if value is not None}
        pars = ' AND '.join(f'{key}="{value}"' for key, value in params.items())

        where = ""
        if pars:
            where = f'WHERE {pars}'

        select = """
                 SELECT ad.id, ad.seller_id, ad.title, ad.date, 
                 car.make, car.model, car.mileage, car.num_owners, car.reg_number, t.name,
                 color.id, color.name, color.hex                                                 
                 FROM ad JOIN car on ad.car_id = car.id           
                 JOIN adtag a on ad.id = a.ad_id
                 JOIN tag t on a.tag_id = t.id
                 JOIN image ON car.id = image.car_id
                 JOIN carcolor ON ad.car_id=carcolor.car_id
                 JOIN color on carcolor.color_id = color.id                     
                 """
        with db.connection as con:
            cur = con.execute(select + where + ';')
            result = cur.fetchall()

        return jsonify([dict(row) for row in result])


    def post(self):
        try:
            seller_id = session['user_id']
        except Exception as e:
            print(e)
            return '', 403
        # ad
        request_json = request.json
        title = request_json.get('title')
        tags = request_json.get('tags')
        car = request_json.get('car')
        date = datetime.datetime.now()
        # car
        make = car.get('make')
        model = car.get('model')
        colors = car.get('colors')
        mileage = car.get('mileage')
        num_owners = car.get('num_owners')
        if not num_owners:
            num_owners = 1
        reg_number = car.get('reg_number')
        images = car.get('images')
        # image
        for image in images:
            img_title = image.get('title')
            url = image.get('url')

        if not title or not tags or not car:
            return 'Not enough user data', 400

        if not make or not model or not colors or not mileage or not reg_number or not images:
            return 'Not enough car data', 400

        if not img_title or not url:
            return 'Not enough image data', 400

        try:
            with db.connection as con:
                cur = con.execute(
                'INSERT INTO car (make, model, mileage, num_owners, reg_number) '
                'VALUES (?, ?, ?, ?, ?)',
                (make, model, mileage, num_owners, reg_number),
                )
                con.commit()
                car_id = cur.lastrowid
        except sqlite3.IntegrityError as e:
            return '', 409

        for color in colors:
            try:
                con.execute(
                    'INSERT INTO carcolor (car_id, color_id) '
                    'VALUES (?, ?)',
                    (car_id, color),
                )

            except sqlite3.IntegrityError as e:
                return '', 409
        con.commit()

        try:
            cur = con.execute(
                'INSERT INTO ad (title, date, seller_id, car_id) '
                'VALUES (?, ?, ?, ?)',
                (title, date, seller_id, car_id),
            )
            con.commit()
            ad_id = cur.lastrowid
        except sqlite3.IntegrityError as e:
            return '', 409


        tags_ids = []
        for tag in tags:
            try:
                cur = con.execute(
                    'INSERT INTO tag (name) '
                    'VALUES (?)',
                    (tag,),
                )
                con.commit()
                t_id = cur.lastrowid
                tags_ids.append(t_id)
            except Exception as e:
                cur = con.execute(
                    'SELECT id '
                    'FROM tag '
                    'WHERE name = ?',
                    (tag,),
                )
                con.commit()
                result = cur.fetchone()
                tag_id = dict(result)
                tags_ids.append(tag_id['id'])

        try:
            for tag_id in tags_ids:

                con.execute(
                    'INSERT INTO adtag (tag_id, ad_id) '
                    'VALUES (?, ?)',
                    (tag_id, ad_id),
                )
            con.commit()
        except Exception as e:
            return f'{e}', 400
        except sqlite3.OperationalError as e:
            return f'{e}', 400

        try:
            con.execute(
                'INSERT INTO image (title, url, car_id) '
                'VALUES (?, ?, ?)',
                (img_title, url, car_id),
            )
            con.commit()
        except sqlite3.IntegrityError as e:
            return '', 409

        cur = con.execute(
            'SELECT * '
            'FROM ad JOIN car on ad.car_id = car.id JOIN image i on car.id = i.car_id '
            'WHERE car.id = ?',
            (car_id,),
        )
        all_data = dict(cur.fetchone())

        return all_data, 201

class AdView(MethodView):
    def get(self, ad_id):
        with db.connection as con:
            cur = con.execute("""
                SELECT ad.id, ad.seller_id, ad.title, ad.date, 
                     car.make, car.model, car.mileage, car.num_owners, car.reg_number, t.name,
                     color.id, color.name, color.hex                                                 
                     FROM ad JOIN car on ad.car_id = car.id           
                     JOIN adtag a on ad.id = a.ad_id
                     JOIN tag t on a.tag_id = t.id
                     JOIN image ON car.id = image.car_id
                     JOIN carcolor ON ad.car_id=carcolor.car_id
                     JOIN color on carcolor.color_id = color.id 
                WHERE ad.id = ?;
                """,
                (ad_id,),
            )
            ad = cur.fetchone()
        if ad is None:
            return '', 404
        return jsonify(dict(ad))

    def patch(self, ad_id):
        return 'Not implemented', 200


    def delete(self, ad_id):
        try:
            seller_id = session['user_id']
        except Exception as e:
            print(e)
            return '', 403

        con = db.connection
        cur = con.execute(
            'DELETE '
            'FROM ad '
            'WHERE id = ?',
            (ad_id,),
        )
        ad = cur.fetchone()
        if ad is None:
            return '', 404


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdView.as_view('ad'))

