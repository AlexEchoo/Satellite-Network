from Defination import SAT_BEAM, SAT_HEIGHT, EARTH_RADIUS
from Position import Convert_Wi_to_W0, Orbit_Info, Sphere_Position, Adjust_Lon, Convert_W0_to_We

class Satellite:
    def __init__(self):
        self.con_id = 0
        self.orbit_ID = 0
        self.sat_ID = 0 #轨道内编号
        self.ID = 0     #整个星座内的id
        self.orbit_radius = SAT_HEIGHT + EARTH_RADIUS
        self.beam = SAT_BEAM
        self.vel = 0.0
        self.original_phi = 0.0         #初始位置的轨道内相位
        self.isNorth = True
        self.user_connected = set()        #连接的用户
        self.my_ob = Orbit_Info()       #轨道参数
        self.wi_pos = Sphere_Position() #轨道面坐标系
        self.w0_pos = Sphere_Position() #静止地球坐标系（忽略自转）
        self.we_pos = Sphere_Position() #地球坐标系（地球自转），真实的坐标位置
        self.w0_pos_last_lat = 0


    def Construct_Satellite(self, cid, oid, id_in_orbit, sid, radius, vel, phi, ob, wi_lon, wi_lat, beam=SAT_BEAM):
        self.con_id = cid
        self.orbit_ID = oid
        self.sat_ID = id_in_orbit
        self.ID = sid
        self.orbit_radius = radius
        self.beam = beam
        self.vel = vel
        self.original_phi = phi
        self.my_ob = ob
        self.wi_pos.radius = self.orbit_radius
        self.wi_pos.lon = wi_lon
        self.wi_pos.lat = wi_lat
        Convert_Wi_to_W0(self.my_ob.theta,self.my_ob.alpha,self.wi_pos,self.w0_pos)
        self.we_pos = self.w0_pos

    def Get_Satellite_Condition(self, time):
        self.w0_pos_last_lat = self.w0_pos.lat
        assert(time>=0)
        self.wi_pos.lon = Adjust_Lon(self.original_phi+self.my_ob.direction*self.vel*time)
        Convert_Wi_to_W0(self.my_ob.theta,self.my_ob.alpha,self.wi_pos,self.w0_pos)
        Convert_W0_to_We(time,self.w0_pos,self.we_pos)

    # 获得卫星指定时刻的地球运动坐标
    def Get_Satellite_We_Condition(self, time)->Sphere_Position:
        assert(time>=0)
        wi_temp = Sphere_Position()
        w0_temp = Sphere_Position()
        we_temp = Sphere_Position()
        wi_temp.lat = 0
        wi_temp.radius = self.orbit_radius
        wi_temp.lon = self.original_phi+self.my_ob.direction*self.vel*time   
        Adjust_Lon(wi_temp.lon)
        Convert_Wi_to_W0(self.my_ob.theta,self.my_ob.alpha,wi_temp,w0_temp)
        Convert_W0_to_We(time,w0_temp,we_temp)
        return we_temp