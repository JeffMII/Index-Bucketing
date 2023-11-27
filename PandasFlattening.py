from time import perf_counter
from sys import getsizeof
from typing import Iterable
import pandas as pd
import json

name = "Pandas"
global prevpass
prevpass = None

def flatten(df: pd.DataFrame):
  complete = True
  df = fill_cols(df)
  dcols = get_dcols(df)
  if len(dcols) > 0:
    complete = False
    df = dicts_to_cols(df, dcols)
    df = fill_cols(df)
  lcols = get_lcols(df)
  if len(lcols) > 0:
    complete = False
    icols = get_icols(df)
    df = lists_to_cols(df, icols)
    df = fill_cols(df)
  if complete:
    return df.to_dict(orient="records")
  else: return flatten(df)

def lists_to_cols(df: pd.DataFrame, icols: list[str]):
  if len(df.columns) == len(icols): return df
  try: df = df.set_index(icols).apply(pd.Series.explode).reset_index()
  except:
    df.reset_index()
    try: df = df.apply(pd.Series.explode)
    except Exception as e:
      global prevpass
      currpass = (len(df), len(df.columns))
      if prevpass == currpass: raise e
      else: prevpass = currpass
  return df.reset_index(drop=True)

def dicts_to_cols(df: pd.DataFrame, dcols: list[str]):
  for dcol in dcols:
    ds: list[dict] = list(df[dcol])
    nds: list[dict] = []
    for d in ds:
      nd: dict = {}
      for k, v in d.items():
        nd.update({f"{dcol}.{k}": v})
      nds.append(nd)
    ddf = pd.DataFrame(nds)
    idx = df.columns.get_loc(dcol)
    df = pd.concat([df.iloc[:, :idx], ddf, df.iloc[:, idx + 1:]], axis=1)
    df[ddf.columns] = ddf
  return df

def get_dcols(df: pd.DataFrame):
  isdicts = col_is_type(df, dict)
  dcols = []; cols = list(df.columns)
  for i in range(len(cols)):
    if isdicts[i]: dcols.append(cols[i])
  return dcols

def get_lcols(df: pd.DataFrame):
  islists = col_is_type(df, list)
  lcols = []; cols = list(df.columns)
  for i in range(len(cols)):
    if islists[i]: lcols.append(cols[i])
  return lcols

def get_icols(df: pd.DataFrame):
  islists = col_is_type(df, list)
  cols = list(df.columns)
  icols = []
  for i in range(len(cols)):
    if not islists[i]:
      icols += [cols[i]]
  return icols
  
def fill_cols(df: pd.DataFrame):
  hasdicts = col_has_type(df, dict)
  haslists = col_has_type(df, list)
  cols = list(df.columns)
  if all(hasdicts): return fillna_dicts(df, cols)
  if all(haslists): return fillna_lists(df, cols)
  if any(hasdicts):
    for i in range(len(cols)):
      if hasdicts[i]: df = fillna_dicts(df, [cols[i]])
  if any(haslists):
    for i in range(len(cols)):
      if haslists[i]: df = fillna_lists(df, [cols[i]])
  return df

def fillna_dicts(df: pd.DataFrame, cols: list[str]):
  for col in cols:
    d: dict = df[col].dropna().values[0]
    keys = list(d.keys())
    d = {}
    for key in keys:
      d.update({key: None})
    df[col] = df[col].fillna(json.dumps(d), inplace=False)
    df[col] = df[col].apply(lambda x: (json.loads(x) if type(x) == str else x))
  return df

def fillna_lists(df: pd.DataFrame, cols: list[str]):
  for col in cols:
    length = len(df[col].dropna().values[0])
    df[col] = df[col].fillna(json.dumps([None]*length), inplace=False)
    df[col] = df[col].apply(lambda x: (json.loads(x) if type(x) == str else x))
  return df

def col_is_type(df: pd.DataFrame, t: type):
  return list(df.transform(lambda x: x.apply(type).eq(t)).all())

def col_has_type(df: pd.DataFrame, t: type):
  return list(df.transform(lambda x: x.apply(type).eq(t)).any())

def col_types(df: pd.DataFrame):
  return set(df.transform(lambda x: x.apply(type)))

def example(data: Iterable):
  df = pd.DataFrame(data)
  try: flat = flatten(df)
  except: return {}
  return flat

def test(data: Iterable):
  s1 = getsizeof(json.dumps(data))
  t1 = perf_counter()
  df = pd.DataFrame(data)
  t1 = perf_counter() - t1
  t2 = perf_counter()
  flats = flatten(df)
  t2 = perf_counter() - t2
  s2 = getsizeof(json.dumps(flats))
  t3 = t1 + t2; s3 = s2 - s1
  global prevpass; prevpass = None
  return ((t1, t2, t3), (s1, s2, s3), len(flats))

if __name__ == "__main__":
  with open("Datasets/SQuAD/dev-v2.0.json") as f:
    data = json.load(f)
  version = data["version"]; count = 1
  if "data" in data:
    data = {"version": version, "data": data["data"][:count]}
  else: data = {"version": version, "data": data[:count]}
  data = example(data)
  with open("Outputs/PandasFlattening.json", "w") as f:
    json.dump(data, f, indent=2)

#################################################################################
### Can't handle duplicate indexes (row, column index). Forced to drop duplicates to explode.
### Dropping duplicates didn't work.
