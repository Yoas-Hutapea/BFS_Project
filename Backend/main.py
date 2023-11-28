import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = {}

    def add_child(self, node):
        self.children[node.name] = node

def bfs(root, name):
    queue = [(root, 0)]
    while queue:
        node, generation = queue.pop(0)
        if node.name == name:
            return node, generation
        for child in node.children.values():
            queue.append((child, generation + 1))
    return None, None

def get_ancestry(node):
    ancestry = []
    while node is not None:
        ancestry.append(node.name)
        node = node.parent
    return ancestry[::-1]

# Membaca data dari file .csv
df = pd.read_csv('Tarombo.csv')

# Membuat pohon keluarga dari data
nodes = {name: Node(name) for name in df['Nama'].unique()}
for _, row in df.iterrows():
    nodes[row['Nama']].parent = nodes.get(row['Ayah'])
    if nodes.get(row['Ayah']):
        nodes[row['Ayah']].add_child(nodes[row['Nama']])

# Mencari berdasarkan nama
name = input("Masukkan nama dan marga (contoh: 'Ompu Raja Hutapea'): ")
matching_names = [node_name for node_name in nodes if name.lower() in node_name.lower()]
print("Nama yang cocok:")
for matching_name in matching_names:
    print(matching_name)

name = input("Masukkan nama lengkap dari daftar di atas: ")
node, generation = bfs(nodes['Siraja Batak'], name)
if node is not None:
    print(f"{name} adalah generasi ke-{generation}")
    print("Keturunan:", " -> ".join(get_ancestry(node)))
else:
    print(f"{name} tidak ditemukan dalam pohon keluarga")

# Membuat grafik menggunakan networkx
G = nx.DiGraph()
edges = [(row['Ayah'], row['Nama']) for _, row in df.iterrows()]
G.add_edges_from(edges)
plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, arrows=False)
plt.show()