import re
import os
from zhconv import convert


def normalize_title(title):
    """标准化标题，去除多余空格"""
    return re.sub(r'\s+', ' ', title.strip())


def preprocess_hongloumeng(input_file, output_file, chap_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = convert(f.read(), 'zh-cn')  # 先整体转换为简体

    # 1. 找到正文开始的位置（简体版）
    start_marker = convert("第一回　甄士隱夢幻識通靈　賈雨村風塵懷閨秀", 'zh-cn')
    start_pos = text.find(start_marker)
    if start_pos == -1:
        raise ValueError("无法找到正文开始位置")
    text = text[start_pos:]

    # 2. 确保章节目录存在
    os.makedirs(chap_dir, exist_ok=True)

    # 3. 改进的正则表达式，兼容多种编号格式
    chapter_pattern = re.compile(
        r'^(第(?:[一二三四五六七八九十零百]+|[\d零一二三四五六七八九十百]+)回)\s*([^\n]+)',
        re.MULTILINE
    )
    matches = list(chapter_pattern.finditer(text))

    # 4. 验证章回数量
    if len(matches) != 120:
        print(f"警告：发现{len(matches)}回，预期120回")

    chapters = []
    for i, match in enumerate(matches):
        chapter_num = f"{i + 1:03d}"  # 001-120
        hanzi_chapter = match.group(1)  # 汉字章回序号
        chapter_title = normalize_title(match.group(2))  # 标题

        # 确定当前回的范围
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_content = text[start_pos:end_pos]

        # 删除非正文内容
        chapter_content = re.sub(r'【.*?】', '', chapter_content)  # 批语
        chapter_content = re.sub(r'〈.*?〉', '', chapter_content)  # 按语
        if '注释' in chapter_content:  # 简体后的注释标记
            chapter_content = chapter_content[:chapter_content.find('注释')]

        # 生成格式化内容
        formatted_chapter = (
            f"\n--------------------\n{chapter_num}\n"
            f"--------------------\n"
            f"{hanzi_chapter} {chapter_title}\n"
            f"{chapter_content[len(match.group(0)):].strip()}"  # 去除标题行
        )

        # 保存单个章回文件
        chap_file = os.path.join(chap_dir, f"{chapter_num}.txt")
        with open(chap_file, 'w', encoding='utf-8') as f:
            f.write(formatted_chapter)

        chapters.append(formatted_chapter)

    # 保存完整文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(chapters))


# 使用示例
input_file = './data/紅樓夢-通行版一百二十回.txt'
output_file = './data/红楼梦_full.txt'
chap_dir = './data/红楼梦_chap/'

preprocess_hongloumeng(input_file, output_file, chap_dir)
print(f"处理完成！完整版保存到 {output_file}")
print(f"分章回文件保存到 {chap_dir} 目录")