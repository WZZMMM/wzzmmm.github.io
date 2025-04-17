import jieba
import jieba.posseg as pseg
from collections import OrderedDict, defaultdict
import csv
from pyecharts import options as opts
from pyecharts.charts import Bar, WordCloud
from pyecharts.globals import ThemeType, SymbolType
from pyecharts.commons.utils import JsCode


def load_data():
    """加载数据"""
    # 加载人物列表
    characters = []
    with open('./data/红楼梦_character.txt', 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip().split()[0]
            characters.append(name)

    # 主要人物映射
    main_characters_map = {
        '宝玉': '贾宝玉',
        '黛玉': '林黛玉',
        '宝钗': '薛宝钗'
    }

    return characters, main_characters_map


def generate_character_wordcloud():
    """生成人物词云图"""
    characters, main_characters_map = load_data()
    jieba.load_userdict("./data/红楼梦_character.txt")

    # 读取全文
    with open('./data/红楼梦_full.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # 统计人物出现频率
    fre_char_dist = defaultdict(int)
    for word, tag in pseg.cut(text):
        # 处理主要人物的别名
        if word in main_characters_map:
            word = main_characters_map[word]
        # 只统计人物名词
        if tag == 'nr' and word in characters:
            fre_char_dist[word] += 1

    # 转换为词云需要的格式
    wordcloud_data = [(name, freq) for name, freq in fre_char_dist.items()]

    # 生成词云
    wc = (
        WordCloud()
        .add("", wordcloud_data, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="《红楼梦》人物词云"),
            tooltip_opts=opts.TooltipOpts(formatter="{b}: {c}次")
        )
    )
    wc.render('./output/character_wordcloud.html')

    # 保存词云数据到CSV
    with open('./output/character_wordcloud.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['人物', '出现频次'])
        writer.writerows(sorted(wordcloud_data, key=lambda x: x[1], reverse=True))

    return wordcloud_data


def save_top3_to_csv(top3_data, filename):
    """保存每回前三数据到CSV"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['回目', '第一名', '频次', '第二名', '频次', '第三名', '频次'])
        # 写入数据
        for chap in range(1, 121):
            top3 = top3_data[chap - 1]  # 修改为列表索引访问
            row = [chap]  # 直接使用数字，不加"第x回"
            for char, count in top3:
                row.extend([char, count])
            # 如果不足3个，补空值
            while len(row) < 7:
                row.extend(["", 0])
            writer.writerow(row)


def save_main_chars_to_csv(main_chars_data, filename):
    """保存主要人物数据到CSV"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['回目', '贾宝玉', '林黛玉', '薛宝钗'])
        # 写入数据
        for chap in range(1, 121):
            row = [chap]  # 直接使用数字，不加"第x回"
            for char in ['贾宝玉', '林黛玉', '薛宝钗']:
                row.append(main_chars_data[char][chap - 1])
            writer.writerow(row)


def top3_appear_per_chapter():
    """每一回出场次数前三的角色（并列柱状图）"""
    characters, main_characters_map = load_data()
    jieba.load_userdict("./data/红楼梦_character.txt")

    top3_data = []  # 改为列表存储每回前三数据
    main_chars_data = {  # 保存主要人物数据
        '贾宝玉': [],
        '林黛玉': [],
        '薛宝钗': []
    }

    # 准备图表数据
    chap_names = [f"第{i}回" for i in range(1, 121)]

    # 遍历120个章节
    for i in range(1, 121):
        chapter_file = f"./data/红楼梦_chap/{i:03d}.txt"
        with open(chapter_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # 统计本章人物出现频率
        fre_char_dist = defaultdict(int)
        for word, tag in pseg.cut(text):
            # 处理主要人物的别名
            if word in main_characters_map:
                word = main_characters_map[word]
            # 只统计人物名词
            if tag == 'nr' and word in characters:
                fre_char_dist[word] += 1

        # 记录主要人物数据
        for char in ['贾宝玉', '林黛玉', '薛宝钗']:
            main_chars_data[char].append(fre_char_dist.get(char, 0))

        # 获取前三名并保存
        sorted_chars = sorted(fre_char_dist.items(), key=lambda x: x[1], reverse=True)
        top3_data.append(sorted_chars[:3])

    # 保存数据到CSV
    save_top3_to_csv(top3_data, './output/top3_characters_per_chapter.csv')
    save_main_chars_to_csv(main_chars_data, './output/main_characters_appear.csv')

    # 准备前三名数据（为了并列显示）
    top1_data = []
    top2_data = []
    top3_data_list = []  # 避免变量名冲突
    top1_names = []
    top2_names = []
    top3_names = []

    for chap in range(120):  # 0-119
        top3 = top3_data[chap]
        # 第一名数据
        if len(top3) > 0:
            top1_data.append(top3[0][1])
            top1_names.append(top3[0][0])
        else:
            top1_data.append(0)
            top1_names.append("")
        # 第二名数据
        if len(top3) > 1:
            top2_data.append(top3[1][1])
            top2_names.append(top3[1][0])
        else:
            top2_data.append(0)
            top2_names.append("")
        # 第三名数据
        if len(top3) > 2:
            top3_data_list.append(top3[2][1])
            top3_names.append(top3[2][0])
        else:
            top3_data_list.append(0)
            top3_names.append("")

    # 生成并列柱状图
    bar = Bar(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT,
        width="1600px",
        height="600px"
    ))

    # 自定义x轴标签格式
    bar.add_xaxis(chap_names)

    # 添加三个系列（并列显示）
    bar.add_yaxis(
        "第一名",
        top1_data,
        category_gap="40%",  # 控制同一分类下柱子的间距
        gap="10%",  # 控制不同分类下柱子的间距
        itemstyle_opts=opts.ItemStyleOpts(color="#c23531"),
        label_opts=opts.LabelOpts(is_show=False)
    )
    bar.add_yaxis(
        "第二名",
        top2_data,
        itemstyle_opts=opts.ItemStyleOpts(color="#2f4554"),
        label_opts=opts.LabelOpts(is_show=False)
    )
    bar.add_yaxis(
        "第三名",
        top3_data_list,
        itemstyle_opts=opts.ItemStyleOpts(color="#61a0a8"),
        label_opts=opts.LabelOpts(is_show=False)
    )

    # 设置全局选项
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="《红楼梦》每回出场次数前三人物"),
        toolbox_opts=opts.ToolboxOpts(),
        datazoom_opts=[opts.DataZoomOpts()],
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(rotate=45),
            splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        yaxis_opts=opts.AxisOpts(
            name="出场次数",
            splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter=JsCode(
                """
                function(params) {
                    var chapIndex = params.dataIndex;
                    var chapName = params.name;
                    var top1Name = %s[chapIndex];
                    var top2Name = %s[chapIndex];
                    var top3Name = %s[chapIndex];
                    var top1Value = %s[chapIndex];
                    var top2Value = %s[chapIndex];
                    var top3Value = %s[chapIndex];

                    var result = chapName + '<br/>';

                    if (top1Name && top1Value > 0) {
                        result += '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#c23531;"></span>'
                               + '第一名: ' + top1Name + ' (' + top1Value + '次)<br/>';
                    }
                    if (top2Name && top2Value > 0) {
                        result += '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#2f4554;"></span>'
                               + '第二名: ' + top2Name + ' (' + top2Value + '次)<br/>';
                    }
                    if (top3Name && top3Value > 0) {
                        result += '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:#61a0a8;"></span>'
                               + '第三名: ' + top3Name + ' (' + top3Value + '次)';
                    }

                    return result;
                }
                """ % (
                    str(top1_names), str(top2_names), str(top3_names),
                    str(top1_data), str(top2_data), str(top3_data_list)
                )
            )
        )
    )

    bar.render('./output/top3_appear_per_chapter.html')
    return main_chars_data


def main_characters_appear(main_chars_data):
    """主要人物出场频次"""
    main_characters = ['贾宝玉', '林黛玉', '薛宝钗']
    chapters = list(range(1, 121))

    # 生成柱状图
    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    bar.add_xaxis([f"第{i}回" for i in chapters])

    # 添加三个主要人物的数据
    bar.add_yaxis("贾宝玉", main_chars_data['贾宝玉'],
                  itemstyle_opts=opts.ItemStyleOpts(color="#c23531"))
    bar.add_yaxis("林黛玉", main_chars_data['林黛玉'],
                  itemstyle_opts=opts.ItemStyleOpts(color="#2f4554"))
    bar.add_yaxis("薛宝钗", main_chars_data['薛宝钗'],
                  itemstyle_opts=opts.ItemStyleOpts(color="#61a0a8"))

    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="《红楼梦》宝、黛、钗出场频次"),
        toolbox_opts=opts.ToolboxOpts(),
        datazoom_opts=[opts.DataZoomOpts()],
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        yaxis_opts=opts.AxisOpts(name="出场次数")
    )
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.render('./output/main_characters_appear.html')


if __name__ == '__main__':
    # 生成人物词云图
    print("正在生成人物词云...")
    generate_character_wordcloud()

    # 生成每回前三人物图表并获取主要人物数据
    print("正在分析每回出场人物...")
    main_chars_data = top3_appear_per_chapter()

    # 生成主要人物出场频次图表
    print("正在分析主要人物出场频次...")
    main_characters_appear(main_chars_data)

    print("\n分析完成！已生成以下文件：")
    print("- character_wordcloud.html (人物词云图)")
    print("- character_wordcloud.csv (人物频次数据)")
    print("- top3_appear_per_chapter.html (每回前三人物并列柱状图)")
    print("- main_characters_appear.html (宝黛钗出场频次柱状图)")
    print("- top3_characters_per_chapter.csv (每回前三人物数据)")
    print("- main_characters_appear.csv (宝黛钗出场频次数据)")