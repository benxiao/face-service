import requests
import base64
import json
import click
import os
import imghdr

# access api-endpoint from os env
try:
    API_ENDPOINT = os.environ["FACE_SERVICE_API_ENDPOINT"]
except KeyError:
    API_ENDPOINT = "http://0.0.0.0:5001/face"
    print('[WARN] environment variable "FACE_SERVICE_API_ENDPOINT" is not set')


@click.group()
def cli():
    pass


def face_command(cmd, **kwargs):
    filename = kwargs['filename']
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} not found")
    inferred_file_format = imghdr.what(filename)
    if inferred_file_format not in ("jpg", "jpeg"):
        raise ValueError(f"image is not a valid jpg file!, its a {inferred_file_format}")
    photo_bytes = open(filename, "rb").read()
    base64encoded = base64.b64encode(photo_bytes)
    json_obj = {"img": base64encoded.decode("utf-8")}
    json_str = json.dumps(json_obj)

    if cmd is "remember":
        resp = requests.post(API_ENDPOINT + f"/remember/{kwargs['name']}", json=json_str)

    elif cmd is "recognize":
        resp = requests.post(API_ENDPOINT + "/recognize", json=json_str)

    else:
        raise (ValueError("unknown command!"))
    return resp


@click.command()
@click.argument('name')
@click.argument('filename')
def remember(name, filename):
    resp = face_command("remember", name=name, filename=filename)
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


@click.command()
@click.argument('filename')
def recognize(filename):
    resp = face_command("recognize", filename=filename)
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


@click.command()
def list_names():
    resp = requests.get(API_ENDPOINT + "/list-names")
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


@click.command()
@click.argument('name')
def encoding(name):
    resp = requests.get(API_ENDPOINT + f"/encoding/{name}")
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


cli.add_command(remember)
cli.add_command(recognize)
cli.add_command(list_names)
cli.add_command(encoding)


if __name__ == '__main__':
    cli()
