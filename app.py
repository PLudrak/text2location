from flask import Flask, request, render_template
import requests

app = Flask(__name__)

OVERPASS_URL = "http://overpass-api.de/api/interpreter"


def build_query(keyword, lat, lon, radius=500):
    return f"""
    [out:json][timeout:25];
    (
        node["name"~"{keyword}", i](around:{radius},{lat},{lon});
        node["shop"~"{keyword}", i](around:{radius},{lat},{lon});
        node["amenity"~"{keyword}", i](around:{radius},{lat},{lon});
        node["tourism"~"{keyword}", i](around:{radius},{lat},{lon});
        node["historic"~"{keyword}", i](around:{radius},{lat},{lon});
    );
    out center
    """


def get_coordinates_from_city(city_name):
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "addressdetails": 1, "limit": 1}
    headers = {"User-Agent": "text2location-app/1.0 (jakwojcicki97@gmail.com)"}
    response = requests.get(nominatim_url, params=params, headers=headers)
    if response.ok:
        data = response.json()
        if data:
            lat = float(data[0].get("lat", 0))
            lon = float(data[0].get("lon", 0))
            return lat, lon
    return None, None


@app.route("/", methods=["GET", "POST"])
def locate():
    locations = []

    if request.method == "POST":
        description = request.form.get("description", "")
        city = request.form.get("city", "")

        print(f"Recived description {description}")
        print(f"City: {city}")

        if city:
            lat, lon = get_coordinates_from_city(city)
            if lat and lon:
                print(f"Coordinates for {city}")
            else:
                lat, lon = 52.2298, 21.0118
                print(f"Using default coordinates (warsaw): {lat}, {lon}")
        else:
            lat, lon = 52.2298, 21.0118
            print(f"Using default coordinates (warsaw): {lat}, {lon}")
        keywords = extract_keywords(description)
        print(f"Extracted keywords: {keywords}")

        for keyword in keywords:
            query = build_query(keyword, lat, lon)
            response = requests.post(OVERPASS_URL, data=query)
            if response.ok:
                elements = response.json().get("elements", [])
                for el in elements:
                    lat = el.get("lat") or el.get("center", {}).get("lat")
                    lon = el.get("lon") or el.get("center", {}).get("lon")
                    if lat and lon:
                        locations.append({"keyword": keyword, "lat": lat, "lon": lon})

    return render_template("index.html", locations=locations)


def extract_keywords(text):
    # Tymczasowo
    return ["pomnik", "Żabka", "Budynek"]


if __name__ == "__main__":
    app.run(debug=True)
