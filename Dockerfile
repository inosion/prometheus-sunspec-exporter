FROM python:3.9


ADD requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /src/pysunspec
RUN git clone --recursive https://github.com/sunspec/pysunspec .
RUN python -m unittest discover -v sunspec
RUN python setup.py install

WORKDIR /sunspec_exporter
ADD sunspec_exporter /sunspec_exporter

EXPOSE 9807

ENTRYPOINT [ "python3", "/sunspec_exporter/sunspec_exporter.py" ]