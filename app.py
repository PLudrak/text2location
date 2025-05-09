from flask import Flask, request, render_template
import requests

app = Flask(__name__)

OVERPASS_URL = "http://overpass-api.de/api/interpreter"


def build_query(keyword):
    return f"""
    [out:json][timeout:25];
    (
        node["name"~"{keyword}", i];
        node["shop"~"{keyword}", i];
        node["amenity"~"{keyword}", i];
        node["tourism"~"{keyword}", i];
        node["historic"~"{keyword}", i];
    );
    out center
    """


@app.route("/", methods=["GET", "POST"])
def locate():
    description = request.form.get("description", "")
    keywords = extract_keywords(description)  # do zaimplementowania

    locations = []

    for keyword in keywords:
        query = build_query(keyword)
        response = requests.post(OVERPASS_URL, data=query)
        if response.ok:
            elements = response.json().get("elements", [])
            for el in elements:
                lat = el.get("lat") or el.get("center", {}).get("lat")
                lon = el.get("lon") or el.get("center", {}).get("lon")
                if lat and lon:
                    locations.append({"keyword": keyword, "lat": lat, "lon": lon})

    if locations:
        print(f"locations {locations}")
    return render_template("index.html", locations=locations)


def extract_keywords(text):
    # Tymczasowo
    return ["pomnik", "Żabka", "Budynek"]


if __name__ == "__main__":
    app.run(debug=True)
