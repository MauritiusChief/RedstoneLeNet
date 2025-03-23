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
        # 最大可表示的数为 2^(2-0) = 2^2 = 4，最小可表示的数为 2^( 2 - (1+2+4+8...+128) ) = 2^(-253)
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
    