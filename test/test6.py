import requests
import json

url = "http://10.0.0.22:5001/pictureRecognition"

payload = json.dumps({
   "pictureUrl": "https://nf-file.hbatg.com/nfshop/MANAGER//9fa3020e98294180aa6e7e620fc248ec.jpg"
})
headers = {
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
