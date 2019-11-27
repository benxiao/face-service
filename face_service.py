from flask import Flask, request, jsonify
from waitress import serve
import face_recognition
import imghdr
import base64
import json
import numpy as np
from io import BytesIO
from pyfiglet import Figlet
from db import FaceDB


tolerance = 0.6
app = Flask(__name__)
db = FaceDB()


def get_encodings_from_photo(photo_in_bytes):
    photo_array = face_recognition.load_image_file(BytesIO(photo_in_bytes))
    locations = face_recognition.face_locations(photo_array)
    return face_recognition.face_encodings(photo_array, locations)


def recognize_from(face_encoding_lookup, face_encoding):
    return min((
        (name, np.linalg.norm(e - face_encoding))
        for name, e
        in face_encoding_lookup.items()
    ), key=lambda x: x[1])


@app.route('/face/remember/<username>', methods=["POST"])
def remember(username):
    face_encodings = db.load_table()
    if username in face_encodings:
        return jsonify({
            "error": "name already exist"
        })

    json_str = request.get_json()
    if json_str is None:
        return jsonify({
            "error": "no json payload!"
        })

    json_object = json.loads(json_str)
    if json_object.get('img') is None:
        return jsonify({
            "error": "bad payload!"
        })

    image_bytes = base64.b64decode(json_object['img'].encode('utf-8'))
    inferred_format = imghdr.what(BytesIO(image_bytes))
    if inferred_format not in ("jpeg", "jpg"):
        return jsonify({"error": f"img is not a valid jpg, its a {inferred_format}"})

    encodings = get_encodings_from_photo(image_bytes)
    if len(encodings) == 0:
        return jsonify({
            "error": "no face in photo"
        })

    if len(encodings) > 1:
        return jsonify({
            "error": "more then one face in photo"
        })

    encoding = encodings[0]
    dist = tolerance
    if face_encodings:
        _, dist = recognize(face_encodings, encoding)
    if dist < tolerance:
        return jsonify({
            "error": "face already exist!"
        })

    db.remember(username, encoding)
    return jsonify({
        "person": username,
        "encoded": True,
        "error": None
    })


@app.route('/face/list-names', methods=['GET'])
def list_people():
    return jsonify(list(db.load_table()))


@app.route('/face/encoding/<username>', methods=['GET'])
def get_encoding(username):
    face_encodings = db.load_table()
    if username not in face_encodings:
        return jsonify({
            "error": "name doesn't exist"
        })
    return jsonify({"name": username, "encoding": list(face_encodings[username])})


@app.route('/face/recognize', methods=['POST'])
def recognize():
    json_str = request.get_json()
    if json_str is None:
        return jsonify({"error": "no json payload"})

    json_object = json.loads(json_str)
    if json_object.get('img') is None:
        return jsonify({"error": "bad payload"})

    image_bytes = base64.b64decode(json_object['img'].encode('utf-8'))
    inferred_format = imghdr.what(BytesIO(image_bytes))
    if inferred_format not in ("jpeg", "jpg"):
        return jsonify({"error": f"img is not a valid jpg, its a {inferred_format}"})

    encodings = get_encodings_from_photo(image_bytes)
    if len(encodings) == 0:
        return jsonify({"error": "no face in photo"})

    if len(encodings) > 1:
        return jsonify({"error": "more than one face in photo"})

    encoding = encodings[0]

    name, dist = recognize_from(db.load_table(), encoding)
    if dist > tolerance:
        return jsonify({"error": "new face!"})

    return {
        "person": name,
        "error": None,
        "dist": dist
    }


if __name__ == '__main__':
    print(Figlet().renderText("FaceService"))
    serve(app, port=5001, host='0.0.0.0')
