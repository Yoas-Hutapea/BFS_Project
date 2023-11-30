import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout

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

    if node is not None:
        path_edges = [(get_ancestry(node)[i], get_ancestry(node)[i+1]) for i in range(len(get_ancestry(node))-1)]
        edge_colors = ["red" if edge in path_edges else "black" for edge in G.edges()]
    else:
        edge_colors = "black"

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, arrows=False)
    plt.show()

def main():
    df = read_data('Tarombo.csv')
    if df is None:
        return

    nodes = build_tree(df)

    name = input("Masukkan nama dan marga (contoh: 'Ompu Raja Hutapea'): ")
    matching_names = find_name(nodes, name)
    print("Nama yang cocok:")
    for matching_name in matching_names:
        print(matching_name)

    name = input("Masukkan nama lengkap dari daftar di atas: ")
    node = bfs(nodes['Mula Jadi Nabolon'], name)
    if node is not None:
        print(f"{name} adalah generasi ke-{node.generation}")
        print("Keturunan:", " -> ".join(get_ancestry(node)))
    else:
        print(f"{name} tidak ditemukan dalam pohon keluarga")

    draw_graph(df, node)

if __name__ == "__main__":
    main()