#!/usr/bin/env python3


"""sunspec-prometheus-exporter

Usage:
  sunspec_exporter.py start [ --port PORT ] [ --sunspec_address SUNSPEC_ADDRESS ] --sunspec_ip SUNSPEC_IP --sunspec_port SUNSPEC_PORT --sunspec_model_ids MODEL_IDS 

Options:
  -h --help                          Show this screen.
  --version                          Show version.
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
import time
import re


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('sunspec_collection_seconds',
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
                                point_label = re.sub('[ :\(\)\{\}]', '_', point.point_type.label)
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
            m = None
            if results[x]["metric_type"] == "Counter":
                m = CounterMetricFamily(f"sunspec_{x}", "", labels=[
                                        "ip", "port", "target"])
            if results[x]["metric_type"] == "Gauge":
                m = GaugeMetricFamily(f"sunspec_{x}", "", labels=[
                                        "ip", "port", "target"])
            
            m.add_metric([self.ip, str(self.port),str(self.target)], results[x]["value"])
            yield m

def model_name(model):
    if model.model_type.label:
        label = '%s (%s)' % (model.model_type.label, str(model.id))
    else:
        label = '(%s)' % (str(model.id))
    return label


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    arguments = docopt(__doc__, version='sunspec-prometheus-exporter 1.0')
    print(arguments)

    sunspec_model_ids = arguments["--sunspec_model_ids"].split(",")
    sunspec_ip =      arguments["--sunspec_ip"]
    sunspec_port =    int(arguments["--sunspec_port"])
    sunspec_address = arguments["--sunspec_address"]


    try:
        sunspec_client = client.SunSpecClientDevice(
            client.TCP, sunspec_address, ipaddr=sunspec_ip, ipport=sunspec_port, timeout=10.0
        )

    except client.SunSpecClientError as e:
        print('Error: %s' % (e))
        sys.exit(1)

    # remove the models that don't match what we want
    # this will make reads faster (ignore unnesscessary models)

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
