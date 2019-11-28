import json
import base64
from io import BytesIO
import imghdr

from flask import Flask, request
from flask_restful import Resource, Api
import numpy as np
import face_recognition
from waitress import serve
from pyfiglet import Figlet

from db import FaceDB


TOLERANCE = 0.55
app = Flask(__name__)
api = Api(app)
db = FaceDB()

RC_FORBIDDEN = 403
RC_BAD_REQUEST = 400
RC_NOT_FOUND = 404
RC_CONFLICT = 409
RC_OK = 200


def get_encodings_from_photo(photo_in_bytes):
    photo_array = face_recognition.load_image_file(BytesIO(photo_in_bytes))
    locations = face_recognition.face_locations(photo_array)
    encodings = face_recognition.face_encodings(photo_array, locations)
    return locations, encodings


def recognize_from(face_encoding_lookup, face_encoding):
    return min((
        (name, np.linalg.norm(e - face_encoding))
        for name, e
        in face_encoding_lookup.items()
    ), key=lambda x: x[1])


class RememberFace(Resource):
    def post(self, username):
        face_encodings = db.load_encodings()
        if username in face_encodings:
            return {"error": "name already exists"}, RC_FORBIDDEN

        json_str = request.get_json()

        if json_str is None:
            return {"error": "no json payload!"}, RC_BAD_REQUEST

        try:
            json_object = json.loads(json_str)
        except:
            return {"error": "not valid json"}, RC_BAD_REQUEST

        if json_object.get('img') is None:
            return {"error": "bad payload!"}, RC_BAD_REQUEST

        image_bytes = base64.b64decode(json_object['img'].encode('utf-8'))
        inferred_format = imghdr.what(BytesIO(image_bytes))
        if inferred_format not in ("jpeg", "jpg"):
            return {"error": f"img is not a valid jpg, its a {inferred_format}"}, RC_BAD_REQUEST

        _, encodings = get_encodings_from_photo(image_bytes)
        if len(encodings) == 0:
            return {"error": "no face in photo"}, RC_BAD_REQUEST

        if len(encodings) > 1:
            return {"error": "more then one face in photo"}, RC_BAD_REQUEST

        encoding = encodings[0]
        dist = TOLERANCE
        if face_encodings:
            _, dist = recognize_from(face_encodings, encoding)

        if dist < TOLERANCE:
            return {"error": "face already exist!"}, RC_CONFLICT

        db.remember(username, encoding)
        return {"message": f"{username} added"}, RC_OK


class ListUsers(Resource):
    def get(self):
        return list(db.load_encodings()), RC_OK


class FaceEncoding(Resource):
    def get(self, username):
        face_encodings = db.load_encodings()
        if username not in face_encodings:
            return {"error": "name doesn't exist"}, RC_NOT_FOUND
        return {"name": username, "encoding": list(face_encodings[username])}, RC_OK


class FaceRecognition(Resource):
    def post(self):
        json_str = request.get_json()
        if json_str is None:
            return {"error": "no json payload"}

        try:
            json_object = json.loads(json_str)
        except:
            return {"error": "not valid json"}, RC_BAD_REQUEST

        if json_object.get('img') is None:
            return {"error": "bad payload"}

        image_bytes = base64.b64decode(json_object['img'].encode('utf-8'))
        inferred_format = imghdr.what(BytesIO(image_bytes))
        if inferred_format not in ("jpeg", "jpg"):
            return {"error": f"img is not a valid jpg, its a {inferred_format}"}

        locations, encodings = get_encodings_from_photo(image_bytes)
        if len(encodings) == 0:
            return {"error": "no face in photo"}, RC_NOT_FOUND

        face_encodings = db.load_encodings()
        lst = []
        for l, e in zip(locations, encodings):
            name, dist = recognize_from(face_encodings, e)
            if dist > TOLERANCE:
                lst.append({"name": "unknown", "dist": dist, "location": list(l)})
            else:
                lst.append({"name": name, "dist": dist, "location": list(l)})

        return lst, RC_OK


class ForgetFace(Resource):
    def delete(self, username):
        face_encodings = db.load_encodings()
        if username not in face_encodings:
            return {"error": "name does not exist"}, RC_NOT_FOUND

        db.forget(username)
        return {"message": f"{username} is deleted"}, RC_OK


class CompareFace(Resource):
    def post(self):
        json_str = request.get_json()
        if json_str is None:
            return {"error": "no json payload"}

        try:
            json_object = json.loads(json_str)
        except:
            return {"error": "not valid json"}, RC_BAD_REQUEST

        if (json_object.get('img0') is None) or (json_object.get("img1") is None):
            return {"error": "bad payload"}, 400

        two_encodings = []
        for fn in ["img0", "img1"]:
            image_bytes = base64.b64decode(json_object[fn].encode('utf-8'))
            inferred_format = imghdr.what(BytesIO(image_bytes))
            if inferred_format not in ("jpeg", "jpg"):
                return {"error": f"img is not a valid jpg, its a {inferred_format}"}, RC_BAD_REQUEST

            _, encodings = get_encodings_from_photo(image_bytes)

            if len(encodings) == 0:
                return {"error": "no face in photo"}, RC_NOT_FOUND

            if len(encodings) > 1:
                return {"error": "only one face is allowed in photo"}, RC_FORBIDDEN

            two_encodings.append(encodings[0])

        e0, e1 = two_encodings
        dist = np.linalg.norm(e0-e1)
        return {"dist": dist, "same_indivdual?": str(dist < TOLERANCE)}, RC_OK


api.add_resource(RememberFace, '/face/remember/<string:username>')
api.add_resource(ListUsers, '/face/list-names')
api.add_resource(FaceEncoding, '/face/encoding/<string:username>')
api.add_resource(FaceRecognition, '/face/recognize')
api.add_resource(ForgetFace, '/face/forget/<string:username>')
api.add_resource(CompareFace, '/face/compare')


if __name__ == '__main__':
    print(Figlet().renderText("Restful-Faces"))
    serve(app, port=5001)
