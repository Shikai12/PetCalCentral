import os
import re
from datetime import datetime

BLOG_DIR = 'blog'
BASE_URL = 'https://petcalcentral.com'

def extract_meta(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'<title>(.*?)\s*\|\s*PetCalCentral</title>', content)
    title = title_match.group(1).strip() if title_match else os.path.basename(html_path)
    
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    excerpt = desc_match.group(1).strip() if desc_match else ''
    if len(excerpt) > 160:
        excerpt = excerpt[:157] + '...'
    
    tags_match = re.search(r'<!--\s*tags:\s*(.*?)\s*-->', content)
    tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []
    
    date_match = re.search(r'datePublished["\']\s*:\s*["\'](.*?)["\']', content)
    date = date_match.group(1) if date_match else datetime.today().strftime('%Y-%m-%d')
    
    return {
        'title': title,
        'file': os.path.basename(html_path),
        'date': date,
        'excerpt': excerpt,
        'tags': tags
    }

def update_blog_index(articles):
    sorted_articles = sorted(articles, key=lambda x: x['date'], reverse=True)
    
    articles_js = 'const articles = [\n'
    for a in sorted_articles:
        articles_js += '    {\n'
        articles_js += f'        title: "{a["title"]}",\n'
        articles_js += f'        file: "{a["file"]}",\n'
        articles_js += f'        date: "{a["date"]}",\n'
        articles_js += f'        excerpt: "{a["excerpt"]}",\n'
        tags_str = '", "'.join(a['tags'])
        articles_js += f'        tags: ["{tags_str}"]\n'
        articles_js += '    },\n'
    articles_js += '];'
    
    with open(os.path.join(BLOG_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()
    
    pattern = r'const articles = \[[\s\S]*?\];'
    html = re.sub(pattern, articles_js, html)
    
    with open(os.path.join(BLOG_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

def update_sitemap(articles):
    urls = [
        f'<url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>',
        f'<url><loc>{BASE_URL}/about.html</loc><priority>0.6</priority></url>',
        f'<url><loc>{BASE_URL}/contact.html</loc><priority>0.4</priority></url>',
        f'<url><loc>{BASE_URL}/faq.html</loc><priority>0.7</priority></url>',
        f'<url><loc>{BASE_URL}/tools/dog-calorie-calculator.html</loc><priority>0.9</priority></url>',
        f'<url><loc>{BASE_URL}/tools/cat-calorie-calculator.html</loc><priority>0.9</priority></url>',
        f'<url><loc>{BASE_URL}/tools/dog-age-calculator.html</loc><priority>0.8</priority></url>',
        f'<url><loc>{BASE_URL}/tools/pet-bmi-calculator.html</loc><priority>0.8</priority></url>',
        f'<url><loc>{BASE_URL}/tools/pet-water-intake-calculator.html</loc><priority>0.7</priority></url>',
        f'<url><loc>{BASE_URL}/blog/</loc><priority>0.8</priority></url>'
    ]
    
    for a in articles:
        urls.append(f'<url><loc>{BASE_URL}/blog/{a["file"]}</loc><priority>0.7</priority></url>')
    
    urls += [
        f'<url><loc>{BASE_URL}/privacy.html</loc><priority>0.3</priority></url>',
        f'<url><loc>{BASE_URL}/terms.html</loc><priority>0.3</priority></url>',
        f'<url><loc>{BASE_URL}/disclaimer.html</loc><priority>0.3</priority></url>',
        f'<url><loc>{BASE_URL}/disclosure.html</loc><priority>0.3</priority></url>',
        f'<url><loc>{BASE_URL}/sitemap.html</loc><priority>0.3</priority></url>'
    ]
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)

def update_llms(articles):
    llms = f'# PetCalCentral\n> Free, science-based pet health calculators and feeding guides for dogs and cats.\n\n'
    llms += '## Core Tools\n' + '\n'.join([
        f'- [Dog Calorie Calculator]({BASE_URL}/tools/dog-calorie-calculator.html)',
        f'- [Cat Calorie Calculator]({BASE_URL}/tools/cat-calorie-calculator.html)',
        f'- [Dog Age Calculator]({BASE_URL}/tools/dog-age-calculator.html)',
        f'- [Pet BMI Calculator]({BASE_URL}/tools/pet-bmi-calculator.html)',
        f'- [Pet Water Intake Calculator]({BASE_URL}/tools/pet-water-intake-calculator.html)'
    ]) + '\n\n## Guides\n'
    llms += '\n'.join([f'- [{a["title"]}]({BASE_URL}/blog/{a["file"]})' for a in articles])
    llms += f'\n\n## Documentation\n- [About]({BASE_URL}/about.html) | [FAQ]({BASE_URL}/faq.html) | [Privacy]({BASE_URL}/privacy.html) | [Terms]({BASE_URL}/terms.html) | [Disclaimer]({BASE_URL}/disclaimer.html) | [Disclosure]({BASE_URL}/disclosure.html)'
    
    with open('llms.txt', 'w', encoding='utf-8') as f:
        f.write(llms)

def main():
    articles = []
    for f in os.listdir(BLOG_DIR):
        if f.endswith('.html') and f != 'index.html':
            articles.append(extract_meta(os.path.join(BLOG_DIR, f)))
    
    update_blog_index(articles)
    update_sitemap(articles)
    update_llms(articles)
    print(f'Updated {len(articles)} articles.')

if __name__ == '__main__':
    main()
