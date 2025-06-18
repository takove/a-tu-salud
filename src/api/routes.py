"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Post, TradingPost
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

    valid_password = check_password_hash(user.hashed_password, f'{body["password"]}{user.salt}')
    if not valid_password:
        return jsonify({
            "msg": "Email or password invalid"
        }), 400

    access_token = create_access_token(identity=user.id)
    response_body = {
        "id": user.id,
        "name": user.name,
        "token": access_token,
        "phone": user.phone,
        "email": user.email,
        "last_name": user.last_name,
        "city": user.city,
        "profile_picture": user.profile_picture,
    }

    return jsonify(response_body), 200

@api.route('/user/<int:userid>')
@jwt_required()
def get_user(userid):
    user = get_jwt_identity()
    get_user = User.query.get_or_404(userid)

    response_body = {
        "id": get_user.id,
        "name": get_user.name,
        "phone": get_user.phone,
        "email": get_user.email,
        "last_name": get_user.last_name,
        "city": get_user.city,
        "profile_picture": get_user.profile_picture,
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
            "list":[post.serializedonations() for post in result]
        }), 200
        else:
            return jsonify({
                "msg":"no posts found"
            }), 404

# moreInfo
@api.route('/post/<int:postid>') 
def get_post(postid):    
    get_post = Post.query.get_or_404(postid)
    print(get_post)
    return jsonify({"list":get_post.serializedonations()}), 200

# moreInfo
@api.route('/trade/<int:postid>') 
def get_exchange_post(postid):    
    get_exchange_post = TradingPost.query.get_or_404(postid)
    print(get_exchange_post)
    return jsonify({"list":get_exchange_post.serialize_trade()}), 200


@api.route('/donation', methods=['GET','POST'])
def handle_donations():
    if request.method=='GET':
        
        result = db.session.query(Post).join(User).filter(User.id == request.args.get('user_id'), Post.typeof == request.args.get('typeof')).all()
        
        if len(result) > 0:
            return jsonify({
            "list":[post.serializedonations() for post in result]
        }), 200
        else:
            return jsonify({
                "msg":"no posts found"
            }), 404

    body = request.json
    new_post = Post.create_donation(body)

    if type(new_post) == dict:
        return jsonify({
            "msg": new_post["msg"]
        }), new_post["status"]

    response_body = {
        "donations": new_post.serializedonations()

    }
    return jsonify(response_body), 200

@api.route('/request', methods=['GET','POST'])
def handle_request():
    if request.method == 'GET':
        result = db.session.query(Post).join(User).filter(User.id == request.args.get('user_id'), Post.typeof == request.args.get('typeof')).all()
        
        if len(result) > 0:
            return jsonify({
            "list":[post.serializedonations() for post in result]
        }), 200
        else:
            return jsonify({
                "msg":"no posts found"
            }), 404

    body = request.json
    new_request = Post.create_request(body)

    if type(new_request) == dict:
        return jsonify({
            "msg": new_request["msg"]
        }), new_request["status"]

    response_body = {
        "request": new_request.serializerequest()

    }
    return jsonify(response_body), 200

########## el atelier de Alejo #########
@api.route('/user/trade', methods=['POST'])
def trade_post():
    body = request.json

    new_trade = TradingPost(
        title = body["nameA"] + " (" + body["presentA"] + ", " + body["dosisA"] + ") por " + body["nameB"] + " (" + body["presentB"] + ", " + body["dosisB"] + ")",
        description = body.get("description"),
        presentation = body["presentA"],
        active_component = body["activeCompA"],
        expiration_date = body["expDateA"],
        dosis = body["dosisA"],
        quantity = body["quantityA"],
        name = body["nameA"],
        medicine_picture = body.get("pictureA"),
        req_presentation =  body["presentB"],
        req_active_component = body["activeCompB"],
        req_expiration_date = body["expDateB"],
        req_dosis = body["dosisB"],
        req_quantity = body["quantityB"],
        req_name = body["nameB"],
        req_medicine_picture = body.get("pictureB"),
        user_id = body["userid"],
        typeof = body["type"]
    )

    if not isinstance(new_trade, TradingPost):
        return jsonify({
            "msg": "Server error"
        }), 500

    saved = new_trade.save_and_commit()

    if saved is False:
        return jsonify({
            "msg": "Data Base error"
        }), 500

    response_body = {
        "msg": "New trade created!",
        "title": new_trade.title
    }

    return jsonify(response_body), 200

@api.route('/trades', methods=['GET'])
def get_trades():
    if request.args.get('user_id') != None:
        result = db.session.query(TradingPost).join(User).filter(User.id == request.args.get('user_id')).all()
        
        if len(result) > 0:
            return jsonify({
            "list":[post.serialize_trade() for post in result]
        }), 200
        else:
            return jsonify({
                "msg":"no posts found"
            }), 404

        

@api.route('/trades-filter', methods=['GET'])
def get_trades_filter():
    filters = [
        ]

    if request.args.get('name') != None:
            filters.append(TradingPost.name == request.args.get('name'))

    if request.args.get('expiration_date') != None:
        filters.append(TradingPost.expiration_date == request.args.get('expiration_date'))

    if request.args.get('typeof') != None:
        filters.append(TradingPost.typeof == request.args.get('typeof'))

    if request.args.get('presentation') != None:
        filters.append(TradingPost.presentation == request.args.get('presentation'))

    if request.args.get('quantity') != None:
        filters.append(TradingPost.quantity == request.args.get('quantity'))

    if request.args.get('city') != None:
        filters.append(User.city == request.args.get('city'))

    # post = db.session.query()
    try:
        result = db.session.query(TradingPost).join(User).filter(*filters).all()
    except Error:
        return jsonify({
            "msg":"something unexpected happened"
        }), 500
    if len(result) > 0:
        return jsonify({
        "msg":"here is the list of posts",
        "list":[post.serialize_trade() for post in result]
    }), 200
    else:
        return jsonify({
            "msg":"no posts found"
        }), 404
# @api.route('/delete-posts/<int:postid>', methods=['DELETE'])
# def delete_posts(postid):
#     try:
#         result = Post.query.filter_by(Post.id == postid).one_or_none()
#         if result != None:
#             db.session.delete(result)
#             db.session.commit()
#             return jsonify({
#                 "msg":"Post deleted succesfully"
#             }), 200
#         else:
#             return jsonify({
#                 "msg":"something unexpected happened"
#             }),400
        
#     except Exception as error:
#         db.session.rollback()
    