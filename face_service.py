from flask import Flask, request, jsonify
from waitress import serve
import face_recognition
import base64
import json
import numpy as np
from io import BytesIO

tolerance = 0.6

app = Flask(__name__)

face_encodings = {}  # can be replaced by database


def get_encoding_from_photo(photo_in_bytes):
    photo_array = face_recognition.load_image_file(BytesIO(photo_in_bytes))
    locations = face_recognition.face_locations(photo_array)
    if not locations:
        return None
    return face_recognition.face_encodings(photo_array, locations)[0]


def recognize(face_encoding_lookup, face_encoding):
    return min([
        (name, np.linalg.norm(e - face_encoding))
        for name, e
        in face_encoding_lookup.items()
    ], key=lambda x: x[1])


@app.route('/remember/<username>', methods=["POST"])
def remember_somebody(username):
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

    encoding = get_encoding_from_photo(base64.b64decode(json_object['img'].encode('utf-8')))
    if encoding is None:
        return jsonify({
            "error": "no face in photo"
        })

    dist = tolerance
    if face_encodings:
        _, dist = recognize(face_encodings, encoding)
    if dist < tolerance:
        return jsonify({
            "error": "face already exist!"
        })

    face_encodings[username] = encoding
    return jsonify({
        "person": username,
        "encoded": True,
        "error": None
    })


@app.route('/recognize', methods=['POST'])
def recognize_somebody():
    json_str = request.get_json()
    if json_str is None:
        return jsonify({"error": "no json payload"})
    json_object = json.loads(json_str)
    if json_object.get('img') is None:
        return jsonify({"error": "bad payload"})

    encoding = get_encoding_from_photo(base64.b64decode(json_object['img'].encode('utf-8')))
    if encoding is None:
        return jsonify({"error": "no face in photo"})
    if not face_encodings:
        return jsonify({"error": "face encodings is empty"})

    name, dist = recognize(face_encodings, encoding)
    if dist > tolerance:
        return jsonify({"error": "new face!"})

    return {
        "person": name,
        "error": None,
        "dist": dist
    }


if __name__ == '__main__':
    serve(app, port=5001, host='0.0.0.0')
