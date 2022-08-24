import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(payload):
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort (404)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(404)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    body = request.get_json()
    print(body)
    try:
        recipe = body['recipe']
        title = body['title']

        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        drink.insert()
        drinks = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    if request.method == "PATCH":
        body = request.get_json()
        print(body)
        
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)

        try:
            title = body.get('title', None)
            recipe = body.get('recipe', None)

            if title != None:
                drink.title = title
            if recipe != None:
                drink.recipe = json.dumps(body['recipe'])

            drink.update()
            drinks = [drink.long()]

            return jsonify({
                'success': True,
                'drinks': drinks
            }), 200

        except:
            abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200  
    except:
        abort(422)
    

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code