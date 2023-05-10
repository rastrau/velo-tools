# velo-tools

Set of useful tools around biking. These have been programmed for a personal use case and as such are a bit 'rough around the edges'.

## [Convert-Veloland-to-KML](https://github.com/rastrau/velo-tools/tree/main/Convert-Veloland-to-KML)
Jupyter Notebook which splits open data from Veloland (schweizmobil.ch) into international, national, regional, and local cycling routes (covering Switzerland) and exports them into four KML files including a more legible (than schweizmobil.ch) visual style. The output KML files can be imported into [map.geo.admin.ch](https://map.geo.admin.ch) using their *Advanced tools* or be visualized in e.g. QGIS.

[![Map viewer with all official cycling
routes](https://github.com/rastrau/velo-tools/blob/main/Convert-Veloland-to-KML/veloland-map-viewer.jpg?raw=true)](https://s.geo.admin.ch/9f31690592)

**More information [here](https://ralphstraumann.ch/portfolio/veloland-karten)**. The datasets have been updated in May 2023. They are based on the [official data](https://opendata.swiss/en/dataset/langsamverkehr-veloland-schweiz) distributed by the Federal Roads Office FEDRO.



## [Download-Strava-bike-trips](https://github.com/rastrau/velo-tools/tree/main/Download-Strava-bike-trips)
Python script which downloads all your recorded cycling trips (type: `Ride`) from Strava and exports them into a GeoPackage (can be visualized e.g. using QGIS).
