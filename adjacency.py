from typing import List, NamedTuple
from pynauty import *
from collections.abc import Iterable
import numpy as np
import json



#def class for jsonencoder for numpy array
class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                    np.int16, np.int32, np.int64, np.uint8,
                    np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                    np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# define function for creating adjacency matrix
def make_adjacency(nodes: int, net: int) -> List[List[int]]:
    """
        *Function for creating adjacency matrix*

        :param nodes: number of nodes
        :type nodes: int
        :param net: number selecting which networks
        :type net: int
        :return: adjacency matrix
    """

    # create flat list of all possible combinations of nodes
    flat_list: List = [0] * (nodes * nodes)

    # create binary vector
    no_of_bits: int = pow(nodes, 2) - nodes
    bin_vec: Iterable[int] = dec_2_bin_vec(net, no_of_bits)

    for x in range(1, nodes, 1):
        low = (1 + x) + (x - 1) * nodes
        high = low + (nodes - 1)

        low_bin = nodes * (x - 1) + 1
        high_bin = low_bin + (nodes - 1)

        flat_list[low - 1:high] = bin_vec[low_bin - 1:high_bin]

    adjacency = [flat_list[i:i+nodes] for i in range(0, len(flat_list), nodes)]
    adjacency = np.array(adjacency)
    adjacency = adjacency.transpose()
    # adjacency = (d for d in adjacency)
    return adjacency


# define function for converting number to binary vector
def dec_2_bin_vec(dec: int or float, bits: int) -> List[int]:
    """
        *Function for converting number to binary vector*

        :param dec: number to be converted
        :type dec: int or float
        :param bits: number of bits
        :type bits: int
        :return: binary vector
    """

    # convert number to binary
    bin_num: str = bin(dec)[2:][::-1]

    # check if length of bin_num is less than bits
    if len(bin_num) < bits:
        # add 0s to bin_num
        bin_num = bin_num.ljust(bits, '0')

        # convert bin_num to list
        bin_num = list(bin_num)
    else:
        # convert bin_num to list
        bin_num = list(bin_num)

    # convert binary vector to list
    bin_vec: Iterable[int] = [int(i) for i in bin_num]

    # return binary vector
    return bin_vec


def create_graph(adjacency: np.ndarray, nodes: int) -> Graph:
    """
        *Function for creating graph*

        :param adjacency: adjacency matrix
        :type adjacency: List[List[int]]
        :return: graph
    """

    # create adjancency dictionary from adjacency
    adj_dict: dict = {}
    for i in range(nodes):
        vertices: List[int] = [i for i, v in enumerate(adjacency[i]) if v == 1]
        adj_dict[i] = vertices

    # create graph
    graph: Graph = Graph(number_of_vertices=nodes,
                         directed=True, adjacency_dict=adj_dict)

    # return graph
    return graph


if __name__ == "__main__":
    print("starting...")
    num_nodes: int = 5
    exp: int = pow(num_nodes, 2) - num_nodes
    possibilities: int = pow(2, exp)
    print("possibilities:", possibilities)
    report: NamedTuple = NamedTuple("report", [("id", str), ("config", np.ndarray), ("graph", Graph)])
    store: List[report] = []
    sorted_store: List[np.ndarray] = []
    temp: List[np.ndarray] = []

    # initalize list for holding data for json file
    data: List = []
    isomorphic_data: List = []

    print("making graphs...")
    for i in range(possibilities + 1):
        matrix = make_adjacency(num_nodes, i)
        g: Graph = create_graph(matrix, num_nodes)
        output = report(id=i, config=matrix, graph=g)
        store.append(output)

    # initialize sorted_store with first graph
    first_report: Graph = store.pop()
    first_output = {first_report.id: first_report.config}
    data.append(first_output)
    isomorphic_data.append({first_report.id: first_report.config})
    sorted_store.append(first_report.graph)
    
    print("sorting graphs...")
    while len(store) > 0:
        print(len(store))
        new: Graph = store.pop()
        result = {new.id: new.config}
        isomorphic_data.append(result)

        # check if new graph is isomorphic to any of the graphs in sorted_store
        for i in range(len(sorted_store)):
            if isomorphic(sorted_store[i], new.graph):
                temp.append(new.graph)
                break
            elif i == len(sorted_store) - 1 and isomorphic(sorted_store[i], new.graph) == False:
                sorted_store.append(new.graph)
                result = {new.id: new.config}
                data.append(result)

    # write data to json file
    file_name: str = f"non-isomorphic-Confs-{num_nodes}-nodes.json"
    file_name2: str = f"isomorphic-Confs-{num_nodes}-nodes.json"
    
    json_data: str = json.dumps(data, cls=NumpyEncoder, indent=4)
    json_data2: str = json.dumps(isomorphic_data, cls=NumpyEncoder, indent=4)
    
    with open(file_name, "w") as f:
        f.write(json_data)
    
    with open(file_name2, "w") as f:
        f.write(json_data2)
    
    # print number of graphs
    print(f"Number of network nodes: {num_nodes}")
    print("\toriginal store:\t", len(store))
    print("\tnon-isomorphic:\t", len(sorted_store))
    print("\tisomorphic:\t", len(temp))
    print("\ttotal:\t\t", len(temp) + len(sorted_store))

    
