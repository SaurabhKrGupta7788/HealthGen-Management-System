import folium
from path_calculating import all_routes_graphml

coord1 = (23.732369, 92.716494)
coord2 = (23.718835, 92.717611)

paths = all_routes_graphml(coord1, coord2, max_paths=2, epsilon=50)

m = folium.Map(location=coord1, zoom_start=15)

colors = ["blue", "green", "red"]

for idx, p in enumerate(paths, start=1):
    original = [(n["lat"], n["lon"]) for n in p["original_nodes"]]
    refined  = [(n["lat"], n["lon"]) for n in p["refined_nodes"]]

    # Original path → solid line
    #folium.PolyLine(original, color=colors[idx-1], weight=4, tooltip=f"Original Path {idx}").add_to(m)
    
    # Refined path → dashed line
    #folium.PolyLine(refined,icon=folium.Icon(color='red'), color=colors[idx-2], weight=2, tooltip=f"Refined Path {idx}").add_to(m)
    for i, point in enumerate(refined):
        folium.CircleMarker(
            location=point,
            radius=4,  # size of the dot
            color=colors[idx-2],  # border color
            fill=True,
            fill_color=colors[idx-2],
            fill_opacity=0.8,
            tooltip=f"Refined Path {idx} - Point {i+1}"
        ).add_to(m)

    # Markers for start/end
    folium.Marker(original[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(original[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)
    
folium.Marker([23.73100779431399, 92.71792604681629], popup='point_1',icon=folium.Icon(color='blue')).add_to(m)
folium.Circle(
    location=[23.73100779431399, 92.71792604681629],   # center point
    radius=70,            # radius in meters
    color="blue",          # circle border color
    weight=2,              # border thickness
    fill=True,
    fill_color="blue",
    fill_opacity=0.2,
    tooltip="70m radius zone"
).add_to(m)
folium.Circle(
    location=[23.73100779431399, 92.71792604681629],   # center point
    radius=62,            # radius in meters
    color="yellow",          # circle border color
    weight=2,              # border thickness
    fill=True,
    fill_color="yellow",
    fill_opacity=0.2,
    tooltip="70m radius zone"
).add_to(m)
m.save("map_paths.html")
print("✅ Map saved as map_paths.html")
