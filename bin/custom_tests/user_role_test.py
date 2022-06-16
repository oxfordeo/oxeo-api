import json
import os

import requests

url_base = "https://api.oxfordeo.com/"
# url_base = "https://t67fnoy4yqyn6tcigjmbsban2u0qgiss.lambda-url.eu-central-1.on.aws/"
# url_base = "http://0.0.0.0:8081/"

# create a user
# payload = {"email": "me@ox.ca", "password": "mypass"}
# r = requests.post(os.path.join(url_base, "users"), json=payload)

# print(r.status_code)
# print(r.text)

# login
U = os.environ.get("email")
P = os.environ.get("password")

authurl = url_base + "auth/token/"
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)


token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

itemurl = url_base + "users/"
r = requests.get(itemurl, headers=headers)

print(r.status_code)
print(r.text)
