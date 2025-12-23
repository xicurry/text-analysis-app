"""
URL文本词频分析可视化系统
功能：
1. 抓取指定URL的**整个网页**文本内容（支持多URL批量爬取）
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
# 引入自定义模块
import crawler
import text_proc

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

# ---------------------- 核心函数 ----------------------
def fetch_url_all_text(url: str) -> str:
    """
    抓取**整个网页**的所有文本内容（替代原文章详情页抓取逻辑）
    :param url: 目标网页URL
    :return: 网页所有可见文本内容
    """
    try:
        # 调用crawler.py的函数获取网页文本（统一爬取逻辑）
        html_content = crawler.get_web_page(url)
        if not html_content:
            st.error(f"无法获取{url}的网页内容")
            return ""
        # 调用crawler.py的解析函数提取完整文本
        full_text = crawler.parse_page(html_content)
        if not full_text:
            st.warning(f"未从{url}中提取到有效文本")
            return ""
        return full_text
    except Exception as e:
        st.error(f"抓取{url}失败：{str(e)}")
        return ""

def process_text_for_freq(text: str, min_freq: int) -> tuple:
    """
    文本处理与词频统计（整合text_proc.py的逻辑）
    :param text: 原始文本
    :param min_freq: 最小词频阈值
    :return: (top20_words, word_freq)
    """
    # 调用text_proc.py的清洗函数
    text_without_html = text_proc.remove_html_tags(text)
    clean_text = text_proc.remove_punctuation(text_without_html)
    # 分词（加入停用词过滤）
    words = jieba.lcut(clean_text)
    valid_words = [
        word for word in words
        if len(word) > 1 
        and word not in STOP_WORDS 
        and not word.isdigit()
    ]
    # 统计词频
    word_counter = Counter(valid_words)
    filtered_counter = Counter({k: v for k, v in word_counter.items() if v >= min_freq})
    top20_words = filtered_counter.most_common(20)
    return top20_words, filtered_counter

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
st.markdown("### 请输入网页URL，一键分析**整站文本**词频并可视化")

# 1. 多URL输入支持（适配整站多页面爬取）
url_count = st.number_input("要分析的URL数量", min_value=1, max_value=5, value=1, step=1)
urls = []
for i in range(url_count):
    url = st.text_input(
        f"网页URL {i+1}", 
        value="", 
        placeholder="例如：https://uiaec.ujs.edu.cn/news_list.php?parentid=4/"
    )
    urls.append(url)

# 2. 低频词过滤滑动条
min_freq = st.slider("过滤低频词（最小词频）", min_value=1, max_value=10, value=2, step=1)

# 3. 分析按钮
if st.button("🚀 开始分析", type="primary"):
    # 过滤空URL
    valid_urls = [url.strip() for url in urls if url.strip()]
    if not valid_urls:
        st.warning("请输入至少一个有效的URL")
    else:
        with st.spinner("正在抓取网页并分析..."):
            # 批量抓取所有URL的文本
            all_text = ""
            for url in valid_urls:
                text = fetch_url_all_text(url)
                all_text += text + "\n"
            
            if not all_text.strip():
                st.warning("未抓取到任何有效文本")
                st.stop()
            
            # 处理文本并统计词频
            top20_words, word_freq = process_text_for_freq(all_text, min_freq)
            
            if not word_freq:
                st.warning(f"无满足最小词频{min_freq}的词汇，请降低阈值")
                st.stop()
            
            # 调用text_proc.py保存词频结果
            text_proc.save_word_freq_to_file(dict(word_freq), top20_words)
            
            # 提取数据用于可视化
            top20_words_list = [word for word, freq in top20_words]
            top20_freq_list = [freq for word, freq in top20_words]

            # ---------------------- 结果展示 ----------------------
            st.success(f"✅ 分析完成！共抓取{len(valid_urls)}个网页，统计到{len(word_freq)}个有效词汇")
            
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
                        .reversal_axis()
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
st.sidebar.markdown("1. 输入**任意网页URL**（支持多个URL批量分析）")
st.sidebar.markdown("2. 调整滑动条设置最小词频阈值")
st.sidebar.markdown("3. 点击「开始分析」查看整站文本的词频结果")
st.sidebar.markdown("4. 侧边栏切换不同图表类型")