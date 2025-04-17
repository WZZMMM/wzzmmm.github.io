import os
import re
import jieba
import jieba.posseg as pseg
import math
from collections import defaultdict
from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.commons.utils import JsCode
from pyecharts.globals import CurrentConfig, ThemeType

# 配置CDN资源
CurrentConfig.ONLINE_HOST = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/"


def setup_paths():
    """设置文件路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    paths = {
        "full_text": os.path.join(data_dir, "红楼梦_full.txt"),
        "chapter_dir": os.path.join(data_dir, "红楼梦_chap"),
        "character": os.path.join(data_dir, "红楼梦_character.txt"),
        "stopwords": os.path.join(data_dir, "stopwords")
    }
    for path in paths.values():
        if not os.path.exists(path):
            raise FileNotFoundError(f"路径不存在: {path}")
    return paths


def load_characters(character_path):
    """加载人物字典"""
    characters = set()
    alias_map = {}
    with open(character_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0]
                    characters.add(name)
                    if name == "宝玉":
                        alias_map["贾宝玉"] = name
                    elif name == "黛玉":
                        alias_map["林黛玉"] = name
                    elif name == "宝钗":
                        alias_map["薛宝钗"] = name
    return characters, alias_map


def load_stopwords(stopwords_dir):
    """加载停用词"""
    stopwords = set()
    for fname in os.listdir(stopwords_dir):
        with open(os.path.join(stopwords_dir, fname), 'r', encoding='utf-8') as f:
            stopwords.update(line.strip() for line in f if line.strip())
    return stopwords


def load_text_data(full_path, chapter_dir):
    """加载文本内容"""
    if os.path.exists(chapter_dir) and os.listdir(chapter_dir):
        text = []
        for fname in sorted(os.listdir(chapter_dir)):
            if fname.endswith('.txt'):
                with open(os.path.join(chapter_dir, fname), 'r', encoding='utf-8') as f:
                    text.append(f.read())
        return "\n".join(text)
    else:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()


def cut_sentences(text):
    """中文分句"""
    sentences = re.split(r'([。！？\?])', text)
    return [s1 + s2 for s1, s2 in zip(sentences[::2], sentences[1::2])]


def analyze_co_occurrence(text, characters, alias_map, window_size=3):
    """分析共现关系"""
    for char in characters:
        jieba.add_word(char, tag='nr')

    sentences = cut_sentences(text)
    freq = defaultdict(int)
    co_occur = defaultdict(int)
    co_occur_detail = defaultdict(dict)

    for i in range(0, len(sentences), window_size):
        window = "".join(sentences[i:i + window_size])
        words = pseg.cut(window)
        current_chars = set()

        for word, flag in words:
            if flag == 'nr':
                normalized = alias_map.get(word, word)
                if normalized in characters:
                    current_chars.add(normalized)

        # 更新统计
        for char in current_chars:
            freq[char] += 1

        # 更新共现
        chars_list = list(current_chars)
        for j in range(len(chars_list)):
            for k in range(j + 1, len(chars_list)):
                char1, char2 = sorted((chars_list[j], chars_list[k]))
                co_occur[(char1, char2)] += 1
                co_occur_detail[char1][char2] = co_occur_detail[char1].get(char2, 0) + 1
                co_occur_detail[char2][char1] = co_occur_detail[char2].get(char1, 0) + 1

    return freq, co_occur, co_occur_detail


def filter_data(freq, co_occur, co_occur_detail, top_n=120, main_chars=None):
    """筛选数据"""
    top_chars = {char for char, _ in sorted(freq.items(), key=lambda x: -x[1])[:top_n]}

    if main_chars:
        main_chars = set(main_chars)
        top_chars.update(main_chars)
        related_chars = set()
        for pair in co_occur:
            if pair[0] in main_chars or pair[1] in main_chars:
                related_chars.update(pair)
        top_chars.update(related_chars)

    # 过滤数据
    filtered_freq = {k: v for k, v in freq.items() if k in top_chars}
    filtered_co = {
        pair: count for pair, count in co_occur.items()
        if pair[0] in top_chars and pair[1] in top_chars
           and (not main_chars or (pair[0] in main_chars or pair[1] in main_chars))
    }

    filtered_co_detail = {}
    for char in top_chars:
        if char in co_occur_detail:
            filtered_co_detail[char] = {
                k: v for k, v in co_occur_detail[char].items()
                if k in top_chars
            }

    return filtered_freq, filtered_co, filtered_co_detail


def get_color(name):
    """获取节点颜色"""
    color_map = {
        "宝玉": "#c23531",
        "黛玉": "#2f4554",
        "宝钗": "#61a0a8",
    }
    return color_map.get(name, "#d48265")


def create_graph(freq, co_occur, co_occur_detail, output_file, main_char=None):
    """创建关系图"""
    # 节点数据（修复频次显示问题）
    max_freq = max(freq.values()) if freq else 1
    nodes = []
    for name, count in freq.items():
        relations = sorted(
            [(k, v) for k, v in co_occur_detail.get(name, {}).items() if k != name],
            key=lambda x: -x[1]
        )[:5]

        nodes.append({
            "name": name,
            "value": count,  # 确保传递频次数据
            "symbolSize": 8 + 25 * (math.log(count + 1) / math.log(max_freq + 1)),
            "itemStyle": {"color": get_color(name)},
            "label": {"show": True, "fontSize": 10},
            "relations": relations
        })

    # 边数据
    max_co = max(co_occur.values()) if co_occur else 1
    links = [{
        "source": pair[0],
        "target": pair[1],
        "value": count,
        "lineStyle": {
            "width": 0.3 + 2 * (count / max_co),
            "opacity": 0.7,
            "curveness": 0.1
        }
    } for pair, count in co_occur.items()]

    # 修正后的tooltip格式化函数
    tooltip_formatter = JsCode("""
        function(params) {
            if (params.dataType === 'node') {
                var relations = params.data.relations || [];
                var result = [
                    '<div style="font-size:14px;font-weight:bold">' + params.name + '</div>',
                    '<div style="font-size:12px;color:#666">出现频次: ' + params.data.value + '</div>'
                ];
                if (relations.length > 0) {
                    result.push('<div style="margin:5px 0 3px 0;color:#666">主要共现:</div>');
                    relations.forEach(function(item) {
                        result.push('<div style="font-size:12px">• ' + item[0] + ': ' + item[1] + '次</div>');
                    });
                }
                return result.join('');
            } else if (params.dataType === 'edge') {
                return [
                    '<div style="font-size:14px;font-weight:bold">' + params.data.source + ' ↔ ' + params.data.target + '</div>',
                    '<div style="font-size:12px">共现次数: ' + params.data.value + '次</div>'
                ].join('');
            }
            return '';
        }
    """)

    # 创建图表
    graph = (
        Graph(init_opts=opts.InitOpts(
            width="720px",
            height="720px",
            theme=ThemeType.LIGHT,
            page_title="红楼梦人物共现关系",
            js_host=CurrentConfig.ONLINE_HOST
        ))
        .add(
            series_name="人物共现关系",
            nodes=nodes,
            links=links,
            repulsion=200,
            edge_length=150,
            gravity=0.03,
            layout="force",
            is_draggable=True,
            label_opts=opts.LabelOpts(
                position="right",
                font_size=10,
                color="#333"
            ),
            linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.1),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter=tooltip_formatter,
                background_color="rgba(255,255,255,0.95)",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(font_size=12)
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"《红楼梦》{'人物共现网络(出现频次Top120)' if not main_char else main_char + '共现关系图'}",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_size=16)
            )
        )
    )

    # 渲染完整HTML
    graph.render(output_file)
    print(f"已生成: {output_file}")


def main():
    try:
        # 1. 加载数据
        paths = setup_paths()
        text = load_text_data(paths["full_text"], paths["chapter_dir"])
        characters, alias_map = load_characters(paths["character"])
        stopwords = load_stopwords(paths["stopwords"])

        # 2. 分析数据
        freq, co_occur, co_occur_detail = analyze_co_occurrence(
            text, characters, alias_map
        )

        # 3. 生成全图 (Top120)
        f_freq, f_co, f_detail = filter_data(
            freq, co_occur, co_occur_detail, top_n=120
        )
        create_graph(f_freq, f_co, f_detail, "./output/co_occurrence.html")

        # 4. 生成主角图
        for char, pinyin in [("宝玉", "baoyu"), ("黛玉", "daiyu"), ("宝钗", "baochai")]:
            cf_freq, cf_co, cf_detail = filter_data(
                freq, co_occur, co_occur_detail, main_chars=[char]
            )
            create_graph(cf_freq, cf_co, cf_detail,
                         f"./output/co_occurrence_{pinyin}.html", char)

    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
