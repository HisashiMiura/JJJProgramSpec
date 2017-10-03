
# coding: utf-8

# In[1]:

import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
from enum import Enum
from collections import namedtuple
from collections import OrderedDict


# # I 外皮性能の計算方法 (関数)

# ## 1) はじめに

# 本計算は第3章「暖冷房負荷と外皮性能」第2章「外皮性能」にもとづく。

# ## 2) 型について

# ### 地域の区分に関する列挙型

# 地域の区分8地域を表す。

# In[2]:

class Region(Enum):
    Division1 = 1
    Division2 = 2
    Division3 = 3
    Division4 = 4
    Division5 = 5
    Division6 = 6
    Division7 = 7
    Division8 = 8


# ### Orientation 型 (簡易法のみに使用)

# 主開口方位から時計回りに0°、90°、180°、270°を表す。省エネ基準における簡易評価法においては、主開口方位は南西と固定されているため、順に、南西、北西、北東、南東の意味と同じである。

# In[3]:

Orientation = namedtuple('Orientation', 'D0 D90 D180 D270')


# ### 方位に関する列挙型

# 基準で扱う方位は8方位と上面・下面である。

# In[4]:

class Direction(Enum):
    S  = 0
    SW = 1
    W  = 2
    NW = 3
    N  = 4
    NE = 5
    E  = 6
    SE = 7
    top = 8
    bottom = 9


# ### 隣接空間に関する列挙型

# 隣接空間の種類は付録Bで定められている。  
# ここでは、以下のようにネーミングする。  
# * External: 「外気」「外気に通じる空間」
# * SemiExternal: 「外気に通じていない空間」「外気に通じる床裏」
# * Internal: 「住戸及び住戸と同様の熱的環境の空間」「外気に通じていない床裏」

# In[5]:

class AdjacentSpaceType(Enum):
    External     = 0
    SemiExternal = 1
    Internal     = 2


# ## 3-1) 関数(共通)

# ### 熱損失係数(換気による熱損失を含まない)

# #### 定義

# 熱損失係数(換気による熱損失を含まない)$Q'$(W/m<sup>2</sup>K)は式(1)に基づく。

# In[6]:

def get_Q_dash(U_A, r_env):
    # U_A: 外皮平均熱損失係数(W/m2K)
    # r_env: 床面積の合計に対する外皮の部位の面積の合計の比
    return U_A * r_env


# #### 説明

# 外皮平均熱貫流率は、単位温度差あたりの熱損失量 $q$ を床面積の合計で除した値である。  
# $ U_A = q \div A_f $  
# 熱損失係数は、単位温度差あたりの熱損失量 $q$ を外皮の部位の面積の合計で除した値である。  
# $ Q' = q \div A_{env} $  
# 床面積の合計に対する外皮の部位の面積の合計の比 $r_{env}$ は、 $U_A$ 値を $Q'$ に変換する係数である。

# In[7]:

get_Q_dash( 0.87 , 307.51/120.08 )


# ### 日射取得係数

# #### 定義

# 暖房期の日射取得係数($\mu_H$)は式(2)に基づく。

# In[8]:

def get_Mu_H(eta_A_H, r_env):
    # eta_A_H: 暖房期の日射取得係数(-)
    # r_env: 床面積の合計に対する外皮の部位の面積の合計の比
    return eta_A_H * r_env / 100


# 冷房期の日射取得係数($\mu_C$)は式(3)に基づく。

# In[9]:

def get_Mu_C(eta_A_C, r_env):
    # eta_A_C: 冷房期の日射取得係数(-)
    # r_env: 床面積の合計に対する外皮の部位の面積の合計の比
    return eta_A_C * r_env / 100


# #### 説明

# In[10]:

get_Mu_H(4.3, 307.51/120.08 )


# In[11]:

get_Mu_C(2.8, 307.51/120.08 )


# ## 3-2) 関数(当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法)

# ### 外皮平均熱貫流率

# #### 定義

# 外皮平均熱貫流率($U_A$)は式(4)に基づく。得られた値の100分の1未満の端数は切り上げ、小数第2位までの値とする。

# 熱橋は、長さ・線熱損失係数・暖房期の日射熱取得率・冷房期の日射熱取得率・方位1と方位2・隣接空間の種類をもつ。熱橋は多くの場合、隅角部等に発生し、2方位に面する場合が多いため、方位1と方位2を持つことにする。方位1と方位2に順番は無い。また、T型熱橋など、接続する部位が同じ方位を持つ場合は、方位1と方位2に同じ方位を入力すること。  
# ただし、熱橋の日射熱取得率は、本来であれば、  
# $\begin{align} \eta = \gamma \times 0.034 \times \frac{ L \times \psi }{ A } \end{align}$  
# で表されるのに対し、  
# $\begin{align} \eta' = \gamma \times 0.034 \times \psi \end{align} $  
# で表されることとする。  
# ここで、  
# $\eta$: 日射熱取得率(-)  
# $\eta'$: 熱橋の日射熱取得率(m)  
# 従って、$ m $ 値(m<sup>2</sup>)の計算において、仕様書によると、  
# $\begin{align} m = A \times \eta \times \nu \end{align} $  
# ではなく、  
# $\begin{align} m = L \times \eta' \times \nu \end{align} $  
# で計算される。

# In[12]:

def get_UA( U_parts, psi_parts, A_env ):
    # U_parts: 外皮の部位 [ U_part の配列 ]
    #          U_part: 外皮の部位 ( 面積(m2), 熱貫流率(W/m2K), 温度差係数(-) )
    # psi_parts: 熱橋等 [ psi_part の配列 ]
    #            psi_part: 熱橋等 ( 長さ(m), 線熱貫流率(W/mK), 温度差係数(-) )
    # A_env: 外皮の部位の面積の合計(m2)
    return Decimal( (   sum([U_part[0]   * U_part[1]   * U_part[2]   for U_part   in U_parts  ])
                      + sum([psi_part[0] * psi_part[1] * psi_part[2] for psi_part in psi_parts])
                    ) / A_env
                  ).quantize( Decimal('0.00'), rounding = 'ROUND_UP' )


# #### 説明

# 例題として、以下の住宅で計算する。  
# * 4m × 4m × 2.5m の基礎断熱住宅（屋根 16 m<sup>2</sup>、 壁 10 m<sup>2</sup> が4枚、 地盤の周囲は 4m が4か所）
# * $U$値は1.0
# * $\psi$値は1.8
# * 温度差係数は1.0  
# 外皮の面積の合計には、熱損失はゼロである土間床も含まれる。

# In[13]:

# 配列の要素は、Uに関しては(壁,壁,壁,壁,天井)、Lに関しては(地盤周囲 × 4)
get_UA( [(10.0, 1.0, 1.0), (10.0, 1.0, 1.0), (10.0, 1.0, 1.0), (10.0, 1.0, 1.0), (16.0, 1.0, 1.0)],
     [(4.0, 1.8, 1.0), (4.0, 1.8, 1.0), (4.0, 1.8, 1.0)],
     72.0 )


# ### 暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率

# #### 定義

# 暖房期の平均日射熱取得率($\eta_{A,H}$)は式(5)に基づく。得られた値の10分の1未満の端数は切り下げ、小数第1位までの値とする。

# In[14]:

def get_eta_A_H(parts, partHBs, A_env):
    # parts: 外皮の部位 [part の配列]
    #        part: 外皮の部位 ( 面積(m2), 暖房期の日射熱取得率(-), 暖房期の方位係数(-) )
    # partHBs: 熱橋 [partHB の配列]
    #          partHB: 熱橋 ( 長さ(m), 暖房期の熱橋の日射熱取得率(m), 暖房期の方位係数1(-), 暖房期の方位係数2(-) )
    # A_env: 外皮の部位の面積の合計(m2)
    return Decimal( (   sum([ part[0]   * part[1]   * part[2]                     for part   in parts   ])
                      + sum([ partHB[0] * partHB[1] * ( partHB[2] + partHB[3] )/2 for partHB in partHBs ])
                    ) / A_env * 100
                   ).quantize(Decimal('0.0'), rounding = 'ROUND_DOWN')


# 冷房期の平均日射熱取得率($\eta_{C,H}$)は式(6)に基づく。得られた値の10分の1未満の端数は切り上げ、小数第1位までの値とする。

# In[15]:

def get_eta_A_C(parts, partHBs, A_env):
    # parts: 外皮の部位 [part の配列]
    #        part: 外皮の部位 ( 面積(m2), 冷房期の日射熱取得率(-), 冷房期の方位係数(-) )
    # partHBs: 熱橋 [partHB の配列]
    #          partHB: 熱橋 ( 長さ(m), 冷房期の熱橋の日射熱取得率(m), 冷房期の方位係数1(-), 冷房期の方位係数2(-) )
    # A_env: 外皮の部位の面積の合計(m2)
    return Decimal( (   sum([ part[0]   * part[1]   * part[2]                     for part   in parts   ])
                      + sum([ partHB[0] * partHB[1] * ( partHB[2] + partHB[3] )/2 for partHB in partHBs ])
                    ) / A_env * 100 
                  ).quantize(Decimal('0.0'), rounding = 'ROUND_UP')


# #### 説明

# 例題として、以下の住宅で計算する。  
# * 4m × 4m × 2.5m の基礎断熱住宅（屋根 16 m<sup>2</sup>、 壁 10 m<sup>2</sup> が4枚）
# * $\eta$値は暖房期・冷房期ともに0.034  
# * $\eta'$値は暖房期・冷房期ともに0.05
# * 方位係数は6地域の東西南北とする。つまり、暖房期は、東(0.579)、西(0.523)、南(0.936)、北(0.261)、冷房期は、東(0.512)、西(0.504)、南(0.434)、北(0.341)、上面は暖房期・冷房期ともに1.0

# In[16]:

# 配列の要素は、(壁,壁,壁,壁,天井)
get_eta_A_H( [ (10.0, 0.034, 0.579), (10.0, 0.034, 0.523), (10.0, 0.034, 0.936), (10.0, 0.034, 0.261),
               (16.0, 0.034, 1.0) ], 
             [ (2.5, 0.05, 0.579, 0.523), (2.5, 0.05, 0.523, 0.936), (2.5, 0.05, 0.936, 0.261), (2.5, 0.05, 0.261, 0.579),
               (2.0, 0.05, 0.579, 1.0), (2.0, 0.05, 0.523, 1.0), (2.0, 0.05, 0.936, 1.0), (2.0, 0.05, 0.261, 1.0) ],
             72.0 )


# In[17]:

# 配列の要素は、(壁,壁,壁,壁,天井)
get_eta_A_C( [ (10.0, 0.034, 0.512), (10.0, 0.034, 0.504), (10.0, 0.034, 0.434), (10.0, 0.034, 0.341),
               (16.0, 0.034, 1.0) ],
             [ (2.5, 0.05, 0.512, 0.504), (2.5, 0.05, 0.504, 0.434), (2.5, 0.05, 0.434, 0.341), (2.5, 0.05, 0.341, 0.512),
               (2.0, 0.05, 0.512, 1.0), (2.0, 0.05, 0.523, 1.0), (2.0, 0.05, 0.936, 1.0), (2.0, 0.05, 0.261, 1.0) ],
             72.0 )


# ### 床面積の合計に対する外皮の部位の面積の合計の比

# #### 定義

# 床面積の合計に対する外皮部位比($r_{env}$)は式(7)に基づく。

# In[18]:

def get_r_env(A_env, A_A):
    # A_env: 外皮の部位の面積の合計(m2)
    # A_A: 当該住戸の床面積の合計(m2)
    return A_env / A_A


# #### 説明

# In[19]:

get_r_env( 307.51, 120.08 )


# ### 外皮の部位の面積の合計

# #### 定義

# 外皮の部位の面積の合計($A_{env}$)は式(8)に基づく。

# In[20]:

def get_A_env(A, A_EF):
    # A: 外皮の部位(一般部位又は開口部)の面積 [配列]
    # A_EF: 土間床等の面積 [配列]
    return sum(A) + sum(A_EF)


# #### 説明

# 例題として、以下の住宅で計算する。  
# * 4m × 4m × 2.5m の基礎断熱住宅（屋根 16 m<sup>2</sup>、 壁 10 m<sup>2</sup> が4枚、 地盤 16 m<sup>2</sup>）

# In[21]:

get_A_env( [10.0, 10.0, 10.0, 10.0, 16.0], [16.0] )


# ## 3-3) 関数(当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法)

# ### 外皮平均熱貫流率(簡易)

# #### 定義

# 外皮平均熱貫流率$U_A$は、式(9a)及び式(9b)に基づく。得られた値の100分の1未満の端数は切り上げ、小数第2位までの値とする。

# In[22]:

def get_simple_U_A (A_roof, A_wall, A_door, A_wnd, A_IF, A_base, A_base_IS, A_base_d, A_base_d_IS, L_prm, L_prm_IS, L_prm_d, L_prm_d_IS, H_roof, H_wall, H_door, H_wnd, H_floor, H_base_OS, H_base_IS, H_prm_OS, H_prm_IS, U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d, A_env ):
    # A_roof: 標準住戸における屋根又は天井の面積 (m2)
    # A_wall: 標準住戸における壁の面積 (m2) (E0,E90,E180,E270)
    # A_door: 標準住戸におけるドアの面積 (m2) (E0,E90,E180,E270)
    # A_wnd: 標準住戸における窓の面積 (m2) (E0,E90,E180,E270)
    # A_IF: 標準住戸における床断熱した床の面積 (m2)
    # A_base: 標準住戸における玄関等を除く基礎の面積 (m2) (E0,E90,E180,E270)
    # A_base_IS: 標準住戸における床下に面した玄関等を除く基礎の面積 (m2)
    # A_base_d: 標準住戸における玄関等の基礎の面積 (m2) (E0,E90,E180,E270)
    # A_base_d_IS: 標準住戸における床下に面した玄関等の基礎の面積 (m2)
    # L_prm: 標準住戸における玄関等を除く土間床等の外周部の長さ (m) (E0,E90,E180,E270)
    # L_prm_IS: 標準住戸における床下に面した玄関等を除く土間床等の外周部の長さ (m)
    # L_prm_d: 標準住戸における玄関等の土間床等の外周部の長さ (m) (E0,E90,E180,E270)
    # L_prm_d_IS: 標準住戸における床下に面した玄関等の土間床等の外周部の長さ (m)
    # H_roof: 屋根又は天井の温度差係数
    # H_wall: 壁の温度差係数
    # H_door: ドアの温度差係数
    # H_wnd: 窓の温度差係数
    # H_floor: 床の温度差係数
    # H_base_OS: 外気に面した基礎の温度差係数
    # H_base_IS: 床下に面した基礎の温度差係数
    # H_prm_OS: 外気に面した土間床等の周辺部の温度差係数
    # H_prm_IS: 床下に面した土間床等の周辺部の温度差係数
    # U_roof: 屋根又は天井の熱貫流率(W/m2K)
    # U_wall: 壁の熱貫流率(W/m2K)
    # U_door: ドアの熱貫流率(W/m2K)
    # U_wnd: 窓の熱貫流率(W/m2K)
    # U_floor: 床の熱貫流率(W/m2K)
    # U_base: 玄関等を除く基礎の熱貫流率(W/m2K)
    # U_base_d: 玄関等の基礎の熱貫流率(W/m2K)
    # psi_prm: 玄関等を除く土間床等の外周部の熱貫流率(W/mK)
    # psi_prm_d: 玄関等を除く土間床等の熱貫流率(W/mK)
    # A_env: 標準住戸における外皮の部位の面積の合計(m2)

    q = A_roof * H_roof * U_roof       + sum(A_wall) * H_wall * U_wall       + sum(A_door) * H_door * U_door       + sum(A_wnd) * H_wnd * U_wnd       + A_IF * H_floor * U_floor       + ( sum(A_base) * H_base_OS + A_base_IS * H_base_IS ) * U_base       + ( sum(A_base_d) * H_base_OS + A_base_d_IS * H_base_IS ) * U_base_d       + ( sum(L_prm) * H_prm_OS + L_prm_IS * H_prm_IS ) * psi_prm       + ( sum(L_prm_d) * H_prm_OS + L_prm_d_IS * H_prm_IS ) * psi_prm_d        
    
    return Decimal(q / A_env).quantize(Decimal('0.00'), rounding='ROUND_UP')


# #### 説明

# 面積・温度差係数は、後述するように、床断熱住宅と基礎断熱住宅でそれぞれデフォルト値が定義されている。例として、ここでは床断熱住宅の値を用いる。  
# 部位の熱貫流率・線熱貫流率の値は、全て1.0とする。

# In[23]:

get_simple_U_A (50.85, Orientation(30.47, 22.37, 47.92, 22.28), Orientation(0.0, 1.89, 1.62, 0.0), Orientation(22.69, 2.38, 3.63, 4.37), 45.05, Orientation(0.00, 0.91, 0.91, 0.00), 1.82, Orientation(0.00, 0.33, 0.25, 0.00), 0.57, Orientation(0.00, 1.82, 1.82, 0.00), 3.64, Orientation(0.00, 1.82, 1.37, 0.00), 3.19, 1.0, 1.0, 1.0, 1.0, 0.7, 1.0, 0.7, 1.0, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 266.10 )


# ### 方位係数(簡易)

# 主たる方位を南西とする。従って、  
# * 主たる方位から  0度 = 南西
# * 主たる方位から 90度 = 北西
# * 主たる方位から180度 = 北東
# * 主たる方位から270度 = 南東

# In[24]:

def get_simple_Orientation_value_from_Direction(DirectionValue):
    # DirectionValue: [(S,SW,W,NW,N,NE,E,SE,top,bottom)の辞書型]
    return Orientation(
        D0   = DirectionValue[Direction.SW],
        D90  = DirectionValue[Direction.NW],
        D180 = DirectionValue[Direction.NE],
        D270 = DirectionValue[Direction.SE]
    )


# ### 暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率(簡易)

# #### 定義

# 暖房期の平均日射熱取得率($\eta_{A,H}$)は式(10a)及び式(10b)に基づく。得られた値の10分の1未満の端数は切り下げ、小数第1位までの値とする。

# In[25]:

def get_simple_eta_A_H(A_roof, A_wall, A_door, A_wnd, A_base, A_base_d, nu_H_top, nu_H, eta_H_roof, eta_H_wall, eta_H_door, eta_H_wnd, eta_H_base, eta_H_base_d, A_env):
    # A_roof: 標準住戸における屋根又は天井の面積(m2)
    # A_wall: 標準住戸における壁の面積(m2) (E0,E90,E180,E270)
    # A_door: 標準住戸におけるドアの面積(m2) (E0,E90,E180,E270)
    # A_wnd: 標準住戸における窓の面積(m2) (E0,E90,E180,E270)
    # A_base: 標準住戸における玄関等を除く基礎の面積(m2) (E0,E90,E180,E270)
    # A_base_d: 標準住戸における玄関の基礎の面積(m2) (E0,E90,E180,E270)
    # nu_H_top; 上面に面した外皮の部位の暖房期の方位係数
    # nu_H: 外皮の部位の暖房期の方位係数 (E0,E90,E180,E270)
    # eta_H_roof: 屋根又は天井の暖房期の日射熱取得率
    # eta_H_wall: 壁の暖房期の日射熱取得率
    # eta_H_door: ドアの暖房期の日射熱取得率
    # eta_H_wnd: 窓の暖房期の日射熱取得率 (E0,E90,E180,E270)
    # eta_H_base: 玄関等を除く基礎の暖房期の日射熱取得率
    # eta_H_base_d: 玄関等の基礎の暖房期の日射熱取得率
    # A_env: 標準住戸における外皮の部位の面積の合計(m2)
    m_H = A_roof * nu_H_top * eta_H_roof         + ( np.array(A_wall) * np.array(nu_H) ).sum() * eta_H_wall         + ( np.array(A_door) * np.array(nu_H) ).sum() * eta_H_door         + ( np.array(A_wnd) * np.array(nu_H) * np.array(eta_H_wnd) ).sum()         + ( np.array(A_base) * np.array(nu_H) ).sum() * eta_H_base         + ( np.array(A_base_d) * np.array(nu_H) ).sum() * eta_H_base_d

    return Decimal( m_H / A_env * 100 ).quantize(Decimal('0.0'), rounding = 'ROUND_DOWN')


# In[26]:

def get_simple_eta_A_C(A_roof, A_wall, A_door, A_wnd, A_base, A_base_d, nu_C_top, nu_C, eta_C_roof, eta_C_wall, eta_C_door, eta_C_wnd, eta_C_base, eta_C_base_d, A_env):
    # A_roof: 標準住戸における屋根又は天井の面積(m2)
    # A_wall: 標準住戸における壁の面積(m2) (E0,E90,E180,E270)
    # A_door: 標準住戸におけるドアの面積(m2) (E0,E90,E180,E270)
    # A_wnd: 標準住戸における窓の面積(m2) (E0,E90,E180,E270)
    # A_base: 標準住戸における玄関等を除く基礎の面積(m2) (E0,E90,E180,E270)
    # A_base_d: 標準住戸における玄関の基礎の面積(m2) (E0,E90,E180,E270)
    # nu_C_top; 上面に面した外皮の部位の冷房期の方位係数
    # nu_C: 外皮の部位の冷房期の方位係数 (E0,E90,E180,E270)
    # eta_C_roof: 屋根又は天井の冷房期の日射熱取得率
    # eta_C_wall: 壁の冷房期の日射熱取得率
    # eta_C_door: ドアの冷房期の日射熱取得率
    # eta_C_wnd: 窓の冷房期の日射熱取得率 (E0,E90,E180,E270)
    # eta_C_base: 玄関等を除く基礎の冷房期の日射熱取得率
    # eta_C_base_d: 玄関等の基礎の冷房期の日射熱取得率
    # A_env: 標準住戸における外皮の部位の面積の合計(m2)
    m_C = A_roof * nu_C_top * eta_C_roof         + ( np.array(A_wall) * np.array(nu_C) ).sum() * eta_C_wall         + ( np.array(A_door) * np.array(nu_C) ).sum() * eta_C_door         + ( np.array(A_wnd) * np.array(nu_C) * np.array(eta_C_wnd) ).sum()         + ( np.array(A_base) * np.array(nu_C) ).sum() * eta_C_base         + ( np.array(A_base_d) * np.array(nu_C) ).sum() * eta_C_base_d

    return Decimal( m_C / A_env * 100 ).quantize(Decimal('0.0'), rounding = 'ROUND_UP')


# #### 説明

# 面積は、後述するように、床断熱住宅と基礎断熱住宅でそれぞれデフォルト値が定義されている。例として、ここでは床断熱住宅の値を用いる。  
# * 非透明部位の日射熱取得率は0.34とし、透明部位の日射熱取得率は0.5とする。  
# * 線熱貫流率の値は、全て1.0とする。
# * 方位係数は6地域の値とし、方位は、順に、南西・北西・北東・南東の方位係数を使用した。

# In[27]:

get_simple_eta_A_H(50.85, Orientation(30.47, 22.37, 47.92, 22.28), Orientation(0.0, 1.89, 1.62, 0.0), Orientation(22.69, 2.38, 3.63, 4.37), Orientation(0.00, 0.91, 0.91, 0.00), Orientation(0.00, 0.33, 0.25, 0.00), 1.0, Orientation(0.763, 0.317, 0.325, 0.833), 0.034, 0.034, 0.034, Orientation(0.5, 0.5, 0.5, 0.5), 0.034, 0.034, 266.10)


# In[28]:

get_simple_eta_A_C(50.85, Orientation(30.47, 22.37, 47.92, 22.28), Orientation(0.0, 1.89, 1.62, 0.0), Orientation(22.69, 2.38, 3.63, 4.37), Orientation(0.00, 0.91, 0.91, 0.00), Orientation(0.00, 0.33, 0.25, 0.00), 1.0, Orientation(0.491, 0.427, 0.431, 0.498), 0.034, 0.034, 0.034, Orientation(0.5, 0.5, 0.5, 0.5), 0.034, 0.034, 266.10)


# ### 床面積の合計に対する外皮の部位の面積の合計の比

# #### 定義

# 床面積の合計に対する外皮の部位の面積の合計の比 $r_{env}$は式(12)に基づく。この式は、式(7)と同じである。

# ### 標準住戸の種類

# #### 定義

# 標準住戸の面積は、住宅の種類（「床断熱住戸」又は「基礎断熱住戸」）に依存する。これらに、床断熱住戸と基礎断熱住戸の両方の条件を満たす住戸（「床断熱と基礎断熱の併用住戸」という。）を加えて、住宅の種類を定義する。

# In[29]:

class simple_HouseType(Enum):
    floor_ins          = 0
    base_ins           = 1
    floor_and_base_ins = 2


# ### 標準住戸における外皮の部位の面積及び土間床等の外周部の長さ等

# #### 定義

# 標準住戸における外皮の部位の面積及び土間床等の外周部の長さ等は、表3に基づく。

# In[30]:

class simple_Area_and_Length:
    
    def __init__(self, house_type):
        # house_type: HouseType 列挙型

        if house_type == simple_HouseType.floor_and_base_ins:
            rase("Not Defined")

        # 外皮の部位の面積の合計(m2)
        self.env    = [ 266.10, 275.69 ][house_type.value]

        # 延べ床面積の合計(m2)
        self.A      = 90.0
        
        # 屋根又は天井の面積(m2)
        self.roof   = 50.85
        
        # 壁の面積(m2)
        self.wall   = Orientation( 30.47, 22.37, 47.92, 22.28 )

        # ドアの面積(m2)
        self.door   = Orientation( 0.00, 1.89, 1.62, 0.00 )

        # 窓の面積(m2) 
        self.wnd    = Orientation( 22.69, 2.38, 3.63, 4.37 )
        
        # 床（床断熱した床）の面積(m2)
        self.floor  = [ 45.05, 0.0 ][house_type.value]

        # 玄関等を除く基礎の面積(m2)
        self.base   = [ Orientation(  0.00, 0.91, 0.91, 0.00 ),
                        Orientation(  5.30, 1.48, 4.62, 2.40 ) ][house_type.value]
        self.base_IS = [ 1.82, 0.00 ][house_type.value]

        # 玄関等の基礎の面積(m2)
        self.base_d = [ Orientation(  0.00, 0.33, 0.25, 0.00 ),
                        Orientation(  0.00, 0.33, 0.25, 0.00 )][house_type.value]
        self.base_d_IS = [ 0.57, 0.00 ][house_type.value]
        
        # 玄関等を除く土間床等の外周部の長さ(m)        
        self.prm = [ Orientation(  0.00, 1.82, 1.82, 0.00 ),
                     Orientation( 10.61, 2.97, 9.24, 4.79 ) ][house_type.value]
        self.prm_IS = [ 3.64, 0.00 ][house_type.value]
        
        # 玄関等の土間床等の外周部の長さ(m)
        self.prm_d  = [ Orientation(  0.00, 1.82, 1.37, 0.00 ),
                        Orientation(  0.00, 1.82, 1.37, 0.00 ) ][house_type.value]
        self.prm_d_IS = [ 3.19, 0.00 ][house_type.value]        


# #### 説明

# 値の確認。

# 床断熱住戸の場合

# In[31]:

simple_Area_and_Length(simple_HouseType.floor_ins).__dict__


# 基礎断熱住戸の場合

# In[32]:

simple_Area_and_Length(simple_HouseType.base_ins).__dict__


# ### 床断熱住宅か基礎断熱住宅の判断

# #### 定義

# 「9.5 標準住戸における外皮の部位の面積及び土間床等の外周部の長さ等」において、「床断熱住戸」及び「基礎断熱住戸」のどちらにも該当する場合、両方の場合で外皮平均熱貫流率を計算し、値が大きい方の場合を採用することとなっている。

# In[33]:

def judge_simple_house_type(floor_ins_U_A, base_ins_U_A):
    # floor_ins_U_A: 床断熱住戸のUA値(W/m2K)
    # base_ins_U_A: 基礎熱住戸のUA値(W/m2K)
    if floor_ins_U_A > base_ins_U_A:
        return (floor_ins_U_A, simple_HouseType.floor_ins)
    else:
        return (base_ins_U_A, simple_HouseType.base_ins)


# #### 説明

# 床断熱住戸の方のUA値が大きい場合。

# In[34]:

judge_simple_house_type(2.2, 1.1)


# 基礎熱住戸の方のUA値が大きい場合。

# In[35]:

judge_simple_house_type(1.1, 2.2)


# ### 外皮の部位及び土間床等の周辺部の温度差係数

# #### 定義

# 外皮の部位及び土間床等の周辺部の温度差係数は表4に基づく。

# In[36]:

class simple_HValue:
    roof    = 1.0
    wall    = 1.0
    door    = 1.0
    wnd     = 1.0
    floor   = 0.7
    base_OS = 1.0
    base_IS = 0.7
    prm_OS  = 1.0
    prm_IS  = 0.7


# ### 外皮の部位の熱貫流率

# #### 定義

# 屋根又は天井の熱貫流率($U_{roof}$)は、「9.8.1 屋根又は天井の熱貫流率」に基づく。  
# 壁の熱貫流率($U_{wall}$)は、「9.8.2 壁の熱貫流率」に基づく。  
# ドアの熱貫流率($U_{door}$)は、「9.8.3 ドアの熱貫流率」に基づく。  
# 窓の熱貫流率($U_{wnd}$)は、「9.8.4 窓の熱貫流率」に基づく。  
# 床の熱貫流率($U_{floor}$)は、「9.8.5 床の熱貫流率」に基づく。  
# 玄関等を除く基礎の熱貫流率($U_{base}$)は、「9.8.6 玄関等を除く基礎の熱貫流率」に基づく。  
# 玄関等の基礎の熱貫流率($U_{base,d}$)は、「9.8.7 玄関等の基礎の熱貫流率」に基づく。  
# なお、窓の熱貫流率の2%ルール(床面積の2%に満たない面積の部位は除外できる。)や浴室下部の除外ルール(断熱措置がある場合)等のルールは実装しない。

# In[37]:

def get_simple_U_part(parts):
    # parts: 外皮の部位 [ part の配列 ]
    #        part: 外皮の部位 ( U値(W/m2K), H値 )
    return max ( parts, key = ( lambda part: part[0] * part[1] ) )

get_simple_U_roof   = get_simple_U_part
get_simple_U_wall   = get_simple_U_part
get_simple_U_door   = get_simple_U_part
get_simple_U_wnd    = get_simple_U_part
get_simple_U_floor  = get_simple_U_part
get_simple_U_base   = get_simple_U_part
get_simple_U_base_d = get_simple_U_part


# #### 説明

# 計算例。U値が大きい方が選択される例。

# In[38]:

get_simple_U_part([ (1.5,1.0), (2.0,1.0)] )


# 計算例。H値の違いによりU値が小さい方が選択される例。

# In[39]:

get_simple_U_part([ (1.5,1.0), (2.0,0.7)] )


# ### 土間床等の周辺部の熱貫流率

# #### 定義

# 玄関等を除く土間床等の外周部の線熱貫流率($\psi_{prm}$)は、「9.2.8 玄関等を除く土間床等の外周部の線熱貫流率」に基づく。  
# 玄関等の土間床等の外周部の線熱貫流率($\psi_{prm,d}$)は、「9.2.9 玄関等の土間床等の外周部の線熱貫流率」に基づく。  

# In[40]:

def get_simple_psi_part(parts):
    # parts: 土間床等の外周部 [ part の配列 ]
    #        part: 土間床等の外周部 ( psi値(W/mK), H値)
    return max ( parts, key = ( lambda part: part[0] * part[1] ) )

get_simple_psi_prm   = get_simple_psi_part
get_simple_psi_prm_d = get_simple_psi_part


# #### 説明

# 計算例。U値が大きい方が選択される例。

# In[41]:

get_simple_psi_part( [ (1.5,1.0), (2.0,1.0) ] )


# 計算例。H値の違いによりU値が小さい方が選択される例。

# In[42]:

get_simple_psi_part( [ (1.5,1.0), (2.0,0.7) ] )


# ### 外皮の部位(窓を除く)の日射熱取得率

# #### 定義

# 屋根又は天井の日射熱取得率($\eta_{H,roof}$・$\eta_{C,roof}$)は、屋根又は天井の熱貫流率$U_{roof}$を用いて、「9.9.1 屋根又は天井の日射熱取得率」に基づく方法で計算される。  
# 壁の日射熱取得率($\eta_{H,wall}$・$\eta_{C,wall}$)は、壁の熱貫流率$U_{wall}$を用いて、「9.9.2 壁の日射熱取得率」に基づく方法で計算される。  
# ドアの日射熱取得率($\eta_{H,door}$・$\eta_{C,door}$)は、ドアの熱貫流率$U_{door}$を用いて、「9.9.3 ドアの日射熱取得率」に基づく方法で計算される。  
# 玄関等を除く基礎の日射熱取得率($\eta_{H,base}$・$\eta_{C,base}$)は、玄関等を除く基礎の熱貫流率$U_{base}$を用いて、「9.9.5 玄関等を除く基礎の日射熱取得率」に基づく方法で計算される。  
# 玄関等の基礎の日射熱取得率($\eta_{H,base,d}$・$\eta_{C,base,d}$)は、玄関等の基礎の熱貫流率$U_{base,d}$を用いて、「9.9.6 玄関等の基礎の日射熱取得率」に基づく方法で計算される。  

# In[43]:

def get_simple_eta_H_not_wnd(U_part):
    # U_part: 外皮の部位(窓を除く)の熱貫流率(W/m2K)
    gamma_H = 1.0 # 暖房期の日除けの効果係数
    return 0.034 * U_part * gamma_H

get_simple_eta_H_roof   = get_simple_eta_H_not_wnd
get_simple_eta_H_wall   = get_simple_eta_H_not_wnd
get_simple_eta_H_door   = get_simple_eta_H_not_wnd
get_simple_eta_H_base   = get_simple_eta_H_not_wnd
get_simple_eta_H_base_d = get_simple_eta_H_not_wnd


# In[44]:

def get_simple_eta_C_not_wnd(U_part):
    # U_part: 外皮の部位(窓を除く)の熱貫流率(W/m2K)
    gamma_C = 1.0 # 冷房期の日除けの効果係数
    return 0.034 * U_part * gamma_C

get_simple_eta_C_roof   = get_simple_eta_C_not_wnd
get_simple_eta_C_wall   = get_simple_eta_C_not_wnd
get_simple_eta_C_door   = get_simple_eta_C_not_wnd
get_simple_eta_C_base   = get_simple_eta_C_not_wnd
get_simple_eta_C_base_d = get_simple_eta_C_not_wnd


# #### 説明

# 計算例。U値=1.0の場合。

# In[45]:

get_simple_eta_H_not_wnd(1.0)


# In[46]:

get_simple_eta_C_not_wnd(1.0)


# ### 窓の日射熱取得率

# #### 定義

# 窓の日射熱取得率($\eta_{H,wnd,0}$・$\eta_{H,wnd,90}$・$\eta_{H,wnd,180}$・$\eta_{H,wnd,270}$・$\eta_{C,wnd,0}$・$\eta_{C,wnd,90}$・$\eta_{C,wnd,180}$・$\eta_{C,wnd,270}$)は、「9.9.4 窓の日射熱取得率」に基づく方法で計算される。

# 窓の$\eta_d$値として、安全側、つまり複数の窓の中で暖房期は最も小さい値、冷房期は最も大きい値を代表値とする。

# In[47]:

def get_simple_eta_d_H_window(eta_d_H_windows):
    # eta_d_H_windows: eta_d_H_window の配列
    #                  eta_d_H_window: 窓のηd値(-)
    return min( eta_d_H_windows )


# In[48]:

def get_simple_eta_d_C_window(eta_d_C_windows):
    # eta_d_C_windows: eta_d_C_window の配列
    #                  eta_d_C_window: 窓のηd値(-)
    return max( eta_d_C_windows )


# 窓のf値として、安全側、つまり複数の窓の中で暖房期は最も小さい値、冷房期は最も大きい値を代表値とする。

# In[49]:

def get_simple_f_H_value(f_H_values):
    # f_H_values: f_H_value の配列
    #             f_H_value: 暖房期の窓の日射熱取得補正係数(-) デフォルト値を持つ場合は必ずしも指定しなくても良い
    return min(f_H_values)


# In[50]:

def get_simple_f_C_value(f_C_values):
    # f_C_values: f_C_value の配列
    #             f_C_value: 冷房期の窓の日射熱取得補正係数(-) デフォルト値を持つ場合は必ずしも指定しなくても良い
    return max(f_C_values)


# 窓のf値として、各窓の最も安全側の値を使用するか、デフォルト値を使用するか、選択可能である。

# In[51]:

def get_simple_eta_H_window(eta_d_H, f_H, is_f_value_default, default_f_H):
    # eta_d_H: 窓の日射熱取得率(-)
    # is_f_value_default: f値にデフォルト値を使用するかどうか
    # default_f_H_value: f値にデフォルト値を使用する場合の値 [Orientation型]
    if( is_f_value_default == True ):
        return Orientation(eta_d_H * default_f_H.D0, eta_d_H * default_f_H.D90, eta_d_H * default_f_H.D180, eta_d_H * default_f_H.D270)
    else:
        return Orientation(eta_d_H * f_H, eta_d_H * f_H, eta_d_H * f_H, eta_d_H * f_H)


# In[52]:

def get_simple_eta_C_window(eta_d_C, f_C, is_f_value_default, default_f_C):
    # eta_d_C: 窓の日射熱取得率(-)
    # is_f_value_default: f値にデフォルト値を使用するかどうか
    # default_f_C_value: f値にデフォルト値を使用する場合の値 [Orientation型]
    if( is_f_value_default == True ):
        return Orientation(eta_d_C * default_f_C.D0, eta_d_C * default_f_C.D90, eta_d_C * default_f_C.D180, eta_d_C * default_f_C.D270)
    else:
        return Orientation(eta_d_C * f_C, eta_d_C * f_C, eta_d_C * f_C, eta_d_C * f_C)


# #### 説明

# f値にデフォルト値を使用する場合。

# In[53]:

windows = [(0.5,0.7),(0.6,1.0)]
default_f = Orientation(0.4, 0.3, 0.4, 0.3)
get_simple_eta_H_window(get_simple_eta_d_H_window([window[0] for window in windows]),
                        get_simple_f_H_value([window[1] for window in windows]),
                        True, default_f)


# In[54]:

windows = [(0.5,0.7),(0.6,1.0)]
default_f = Orientation(0.4, 0.3, 0.4, 0.3)
get_simple_eta_C_window(get_simple_eta_d_C_window([window[0] for window in windows]),
                        get_simple_f_C_value([window[1] for window in windows]),
                        True, default_f)


# f値にデフォルト値を使用しない場合。

# In[55]:

windows = [(0.5,0.7),(0.6,1.0)]
default_f = Orientation(0.4, 0.3, 0.4, 0.3)
get_simple_eta_H_window(get_simple_eta_d_H_window([window[0] for window in windows]),
                        get_simple_f_H_value([window[1] for window in windows]),
                        False, default_f)


# In[56]:

windows = [(0.5,0.7),(0.6,1.0)]
default_f = Orientation(0.4, 0.3, 0.4, 0.3)
get_simple_eta_C_window(get_simple_eta_d_C_window([window[0] for window in windows]),
                        get_simple_f_C_value([window[1] for window in windows]),
                        False, default_f)


# ## 3-4) 係数等

# ### 温度差係数

# #### 定義

# In[57]:

def get_H(ASType, region):
    # ASType: 隣接空間の種類 [ AdjacentSpaceType 列挙体 ]
    # resion: 地域の区分 [ Region 列挙体 ]
    if region in { Region.Division1, Region.Division2, Region.Division3 }: # 地域の区分が1～3 の場合
        h = {
            AdjacentSpaceType.External : 1.0,
            AdjacentSpaceType.SemiExternal : 0.7,
            AdjacentSpaceType.Internal : 0.05
        }
        return h[ASType]
    else:  # 地域の区分が4～8 の場合
        h = {
            AdjacentSpaceType.External : 1.0,
            AdjacentSpaceType.SemiExternal : 0.7,
            AdjacentSpaceType.Internal : 0.15
        }
        return h[ASType]


# #### 説明

# In[58]:

get_H(AdjacentSpaceType.Internal, Region.Division5 )


# In[59]:

get_H(AdjacentSpaceType.Internal, Region.Division3 )


# ### 方位係数

# #### 定義

# In[60]:

def get_nu_H(region):
    # region: 地域の区分 [ Resion 列挙体 ]
    r = region.value # 1～8 地域の区分の番号に対応
    
    S      = [ 0.935, 0.856, 0.851, 0.815, 0.983, 0.936, 1.023, 'ND' ][r-1]
    SW     = [ 0.790, 0.753, 0.750, 0.723, 0.815, 0.763, 0.848, 'ND' ][r-1]
    W      = [ 0.535, 0.544, 0.542, 0.527, 0.538, 0.523, 0.548, 'ND' ][r-1]
    NW     = [ 0.325, 0.341, 0.351, 0.326, 0.297, 0.317, 0.284, 'ND' ][r-1]
    N      = [ 0.260, 0.263, 0.284, 0.256, 0.238, 0.261, 0.227, 'ND' ][r-1]
    NE     = [ 0.333, 0.341, 0.348, 0.330, 0.310, 0.325, 0.281, 'ND' ][r-1]
    E      = [ 0.564, 0.554, 0.540, 0.531, 0.568, 0.579, 0.543, 'ND' ][r-1]
    SE     = [ 0.823, 0.766, 0.751, 0.724, 0.846, 0.833, 0.843, 'ND' ][r-1]
    top    = [ 1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   'ND' ][r-1]
    bottom = [ 0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   'ND' ][r-1]
    
    return {
             Direction.S      : S,
             Direction.SW     : SW,
             Direction.W      : W,
             Direction.NW     : NW,
             Direction.N      : N,
             Direction.NE     : NE,
             Direction.E      : E,
             Direction.SE     : SE,
             Direction.top    : top,
             Direction.bottom : bottom,
           }


# In[61]:

def get_nu_C(region):
    # region: 地域の区分 [ Resion 列挙体 ]
    r = region.value # 1～8 地域の区分の番号に対応

    S      = [ 0.502, 0.507, 0.476, 0.437, 0.472, 0.434, 0.412, 0.480 ][r-1]
    SW     = [ 0.526, 0.548, 0.550, 0.481, 0.520, 0.491, 0.479, 0.517 ][r-1]
    W      = [ 0.508, 0.529, 0.553, 0.481, 0.518, 0.504, 0.495, 0.505 ][r-1]
    NW     = [ 0.411, 0.428, 0.447, 0.401, 0.442, 0.427, 0.406, 0.411 ][r-1]
    N      = [ 0.329, 0.341, 0.335, 0.322, 0.373, 0.341, 0.307, 0.325 ][r-1]
    NE     = [ 0.430, 0.412, 0.390, 0.426, 0.437, 0.431, 0.415, 0.414 ][r-1]
    E      = [ 0.545, 0.503, 0.468, 0.518, 0.500, 0.512, 0.509, 0.515 ][r-1]
    SE     = [ 0.560, 0.527, 0.487, 0.508, 0.500, 0.498, 0.490, 0.528 ][r-1]
    top    = [ 1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0,   1.0   ][r-1]
    bottom = [ 0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0   ][r-1]
    
    return {
             Direction.S      : S,
             Direction.SW     : SW,
             Direction.W      : W,
             Direction.NW     : NW,
             Direction.N      : N,
             Direction.NE     : NE,
             Direction.E      : E,
             Direction.SE     : SE,
             Direction.top    : top,
             Direction.bottom : bottom,
           }


# #### 説明

# In[62]:

get_nu_H(Region.Division1)[Direction.E]


# In[63]:

get_nu_C(Region.Division1)[Direction.E]


# # II 外皮性能の計算方法 (統合)

# ## 1-1) 外皮の部位

# 外皮の部位は、外壁(界壁)・天井・屋根・床(界床)から成る一般部位と、開口部（窓・ドア）、土間床で構成される。また、熱の計算においては、外皮の部位を面的に流れる熱流に加え、RC造やS造の隅角部等における熱橋計算および土間床外周部の熱計算を行う必要がある。  
# * 熱損失が面積あたりで定義される部位：「一般部位」「開口部(窓)」「開口部(ドア)」  
# * 熱損失が長さあたりで定義される部位：「熱橋」「土間床外周部」

# ## 1-2) 外皮の部位(詳細法)

# ### 一般部位・開口部(窓)・開口部(ドア)

# 一般部位・開口部(窓)・開口部(ドア)は、面積・熱損失係数(U値)・暖房期の日射熱取得率・冷房期の日射熱取得率・方位・隣接空間の種類をもつ。

# In[64]:

EnvGeneral = namedtuple("EnvGeneral", "A U eta_H eta_C direction ASType")
EnvWindow  = namedtuple("EnvWindow",  "A U eta_H eta_C direction ASType")
EnvDoor    = namedtuple("EnvDoor",    "A U eta_H eta_C direction ASType")
# A: 面積(m2)
# U: 熱損失係数(W/m2K)
# eta_H: 暖房期の日射熱取得率(-)
# eta_C: 冷房期の日射熱取得率(-)
# direction: 方位 [direction列挙型]
# ASType: 隣接空間の種類 [AdjacentSpaceType型]


# ### 熱橋

# 熱橋は、長さ・線熱損失係数・暖房期の日射熱取得率・冷房期の日射熱取得率・方位1と方位2・隣接空間の種類をもつ。熱橋は多くの場合、隅角部等に発生し、2方位に面する場合が多いため、方位1と方位2を持つことにする。方位1と方位2に順番は無い。また、T型熱橋など、接続する部位が同じ方位を持つ場合は、方位1と方位2に同じ方位を入力すること。  
# ただし、熱橋の日射熱取得率は、本来であれば、  
# $\begin{align} \eta = \gamma \times 0.034 \times \frac{ L \times \psi }{ A } \end{align}$  
# で表されるのに対し、  
# $\begin{align} \eta' = \gamma \times 0.034 \times \psi \end{align} $  
# で表されることとする。  
# ここで、  
# $\eta$: 日射熱取得率(-)  
# $\eta'$: 熱橋の日射熱取得率(m)  
# 従って、$ m $ 値(m<sup>2</sup>)の計算において、仕様書によると、  
# $\begin{align} m = A \times \eta \times \nu \end{align} $  
# ではなく、  
# $\begin{align} m = L \times \eta' \times \nu \end{align} $  
# で計算される。

# In[65]:

EnvHB = namedtuple("EnvHB", "L psi eta_H_dash eta_C_dash direction1 direction2 ASType")
# L: 長さ(m)
# psi: 線熱損失係数(W/mK)
# eta_H: 暖房期の熱橋の日射熱取得率(m)
# eta_C: 冷房期の熱橋の日射熱取得率(m)
# direction1: 方位1 [direction列挙型]
# direction2: 方位2 [direction列挙型]
# ASType: 隣接空間の種類 [AdjacentSpaceType型]


# ### 土間床外周部

# 土間床外周部は、長さ・線熱損失係数・隣接空間の種類をもつ。日射に関する熱の移動はない。従って、方位の概念も持たない。

# In[66]:

EnvEFPeri = namedtuple("EnvEFPeri", "L psi ASType")
# L: 長さ(m)
# psi: 線熱損失係数(W/mK)
# ASType: 隣接空間の種類 [AdjacentSpaceType型]


# ## 1-3) 外皮の部位(簡易法)

# ### 一般部位・開口部(ドア)

# 外皮の部位の簡易法版。詳細法版と異なり、面積・方位をもたない。

# In[67]:

SimpleEnvGeneral = namedtuple("SimpleEnvGeneral", "U eta_H eta_C ASType")
SimpleEnvDoor    = namedtuple("SimpleEnvDoor",    "U eta_H eta_C ASType")
# U: 熱損失係数(W/m2K)
# eta_H: 暖房期の日射熱取得率(-)
# eta_C: 冷房期の日射熱取得率(-)
# ASType: 隣接空間の種類 [AdjacentSpaceType型]


# ### 開口部(窓)

# 外皮の部位(窓)の簡易法版。簡易法に限り、窓の$U$値、$\eta_H$値、$\eta_C$値、方位、隣接空間の種類に加えて、$\eta_d$値、$f_H$値、$f_C$値が必要である。簡易法の場合、最も不利側の$\eta_d$値、$f$値を計算する必要があるため。ただし、$f$値に関しては、デフォルト値を適用する場合、入力する必要はない。

# In[68]:

SimpleEnvWindow = namedtuple("SimpleEnvWindow", "U eta_H eta_C ASType eta_d f_H f_C")
# U: 熱損失係数(W/m2K)
# eta_H: 暖房期の日射熱取得率(-)
# eta_C: 冷房期の日射熱取得率(-)
# ASType: 隣接空間の種類 [AdjacentSpaceType型]
# eta_d: 垂直面日射熱取得率(-)
# f_H: 暖房期の取得日射熱補正係数(-)
# f_C: 冷房期の取得日射熱補正係数(-)


# ### 熱橋

# 熱橋の簡易法版はない。現時点で、簡易法は木造戸建て住宅のみ認められている。木造戸建て住宅は熱橋計算が不要なため、簡易法では熱橋を持つ必要はない。

# ### 土間床外周部

# 土間床外周部の簡易法版。詳細法版と違い、長さをもたない。

# In[69]:

SimpleEnvEFPeri = namedtuple("SimpleEnvEFPeri", "psi ASType")
# psi: 線熱損失係数(W/mK)
# ASType: 隣接空間の種類 [AdjacentSpaceType型]


# ## 2) 関数の統合

# ### 詳細法

# #### 定義

# In[70]:

def getEnvPerformance(env_generals, env_windows, env_doors, env_HBs, env_EF_Peris, A_EF, A_A, region):

    results = OrderedDict()
    
    ##### 面積関係の計算 #####
    
    # 外皮の表面積の合計(m2)
    a_env = get_A_env(  [ env_general.A for env_general in env_generals ]
                      + [ env_window.A  for env_window  in env_windows  ]
                      + [ env_door.A    for env_door    in env_doors    ], A_EF )
    results["外皮の面積の合計"] = a_env
    
    # 床面積の合計に対する外皮の部位の比
    r_env = get_r_env( a_env, A_A )
    results["床面積の合計に対する外皮の部位の比"] = r_env
    
    ##### UA値、Q'値の計算 #####

    # ( 面積, U値, 温度差係数 ) の配列を作成
    # 温度差係数は、隣接空間の種類と地域の区分から決定
    U_generals = [ (env_general.A, env_general.U, get_H(env_general.ASType, region) ) for env_general in env_generals ]
    U_windows  = [ (env_window.A,  env_window.U,  get_H(env_window.ASType, region)  ) for env_window  in env_windows  ]
    U_doors    = [ (env_door.A,    env_door.U,    get_H(env_door.ASType, region)    ) for env_door    in env_doors    ]
    results["U_generals"] = U_generals
    results["U_windows"] = U_windows
    results["U_doors"] = U_doors
    
    # ( 長さ, psi値, 温度差係数 ) の配列を作成
    # 温度差係数は、隣接空間の種類と地域の区分から決定
    psi_HBs = [ (env_HB.L, env_HB.psi, get_H(env_HB.ASType, region) ) for env_HB in env_HBs ]
    results["psi_HBs"] = psi_HBs
    
    # ( 長さ, psi値, 温度差係数 ) の配列を作成
    # 温度差係数は、隣接空間の種類と地域の区分から決定
    psi_EF_Peris = [ (env_EF_Peri.L, env_EF_Peri.psi, get_H(env_EF_Peri.ASType, region) ) for env_EF_Peri in env_EF_Peris ]
    results["psi_EF_Peris"] = psi_EF_Peris

    # UA値(W/m2K)
    UA = get_UA( U_generals + U_windows + U_doors , psi_HBs + psi_EF_Peris , a_env )
    results["UA値"] = UA
    
    # 熱損失係数(換気による熱損失を含まない) 
    Q_dash = get_Q_dash( float(UA), r_env )
    results["熱損失係数(換気による熱損失を含まない) "] = Q_dash
    
    ##### ηA値、m値の計算 (暖房期) #####

    # ( 面積, 日射熱取得率, 方位係数 ) の配列を作成
    eta_H_generals = [ (env_general.A, env_general.eta_H, get_nu_H(region)[env_general.direction] ) for env_general in env_generals ]
    eta_H_windows  = [ (env_window.A,  env_window.eta_H,  get_nu_H(region)[env_window.direction ] ) for env_window  in env_windows  ]
    eta_H_doors    = [ (env_door.A,    env_door.eta_H,    get_nu_H(region)[env_door.direction   ] ) for env_door    in env_doors    ]
    results["eta_H_generals"] = eta_H_generals
    results["eta_H_windows"] = eta_H_windows
    results["eta_H_doors"] = eta_H_doors

    # ( 面積, 熱橋の日射熱取得率, 方位係数1, 方位係数2 ) の配列を作成
    eta_H_dash_HBs = [ (env_HB.L, env_HB.eta_H_dash, get_nu_H(region)[env_HB.direction1], get_nu_H(region)[env_HB.direction2] ) for env_HB in env_HBs ]
    results["eta_H_dash_HBs"] = eta_H_dash_HBs

    # ηAH値(-)
    eta_A_H = get_eta_A_H(eta_H_generals + eta_H_windows + eta_H_doors , eta_H_dash_HBs, a_env)
    results["eta_A_H"] = eta_A_H
    
    # μH値(-)
    mu_H = get_Mu_H(float(eta_A_H), r_env)
    results["mu_H"] = mu_H
    
    ##### ηA値、m値の計算 (冷房期) #####

    # ( 面積, 日射熱取得率, 方位係数 ) の配列を作成
    eta_C_generals = [ (env_general.A, env_general.eta_C, get_nu_C(region)[env_general.direction] ) for env_general in env_generals ]
    eta_C_windows  = [ (env_window.A,  env_window.eta_C,  get_nu_C(region)[env_window.direction]  ) for env_window  in env_windows  ]
    eta_C_doors    = [ (env_door.A,    env_door.eta_C,    get_nu_C(region)[env_door.direction]    ) for env_door    in env_doors    ]
    results["eta_C_generals"] = eta_C_generals
    results["eta_C_windows"] = eta_C_windows
    results["eta_C_doors"] = eta_C_doors
    
    # ( 面積, 熱橋の日射熱取得率, 方位係数1, 方位係数2 ) の配列を作成
    eta_C_dash_HBs = [ (env_HB.L, env_HB.eta_C_dash, get_nu_C(region)[env_HB.direction1], get_nu_C(region)[env_HB.direction2] ) for env_HB in env_HBs ]
    results["eta_C_dash_HBs"] = eta_C_dash_HBs    

    # ηAC値(-)
    eta_A_C = get_eta_A_C(eta_C_generals + eta_C_windows + eta_C_doors , eta_C_dash_HBs, a_env)
    results["eta_A_C"] = eta_A_C

    # mC値(-)
    mu_C = get_Mu_C(float(eta_A_C), r_env)
    results["mu_C"] = mu_C
    
    return results


# #### 説明

# In[71]:

env_general_1 = EnvGeneral(A=9.0,U=1.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_general_2 = EnvGeneral(A=9.0,U=1.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_general_3 = EnvGeneral(A=9.0,U=1.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_general_4 = EnvGeneral(A=9.0,U=1.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_window_1 = EnvWindow(A=1.0,U=3.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_window_2 = EnvWindow(A=1.0,U=3.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_door_1 = EnvDoor(A=1.0,U=2.0,eta_H=1.0,eta_C=1.0,direction=Direction.E,ASType=AdjacentSpaceType.External)
env_HB_1 = EnvHB(L=1.0,psi=1.0,eta_H_dash=1.0,eta_C_dash=1.0,direction1=Direction.E,direction2=Direction.S,ASType=AdjacentSpaceType.External)
env_HB_2 = EnvHB(L=1.0,psi=1.0,eta_H_dash=1.0,eta_C_dash=1.0,direction1=Direction.E,direction2=Direction.S,ASType=AdjacentSpaceType.External)
env_HB_3 = EnvHB(L=1.0,psi=1.0,eta_H_dash=1.0,eta_C_dash=1.0,direction1=Direction.E,direction2=Direction.S,ASType=AdjacentSpaceType.External)
env_EF_Peri_1 = EnvEFPeri(L=1.0,psi=1.0,ASType=AdjacentSpaceType.External)
env_EF_Peri_2 = EnvEFPeri(L=1.0,psi=1.0,ASType=AdjacentSpaceType.External)
env_EF_Peri_3 = EnvEFPeri(L=1.0,psi=1.0,ASType=AdjacentSpaceType.External)

getEnvPerformance( [ env_general_1, env_general_2, env_general_3, env_general_4 ],
                [ env_window_1, env_window_2 ],
                [ env_door_1 ],
                [ env_HB_1, env_HB_2, env_HB_3 ],
                [ env_EF_Peri_1, env_EF_Peri_2, env_EF_Peri_3 ],
                [ 16.0 ], 30.0, Region.Division6 )


# ### 簡易法(最も不利側の値となるようにU値やη値を選択した後の計算)

# #### 定義

# In[72]:

def simpleEnvPerformanceSelected(house_type, region,
                                 U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d,
                                 eta_d_H, eta_d_C, f_H, f_C, is_f_value_default, default_f_H, default_f_C):
    # house_type: 住宅の種類(床断熱住宅・基礎断熱住宅・床断熱基礎断熱併用住宅)
    # region: 地域の区分
    # U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d: 熱損失係数(W/m2K)(屋根・外壁・ドア・窓・床・基礎・玄関等の基礎)
    # psi_prm, psi_prm_d: 線熱損失係数(W/mK)(土間床外周部・玄関等の土間床外周部)
    # eta_d_H, eta_d_C: 窓のηd値(暖房期・冷房期)(-)
    # f_H, f_C: 窓のf値(暖房期・冷房期)(-)(各窓において最も安全側の値として選択された値である。f値としてデフォルト値を使用する場合はこの値は使用しない。)
    # is_f_value_default: f値としてデフォルト値を使用するか否か [bool値]
    # default_f_H, default_f_C; f値としてデフォルト値を使用する場合のf値(暖房期・冷房期)(-)

    results = OrderedDict()

    def get_U_A_provisional(house_type, U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d):
        al = simple_Area_and_Length(house_type)
        return get_simple_U_A (al.roof, al.wall, al.door, al.wnd, al.floor, al.base, al.base_IS, al.base_d, al.base_d_IS, al.prm, al.prm_IS, al.prm_d, al.prm_d_IS,
                               simple_HValue.roof, simple_HValue.wall, simple_HValue.door, simple_HValue.wnd, simple_HValue.floor, simple_HValue.base_OS, simple_HValue.base_IS, simple_HValue.prm_OS, simple_HValue.prm_IS,
                               U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d,
                               al.env )
    
    U_A_floor_ins = get_U_A_provisional(simple_HouseType.floor_ins,U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d)
    U_A_base_ins  = get_U_A_provisional(simple_HouseType.base_ins ,U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d)
    
    if house_type == simple_HouseType.floor_ins:
        house_type_on_calc = house_type
        U_A = U_A_floor_ins
    elif house_type == simple_HouseType.base_ins:
        house_type_on_calc = house_type
        U_A = U_A_base_ins
    else:
        U_A, house_type_on_calc = judge_simple_house_type(U_A_floor_ins, U_A_base_ins)
    
    results["Judged House Type"] = house_type_on_calc
    results["UA"] = U_A
    
    al = simple_Area_and_Length(house_type_on_calc)

    eta_H_roof   = get_simple_eta_H_roof(U_roof)
    eta_H_wall   = get_simple_eta_H_wall(U_wall)
    eta_H_door   = get_simple_eta_H_door(U_door)
    eta_H_wnd    = get_simple_eta_H_window(eta_d_H, f_H, is_f_value_default, default_f_H)
    eta_H_base   = get_simple_eta_H_base(U_base)
    eta_H_base_d = get_simple_eta_H_base_d(U_base_d)
    eta_C_roof   = get_simple_eta_C_roof(U_roof)
    eta_C_wall   = get_simple_eta_C_wall(U_wall)
    eta_C_door   = get_simple_eta_C_door(U_door)
    eta_C_wnd    = get_simple_eta_C_window(eta_d_C, f_C, is_f_value_default, default_f_C)
    eta_C_base   = get_simple_eta_C_base(U_base)
    eta_C_base_d = get_simple_eta_C_base_d(U_base_d)
    
    results["eta_H_wnd"]=eta_H_wnd
    results["eta_C_wnd"]=eta_C_wnd

    eta_A_H = get_simple_eta_A_H(al.roof, al.wall, al.door, al.wnd, al.base, al.base_d,
                                 get_nu_H(region)[Direction.top], get_simple_Orientation_value_from_Direction(get_nu_H(region)),
                                 eta_H_roof, eta_H_wall, eta_H_door, eta_H_wnd, eta_H_base, eta_H_base_d,
                                 al.env)
    eta_A_C = get_simple_eta_A_C(al.roof, al.wall, al.door, al.wnd, al.base, al.base_d,
                                 get_nu_C(region)[Direction.top], get_simple_Orientation_value_from_Direction(get_nu_C(region)),
                                 eta_C_roof, eta_C_wall, eta_C_door, eta_C_wnd, eta_C_base, eta_C_base_d,
                                 al.env)

    results["eta_A_H"] = eta_A_H
    results["eta_A_C"] = eta_A_C
    
    r_env = get_r_env(al.env, al.A)

    Q_dash = get_Q_dash( float(U_A), r_env )
    results["Q_dash"] = Q_dash
    
    Mu_H = get_Mu_H(float(eta_A_H), r_env)
    Mu_C = get_Mu_C(float(eta_A_C), r_env)
    results["Mu_H"] = Mu_H
    results["Mu_C"] = Mu_C
    return results


# #### 説明

# In[73]:

simpleEnvPerformanceSelected( house_type = simple_HouseType.base_ins, region = Region.Division6,
                             U_roof=0.240,U_wall=0.530,U_door=2.330,U_wnd=3.490,U_floor=0.480,
                             U_base=0.0, U_base_d=0.0,psi_prm=1.8,psi_prm_d=1.8,
                             eta_d_H = 0.510, eta_d_C = 0.510,f_H=1.0, f_C=1.0, is_f_value_default=True,
                             default_f_H = Orientation(0.654,0.595,0.589,0.674666667),
                             default_f_C = Orientation(0.852,0.864,0.862,0.852))    


# ### 簡易法(最も不利側の値となるようにU値やη値を選択する計算を含む)

# #### 定義

# In[74]:

def simpleEnvPerformance(house_type, region,
                         roofs, walls, doors, windows, floors, bases, baseds, prms, prmds,
                         is_f_value_default,
                         default_f_H, default_f_C
                        ):
    # house_type: 住宅の種類(床断熱住宅・基礎断熱住宅・床断熱基礎断熱併用住宅)
    # region: 地域の区分
    # roofs, walls, floors, bases, baseds: SimpleEnvGeneral (熱損失係数(W/m2K), 暖房期の日射熱取得率(-), 冷房期の日射熱取得率(-), 隣接空間の種類)
    # doors: SimpleEnvDoor (熱損失係数(W/m2K), 暖房期の日射熱取得率(-), 冷房期の日射熱取得率(-), 隣接空間の種類)
    # windows: SimpleEnvWindow (熱損失係数(W/m2K), 暖房期の日射熱取得率(-), 冷房期の日射熱取得率(-), 隣接空間の種類, 垂直面日射熱取得率(-), 暖房期の取得日射熱補正係数(-), 冷房期の取得日射熱補正係数(-))
    # prms, prmds: SimpleEnvEFPeri (線熱損失係数(W/mK), 隣接空間の種類)
    # is_f_value_default: f値としてデフォルト値を使用するか否か [bool値]
    # default_f_H, default_f_C; f値としてデフォルト値を使用する場合のf値(暖房期・冷房期)(-)

    U_roof    = get_simple_U_roof  ([(roof.U,   get_H(roof.ASType,   region)) for roof   in roofs  ])
    U_wall    = get_simple_U_wall  ([(wall.U,   get_H(wall.ASType,   region)) for wall   in walls  ])
    U_door    = get_simple_U_door  ([(door.U,   get_H(door.ASType,   region)) for door   in doors  ])
    U_wnd     = get_simple_U_wnd   ([(window.U, get_H(window.ASType, region)) for window in windows]) 
    U_floor   = get_simple_U_floor ([(floor.U,  get_H(floor.ASType,  region)) for floor  in floors ])
    U_base    = get_simple_U_base  ([(base.U,   get_H(base.ASType,   region)) for base   in bases  ])
    U_base_d  = get_simple_U_base_d([(based.U,  get_H(based.ASType,  region)) for based  in baseds ])
    psi_prm   = get_simple_U_prm   ([(prm.psi,  get_H(prm.ASType,    region)) for prm    in prms   ])
    psi_prm_d = get_simple_U_prm_d ([(prmd.psi, get_H(prmd.ASType,   region)) for prmd   in prmds  ])
    
    eta_d_H = get_simple_eta_d_H_window([wnd.eta_d for wnd in wnds])
    eta_d_C = get_simple_eta_d_C_window([wnd.eta_d for wnd in wnds])
    
    f_H = get_simple_f_H_value([wnd.f_H for wnd in wnds])
    f_C = get_simple_f_C_value([wnd.f_C for wnd in wnds])
    
    return simpleEnvPerformanceSelected( house_type, region,
                             U_roof, U_wall, U_door, U_wnd, U_floor, U_base, U_base_d, psi_prm, psi_prm_d,
                             eta_d_H, eta_d_C, f_H, f_C, is_f_value_default, default_f_H, default_f_C )


# In[ ]:



