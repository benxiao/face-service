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

## Installing 
```shell script
pip install -r requirements.txt
```

## Start server
```shell script
python face_service.py
```

## Docker
```shell script
cd path/face-service
```
```shell script
docker build -t face-service:v0.1 .
```