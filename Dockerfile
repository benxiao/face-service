FROM ubuntu:18.04
MAINTAINER ranxiao

# update install and clean
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# copy source to container
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5001

CMD ["python3", "face_service.py"]