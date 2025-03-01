from Orchestrator import *
from scipy import stats
import time
import random
import matplotlib.pyplot as plt
import time

business_out = open("./log/business.log", 'w', encoding='utf-8')
simulation_out = open("./log/simulation.log", 'w', encoding='utf-8')

if __name__ == '__main__':
    # 初始化拓扑
    topo = Topology()

    # # 大规模倾斜轨道
    # orbit_num = 27 #12
    # sat_per_orbit = 40   #9
    # height = 1150000
    # phase = 0  # 轨道相位因子
    # first_phi = 2.0 * phase * pi / (orbit_num * sat_per_orbit)  # 相邻轨道卫星相位差
    # lean = 50 / 180.0 * pi  # 轨道倾角
    # theta = 2 * pi / orbit_num  # 升交点赤经差
    # topo.Add_Constellation(orbit_num, sat_per_orbit, height, first_phi, lean, theta, TYPE_2PI)

    # 倾斜轨道
    orbit_num = 12 #12
    sat_per_orbit = 9   #9
    height = 1150000
    phase = 0  # 轨道相位因子
    first_phi = 2.0 * phase * pi / (orbit_num * sat_per_orbit)  # 相邻轨道卫星相位差
    lean = 50 / 180.0 * pi  # 轨道倾角
    theta = 2 * pi / orbit_num  # 升交点赤经差
    topo.Add_Constellation(orbit_num, sat_per_orbit, height, first_phi, lean, theta, TYPE_2PI)

    # # 近极轨星座
    # orbit_num = 6
    # sat_per_orbit = 10
    # height = 1175000
    # phase = 0  # 轨道相位因子
    # first_phi = 2.0 * phase * pi / (orbit_num * sat_per_orbit)  # 相邻轨道卫星相位差
    # lean = 86.5 / 180.0 * pi  # 轨道倾角
    # theta = pi / orbit_num  # 升交点赤经差
    # topo.Add_Constellation(orbit_num, sat_per_orbit, height, first_phi, lean, theta, TYPE_PI)

    topo.Each_Satellite()

    for i in range(30):
        topo.Add_User()

    for i in range(8):
        topo.Add_Gateway()

    average_bandwidth_data = []

    Delay_Max_data = []
    Jitter_Max_data = []

    delete_flag = 0

    # 初始化承载网
    SAT_Network = BearerNetwork(topo)
    SAT_Network.Initial_Network()
    SAT_Network.Update_LSDB()
    SAT_Network.Network_Graph = SAT_Network.network_to_graph()
    SAT_Network.Update_delay()
    SAT_Network.update_graph_bandwidth()

    # 初始化接入网
    Access_Network = AccessNetwork(topo)
    Access_Network.initial_AccessNode_list()

    # 初始化优先级队列
    orchestrator = Orchestrator()

    parameter_dict = {}

    time_data = []

    business_ID = 1

    business_total_num = 0
    business_finish_num = 0
    business_fail_num = 0

    numOfBusiness = 0

    start = 0
    end = 6000
    step = 10

    for t in range(start + step, end, step):
        topo.Update_Topology_Status(t)

        # # 存在反向缝（如近极轨）必须执行该语句
        SAT_Network.Update_LSDB()

        SAT_Network.Network_Graph = SAT_Network.network_to_graph()
        SAT_Network.Update_delay()
        SAT_Network.update_graph_bandwidth()

        Access_Network.print_carrier_log(t)
        SAT_Network.print_LSDB_log(t)
        SAT_Network.Network_Graph.display_graph(t)



        if t <= 6000:
            # 生成若干新业务，加入优先级队列
            # business_num = int(topo.total_user * 0.2)

            # temp = stats.poisson.rvs(topo.total_user * 0.2, size=1)
            # business_num = temp[0]
            # business_total_num += business_num
            business_num = 5
            business_total_num += business_num
            numOfBusiness = numOfBusiness + 1

            for n in range(business_num):
                business_type = random.randint(1, 9)
                request_time = 0.5*random.randint(2*t, 2*(t+10))
                request_duration = step * random.randint(4, 10)

                if topo.total_user != 0:
                    source_id = randint(1, topo.total_user)
                if topo.total_gateway != 0:
                    destiny_id = randint(1, topo.total_gateway)
                    destiny_pos = topo.gateway[destiny_id - 1].we_pos

                # # 近极轨
                # delay = random.randint(110, 130)
                # bandwidth = 5 * random.randint(20, 40)
                # loss = random.uniform(0.0001, 0.0002)
                # jitter = 0.5 * random.randint(180, 220)
                # new_business = topo.user[source_id - 1].generate_business_request(business_type, request_time,
                #                                                                   request_duration,
                #                                                                   destiny_id, destiny_pos, delay,
                #                                                                   bandwidth,
                #                                                                   loss, jitter, business_ID)
                # 倾斜轨
                delay = random.randint(100, 120)
                bandwidth = 5 * random.randint(60, 120)
                # bandwidth = 500

                loss = random.uniform(0.0001, 0.0002)
                jitter = 0.5 * random.randint(80, 120)
                new_business = topo.user[source_id - 1].generate_business_request(business_type, request_time,
                                                                                  request_duration,
                                                                                  destiny_id, destiny_pos, delay,
                                                                                  bandwidth,
                                                                                  loss, jitter, business_ID)
                business_ID += 1

                orchestrator.queue_push(new_business, business_type)

                output_line = list(new_business)
                # business_out.write("{}\n".format(output_line))
                business_out.write("业务ID:{},源用户:{},目的信关站:{},业务优先级:{},发起时间:{},持续时间{}\n".
                                   format(output_line[11],output_line[0],output_line[5],output_line[2],
                                          output_line[3],output_line[4]))

        print("****************t={}****************".format(t))
        simulation_out.write("****************t={}****************\n".format(t))
        # 从队列中按业务优先级提取业务，更新资源
        business_list = []

        business_num_InSlice = 0
        business_num_InSlice_jit = 0

        delay_max_InSlice = 0
        jitter_max_InSlice = 0

        delay_sum = 0   # 统计卫星至信关站平均性能
        bandwidth_sum = 0
        jitter_sum = 0

        for i in range(orchestrator.queue_len):
            # 提取一个业务
            business = orchestrator.queue_pop()

            print("***********************************")
            simulation_out.write("***********************************\n")

            # 当前时刻业务已结束
            if t >= (business[3] + business[4]):
                print("业务{}已结束".format(business[11]))
                simulation_out.write("业务{}已结束\n".format(business[11]))

                # 释放承载侧资源，输入参数:带宽、path_list
                SAT_Network.Bearer_resource_release(business[8], parameter_dict[business][1])
                # 释放接入侧资源，输入参数:接入卫星、带宽
                Access_Network.access_resource_release(parameter_dict[business][0], business[8])

                del parameter_dict[business]

                business_finish_num += 1
            else:
                time1 = time.time()

                # 考虑到接入星改变等情况，先释放原有资源，再重新分配
                if business in parameter_dict.keys():
                    # 释放承载侧资源，输入参数:带宽、path_list
                    SAT_Network.Bearer_resource_release(business[8], parameter_dict[business][1])
                    # 释放接入侧资源，输入参数:接入卫星、带宽
                    Access_Network.access_resource_release(parameter_dict[business][0], business[8])

                # 更新承载网上次时延（用于限制抖动）
                if business in parameter_dict.keys():
                    SAT_Network.path_delay_last = parameter_dict[business][2]
                else:
                    SAT_Network.path_delay_last = 0

                if business in parameter_dict.keys():
                    process_Request = EachRequest(business[0], business[5], business[1], business[6], business[3],
                                                  business[4], business[7], business[8], business[9], business[10])
                else:
                    process_Request = EachRequest(business[0], business[5], business[1], business[6], business[3],
                                                  business[4], business[7], business[8], business[9], 9999)

                print("业务qos需求:delay=%.3f,band=%d,loss=%.7f,jitter=%3f"%(business[7], business[8], business[9], business[10]))
                simulation_out.write("业务qos需求:delay=%.3f,band=%d,loss=%.7f,jitter=%3f\n"%
                                     (business[7], business[8], business[9], business[10]))

                status_allocation = process_Request.request_parsing_and_allocation(SAT_Network, Access_Network,
                                                                                   Carrier_threshold)
                if status_allocation:
                    bearer_qos, access_qos, total_qos, sat_Access_ID, path_list = status_allocation

                    # 统计卫星至信关站最大时延、抖动
                    # bandwidth_sum += bearer_qos[1]
                    # business_num_InSlice += 1
                    if bearer_qos[0] > delay_max_InSlice:
                        delay_max_InSlice = bearer_qos[0]

                    # 初次分配的业务不计入抖动
                    if business in parameter_dict.keys():
                        # jitter_sum += bearer_qos[3]
                        # business_num_InSlice_jit += 1
                        if bearer_qos[3] > jitter_max_InSlice:
                            jitter_max_InSlice = bearer_qos[3]

                    # 保存业务参数 用于释放资源
                    parameter_dict.update({business: (sat_Access_ID, path_list, bearer_qos[0])})

                    # 装入临时列表，待重新入队;若分配不成功移除队列
                    business_list.append(business)

                    print("资源分配成功")
                    simulation_out.write("资源分配成功\n")
                    # print("承载网qos(卫星-信关站):delay=%.3f,band=%d,loss=%.7f,jitter=%3f"%(bearer_qos[0], bearer_qos[1],
                    #                                                           bearer_qos[2], bearer_qos[3]))
                    simulation_out.write("承载网qos(卫星-信关站):delay=%.3f,band=%d,loss=%.7f,jitter=%3f\n"%(bearer_qos[0], bearer_qos[1],
                                                                             bearer_qos[2], bearer_qos[3]))
                    # print("接入网qos:delay=%.3f,band=%d,loss=%.7f,jitter=%3f"%(access_qos[0], access_qos[1],
                    #                                                          access_qos[2], access_qos[3]))
                    simulation_out.write("接入网qos:delay=%.3f,band=%d,loss=%.7f,jitter=%3f\n"%(access_qos[0],
                                                                             access_qos[1],access_qos[2], access_qos[3]))
                    # print("总qos性能:delay=%.3f,band=%d,loss=%.7f,jitter=%3f"%(total_qos[0], total_qos[1],
                    #                                                          total_qos[2], total_qos[3]))
                    simulation_out.write("总qos性能:delay=%.3f,band=%d,loss=%.7f,jitter=%3f\n"%(total_qos[0], total_qos[1],
                                                                             total_qos[2], total_qos[3]))

                    simulation_out.write("业务{}:当前路径:".format(business[-1]))
                    for edge in path_list:
                        simulation_out.write("{}->".format(edge.From.ID))
                    simulation_out.write("{},时延={}ms,带宽={}\n".format(edge.To.ID, bearer_qos[0],
                                                                     bearer_qos[1]))
                    for edge in path_list:
                        simulation_out.write("{}->".format(edge.bandwidth))
                    simulation_out.write("\n")

                    # if t == 100 and delete_flag < 3:
                    #     path_list.pop(-1)
                    #     random_Link = random.sample(path_list, int(0.5*len(path_list)))
                    #     for link in random_Link:
                    #         source = link.From.ID
                    #         destiny = link.To.ID
                    #
                    #         for i in range(4):
                    #             if SAT_Network.LSDB[0][source - 1][i].destinate_ID == destiny:
                    #                 SAT_Network.LSDB[0][source - 1][i].Remaining_band = 0.02 * BANDWIDTH
                    #                 SAT_Network.LSDB[0][source - 1][i].used_band = 0.98 * BANDWIDTH
                    #                 break
                    #         for i in range(4):
                    #             if SAT_Network.LSDB[0][destiny - 1][i].destinate_ID == source:
                    #                 SAT_Network.LSDB[0][destiny - 1][i].Remaining_band = 0.02 * BANDWIDTH
                    #                 SAT_Network.LSDB[0][destiny - 1][i].used_band = 0.98 * BANDWIDTH
                    #                 break
                    #     delete_flag += 1
                else:
                    print("业务{}中途中止".format(business[11]))
                    simulation_out.write("业务{}中途中止\n".format(business[11]))
                    business_fail_num += 1

                time2 = time.time()
                time_data.append(time2 - time1)

        Delay_Max_data.append(delay_max_InSlice)
        Jitter_Max_data.append(jitter_max_InSlice)

        # if business_num_InSlice != 0:
        #     average_bandwidth = bandwidth_sum/business_num_InSlice
        #     average_bandwidth_data.append(average_bandwidth)

        # 重新入队
        for busi in business_list:
            orchestrator.queue_push(busi, busi[2])

    time_sum = 0
    for i in time_data:
        time_sum += i
    print("平均时间开销为{}".format(time_sum / len(time_data)))
    print("总时间开销为{}".format(time_sum))

    for i in range(20):
        Delay_Max_data.pop(-1)
    x_axis_data = [(i + 1) * 10 for i in range(len(Delay_Max_data))]
    y_axis_data = Delay_Max_data
    # plot中参数的含义分别是横轴值，纵轴值，线的形状，颜色，透明度,线的宽度和标签
    plt.plot(x_axis_data, y_axis_data, 'o-', color='#4169E1', alpha=0.8, linewidth=1, label='Delay')
    plt.legend(loc="upper right")
    plt.ylim(60, 120)
    plt.xlabel('time(s)')
    plt.ylabel('delay(s)')
    plt.show()

    for i in range(20):
        Jitter_Max_data.pop(-1)
    x_axis_data = [(i + 1) * 10 for i in range(len(Jitter_Max_data))]
    y_axis_data = Jitter_Max_data
    # plot中参数的含义分别是横轴值，纵轴值，线的形状，颜色，透明度,线的宽度和标签
    # plt.plot(x_axis_data, y_axis_data, 'o-', color='#C0C0C0', alpha=0.8, linewidth=1, label='Delay')
    plt.bar(x_axis_data, y_axis_data, label='Jitter', color="orange", width=3)
    plt.legend(loc="upper left")
    plt.ylim(0, 1.25*max(y_axis_data))
    plt.xlim(0, 6000)
    plt.xlabel('time(s)')
    plt.ylabel('jitter(ms)')
    plt.show()
    #
    # average_bandwidth_data.pop(-1)
    # average_bandwidth_data.pop(-1)
    # x_axis_data = [(i+1)*10 for i in range(len(average_bandwidth_data))]
    # y_axis_data = average_bandwidth_data
    # # plot中参数的含义分别是横轴值，纵轴值，线的形状，颜色，透明度,线的宽度和标签
    # plt.plot(x_axis_data, y_axis_data, 'o-', color='#ff0000', alpha=0.8, linewidth=1, label='Bandwidth')
    # plt.legend(loc="upper right")
    # plt.ylim(350, 550)
    # plt.xlabel('time(s)')
    # plt.ylabel('bandwidth(Mbps)')
    # plt.show()

    print("共生成{}个业务,完成业务{}个,中途失败{}个".format(business_total_num, business_finish_num, business_fail_num))
    simulation_out.write("共生成{}个业务,完成业务{}个,中途失败{}个".format(business_total_num, business_finish_num, business_fail_num))
    print(numOfBusiness)
