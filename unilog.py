import os
import requests


def log(data: str):
  print(data)
  try:
    url = "https://UniLog.nekogravitycat.repl.co/log"
    data = {
      "cat": "kemobot",
      "data": data,
      "token": os.environ["unilog_token"]
    }
    requests.post(url, json=data)
  except:
    print("UniLog failed")