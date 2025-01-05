import flask, json, os
from flask import render_template, session
import geopy.distance
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = flask.Flask(__name__)
app.secret_key="SECRET_KEY"
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
    print("home called by "+get_remote_address())
    return render_template("home.html")

@app.route("/documentation")
def docs():
    print("documentation called by "+get_remote_address())
    return render_template("docs.html")

@app.route("/datenschutz")
def pp():
    print("pp called by "+get_remote_address())
    return render_template("privacy policy.html")

@app.route("/api/reset")
def reset_session():
    print("reset_session called by "+get_remote_address())
    session["key"]=""
    print(get_remote_address()+" 1")
    return {
            "status" : "1",
            "message" : "Success"
        }

@app.route("/api/get_nearest_place/<latitude>/<longitude>")
@limiter.limit("500/day")
def api(latitude: str, longitude: str):
    print("api called by "+get_remote_address())
    try:
        latitude=float(latitude)
        longitude=float(longitude)
    except:
        print(get_remote_address()+" 0")
        return {
            "status" : "0",
            "message" : "Die App hat fehlerhafte Koordinaten gesendet."
        }
    places = database["places"]
    new_places=[]
    for place in places:
        if place["information"] != "":
            place["index"] = places.index(place)
            place["distance"] = geopy.distance.geodesic((latitude, longitude), (place["latitude"], place["longitude"])).meters
            new_places.append(place)
    new_places.sort(key=get_sort_key)
    if new_places[0]["distance"] < new_places[0]["min_distance"]:
        number = new_places[0]["index"]
        value=session.get("key", None)
        if value == None:
            session["key"]=""
            value=session.get("key", None).split(";")
        else:
            value=value.split(";")
        if value[len(value)-1] == "":
            value.pop(len(value)-1)
        if not str(number) in value:
            list=""
            for a in value:
                if len(a) >= 1:
                    list=list+a+";"
            list=list+str(number)+";"
            session["key"]=list
            if new_places[0]["information"].startswith("file/"):
                print(get_remote_address()+" 3")
                return {
                    "status" : "3",
                    "message" : new_places[0]["information"][5:]+".mp3"
                }
            print(get_remote_address()+" 1")
            return {
                "status" : "1",
                "message" : new_places[0]["information"]
            }
        else:
            print(get_remote_address()+" 2")
            return {
                "status" : "2",
                "message" : "Warst schon hier."
            }
    print(get_remote_address()+" 2")
    return {
        "status" : "2",
        "message" : "Zu weit von markierten Stellen entfernt."
    }

@app.errorhandler(429)
def too_many_request_errorhandler(e):
    print("too_many_request_errorhandler called by "+get_remote_address())
    print(get_remote_address()+" 0")
    return {
        "status" : "0",
        "message" : "Sie haben ihr tägliches Kontingent von 500 Anfragen am Tag verbraucht."
    }

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)