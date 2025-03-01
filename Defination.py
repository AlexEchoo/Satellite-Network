from math import pi

# 卫星轨道参数--倾斜轨
ORBIT_NUM = 16           # 卫星网络默认轨道数量
SAT_PER_ORBIT = 14      # 卫星网络默认每轨道卫星数量
SAT_HEIGHT = 1150000     # 卫星默认高度
LEAN = 50 / 180.0 * pi    # 轨道倾角
PHASE = 0  # 轨道相位因子
FIRST_PHI = 2.0 * PHASE * pi / (ORBIT_NUM * SAT_PER_ORBIT)           # 相邻轨道之间第一号卫星的纬度差
THETA = 2 * pi / ORBIT_NUM          # 升交点赤经差，轨道与赤道交点的经度差值
CCW = True              # 逆时针旋转方向
CW = False              # 顺时针旋转方向
TYPE_PI = 1             # pi星座，有反向缝
TYPE_2PI = 2            # 2pi星座，无反向缝

# # 卫星轨道参数--近极轨
# ORBIT_NUM = 6            # 卫星网络默认轨道数量
# SAT_PER_ORBIT = 10       # 卫星网络默认每轨道卫星数量
# SAT_HEIGHT = 1175000     # 卫星默认高度
# LEAN = 86.5 / 180.0 * pi    # 轨道倾角
# PHASE = 0  # 轨道相位因子
# FIRST_PHI = 2.0 * PHASE * pi / (ORBIT_NUM * SAT_PER_ORBIT)           # 相邻轨道之间第一号卫星的纬度差
# THETA = pi / ORBIT_NUM          # 升交点赤经差，轨道与赤道交点的经度差值
# CCW = True              # 逆时针旋转方向
# CW = False              # 顺时针旋转方向
# TYPE_PI = 1             # pi星座，有反向缝
# TYPE_2PI = 2            # 2pi星座，无反向缝

# # 卫星轨道参数--大规模倾斜轨
# ORBIT_NUM = 27          # 卫星网络默认轨道数量
# SAT_PER_ORBIT = 40     # 卫星网络默认每轨道卫星数量
# SAT_HEIGHT = 1150000     # 卫星默认高度
# LEAN = 50 / 180.0 * pi    # 轨道倾角
# PHASE = 0  # 轨道相位因子
# FIRST_PHI = 2.0 * PHASE * pi / (ORBIT_NUM * SAT_PER_ORBIT)           # 相邻轨道之间第一号卫星的纬度差
# THETA = 2 * pi / ORBIT_NUM          # 升交点赤经差，轨道与赤道交点的经度差值
# CCW = True              # 逆时针旋转方向
# CW = False              # 顺时针旋转方向
# TYPE_PI = 1             # pi星座，有反向缝
# TYPE_2PI = 2            # 2pi星座，无反向缝

# 接入网参数
ACCESS_DATA_RATE = 4000   # 4Gbps，单位Mbps

# 终端参数
SAT_BEAM = ACCESS_DATA_RATE/5                   # 卫星默认波束数量
USER_HEIGHT = 0                 # 终端默认高度
USER_ELEVATION = pi/180.0*5    # 终端默认仰角

# 地球参数
EARTH_RADIUS = 6.370856e+6  # 地球半径，单位米
EARTH_ROTATE = 0.000072918  # 地球自转角速度，弧度制

# 计算所需常数
G_EARTH = 6.67408e-11   # 计算角速度所需
M_EARTH = 5.965e24      # 计算角速度所需

# 承载网网络参数
THRESHOLD = pi/180.0*70 # 极轨断开
METRIC = 1              # 路由条目默认metric
BANDWIDTH = 3000       # 带宽3Gbps，单位Mbps
BEARER_LOSS = 0.00001

# QoS分解算法--接入网利用率阈值
Carrier_threshold = 0.6

# 调试参数
TOPO_LOG_LEVEL = 0       # 是否输出log文件
NET_LOG_LEVEL = 6         # 
HO_LOG_LEVEL = 2

SINGLE_FIRST = 2
COST_FIRST = 1
BANDWIDTH_FIRST = 0

queue_maxsize = 100

ACCESS_LOSS_BEST = 0.00003
ACCESS_JITTER_BEST = 1.0
ACCESS_Processing_delay_BEST = 1.0


