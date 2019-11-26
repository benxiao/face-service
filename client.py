import requests
import base64
import json
import click
import os


@click.group()
def cli():
    pass


def face_command(cmd, **kwargs):
    filename = kwargs['filename']
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} not found")
    photo_bytes = open(filename, "rb").read()
    base64encoded = base64.b64encode(photo_bytes)
    json_obj = {"img": base64encoded.decode("utf-8")}
    json_str = json.dumps(json_obj)

    if cmd is "remember":
        resp = requests.post(f"http://0.0.0.0:5001/remember/{kwargs['name']}", json=json_str)
    elif cmd is "recognize":
        resp = requests.post(f"http://0.0.0.0:5001/recognize", json=json_str)
    else:
        raise(ValueError("unknown command!"))
    return resp


@click.command()
@click.argument('name')
@click.argument('filename')
def remember(name, filename):
    resp = face_command("remember", name=name, filename=filename)
    print("status_code:", resp.status_code)
    print(resp.content)


@click.command()
@click.argument('filename')
def recognize(filename):
    resp = face_command("recognize", filename=filename)
    print("status_code:", resp.status_code)
    print(resp.content)


cli.add_command(remember)
cli.add_command(recognize)

if __name__ == '__main__':
    cli()
