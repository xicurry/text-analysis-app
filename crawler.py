import requests
from bs4 import BeautifulSoup
import time

# 步骤1：发送请求，获取网页源代码
def get_web_page(url):
    """
    发送GET请求获取网页源代码（适配任意网页，增强容错）
    :param url: 目标网页URL
    :return: 网页源代码（str）/ None（请求失败）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        # 强制使用UTF-8编码（避免乱码）
        response.encoding = response.apparent_encoding or 'utf-8'
        return response.text
    except requests.exceptions.ConnectTimeout:
        print(f"错误：连接{url}超时！请检查网络或URL有效性")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"错误：{url}返回HTTP错误 {e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None
    except Exception as e:
        print(f"未知错误：{e}")
        return None

# 步骤2：解析网页，提取**整个网页**的所有纯文本（关键修改）
def parse_page(html):
    """
    解析HTML，提取**整个网页**的所有可见文本（非仅文章内容）
    :param html: 网页源代码
    :return: 完整的纯文本内容（带自然换行）
    """
    if not html:
        return None
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除无关标签（避免抓取无效文本）
        for tag in soup(["script", "style", "noscript", "iframe", "header", "footer"]):
            tag.extract()
        
        # 提取**所有标签**的文本（覆盖整站内容：导航、正文、侧边栏等）
        all_text = soup.get_text(separator='\n', strip=True)
        
        # 过滤空行和重复行，精简文本
        lines = []
        for line in all_text.split('\n'):
            stripped_line = line.strip()
            if stripped_line and stripped_line not in lines:
                lines.append(stripped_line)
        
        final_text = '\n'.join(lines)
        
        # 确保文本有足够长度
        if len(final_text) < 50:
            print("警告：提取的文本过短，可能是无效页面")
            return None
        
        return final_text
    except Exception as e:
        print(f"解析失败：{e}")
        return None

# 步骤3：保存文本到指定编号的txt文件（UTF-8编码，保留换行）
def save_data(text_content, file_num):
    """
    将整站文本写入txt文件
    :param text_content: 要保存的纯文本内容（带换行）
    :param file_num: 文件编号（1/2/3）
    """
    if not text_content:
        print(f"警告：第{file_num}个文件无内容，跳过保存")
        return
    filename = f"new{file_num}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"成功保存：{filename}")
    except IOError as e:
        print(f"写入{filename}失败：{e}")

# 新增：批量爬取并保存的公开函数（供app.py调用）
def crawl_and_save(target_urls):
    """
    批量爬取URL并保存为newX.txt
    :param target_urls: URL列表
    """
    for idx, url in enumerate(target_urls, start=1):
        print(f"\n========== 处理第{idx}个页面 ==========")
        print(f"目标URL：{url}")
        
        html_content = get_web_page(url)
        if not html_content:
            print(f"第{idx}个页面请求失败，跳过")
            continue
        
        page_text = parse_page(html_content)
        if not page_text:
            print(f"第{idx}个页面解析失败，跳过")
            continue
        
        save_data(page_text, idx)
        time.sleep(1)
    
    print("\n所有页面处理完成！")

# 主程序（独立运行时测试整站爬取）
if __name__ == '__main__':
    # 测试用整站URL
    target_urls = [
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/',
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/#about',
        'https://uiaec.ujs.edu.cn/news_list.php?parentid=4/#contact'
    ]
    
    crawl_and_save(target_urls)