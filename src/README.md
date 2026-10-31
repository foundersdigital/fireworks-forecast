# Source

- `data/merged_raw.json`: researched listings with sources and evidence notes.
- `scripts/build_data.py`: cleans names, adds notes, geocodes venues -> `data/events_final.json`.
- `scripts/build.py <config> <out>`: injects config, events and postcode districts into `template.html` -> `index.html`.
- Postcode district centroids (`data/districts_named.json`) are derived from ONSPD / OS Open Names (Open Government Licence v3.0).
