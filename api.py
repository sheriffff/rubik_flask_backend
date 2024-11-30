from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
import os

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
    try:
        with (connection.cursor() as cursor):
            query = f"""
            SELECT first_sticker, second_sticker, commutator
            FROM {piece_type}_commutators
            """
            cursor.execute(query)
            results = cursor.fetchall()

            stickers_and_letters = get_user_stickers_and_letters(piece_type, user_name).get_json()
            stickers_to_letters = {elem['sticker']: elem['letter'] for elem in stickers_and_letters}

            results = [
                {
                    'first_letter': stickers_to_letters[elem['first_sticker']],
                    'second_letter': stickers_to_letters[elem['second_sticker']],
                    'commutator': elem['commutator']
                }
                for elem in results
            ]

            return jsonify(results)
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
