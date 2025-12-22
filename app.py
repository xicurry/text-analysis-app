"""
URL文本词频分析可视化系统
功能：
1. 抓取指定URL的文章文本内容
2. 中文分词与词频统计（过滤停用词、低频词）
3. 基于Pyecharts的多图表可视化（9种图表）
4. Streamlit交互式界面（侧边栏图表筛选、低频词过滤）

"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
import re
from collections import Counter
import numpy as np
# Pyecharts相关
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Radar, Scatter, HeatMap, TreeMap, Polar
from streamlit_echarts import st_pyecharts

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="URL文本词频分析系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- 全局常量 ----------------------
# 中文停用词表（扩充版）
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也",
    "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
    "他", "她", "它", "我们", "你们", "他们", "这里", "那里", "然后", "但是", "因为", "所以",
    "如果", "虽然", "这些", "那些", "什么", "怎么", "为什么", "哪个", "哪", "多少", "几",
    "与", "及", "等", "对", "对于", "关于", "通过", "为了", "来自", "用于", "其中", "包括",
    "可以", "将", "能", "让", "使", "被", "把", "给", "向", "从", "以", "之", "而", "则",
    "此", "该", "其", "或", "即", "因", "由", "及", "并", "个", "位", "件", "条", "本", "项"
])

# 无效字符过滤正则
INVALID_CHAR_REG = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9]")

# ---------------------- 核心函数 ----------------------
def fetch_url_content(url: str) -> str:
    """
    抓取URL页面的文本内容（适配常见新闻网站结构）
    :param url: 文章URL
    :return: 抓取的文本内容（标题+正文）
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误
        response.encoding = response.apparent_encoding  # 自动识别编码
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 抓取标题
        title = soup.find("h1") or soup.find("title")
        title_text = title.get_text(strip=True) if title else ""
        
        # 抓取正文（匹配常见的正文容器类名）
        content_tags = soup.find_all(
            ["div", "p"], 
            attrs={"class": re.compile(r"content|article|main|text|body|content-box", re.I)}
        )
        content_text = ""
        for tag in content_tags:
            # 过滤script/style标签
            for script in tag(["script", "style"]):
                script.extract()
            content_text += tag.get_text(strip=True) + " "
        
        # 合并标题+正文
        full_text = title_text + " " + content_text
        if not full_text.strip():
            st.warning("未抓取到有效文本内容，请检查URL是否为文章详情页")
        return full_text
    except requests.exceptions.RequestException as e:
        st.error(f"URL抓取失败：{str(e)}")
        return ""

def segment_text(text: str) -> list:
    """
    文本分词：过滤无效字符、停用词，返回有效词列表
    :param text: 原始文本
    :return: 有效词列表
    """
    # 过滤无效字符
    clean_text = INVALID_CHAR_REG.sub(" ", text)
    # jieba分词
    words = jieba.lcut(clean_text)
    # 过滤停用词、单字、空白词
    valid_words = [
        word for word in words
        if len(word) > 1 
        and word not in STOP_WORDS 
        and not word.isspace()
    ]
    return valid_words

def get_word_freq(words: list, min_freq: int) -> Counter:
    """
    统计词频，过滤低频词
    :param words: 有效词列表
    :param min_freq: 最小词频阈值
    :return: 过滤后的词频统计结果
    """
    word_counter = Counter(words)
    # 过滤低于最小词频的词
    filtered_counter = Counter({k: v for k, v in word_counter.items() if v >= min_freq})
    return filtered_counter

# ---------------------- 侧边栏：图表筛选 ----------------------
st.sidebar.title("📊 可视化图表筛选")
chart_type = st.sidebar.selectbox(
    "选择图表类型",
    options=[
        "词云图", "词频前20柱状图", "词频前20折线图", "词频前20饼图",
        "词频雷达图", "词频散点图", "词频热力图", "词频树状图", "词频极坐标图"
    ],
    index=0
)

# ---------------------- 主页面：输入与分析 ----------------------
st.title("🔍 URL文本词频分析可视化系统")
st.markdown("### 请输入文章URL，一键分析文本词频并可视化")

# 1. URL输入框
url = st.text_input(
    "文章URL", 
    value="", 
    placeholder="例如：https://www.example.com/news/123.html"
)

# 2. 低频词过滤滑动条
min_freq = st.slider("过滤低频词（最小词频）", min_value=1, max_value=10, value=2, step=1)

# 3. 分析按钮
if st.button("🚀 开始分析", type="primary"):
    if not url.strip():
        st.warning("请输入有效的URL")
    else:
        with st.spinner("正在抓取URL并分析..."):
            # 步骤1：抓取文本
            text = fetch_url_content(url)
            if not text:
                st.stop()
            
            # 步骤2：分词
            words = segment_text(text)
            if not words:
                st.warning("分词后无有效词汇")
                st.stop()
            
            # 步骤3：统计词频（过滤低频词）
            word_freq = get_word_freq(words, min_freq)
            if not word_freq:
                st.warning(f"无满足最小词频{min_freq}的词汇，请降低最小词频阈值")
                st.stop()
            
            # 步骤4：获取词频前20的词汇
            top20_words = word_freq.most_common(20)
            top20_words_list = [word for word, freq in top20_words]
            top20_freq_list = [freq for word, freq in top20_words]

            # ---------------------- 结果展示 ----------------------
            st.success(f"✅ 分析完成！共抓取有效词汇 {len(word_freq)} 个")
            
            # 分两列展示：词频排名 + 图表
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 📈 词频前20排名")
                for idx, (word, freq) in enumerate(top20_words, 1):
                    st.write(f"{idx}. **{word}** - {freq}次")
            
            with col2:
                st.markdown(f"### 📊 {chart_type}")
                # 根据选择的图表类型生成对应图表
                if chart_type == "词云图":
                    # 词云图数据格式：[(词, 频), ...]
                    wordcloud_data = list(word_freq.items())
                    wc = (
                        WordCloud()
                        .add("", wordcloud_data, word_size_range=[20, 100], shape="circle")
                        .set_global_opts(title_opts=opts.TitleOpts(title="文本词云图", pos_left="center"))
                    )
                    st_pyecharts(wc, width="100%", height="500px")
                
                elif chart_type == "词频前20柱状图":
                    bar = (
                        Bar()
                        .add_xaxis(top20_words_list)
                        .add_yaxis("词频", top20_freq_list)
                        .reversal_axis()  # 横向柱状图，更适合展示词汇
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20柱状图", pos_left="center"),
                            xaxis_opts=opts.AxisOpts(name="词频"),
                            yaxis_opts=opts.AxisOpts(name="词汇")
                        )
                    )
                    st_pyecharts(bar, width="100%", height="500px")
                
                elif chart_type == "词频前20折线图":
                    line = (
                        Line()
                        .add_xaxis(top20_words_list)
                        .add_yaxis("词频", top20_freq_list, is_smooth=True)
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20折线图", pos_left="center"),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30))
                        )
                    )
                    st_pyecharts(line, width="100%", height="500px")
                
                elif chart_type == "词频前20饼图":
                    pie = (
                        Pie()
                        .add("", top20_words)
                        .set_global_opts(title_opts=opts.TitleOpts(title="词频前20饼图", pos_left="center"))
                        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                    )
                    st_pyecharts(pie, width="100%", height="500px")
                
                elif chart_type == "词频雷达图":
                    # 雷达图最多展示前10个词汇，避免过于拥挤
                    radar_words = top20_words_list[:10]
                    radar_freq = top20_freq_list[:10]
                    if radar_freq:
                        radar = (
                            Radar()
                            .add_schema(schema=[opts.RadarIndicatorItem(name=word, max_=max(radar_freq)) for word in radar_words])
                            .add("词频", [radar_freq])
                            .set_global_opts(title_opts=opts.TitleOpts(title="词频前10雷达图", pos_left="center"))
                        )
                        st_pyecharts(radar, width="100%", height="500px")
                
                elif chart_type == "词频散点图":
                    scatter = (
                        Scatter()
                        .add_xaxis(top20_words_list)
                        .add_yaxis("词频", top20_freq_list)
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20散点图", pos_left="center"),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30))
                        )
                    )
                    st_pyecharts(scatter, width="100%", height="500px")
                
                elif chart_type == "词频热力图":
                    # 热力图数据格式：[[行, 列, 值], ...]
                    heatmap_data = [[0, idx, freq] for idx, freq in enumerate(top20_freq_list)]
                    heatmap = (
                        HeatMap()
                        .add_xaxis(top20_words_list)
                        .add_yaxis("词频", [" "], heatmap_data)
                        .set_global_opts(
                            title_opts=opts.TitleOpts(title="词频前20热力图", pos_left="center"),
                            visualmap_opts=opts.VisualMapOpts(min_=min(top20_freq_list), max_=max(top20_freq_list))
                        )
                    )
                    st_pyecharts(heatmap, width="100%", height="300px")
                
                elif chart_type == "词频树状图":
                    treemap_data = [{"name": k, "value": v} for k, v in top20_words]
                    treemap = (
                        TreeMap()
                        .add("", treemap_data)
                        .set_global_opts(title_opts=opts.TitleOpts(title="词频前20树状图", pos_left="center"))
                        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                    )
                    st_pyecharts(treemap, width="100%", height="500px")
                
                elif chart_type == "词频极坐标图":
                    # 极坐标图最多展示前10个词汇
                    polar_words = top20_words_list[:10]
                    polar_freq = top20_freq_list[:10]
                    if polar_freq:
                        polar = (
                            Polar()
                            .add_schema(angleaxis_opts=opts.AngleAxisOpts(data=polar_words, type_="category"))
                            .add("词频", polar_freq, type_="bar")
                            .set_global_opts(title_opts=opts.TitleOpts(title="词频前10极坐标图", pos_left="center"))
                        )
                        st_pyecharts(polar, width="100%", height="500px")

# ---------------------- 侧边栏说明 ----------------------
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📝 使用说明")
st.sidebar.markdown("1. 输入**文章详情页URL**（非列表页）")
st.sidebar.markdown("2. 调整滑动条设置最小词频阈值")
st.sidebar.markdown("3. 点击「开始分析」查看结果")
st.sidebar.markdown("4. 侧边栏切换不同图表类型")