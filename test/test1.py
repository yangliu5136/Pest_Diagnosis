import requests

url = "http://127.0.0.1:5001/pictureRecognition"

payload = "{\"pictureUrl\": \"https://nf-file.hbatg.com/nfshop/MEMBER/1784489769980743680//5e13e97e47d84a05aa2e5834b46a621a.jpg\"}"
headers = {
   'Content-Type': 'application/json; charset=utf-8'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
