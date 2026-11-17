import requests

url = "http://127.0.0.1:5000/notes"
r = requests.post(url, json={"text": "Привет"})
print(r.status_code, r.json())

r = requests.post(url, json={"text": ""})
print(r.status_code, r.json())

r = requests.post(url, data={"text": "x"})
print(r.status_code, r.json())