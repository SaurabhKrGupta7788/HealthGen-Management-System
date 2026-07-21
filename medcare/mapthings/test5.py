import osmnx as ox
import networkx as nx
import math

def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two (lat, lon) points in meters."""
    R = 6371000  # Earth radius (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def refine_path(path_nodes, epsilon=50):
    """
    Refine path so that distance between consecutive nodes ≤ epsilon (m).
    Splits long segments into nearly equal parts.
    """
    refined = []
    for i in range(len(path_nodes)-1):
        p1 = path_nodes[i]
        p2 = path_nodes[i+1]

        if not refined:
            refined.append(p1)

        # distance between p1 and p2
        dist = haversine(p1["lat"], p1["lon"], p2["lat"], p2["lon"])

        if dist <= epsilon:
            refined.append(p2)
        else:
            steps = math.ceil(dist / epsilon)  # number of equal parts
            step_len = dist / steps            # almost equal length, ≤ epsilon

            for k in range(1, steps+1):
                lat = p1["lat"] + (p2["lat"] - p1["lat"]) * k/steps
                lon = p1["lon"] + (p2["lon"] - p1["lon"]) * k/steps
                refined.append({
                    "node": p2["node"] if k == steps else None,  # keep real node at end
                    "lat": lat,
                    "lon": lon,
                    "distance_from_start_m": p1["distance_from_start_m"] + step_len * k
                })
    return refined

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

        path_nodes = []
        cumulative_distance = 0.0

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

        # refine with epsilon
        refined_nodes = refine_path(path_nodes, epsilon)

        all_paths.append({
            "total_distance_km": cumulative_distance / 1000,
            "original_nodes": path_nodes,
            "refined_nodes": refined_nodes
        })

    return all_paths


# Example usage
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
