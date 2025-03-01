from math import *
from Defination import *

infinity = float('inf')
paths = []

graph_out = open("./log/graph.log", 'w', encoding='utf-8')

# 节点
class Vertax:
    def __init__(self):
        self.ID = 0

    def set_ID(self, ID):
        self.ID = ID


class Edge:
    def __init__(self, From, To, ID, cost: float, bandwidth: float, loss: float):  # From/To:Vertax
        self.From = From
        self.To = To
        self.ID = ID
        self.cost = cost
        self.bandwidth = bandwidth
        self.loss = loss


class Graph:
    def __init__(self):
        self.Vertax_num = 0
        self.Edge_num = 0
        self.VertexSet = {}

        self.unvisitedSet = {}  # Vertax->bool
        self.distSet = {}  # Vertax->int
        self.prevSet = {}  # Vertax->edge列表

        self.dfs_visited = {}  # Vertax->bool
        self.dfs_path = []

    def addNode(self, v: Vertax):
        if (not (v in self.VertexSet.keys())):
            self.VertexSet.update({v: []})
            # print("节点已添加，ID为{}".format(v.ID))

            self.unvisitedSet.update({v: True})
            self.distSet.update({v: infinity})
            self.prevSet.update({v: []})

            self.dfs_visited.update({v: False})

    def AddEdge_Oneway(self, source: Vertax, to: Vertax, ID, cost, bandwidth, loss):  # 按参数添加一条有向边
        edge = Edge(source, to, ID, cost, bandwidth, loss)
        self.addEdge(edge)

    def AddEdge(self, source: Vertax, to: Vertax, ID, cost, bandwidth, loss):  # 按参数添加一条双向边
        self.AddEdge_Oneway(source, to, ID, cost, bandwidth, loss)
        self.AddEdge_Oneway(to, source, ID, cost, bandwidth, loss)

    def addEdge(self, edge):  # 添加一条边
        self.addNode(edge.From)
        self.addNode(edge.To)
        self.VertexSet[edge.From].append(edge)

    def removeEdge(self, edge):
        from_t = edge.From
        to_t = edge.To

        self.VertexSet[edge.From].remove(edge)
        for i in self.VertexSet[to_t]:
            if (i.To == from_t):
                self.VertexSet[edge.To].remove(i)

    def removeEdge_between(self, From, To):
        for i in self.VertexSet[From]:
            if i.To == To:
                self.VertexSet[From].remove(i)
                break

        for i in self.VertexSet[To]:
            if i.To == From:
                self.VertexSet[To].remove(i)
                break

    def display_edge_information(self, From, To):
        for i in self.VertexSet[From]:
            if i.To == To:
                print("Graph:cost={},bandwidth={},loss={}".format(i.cost, i.bandwidth, i.loss))
                break

    def display_graph(self, time):  # 打印图
        graph_out.write("t={}\n".format(time))
        for key in self.VertexSet.keys():
            graph_out.write("{}:".format(key.ID))
            if len(self.VertexSet[key]) == 0:
                print("none")
            else:
                for i in range(len(self.VertexSet[key])):
                    graph_out.write("{}-->{}边-->{},band={}   ;".format(key.ID, self.VertexSet[key][i].ID, self.VertexSet[key][i].To.ID,
                                                       self.VertexSet[key][i].bandwidth))
            graph_out.write("\n")

    def edgeSatisfiesConstranints(self, e:Edge, cons_bandwidth):
        if e.bandwidth > cons_bandwidth:
            return True
        else:
            return False

    def getSmallestDistanceVertex(self):
        smallestDist = infinity
        closestVertax = Vertax()
        is_founded = 0
        for v in self.unvisitedSet:
            dist = self.distSet[v]
            if dist < smallestDist:
                smallestDist = dist
                closestVertax = v
                is_founded = 1

        if is_founded == 0:
            return False
        else:
            return closestVertax

    # 按带宽约束 获得最短路径
    # 返回:只包含最短路径和部分残缺路径的图
    def CSPF(self, source, to, cons_bandwidth):

        for v in self.VertexSet:
            self.unvisitedSet[v] = True
            self.distSet[v] = infinity
            self.prevSet[v].clear()

        self.distSet[source] = 0

        while len(self.unvisitedSet) > 0:

            setSize = len(self.unvisitedSet)
            closestVertex = self.getSmallestDistanceVertex()

            if closestVertex == False:
                break
            else:
                self.unvisitedSet.pop(closestVertex)

                if setSize == len(self.unvisitedSet):
                    break

                for edge in self.VertexSet[closestVertex]:
                    if (edge.To in self.unvisitedSet.keys()):
                        # 找出符合条件的链路
                        satisfied = self.edgeSatisfiesConstranints(edge, cons_bandwidth)
                        if satisfied == True:
                            distFromNeighbor = self.distSet[closestVertex] + edge.cost
                            if (distFromNeighbor < self.distSet[edge.To]):
                                self.distSet[edge.To] = distFromNeighbor
                                # self.prevSet[edge.To].append(edge)
                                if (len(self.prevSet[edge.To]) == 0):
                                    self.prevSet[edge.To].append(edge)
                                else:
                                    self.prevSet[edge.To][0] = edge

                            elif (distFromNeighbor == self.distSet[edge.To]):
                                self.distSet[edge.To] = distFromNeighbor
                                self.prevSet[edge.To].append(edge)

        SPF = Graph()
        if (to in self.prevSet.keys() or to == source):
            for edges in self.prevSet:
                for edge in self.prevSet[edges]:
                    SPF.addEdge(edge)
        return SPF

    # 对SPF进行dfs 获得路径
    def dfs(self, source, to, edge):
        global paths
        self.dfs_visited[source] = True

        if edge != None:
            self.dfs_path.append(edge)

        if source == to:
            paths.append(self.dfs_path)
        else:
            if source in self.VertexSet.keys():
                for edge in self.VertexSet[source]:
                    if not self.dfs_visited[edge.To]:
                        self.dfs(edge.To, to, edge)

        if len(self.dfs_path) > 0:
            self.dfs_path = self.dfs_path[:-1]
        self.dfs_visited[source] = False

    # 调用dfs,获得两点间最短路径，并计算路径参数
    # 返回(cost,band,loss,p)的列表，p为路径的集合
    def graph_to_path(self, source, to):
        self.dfs_path.clear()
        for node in self.dfs_visited:
            self.dfs_visited[node] = False

        self.dfs(source, to, None)

        path_result = []
        for Path in paths:
            p = []
            cost = 0
            bandwidth = 9999999
            path_success = 1

            for edge in Path:
                temp_edge = Edge(edge.From, edge.To, edge.ID, edge.cost, edge.bandwidth, edge.loss)
                p.append(temp_edge)

                cost = cost + edge.cost
                path_success *= (1 - edge.loss)
                if edge.bandwidth < bandwidth:
                    bandwidth = edge.bandwidth
            path_loss = 1 - path_success
            path_result.append((cost, bandwidth, path_loss, p))

        paths.clear()
        return path_result

    # 调用graph_to_path并打印最短路径
    def print_path(self, source, to):
        path_result = self.graph_to_path(source, to)
        for road in path_result:
            print("********找到路径********")
            for j in road[3]:
                print(j.ID, end=' ')
            print("cost={}".format(road[0]))

    # 计算次短路径
    # 当最短路径不满足所有约束条件时，Preferred_cons=COST_FIRST，寻找符合条件的次短路径。仍未找到返回False
    # 当最短路径满足条件，但时延远小于qos需求时，Preferred_cons=BANDWIDTH_FIRST，评估剩余带宽。若剩余带宽不足，使用带宽更大、时延更大的路径
    def get_sub_shortest_path(self, source, to, Preferred_cons, Path_list, cons_delay, cons_bandwidth, cons_loss,
                              cons_jitter, path_delay_last):
        if Preferred_cons == SINGLE_FIRST:
            road = Path_list[0]
            edge = road[3][0]
            # self.removeEdge(edge)

            edge_saved = edge
            self.removeEdge_between(edge.From, edge.To)

            Graph_sub = self.CSPF(source, to, cons_bandwidth)
            Path_sub = Graph_sub.graph_to_path(source, to)

            self.addEdge(edge_saved)
            if len(Path_sub):
                Road_alternative = Path_sub[0]

                path_jitter = fabs(Road_alternative[0] - path_delay_last)
                path = Road_alternative[3]
                return Road_alternative, path_jitter
            else:
                return False

        else:
            Road_to_be_Selected = []
            for road in Path_list:
                for edge in road[3]:
                    edge_saved = edge
                    # self.removeEdge(edge)
                    self.removeEdge_between(edge.From, edge.To)

                    Graph_sub = self.CSPF(source, to, cons_bandwidth)
                    Path_sub = Graph_sub.graph_to_path(source, to)
                    for road in Path_sub:
                        Road_to_be_Selected.append(road)
                        # cost_test.append(road[0])
                    self.addEdge(edge_saved)

            if len(Road_to_be_Selected) != 0:
                if Preferred_cons == COST_FIRST:
                    Road_to_be_Selected.sort(key=lambda t: t[0])  # 按cost从小到大排序

                    path_loss = 0
                    path_jitter = 0

                    for road in Road_to_be_Selected:  # 找到满足条件且cost较小的路径
                        path_band = road[1]
                        path_loss = road[2]
                        path_jitter = fabs(road[0] - path_delay_last)
                        if (path_loss < cons_loss) and (path_jitter <= cons_jitter) and (road[0] <= cons_delay):
                            # if (path_loss < cons_loss):
                            return road, path_jitter

                    if road == Road_to_be_Selected[-1]:  # 未找到满足所有约束的路径
                        print("其余不符合要求")
                        print(cons_delay, cons_loss, cons_jitter)
                        print(road[0], path_delay_last)
                        return False

                elif Preferred_cons == BANDWIDTH_FIRST:
                    Road_to_be_Selected.sort(key=lambda t: t[1])
                    Road_to_be_Selected.reverse()  # 按带宽从大到小排序

                    for road in Road_to_be_Selected:  # 找到满足条件且带宽较大的路径
                        for edge in road[3]:
                            print(edge.From.ID, end='->')
                        print(road[3][-1].To.ID)

                        path_band = road[1]
                        path_loss = road[2]
                        path_jitter = fabs(road[0] - path_delay_last)
                        if (path_loss < cons_loss) and (path_jitter <= cons_jitter) and (road[0] <= cons_delay):
                            return road, path_jitter

                    if road == Road_to_be_Selected[-1]:  # 未找到，直接返回带宽最大的路径
                        road = Road_to_be_Selected[0]
                        path_band = road[1]
                        path_loss = road[2]
                        path_jitter = fabs(road[0] - path_delay_last)
                        return road, path_jitter

            else:
                return False

    # 按照所有约束条件 生成最短路径
    def Get_CSPF_path(self, source, to, cons_delay, cons_bandwidth, cons_loss, cons_jitter, path_delay_last):

        #返回CSPF约束的一条路径
        Graph_temp = self.CSPF(source, to, cons_bandwidth)
        Path_temp = Graph_temp.graph_to_path(source, to)

        Alternative_path = []
        Alternative_jitter = 0

        # flag_founded = 0

        if len(Path_temp) == 0:
            print("带宽不符合要求，未找到路径")
            return False
        else:
            for road in Path_temp:
                path_band = road[1]
                path_loss = road[2]
                path_jitter = fabs(road[0] - path_delay_last)

                if (path_loss <= cons_loss) and (path_jitter <= cons_jitter) and (road[0] <= cons_delay):
                    flag_founded = 1
                    if road[0] <= cons_delay * 0.4:
                        if path_band / BANDWIDTH <= 0.15:   # 当前路径性能过剩且资源不足，保存为备选路径；另找一条带宽更大的路径

                            Alternative_road = road
                            Alternative_jitter = path_jitter

                            print("链路性能过剩且资源已不足，选用次优路径")
                            temp = self.get_sub_shortest_path(source, to, BANDWIDTH_FIRST, Path_temp, cons_delay,
                                                              cons_bandwidth,
                                                              cons_loss, cons_jitter, path_delay_last)
                            if temp:
                                (road, path_jitter) = temp
                                return road, path_jitter, Alternative_road, Alternative_jitter
                            else:
                                return False
                            # return self.get_sub_shortest_path(source, to, BANDWIDTH_FIRST, Path_temp, cons_delay,
                            #                                   cons_bandwidth,
                            #                                   cons_loss, cons_jitter, path_delay_last)
                        else:
                            # 返回最短路径;获取一条备选路径
                            temp = self.get_sub_shortest_path(source, to, SINGLE_FIRST, Path_temp, cons_delay,
                                                              cons_bandwidth,
                                                              cons_loss, cons_jitter, path_delay_last)
                            if temp:
                                (Alternative_road, Alternative_jitter) = temp
                                return road, path_jitter, Alternative_road, Alternative_jitter
                            else:
                                return False
                    else:
                        # 返回最短路径;获取一条备选路径
                        temp = self.get_sub_shortest_path(source, to, SINGLE_FIRST, Path_temp, cons_delay,
                                                          cons_bandwidth,
                                                          cons_loss, cons_jitter, path_delay_last)
                        if temp:
                            (Alternative_road, Alternative_jitter) = temp
                            return road, path_jitter, Alternative_road, Alternative_jitter
                        else:
                            return False

            # 未找到满足所有约束的路径,开始寻找次短路径
            # 仍未找到时返回False
            if road == Path_temp[-1]:
                # 获取一条备选路径
                temp = self.get_sub_shortest_path(source, to, COST_FIRST, Path_temp, cons_delay,
                                                  cons_bandwidth,
                                                  cons_loss, cons_jitter, path_delay_last)
                if temp:
                    (road, path_jitter) = temp
                return road, path_jitter, road, path_jitter

