# from UE import BusinessReq
from Position import *
from Bearer_network import *
from Access_network import *
from decimal import *
from Topology import *
from random import *
import heapq


# 业务优先级队列
class Orchestrator:
    def __init__(self):
        self.queue = []
        self.queue_len = 0
        self.index = 0

    # 元素入队
    def queue_push(self, item, priority):
        heapq.heappush(self.queue, (-priority, self.index, item))
        self.index += 1
        self.queue_len +=1

    # 元素出队
    def queue_pop(self):
        self.queue_len -= 1
        return heapq.heappop(self.queue)[-1]


def takeBusinessType(elem):
    return elem[3]


class EachRequest:
    def __init__(self, sour_ID, dest_ID, sour_we_pos, dest_we_pos,req_time, req_dur, cons_delay, cons_bandwidth,
                 cons_loss, cons_jitter):
        self.sour_ID = sour_ID
        self.dest_ID = dest_ID
        self.sour_we_pos = sour_we_pos
        self.dest_we_pos = dest_we_pos
        self.req_time = req_time
        self.req_dur = req_dur
        self.cons_bandwidth = cons_bandwidth
        self.cons_delay = cons_delay
        self.cons_loss = cons_loss
        self.cons_jitter = cons_jitter

    def getAccessQoS(self, bearer_delay, bearer_loss, bearer_jitter):
        self.access_qos = [0.0 for i in range(3)]
        self.access_qos[0] = self.cons_delay - bearer_delay
        self.access_qos[1] = (self.cons_loss - bearer_loss)/(1 - bearer_loss)
        self.access_qos[2] = self.cons_jitter - bearer_jitter
        return self.access_qos

    def getBearerQoS(self, access_delay, access_loss, access_jitter):
        self.bearer_qos = [0.0 for i in range(3)]

        print("get bearer: delay={}，consdelay={}".format(access_delay, self.cons_delay))
        self.bearer_qos[0] = self.cons_delay - access_delay
        self.bearer_qos[1] = (self.cons_loss - access_loss)/(1 - access_loss)
        self.bearer_qos[2] = self.cons_jitter - access_jitter
        return self.bearer_qos

    def resource_schedule_judge(self, access_network, bearer_network, access_delay, access_bandwidth, access_loss,
                                access_jitter,
                                is_bearer_best, source_ID, destination_ID):

        if access_network.access_judge(access_delay, access_bandwidth, access_loss, access_jitter)==True:
            bearerQoS = self.getBearerQoS(access_delay, access_loss, access_jitter)

            if is_bearer_best:
                status_allocation = bearer_network.Bearer_resource_allocation(source_ID, destination_ID, self.cons_delay,
                                                                          self.cons_bandwidth, self.cons_loss, self.cons_jitter)
            else:
                status_allocation = bearer_network.Bearer_resource_allocation(source_ID, destination_ID, bearerQoS[0],
                                                                          self.cons_bandwidth, bearerQoS[1],bearerQoS[2])

            if status_allocation:
                bearer_delay, bearer_cons_bandwidth, bearer_loss, bearer_jitter, bearer_path_list = status_allocation
                access_network.access_resource_allocation(source_ID, access_bandwidth)  # 源ID即接入卫星ID

                return bearer_delay, bearer_cons_bandwidth, bearer_loss, bearer_jitter, bearer_path_list
            else:
                print("----------承载网分配失败")
                return False

        else:
            print("----------接入网分配失败")
            return False


    def floatrange(self, start, stop, steps):
        resultList = []

        while Decimal(str(start)) <= Decimal(str(stop)):
            resultList.append(float(Decimal(str(start))))

            start = Decimal(str(start)) + Decimal(str(steps))

        return resultList


    def update_QoS_split(self, access_network, bearer_network, access_delay, access_bandwidth, access_loss,
                         access_jitter, step, source_ID, destination_ID):
        delay_list = self.floatrange(access_delay, 100, step)   # 5
        for i in range(len(delay_list)):
            status_judge = self.resource_schedule_judge(access_network, bearer_network, delay_list[i], access_bandwidth,
                                                        access_loss, access_jitter,
                                                        0, source_ID, destination_ID)
            if status_judge:
                bearer_delay, bearer_bandwidth, bearer_loss, bearer_jitter, bearer_path_list = status_judge

                if (bearer_delay <= self.cons_delay - delay_list[i] and bearer_bandwidth >= self.cons_bandwidth and
                        bearer_loss <= self.cons_loss - access_loss and bearer_jitter <= self.cons_jitter - access_jitter):

                    bearer_qos = [bearer_delay, bearer_bandwidth, bearer_loss, bearer_jitter]
                    access_qos_temp = self.getAccessQoS(bearer_delay, bearer_loss, bearer_jitter)
                    # access_qos = [access_qos_temp[0], access_bandwidth, access_qos_temp[1], access_qos_temp[2]]

                    # 此处传入为接入网最优性能
                    access_qos = [access_delay, access_bandwidth, access_loss, access_jitter]
                    return bearer_qos, access_qos, source_ID, bearer_path_list
                else:
                    print("QoS_split失败")
                    return False
            else:
                return False

    # 业务请求解析
    def request_parsing_and_allocation(self, Bearer_network:BearerNetwork, accessnetwork:AccessNetwork, N):
        # 1.由UE地址和目的信关站地址解析出接入卫星和落地卫星的ID
        # 要传入拓扑信息，获取卫星列表中各个卫星的位置
        sour_user = Bearer_network.topo.user[self.sour_ID - 1]
        dest_gateway = Bearer_network.topo.gateway[self.dest_ID - 1]

        temp = Bearer_network.topo.Location_parsing(sour_user, dest_gateway)
        # 接入、落地星已确定
        if temp:
            sat_Access_ID = temp
            dest_gateway_ID = dest_gateway.id

            # 2.获取CSPF最优路径对应的QoS指标并判断
            node1 = Bearer_network.node_list[sat_Access_ID - 1]
            node2 = Bearer_network.GatewayNode_list[dest_gateway.id - 1]

            # global path_delay_last
            print("初次获取路径")
            Path_from_CSPF = Bearer_network.Network_Graph.Get_CSPF_path(node1, node2, self.cons_delay, self.cons_bandwidth,
                                                                        self.cons_loss, self.cons_jitter,
                                                                        Bearer_network.path_delay_last)

            if not Path_from_CSPF:
                print("----------承载网分配失败")
                return False
            else:
                # 承载网最优性能
                delay = Path_from_CSPF[0][0]
                bandwidth = Path_from_CSPF[0][1]  # 为路径的实际带宽
                loss = Path_from_CSPF[0][2]
                path_list = Path_from_CSPF[0][3]
                jitter = Path_from_CSPF[1]

                #判断
                if delay>self.cons_delay or bandwidth<self.cons_bandwidth or loss>self.cons_loss or jitter>self.cons_jitter:
                    return False
                else:
                    # 获取接入节点利用率
                    access_ratio = accessnetwork.calculate_access_resource(sat_Access_ID)

                    # 计算接入网QoS性能边界+承载网的性能边界

                    # 获取接入网最优性能
                    # 最短时延:传播+排队处理
                    sat_Access = Bearer_network.topo.satellite[sat_Access_ID - 1]
                    distance = Calc_Sphere_Distance(sour_user.we_pos, sat_Access.we_pos)
                    access_delay_best = distance / 3e8 * 1000 + ACCESS_Processing_delay_BEST

                    # access_delay_best = distance / 3e8 * 1000 + randint(1,5)
                    # 最优带宽、抖动、丢包
                    access_node = accessnetwork.AccessNode_list[sat_Access_ID - 1]
                    access_bandwidth_best = (access_node.total_data_rate - access_node.used_data_rate)
                    access_loss_best = ACCESS_LOSS_BEST
                    access_jitter_best = ACCESS_JITTER_BEST

                    # 保存先验最优值
                    accessnetwork.access_cons_delay = access_delay_best
                    accessnetwork.access_cons_bandwidth = access_bandwidth_best
                    accessnetwork.access_cons_loss = access_loss_best
                    accessnetwork.access_cons_jitter = access_jitter_best

                    if access_ratio > N:
                        print("承载网最优")
                        # 使用承载网最优性能作边界

                        r = self.resource_schedule_judge(accessnetwork, Bearer_network,
                                                         self.cons_delay-delay, self.cons_bandwidth,
                                                         (self.cons_loss-loss)/(1-loss),self.cons_jitter-jitter,
                                                         1, sat_Access_ID, dest_gateway_ID)

                        if r != False:
                            bearer_delay, bearer_cons_bandwidth, bearer_loss, bearer_jitter, bearer_path_list = r

                            bearer_qos = [bearer_delay, bearer_cons_bandwidth, bearer_loss, bearer_jitter]
                            access_qos_target = self.getAccessQoS(bearer_delay, bearer_loss, bearer_jitter)
                            # access_qos = [access_qos_temp[0], self.cons_bandwidth, access_qos_temp[1], access_qos_temp[2]]

                            ACCESS_Processing_delay_DEFAULT = randint(1, 5)
                            access_delay = distance / 3e8 * 1000 + ACCESS_Processing_delay_DEFAULT

                            access_default_jitter = randint(ACCESS_JITTER_BEST, 4)
                            access_default_loss = uniform(ACCESS_LOSS_BEST, 0.00008)

                            access_qos = [access_delay, self.cons_bandwidth,
                                          access_default_loss, access_default_jitter]

                            total_qos = [0 for i in range(4)]
                            total_qos[0] = bearer_qos[0] + access_qos[0]
                            total_qos[1] = bearer_qos[1] if bearer_qos[1]<access_qos[1] else access_qos[1]
                            total_qos[2] = 1 - (1 - bearer_qos[2])*(1 - access_default_loss)
                            # total_qos[2] = bearer_qos[2] + access_default_loss
                            total_qos[3] = bearer_qos[3] + access_default_jitter

                            return bearer_qos, access_qos, total_qos, sat_Access_ID, bearer_path_list
                            # return bearer_qos, access_qos, sat_Access_ID, path_list
                        else:
                            print("资源调度失败1")
                            return False    # 这里应该return false吗？
                    else:
                        print("接入网最优")
                        # 使用接入网最优性能
                        status_split = self.update_QoS_split(accessnetwork, Bearer_network, access_delay_best,
                                                             self.cons_bandwidth, access_loss_best,
                                                             access_jitter_best, 5, sat_Access_ID, dest_gateway_ID)
                        if status_split:
                            bearer_qos, access_qos, sat_Access_ID, bearer_path_list = status_split

                            access_default_jitter = randint(ACCESS_JITTER_BEST, 4)
                            access_default_loss = uniform(ACCESS_LOSS_BEST, 0.00008)

                            total_qos = [0 for i in range(4)]
                            total_qos[0] = bearer_qos[0] + access_qos[0]
                            total_qos[1] = bearer_qos[1] if bearer_qos[1]<access_qos[1] else access_qos[1]
                            total_qos[2] = 1 - (1 - bearer_qos[2])*(1 - access_default_loss)
                            total_qos[3] = bearer_qos[3] + access_qos[3]
                            return bearer_qos, access_qos, total_qos, sat_Access_ID, bearer_path_list
                        else:
                            print("资源调度失败2")
                            return False

        else:
            return False

