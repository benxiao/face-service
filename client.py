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


def base64str_from_imagefile(filename):
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} not found")
    inferred_file_format = imghdr.what(filename)
    if inferred_file_format not in ("jpg", "jpeg"):
        raise ValueError(f"image is not a valid jpg file!, its a {inferred_file_format}")
    photo_bytes = open(filename, "rb").read()
    base64encoded = base64.b64encode(photo_bytes)
    return base64encoded.decode("utf-8")


@click.command()
@click.argument('name')
@click.argument('filename')
def remember(name, filename):
    json_str = json.dumps({"img": base64str_from_imagefile(filename)})
    resp = requests.post(API_ENDPOINT + f"/remember/{name}", json=json_str)
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


@click.command()
@click.argument('filename')
def recognize(filename):
    json_str = json.dumps({"img": base64str_from_imagefile(filename)})
    resp = requests.post(API_ENDPOINT + "/recognize", json=json_str)
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


@click.command()
@click.argument('name')
def forget(name):
    resp = requests.delete(API_ENDPOINT+f"/forget/{name}")
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


@click.command()
@click.argument('fn0')
@click.argument('fn1')
def compare(fn0, fn1):
    json_str = json.dumps({"img0":base64str_from_imagefile(fn0), "img1":base64str_from_imagefile(fn1)})
    resp = requests.post(API_ENDPOINT + "/compare", json=json_str)
    print("status_code:", resp.status_code)
    print(resp.content.decode("utf-8"))


cli.add_command(remember)
cli.add_command(recognize)
cli.add_command(list_names)
cli.add_command(encoding)
cli.add_command(forget)
cli.add_command(compare)


if __name__ == '__main__':
    cli()
