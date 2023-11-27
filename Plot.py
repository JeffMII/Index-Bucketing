from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

def plot():
  df = pd.read_csv("Outputs/Evaluate.csv")
  df.set_index(["Dataset", "Implementation"], inplace=True)

  index = pd.MultiIndex.from_tuples((
    ("SQuAD", "Index Bucketing"), ("SQuAD", "Pandas"), ("SQuAD", "Basic"),
    ("QuAC", "Index Bucketing"), ("QuAC", "Pandas"), ("QuAC", "Basic"),
    ("NewsQA", "Index Bucketing"), ("NewsQA", "Pandas"), ("NewsQA", "Basic")
  ))

  SQuADIBucketTTime = df.loc[index[0], :]
  SQuADPandasTTime = df.loc[index[1], :]
  SQuADBasicTTime = df.loc[index[2], :]

  QuACIBucketTTime = df.loc[index[3], :]
  QuACPandasTTime = df.loc[index[4], :]
  QuACBasicTTime = df.loc[index[5], :]

  NewsQAIBucketTTime = df.loc[index[6], :]
  NewsQABasicTTime = df.loc[index[8], :]

  SQuADLength = len(SQuADBasicTTime["Initial Size(B)"]) - 1
  QuACLength = len(QuACBasicTTime["Initial Size(B)"]) - 1
  NewsQALength = len(NewsQABasicTTime["Initial Size(B)"]) - 1

  titles = (
    "IBucket (SQuAD)",
    "IBucket (QuAC)",
    "IBucket (NewsQA)",
    "Pandas (SQuAD)",
    "Pandas (QuAC)",
    "Pandas (NewsQA)",
    "Basic (SQuAD)",
    "Basic (QuAC)",
    "Basic (NewsQA)",
  )

  fig = make_subplots(rows=3, cols=3, subplot_titles=titles, shared_xaxes=True, shared_yaxes=True)
  fig.add_trace(go.Scatter(
    x=SQuADIBucketTTime["Initial Size(B)"], y=SQuADIBucketTTime["Initial Time(s)"],
  ), row=1, col=1)
  fig.add_trace(go.Scatter(
    x=QuACIBucketTTime["Initial Size(B)"], y=QuACIBucketTTime["Initial Time(s)"],
  ), row=1, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQAIBucketTTime["Initial Size(B)"], y=NewsQAIBucketTTime["Initial Time(s)"],
  ), row=1, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADPandasTTime["Initial Size(B)"], y=SQuADPandasTTime["Initial Time(s)"],
  ), row=2, col=1)
  fig.add_trace(go.Scatter(
    x=QuACPandasTTime["Initial Size(B)"], y=QuACPandasTTime["Initial Time(s)"],
  ), row=2, col=2)
  fig.add_trace(go.Scatter(
    x=(NewsQABasicTTime["Initial Size(B)"][0],), y=(0,), text=("Failed",),
    textposition="middle right", mode="markers+text",
  ), row=2, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADBasicTTime["Initial Size(B)"], y=SQuADBasicTTime["Initial Time(s)"],
    text=(("",)*SQuADLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=1)
  fig.add_trace(go.Scatter(
    x=QuACBasicTTime["Initial Size(B)"], y=QuACBasicTTime["Initial Time(s)"],
    text=(("",)*QuACLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQABasicTTime["Initial Size(B)"], y=NewsQABasicTTime["Initial Time(s)"],
    text=(("",)*NewsQALength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=3)
  fig.update_layout(title={
    "text": "Initial Size(bytes) vs Initial Time(seconds)",
    "x": 0.5,
    "y": 0.05,
    "xanchor": "center",
    "yanchor": "top",
  }, legend={"visible": False})
  fig.show()
  fig.write_image("Outputs/InitialTimeEvaluation.svg")

  fig = make_subplots(rows=3, cols=3, subplot_titles=titles, shared_xaxes=True, shared_yaxes=True)
  fig.add_trace(go.Scatter(
    x=SQuADIBucketTTime["Initial Size(B)"], y=SQuADIBucketTTime["Execution Time(s)"],
  ), row=1, col=1)
  fig.add_trace(go.Scatter(
    x=QuACIBucketTTime["Initial Size(B)"], y=QuACIBucketTTime["Execution Time(s)"],
  ), row=1, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQAIBucketTTime["Initial Size(B)"], y=NewsQAIBucketTTime["Execution Time(s)"],
  ), row=1, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADPandasTTime["Initial Size(B)"], y=SQuADPandasTTime["Execution Time(s)"],
  ), row=2, col=1)
  fig.add_trace(go.Scatter(
    x=QuACPandasTTime["Initial Size(B)"], y=QuACPandasTTime["Execution Time(s)"],
  ), row=2, col=2)
  fig.add_trace(go.Scatter(
    x=(NewsQABasicTTime["Initial Size(B)"][0],), y=(0,), text=("Failed",),
    textposition="middle right", mode="markers+text",
  ), row=2, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADBasicTTime["Initial Size(B)"], y=SQuADBasicTTime["Execution Time(s)"],
    text=(("",)*SQuADLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=1)
  fig.add_trace(go.Scatter(
    x=QuACBasicTTime["Initial Size(B)"], y=QuACBasicTTime["Execution Time(s)"],
    text=(("",)*QuACLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQABasicTTime["Initial Size(B)"], y=NewsQABasicTTime["Execution Time(s)"],
    text=(("",)*NewsQALength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=3)
  fig.update_layout(title={
    "text": "Initial Size(bytes) vs Execution Time(seconds)",
    "x": 0.5,
    "y": 0.05,
    "xanchor": "center",
    "yanchor": "top",
  }, legend={"visible": False})
  fig.show()
  fig.write_image("Outputs/ExecutionTimeEvaluation.svg")

  fig = make_subplots(rows=3, cols=3, subplot_titles=titles, shared_xaxes=True, shared_yaxes=True)
  fig.add_trace(go.Scatter(
    x=SQuADIBucketTTime["Initial Size(B)"], y=SQuADIBucketTTime["Total Time(s)"],
  ), row=1, col=1)
  fig.add_trace(go.Scatter(
    x=QuACIBucketTTime["Initial Size(B)"], y=QuACIBucketTTime["Total Time(s)"],
  ), row=1, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQAIBucketTTime["Initial Size(B)"], y=NewsQAIBucketTTime["Total Time(s)"],
  ), row=1, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADPandasTTime["Initial Size(B)"], y=SQuADPandasTTime["Total Time(s)"],
  ), row=2, col=1)
  fig.add_trace(go.Scatter(
    x=QuACPandasTTime["Initial Size(B)"], y=QuACPandasTTime["Total Time(s)"],
  ), row=2, col=2)
  fig.add_trace(go.Scatter(
    x=(NewsQABasicTTime["Initial Size(B)"][0],), y=(0,), text=("Failed",),
    textposition="middle right", mode="markers+text",
  ), row=2, col=3)
  fig.add_trace(go.Scatter(
    x=SQuADBasicTTime["Initial Size(B)"], y=SQuADBasicTTime["Total Time(s)"],
    text=(("",)*SQuADLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=1)
  fig.add_trace(go.Scatter(
    x=QuACBasicTTime["Initial Size(B)"], y=QuACBasicTTime["Total Time(s)"],
    text=(("",)*QuACLength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=2)
  fig.add_trace(go.Scatter(
    x=NewsQABasicTTime["Initial Size(B)"], y=NewsQABasicTTime["Total Time(s)"],
    text=(("",)*NewsQALength)+("Timeout",), textposition="middle right", mode="markers+text+lines"
  ), row=3, col=3)
  fig.update_layout(title={
    "text": "Initial Size(bytes) vs Total Time(seconds)",
    "x": 0.5,
    "y": 0.05,
    "xanchor": "center",
    "yanchor": "top",
  }, legend={"visible": False})
  fig.show()
  fig.write_image("Outputs/TotalTimeEvaluation.svg")

if __name__ == "__main__": plot()