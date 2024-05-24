import requests

url = "https://genius.com/Taylor-swift-i-hate-it-here-lyrics"

response = requests.get(url)
print(response.text)
