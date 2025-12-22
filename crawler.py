import requests
from bs4 import BeautifulSoup
import time

# 步骤1：发送请求，获取网页源代码
def get_web_page(url):
    """
    发送GET请求获取网页源代码
    :param url: 目标网页URL
    :return: 网页源代码（str）/ None（请求失败）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.ConnectTimeout:
        print(f"错误：连接{url}超时！请检查网络")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None
    except Exception as e:
        print(f"未知错误：{e}")
        return None

# 步骤2：解析网页，提取body标签内带换行的纯文本
def parse_page(html):
    """
    解析HTML，提取body标签内的纯文本（保留自然换行，实现竖状排版）
    :param html: 网页源代码
    :return: body纯文本内容（str）/ None（解析失败）
    """
    if not html:
        return None
    try:
        soup = BeautifulSoup(html, 'html.parser')
        body_tag = soup.body
        if not body_tag:
            print("警告：未找到body标签")
            return None
        
        body_text = body_tag.get_text(separator='\n', strip=True)
        
        lines = []
        for line in body_text.split('\n'):
            stripped_line = line.strip()
            if stripped_line: 
                lines.append(stripped_line)
        final_text = '\n'.join(lines)
        
        return final_text
    except Exception as e:
        print(f"解析失败：{e}")
        return None

# 步骤3：保存文本到指定编号的txt文件（UTF-8编码，保留换行）
def save_data(text_content, file_num):
    """
    将带换行的正文文本写入txt文件，实现竖状排版
    :param text_content: 要保存的纯文本内容（带换行）
    :param file_num: 文件编号（1/2/3）
    """
    if not text_content:
        print(f"警告：第{file_num}个文件无内容，跳过保存")
        return
    filename = f"new{file_num}.txt"
    try:
        # 直接写入带换行的文本，无需额外处理
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"成功保存：{filename}")
    except IOError as e:
        print(f"写入{filename}失败：{e}")

# 主程序
if __name__ == '__main__':
    # 目标网站（3个不同页面，可替换为真实子页面）
    target_urls = [
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/',          # 第1篇：主站
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/#about',    # 第2篇：关于板块
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/#contact'   # 第3篇：联系板块
    ]
    
    # 遍历处理3个页面
    for idx, url in enumerate(target_urls, start=1):
        print(f"\n========== 处理第{idx}个页面 ==========")
        print(f"目标URL：{url}")
        
        html_content = get_web_page(url)
        if not html_content:
            print(f"第{idx}个页面请求失败，跳过")
            continue
        
        body_text = parse_page(html_content)
        if not body_text:
            print(f"第{idx}个页面解析失败，跳过")
            continue
        
        save_data(body_text, idx)
        time.sleep(1)
    
    print("\n所有页面处理完成！")