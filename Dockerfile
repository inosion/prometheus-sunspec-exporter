FROM python:3.9-alpine

ADD requirements.txt /
RUN pip install -r /requirements.txt

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh
    
WORKDIR /src/pysunspec
RUN git clone --recursive https://github.com/sunspec/pysunspec .
RUN python -m unittest discover -v sunspec
RUN python setup.py install

WORKDIR /prometheus_sunspec_exporter
ADD prometheus_sunspec_exporter /prometheus_sunspec_exporter

EXPOSE 9807

ENTRYPOINT [ "python3", "/prometheus_sunspec_exporter/prometheus_sunspec_exporter.py" ]