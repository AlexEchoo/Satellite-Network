from Defination import *
from Topology import Topology
from math import cos, fabs
from CSPF import *
# from User import User
# from Satellite import Satellite
from Position import Calc_Sphere_Distance

# from Logger import Logger

# 输出文件列表
LSDB_log = open("./log/LSDB.log", 'w', encoding='utf-8')
path_log = open("./log/path.log", 'w', encoding='utf-8')


# Link state advertisement, OSPF中的链路状态通告，用于通告其他节点链路状态，此处代表LSDB中的一个条目（一条链路的数据结构）
class LSA:
    def __init__(self):
        self.isEstablished = False
        self.source_ID = 0
        self.source_interface = 0
        self.destinate_ID = 0
        self.destinate_interface = 0


        self.delay = 0.0
        self.loss = BEARER_LOSS
        self.total_band = BANDWIDTH
        self.used_band = 0.0
        self.Remaining_band = self.total_band - self.used_band

    def Config(self, flag, sid, sif, did, dif, delay):
        self.isEstablished = flag
        self.source_ID = sid
        self.source_interface = sif
        self.destinate_ID = did
        self.destinate_interface = dif
        self.delay = delay

    def Establish(self, sid, sif, did, dif, delay):
        self.Config(True, sid, sif, did, dif, delay)

    def Interrupt(self):
        self.isEstablished = False
        self.total_band = 0.0
        self.used_band = 0.0


class BearerNetwork:
    def __init__(self, topo):
        self.topo = topo
        self.LSDB = []
        self.Alternative_path = {}

        v = Vertax()
        self.node_list = [v for i in range(len(self.topo.satellite))]  # 按ID索引卫星节点
        self.GatewayNode_list = [v for i in range(len(self.topo.gateway))]  # 按ID索引卫星节点

        self.Network_Graph = Graph()
        self.path_delay_last = 0

    def Initial_Network(self):
        con_num = len(self.topo.constellation)
        self.LSDB = [[] for _ in range(con_num)]

        for i in range(con_num):
            sat_num = self.topo.constellation[i].orbit_num * self.topo.constellation[i].sat_per_orbit
            self.LSDB[i] = [[] for _ in range(sat_num)]
            for j in range(sat_num):
                self.LSDB[i][j] = [LSA() for _ in range(4)]

    # 链路状态数据库更新，只更新链路对应关系
    def Update_LSDB(self):
        for i in range(len(self.topo.constellation)):
            temp_con = self.topo.constellation[i]
            for j in range(temp_con.orbit_num):
                temp_orbit = temp_con.orbit_sat[j]
                for k in range(temp_orbit.sat_num):
                    temp_sat = temp_orbit.sat_in_orbit[k]
                    self.LSDB[i][j * temp_con.sat_per_orbit + k][0].Config(True, temp_sat.ID, 1,
                                                                           temp_sat.ID + temp_orbit.sat_num - 1 if temp_sat.ID % temp_orbit.sat_num == 1 else temp_sat.ID - 1,
                                                                           2, METRIC)
                    self.LSDB[i][j * temp_con.sat_per_orbit + k][1].Config(True, temp_sat.ID, 2,
                                                                           temp_sat.ID - temp_orbit.sat_num + 1 if temp_sat.ID % temp_orbit.sat_num == 0 else temp_sat.ID + 1,
                                                                           1, METRIC)
                    if temp_con.orbit_num > 1:
                        if fabs(temp_sat.we_pos.lat) <= THRESHOLD:
                            if temp_orbit.orbit_id == 1:
                                if temp_con.type == TYPE_2PI:
                                    index = temp_con.sat_per_orbit * (temp_con.orbit_num - 1)
                                    if fabs(temp_con.orbit_sat[temp_con.orbit_num - 1].sat_in_orbit[
                                                k].we_pos.lat) <= THRESHOLD:
                                        self.LSDB[i][j * temp_con.sat_per_orbit + k][2].Config(True, temp_sat.ID,
                                                                                               3 if temp_sat.isNorth else 4,
                                                                                               temp_sat.ID + index,
                                                                                               4 if temp_sat.isNorth else 3,
                                                                                               METRIC)
                                if fabs(temp_con.orbit_sat[j + 1].sat_in_orbit[k].we_pos.lat) <= THRESHOLD:
                                    self.LSDB[i][j * temp_con.sat_per_orbit + k][3].Config(True, temp_sat.ID,
                                                                                           4 if temp_sat.isNorth else 3,
                                                                                           temp_sat.ID + temp_orbit.sat_num,
                                                                                           3 if temp_sat.isNorth else 4,
                                                                                           METRIC)
                            elif temp_orbit.orbit_id < temp_con.orbit_num:
                                if fabs(temp_con.orbit_sat[j - 1].sat_in_orbit[k].we_pos.lat) <= THRESHOLD:
                                    self.LSDB[i][j * temp_con.sat_per_orbit + k][2].Config(True, temp_sat.ID,
                                                                                           3 if temp_sat.isNorth else 4,
                                                                                           temp_sat.ID - temp_orbit.sat_num,
                                                                                           4 if temp_sat.isNorth else 3,
                                                                                           METRIC)
                                if fabs(temp_con.orbit_sat[j + 1].sat_in_orbit[k].we_pos.lat) <= THRESHOLD:
                                    self.LSDB[i][j * temp_con.sat_per_orbit + k][3].Config(True, temp_sat.ID,
                                                                                           4 if temp_sat.isNorth else 3,
                                                                                           temp_sat.ID + temp_orbit.sat_num,
                                                                                           3 if temp_sat.isNorth else 4,
                                                                                           METRIC)
                            else:
                                if fabs(temp_con.orbit_sat[j - 1].sat_in_orbit[k].we_pos.lat) <= THRESHOLD:
                                    self.LSDB[i][j * temp_con.sat_per_orbit + k][2].Config(True, temp_sat.ID,
                                                                                           3 if temp_sat.isNorth else 4,
                                                                                           temp_sat.ID - temp_orbit.sat_num,
                                                                                           4 if temp_sat.isNorth else 3,
                                                                                           METRIC)
                                if temp_con.type == TYPE_2PI:
                                    index = temp_con.sat_per_orbit * (temp_con.orbit_num - 1)
                                    if fabs(temp_con.orbit_sat[0].sat_in_orbit[k].we_pos.lat) <= THRESHOLD:
                                        self.LSDB[i][j * temp_con.sat_per_orbit + k][3].Config(True, temp_sat.ID,
                                                                                               4 if temp_sat.isNorth else 3,
                                                                                               temp_sat.ID - index,
                                                                                               3 if temp_sat.isNorth else 4,
                                                                                               METRIC)

    def Update_delay(self):  # 更新链路时延（LSDB和图）
        for sat in self.topo.satellite:
            for i in range(4):
                sat1_loc = sat.we_pos
                sat2_loc = self.topo.satellite[self.LSDB[0][sat.ID - 1][i].destinate_ID - 1].we_pos
                delay = Calc_Sphere_Distance(sat1_loc, sat2_loc) / 3e8 * 1000

                self.LSDB[0][sat.ID - 1][i].delay = delay  # 更新LSDB

                node = self.node_list[sat.ID - 1]  # 更新图
                for edge in self.Network_Graph.VertexSet[node]:
                    if edge.To.ID == self.LSDB[0][sat.ID - 1][i].destinate_ID:
                        edge.cost = delay

    def update_graph_bandwidth(self):  # 更新链路带宽（图）

        for sat in self.topo.satellite:
            node = self.node_list[sat.ID - 1]  # 更新图
            for i in range(4):
                for edge in self.Network_Graph.VertexSet[node]:
                    if edge.To.ID == self.LSDB[0][sat.ID - 1][i].destinate_ID:
                        edge.bandwidth = self.LSDB[0][sat.ID - 1][i].Remaining_band
                        break


    def display_LSA_information(self, From, To):
        for i in range(4):
            if self.LSDB[0][From - 1][i].destinate_ID == To:
                print("LSA:delay={},bandwidth={},loss={}".format(self.LSDB[0][From - 1][i].delay,
                                                                 self.LSDB[0][From - 1][i].Remaining_band,
                                                                 self.LSDB[0][From - 1][i].loss))
                break

    # 检索链路，返回指针
    def Lookup_LSA(self, con, source, destination):
        for i in range(len(self.LSDB[con - 1][source - 1])):
            if self.LSDB[con - 1][source - 1][i].isEstablished and self.LSDB[con - 1][source - 1][i].destinate_ID == destination:
                return self.LSDB[con - 1][source - 1][i]
        return None

    # 检索链路对应节点的几号端口，返回端口号
    def Lookup_LSA_Index(self, con, source, destination):
        for i in range(len(self.LSDB[con - 1][source - 1])):
            if self.LSDB[con - 1][source - 1][i].isEstablished and self.LSDB[con - 1][source - 1][i].destinate_ID == destination:
                return i + 1
        return -1

    def network_to_graph(self):  # 使用LSDB数据建立图
        g = Graph()
        for sat in self.topo.satellite:
            node = Vertax()
            node.set_ID(sat.ID)
            self.node_list[sat.ID - 1] = node  # 便于根据ID索引卫星节点
            g.addNode(node)

        for gateway in self.topo.gateway:
            node = Vertax()
            node.set_ID(len(self.topo.satellite) + gateway.id)
            self.GatewayNode_list[gateway.id - 1] = node  # 便于根据ID索引卫星节点
            g.addNode(node)

        edge_count = 0

        for sat in self.topo.satellite:
            for i in range(4):
                node1 = self.node_list[self.LSDB[0][sat.ID - 1][i].source_ID - 1]
                node2 = self.node_list[self.LSDB[0][sat.ID - 1][i].destinate_ID - 1]
                if self.LSDB[0][sat.ID - 1][i].isEstablished:
                    g.AddEdge_Oneway(node1, node2, edge_count,
                                     self.LSDB[0][sat.ID - 1][i].delay, self.LSDB[0][sat.ID - 1][i].Remaining_band,
                                     self.LSDB[0][sat.ID - 1][i].loss)
                    edge_count += 1

        for gateway in self.topo.gateway:
            node2 = self.GatewayNode_list[gateway.id - 1]
            for Edge in g.VertexSet[node2]:
                V_destiny = Edge.To
                for edge in g.VertexSet[V_destiny]:
                    if edge.To == node2:
                        g.removeEdge(edge)
                        break

            for sat in gateway.sat_covered:
                pos_sat = sat.we_pos
                pos_gateway = gateway.we_pos
                delay = Calc_Sphere_Distance(pos_sat, pos_gateway) / 3e8 * 1000

                node1 = self.node_list[sat.ID - 1]
                g.AddEdge_Oneway(node1, node2, edge_count, delay, 99999, 0.0000001)
                # 便于拆除链路 上行链路不参与CSPF
                g.AddEdge_Oneway(node2, node1, edge_count, delay, 0, 0.0000001)
                edge_count += 1
        return g

    # 传入源用户、目的信关站ID，按约束条件生成最短路径，并分配资源
    def Bearer_resource_allocation(self, source_ID, destination_ID, cons_delay, cons_bandwidth, cons_loss, cons_jitter):
        node1 = self.node_list[source_ID - 1]
        node2 = self.GatewayNode_list[destination_ID - 1]

        Path_from_CSPF = self.Network_Graph.Get_CSPF_path(node1, node2, cons_delay, cons_bandwidth, cons_loss,
                                                          cons_jitter, self.path_delay_last)

        if Path_from_CSPF:
            delay = Path_from_CSPF[0][0]
            bandwidth = Path_from_CSPF[0][1]  # 为路径的实际带宽
            loss = Path_from_CSPF[0][2]
            path_list = Path_from_CSPF[0][3]
            jitter = Path_from_CSPF[1]

            # 备份路径信息
            Alternative_path = Path_from_CSPF[2]
            Alternative_delay = Path_from_CSPF[2][0]
            Alternative_jitter = Path_from_CSPF[3]

            # 保存备份路径;输出至日志
            self.Alternative_path.update({(source_ID, destination_ID):(Alternative_path, Alternative_jitter)})
            self.print_main_alt_path(self.topo.current_time, path_list, delay, Alternative_path[3], Alternative_delay)

            for edge in path_list:
                node1 = edge.From
                node2 = edge.To
                for i in range(4):  # 更新双向链路带宽
                    if node1.ID <= len(self.topo.satellite) :
                        if self.LSDB[0][node1.ID - 1][i].destinate_ID == node2.ID:
                            self.LSDB[0][node1.ID - 1][i].used_band += cons_bandwidth
                            self.LSDB[0][node1.ID - 1][i].Remaining_band -= cons_bandwidth
                            break
                for i in range(4):
                    if node2.ID <= len(self.topo.satellite):
                        if self.LSDB[0][node2.ID - 1][i].destinate_ID == node1.ID:
                            self.LSDB[0][node2.ID - 1][i].used_band += cons_bandwidth
                            self.LSDB[0][node2.ID - 1][i].Remaining_band -= cons_bandwidth
                            break

            self.update_graph_bandwidth()
            return delay, cons_bandwidth, loss, jitter, path_list

        else:
            return False

    # 根据带宽和路径释放资源
    def Bearer_resource_release(self, bandwidth, path_list):
        for edge in path_list:
            node1 = edge.From
            node2 = edge.To
            for i in range(4):  # 更新双向链路的LSDB
                if node1.ID <= len(self.topo.satellite):
                    if self.LSDB[0][node1.ID - 1][i].destinate_ID == node2.ID:
                        self.LSDB[0][node1.ID - 1][i].used_band -= bandwidth
                        self.LSDB[0][node1.ID - 1][i].Remaining_band += bandwidth
                        # print("{}--{}间链路释放资源{},已用带宽{}".format(node1.ID, node2.ID, bandwidth,
                        #                                       self.LSDB[0][node1.ID - 1][i].used_band))
                        break
            for i in range(4):
                if node2.ID <= len(self.topo.satellite):
                    if self.LSDB[0][node2.ID - 1][i].destinate_ID == node1.ID:
                        self.LSDB[0][node2.ID - 1][i].used_band -= bandwidth
                        self.LSDB[0][node2.ID - 1][i].Remaining_band += bandwidth
                        break
        self.update_graph_bandwidth()

    def print_LSDB_log(self, t):
        LSDB_log.write("*************time = {}*************\n".format(t))
        for i in range(len(self.topo.satellite)):
            for j in range(4):
                # str = "卫星%d--卫星%d,时延%.5f  " % (i + 1, self.LSDB[0][i][j].destinate_ID,
                #                              self.LSDB[0][i][j].delay)
                str = "卫星%d--卫星%d,剩余带宽%d  " % (i + 1, self.LSDB[0][i][j].destinate_ID,
                                             self.LSDB[0][i][j].Remaining_band)
                # str = "卫星{}--卫星{},建立状态{}  ".format(i + 1, self.LSDB[0][i][j].destinate_ID,
                #                              self.LSDB[0][i][j].isEstablished)
                LSDB_log.write(str)
            LSDB_log.write("\n")

    # 输出主路径、备份路径
    def print_main_alt_path(self, t, path_list, delay, Alternative_path, Alternative_delay):
        path_log.write("*************time = {}*************\n".format(t))
        path_log.write("主路径:")
        for edge in path_list:
            path_log.write("{}->".format(edge.From.ID))
        path_log.write("{},时延={}ms\n".format(edge.To.ID, delay))

        path_log.write("备份路径:")
        for edge in Alternative_path:
            path_log.write("{}->".format(edge.From.ID))
        path_log.write("{},时延={}ms\n".format(edge.To.ID, Alternative_delay))
