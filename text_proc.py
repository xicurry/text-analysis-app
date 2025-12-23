import re
import jieba
from collections import Counter

# 新增：停用词表（与app.py保持一致，增强过滤效果）
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也",
    "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那"
])

# 1. 读取文本文件（支持读取单个或多个new系列文本文件）
def read_text_files(file_nums=[1, 2, 3]):
    """
    读取new1.txt、new2.txt、new3.txt文件（整站爬取的结果）
    :param file_nums: 文件编号列表，默认[1,2,3]
    :return: 合并后的所有文本内容（str）
    """
    total_text = ""
    for num in file_nums:
        file_path = f"new{num}.txt"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            total_text += text + "\n"
            print(f"成功读取：{file_path}")
        except FileNotFoundError:
            print(f"警告：未找到文件 {file_path}，跳过该文件")
        except Exception as e:
            print(f"读取{file_path}失败：{e}，跳过该文件")
    return total_text

# 2. 使用正则表达式去除HTML标签（兼容残留标签）
def remove_html_tags(text):
    """去除文本中所有HTML标签（包括跨行标签）"""
    html_pattern = re.compile(r'<.*?>', re.S)
    clean_text = html_pattern.sub('', text)
    return clean_text

# 3. 去除文本中的标点符号（中英文标点全覆盖）
def remove_punctuation(text):
    """去除中英文标点符号、多余空格和换行符"""
    punctuation_pattern = re.compile(
        r'[\u3000-\u303f\u2000-\u206f\u0021-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007e\uff01-\uff1f\uff0c-\uff1a\uff1b\uff0e\uff1f\uff01]'
    )
    text_without_punc = punctuation_pattern.sub('', text)
    text_without_punc = re.sub(r'\s+', ' ', text_without_punc).strip()
    return text_without_punc

# 4. 分词并统计词频，返回TOP N高频词和完整词频字典
def analyze_word_frequency(text, top_n=20):
    """
    对清洗后的整站文本分词、过滤无意义词汇、统计词频
    """
    if not text:
        print("警告：无有效文本可供分词统计")
        return [], {}
    
    # 使用jieba精确模式分词
    word_list = jieba.lcut(text)
    
    # 增强过滤：加入停用词过滤（适配整站文本的噪音）
    filtered_words = []
    for word in word_list:
        if len(word) > 1 and not word.isdigit() and word not in STOP_WORDS:
            filtered_words.append(word)
    
    # 统计词频
    word_counter = Counter(filtered_words)
    top_words = word_counter.most_common(top_n)
    full_word_freq = dict(word_counter)
    return top_words, full_word_freq

# 5. 格式化输出TOP N高频词
def print_top_words(top_words):
    """格式化输出高频词结果"""
    if not top_words:
        print("无高频词可输出")
        return
    
    print("\n" + "="*60)
    print(f"词频最高的20个词如下（按频次降序排列）")
    print("="*60)
    print(f"{'排名':<6}{'词汇':<12}{'出现频次':<8}")
    print("-"*60)
    for idx, (word, freq) in enumerate(top_words, 1):
        print(f"{idx:<6}{word:<12}{freq:<8}")
    print("="*60)

# 6. 保存分词结果及词频到words.txt文件
def save_word_freq_to_file(full_word_freq, top_words, file_name="words.txt"):
    """
    将完整词频和TOP20高频词保存到words.txt
    """
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("=== 整站文本分词词频统计结果 ===\n")
            f.write(f"有效词汇总数：{len(full_word_freq)}\n\n")
            
            f.write("=== 词频TOP20 ===\n")
            f.write(f"{'排名':<6}{'词汇':<12}{'出现频次':<8}\n")
            f.write("-"*30 + "\n")
            for idx, (word, freq) in enumerate(top_words, 1):
                f.write(f"{idx:<6}{word:<12}{freq:<8}\n")
            f.write("\n")
            
            f.write("=== 所有词汇词频（按频次降序） ===\n")
            sorted_full_freq = sorted(full_word_freq.items(), key=lambda x: x[1], reverse=True)
            for word, freq in sorted_full_freq:
                f.write(f"{word:<12}{freq:<8}\n")
        
        print(f"\n成功将分词结果及词频保存到：{file_name}")
    except IOError as e:
        print(f"保存{file_name}失败：{e}")

# 7. 统一处理函数（供app.py调用）
def process_text(file_nums=[1,2,3], top_n=20):
    """
    统一的文本处理入口：读取→清洗→分词→统计→保存
    """
    raw_text = read_text_files(file_nums)
    if not raw_text:
        return [], {}
    text_without_html = remove_html_tags(raw_text)
    clean_text = remove_punctuation(text_without_html)
    top_words, full_word_freq = analyze_word_frequency(clean_text, top_n)
    save_word_freq_to_file(full_word_freq, top_words)
    print_top_words(top_words)
    return top_words, full_word_freq

# 主程序执行
if __name__ == "__main__":
    top_20_words, full_word_freq = process_text(file_nums=[1, 2, 3], top_n=20)
    
    if not top_20_words:
        print("未统计到有效词频，程序结束")
    else:
        print("\n所有任务执行完成！")