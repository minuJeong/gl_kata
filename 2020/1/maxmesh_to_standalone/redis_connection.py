from redis import Redis


connection = Redis(host="10.0.75.1", port=6379, db=0)
# connection.set("hello", "randomvalue")
print(connection.hmget("hello"))
