import networkx as nx
import streamlit as st
import random
import matplotlib.pyplot as plt
#to run type in console: python3 -m streamlit run app.py

G = nx.Graph()

#adding nodes (stations)
stations = ['Great Portland Street', 'Tower Hill', 'Wembley Park', 'Notting Hill Gate', 'Baker Street']
G.add_nodes_from(stations)

#adding edges (routes)
routes = [('Great Portland Street', 'Tower Hill'), ('Great Portland Street', 'Wembley Park'), ('Tower Hill', 'Notting Hill Gate'), ('Wembley Park', 'Notting Hill Gate'), ('Notting Hill Gate', 'Baker Street')]
weights = [4, 7, 6, 9, 2]
for i in range(len(routes)):
    G.add_edge(routes[i][0], routes[i][1], weight=weights[i])

print(G.edges(data=True))

#function to find the fastest route using Dijkstra's algorithm (from Further Decision 1)
def find_fastest_route(graph, start, end):
    path = nx.shortest_path(graph, start, end, weight='weight')
    time = nx.shortest_path_length(graph, start, end, weight='weight')
    return path, time

route, time = find_fastest_route(G, 'Great Portland Street', 'Baker Street')
print(f"The fastest route from Great Portland Street to Baker Street is: {route} with a travel time of {time} units.")

#recalculate the fastest route after simulating delay
route, time = find_fastest_route(G, 'Great Portland Street', 'Baker Street')
print(f"After simulating delay, the fastest route from Great Portland Street to Baker Street is: {route} with a travel time of {time} units.")

#route comparison
def compare_routes(graph, start, end):
    all_routes = list(nx.all_simple_paths(graph, start, end))

    results = []
    for route in all_routes:
        time = 0
        for i in range(len(route) - 1):
            edge = (route[i], route[i + 1])
            time += graph[edge[0]][edge[1]]['weight']
        results.append((route, time))
    
    return sorted(results, key=lambda x: x[1])

routes = compare_routes(G, 'Great Portland Street', 'Baker Street')
for r in routes:
    print(r)

#testing the reliability of the routes by simulating random delays
def simulate_random_delays(graph):
    for edge in graph.edges:
        if random.random() < 0.3:  # 30% chance of delay
            delay = random.randint(1, 3)  # Random delay between 1 and 3 units
            graph[edge[0]][edge[1]]['weight'] += delay

st.title("Route Planner")

start = st.selectbox("Select Starting Point", stations)
end = st.selectbox("Select Destination", stations)

# Simulate random delays
edge = st.selectbox("Select edge to disrupt", list(G.edges))
delay = st.slider("Select delay time (units)", 1, 5, 1)

if st.button("Simulate Delay"):
    G[edge[0]][edge[1]]['weight'] += delay

#calualing the route
path = nx.shortest_path(G, start, end, weight='weight')
time = nx.shortest_path_length(G, start, end, weight='weight')

st.write(f"The fastest route from {start} to {end} is: {path} with a travel time of {time} units.")
st.subheader("Insights")

st.write("""
- Disruptions significantly change optimal routes.
- Some routes are consistently more reliable.
- Users should consider both speed and stability.
""")

nx.draw(G, with_labels=True)
st.pyplot(plt)