from time import perf_counter
from sys import getsizeof
from typing import Iterable
from collections import defaultdict
import json; import re

name = "Basic"
enum = lambda d: dict(enumerate(d))

def isidxs(s: str):
  if type(s) is int: return True
  return re.search(r"^\d+(\.\d+)*$", s) is not None

def flatten(data):
  result = gatherkeys(data)
  result = gatheridxs(result)
  result = distribute(result)
  result = fill(result)
  return result

def gatheridxs(data: dict | list) -> dict:
  if type(data) in (list, tuple, set):
    data = enum(data)
  if type(data) in (dict, defaultdict):
    result = defaultdict(dict)
    for key, val in data.items():
      if type(val) in (dict, list, tuple, set):
        subresult = gatheridxs(val)
        for skey, sval in subresult.items():
          if (isidxs(key), isidxs(skey)) == (True, False):
            result[str(key)].update({skey: sval})
          elif (isidxs(key), isidxs(skey)) == (False, True):
            result[str(skey)].update({key: sval})
          else: result[f"{key}.{skey}"] = sval
      else: result[key] = val
    return result
  return data

def gatherkeys(data: dict) -> dict:
  if type(data) in (list, tuple, set):
    data = enum(data)
  if type(data) in (dict, defaultdict):
    result = defaultdict(dict)
    for key, val in data.items():
      if type(val) in (dict, list, tuple, set):
        subresult = gatherkeys(val)
        for skey, sval in subresult.items():
          if (isidxs(key), isidxs(skey)) == (True, False):
            result[skey].update({str(key): sval})
          elif (isidxs(key), isidxs(skey)) == (False, True):
            result[key].update({str(skey): sval})
          else: result[f"{key}.{skey}"] = sval
      else: result[key] = val
    return result
  return data

def distribute(data: dict) -> list:
  if type(data) in (dict, defaultdict):
    result = dict(); deleted = 0; depth = 0
    for key in data.keys():
      if isidxs(key):
        depth = max(depth, len(key.split(".")))
    for i in range(len(data)):
      key, val = list(data.items())[i - deleted]
      length = len(key.split("."))
      skip = length < depth or not isidxs(key)
      if not skip:
        result.update({key: val})
        del data[key]; deleted += 1
    for k, v in data.items():
      for key, val in result.items():
        if type(v) not in (dict, defaultdict):
          result[key].update({k: v})
        elif key.startswith(k):
          result[key].update(v)
    return list(result.values())
  return data

def fill(data):
  if type(data) is list:
    template = dict()
    for flat in data:
      if type(flat) in (dict, defaultdict):
        for key in flat.keys():
          template[key] = None
    result = []
    for flat in data:
      if type(flat) in (dict, defaultdict):
        temp = template.copy()
        temp.update(flat)
        result.append(temp)
    return result
  return data

def test(data: Iterable):
  s1 = getsizeof(json.dumps(data))
  t1 = 0
  t2 = perf_counter()
  flats = flatten(data)
  t2 = perf_counter() - t2
  s2 = getsizeof(json.dumps(flats))
  t3 = t1 + t2; s3 = s2 - s1
  return ((t1, t2, t3), (s1, s2, s3), len(flats))

if __name__ == "__main__":
  with open("Datasets/SQuAD/full-v0.2.json") as f:
    data = json.load(f)
  version = "v0.2"; count = 125
  if "data" in data:
    data = {"version": version, "data": data["data"][:count]}
  else: data = {"version": version, "data": data[:count]}
  data = flatten(data)
  with open("Outputs/PythonFlattening.json", "w") as f:
    json.dump(data, f, indent=2)
    