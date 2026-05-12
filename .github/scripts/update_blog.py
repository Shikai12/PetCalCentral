import os
import glob
import re
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

BASE_URL = "https://petcalcentral.com"
BLOG_DIR = "blog"
SITEMAP_FILE = "sitemap.xml"
INDEX_FILE = os.path.join(BLOG_DIR, "index.html")
LLMS_FILE = "llms.txt"

def extract_metadata(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Untitled"
    
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else ""
    
    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', content)
    if date_match:
        date_str = date_match.group(0)
        try:
            pub_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        except:
            pub_date = datetime.now().strftime("%Y-%m-%d")
    else:
        pub_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "title": title,
        "description": description,
        "date": pub_date,
        "url": f"{BASE_URL}/{html_path.replace('\\', '/')}"
    }

def generate_index(posts):
    posts.sort(key=lambda x: x["date"], reverse=True)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog | PetCalCentral</title>
    <meta name="description" content="Real-life stories about my golden retriever Gus and cat Mochi. Dog weight, slow feeders, pet cameras, and more.">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f9fafb; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .post-card {{ background: white; border-radius: 1rem; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .post-title {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .post-meta {{ color: #6b7280; font-size: 0.875rem; margin-bottom: 0.75rem; }}
        .post-description {{ color: #374151; line-height: 1.5; }}
        a {{ text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
<div class="container">
    <h1 class="text-3xl font-bold mb-6">Blog</h1>
'''
    for post in posts:
        html += f'''
    <div class="post-card">
        <div class="post-title"><a href="{post['url']}">{post['title']}</a></div>
        <div class="post-meta">{post['date']}</div>
        <div class="post-description">{post['description'][:150]}...</div>
    </div>
'''
    html += '''
</div>
</body>
</html>'''
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_sitemap(posts):
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    url = SubElement(urlset, 'url')
    loc = SubElement(url, 'loc')
    loc.text = BASE_URL + '/'
    lastmod = SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime("%Y-%m-%d")
    
    for post in posts:
        url = SubElement(urlset, 'url')
        loc = SubElement(url, 'loc')
        loc.text = post['url']
        lastmod = SubElement(url, 'lastmod')
        lastmod.text = post['date']
        priority = SubElement(url, 'priority')
        priority.text = '0.8'
    
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
        content += f"- {post['date']}: {post['title']} ({post['url']})\n"
    with open(LLMS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    blog_files = glob.glob(f"{BLOG_DIR}/*.html")
    blog_files = [f for f in blog_files if not f.endswith("index.html")]
    posts = []
    for file in blog_files:
        meta = extract_metadata(file)
        posts.append(meta)
    
    generate_index(posts)
    generate_sitemap(posts)
    generate_llms(posts)
    print(f"Updated {len(posts)} posts, regenerated index, sitemap, llms.txt")

if __name__ == "__main__":
    main()