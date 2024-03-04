FROM python:3-alpine
COPY ./requirements.txt /tmp
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt
COPY ./sensor.py /opt/
WORKDIR /opt
ENTRYPOINT python -m aiohttp.web -H 0.0.0.0 -P 9898 sensor:init_func
