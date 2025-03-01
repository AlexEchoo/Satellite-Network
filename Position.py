from Defination import *
from math import sqrt,asin,atan,acos,pi,cos,sin


class Orbit_Info:
    def __init__(self):
        self.theta = 0.0
        self.alpha = 0.0
        self.direction = CCW

class Coord:
    def __init__(self):
        self.lon = 0.0
        self.lat = 0.0

#XYZ直角坐标系
class Rectangle_Position:
    def __init__(self):
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0

#球面坐标系
class Sphere_Position:
    def __init__(self):
        self.radius = 0
        self.lon = 0.0
        self.lat = 0.0

#将轨道内坐标转化为地球静止坐标
def Convert_Wi_to_W0(theta, alpha, wi, w0):
    original_r_pos = Rectangle_Position()
    Convert_Sphere_to_Rectangle(wi,original_r_pos)
    converted_r_pos = Rectangle_Position()
    converted_r_pos.X=cos(theta)*original_r_pos.X-sin(theta)*cos(alpha)*original_r_pos.Y+sin(theta)*sin(alpha)*original_r_pos.Z
    converted_r_pos.Y=sin(theta)*original_r_pos.X+cos(theta)*cos(alpha)*original_r_pos.Y-cos(theta)*sin(alpha)*original_r_pos.Z
    converted_r_pos.Z=sin(alpha)*original_r_pos.Y+cos(alpha)*original_r_pos.Z
    Convert_Rectangle_to_Sphere(converted_r_pos,w0)

#将地球静止坐标转化为运动地球坐标
def Convert_W0_to_We(time, w0, we):
    we.radius = w0.radius
    we.lat = w0.lat
    we.lon = w0.lon-EARTH_ROTATE*time
    Adjust_Lon(we.lon)

#将球面坐标转化为直角坐标
def Convert_Sphere_to_Rectangle(sp,rp):
    rp.X = sp.radius*cos(sp.lat)*cos(sp.lon)
    rp.Y = sp.radius*cos(sp.lat)*sin(sp.lon)
    rp.Z = sp.radius*sin(sp.lat)

#将直角坐标转化为球面坐标
def Convert_Rectangle_to_Sphere(rp,sp):
    sp.radius = sqrt(rp.X*rp.X+rp.Y*rp.Y+rp.Z*rp.Z)
    sp.lat = asin(rp.Z/sp.radius)
    if rp.X>0:
        sp.lon=atan(rp.Y/rp.X)
    elif rp.X<0:
        if rp.Y>=0:
            sp.lon=atan(rp.Y/rp.X)+pi
        else:
            sp.lon=atan(rp.Y/rp.X)-pi
    else:
        sp.lon=0

#将经度调整到-pi到pi
def Adjust_Lon(lon):
    while lon>pi:
        lon-=2*pi
    while lon<-1*pi:
        lon+=2*pi
    return lon

#弧度制到角度制
def Convert_PI_to_Angle(a):
    return a/pi*180.0

#角度制到弧度制
def Convert_Angle_to_PI(a):
    return a/180.0*pi

#计算直角坐标的轨道半径
def Calc_Radius(rp):
    return sqrt(pow(rp.X,2)+pow(rp.Y,2)+pow(rp.Z,2))

#计算两个直角坐标之间的直线距离
def Calc_Rectangle_Distance(rp1, rp2):
    return sqrt(pow(rp1.X-rp2.X,2)+pow(rp1.Y-rp2.Y,2)+pow(rp1.Z-rp2.Z,2))

#计算两个球面坐标之间的直线距离
def Calc_Sphere_Distance(sp1, sp2):
    rp1 = Rectangle_Position()
    rp2 = Rectangle_Position()
    Convert_Sphere_to_Rectangle(sp1,rp1)
    Convert_Sphere_to_Rectangle(sp2,rp2)
    return Calc_Rectangle_Distance(rp1,rp2)

#计算两个直角坐标之间的方位角
def Calc_Rectangle_Azimuth(rp1, rp2):
    aa = Calc_Rectangle_Distance(rp1,rp2)
    bb = Calc_Radius(rp1)
    cc = Calc_Radius(rp2)
    return acos((pow(bb,2)+pow(cc,2)-pow(aa,2))/(2*bb*cc))

#计算两个球面坐标之间的方位角
def Calc_Sphere_Azimuth(sp1, sp2):
    return acos(sin(sp1.lat)*sin(sp2.lat)+cos(sp1.lat)*cos(sp2.lat)*cos(sp1.lon-sp2.lon))

#通过终端高度，卫星高度，终端仰角计算方位角
def Calc_Elevation_Azimuth(rs, ru, elevation):
    return acos(ru*cos(elevation)/rs)-elevation

#计算两个球面坐标之间的仰角
def Calc_Sphere_Elevation(sp1, sp2):
    azimuth = Calc_Sphere_Azimuth(sp1,sp2)
    if azimuth==0:
        return pi/2
    if sp1.radius>sp2.radius:
        return atan((sp1.radius*cos(azimuth)-sp2.radius)/sp1.radius/sin(azimuth))
    else:
        return atan((sp2.radius*cos(azimuth)-sp1.radius)/sp2.radius/sin(azimuth))

#计算两个直角坐标之间的仰角
def Calc_Rectangle_Elevation(rp1, rp2):
    aa = Calc_Sphere_Distance(rp1,rp2)
    bb = Calc_Radius(rp1)
    cc = Calc_Radius(rp2)
    azimuth = acos((pow(bb,2)+pow(cc,2)-pow(aa,2))/(2*bb*cc))
    if aa>bb:
        return atan((aa*cos(azimuth)-bb)/aa/sin(azimuth))
    else:
        return atan((bb*cos(azimuth)-aa)/bb/sin(azimuth))

def Calc_Angle_Cos(rp1, rp2, rp3):
    prod = (rp2.X-rp1.X)*(rp3.X-rp1.X)+(rp2.Y-rp1.Y)*(rp3.Y-rp1.Y)+(rp2.Z-rp1.Z)*(rp3.Z-rp1.Z)
    AB2 = pow((rp2.X-rp1.X),2)+pow((rp2.Y-rp1.Y),2)+pow((rp2.Z-rp1.Z),2)
    AC2 = pow((rp3.X-rp1.X),2)+pow((rp3.Y-rp1.Y),2)+pow((rp3.Z-rp1.Z),2)
    res = prod/sqrt(AB2*AC2)
    return res