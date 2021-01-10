#!/usr/bin/env python3


"""sunspec-prometheus-exporter

Usage:
  sunspec_exporter.py start [ --port PORT ] [ --sunspec_address SUNSPEC_ADDRESS ] --sunspec_ip SUNSPEC_IP --sunspec_port SUNSPEC_PORT --sunspec_model_ids MODEL_IDS 
  sunspec_exporter.py query [ --sunspec_address SUNSPEC_ADDRESS ] --sunspec_ip SUNSPEC_IP --sunspec_port SUNSPEC_PORT 

Options:
  -h --help                          Show this screen.
  --version                          Show version.
  query                              Dump out current data for analysis; and exit
  start                              Run the prometheus node_exporter
  --port PORT                        Prometheus Client listen port [default: 9012]
  --sunspec_ip SUNSPEC_IP            IP Address of the SunSpec device (Modbus TCP)
  --sunspec_model_ids MODEL_IDS      Comma separated list of the ids of the module you want the data from
  --sunspec_port SUNSPEC_PORT        Modbus port [default: 502]
  --sunspec_address SUNSPEC_ADDRESS  Target modbus device address [default: 1]

"""
from docopt import docopt
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import sunspec.core.client as client
import sunspec.core.suns as suns
try:
    import xml.etree.ElementTree as ET
except:
    import elementtree.ElementTree as ET
import sunspec.core.pics as pics
import sunspec.core.util as util
from xml.dom import minidom
import time
import re


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('sunspec_fn_collect_data',
                       'Time spent collecting the data')

# Decorate function with metric.
@REQUEST_TIME.time()
def collect_data(sunspec_client, model_ids):

    if sunspec_client is None:
        print("no sunspec client defined, init() call, ignoring")
        return

    results = { }

    if sunspec_client is not None:
        print( '\nTimestamp: %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))

        sunspec_client.read()

        # requested_models = [ model for model in sunspec_client.device.models_list if str(model.id) in model_ids]

        
        for model in sunspec_client.device.models_list:
                label = model_name(model)
                print("# ---------------------")
                print(f"# model: {label}")
                print("# ---------------------")
                for block in model.blocks:
                    if block.index > 0:
                        index = '%02d_' % (block.index)
                    else:
                        index = ''
                    for point in block.points_list:
                        if point.value is not None:
                            if point.point_type.label:
                                point_label = re.sub('[^a-zA-Z0-9_]', '_', point.point_type.label)
                                metric_label = f"{index}{point_label}_{point.point_type.id}"
                            else:
                                metric_label = f"{index}{point.point_type.id}"
                            
                            units = point.point_type.units
                            unit_label = ""

                            if units is not None:
                                unit_label = f"_{units}"
                                metric_type = "Gauge"
                            else:
                                metric_type = "Counter"
                            
                            if point.point_type.type == suns.SUNS_TYPE_BITFIELD16:
                                value = '%x' % (point.value)
                            elif point.point_type.type == suns.SUNS_TYPE_BITFIELD32:
                                value = '%x' % (point.value)
                            else:
                                value = str(point.value).rstrip('\0')
                            
                            print(f"# {metric_label}{unit_label}: {value}")
                            results[f"{metric_label}{unit_label}"] = { "value" : value, "metric_type": metric_type }

    return results


class SunspecCollector(object):
    "The ip, port and target is of the modbus/sunspec device"

    def __init__(self, sunspec_client, model_ids, ip, port, target):
        self.sunspec_client = sunspec_client
        self.model_ids = model_ids
        self.ip = ip
        self.port = port
        self.target = target

    def collect(self):
        # yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        results = collect_data(self.sunspec_client, self.model_ids)
        for x in results:  # call sunspec here
            the_value = results[x]["value"]
            if is_numeric(the_value):
                m = None
                if results[x]["metric_type"] == "Counter":
                    m = CounterMetricFamily(f"sunspec_{x}", "", labels=[
                                            "ip", "port", "target"])
                if results[x]["metric_type"] == "Gauge":
                    m = GaugeMetricFamily(f"sunspec_{x}", "", labels=[
                                            "ip", "port", "target"])
            
                m.add_metric([self.ip, str(self.port),str(self.target)], the_value)
                yield m
            else:
                print(f"# metric from {self.ip}:{self.port}/{self.target} sunspec_{x} Value: {the_value} is a {type(the_value)}, Ignoring")


# https://stackoverflow.com/a/52676692/2150411
import ast
import numbers
def is_numeric(obj):
    try:
        if isinstance(obj, numbers.Number):
            return True
        elif isinstance(obj, str):
            nodes = list(ast.walk(ast.parse(obj)))[1:]
            if not isinstance(nodes[0], ast.Expr):
                return False
            if not isinstance(nodes[-1], ast.Num):
                return False
            nodes = nodes[1:-1]
            for i in range(len(nodes)):
                #if used + or - in digit :
                if i % 2 == 0:
                    if not isinstance(nodes[i], ast.UnaryOp):
                        return False
                else:
                    if not isinstance(nodes[i], (ast.USub, ast.UAdd)):
                        return False
            return True
        else:
            return False
    except:
        return False

def model_name(model):
    "Model Data Name"
    if model.model_type.label:
        label = '%s (%s)' % (model.model_type.label, str(model.id))
    else:
        label = '(%s)' % (str(model.id))
    return label

def sunspec_test(ip, port, address):

    """
    Original suns options:

        -o: output mode for data (text, xml)
        -x: export model description (slang, xml)
        -t: transport type: tcp or rtu (default: tcp)
        -a: modbus slave address (default: 1)
        -i: ip address to use for modbus tcp (default: localhost)
        -P: port number for modbus tcp (default: 502)
        -p: serial port for modbus rtu (default: /dev/ttyUSB0)
        -b: baud rate for modbus rtu (default: 9600)
        -T: timeout, in seconds (can be fractional, such as 1.5; default: 2.0)
        -r: number of retries attempted for each modbus read
        -m: specify model file
        -M: specify directory containing model files
        -s: run as a test server
        -I: logger id (for sunspec logger xml output)
        -N: logger id namespace (for sunspec logger xml output, defaults to 'mac')
        -l: limit number of registers requested in a single read (max is 125)
        -c: check models for internal consistency then exit
        -v: verbose level (up to -vvvv for most verbose)
        -V: print current release number and exit
    """


    try:
        sd = client.SunSpecClientDevice(client.TCP, address, ipaddr=ip, ipport=port, timeout=10.0)

    except client.SunSpecClientError as e:
        print('Error: %s' % (e))
        sys.exit(1)

    if sd is not None:

        print( '\nTimestamp: %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))

        # read all models in the device
        sd.read()

        root = ET.Element(pics.PICS_ROOT)
        sd.device.to_pics(parent = root, single_repeating = True)
        print(minidom.parseString(ET.tostring(root)).toprettyxml(indent="  "))

        for model in sd.device.models_list:
            if model.model_type.label:
                label = '%s (%s)' % (model.model_type.label, str(model.id))
            else:
                label = '(%s)' % (str(model.id))
            print('\nmodel: %s\n' % (label))
            for block in model.blocks:
                if block.index > 0:
                  index = '%02d:' % (block.index)
                else:
                  index = '   '
                for point in block.points_list:
                    if point.value is not None:
                        if point.point_type.label:
                            label = '   %s%s (%s):' % (index, point.point_type.label, point.point_type.id)
                        else:
                            label = '   %s(%s):' % (index, point.point_type.id)
                        units = point.point_type.units
                        if units is None:
                            units = ''
                        if point.point_type.type == suns.SUNS_TYPE_BITFIELD16:
                            value = '0x%04x' % (point.value)
                        elif point.point_type.type == suns.SUNS_TYPE_BITFIELD32:
                            value = '0x%08x' % (point.value)
                        else:
                            value = str(point.value).rstrip('\0')
                        print('%-40s %20s %-10s' % (label, value, str(units)))




if __name__ == '__main__':
    # Start up the server to expose the metrics.
    arguments = docopt(__doc__, version='sunspec-prometheus-exporter 1.0')
    print(arguments)

    sunspec_ip =        arguments["--sunspec_ip"]
    sunspec_port =      int(arguments["--sunspec_port"])
    sunspec_address =   arguments["--sunspec_address"]
 
    if arguments["query"]:

        sunspec_test(sunspec_ip, sunspec_port, sunspec_address)
        sys.exit(0)

  
    if arguments["start"]:

        sunspec_model_ids = arguments["--sunspec_model_ids"].split(",")
        try:
            sunspec_client = client.SunSpecClientDevice(
                client.TCP, sunspec_address, ipaddr=sunspec_ip, ipport=sunspec_port, timeout=10.0
            )
        except client.SunSpecClientError as e:
            print('Error: %s' % (e))
            sys.exit(1)

        # remove the models that don't match what we want
        # this will make reads faster (ignore unnecessary model data sets)

        print("# !!! Enumerating all models, removing from future reads unwanted ones")
        models = sunspec_client.device.models_list.copy()
        for model in models:
            name = model_name(model)
            if str(model.id) not in sunspec_model_ids:
                print(f"#    Removed [{name}]")
                sunspec_client.device.models_list.remove(model)
            else:
                print(f"#  Keeping [{name}]")


        REGISTRY.register(SunspecCollector(
                sunspec_client,
                sunspec_model_ids,
                sunspec_ip,
                sunspec_port,
                sunspec_address
            )
        )

        start_http_server(int(arguments["--port"]))

        while True:
            time.sleep(1000)
