from Defination import *
Subcarrier_log = open("./log/Subcarrier.log", 'w', encoding='utf-8')


# 接入节点数据类型
class AccessNode:
    def __init__(self,ID):
        self.ID = ID
        self.total_data_rate = ACCESS_DATA_RATE       # 带宽5Gbps，单位Mbps
        self.used_data_rate = 0


class AccessNetwork:
    def __init__(self,  topo):
        # 接入网的先验知识
        self.topo = topo
        self.AccessNode_list = []

        self.access_cons_delay = 0
        self.access_cons_bandwidth = 0
        self.access_cons_loss = 0
        self.access_cons_jitter = 0

    def initial_AccessNode_list(self):
        for sat in self.topo.satellite:
            node = AccessNode(sat.ID)
            self.AccessNode_list.append(node)

    # 获取某节点接入资源利用率
    def calculate_access_resource(self, node_ID):
        Total_Data_Rate = self.AccessNode_list[node_ID - 1].total_data_rate
        Used_Data_Rate = self.AccessNode_list[node_ID - 1].used_data_rate
        access_ratio = float(Used_Data_Rate) / Total_Data_Rate
        return access_ratio

    # 输入：当前接入网实际qos指标
    # 输出：是否接入成功
    def access_judge(self, access_delay, access_bandwidth, access_loss, access_jitter):
        if(access_delay >= self.access_cons_delay)and(access_bandwidth <= self.access_cons_bandwidth)and\
          (access_loss>=self.access_cons_loss)and(access_jitter>=self.access_cons_jitter):
            return True
        else:
            return False

    # 进行实际的接入资源分配
    def access_resource_allocation(self, node_ID, access_bandwidth):
        node = self.AccessNode_list[node_ID - 1]
        assert node.used_data_rate + access_bandwidth <= node.total_data_rate
        self.AccessNode_list[node_ID - 1].used_data_rate += access_bandwidth
        # print("{}扣除{}Mbps".format(node_ID, access_bandwidth),end=",")
        # print("此时已使用{}Mbps".format(self.AccessNode_list[node_ID - 1].used_data_rate))

    # 资源释放
    def access_resource_release(self, node_ID, access_bandwidth):
        self.AccessNode_list[node_ID - 1].used_data_rate -= access_bandwidth
        # print("{}恢复{}Mbps".format(node_ID, access_bandwidth),end=",")
        # print("此时已使用{}Mbps".format(self.AccessNode_list[node_ID - 1].used_data_rate))

    def print_carrier_log(self, t):
        Subcarrier_log.write("*************time = {}*************\n".format(t))
        for Node in self.AccessNode_list:
            str = "卫星{}当前已使用:{}Mbps\n".format(Node.ID, Node.used_data_rate)
            Subcarrier_log.write(str)
