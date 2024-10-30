let map;

require(["esri/Map", "esri/views/MapView", "esri/layers/WebTileLayer"], function(Map, MapView, WebTileLayer) {
    map = new Map({ basemap: "satellite" });
    const view = new MapView({
        container: "mapDiv",
        map: map,
        center: [55.25, 25.25],
        zoom: 6
    });
});

function calculateIndices() {
    const data = {
        start_date: document.getElementById("startDate").value,
        end_date: document.getElementById("endDate").value,
        cloud_cover: parseInt(document.getElementById("cloudCover").value),
        min_lat: parseFloat(document.getElementById("minLat").value),
        max_lat: parseFloat(document.getElementById("maxLat").value),
        min_lon: parseFloat(document.getElementById("minLon").value),
        max_lon: parseFloat(document.getElementById("maxLon").value),
        scale: 100
    };

    fetch("/calculate_indices", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        const ndviLayer = new WebTileLayer({ urlTemplate: data.ndvi_url });
        const ndwiLayer = new WebTileLayer({ urlTemplate: data.ndwi_url });
        const satelliteLayer = new WebTileLayer({ urlTemplate: data.satellite_url });

        map.removeAll();
        map.addMany([satelliteLayer, ndviLayer, ndwiLayer]);
    });
}

