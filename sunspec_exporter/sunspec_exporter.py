#!/usr/bin/env python3


"""sunspec-prometheus-exporter

Usage:
  sunspec_exporter.py start --port <port> --sunspec_ip <target_ip> --sunspec_port <target_port> --sunspec_address <target_address> --sunspec_model_ids <model_ids>

Options:
  -h --help     Show this screen.
  --version     Show version.
  --port <port> Prometheus Client listen port
  --sunspec_ip <target_ip>
  --sunspec_model_ids <model_ids>  Comma separated list of the ids of the module you want the data from
  --sunspec_port <target_port>
  --sunspec_address <target_address>

"""
from docopt import docopt
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import sunspec.core.client as client
import sunspec.core.suns as suns
import time


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('sunspec_collection_seconds',
                       'Time spent collecting the data')


# Decorate function with metric.
@REQUEST_TIME.time()
def collect_data(sunspec_client, model_ids):

    if sunspec_client is None:
        print("no sunspec client defined, init() call, ignoring")
        return

    if sunspec_client is not None:
        print( '\nTimestamp: %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))

        sunspec_client.read()

        for model in sunspec_client.device.models_list:
#            if model.id in model_ids:
                if model.model_type.label:
                    label = '%s (%s)' % (model.model_type.label, str(model.id))
                else:
                    label = '(%s)' % (str(model.id))
                print('# ---------------------)
                print('# model: %s\n' % (label))
                print('# ---------------------)
                for block in model.blocks:
                    if block.index > 0:
                        index = '%02d:' % (block.index)
                    else:
                        index = '   '
                    for point in block.points_list:
                        if point.value is not None:
                            if point.point_type.label:
                                label = '   %s%s (%s):' % (
                                    index, point.point_type.label, point.point_type.id)
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
                            print('# %-40s %20s %-10s' % (label, value, str(units)))

    return {

        "Amps":                             7.800000000000001,
        "Amps_PhaseA":                                 2.6,
      "Amps_PhaseB":                                 2.6,
      "Amps_PhaseC":                                 2.6,
      "Phase_Voltage_AN_PhVphA":                        229.9,
      "Phase_Voltage_BN_PhVphB":           242.20000000000002,
      "Phase_Voltage_CN_PhVphC":           237.20000000000002,
      "Watts_W":                                       1840.0,
      "Hz_Hz":                                          49.96,
      "VA_VA":                                         1840.0,
      "VAr_VAr": -10.0,
      "WattHours_WH":                              14713730.0,
      "Cabinet_Temperature_TmpCab":                        42,
      "Operating_State_St":                                 4,
      "Event1_Evt1":                               0x00000000
    }


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
            print(x)
            c = CounterMetricFamily(f"sunspec_{x}", 'some help', labels=[
                                    "ip", "port", "target"])
            c.add_metric([self.ip, str(self.port),
                          str(self.target)], results[x])
            yield c


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
