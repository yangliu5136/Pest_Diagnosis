import requests

url = "https://www.hbatg.com/api/common/common/common/upload/file"


def upload_file(file_name, file_path):
    print('file_name====',file_name,'file_path====',file_path)
    payload = {}
    files = [
        ('file', (file_name,
                  open(file_path, 'rb'),
                  'image/jpg'))
    ]
    headers = {
        'accesstoken': 'eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyQ29udGV4dCI6IntcInVzZXJuYW1lXCI6XCJtMTM1KioqKjUxMzZcIixcIm5pY2tOYW1lXCI6XCLmnajmn7NcIixcImZhY2VcIjpcImh0dHBzOi8vbmYtZmlsZS5oYmF0Zy5jb20vbmZzaG9wL01FTUJFUi8xNzg0NDg5NzY5OTgwNzQzNjgwLy83YTYwMjM0YThiMGM0NDFhYTFiNGNhMTRiYWQ4Njg1Ni5qcGVnXCIsXCJpZFwiOlwiMTc4NDQ4OTc2OTk4MDc0MzY4MFwiLFwibG9uZ1Rlcm1cIjpmYWxzZSxcInJvbGVcIjpcIk1FTUJFUlwifSIsInN1YiI6Im0xMzUqKioqNTEzNiIsImV4cCI6MTc0NDAwNDQ1MH0.tFLd1-44IowpsG2kRfdHyYYhPNNGb29qCPimbQa1N9M'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response.text
