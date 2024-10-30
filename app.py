from flask import Flask, render_template, request, jsonify
import ee
import json

app = Flask(__name__)

# Initialize Earth Engine
try:
    ee.Initialize(opt_url='https://earthengine.googleapis.com', project='ee-sabdulazeez44')
except ee.EEException:
    ee.Authenticate()
    ee.Initialize(opt_url='https://earthengine.googleapis.com', project='ee-sabdulazeez44')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_indices', methods=['POST'])
def calculate_indices():
    data = request.json
    start_date = data['start_date']
    end_date = data['end_date']
    cloud_cover = data['cloud_cover']
    min_lat, max_lat = data['min_lat'], data['max_lat']
    min_lon, max_lon = data['min_lon'], data['max_lon']
    scale = data.get('scale', 100)

    roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

    # Set up Earth Engine Collection and Compute Indices
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_cover))
    )

    def add_indices(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
        return image.addBands([ndvi, ndwi])

    collection = collection.map(add_indices)
    ndvi = collection.select("NDVI").median().clip(roi)
    ndwi = collection.select("NDWI").median().clip(roi)

    # Generate Map Tile URLs for NDVI, NDWI, and Satellite Imagery
    ndvi_url = ndvi.getMapId({"min": -1, "max": 1, "palette": ["blue", "white", "green"]})['tile_fetcher'].url_format
    ndwi_url = ndwi.getMapId({"min": -1, "max": 1, "palette": ["cyan", "white", "darkblue"]})['tile_fetcher'].url_format
    satellite_url = collection.median().clip(roi).getMapId({"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000})['tile_fetcher'].url_format

    return jsonify({"ndvi_url": ndvi_url, "ndwi_url": ndwi_url, "satellite_url": satellite_url})

if __name__ == '__main__':
    app.run(debug=True)

