from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import pydot
from networkx.drawing.nx_pydot import graphviz_layout

app = Flask(__name__)

class Node:
    def __init__(self, name, parent=None, generation=0):
        self.name = name
        self.parent = parent
        self.children = {}
        self.generation = generation

    def add_child(self, node):
        self.children[node.name] = node
        node.generation = self.generation + 1

def bfs(root, name):
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node.name == name:
            return node
        for child in node.children.values():
            queue.append(child)
    return None

def get_ancestry(node):
    ancestry = []
    while node is not None:
        ancestry.append(node.name)
        node = node.parent
    return ancestry[::-1]

def read_data(file_name):
    try:
        df = pd.read_csv(file_name)
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def build_tree(df):
    nodes = {name: Node(name) for name in df['Nama'].unique()}
    nodes['Mula Jadi Nabolon'] = Node('Mula Jadi Nabolon')  # Menambahkan 'Mula Jadi Nabolon' secara manual
    for _, row in df.iterrows():
        nodes[row['Nama']].parent = nodes.get(row['Ayah'])
        if nodes.get(row['Ayah']):
            nodes[row['Ayah']].add_child(nodes[row['Nama']])
    return nodes

def find_name(nodes, name):
    matching_names = [node_name for node_name in nodes if name.lower() in node_name.lower()]
    return matching_names

def draw_graph(df, node=None):
    G = nx.DiGraph()
    edges = [(row['Ayah'], row['Nama']) for _, row in df.iterrows()]
    G.add_edges_from(edges)

    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")

    edge_traces = []
    if node is not None:
        path_edges = [(get_ancestry(node)[i], get_ancestry(node)[i+1]) for i in range(len(get_ancestry(node))-1)]
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_color = "rgb(255,0,0)" if edge in path_edges else "rgb(0,0,0)"
            edge_trace = go.Scatter(
                x=[x0, x1], y=[y0, y1],
                line=dict(width=0.5, color=edge_color),
                hoverinfo='none',
                mode='lines')
            edge_traces.append(edge_trace)
    else:
        edge_color = "rgb(0,0,0)"
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace = go.Scatter(
                x=[x0, x1], y=[y0, y1],
                line=dict(width=0.5, color=edge_color),
                hoverinfo='none',
                mode='lines')
            edge_traces.append(edge_trace)

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{adjacencies[0]}')

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=edge_traces+[node_trace],
                    layout=go.Layout(
                        title='<br>Network graph made with Python',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig.to_html()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        df = read_data('Tarombo.csv')
        if df is None:
            return render_template('index.html', error="Error reading data file.")
        nodes = build_tree(df)
        matching_names = find_name(nodes, name)
        if not matching_names:
            return render_template('index.html', error="No matching names found.")
        node = bfs(nodes['Mula Jadi Nabolon'], matching_names[0])
        if node is not None:
            result = f"{matching_names[0]} adalah generasi ke-{node.generation}"
            result += "\nKeturunan: " + " -> ".join(get_ancestry(node))
        else:
            result = f"{matching_names[0]} tidak ditemukan dalam pohon keluarga"
        graph = draw_graph(df, node)
        return render_template('index.html', result=result, graph=graph)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
