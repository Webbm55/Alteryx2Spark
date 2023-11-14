import xml.etree.ElementTree as ET
from Node import NodeElement
import csv
import matplotlib.pyplot as plt
from shutil import copyfile
import sys
import networkx as nx


# Ask the user for the filename
file = input("Please enter the filename: ")  # User provides the filename
file = "input\\" + file   # Assuming the file is in the 'input' directory

#provide below two names

output_file_name = "output\\outputname.csv"            # output file name
dag_name = "output\\dagname.png"                # Dag Nam


assert len(file.split('.')) > 1, 'Input file must have an extension'
file_ext = file.split('.')[-1]
assert file_ext == 'xml' or file_ext == 'yxmd', 'Input file must be .xml or .yxmd'
if file_ext == 'yxmd':
    xml = file.split('.')[0] + '.xml'
    # copyfile(file, xml)
    tree = ET.parse(xml)
else:
    tree = ET.parse(file)      
assert len(output_file_name.split('.')) > 1, 'Output file must have an extension'
output_file_ext = output_file_name.split('.')[-1]
assert output_file_ext == 'csv', 'Output file must be .csv'
graph = nx.DiGraph()
root = tree.getroot()
print(root)
lst = []
for x in root.iter('Node'):
    node = NodeElement(x,root)
    lst.append(node.data)
    graph.add_node(node.data['Tool ID'])
    

for connection in root.find('Connections').iter('Connection'):
    
    connected_tool_id = connection.find('Origin').attrib.get('ToolID')
    graph.add_edge(connected_tool_id, connection.find('Destination').attrib.get('ToolID'))


mst=[]
for node in nx.algorithms.topological_sort(graph):
    # print("massa"+node)
    # print(int(node))
    mst = mst + ([d for d in lst if int(d.get('Tool ID')) == int(node)])

G = nx.DiGraph()

for connection in root.find('Connections').findall('Connection'):
    origin_tool_id = connection.find('Origin').attrib['ToolID']
    destination_tool_id = connection.find('Destination').attrib['ToolID']
    G.add_edge(origin_tool_id, destination_tool_id)


pos = nx.spring_layout(nx.algorithms.topological_sort(graph), seed=142)
for node_data in lst:
    tool_id = node_data['Tool ID']
    x = node_data.get('x')  
    y = node_data.get('y')
    if x is not None and y is not None:
        pos[tool_id] = (int(x), int(y))
plt.figure(figsize=(60, 20))
nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=10, font_color='black', font_weight='bold', arrowsize=20)

edge_labels = {(u, v): v for u, v in G.edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title("Directed Acyclic Graph (DAG)")

plt.savefig(dag_name, format='png', bbox_inches='tight')

with open(output_file_name, 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, mst[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(mst)

