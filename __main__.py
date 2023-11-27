from os import mkdir
from genericpath import exists
from Evaluate import evaluate
from Plot import plot

if not exists("Outputs"):
  mkdir("Outputs")
evaluate()
plot()
