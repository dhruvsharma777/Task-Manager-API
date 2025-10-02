import requests
import json

url = "http://127.0.0.1:5000/auth/register"
user_data = {
    "username": "script_user",
    "password": "a_very_good_password"
}


response = requests.post(url, json=user_data)

response.raise_for_status()  

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())

