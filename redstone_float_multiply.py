
from redstone_float import RedstoneFloat as rf


def exponent_add(e_a: dict[str: int], e_b: dict[str: int]) -> dict[str: int]:
    """模拟指数部分相加"""
    # colors依次表示 2^(0)=1, 2^(1)=2, 2^(2)=4, ..., 2^(7)
    # 但有偏移量 -2，且需要的指数多为负数，所以最终运算时应该是2^(2-value)
    colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray"]
    next_colors = ["orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", ""]

    # result 提前填充补码以减去偏移量 2
    result = {color: 1 for color in colors}
    result["white"] = 0

    for color in colors:
        result[color] += (e_a.get(color, 0) + e_b.get(color, 0)) # 模拟直接混合到一个箱子里

    # 实际过程中应该是8次有序的独立的检测
    for color, next_color in zip(colors, next_colors):
        while result[color] >= 2: # 存量转信器发出信号
            result[color] -= 2 # 信号指示黄铜漏斗漏掉2个物品
            if next_color: result[next_color] += 1 # 信号指示投入一个物品表示进位
    return result

def mantissa_multiply(m_a: dict[str: int], m_b: dict[str: int]) -> dict[str: int]:
    """模拟尾数部分相乘"""
    # colors依次表示 2^(-1), 2^(-2), 2^(-3), ..., 2^(-16)
    colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
    shift_next_colors = {"white": [], "orange": [], "magenta": [], "light_blue": [], "yellow": [], "lime": [], "pink": [], "gray": [], 
                  "light_gray": [], "cyan": [], "purple": [], "blue": [], "brown": [], "green": [], "red": [], "black": []} # 位移装置用
    next_colors = ["", "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red"]
    
    result = {color: 0 for color in colors}
    # 实际过程中应该是16个独立的检测通道，每个检测通道中0~16次检测
    for i, chanel in enumerate(colors):
        # 此处动态构建shift_next_colors，实际过程中应该是提前准备好的
        shifted_colors = colors[i+1:]
        for _, c in enumerate(colors):
            # print(c)
            if c not in shifted_colors: shifted_colors.append("")
        shift_next_colors[chanel] = shifted_colors
        # print(f"chanel: {chanel}, shifted_colors: {shifted_colors}")

        # m_a 没有对应数字则检测通道不开启
        if not m_a[chanel] > 0: continue

        # 如前文所述，实际过程中应是0~16次独立的检测
        for color, shifted_color in zip(colors, shift_next_colors[chanel]):
            # print(f"color: {color}, shifted_color: {shifted_color}")
            if not (m_b[color]>0 and shifted_color): continue
            result[shifted_color] += 1
    # print(f"result: {result}")

    # 实际过程中应该是16次有序的独立的检测
    for color, next_color in zip(colors[::-1], next_colors[::-1]): # 注意此处是从末往前进位
        while result[color] >= 2: # 存量转信器发出信号
            result[color] -= 2 # 信号指示黄铜漏斗漏掉2个物品
            if next_color: result[next_color] += 1 # 信号指示投入一个物品表示进位
    print(f"result: {result}")
    return result

def multiplying(a: rf, b: rf):
    """实现基于位移加法的浮点数乘法"""
    
    # 模拟计算新符号位
    new_s = ''
    if ('obsidian' in a.s):
        new_s = 'obsidian'
    if ('obsidian' in b.s):
        new_s = 'obsidian'
    if ('obsidian' in a.s and 'obsidian' in b.s):
        new_s = ''
    
    # 模拟计算指数部分
    raw_E = exponent_add(a.E, b.E)
    
    # 计算尾数部分（位移加法乘法）
    raw_M = mantissa_multiply(a.M, b.M)

    return rf(new_s, raw_M, raw_E)

    mantissa_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
                    "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
    exponent_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray"]
    new_M = {color: 0 for color in mantissa_colors}
    new_E = {color: 0 for color in exponent_colors}

    # 尾数部分标准化为0.1xx...，同时调整指数部分
    temp_slots_M = [count for count in raw_M.values()] # 模拟把raw_M物品分配到位移装置中
    temp_slots_E = [count for count in raw_E.values()] # 模拟把raw_E物品分配到位移装置中
    while True:
        if temp_slots_M[0] > 0: break
        temp_slots_M = temp_slots_M[1:] + [0] # 最前端的物品被丢弃
        temp_slots_E = [1] + temp_slots_E[:-1] # 负数部分向右位移，最末端的物品被丢弃
    # 只检测位移装置中各槽位的物品数量，生成新的物品列，扔进结果箱子
    for j, count in enumerate(temp_slots_M):
        if count > 0:
            new_M[mantissa_colors[j]] += count
    for j, count in enumerate(temp_slots_E):
        if count > 0:
            new_E[exponent_colors[j]] += count
    temp_slots_M = [0] * 16 # 清空位移装置
    temp_slots_E = [0] * 8 # 清空位移装置
    
    return rf(new_s, new_M, new_E)

# 测试指数相加部分
# e_a = {"orange": 1}
# e_b = {"white": 1, "orange": 1}
# print(exponent_add(e_a, e_b))

# # 测试to_float和from_float
# na = 1.4271e+00
# # na = 0.75
# print(rf.redstr(na))
# a = rf.from_string(rf.redstr(na))
# print(a)
# print(a.to_float())
# nb = 1.1470e-05
# # nb = 0.421875
# print(rf.redstr(nb))
# b = rf.from_string(rf.redstr(nb))
# print(b)
# print(b.to_float())

# 测试乘法
print("### 乘数 a ###")
# a = rf.from_string(rf.redstr(1.4271e+00))
# a = rf.from_string(rf.redstr(-0.421875))
# a = rf.from_string(rf.redstr(1.7347))
sa = ".11011e-111(+2)" # 0.84375 * 2^(-5)
# sa = ".00001101e-10110(+2)"
a = rf.from_string(sa)
print("[红石浮点数表示]")
print(a)
print(f"[二进制转写]\n{sa}")
print(f"[十进制数值]")
print(f"{a.to_float()}")

print("### 乘数 b ###")
# b = rf.from_string(rf.redstr(-1.1470e-05))
# b = rf.from_string("-.11e-100(+2)") # -0.75 * 2^(-2)
# b = rf.from_string(rf.redstr(1.7347))
sb = "-.11e-100(+2)" # -0.75 * 2^(-2)
# sb = "-.0001110001e-100010(+2)"
b = rf.from_string(sb)
print("[红石浮点数表示]")
print(b)
print(f"[二进制转写]\n{sb}")
print(f"[十进制数值]")
print(f"{b.to_float()}")

print("### 计算结果 r ###")
r = multiplying(a, b)
print("[红石浮点数表示]")
print(r)
print(f"[十进制数值]")
print(f"{r.to_float()}")