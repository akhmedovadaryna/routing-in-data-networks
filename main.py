import networkx as nx

import matplotlib.pyplot as plt
import random

# params
duplex = 0
half_duplex = 1
satellite = 2
virtual_chanel = 0
datagram = 1

matrix = []
node_n_reg1 = 7
node_n_reg2 = 7
node_n_reg3 = 7
node_n_reg4 = 7
node_n = node_n_reg1 + node_n_reg2 + node_n_reg3 + node_n_reg4
#node_n = 8
av_deg = 2.5
inf_packet_size = 1000
service_packet_size = 100
arr_weight = [1, 2, 3, 5, 7, 8, 12, 15, 21, 26, 27, 28, 30]
colors = ['red', 'green', 'blue']
n_satellite = 0
# channel capacity = def_capacity / weight
def_capacity = 100000000  # 100 Mbit/s
error_on = True
routing_tab = []
sending_tab = []


def average_deg(m, n):
    s = 0
    for i in range(n):
        s += sum(m[i])

    return float(s) / n


def generate_adjacency_matrix():
    reg1 = generate_adjacency_matrix_region(node_n_reg1)
    reg2 = generate_adjacency_matrix_region(node_n_reg2)
    reg3 = generate_adjacency_matrix_region(node_n_reg3)
    reg4 = generate_adjacency_matrix_region(node_n_reg4)

    reg1_zero = []
    for i in range(node_n_reg1):
        reg1_zero.append(0)

    reg2_zero = []
    for i in range(node_n_reg2):
        reg2_zero.append(0)

    reg3_zero = []
    for i in range(node_n_reg3):
        reg3_zero.append(0)

    reg4_zero = []
    for i in range(node_n_reg4):
        reg4_zero.append(0)

    for i in range(node_n_reg1):
        matrix.append(reg1[i] + reg2_zero + reg3_zero + reg4_zero)

    for i in range(node_n_reg2):
        matrix.append(reg1_zero + reg2[i] + reg3_zero + reg4_zero)

    for i in range(node_n_reg3):
        matrix.append(reg1_zero + reg2_zero + reg3[i] + reg4_zero)

    for i in range(node_n_reg4):
        matrix.append(reg1_zero + reg2_zero + reg3_zero + reg4[i])

    nodes = []
    nodes.append(random.randint(0, node_n_reg1-1))
    nodes.append(random.randint(node_n_reg1, node_n_reg1 + node_n_reg2 - 1))
    nodes.append(random.randint(node_n_reg1 + node_n_reg2, node_n_reg1 + node_n_reg2 + node_n_reg3 - 1))
    nodes.append(random.randint(node_n_reg1 + node_n_reg2 + node_n_reg3, node_n_reg1 + node_n_reg2 + node_n_reg3 + node_n_reg4 - 1))

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            matrix[nodes[i]][nodes[j]] = 2
            matrix[nodes[j]][nodes[i]] = 2


def generate_adjacency_matrix_region(n):
    reg_matrix = []
    for i in range(n):
        reg_matrix.append([])
        for j in range(n):
            reg_matrix[i].append(0)

    for i in range(n - 1):
        j = random.randint(i + 1, n - 1)
        reg_matrix[i][j] = 1
        reg_matrix[j][i] = reg_matrix[i][j]

    deg = average_deg(reg_matrix, n)
    while deg < av_deg:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
        if i != j and reg_matrix[i][j] == 0:
            reg_matrix[i][j] = 1
            reg_matrix[j][i] = 1
        deg = average_deg(reg_matrix, n)

    return reg_matrix


def create_network():
    global n_satellite
    G = nx.Graph()
    for i in range(node_n):
        for j in range(i, node_n):
            if i != j:
                if matrix[i][j] > 0:

                    edge_type = random.randint(0, 1)
                    if matrix[i][j] != 2:
                        w = arr_weight[random.randint(0, 10)]
                    else:
                        w = arr_weight[0]
                        if n_satellite < 2:
                            edge_type = 2
                            if edge_type == 2:
                                n_satellite += 1
                        else:
                            edge_type = random.randint(0, 1)
                    G.add_edge(i, j, weight=w, type=edge_type, err=random.uniform(0, 0.05),
                               capacity=def_capacity / (w * (edge_type + 1)))
    return G


def print_network(G):
    edge_colors = []
    for edge in G.edges():
        edge_colors.append(colors[G[edge[0]][edge[1]]['type']])
    # pos = nx.circular_layout(G)
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, edge_color=edge_colors, width=1.5, with_labels=True, node_color="green", node_size=300)
    # nx.draw_circular(G, edge_color=edge_colors, width=1.5, with_labels=True, node_color="green", node_size=300)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    # for label in edge_labels:
    #    edge_labels[label] = str(G[label[0]][label[1]]['weight']) + " (" \
    #                         + str(round(float(edge_labels[label]) * 100 / def_capacity, 2)) + " Mbit/s)"
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.4, font_size=8)
    plt.savefig("edge_colormap.png")
    plt.show()


def menu():
    print "NETWORK Params:"
    print "\tNode n :", node_n
    print "\tAverage degree :", av_deg
    print "\tWeights :", arr_weight
    print "\n\nMenu"
    print "1. Print Graph"
    print "2. Print routes table"
    print "3. Testing"
    print "0. Exit"
    key = input("Enter: ")
    if key == 0:
        exit()
    elif key == 1:
        print_network(G)
        print "\n\n\n"
    elif key == 2:
        generate_routes()
        print_routing()
        print "\n\n\n"
    elif key == 3:
        testing()
        print "\n\n\n"
    else:
        print "\n\n\n"
        print "Wrong command"


def m_max(dict, node_stack):
    max_f = 0
    indexes = []
    for i in dict:
        if i not in node_stack:
            if dict[i] > max_f:
                max_f = dict[i]
                indexes = [i]
            elif dict[i] == max_f:
                indexes.append(i)

    return max_f, indexes


def routes(type, source, sink):
    if type == 0:
        distance = nx.eccentricity(G, source)
    else:
        distance = node_n
    lavina_routes = []
    prev_routes = [[source]]
    res_route = []
    arr_node = [source]
    n_packet = 0
    # distance = 5
    for l in range(distance):
        buf_arr_source = []
        b = []
        for n in range(len(arr_node)):
            buf = []
            for i in G[arr_node[n]]:
                if i not in prev_routes[n]:
                    n_packet += 1
                    if i != sink:
                        buf.append(prev_routes[n] + [i])
                        buf_arr_source.append(i)
                    else:
                        res_route.append(prev_routes[n] + [i])
            b.append(buf)
        prev_routes = []
        for i in b:
            for j in i:
                prev_routes.append(j)
        lavina_routes = prev_routes
        arr_node = buf_arr_source

    return res_route, n_packet


def print_routing():
    print 'Source\t', 'Sink\t', 'Min weight\t\t\t', 'Route with min weight\t\t\t\t\t\t', 'Min distance (nodes)\t', \
        'Route with min distance\t'

    for row in routing_tab:
        str_min_weight = ""
        str_min_distance = ""
        str_min_distance_flow = str(row['min_dist_flow'])
        str_max_flow = str(row['max_flow'])
        for i in row['min_weight_route']:
            if str_min_weight != "":
                str_min_weight += "->"
            str_min_weight += str(i)
        for i in range(40 - len(str_min_weight)):
            str_min_weight += " "
        for i in row['min_distance_route']:
            if str_min_distance != "":
                str_min_distance += "->"
            str_min_distance += str(i)
        for i in range(20 - len(str_min_distance_flow)):
            str_min_distance_flow += " "

        for i in range(15 - len(str_max_flow)):
            str_max_flow += " "

        print row['source'], "\t\t", \
            row['sink'], "\t\t", \
            str_max_flow, "\t", \
            str_min_weight, "\t", \
            str_min_distance_flow, "\t", \
            str_min_distance
    raw_input("Press enter...")


def generate_routes():
    for source in G.nodes():
        for sink in G.nodes():
            if source != sink:
                route, n = routes(0, source, sink)
                max_flow = 0
                index_max = 0
                min_route_weight = []
                for r in route:
                    prev_i = 0
                    weight = 0
                    for i in range(1, len(r)):
                        if weight < G[r[prev_i]][r[i]]['weight'] or weight == 0:
                            weight = G[r[prev_i]][r[i]]['weight']
                        prev_i = i
                    min_route_weight.append(weight)
                index_min = 0
                min_weight = 0
                for i in range(len(min_route_weight)):
                    if min_weight > min_route_weight[i] or min_weight == 0:
                        min_weight = min_route_weight[i]
                        index_min = i

                index_min_len = 0
                min_len = 0
                for r in range(len(route)):
                    length = len(route[r])
                    if min_len > length or min_len == 0:
                        min_len = length
                        index_min_len = r

                routing_tab.append({'source': source,
                                    'sink': sink,
                                    'max_flow': min_weight,
                                    'min_weight_route': route[index_min],
                                    'min_dist_flow': min_len,
                                    'min_distance_route': route[index_min_len]})


def send_massage(type, source, sink, size):
    # if (source, sink) in G.edges() or (sink, source) in G.edges():
    # size in byte
    route = []
    flow = 0
    err = 0
    if type == virtual_chanel:
        route, n_packet = routes(type, source, sink)
        min_route_cap = []
        for r in route:
            prev_i = 0
            min_cap = 0
            for i in range(1, len(r)):
                if min_cap > G[r[prev_i]][r[i]]['capacity'] or min_cap == 0:
                    min_cap = G[r[prev_i]][r[i]]['capacity']
                prev_i = i
            min_route_cap.append(min_cap)
        index_min = 0
        min_cap = 0
        for i in range(len(min_route_cap)):
            if min_cap < min_route_cap[i] or min_cap == 0:
                min_cap = min_route_cap[i]
                index_min = i
        n_inf_packet = size / inf_packet_size
        if size % inf_packet_size != 0:
            n_inf_packet += 1

        n_inf_packet *= len(route[index_min]) - 1

        if error_on == True:
            err = 0
            for i in range(n_inf_packet):
                a = route[index_min][0]
                for b in range(1, len(route[index_min])):

                    x = random.random()
                    if G[a][route[index_min][b]]['err'] > x:
                        err += 1
                    a = route[index_min][b]
        n_service_packet = n_inf_packet + n_packet + 3 * len(route[index_min]) - 1
        if error_on == True:
            for i in range(n_service_packet):
                a = route[index_min][0]
                for b in range(1, len(route[index_min])):

                    x = random.random()
                    if G[a][route[index_min][b]]['err'] > x:
                        err += 1
                    a = route[index_min][b]

        route = route[index_min]
        size_inf_part = n_inf_packet * inf_packet_size
        size_service_part = n_service_packet * service_packet_size
        time = round((float(size_inf_part + size_service_part) / min_cap) * 1000, 2)

    else:
        arr_route = []
        queue_route = []
        arr_route, n_packet = routes(type, source, sink)
        min_route_cap = []
        for r in arr_route:
            prev_i = 0
            min_cap = 0
            for i in range(1, len(r)):
                if min_cap > G[r[prev_i]][r[i]]['capacity'] or min_cap == 0:
                    min_cap = G[r[prev_i]][r[i]]['capacity']
                prev_i = i
            min_route_cap.append(min_cap)
        index_min = 0
        min_cap = 0
        arr = {}
        for i in range(len(min_route_cap)):
            arr[min_route_cap[i]] = arr_route[i]
        arr = sorted(arr.items())

        routes_time_inf = []
        routes_time_service = []
        for i in arr:
            routes_time_inf.append(round((float(inf_packet_size) / i[0]) * 1000, 2))
            routes_time_service.append(round((float(service_packet_size) / i[0]) * 1000, 2))
            queue_route.append(0)
        n_inf_packet = size / inf_packet_size
        if size % inf_packet_size != 0:
            n_inf_packet += 1
        time = 0
        sum_n_packet = 0
        size_inf_part = 0
        size_service_part = 0
        add_inf = 0
        add_service = 0

        for packet in range(n_inf_packet):
            delay = []
            for i in range(len(queue_route)):
                delay.append((queue_route[i] + 1) * routes_time_inf[i])
            index_min_delay = len(delay) - 1
            min_delay = delay[index_min_delay]
            for i in range(len(delay)):
                if delay[i] <= min_delay:
                    min_delay = delay[i]
                    index_min_delay = i

            r = arr[index_min_delay][1]
            a = r[0]
            if error_on == True:
                for b in range(1, len(r)):
                    x1 = random.random()
                    x2 = random.random()

                    if G[a][r[b]]['err'] > x1:
                        err += 1
                    if G[a][r[b]]['err'] > x2:
                        err += 1
                    a = r[b]

            queue_route[index_min_delay] += 1
            k = (len(arr_route[index_min_delay]) - 1)
            sum_n_packet += k
            size_inf_part += inf_packet_size * k
            size_service_part += service_packet_size * k
            for i in range(len(delay)):
                delay[i] -= routes_time_inf[i]
            time = max(delay)

        n_inf_packet = sum_n_packet + add_inf
        n_service_packet = sum_n_packet + add_service



    sending_tab.append({'type': type,
                        'source': source,
                        'sink': sink,
                        'n_inf_packet': n_inf_packet,
                        'n_service_packet': n_service_packet,
                        'size_inf_part': size_inf_part,
                        'size_service_part': size_service_part,
                        'time': time,
                        'route': route,
                        'err': err})


def print_sending_tab():
    global sending_tab
    print 'Type\t', 'Source\t', 'Sink\t', 'Amount information packages\t', 'Amount service packages\t', \
        'Packages with error\t', 'Size information part\t', 'Size service part\t', 'Time\t\t', 'Route'
    for row in sending_tab:
        str_type = ""
        if row['type'] == 0:
            str_type = "vc"
        else:
            str_type = "dg"
        str_n_inf_packet = str(row['n_inf_packet'])
        str_n_service_packet = str(row['n_service_packet'])
        str_size_inf_part = str(row['size_inf_part'])
        str_size_service_part = str(row['size_service_part'])
        str_time = str(row['time'])
        str_route = ""
        str_err = str(row['err'])
        for i in range(len('Packages with error') - len(str_err)):
            str_err += " "
        for i in range(len('Amount information packages') - len(str_n_inf_packet)):
            str_n_inf_packet += " "
        for i in range(len('Amount service packages') - len(str_n_service_packet)):
            str_n_service_packet += " "
        for i in range(len('Size information part') - len(str_size_inf_part)):
            str_size_inf_part += " "
        for i in range(len('Size service part') - len(str_size_service_part)):
            str_size_service_part += " "
        for i in range(len('Time    ') - len(str_time)):
            str_time += " "
        for i in row['route']:
            if str_route != "":
                str_route += "->"
            str_route += str(i)
        print str_type, "\t\t", \
            row['source'], "\t\t", \
            row['sink'], "\t\t", \
            str_n_inf_packet, \
            str_n_service_packet, \
            str_err, \
            str_size_inf_part, "\t", \
            str_size_service_part, "\t", \
            str_time, "\t", \
            str_route
    raw_input("Press enter...")

    sending_tab = []


def testing():
    """
        virtual channel and datagram
    """
    print "virtual channel and datagram "
    for i in range(10):
        while True:
            n1 = random.randint(0, node_n - 1)
            n2 = random.randint(0, node_n - 1)
            if n1 != n2:
                break
        send_massage(virtual_chanel, n1, n2, 700000)
        send_massage(datagram, n1, n2, 700000)
    print_sending_tab()

    """
            different size
    """
    print "different size "

    for i in range(10):
        size = random.randint(1, 700000)
        print size
        while True:
            n1 = random.randint(0, node_n - 1)
            n2 = random.randint(0, node_n - 1)
            if n1 != n2:
                break
        send_massage(virtual_chanel, n1, n2, size)
        send_massage(datagram, n1, n2, size)
    print_sending_tab()

    """
                different size of packet
        """
    print "different size of packet "

    global inf_packet_size
    while True:
        n1 = random.randint(0, node_n - 1)
        n2 = random.randint(0, node_n - 1)
        if n1 != n2:
            break
    for i in range(10):
        inf_packet_size += 1000
        send_massage(virtual_chanel, n1, n2, 700000)
        send_massage(datagram, n1, n2, 700000)
    inf_packet_size = 1000
    print_sending_tab()


if __name__ == '__main__':
    generate_adjacency_matrix()
    G = create_network()
    av_deg = (float(sum(G.degree().values())) - 12) / node_n
    while True:
        menu()
