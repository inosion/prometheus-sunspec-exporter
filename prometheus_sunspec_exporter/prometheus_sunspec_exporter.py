#!/usr/bin/env python3

"""prometheus-sunspec-exporter

Usage:
  prometheus-sunspec-exporter.py start [ --port PORT ] [ --sunspec_address SUNSPEC_ADDRESS ] [ --filter METRIC_FILTER... ] --sunspec_ip SUNSPEC_IP --sunspec_port SUNSPEC_PORT --sunspec_model_ids MODEL_IDS
  prometheus-sunspec-exporter.py query [ --sunspec_address SUNSPEC_ADDRESS ] --sunspec_ip SUNSPEC_IP --sunspec_port SUNSPEC_PORT 

Options:
  -h --help                          Show this screen.
  --version                          Show version.
  query                              Dump out current data for analysis; and exit
  start                              Run the prometheus node_exporter
  --port PORT                        Prometheus Client listen port [default: 9807]
  --sunspec_ip SUNSPEC_IP            IP Address of the SunSpec device (Modbus TCP)
  --sunspec_model_ids MODEL_IDS      Comma separated list of the ids of the module you want the data from
  --sunspec_port SUNSPEC_PORT        Modbus port [default: 502]
  --sunspec_address SUNSPEC_ADDRESS  Target modbus device address [default: 1]
  --filter METRICFILTER              Filter the value and alter the reponse. 

Filtering:
  Some devices require filtering of the register values received, due to bugs or features in the hardware.
  This filter support, allows rewriting the exported value, with some basic functions.

  For example, some SMA inverter models return 3276.8 for NaN, for DC Amps, at night time.
  The correct value is 0 when it is not converting energy.

  See https://github.com/inosion/prometheus-sunspec-exporter/blob/main/images/filtering_example_amps_bad.png for an example.

  METRICFILTER is a space separated 3-Tuple, <metric_regex> <function>:<args> <replace_value> 
  
  "Amps_Phase[A-Z]_Aph[A-Z] gt:3276 0"

  Which reads, when the metric matching regex, Amps_Phase[A-Z]_Aph[A-Z] is greater than 3276, set the metric as 0.
  In this example case, the inverter jumps from low 0.4, 0.5 Amps, up to 3276.7 (signed int16 Upper) represented as NaN. 

  The sudden jump, results in out of whack telemetry.

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
import collections

# Internal modules
from util import is_numeric
from util_sunspec import sunspec_test, model_name
from filtering import FnMapping, Filter

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('sunspec_fn_collect_data',
                       'Time spent collecting the data')

# Decorate function with metric.
@REQUEST_TIME.time()
def collect_data(sunspec_client, model_ids, filters):

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
                            
                            final_label = f"{metric_label}{unit_label}"

                            if len(filters) > 0:
                                for x in filters:
                                    if x.regex.match(metric_label):
                                        old_value = value
                                        value = x.fn(old_value)
                                        if value != old_value:
                                            print(f"# !! Filtered {metric_label}. {x.regex} matched. {old_value} -> {value}", flush=True)
                                        
                            print(f"# {final_label}: {value}", flush=True)
                            results[f"{final_label}"] = { "value" : value, "metric_type": metric_type }

    return results


class SunspecCollector(object):
    "The ip, port and target is of the modbus/sunspec device"

    def __init__(self, sunspec_client, model_ids, ip, port, target, filters):
        self.sunspec_client = sunspec_client
        self.model_ids = model_ids
        self.ip = ip
        self.port = port
        self.target = target
        self.filters = filters

    def collect(self):
        # yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        results = collect_data(self.sunspec_client, self.model_ids, self.filters)
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

        filters = []
        if arguments["--filter"] is not None:
            for f in arguments["--filter"]:
                (filter_metric_regex, func_n_params, replacement) = f.split(" ")
                func_name, *parameters = func_n_params.split(":")
                func = FnMapping.filter_fn(eval(f"FnMapping.{func_name}"), replacement, *parameters)
                filters.append(Filter(regex=re.compile(filter_metric_regex),fn=func))

        print("# !!! Enumerating all models, removing from future reads unwanted ones")
        models = sunspec_client.device.models_list.copy()
        for model in models:
            name = model_name(model)
            if str(model.id) not in sunspec_model_ids:
                print(f"#    Removed [{name}]")
                sunspec_client.device.models_list.remove(model)
            else:
                print(f"#  Will collect [{name}]")

        REGISTRY.register(SunspecCollector(
                sunspec_client,
                sunspec_model_ids,
                sunspec_ip,
                sunspec_port,
                sunspec_address,
                filters
            )
        )

        start_http_server(int(arguments["--port"]))

        while True:
            time.sleep(1000)
