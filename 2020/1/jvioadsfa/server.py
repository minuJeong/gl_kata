from flask import Flask, request
from redis import Redis


SUCCESS = "success"
FAIL = "fail"


app = Flask("flask server")
db = Redis(host="10.10.7.101", port=6379)


@app.route("/")
def index():
    return "hello from flask"


@app.route("/db/set")
def db_set():
    key = request.args.get("key")
    value = request.args.get("value")
    return SUCCESS if db.set(key, value) else FAIL


@app.route("/db/keys")
def db_keys():
    keys = db.keys()
    return ", ".join(list(map(lambda k: k.decode("utf8"), keys)))


@app.route("/db/delete")
def db_delete():
    key = request.args.get("key")
    return SUCCESS if db.delete(key) else FAIL


class Server(object):
    def __init__(self):
        super(Server, self).__init__()
        app.run(debug=True)

Server()
