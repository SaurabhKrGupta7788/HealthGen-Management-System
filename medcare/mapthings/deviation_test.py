import osmnx as ox
import networkx as nx
import math

# ------------------------------
# Distance calculation
# ------------------------------
def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two (lat, lon) points in meters."""
    R = 6371000  # Earth radius (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ------------------------------
# Path refinement with start/end
# ------------------------------
def refine_path_with_start_end(path_nodes, start_coord, end_coord, epsilon=50):
    """
    Refine path so distance between consecutive nodes is ~epsilon (50m),
    and ensure start/end coordinates are included.
    """
    refined = []

    # Insert artificial start node
    start_node = {
        "node": None,
        "lat": start_coord[0],
        "lon": start_coord[1],
        "distance_from_start_m": 0.0
    }
    refined.append(start_node)

    cumulative_distance = 0.0

    # Interpolate start -> first node
    first = path_nodes[0]
    dist = haversine(start_coord[0], start_coord[1], first["lat"], first["lon"])
    cumulative_distance += dist
    refined.append({
        "node": first["node"],
        "lat": first["lat"],
        "lon": first["lon"],
        "distance_from_start_m": cumulative_distance
    })

    # Interpolate intermediate nodes
    for i in range(len(path_nodes)-1):
        p1, p2 = path_nodes[i], path_nodes[i+1]
        dist = haversine(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
        if dist <= epsilon:
            cumulative_distance += dist
            refined.append({
                "node": p2["node"],
                "lat": p2["lat"],
                "lon": p2["lon"],
                "distance_from_start_m": cumulative_distance
            })
        else:
            dlat, dlon = p2["lat"] - p1["lat"], p2["lon"] - p1["lon"]
            full_steps = int(dist // epsilon)
            step_fraction = epsilon / dist
            for k in range(1, full_steps+1):
                lat = p1["lat"] + dlat * (k * step_fraction)
                lon = p1["lon"] + dlon * (k * step_fraction)
                cumulative_distance = p1["distance_from_start_m"] + k * epsilon
                refined.append({
                    "node": None,
                    "lat": lat,
                    "lon": lon,
                    "distance_from_start_m": cumulative_distance
                })
            cumulative_distance = p1["distance_from_start_m"] + dist
            refined.append({
                "node": p2["node"],
                "lat": p2["lat"],
                "lon": p2["lon"],
                "distance_from_start_m": cumulative_distance
            })

    # Insert artificial end node
    last = path_nodes[-1]
    dist = haversine(last["lat"], last["lon"], end_coord[0], end_coord[1])
    cumulative_distance = last["distance_from_start_m"] + dist
    refined.append({
        "node": None,
        "lat": end_coord[0],
        "lon": end_coord[1],
        "distance_from_start_m": cumulative_distance
    })

    return refined

# ------------------------------
# Path extraction
# ------------------------------
def all_routes_graphml(coord1, coord2, max_paths=3, epsilon=50):
    G_multi = ox.load_graphml(
        r"C:\Users\GANAPATHI\Desktop\NIT\project\ymhhacakthon\medcare\mapthings\mizoram_graph.graphml"
    )

    G = nx.DiGraph()
    G.graph.update(G_multi.graph)
    for n, data in G_multi.nodes(data=True):
        G.add_node(n, **data)
    for u, v, data in G_multi.edges(data=True):
        length = data.get("length", 1)
        if G.has_edge(u, v):
            if length < G[u][v]["length"]:
                G[u][v].update(data)
        else:
            G.add_edge(u, v, **data)

    node1 = ox.distance.nearest_nodes(G, coord1[1], coord1[0])
    node2 = ox.distance.nearest_nodes(G, coord2[1], coord2[0])
    paths_generator = nx.shortest_simple_paths(G, node1, node2, weight="length")

    all_paths = []
    for i, path in enumerate(paths_generator):
        if i >= max_paths: break

        path_nodes, cumulative_distance = [], 0.0
        for j in range(len(path)):
            node = path[j]
            if j > 0:
                edge_len = G[path[j-1]][path[j]]["length"]
                cumulative_distance += edge_len
            path_nodes.append({
                "node": node,
                "lat": G.nodes[node]["y"],
                "lon": G.nodes[node]["x"],
                "distance_from_start_m": cumulative_distance
            })

        refined_nodes = refine_path_with_start_end(path_nodes, coord1, coord2, epsilon)
        all_paths.append({
            "total_distance_km": cumulative_distance / 1000,
            "original_nodes": path_nodes,
            "refined_nodes": refined_nodes
        })
    return all_paths

# ------------------------------
# Deviation check helpers
# ------------------------------
def point_line_distance(lat, lon, p1, p2):
    """Perpendicular distance from (lat, lon) to line segment (p1, p2)."""
    x, y = lon, lat
    x1, y1 = p1["lon"], p1["lat"]
    x2, y2 = p2["lon"], p2["lat"]

    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return haversine(lat, lon, y1, x1)

    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)))
    proj_x, proj_y = x1 + t * dx, y1 + t * dy
    return haversine(lat, lon, proj_y, proj_x)

def is_on_path(live_coord, refined_points, delta=200):
    """Check if live_coord is within delta of the path."""
    lat, lon = live_coord
    start, end = refined_points[0], refined_points[-1]

    # Start/end circle check
    if haversine(lat, lon, start["lat"], start["lon"]) <= delta: return True
    if haversine(lat, lon, end["lat"], end["lon"]) <= delta: return True

    # Path segment check
    for i in range(len(refined_points)-1):
        if point_line_distance(lat, lon, refined_points[i], refined_points[i+1]) <= delta:
            return True
    return False

# ------------------------------
# Example usage
# ------------------------------
coord1 = (23.732369, 92.716494)
coord2 = (23.718835, 92.717611)

paths = all_routes_graphml(coord1, coord2, max_paths=2, epsilon=50)

# Flatten into one list
all_refined = []
for path_id, p in enumerate(paths):
    for node in p["refined_nodes"]:
        node["path_id"] = path_id
        all_refined.append(node)
all_refined.sort(key=lambda x: x["distance_from_start_m"])

# Example deviation test
live_point = (23.73100779431399, 92.71792604681629)

print("Is on path?", is_on_path(live_point, all_refined, delta=62))
