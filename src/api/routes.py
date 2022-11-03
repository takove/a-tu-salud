"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Post
from api.utils import generate_sitemap, APIException
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import bcrypt


api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def log_user():
    body = request.json
    user = User.query.filter_by(email = body["email"]).one_or_none()
    if user is None:
        return jsonify({
            "msg": "Email or password invalid"
        }), 400

    valid_password = check_password_hash(user.hashed_password, f'{body["password"]}{user.salt}') #esto debería ser user.hashed_password en vez de user.password
    if not valid_password:
        return jsonify({
            "msg": "Email or password invalid"
        }), 400

    access_token = create_access_token(identity=user.id)
    response_body = {
        "name": user.name,
        "token": access_token,
        "phone": user.phone,
        "email": user.email,
        "last_name": user.last_name,
        "city": user.city,
    }

    return jsonify(response_body), 200

@api.route('/register', methods=['POST'])

def make_user():
    if request.method == "POST":
        body = request.json
        user = User.query.filter_by(email = body["email"]).one_or_none()
        if user:
            return jsonify({
                "msg": "Email already in use"
            }), 400
        salt = bcrypt.gensalt().decode()
        hashed_password = generate_password_hash(f"{body['password']}{salt}")

        new_user = User(
            email=body['email'],
            phone=body['phone'], 
            hashed_password=hashed_password, 
            salt=salt,
            name=body['name'], 
            last_name=body['last_name'], 
            city=body['city'], 
            profile_picture=body.get('profile_picture')
        )
        print(new_user.serialize())
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "msg":"something unexpected happened",
                "error msg": error.args
            }), 500
        return jsonify(new_user.serialize()),201

# Backend 03 Como visitante quiero poder acceder a la información de busqueda para encontrar lo que necesita
# consultar si el medicamento existe
# filtrar el medicamento por fecha de vencimiento, cantidad, presentación, ciudad. etc.
@api.route('/posts', methods=['GET'])
def posts():
    if request.method == "GET":
        
        filters = [                
            ]
        
        # print(db.session.query(Post).join(Post.users).filter(Post.users.city == 'test'))

        if request.args.get('name') != None:
            filters.append(Post.name == request.args.get('name'))
        
        if request.args.get('expiration_date') != None:
            filters.append(Post.expiration_date == request.args.get('expiration_date'))
        
        if request.args.get('typeof') != None:
            filters.append(Post.typeof == request.args.get('typeof'))
        
        if request.args.get('presentation') != None:
            filters.append(Post.presentation == request.args.get('presentation'))
        
        if request.args.get('quantity') != None:
            filters.append(Post.quantity == request.args.get('quantity'))

        if request.args.get('city') != None:
            filters.append(User.city == request.args.get('city'))
        
        # post = db.session.query()
        try:
            result = db.session.query(Post).join(User).filter(*filters).all()
        except Error:
            return jsonify({
                "msg":"something unexpected happened"
            }), 500
        if len(result) > 0:
            return jsonify({
            "msg":"here is the list of posts",
            "list":[post.serialize() for post in result]
        }), 200
        else:
            return jsonify({
                "msg":"no posts found"
            }), 404

@api.route('/solicitud', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'GET':
        get_post = Post.query.all()

        if get_post is None:
            return jsonify({
                "msg": "There are no requests yet!"
            }), 400

        post_list = list(map(lambda requests: requests.serialize(), get_post))

        return jsonify(post_list), 200

    body = request.json    
    new_post = Post.create(body)   

    if type(new_post) == dict:   
        return jsonify({
            "msg": new_post["msg"]
        }), new_post["status"]

    response_body = {     
        "user": new_post.serialize()
    }
    return jsonify(response_body), 200

