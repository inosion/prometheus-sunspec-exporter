"""
listening-port: <port>
devices: 
- name: smaTriPower:
  ipaddress: 100.64.8.30
  port: 502
  sunspec_address: 126
  sunspec_model_ids:
  - 103
  - 160
  filters:
  - regex: Amps_Phase[ABC]_Aph[ABC]_A
    fn: gt(3276)
    replacement: 0.0
"""

import re

class SunspecDevice:
    def __init__(self, raw):
      self.name =      raw["name"]
      self.ipaddress = raw["ipaddress"]
      self.port      = int(raw["port"])
      self.sunspec_address = int(raw["sunspec_address"])
      self.sunspec_model_ids = raw["sunspec_model_ids"])
      self.filters   = map(FilterConfig,raw['filters'])

class Filter:
    func_regex = r"\b(?P<fn>[^()]+)\((?P<args>[A-Za-z0-9,]+)\)\s*"
    def __init__(self, raw):
        self.replacement = raw["replacement"]
        self.regex = re.compile(raw["regex"])
        fn_def = raw["regex"]
        m = func_regex.match(fn_def)
        func_name = m.group("<fn>")
        parameters = map(str.strip,m.group("<args>").split(","))
        self.fn = FnMapping.filter_fn(eval(f"FnMapping.{func_name}"), replacement, *parameters)

class Config:
    def __init__(self, raw):
        self.test1 = Test1Class(raw['test1'])
        self.test2 = Test2Class(raw['test2'])