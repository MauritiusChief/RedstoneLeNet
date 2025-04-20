import math


class RedstoneFloat:
    def __init__(self, s: str, M: dict[str: int], E: dict[str: int]):
        """
        :param s: 符号位，'obsidian' 表示 1，'' 表示 0
        :param M: 尾数部分，dict 形式的 16 色
        :param E: 指数部分，dict 形式的 8 色混凝土
        """
        self.s = s  # 直接存储字符串，如 'obsidian' 或 ''
        self.M = M  # 以字典存储尾数部分
        self.E = E  # 以字典存储指数部分
    
    def _decode_mantissa(self) -> float:
        """
        仅to_float使用
        将集合转换为尾数的浮点数表示
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
        # 最大可表示的数为 2^(2-0) = 2^2 = 4，最小可表示的数为 2^( 2 - (1+2+4+8...+128) ) = 2^(-253)
        return value
    
    def to_float(self) -> float:
        sign = (-1) ** (self.s == 'obsidian')
        mantissa = self._decode_mantissa()
        exponent = self._decode_exponent()
        print(f"sign: {sign}, mantissa: {mantissa}, exponent: {-exponent}(+2)")
        return sign * mantissa * (2**(2-exponent))

    @staticmethod
    def from_string(encoded: str) -> 'RedstoneFloat':
        """
        从格式为 ".mantissa e -exponent (+2)" 的字符串创建 RedstoneFloat。
        例如：".11011e-10000(+2)" 或 "-.1100000000000000e-00000010(+2)"
        """
        import re

        # 解析字符串
        match = re.fullmatch(r'(-?)\.(\d{1,16})e-(\d{1,8})\(\+2\)', encoded)
        if not match:
            raise ValueError("Invalid format. Expected format: (-?).[01]{1,16}e-[01]{1,8}(+2)")

        sign_str, mantissa_str, exponent_str = match.groups()

        # 解析符号
        s = 'obsidian' if sign_str == '-' else ''

        # 填补 mantissa 和 exponent 到固定长度
        mantissa_str = mantissa_str.ljust(16, '0')
        exponent_str = exponent_str.rjust(8, '0')

        # 颜色映射
        mantissa_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
                           "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
        exponent_colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray"]

        # 构造 M 字典
        M = {
            color: int(bit)
            for color, bit in zip(mantissa_colors, mantissa_str)
        }

        # 构造 E 字典
        exponent_bits = list(map(int, exponent_str))
        # print(f"exponent_str:{exponent_str}, exponent_bits:{exponent_bits}")
        exponent_value = sum(b << i for i, b in enumerate(reversed(exponent_bits)))  # interpret as binary
        # print(f"exponent_value:{exponent_value}")
        E = {}
        for i, color in enumerate((exponent_colors)):
            bit = (exponent_value >> i) & 1
            E[color] = bit

        return RedstoneFloat(s, M, E)
    
    @staticmethod
    def redstr(value: float) -> str:

        if value == 0:
            return ".0e-0(+2)"

        # 处理符号
        sign_str = '-' if value < 0 else ''
        abs_value = abs(value)

        # 拆分为尾数与指数
        exponent = math.floor(math.log2(abs_value))
        mantissa = abs_value / (2 ** exponent)

        # 归一化 mantissa 到 [0.5, 1)
        if mantissa >= 1:
            mantissa /= 2
            exponent += 1

        exponent -= 2  # 偏移 +2 进入编码阶段（实际存储的是 -exponent）

        # 构造 mantissa 位串
        mantissa_bits = ''
        remaining = mantissa
        for i in range(16):
            bit_value = 2 ** (-i - 1)
            if remaining >= bit_value:
                mantissa_bits += '1'
                remaining -= bit_value
            else:
                mantissa_bits += '0'

        # 去除 mantissa 尾部 0
        mantissa_bits = mantissa_bits.rstrip('0') or '0'

        # 构造 exponent 位串（处理为 -exponent，正整数形式）
        exponent_val = -exponent
        if exponent_val < 0 or exponent_val >= 256:
            raise ValueError("Exponent out of range for 8-bit encoding")

        exponent_bits = bin(exponent_val)[2:].zfill(8)
        exponent_bits = exponent_bits.lstrip('0') or '0'

        return f"{sign_str}.{mantissa_bits}e-{exponent_bits}(+2)"
    
    def __repr__(self):
        def format_dict(d, start_index, end_index, itemtype):
            items = list(d.items())
            if (itemtype == "混凝土"): 
                items = items[::-1]
            lines = []
            indexes = list(range(start_index, end_index-1, -1))
            # print(indexes)
            for i in range(0, len(items), 4):
                row = []
                for j in range(4):
                    if i + j < len(items):
                        color, value = items[i + j]
                        color = localize[color]+itemtype
                        # print(i+j)
                        index = indexes[i + j]
                        row.append(f"{color}({index}): 0   " if value == 0 else f"\033[33m{color}({index}): 1\033[0m   ")
                lines.append("\t".join(row))
            return "\n\t".join(lines)

        localize = {"white":"白色", "orange":"橙色", "magenta":"品红色", "light_blue":"淡蓝色", 
                    "yellow":"黄色", "lime":"黄绿色", "pink":"粉红色", "gray":"灰色", 
                    "light_gray":"淡灰色", "cyan":"青色", "purple":"紫色", "blue":"蓝色", 
                    "brown":"棕色", "green":"绿色", "red":"红色", "black":"黑色"}
        M_repr = format_dict(self.M, -1, -16, "羊毛")
        E_repr = format_dict(self.E, 7, 0, "混凝土")
        
        obsidian = ""
        if self.s: obsidian = "黑曜石"
        return f"RedstoneFloat: s= \033[33m{obsidian}\033[0m\nM=\n\t{M_repr}\nE=\n\t{E_repr}"
    