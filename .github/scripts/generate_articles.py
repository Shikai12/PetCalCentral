import os
import re
import glob
import json
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

BASE_URL = "https://petcalcentral.com"
BLOG_DIR = "blog"
SITEMAP_FILE = "sitemap.xml"
ARTICLES_JSON = os.path.join(BLOG_DIR, "articles.json")
LLMS_FILE = "llms.txt"

def extract_metadata(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # 提取描述
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else ""

    # 提取日期（格式：May 14, 2026 或 2026-05-14）
    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', content)
    if not date_match:
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', content)
    if date_match:
        date_str = date_match.group(0)
        try:
            if '-' in date_str:
                pub_date = date_str
            else:
                pub_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        except:
            pub_date = datetime.now().strftime("%Y-%m-%d")
    else:
        pub_date = datetime.now().strftime("%Y-%m-%d")

    # 提取作者（从类似 "— Alex" 或 "– Alex" 的行）
    author_match = re.search(r'[—–]\s*([A-Za-z\s]+)(?:<|$)', content)
    author = author_match.group(1).strip() if author_match else "Alex"

    # 提取标签（从文章中手动添加，如果没有则根据标题生成简单标签，但你可以后续手动编辑 JSON）
    tags = []
    # 可选：从内容中提取常见关键词，这里留空，或者你可以让文章中有 <meta name="keywords"> 再提取
    # 为了简单，先留空，你可以在 JSON 生成后手动添加，或者修改文章 HTML 添加 meta keywords
    # 我们暂时使用默认标签：根据标题判断
    if "cat" in title.lower():
        tags.append("Cat Health")
    if "dog" in title.lower() or "puppy" in title.lower() or "gus" in title.lower():
        tags.append("Dog Health")
    if "weight" in title.lower() or "fat" in title.lower():
        tags.append("Weight Management")
    if "ear" in title.lower():
        tags.append("Ear Care")
    if "feeding" in title.lower() or "food" in title.lower():
        tags.append("Feeding")
    if "camera" in title.lower() or "furbo" in title.lower():
        tags.append("Gadget")
    # 去重
    tags = list(set(tags))
    if not tags:
        tags = ["Pet Care"]

    return {
        "title": title,
        "file": os.path.basename(html_path),
        "date": pub_date,
        "excerpt": description[:150] if description else "",
        "tags": tags,
        "author": author
    }

def generate_articles_json(posts):
    # 按日期倒序
    posts_sorted = sorted(posts, key=lambda x: x["date"], reverse=True)
    with open(ARTICLES_JSON, 'w', encoding='utf-8') as f:
        json.dump(posts_sorted, f, indent=2, ensure_ascii=False)

def generate_sitemap(posts):
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    # 首页
    url = SubElement(urlset, 'url')
    loc = SubElement(url, 'loc')
    loc.text = BASE_URL + '/'
    lastmod = SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime("%Y-%m-%d")
    # 博客文章
    for post in posts:
        url = SubElement(urlset, 'url')
        loc = SubElement(url, 'loc')
        loc.text = f"{BASE_URL}/{BLOG_DIR}/{post['file']}"
        lastmod = SubElement(url, 'lastmod')
        lastmod.text = post['date']
        priority = SubElement(url, 'priority')
        priority.text = '0.8'
    # 工具页
    tools = glob.glob("tools/*.html")
    for tool in tools:
        url = SubElement(urlset, 'url')
        loc = SubElement(url, 'loc')
        loc.text = f"{BASE_URL}/{tool.replace('\\', '/')}"
        lastmod = SubElement(url, 'lastmod')
        lastmod.text = datetime.now().strftime("%Y-%m-%d")
        priority = SubElement(url, 'priority')
        priority.text = '0.6'
    xml_str = minidom.parseString(tostring(urlset)).toprettyxml(indent="  ")
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_str)

def generate_llms(posts):
    content = "# PetCalCentral - Blog Posts\n\n"
    for post in posts:
        url = f"{BASE_URL}/{BLOG_DIR}/{post['file']}"
        content += f"- {post['date']}: {post['title']} ({url})\n"
    with open(LLMS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    html_files = glob.glob(f"{BLOG_DIR}/*.html")
    # 排除 index.html 自身
    html_files = [f for f in html_files if not f.endswith("index.html")]
    posts = []
    for file in html_files:
        meta = extract_metadata(file)
        posts.append(meta)
    generate_articles_json(posts)
    generate_sitemap(posts)
    generate_llms(posts)
    print(f"✅ Updated {len(posts)} posts. regenerated articles.json, sitemap.xml, llms.txt")

if __name__ == "__main__":
    main()