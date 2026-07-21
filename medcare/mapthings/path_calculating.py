#path_calculating.py

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

    # Artificial start
    start_node = {
        "node": None,
        "lat": start_coord[0],
        "lon": start_coord[1],
        "distance_from_start_m": 0.0
    }
    refined.append(start_node)

    cumulative_distance = 0.0

    # Start -> first node
    first = path_nodes[0]
    dist = haversine(start_coord[0], start_coord[1], first["lat"], first["lon"])
    cumulative_distance += dist
    refined.append({
        "node": first["node"],
        "lat": first["lat"],
        "lon": first["lon"],
        "distance_from_start_m": cumulative_distance
    })

    # Intermediate segments
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

    # Artificial end
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

    # Convert MultiDiGraph -> DiGraph
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
        if i >= max_paths:
            break

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

        # ✅ use start/end refinement here
        refined_nodes = refine_path_with_start_end(path_nodes, coord1, coord2, epsilon)

        all_paths.append({
            "total_distance_km": cumulative_distance / 1000,
            "original_nodes": path_nodes,
            "refined_nodes": refined_nodes
        })

    return all_paths


if __name__ == '__main__':
    # ------------------------------
    # Example usage
    # ------------------------------
    coord1 = (23.732369, 92.716494)
    coord2 = (23.718835, 92.717611)

    paths = all_routes_graphml(coord1, coord2, max_paths=2, epsilon=50)

    for idx, p in enumerate(paths, start=1):
        print(f"\nPath {idx}: {p['total_distance_km']:.2f} km")

        print(" Original Path:")
        for n in p["original_nodes"]:
            print(f"  Node {n['node']} ({n['lat']:.5f}, {n['lon']:.5f}) at {n['distance_from_start_m']:.1f} m")

        print(" Refined Path:")
        for n in p['refined_nodes']:
            tag = "Node" if n["node"] else "Interp"
            print(f"  {tag} ({n['lat']:.5f}, {n['lon']:.5f}) at {n['distance_from_start_m']:.1f} m")
