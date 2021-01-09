FROM python:3.9

RUN apt install -y git curl

WORKDIR /src/pysunspec

RUN pip install pySerial

RUN git clone --recursive https://github.com/sunspec/pysunspec .

RUN python -m unittest discover -v sunspec

RUN python setup.py install

WORKDIR /

