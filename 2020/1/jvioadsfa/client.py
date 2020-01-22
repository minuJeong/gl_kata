from redis import Redis
import requests


db = Redis("localhost", 6379)
res = requests.get("http://localhost:5000/db/set?key=key_0&value=value_0")
# res = requests.get("http://localhost:5000/db/keys")
# res = requests.get("http://localhost:5000/db/delete?key=key 0")

print(res.text)
print(db.keys())
