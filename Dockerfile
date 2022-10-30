FROM    python:3.9

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y \
    swig \
    libssl-dev \
    dpkg-dev \
    netcat \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal && export C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /code

ADD requirements.txt /code/

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY ./klubok/ /code/klubok/

WORKDIR /code/klubok

CMD ["bash", "start.sh"]
