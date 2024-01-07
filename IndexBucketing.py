from __future__ import annotations
from typing import Iterable, TypeVar
from types import NoneType
from time import perf_counter
from sys import getsizeof
import json

#####################
## Index Bucketing ##
##### Jeff M II #####
#####################
#  See License CCO  #
#   1.0 Universal   #
#####################
## -- Amendment -- ##
########################################
# Permissions and limitations apply to #
# this file, its contents, and the     #
# thesis: Index Bucketing - A Novel    #
# Approach to Manipulating Nested Data #
# Structures and related works         #
########################################

name = "Index Bucketing"

base = TypeVar("base", str, int, float, complex, bool, None)
enum = lambda d: dict(enumerate(d))

class Node:
  kdx: str | int; value: dict[str | int, Node] | base
  level: int; parent: Node
  def __init__(self, kdx: str | int, value: list[Node], level: int, parent: Node):
    self.kdx = kdx; self.value = value
    self.level = level; self.parent = parent
  def ipath(self) -> list[int] | tuple[str]: raise NotImplemented
  def kpath(self) -> list[str] | str: raise NotImplemented
  def ibucket(self, depth: int):
    bucket = {*()}
    for c in self.value.values():
      bucket.update(c.ibucket(depth))
    return list(sorted(bucket))
  def flatten(self, ipath: tuple[int]) -> dict: raise NotImplemented
  
class Leaf(Node):
  value: base
  def ibucket(self, depth: int):
    if self.level == depth:
      return {self.ipath()}
    else: return {}
  def flatten(self, ipath: list[int]):
    return {self.kpath(): self.value}

class Branch(Node):
  value: dict[str | int, Node]

class Root(Node):
  value: dict[str | int, Node]
  def __init__(self, kdx: str | int, value: list[Node], level: int):
    super().__init__(kdx, value, level, None)
  def ipath(self): return []
  def kpath(self): return []
  def flatten(self, bucket: list[tuple[int]]) -> dict:
    raise NotImplemented

class IndexedLeaf(Leaf):
  def ipath(self):
    ipath = self.parent.ipath()
    ipath.append(self.kdx)
    return tuple(ipath)
  def kpath(self):
    return ".".join(self.parent.kpath())
  
class KeyedLeaf(Leaf):
  def ipath(self):
    return tuple(self.parent.ipath())
  def kpath(self):
    kpath = self.parent.kpath()
    kpath.append(self.kdx)
    return ".".join(kpath)

class Indexed:
  def ipath(self):
    ipath = self.parent.ipath()
    ipath.append(self.kdx)
    return ipath
  def kpath(self):
    return self.parent.kpath()
  
class Keyed:
  def ipath(self):
    return self.parent.ipath()
  def kpath(self):
    kpath = self.parent.kpath()
    kpath.append(self.kdx)
    return kpath

class IndexingBranch(Branch):
  def flatten(self, ipath: list[int]):
    idx = ipath[self.level]
    if idx in self.value:
      chd = self.value[idx]
      return chd.flatten(ipath)
    else: return {}
    
class KeyingBranch(Branch):
  def flatten(self, ipath: list[int]):
    flat = {}
    for c in self.value.values():
      flat.update(c.flatten(ipath))
    return flat

class I2Branch(Indexed, IndexingBranch): pass
class IKBranch(Indexed, KeyingBranch): pass
class KIBranch(Keyed, IndexingBranch): pass
class K2Branch(Keyed, KeyingBranch): pass

class IndexingRoot(Root):
  def __init__(self, kdx: str | int, value: list[Node]):
    super().__init__(kdx, value, 0)
  def flatten(self, ibucket: list[tuple[int]], template: dict[str, NoneType]):
    flats = []
    for ipath in ibucket:
      flat = template.copy()
      idx = ipath[self.level]
      child = self.value[idx]
      flat.update(child.flatten(ipath))
      flats.append(flat)
    return flats
  
class KeyingRoot(Root):
  def __init__(self, kdx: str | int, value: list[Node]):
    super().__init__(kdx, value, -1)
  def flatten(self, ibucket: list[tuple[int]], template: dict[str, NoneType]):
    flats = []
    for ipath in ibucket:
      flat = template.copy()
      for c in self.value.values():
        flat.update(c.flatten(ipath))
      flats += [flat]
    return flats
  
class Tree:
  tree: Root; depth: int = 0
  ibucket: list[tuple[int]] = []
  kbucket: set[str] = {*()}
  template: dict[str, NoneType] = {}
  def __init__(self, kdx: str, data: Iterable):
    self.tree = self.root(kdx, data)
    self.ibucket = self.tree.ibucket(self.depth)
    for kpath in self.kbucket:
      self.template[kpath] = None
  def leaf(self, kdx: str | int, data: base, parent: Node):
    leaf: Leaf = None
    if type(kdx) is int:
      leaf = IndexedLeaf(kdx, data, parent.level, parent)
    else: leaf = KeyedLeaf(kdx, data, parent.level, parent)
    self.depth = max(self.depth, leaf.level)
    self.kbucket.add(leaf.kpath())
    return leaf
  def branch(self, kdx: str | int, data: Iterable, parent: Node):
    if len(data) > 0:
      branch: Branch = None
      if type(data) is not dict:
        data = enum(data)
        if type(kdx) is str:
          branch = KIBranch(kdx, {}, parent.level + 1, parent)
        else: branch = I2Branch(kdx, {}, parent.level + 1, parent)
      elif(type(kdx) is str):
        branch = K2Branch(kdx, {}, parent.level, parent)
      else: branch = IKBranch(kdx, {}, parent.level, parent)
      for k, v in data.items():
        if type(v) in (set, list, dict):
          branch.value.update({k: self.branch(k, v, branch)})
        else: branch.value.update({k: self.leaf(k, v, branch)})
      return branch
    else: return self.leaf(kdx, None, parent)
  def root(self, kdx: str | int, data: Iterable):
    root: Root = None
    if type(data) is not dict:
      data = enum(data)
      root = IndexingRoot(kdx, {})
    else: root = KeyingRoot(kdx, {})
    for k, v in data.items():
      if type(v) in (list, dict):
        root.value.update({k: self.branch(k, v, root)})
      else: root.value.update({k: self.leaf(k, v, root)})
    return root
  def flatten(self):
    return self.tree.flatten(self.ibucket, self.template)

def example(data: Iterable):
  tree = Tree(None, data)
  flats = tree.flatten()
  print(len(flats))
  return flats

def test(data: Iterable):
  s1 = getsizeof(json.dumps(data))
  t1 = perf_counter()
  tree = Tree(None, data)
  t1 = perf_counter() - t1
  t2 = perf_counter()
  flats = tree.flatten()
  t2 = perf_counter() - t2
  s2 = getsizeof(json.dumps(flats))
  t3 = t1 + t2; s3 = s2 - s1
  return ((t1, t2, t3), (s1, s2, s3), len(flats))


if __name__ == "__main__":
  with open("Datasets/SQuAD/full-v1.json") as f:
    data = json.load(f)
  if "data" in data:
    data = data["data"]
  data = example({"version": "v1", "data": data[:1]})
  with open("Outputs/IndexBucketing.json", "w") as f:
    json.dump(data, f, indent=2)
