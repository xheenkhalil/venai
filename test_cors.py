import requests

url = "https://venai.onrender.com/api/v1/chat/sessions/"
headers = {
    "Origin": "https://venai-puce.vercel.app",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization, content-type, whatever-header, traceparent"
}

print("Sending GET request...")
response = requests.get(url, headers=headers)
print("Body:", response.text)
print(f"Status Code: {response.status_code}")
print("Response Headers:")
for key, value in response.headers.items():
    print(f"{key}: {value}")
