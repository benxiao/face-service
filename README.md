# A Simple Facial Recognition Service

it expose two apis to the client
### remember someone
```shell script
python client.py remember <name> <portrait image in jpg>
```
### recognize someone
```shell script
python client.py recognize <portrait image in jpg>
```
### list all names remembered in our service
```shell script
python client.py list-names
```
### get face encoding for a remembered name
```shell script
python client.py encoding <name>
```
### forget someone
```shell script
python client.py forget <name>
```
## Installing 
```shell script
git clone https://github.com/ageitgey/face_recognition.git
cd face_recognition
docker build -t face-recognition:v1.2.2 . # base image
```
## Docker-Compose
```shell script
cd <path>/restful-face
```
```shell script
docker-compose up -d
```