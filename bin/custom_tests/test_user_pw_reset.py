import json
import os
import random
import string

import requests

# url_base = "https://api.oxfordeo.com/"
# url_base = "https://t67fnoy4yqyn6tcigjmbsban2u0qgiss.lambda-url.eu-central-1.on.aws/"
url_base = "http://0.0.0.0:8081/"
authurl = url_base + "auth/token/"


# login
U = os.environ.get("email")
P = os.environ.get("password")
user_email = "<your-email@email.com>"


r = requests.post(authurl, data={"username": U, "password": P})
print("LOGIN")
print(r.status_code)
print(r.text)


token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}


# create a user
print("CRAETE USER")
temp_pass = "".join(
    [random.choice(string.ascii_letters + string.digits) for _ in range(16)]
)
payload = {"email": user_email, "password": temp_pass}
r = requests.post(os.path.join(url_base, "users"), headers=headers, json=payload)

print(r.status_code)
print(r.text)


print("FORGOT_PASS")
payload = {"email": user_email}
r = requests.post(os.path.join(url_base, "auth", "forgot_password"), json=payload)
print(r.status_code)
print(r.text)


# ... go and get the token from your email

TOKEN = "<YOUR-TOKEN>"
NEW_PASS = "<A-NEW-PW>"

print("RESET_PASS")
payload = {"reset_token": TOKEN, "new_password": NEW_PASS, "confirm_password": NEW_PASS}
r = requests.post(os.path.join(url_base, "auth", "reset_password"), json=payload)
print(r.status_code)
print(r.text)


print("LOGIN")
r = requests.post(authurl, data={"username": user_email, "password": NEW_PASS})
print(r.status_code)
print(r.text)
