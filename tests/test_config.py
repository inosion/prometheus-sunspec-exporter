
import unittest
from .context import prometheus_sunspec_exporter
import pyyaml

class TestConfig(unittest.TestCase):
    def test_load_config():
        cfg = Config(yaml.safe_load("""
            listening-port: 9807
            devices: 
            - name: smaTriPower:
            ipaddress: 192.168.77.88
            port: 502
            sunspec_address: 126
            sunspec_model_ids:
            - 103
            - 160
            filters:
            - regex: Amps_Phase[ABC]_Aph[ABC]_A
                fn: gt(3276)
                replacement: 0.0
        """)

        assert len(cfg.devices) = 1
        assert cfg.devices[0].name == "smaTriPower" 