导入 math
从 math 导入 sqrt 作为 root_fn

令 共享_计数器 = 3

函数 增加_全局():
    全局 共享_计数器
    共享_计数器 = 共享_计数器 + 2
    返回 共享_计数器

函数 创建_计数器(开始值):
    令 total = 开始值
    函数 步进():
        非局部 total
        total = total + 1
        返回 total
    返回 步进

令 下一个_计数器 = 创建_计数器(5)
令 第一步 = 下一个_计数器()
令 第二步 = 下一个_计数器()

使用 打开("tmp_complete_en.txt", "w", encoding="utf-8") 作为 写入_句柄:
    写入_句柄.write("ok")

令 文件_文本 = ""
使用 打开("tmp_complete_en.txt", "r", encoding="utf-8") 作为 读取_句柄:
    文件_文本 = 读取_句柄.read()

令 配对_项 = 列表(配对([1, 2, 3], [4, 5, 6]))
令 唯一_值 = 集合([1, 1, 2, 3])
令 固定_值 = 元组([10, 20, 30])
令 第一个_元素, *中间_元素, 最后_元素 = [1, 2, 3, 4]
令 合并_映射 = {**{"x": 1}, **{"y": 2}}

函数 格式_标签(a, /, *, b):
    返回 f"{a}-{b:.1f}"

令 标签_格式化 = 格式_标签(7, b=3.5)
令 种子 = 0
令 胡须_值 = (种子 := 种子 + 9)

类 计数器_盒子:
    函数 __init__(self, 起始_基值):
        self.值 = 起始_基值

类 计数器_子盒子(计数器_盒子):
    函数 __init__(self, 起始_基值):
        父类(计数器_子盒子, self).__init__(起始_基值)
        self.值 = self.值 + 1

函数 生成_三个():
    对于 索引 里 范围(3):
        产出 索引

令 总_生成 = 总和(生成_三个())
令 处理_的 = 假

尝试:
    如果 长度(唯一_值) > 2:
        抛出 ValueError("boom")
除了 ValueError 作为 处理_错误:
    处理_的 = 真
最终:
    令 根_值 = 整数(root_fn(16))

令 临时_值 = 99
删除 临时_值

令 循环_累积 = 0
对于 n 里 范围(6):
    如果 n == 0:
        过
    如果 n == 4:
        终止
    如果 n % 2 == 0:
        继续
    循环_累积 = 循环_累积 + n

令 标志_正常 = 真 且 非 假
断言 标志_正常

令 子_盒子 = 计数器_子盒子(40)

打印(增加_全局())
打印(第一步, 第二步)
打印(文件_文本)
打印(长度(配对_项), 长度(唯一_值), 固定_值[1])
打印(第一个_元素, 中间_元素, 最后_元素)
打印(子_盒子.值)
打印(总_生成, 根_值, 处理_的)
打印(合并_映射["x"] + 合并_映射["y"], 标签_格式化, 胡须_值)
打印(循环_累积)
打印(共享_计数器 是 空)

# Loop else clauses
令 元素_找到 = 假
对于 元素 里 范围(3):
    如果 元素 == 10:
        元素_找到 = 真
        终止
否则:
    元素_找到 = "not_found"

令 当_否则_值 = 0
当 当_否则_值 < 2:
    当_否则_值 = 当_否则_值 + 1
否则:
    当_否则_值 = 当_否则_值 + 10

# Starred unpacking variations
令 a, *剩余 = [10, 20, 30, 40]
令 *init, b = [10, 20, 30, 40]
令 c, *中间, d = [10, 20, 30, 40]

# Set comprehension
令 平方_集合 = {x * x 对于 x 里 范围(5)}

# Extended builtins
令 幂_结果 = 幂(2, 8)
令 divmod_结果 = 商余(17, 5)

# Yield from generator
函数 委托_生成器():
    产出 从 范围(3)

令 委托_的 = 列表(委托_生成器())

打印(元素_找到, 当_否则_值)
打印(a, 剩余, init, b, c, 中间, d)
打印(排序(平方_集合))
打印(幂_结果, divmod_结果)
打印(委托_的)

# Numeric literals
令 shiliujinzhi_shu = 0xFF
令 bajinzhi_shu = 0o17
令 erjinzhi_shu = 0b1010
令 kexue_jishu_shu = 1.5e3

# Augmented assignments
令 zengliang_zhi = 10
zengliang_zhi += 5
zengliang_zhi -= 2
zengliang_zhi *= 3
zengliang_zhi //= 4
zengliang_zhi %= 3

# Bitwise operators
令 bi_yu_zhi = 0b1010 & 0b1100
令 bi_huo_zhi = 0b1010 | 0b0101
令 bi_yihuo_zhi = 0b1010 ^ 0b1111
令 zuoyi_zhi = 1 << 3
令 youyi_zhi = 64 >> 2

# Chained assignment
令 lianjia = lianyi = lianbing = 0

# Type annotations
令 leixing_zhi: int = 99

函数 zhujie_hanshu(x: int, y: float) -> str:
    返回 str(x + y)

# Ternary expression
令 sanyuan_zhi = "yes" 如果 leixing_zhi > 0 否则 "no"

# Default params, *args, **kwargs
函数 duocanshu_hanshu(base, extra=1, *args, **kwargs):
    返回 base + extra + sum(args)
令 duocanshu_jieguo = duocanshu_hanshu(10, 2, 3, 4, key=5)

# Lambda
令 pingfang_hanshu = 匿名 x: x * x

# List/dict comprehensions 且 generator expression
令 liebiao_tuidao = [x * 2 对于 x 里 range(4)]
令 zidian_tuidao = {str(k): k * k 对于 k 里 range(3)}
令 shengcheng_tuidao = list(x + 1 对于 x 里 range(3))
令 qiantao_tuidao = [i + j 对于 i 里 range(2) 对于 j 里 range(2)]
令 guolv_tuidao = [x 对于 x 里 range(6) 如果 x % 2 == 0]

# 尝试/除了/否则
令 changshi_fouze_zhi = 0
尝试:
    changshi_fouze_zhi = int("7")
除了 ValueError:
    changshi_fouze_zhi = -1
否则:
    changshi_fouze_zhi += 1

# Exception chaining
令 lianshi_yichang = 假
尝试:
    尝试:
        抛出 ValueError("v")
    除了 ValueError 作为 ve:
        抛出 RuntimeError("r") 从 ve
除了 RuntimeError:
    lianshi_yichang = 真

# Multiple 除了 handlers
令 duo_yichang_zhi = 0
尝试:
    抛出 TypeError("t")
除了 ValueError:
    duo_yichang_zhi = 1
除了 TypeError:
    duo_yichang_zhi = 2

# Match/情况 使用 默认
令 pipei_zhi = 2
令 pipei_jieguo = "other"
匹配 pipei_zhi:
    情况 1:
        pipei_jieguo = "one"
    情况 2:
        pipei_jieguo = "two"
    默认:
        pipei_jieguo = "默认"

# Decorator
函数 jiabeiqi(func):
    函数 baozhuangqi(*args, **kwargs):
        返回 func(*args, **kwargs) * 2
    返回 baozhuangqi

@jiabeiqi
函数 shi():
    返回 10

令 zhuangshi_jieguo = shi()

# Multiple inheritance, static/类 methods, property
类 HunruLei:
    函数 hunhe(self):
        返回 1

类 JiLeiEr:
    函数 __init__(self, start):
        self.value = start

类 ZuheLei(JiLeiEr, HunruLei):
    @staticmethod
    函数 biaoqian():
        返回 "combined"
    @classmethod
    函数 goujian(cls, v):
        返回 cls(v)
    @property
    函数 shuangbei_shuxing(self):
        返回 self.value * 2

令 zuhe_duixiang = ZuheLei.goujian(3)
令 shuxing_zhi = zuhe_duixiang.shuangbei_shuxing

# Docstring
函数 dai_wendang():
    """Has a docstring."""
    返回 真

print(shiliujinzhi_shu, bajinzhi_shu, erjinzhi_shu, kexue_jishu_shu)
print(zengliang_zhi, bi_yu_zhi, bi_huo_zhi, bi_yihuo_zhi, zuoyi_zhi, youyi_zhi)
print(lianjia, lianyi, lianbing)
print(leixing_zhi, zhujie_hanshu(3, 1.5), sanyuan_zhi)
print(duocanshu_jieguo, pingfang_hanshu(5))
print(liebiao_tuidao, zidian_tuidao, shengcheng_tuidao)
print(qiantao_tuidao, guolv_tuidao)
print(changshi_fouze_zhi, lianshi_yichang, duo_yichang_zhi)
print(pipei_jieguo, zhuangshi_jieguo, shuxing_zhi)
print(dai_wendang())
