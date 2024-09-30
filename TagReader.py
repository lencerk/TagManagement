import requests
import json

url = "https://api.fmafrica.com:4615/api/Users/login"
headers = {
"accept": "*/*",
"Content-Type": "application/json"
}
data = {
"email": "Naledi@nano.com",
"password": "P@ssword"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    
    # Parse the JSON response to get the token
    response_data = json.loads(response.text)
    token = response_data.get('token')  # Adjust 'token' based on the actual key in the response
    print(token)
