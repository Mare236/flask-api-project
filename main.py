from flask import Flask, abort, render_template, redirect, url_for, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from schemas import PutSchema, NestedPutSchema, OstecenjeSchema, NestedOstecenjeSchema, UserSchema



app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///baza.db"
app.config["JWT_SECRET_KEY"] = "199nudj2i9jf379kocer8ut54ds0"  # Change this!
jwt = JWTManager(app)

db = SQLAlchemy()
db.init_app(app)

#MODELI

class Put(db.Model):
    __tablename__ = "put"
    id = db.Column(db.Integer, primary_key = True)
    ime = db.Column(db.String(100))
    poddeonica = db.Column(db.String(100))
    sirina = db.Column(db.Integer)
    duzina_poddeonice = db.Column(db.Integer)
    broj_traka = db.Column(db.Integer)
    ostecenja = db.relationship("Ostecenje", back_populates="put", lazy="dynamic", cascade="all, delete")


class Ostecenje(db.Model):
    __tablename__ = "ostecenje"
    id = db.Column(db.Integer, primary_key = True)
    tip_ostecenja = db.Column(db.String(100))
    PSI_broj = db.Column(db.Integer)
    stacionaza = db.Column(db.String(100))
    kostanje = db.Column(db.Integer)
    put_id = db.Column(db.Integer, db.ForeignKey("put.id"), unique=False, nullable=False)
    put = db.relationship("Put", back_populates="ostecenja")

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)


#SCHEMAS INITIALIZATION
put_schema = PutSchema()
putevi_schema = NestedPutSchema(many=True)
ostecenje_schema = NestedOstecenjeSchema()
ostecenja_schema = NestedOstecenjeSchema(many=True)
user_schema = UserSchema()

#DB INITIALIZATION
with app.app_context():
    db.create_all()

#ENDPOINTS

@app.route("/road", methods=["POST"])
def post_put():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400
    try:
        data = put_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422
    put = Put(ime=data["ime"], poddeonica=data["poddeonica"], sirina=data["sirina"], duzina_poddeonice=data["duzina_poddeonice"], broj_traka=data["broj_traka"])
    db.session.add(put)
    db.session.commit()
    return {"message": "Successfuly add new PUT."}

@app.route("/post/odsteta", methods=["POST"])
def post_odsteta():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400
    try:
        data = ostecenje_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422
    ostecenje = Ostecenje(tip_ostecenja=data["tip_ostecenja"],
        PSI_broj=data["PSI_broj"],
        stacionaza=data["stacionaza"],
        kostanje=data["kostanje"],
        put_id=data["put_id"])
    db.session.add(ostecenje)
    db.session.commit()
    return {"message": "Successfully added new Ostecenje."}


@app.route("/road")
#@jwt_required()
def get_all_puteve():
    putevi = Put.query.all()
    ostecenja = Ostecenje.query.all()
    # Serialize the queryset
    putevi_results = putevi_schema.dump(putevi)
    print(putevi)
    print(putevi_results)
    return {"putevi": putevi_results}


@app.route("/put/<int:id>")
def get_put(id):
    try:
        put = Put.query.filter(Put.id == id).one()
    except (SQLAlchemyError, ValueError):
        abort(500, "Can not get items.")
    put_result = put_schema.dump(put)
    ostecenja_result = ostecenja_schema.dump(put.ostecenja.all())
    return jsonify(Saobracajnica=put_result, Ostecenja=ostecenja_result)


@app.route("/all_damages")
def get_all_damages():
    ostecenja = Ostecenje.query.all()
    ostecenja_result = ostecenja_schema.dump(ostecenja)
    return jsonify(Ostecenja=ostecenja_result)

@app.route("/search_road")
def search_road():
    query_name = request.args.get("name")
    putevi = Put.query.filter(Put.ime == query_name).all()
    putevi_result = putevi_schema.dump(putevi)
    if putevi_result:
        return {"Road": putevi_result}
    else:
        return {"Not Found."}

@app.route("/update_road_name/<int:road_id>", methods=["PATCH"])
def patch_new_name(road_id):
    new_name = request.args.get("new_name")
    road = db.get_or_404(Put, road_id)
    if road:
        road.ime = new_name
        db.session.commit()
        return {"message": "Successfully updated name."}
    else:
        return {"message": "Error: item not found."}


@app.route("/delete_road/<int:road_id>", methods=["DELETE"])
def delete_road(road_id):
    road = db.get_or_404(Put, road_id)
    db.session.delete(road)
    db.session.commit()
    return {"message": "Road deleted"}


# @app.route("/register", methods=["POST"])
# def register_user():
#     data = request.get_json()
#     user_data = user_schema.load(data)
#     if User.query.filter(User.user == user_data["user"]).first():
#         abort(409, message="A user with this username allready exists")
#     user = User(user=user_data["user"], password=pbkdf2_sha256.hash(user_data["password"]))
#     db.session.add(user)
#     db.session.commit()
#
#     return {"message": "Successfully registered."}
#
# @app.route("/login", methods=["POST"])
# def login_user():
#     data = request.get_json()
#     user_data = user_schema.load(data)
#     user_login = User.query.filter(User.user == user_data["user"]).first()
#     if user_login and pbkdf2_sha256.verify(user_data["password"], user_login.password):
#         access_token = create_access_token(identity=user_login.id)
#         #access_token = "1234567890"
#         return {"access_token": access_token}
#     abort(401, message="Invalid credentials")


if __name__ == "__main__":
    app.run(debug=True, port=5117)