import re
import jieba
from collections import Counter

# 1. 读取文本文件（支持读取单个或多个new系列文本文件）
def read_text_files(file_nums=[1, 2, 3]):
    """
    读取上次作业生成的new1.txt、new2.txt、new3.txt文件
    :param file_nums: 文件编号列表，默认[1,2,3]
    :return: 合并后的所有文本内容（str）
    """
    total_text = ""
    for num in file_nums:
        file_path = f"new{num}.txt"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            total_text += text + "\n"  # 合并文本，添加换行分隔
            print(f"成功读取：{file_path}")
        except FileNotFoundError:
            print(f"警告：未找到文件 {file_path}，跳过该文件")
        except Exception as e:
            print(f"读取{file_path}失败：{e}，跳过该文件")
    return total_text

# 2. 使用正则表达式去除HTML标签（兼容残留标签）
def remove_html_tags(text):
    """去除文本中所有HTML标签（包括跨行标签）"""
    # 正则匹配规则：匹配<开头、>结尾的所有内容（非贪婪匹配，支持跨行）
    html_pattern = re.compile(r'<.*?>', re.S)
    clean_text = html_pattern.sub('', text)
    return clean_text

# 3. 去除文本中的标点符号（中英文标点全覆盖）
def remove_punctuation(text):
    """去除中英文标点符号、多余空格和换行符"""
    # 匹配中英文标点符号的Unicode范围
    punctuation_pattern = re.compile(
        r'[\u3000-\u303f\u2000-\u206f\u0021-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007e\uff01-\uff1f\uff0c-\uff1a\uff1b\uff0e\uff1f\uff01]'
    )
    # 去除标点
    text_without_punc = punctuation_pattern.sub('', text)
    # 去除多余的空格、换行符，只保留单个空格
    text_without_punc = re.sub(r'\s+', ' ', text_without_punc).strip()
    return text_without_punc

# 4. 分词并统计词频，返回TOP N高频词和完整词频字典
def analyze_word_frequency(text, top_n=20):
    """
    对清洗后的文本分词、过滤无意义词汇、统计词频
    :param text: 清洗后的纯文本
    :param top_n: 要返回的高频词数量
    :return: (TOP N高频词列表, 完整词频字典)
    """
    if not text:
        print("警告：无有效文本可供分词统计")
        return [], {}
    
    # 使用jieba精确模式分词
    word_list = jieba.lcut(text)
    
    # 过滤无意义词汇：排除单字、纯数字
    filtered_words = []
    for word in word_list:
        # 长度大于1 且 不是纯数字
        if len(word) > 1 and not word.isdigit():
            filtered_words.append(word)
    
    # 统计词频
    word_counter = Counter(filtered_words)
    # 获取TOP N高频词
    top_words = word_counter.most_common(top_n)
    # 转换为完整字典（便于保存所有词频）
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
    # 格式化表头
    print(f"{'排名':<6}{'词汇':<12}{'出现频次':<8}")
    print("-"*60)
    # 输出每个高频词
    for idx, (word, freq) in enumerate(top_words, 1):
        print(f"{idx:<6}{word:<12}{freq:<8}")
    print("="*60)

# 6. 保存分词结果及词频到words.txt文件
def save_word_freq_to_file(full_word_freq, top_words, file_name="words.txt"):
    """
    将完整词频和TOP20高频词保存到words.txt
    :param full_word_freq: 完整词频字典
    :param top_words: TOP20高频词列表
    :param file_name: 保存的文件名
    """
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            # 写入文件说明
            f.write("=== 文本分词词频统计结果 ===\n")
            f.write(f"统计时间：自动生成\n")
            f.write(f"有效词汇总数：{len(full_word_freq)}\n\n")
            
            # 先写入TOP20高频词（醒目展示）
            f.write("=== 词频TOP20 ===\n")
            f.write(f"{'排名':<6}{'词汇':<12}{'出现频次':<8}\n")
            f.write("-"*30 + "\n")
            for idx, (word, freq) in enumerate(top_words, 1):
                f.write(f"{idx:<6}{word:<12}{freq:<8}\n")
            f.write("\n")
            
            # 再写入所有词汇的词频（按频次降序排列）
            f.write("=== 所有词汇词频（按频次降序） ===\n")
            # 对完整词频按频次降序排序
            sorted_full_freq = sorted(full_word_freq.items(), key=lambda x: x[1], reverse=True)
            for word, freq in sorted_full_freq:
                f.write(f"{word:<12}{freq:<8}\n")
        
        print(f"\n成功将分词结果及词频保存到：{file_name}")
    except IOError as e:
        print(f"保存{file_name}失败：{e}")

# 主程序执行
if __name__ == "__main__":
    # 步骤1：读取new1.txt、new2.txt、new3.txt
    raw_text = read_text_files(file_nums=[1, 2, 3])
    if not raw_text:
        print("未读取到任何文本内容，程序结束")
        exit()
    
    # 步骤2：去除HTML标签（兼容爬取残留的标签）
    text_without_html = remove_html_tags(raw_text)
    
    # 步骤3：去除标点符号和多余空白
    clean_text = remove_punctuation(text_without_html)
    
    # 步骤4：分词并统计TOP20词频+完整词频
    top_20_words, full_word_freq = analyze_word_frequency(clean_text, top_n=20)
    
    # 步骤5：格式化输出结果
    print_top_words(top_20_words)
    
    # 步骤6：保存到words.txt
    save_word_freq_to_file(full_word_freq, top_20_words)
    
    print("\n所有任务执行完成！")