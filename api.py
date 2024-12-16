from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
import os

from utils import map_commutator

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'flutter_app',
    'password': os.environ["MARIA_DB_PASS"],
    'database': 'rubik_app_db',
    'port': 3306,
    'cursorclass': DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)


@app.route('/')
def home():
    return "APP IS UP AND RUNNING", 200


# TODO: shall connect each time? or reuse connection?
@app.route('/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT user_name FROM users")
            users = [row['user_name'] for row in cursor.fetchall()]
        return jsonify(users)
    finally:
        connection.close()


@app.route('/buffer/<piece_type>/<user_name>', methods=['GET'])
def get_user_buffer(piece_type, user_name):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT buffer_{piece_type} AS buffer
                FROM users
                WHERE user_name = '{user_name}'
            """
            cursor.execute(query)
            buffer = cursor.fetchone()
        return jsonify(buffer)
    finally:
        connection.close()


@app.route('/stickers/<piece_type>/<user_name>', methods=['GET'])
def get_user_stickers_and_letters(piece_type, user_name):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT sticker, letter 
                FROM {piece_type}_stickers 
                WHERE user_name = '{user_name}'
            """
            cursor.execute(query)
            results = cursor.fetchall()
        return jsonify(results)
    finally:
        connection.close()


@app.route('/commutators/<piece_type>/<user_name>', methods=['GET'])
def get_user_commutators(piece_type, user_name):
    connection = get_db_connection()

    buffer = get_user_buffer(piece_type, user_name).get_json()['buffer']
    try:
        with (connection.cursor() as cursor):
            query = f"""
            SELECT first_sticker, second_sticker, commutator, commutator_simplified
            FROM {piece_type}_commutators
            WHERE buffer_sticker = '{buffer}'
            """
            cursor.execute(query)
            results = cursor.fetchall()

            stickers_and_letters = get_user_stickers_and_letters(piece_type, user_name).get_json()
            stickers_to_letters = {elem['sticker']: elem['letter'] for elem in stickers_and_letters}

            results = [
                {
                    'first_letter': stickers_to_letters[elem['first_sticker']],
                    'second_letter': stickers_to_letters[elem['second_sticker']],
                    'commutator': map_commutator(elem['commutator'], stickers_to_letters),
                    "commutator_simplified": elem['commutator_simplified']
                }
                for elem in results
            ]

            return jsonify(results)
    finally:
        connection.close()


@app.route('/letter_pairs/<user_name>', methods=['GET'])
def get_user_letter_pairs(user_name):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = f"""
                SELECT id, first_letter, second_letter, word
                FROM letter_pairs
                WHERE user_name = '{user_name}'
            """
            cursor.execute(query)
            results = cursor.fetchall()
        return jsonify(results)
    finally:
        connection.close()


@app.route('/update_letter_pair/<int:id_>', methods=['PATCH'])
def update_letter_pair(id_: int) -> str:
    data = request.json  # Get JSON body
    new_word = data.get('newWord')
    if not new_word:
        return jsonify({'error': 'Invalid request data'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = f"UPDATE letter_pairs SET word = '{new_word}' WHERE id = {id_}"
            cursor.execute(query)
            connection.commit()
        return jsonify({'message': 'Letter pair updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()


@app.route('/notes/<username>', methods=['GET'])
def get_notes(username):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT id, username, content FROM notes WHERE username = %s"
            cursor.execute(query, (username,))
            notes = cursor.fetchall()
        return jsonify(notes), 200
    finally:
        connection.close()


@app.route('/notes', methods=['POST'])
def add_note():
    data = request.json
    username = data.get('username')
    content = data.get('content', '')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO notes (username, content) VALUES (%s, %s)"
            cursor.execute(query, (username, content))
            connection.commit()
            return jsonify({'message': 'Note added', 'id': cursor.lastrowid}), 201
    finally:
        connection.close()


@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    content = data.get('content', '')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "UPDATE notes SET content = %s WHERE id = %s"
            cursor.execute(query, (content, note_id))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Note not found'}), 404
            return jsonify({'message': 'Note updated'}), 200
    finally:
        connection.close()


@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM notes WHERE id = %s"
            cursor.execute(query, (note_id,))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Note not found'}), 404
            return jsonify({'message': 'Note deleted'}), 200
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
