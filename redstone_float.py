import math


class RedstoneFloat:
    def __init__(self, s: str, M: dict[str: int], E: dict[str: int]):
        """
        :param s: 符号位，'obsidian' 表示 1，'' 表示 0
        :param M: 尾数部分，dict 形式的 16 色羊毛
        :param E: 指数部分，dict 形式的 8 色混凝土
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
            if self.M[color] > 0:
                value += 2 ** (-i-1)
        return value
    
    def _decode_exponent(self) -> int:
        """
        仅to_float使用
        将混凝土集合转换为指数的整数表示
        """
        value = 0
        colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray"]
        # 依次表示 2^0=1, 2^1=2, 2^2=4, ..., 2^(7)=128
        # 但有偏移量 -2，且需要的指数多为负数，所以最终运算时应该是2^(2-value)
        for i, color in enumerate(colors):
            if self.E[color] > 0:
                value += 2 ** (i)
        # 例如：假如有 white, orange, magenta, 则 value = 1 + 2 + 4 = 7，实际表示的指数为 2^(2-7) = 2^(-5)
        # 最大可表示的数为 2^(2-0) = 2^2 = 4，最小可表示的数为 2^( 2 - (1+2+4+8...+128) )
        return value
    
    def to_float(self) -> float:
        sign = (-1) ** (self.s == 'obsidian')
        mantissa = self._decode_mantissa()
        exponent = self._decode_exponent()
        print(f"sign: {sign}, mantissa: {mantissa}, exponent: {-exponent}(+2)")
        return sign * mantissa * (2**(2-exponent))

    @staticmethod
    def from_float(value: float) -> 'RedstoneFloat':
        """
        将一个 Python float 转换为 RedstoneFloat 表示。
        """
        import math

        # 处理符号位
        s = 'obsidian' if value < 0 else ''

        # 获取绝对值
        abs_value = abs(value)

        # 特殊处理0
        if abs_value == 0:
            return RedstoneFloat(s, {}, {})

        # 分离尾数和指数
        exponent = math.floor(math.log2(abs_value))
        mantissa = abs_value / (2 ** exponent)

        # 尾数处理为 [0, 1) 之间
        if mantissa >= 1:
            mantissa /= 2
            exponent += 1
        exponent -= 2  # 调整指数偏移量
        print(f"exponent: {exponent}(+2), mantissa: {mantissa}")

        # 尾数转换为16色羊毛
        mantissa_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
                        "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
        # 依次表示 2^(-1), 2^(-2), 2^(-3), ..., 2^(-16)

        M = {color: 0 for color in mantissa_colors}
        remaining = mantissa
        for i, color in enumerate(mantissa_colors):
            bit_value = 2 ** (-i-1)
            if remaining >= bit_value:
                M[color] = 1
                remaining -= bit_value

        # 指数转换为8色混凝土
        exponent_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray"]
        # 依次表示 1, 2, 4, ..., 2^(7)
        # 但有偏移量 -2，且需要的指数多为负数，所以最终运算时应该是2^(2-value)
        rev_exponent_colors = exponent_colors[::-1]

        E = {color: 0 for color in exponent_colors}
        exp_remaining = exponent
        for i, color in enumerate(rev_exponent_colors):
            bit_exp = 2 ** (7-i)
            # print(f"i: {i}, bit_exp: {bit_exp}, exp_remaining: {exp_remaining}")
            if -exp_remaining >= bit_exp:
                E[color] = 1
                # print(f"Adding color {color} to E")
                exp_remaining += bit_exp

        return RedstoneFloat(s, M, E)
    
    def __repr__(self):
        def format_dict(d, start_index, direction):
            items = list(d.items())
            lines = []
            for i in range(0, len(items), 4):
                row = []
                for j in range(4):
                    if i + j < len(items):
                        color, value = items[i + j]
                        index = start_index + (i + j)*direction
                        row.append(f"{color}({index}): 0" if value == 0 else f"\033[33m{color}({index}): 1\033[0m")
                lines.append("\t".join(row))
            return "\n\t".join(lines)

        M_repr = format_dict(self.M, -1, -1)
        E_repr = format_dict(self.E, 0, 1)

        return f"RedstoneFloat: s= \033[33m{self.s}\033[0m\nM=\n\t{M_repr}\nE=\n\t{E_repr}"
    

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
    shift_next_colors = ["orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", ""] # 位移装置用
    next_colors = ["", "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", 
                  "light_gray", "cyan", "purple", "blue", "brown", "green", "red"]
    
    result = {color: 0 for color in colors}
    shift_device = {color: 0 for color in colors} # 模拟位移装置
    temp_shift_device = {color: 0 for color in colors} # 模拟不被存量转信器检测时的位移装置
    # 实际过程中应该是16次有序的独立的检测
    for i, color in enumerate(colors):
        shift = i + 1
        if m_a[color] > 0:
            shift_device = m_b.copy() # 模拟把m_b物品分配到位移装置中，实际过程中应该是16个检测装置
            # 执行shift次位移
            for _ in range(shift):
                # 类似，实际过程中应该是16次有序的独立的检测
                for color, shift_next_color in zip(colors, shift_next_colors):
                    if shift_device[color] >= 1: # 存量转信器发出信号
                        # 同时给予黄铜漏斗一个短暂解锁信号
                        shift_device[color] -= 1 # 信号指示黄铜漏斗漏掉1个物品
                        if shift_next_color: temp_shift_device[shift_next_color] += 1 # 信号指示呼叫一个物品进行位移，由于解锁信号很短，呼叫的物品不允许进入位移装置
                        # print(f"temp_shift_device: {temp_shift_device}")
                # 解锁信号结束，等待呼叫的物品进入位移装置，以准备下一次位移
                for color in colors:
                    shift_device[color] += temp_shift_device[color]
                    temp_shift_device[color] = 0 # 清空临时位移装置
                # print(f"shift_device: {shift_device}")
            for color in colors:
                result[color] += shift_device[color] # 模拟位移结果添加到结果箱
    # print(f"result: {result}")

    # 实际过程中应该是16次有序的独立的检测
    for color, next_color in zip(colors[::-1], next_colors[::-1]): # 注意此处是从末往前进位
        while result[color] >= 2: # 存量转信器发出信号
            result[color] -= 2 # 信号指示黄铜漏斗漏掉2个物品
            if next_color: result[next_color] += 1 # 信号指示投入一个物品表示进位
    # print(f"result: {result}")
    return result

def multiplying(a: RedstoneFloat, b: RedstoneFloat):
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

    return RedstoneFloat(new_s, raw_M, raw_E)

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
    
    return RedstoneFloat(new_s, new_M, new_E)

# 测试指数相加部分
# e_a = {"orange": 1}
# e_b = {"white": 1, "orange": 1}
# print(exponent_add(e_a, e_b))

# 测试to_float和from_float
# a = RedstoneFloat.from_float(1.4271e+00)
# # a = RedstoneFloat.from_float(0.75)
# print(a)
# print(a.to_float())
# b = RedstoneFloat.from_float(1.1470e-05)
# # b = RedstoneFloat.from_float(0.421875)
# print(b)
# print(b.to_float())

# 测试乘法
print("### a ###")
# a = RedstoneFloat.from_float(1.4271e+00)
# a = RedstoneFloat.from_float(-0.421875)
a = RedstoneFloat.from_float((0b11011/2**5) * 2**( -0b00000111 +2)) # 0.84375 * 2^(-5)
# a = RedstoneFloat.from_float(1.7347)
# a = RedstoneFloat.from_float((1/2) * 2**(-0b01001010 + 2))
print(a)

print("### b ###")
# b = RedstoneFloat.from_float(-1.1470e-05)
b = RedstoneFloat.from_float((0b11/2**2) * 2**( -0b00000100 +2)) # 0.75 * 2^(-2)
# b = RedstoneFloat.from_float(1.7347)
# b = RedstoneFloat.from_float((1/2) * 2**(-0b01101011 + 2))
print(b)

print("### r ###")
r = multiplying(a, b)
print(r)
print(r.to_float())