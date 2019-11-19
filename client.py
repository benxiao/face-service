import requests
import base64
import json
import click
import os


@click.group()
def cli():
    pass


@click.command()
@click.argument('name')
@click.argument('filename')
def remember(name, filename):
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} not found")
    photo_bytes = open(filename, "rb").read()
    base64encoded = base64.b64encode(photo_bytes)
    json_obj = { "img" : base64encoded.decode("utf-8") }
    json_str = json.dumps(json_obj)
    resp = requests.post(f"http://0.0.0.0:5001/remember/{name}", json=json_str)
    print(resp.status_code)
    print(resp.content)


@click.command()
@click.argument('filename')
def recognize(filename):
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} not found")
    photo_bytes = open(filename, "rb").read()
    base64encoded = base64.b64encode(photo_bytes)
    json_obj = {"img": base64encoded.decode("utf-8")}
    json_str = json.dumps(json_obj)
    resp = requests.post(f"http://0.0.0.0:5001/recognize", json=json_str)
    print(resp.status_code)
    print(resp.content)


cli.add_command(remember)
cli.add_command(recognize)


if __name__ == '__main__':
    cli()
