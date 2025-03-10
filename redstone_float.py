import math


class RedstoneFloat:
    def __init__(self, s: str, M: dict[str: int], E: dict[str: int]):
        """
        :param s: 符号位，'obsidian' 表示 1，'' 表示 0
        :param M: 尾数部分，dict 形式的 16 色羊毛
        :param E: 指数部分，dict 形式的 20 色混凝土和混凝土粉末
        """
        self.s = s  # 直接存储字符串，如 'obsidian' 或 ''
        self.M = M  # 以字典存储尾数部分
        self.E = E  # 以字典存储指数部分
    
    def _decode_mantissa(self) -> float:
        """
        仅to_float使用
        将羊毛集合转换为尾数的浮点数表示
        """
        value = 0
        colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
        # 依次表示 2^(-1), 2^(-2), 2^(-3), ..., 2^(-16)
        for i, color in enumerate(colors):
            if color in self.M:
                value += 2 ** (-i-1)
        return value
    
    def _decode_exponent(self) -> int:
        """
        仅to_float使用
        将混凝土集合转换为指数的整数表示
        """
        value = 0
        colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
                  "white_powder", "orange_powder", "magenta_powder", "light_blue_powder"]
        # 依次表示 2^(1), 2^(0), 2^(-1), ..., 2^(-18)
        for i, color in enumerate(colors):
            if color in self.E:
                value += 2 ** (1 - i)
        return value
    
    def to_float(self) -> float:
        sign = (-1) ** (self.s == 'obsidian')
        mantissa = self._decode_mantissa()
        exponent = self._decode_exponent()
        print(f"sign: {sign}, mantissa: {mantissa}, exponent: {exponent}")
        return sign * mantissa * (2 ** exponent)

    def from_float(cls, value: float) -> "RedstoneFloat":
        """
        将 float 转换为 RedstoneFloat 表示。
        表示的形式为： value = sign * (k/2^16) * 2^(e)
        其中 k 为 0 到 2^16-1 的整数（尾数部分），e 是 20 色混凝土能表示的指数（分辨率为 2^(-18)）。
        """
        # 对于 0 或太小的数，直接返回零表示
        if value == 0 or abs(value) < 2**(-16):
            return cls('' if value >= 0 else 'obsidian', {}, {})
        
        # 符号
        s = 'obsidian' if value < 0 else ''
        r = abs(value)
        
        # 选择一个初步的指数猜测，使得 m = r / 2^(e_guess) 落在 [0.5, 1) 内
        e_guess = math.ceil(math.log2(r))
        m_guess = r / (2**e_guess)
        
        # 将 m_guess 量化到 16 位（尾数精度为 1/2^16）
        k = round(m_guess * (2**16))
        if k == 0:
            k = 1
        if k >= 2**16:
            k = 2**16 - 1
        
        # 为了精确还原 r，理想上应满足： r = (k/2^16) * 2^(e_ideal)
        # 故有： e_ideal = log2(r) - log2(k/2^16)
        e_ideal = math.log2(r) - math.log2(k/2**16)
        
        # 将 e_ideal 量化到 2^(-18) 的步长上
        step = 2**(-18)
        e_quantized = round(e_ideal / step) * step
        
        # 指数部分可表示的颜色列表（共 20 个），最小步长为 2^(1-19)=2^(-18)
        exp_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                        "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
                        "white_powder", "orange_powder", "magenta_powder", "light_blue_powder"]
        # 最大可表示的指数：所有颜色都“打开”
        max_e = sum(2**(1 - i) for i in range(len(exp_colors)))
        # 保证指数在 [0, max_e] 内（本表示不支持负指数）
        if e_quantized < 0:
            e_quantized = 0
        if e_quantized > max_e:
            e_quantized = max_e

        # 构造尾数字典 M：按照顺序，将 k 的 16 位二进制表示与 16 种羊毛颜色对应
        M = {}
        mantissa_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                            "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
        bin_str = format(k, '016b')  # 16 位二进制字符串
        for i, bit in enumerate(bin_str):
            if bit == '1':
                M[mantissa_colors[i]] = 1

        # 构造指数字典 E：使用贪心算法，从 exp_colors 列表中依次扣除权重
        E = {}
        remaining = e_quantized
        for i, color in enumerate(exp_colors):
            weight = 2**(1 - i)
            if remaining >= weight - 1e-12:  # 考虑浮点误差
                E[color] = 1
                remaining -= weight

        return cls(s, M, E)
    
    def __repr__(self):
        return f"RedstoneFloat(s={self.s}, M={self.M}, E={self.E})"
    

def adding(e_a: dict[str: int], e_b: dict[str: int]) -> dict[str: int]:
    """模拟指数部分相加"""
    colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
                "white_powder", "orange_powder", "magenta_powder", "light_blue_powder"]
    next_colors = ["orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
                "white_powder", "orange_powder", "magenta_powder", "light_blue_powder", ""]
    result = {}
    for color in colors:
        result[color] = e_a.get(color, 0) + e_b.get(color, 0) # 模拟直接混合到一个箱子里
    
    # 实际过程中应该是16次有序的独立的检测
    for i, color in enumerate(colors): # 模拟进位
        while result[color] >= 2: # 存量转信器发出信号
            result[color] -= 2 # 信号指示黄铜漏斗漏掉2个物品
            next_color = next_colors[i]
            result[next_color] = result.get(next_color, 0) + 1 # 信号指示投入一个物品表示进位
    return result

# def mantissa_multiply(m_a: dict[str: int], m_b: dict[str: int]) -> dict[str: int]:
#     """模拟尾数部分相乘"""
#     colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
#                 "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
#                 "white_powder", "orange_powder", "magenta_powder", "light_blue_powder"]
#     colors = ["orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
#                 "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", 
#                 "white_powder", "orange_powder", "magenta_powder", "light_blue_powder", ""]
#     for color in colors:
#         if color in m_a:

def redstone_multiply(a: RedstoneFloat, b: RedstoneFloat):
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
    new_E = adding(a.E, b.E)
    
    # 计算尾数部分（位移加法乘法）
    # result_m_set = set()
    # temp_m_set = a.M.copy()
    
    # for i, color in enumerate(["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
    #                            "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]):
    #     if color in b.M:
    #         result_m_set.update(temp_m_set)
    #     temp_m_set = {c for c in temp_m_set if c in ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
    #                                                    "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]}  # 进行位移
    
    # return RedstoneFloat(new_s, result_m_set, new_E)

# 测试指数相加部分
# e_a = {"white": 1, "orange": 1}
# e_b = {"white": 1, "orange": 1}
# print(exponent_add(e_a, e_b))

# 测试to_float和from_float
a = RedstoneFloat.from_float(RedstoneFloat, 1.1470e-05)
print(a)
print(a.to_float())