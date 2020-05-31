if session['user_id']:
    con = db.connection
    cur = con.execute(
        'SELECT ad.id, ad.seller_id, ad.title, ad.date,'
        'car.make, car.model, car.mileage, car.num_owners, car.reg_number, '
        'color.id, color.name, color.hex, image.title, image.url '
        'FROM ad JOIN car on ad.car_id = car.id '
        'JOIN carcolor ON ad.car_id=carcolor.car_id '
        'JOIN color on carcolor.color_id = color.id '
        'JOIN image ON car.id = image.car_id ;'
    )
para = ', '.join(f'{key}="{value}"' for key, value in param.items())
        print(f"para: {para}")

new = []
        for k,v in param.items():
            new.append(f'{k}="{v}"')
        new =', '.join(new)
        print(f"new: {new}")

в app прописываем неизменяемый URL
в блюпринте указываем остальную часть, можно с изменяемым параметром


ads post

cur = con.execute(
                'SELECT ad.id, ad.seller_id, ad.title, ad.date, '
                'tag.name, car.make, car.model, color.id, color.name, color.hex, '
                'car.mileage, car.num_owners, car.reg_number, image.title, image.url '
                'FROM ad '
                'JOIN seller ON ad.seller_id = seller.id '
                'JOIN car ON ad.car_id = car.id '
                'JOIN carcolor ON ad.car_id=carcolor.car_id '
                'JOIN color on carcolor.color_id = color.id '
                'JOIN image ON car.id = image.car_id '
                'JOIN adtag ON ad.id=adtag.ad_id '
                'JOIN tag ON adtag.tag_id = tag.id ; '
            )
seller_id = request.args.get("seller_id")
        tags = request.args.get("tags")
        make = request.args.get("make")
        model = request.args.get("model")
        print(f"seller_id {seller_id} \n"
              f"tags {tags} \n"
              f"make {make} \n"
              f"model {model} ")


"""
    def post(self):
        user_id = session.get('user_id')
        if user_id is None:
            return '', 403

        request_json = request.json
        title = request_json.get('title')

        if not title:
            return '', 400


        con = db.connection
        con.execute(
            'INSERT INTO ad (title, seller_id) '
            'VALUES (?, ?)',
            (title, user_id),
        )
        con.commit()

        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE seller_id = ? AND title = ?',
            (user_id, title),
        )
        ad = cur.fetchone()
        return jsonify(dict(ad)), 201
"""

users update

con.execute(
    'UPDATE user '
    'SET username = ? '
    'WHERE id = ?',
    (username, user_id),
)