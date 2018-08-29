import requests, config
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": config.goodreads_api, "isbns": "9781632168146"})
print(res.json())
