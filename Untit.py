import xml.etree.ElementTree as ET
from Node import NodeElement
import csv
import matplotlib.pyplot as plt
from shutil import copyfile
import sys
import networkx as nx

# Input file
file = "/Users/d0m0l9x/Downloads/samplefile.yxmd"   # provide the filename
assert len(file.split('.')) > 1, 'Input file must have an extension'
file_ext = file.split('.')[-1]
assert file_ext == 'xml' or file_ext == 'yxmd', 'Input file must be .xml or .yxmd'
if file_ext == 'yxmd':
    xml = file.split('.')[0] + '.xml'
    copyfile(file, xml)
    tree = ET.parse(xml)
else:
    tree = ET.parse(file)
# print(tree)
# Output file
output_file_name = "/Users/d0m0l9x/Downloads/kpi.csv"  # provide output file name
assert len(output_file_name.split('.')) > 1, 'Output file must have an extension'
output_file_ext = output_file_name.split('.')[-1]
assert output_file_ext == 'csv', 'Output file must be .csv'
graph = nx.DiGraph()
root = tree.getroot()
# print(root)
lst = []
for x in root.iter('Node'):
   # print(x)
    node = NodeElement(x,root)
    lst.append(node.data)
    graph.add_node(node.data['Tool ID'])
    # print(node)
    

for connection in root.iter('Connection'):
    
    connected_tool_id = connection.find('Origin').attrib.get('ToolID')
    # print("orig"+connected_tool_id)
    # print("dest"+connection.find('Destination').attrib.get('ToolID'))
    graph.add_edge(connected_tool_id, connection.find('Destination').attrib.get('ToolID'))

keys = lst[0].keys()
# print(keys)
# # print(graph)
# print(lst)
nx.draw(graph,with_labels = True)
# for node in graph:
#     # Generate a SQL query for each edge that points to this node
#     print("node --"+node)
#     for neighbor in graph[node]:
#         print("neighbour"+neighbor)

# visited = set()

# def dfs(node):
#     visited.add(node)
#     print(node)
#     for neighbor in graph.neighbors(node):
#         if neighbor not in visited:
#             dfs(neighbor)

# dfs(29)
plt.savefig("/Users/d0m0l9x/Downloads/filename.png")
# with open(output_file_name, 'w') as output_file:
#     dict_writer = csv.DictWriter(output_file, keys)
#     dict_writer.writeheader()
#     dict_writer.writerows(lst)


mst=[]
for node in nx.algorithms.topological_sort(graph):
    # print("massa"+node)
    # print(int(node))
    mst = mst + ([d for d in lst if int(d.get('Tool ID')) == int(node)])

# print(mst)

with open(output_file_name, 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys())
    dict_writer.writeheader()
    dict_writer.writerows(mst)



# FY_Extract_Load_bq_1.0.yxmd
# ForestCDP-PRODLoad-NoData.yxmd
