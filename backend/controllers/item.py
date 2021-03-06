from flask import request, Blueprint, jsonify

from models.item import ItemModel
from helpers.errors import *
from helpers.validators import *
from helpers.security import *

item_api = Blueprint('item_api', __name__)


@item_api.route('/items', methods=['GET'])
def get_all_items():
    return jsonify([item.represent() for item in ItemModel.query.all()]), 200


@item_api.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = ItemModel.find_by_id(item_id)
    if item:
        return jsonify(item.represent())
    return jsonify({'message': 'No item found'}), 404


@item_api.route('/items', methods=['POST'])
def create_item():
    try:
        # VALIDATE REQUEST'S HEADERS, TOKEN, BODY
        token = validate_request_header(request, content=True, authorization=True)
        user = identity(token)  # validate request's token
        validated_request_body = validate_request_body(request, action='create', resource='item')

        # CREATE ITEM
        validated_request_body['author_id'] = user.id
        item = ItemModel(**validated_request_body)
        item.save_to_db()

        # SUCCEED, RETURN CREATED CATEGORY
        return jsonify(item.represent()), 201

    except BadRequestError as err:
        return jsonify(err.represent()), 400
    except UnauthorizedError as err:
        return jsonify(err.represent()), 401
    except NotFoundError as err:
        return jsonify(err.represent()), 404


@item_api.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        # VALIDATE REQUEST'S HEADERS, TOKEN, BODY
        token = validate_request_header(request, content=True, authorization=True)
        user = identity(token)  # validate request's token
        validated_request_body = validate_request_body(request, action='update',
                                                       resource_id=item_id, resource='item')

        # AUTHORIZE USER
        item = ItemModel.find_by_id(item_id)
        if user.id != item.author_id:
            return jsonify({'message': 'Unauthorized action'}), 401

        # UPDATE CATEGORY
        item.name = validated_request_body['name']
        item.description = validated_request_body['description']
        item.category_id = validated_request_body['category_id']
        item.save_to_db()

        # SUCCEED, RETURN UPDATED CATEGORY
        return jsonify(item.represent()), 200

    except BadRequestError as err:
        return jsonify(err.represent()), 400
    except UnauthorizedError as err:
        return jsonify(err.represent()), 401
    except NotFoundError as err:
        return jsonify(err.represent()), 404


@item_api.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    # VALIDATE REQUEST HEADER, TOKEN
    try:
        token = validate_request_header(request, content=False, authorization=True)
        user = identity(token)  # validate request's token

        # VALIDATE ITEM_ID
        item = ItemModel.find_by_id(item_id)
        if item is None:
            return jsonify({'message': 'No item found'}), 404

        # AUTHORIZE USER
        if user.id != item.author_id:
            return jsonify({'message': 'Unauthorized action'}), 401

        # DELETE CATEGORY
        item.delete_from_db()

        # SUCCEED, RETURN MESSAGE
        return jsonify({'message': 'Item deleted'}), 200

    except BadRequestError as err:
        return jsonify(err.represent()), 400
    except UnauthorizedError as err:
        return jsonify(err.represent()), 401
    except NotFoundError as err:
        return jsonify(err.represent()), 404

