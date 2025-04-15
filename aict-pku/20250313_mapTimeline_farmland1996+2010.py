from pyecharts.charts import Map, Timeline
from pyecharts import options as opts

data_dict = {
    "全国": [0, 13003.93, -203.27, 12800.67],
    "北京市": [11, 34.4, 0, 34.4],
    "天津市": [12, 48.53, 0, 48.53],
    "河北省": [13, 688.33, -3, 685.33],
    "山西省": [14, 458.87, -3.6, 455.27],
    "内蒙古自治区": [15, 820.07, -44.33, 775.73],
    "辽宁省": [21, 417.47, 0, 417.47],
    "吉林省": [22, 557.87, 0, 557.87],
    "黑龙江省": [23, 1177.27, 6.67, 1183.93],
    "上海市": [31, 31.53, 0, 31.53],
    "江苏省": [32, 506.2, 0, 506.2],
    "浙江省": [33, 212.53, -6.93, 205.6],
    "安徽省": [34, 597.2, 0, 597.2],
    "福建省": [35, 143.47, -0.33, 143.13],
    "江西省": [36, 299.33, -1.33, 298],
    "山东省": [37, 768.93, 0, 768.93],
    "河南省": [41, 811.07, 0, 811.07],
    "湖北省": [42, 494.93, -18.67, 476.27],
    "湖南省": [43, 395.27, 0, 395.27],
    "广东省": [44, 327.2, -1.47, 325.73],
    "广西壮族自治区": [45, 440.8, -5.33, 435.47],
    "海南省": [46, 76.2, -0.87, 75.33],
    "重庆市": [50, 254.53, -18.6, 235.93],
    "四川省": [51, 662.4, -27.47, 634.93],
    "贵州省": [52, 490.33, -30.47, 459.87],
    "云南省": [53, 642.13, -32.33, 609.8],
    "西藏自治区": [54, 36.27, 0.67, 36.93],
    "陕西省": [61, 514.07, -38.93, 475.13],
    "甘肃省": [62, 502.47, -5.13, 497.33],
    "青海省": [63, 68.8, -1, 67.8],
    "宁夏回族自治区": [64, 126.87, 0, 126.87],
    "新疆维吾尔自治区": [65, 398.53, 55.87, 454.4]
}

# 创建 Timeline 对象
tl = Timeline()

# 1996年数据
data_1996 = [(key, value[1]) for key, value in data_dict.items() if key != "全国"]
map_1996 = (
    Map()
    .add(
        "1996年实有耕地面积（单位：万公顷）",
        data_pair=data_1996,
        maptype="china",
        is_map_symbol_show=False,  # 不描点
        label_opts=opts.LabelOpts(is_show=False),  # 隐藏省份名称
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="1996年全国实有耕地面积",
            subtitle="数据来源：国办发〔1999〕34号"
        ),
        visualmap_opts=opts.VisualMapOpts(min_=20, max_=1500, is_piecewise=True),
    )
)
tl.add(map_1996, "1996年")

# 2010年数据
data_2010 = [(key, value[3]) for key, value in data_dict.items() if key != "全国"]
map_2010 = (
    Map()
    .add(
        "2010年耕地保有量指标（单位：万公顷）",
        data_pair=data_2010,
        maptype="china",
        is_map_symbol_show=False,  # 不描点
        label_opts=opts.LabelOpts(is_show=False),  # 隐藏省份名称
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="2010年全国耕地保有量指标",
            subtitle="数据来源：国办发〔1999〕34号"
        ),
        visualmap_opts=opts.VisualMapOpts(min_=20, max_=1500, is_piecewise=True),
    )
)
tl.add(map_2010, "2010年")

# 渲染轮播地图
tl.render('./output/全国耕地保有量1996+2010_mapTimeline.html')
