from Defination import *
from Orbit import Orbit
from Position import Adjust_Lon


class Constellation:        # 星座

    def __init__(self):
        self.ID = 0     #星座id
        self.orbit_num = ORBIT_NUM          #星座中轨道数量
        self.sat_per_orbit = SAT_PER_ORBIT  #每个轨道中卫星数量
        self.height = SAT_HEIGHT            #距离地面高度
        self.lean = LEAN                    #轨道倾角
        self.first_phi = FIRST_PHI          #轨道1与轨道2之间第一个节点纬度相差的数值
        self.theta = THETA                  #升交点赤经差
        self.type = TYPE_2PI                 #星座类型
        self.threshold = THRESHOLD          #高纬度链路断开阈值
        self.beam = SAT_BEAM                #每颗卫星波束数量
        self.rotate_direction = CCW         #轨道旋转方向
        self.orbit_sat = []                 #轨道数据结构

    #按照轨道数据结构构建星座
    def Construct_Constellation(self, cid, orbit, sat, height, phi, lean, theta,
                                ctype, threshold=THRESHOLD, beam=SAT_BEAM):
        self.ID = cid
        self.orbit_num = orbit
        self.sat_per_orbit = sat
        self.height = height
        self.lean = lean
        self.first_phi = phi
        self.theta = theta
        self.type = ctype
        self.threshold = threshold
        self.beam = beam
        for i in range(self.orbit_num):
            temp = Orbit()
            self.orbit_sat.append(temp)
            orbit_theta = Adjust_Lon(i*self.theta)   #当前轨道升交点赤经差
            orbit_lean = self.lean
            original_phi = Adjust_Lon(i*self.first_phi)
            orbit_radius = self.height+EARTH_RADIUS
            self.orbit_sat[i].Construct_Orbit(self.ID,i+1,self.sat_per_orbit,orbit_radius,original_phi,
                                                orbit_lean,orbit_theta,self.rotate_direction,self.beam)

    def Get_Constellation_Condition(self, time):
        for orbit in self.orbit_sat:
            orbit.Get_Orbit_Condition(time)
