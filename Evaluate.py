import csv
import sys
import IndexBucketing as ibg
import PandasFlattening as pdf
import PythonFlattening as pyf

algorithms = (
  ibg,
  pdf,
  pyf,
)

datasets = dict(
  QuAC = "Datasets/QuAC/full-v0.2.json",
  SQuAD = "Datasets/SQuAD/full-v2.0.json",
  NewsQA = "Datasets/NewsQA/full-v1.json",
)

ratios = (
  0.001,
  0.002,
  0.003,
  0.005,
  0.008,
  0.013,
  0.021,
  0.034,
  0.055,
  0.089,
  0.144,
  0.233,
  0.377,
  0.610,
  0.987,
  1.000,
)

count = 3
# duration = 60*30
duration = 60*5

import plotly.express as px
from typing import Callable
from math import floor
from tqdm import tqdm
import json; import ctypes
import threading

def run(test: Callable, data):
  class InterruptableThread(threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
      self.result = None
    def run(self):
      stdout = sys.stdout
      stderr = sys.stderr
      try: self.result = test(data)
      except: self.result = None
      sys.stdout = stdout
      sys.stderr = stderr
    def timeout(self):
      if self.is_alive():
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
          ctypes.c_long(self.ident),
          ctypes.py_object(KeyboardInterrupt))
        raise TimeoutError
  it = InterruptableThread()
  it.start(); it.join(duration)
  if it.is_alive(): it.timeout()
  elif it.result: return it.result
  else: raise Exception

def evaluate():
  evals_csv = [[
    "Implementation", "Dataset", "Ratio", "Count",
    "Initial Time(s)", "Execution Time(s)", "Total Time(s)",
    "Initial Size(B)", "Final Size(B)", "Added Size(B)",
    "Records"]]
  evals_json = []
  for algorithm in algorithms:
    for dataset, file in datasets.items():
      with open(file, "r") as f: data = json.load(f)
      if "data" in data: data = data["data"]
      for ratio in ratios:
        dat = data[:floor(len(data) * ratio)]
        if len(dat) < 1: dat = data[:1]
        description = f"{algorithm.name} {dataset} {ratio} {len(dat)}"
        t1s, t2s, t3s = [], [], []
        s1s, s2s, s3s = [], [], []
        rs = []; timedout = False; failed = False
        for _ in tqdm(range(count), desc=description):
          try: result = run(algorithm.test, dat)
          except TimeoutError: timedout = True
          except Exception: failed = True
          if timedout or failed: break
          ((t1, t2, t3), (s1, s2, s3), r) = result
          t1s += [t1]; t2s += [t2]; t3s += [t3]
          s1s += [s1]; s2s += [s2]; s3s += [s3]
          rs += [r]
        if timedout or failed: break
        (t1, s1) = (sum(t1s) / count, sum(s1s) // count)
        (t2, s2) = (sum(t2s) / count, sum(s2s) // count)
        (t3, s3) = (sum(t3s) / count, sum(s3s) // count)
        r = sum(rs) // count
        evals_csv.append([
          algorithm.name, dataset, ratio, len(dat),
          t1, t2, t3, s1, s2, s3, r])
        evals_json.append({
          "Implementation": algorithm.name,
          "Dataset": dataset,
          "Ratio": ratio,
          "Count": len(dat),
          "Initial Time(s)": t1,
          "Execution Time(s)": t2,
          "Total Time(s)": t3,
          "Initial Size(B)": s1,
          "Final Size(B)": s2,
          "Added Size(B)": s3,
          "Records": r
        })

  with open("Outputs/Evaluate.json", "w") as f:
    json.dump(evals_json, f, indent=2)
  json.dump(evals_json, sys.stdout, indent=2)
  with open("Outputs/Evaluate.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerows(evals_csv)
  writer = csv.writer(sys.stdout, delimiter=",")
  writer.writerows(evals_csv)
  fig = px.scatter(
    evals_csv, x="Ratio", y="Total Time(s)", color="Implementation",
  )
  fig.show()

if __name__ == "__main__": evaluate()
