from Defination import *
from Position import Orbit_Info
from math import sqrt, pi
from Satellite import Satellite


class Orbit:
    def __init__(self):
        self.ob = Orbit_Info()  # 轨道参数
        self.sat_in_orbit = []  # 轨道内卫星
        self.con_id = 0
        self.orbit_id = 0
        self.orbit_radius = SAT_HEIGHT  # 轨道半径
        self.sat_num = SAT_PER_ORBIT  # 轨道内卫星数量
        self.orbit_vel = 0.0  # 轨道角速度，弧度制
        self.beam = SAT_BEAM

    def Construct_Orbit(self, cid, oid, sat_num, r=SAT_HEIGHT+EARTH_RADIUS, original_first_phi=0.0, alpha=LEAN, theta=0.0, 
                        direction=CCW, beam=SAT_BEAM):
        assert(cid>0)
        assert(oid>0)
        assert(sat_num>0)
        assert(r>=EARTH_RADIUS)
        assert(original_first_phi>=-1*pi)
        assert(original_first_phi<=pi)
        assert(alpha>=0)
        assert(alpha<=pi/2)
        assert(theta>=-1*pi)
        assert(theta<=pi)
        self.ob = Orbit_Info()
        self.sat_in_orbit = []
        self.ob.theta = theta
        self.ob.alpha = alpha
        self.ob.direction = direction
        self.con_id = cid
        self.orbit_id = oid
        self.orbit_radius = r
        self.sat_num = sat_num
        self.orbit_vel = sqrt((G_EARTH*M_EARTH)/(pow(r, 3)))
        self.beam = beam
        phi_div = 2*pi/sat_num      #相位差
        for i in range(self.sat_num):
            temp = Satellite()
            sat_id = (self.orbit_id-1)*self.sat_num+i+1 #卫星在星座内的编号
            temp.Construct_Satellite(self.con_id, self.orbit_id, i+1, sat_id, self.orbit_radius, self.orbit_vel, 
                            original_first_phi+i*phi_div, self.ob, original_first_phi+i*phi_div, 0,self.beam)
            self.sat_in_orbit.append(temp)

    def Get_Orbit_Condition(self, time):
        for sat in self.sat_in_orbit:
            sat.Get_Satellite_Condition(time)