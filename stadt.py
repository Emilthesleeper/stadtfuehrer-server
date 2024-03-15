import flask, json
from flask import render_template
import geopy.distance
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = flask.Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
)

with open("database.json", "r") as f:
    database = json.load(f)

def get_sort_key(object):
    try:
        return float(object["distance"])
    except:
        return 0

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/documentation")
def docs():
    return render_template("docs.html")

@app.route("/datenschutz")
def pp():
    return render_template("privacy policy.html")

@app.route("/api/get_nearest_place/<latitude>/<longitude>")
@limiter.limit("500/day")
def api(latitude: str, longitude: str):
    try:
        latitude=float(latitude)
        longitude=float(longitude)
    except:
        return {
            "status" : "0",
            "message" : "Die App hat fehlerhafte Koordinaten gesendet."
        }
    places = database["places"]
    new_places=[]
    for place in places:
        if place["information"] != "":
            place["distance"] = geopy.distance.geodesic((latitude, longitude), (place["latitude"], place["longitude"])).meters
            new_places.append(place)
    new_places.sort(key=get_sort_key)
    if new_places[0]["distance"] < new_places[0]["min_distance"]:
        return {
            "status" : "1",
            "message" : new_places[0]["information"]
        }
    return {
        "status" : "2",
        "message" : "Zu weit von markierten Stellen entfernt."
    }

@app.errorhandler(429)
def too_many_request_errorhandler(e):
    return {
        "status" : "0",
        "message" : "Sie haben ihr tägliches Kontingent von 500 Anfragen am Tag verbraucht."
    }

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80, debug=True)