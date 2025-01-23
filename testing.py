import requests

response = requests.get("http://localhost:8080/health")
print(response.json())

url = "http://localhost:8080/process"

params = {
    "kernel_size": 9,
    "segment_size": 90,
    "brightness_threshold": 100,
}
files = {
    "image1": open("images/image4.png", "rb"),
    "image2": open("app/requirements.txt", "rb"),
}
response = requests.post(url, files=files, data=params)

if response.status_code == 200:
    with open(f"output.png", "wb") as f:
        f.write(response.content)
    print("Collage saved as 'output_collage.png'.")
else:
    print("Error:", response.text)
