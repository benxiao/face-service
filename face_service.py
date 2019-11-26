from flask import Flask, request, jsonify
from waitress import serve
import face_recognition
import base64
import json
import numpy as np
from io import BytesIO
import sys

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


@app.route('/face/remember/<username>', methods=["POST"])
def remember_somebody(username):
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


@app.route('/face/list-names', methods=['GET'])
def list_faces():
    return jsonify(list(face_encodings))


@app.route('/face/encoding/<username>', methods=['GET'])
def get_encoding(username):
    if username not in face_encodings:
        return jsonify({
            "error": "name doesn't exist"
        })
    return jsonify({"name": username, "encoding": list(face_encodings[username])})


@app.route('/face/recognize', methods=['POST'])
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
    # try:
    serve(app, port=5001, host='0.0.0.0')
    # except KeyboardInterrupt:
    #     json_object = {name: list(encodings) for name, encodings in face_encodings.items()}
    #     with open("encoding.json") as fp:
    #         json.dump(json_object, fp)


