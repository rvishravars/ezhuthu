import os
import json
import re
import urllib.parse
import datetime

# Paths
BASE_DIR = '/Users/vishravars/code/ezhuthu'
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
POSTS_DIR = os.path.join(BASE_DIR, 'posts')

def format_rfc822_date(date_str):
    try:
        # e.g., "July 6, 2026"
        dt = datetime.datetime.strptime(date_str, "%B %d, %Y")
        return dt.strftime("%a, %d %b %Y 00:00:00 +0000")
    except Exception as e:
        print(f"Warning: Could not parse date format '{date_str}': {e}")
        # Fallback to current time RFC822 if parse fails
        return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

def linkify(text):
    # Regex to find http/https URLs, ignoring trailing punctuation like periods or commas
    pattern = r'(https?://[^\s<>"]+?)(?=[.,;:!?]?(?:\s|$))'
    return re.sub(pattern, r'<a href="\1" target="_blank">\1</a>', text)

def main():
    # Load posts metadata
    posts_json_path = os.path.join(BASE_DIR, 'posts.json')
    with open(posts_json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    # Read templates
    with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        index_template = f.read()
    with open(os.path.join(TEMPLATES_DIR, 'post.html'), 'r', encoding='utf-8') as f:
        post_template = f.read()

    articles_html = []
    rss_items = []

    # Ensure posts folder exists
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    for post in posts:
        post_id = post['id']
        title = post['title']
        date_str = post['date']
        lang = post['lang']
        src_file = post['src']
        
        # Read post text content
        src_path = os.path.join(BASE_DIR, 'raw_posts', src_file)
        if not os.path.exists(src_path):
            print(f"Error: Source file {src_path} not found for post {post_id}")
            continue
            
        with open(src_path, 'r', encoding='utf-8') as f:
            text_content = f.read()

        # Render paragraphs
        paragraphs_raw = re.split(r'\n\s*\n', text_content.strip())
        paragraphs = []
        for p in paragraphs_raw:
            if p.strip():
                p_formatted = p.replace('\n', '<br>')
                p_formatted = linkify(p_formatted)
                paragraphs.append(f"<p>{p_formatted}</p>")
        content_html = "".join(paragraphs)

        # Word count & reading time
        word_count = len(text_content.strip().split())
        reading_time = max(1, (word_count + 199) // 200)
        read_time_str = f"{reading_time} min read"

        # Canonical post URLs
        canonical_post_url = f"https://www.vishravars.me/posts/{post_id}/"
        encoded_live_url = urllib.parse.quote_plus(canonical_post_url)
        encoded_title = urllib.parse.quote_plus(title)

        # Pre-rendered translate link
        translate_link_html = ""
        index_translate_link_html = ""
        if lang != 'en':
            translate_url = f"https://translate.google.com/translate?sl={lang}&tl=en&u={encoded_live_url}"
            # post.html translate link (centered with post-meta-separator)
            translate_link_html = f"""<a id="translate-link" href="{translate_url}" target="_blank" class="translate-link post-meta-separator">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                    Translate to English
                </a>"""
            # index.html translate link (bottom row next to read article)
            index_translate_link_html = f"""<a href="{translate_url}" target="_blank" class="translate-link">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                                    Translate to English
                                </a>"""

        # Populate post page template
        post_html = post_template
        
        # Render featured image if present
        featured_image_html = ""
        if post.get('image'):
            img_name = post['image']
            featured_image_html = f'<div class="featured-image-container" style="text-align: center; margin-bottom: 2.5rem;"><img src="/images/{img_name}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"></div>'

        post_html = post_html.replace('{{TITLE}}', title)
        post_html = post_html.replace('{{DATE}}', date_str)
        post_html = post_html.replace('{{LANG}}', lang)
        post_html = post_html.replace('{{READ_TIME}}', read_time_str)
        post_html = post_html.replace('{{TRANSLATE_LINK_HTML}}', translate_link_html)
        post_html = post_html.replace('{{FEATURED_IMAGE}}', featured_image_html)
        post_html = post_html.replace('{{CONTENT}}', content_html)
        post_html = post_html.replace('{{SHARE_URL}}', encoded_live_url)
        post_html = post_html.replace('{{SHARE_TEXT}}', encoded_title)

        # Create output directory for post
        post_output_dir = os.path.join(POSTS_DIR, post_id)
        if not os.path.exists(post_output_dir):
            os.makedirs(post_output_dir)
            
        with open(os.path.join(post_output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(post_html)
        print(f"Generated post page: /posts/{post_id}/index.html")

        # Create index.html preview
        plain_text = re.sub(r'\s+', ' ', text_content).strip()
        preview_text = plain_text[:250].strip() + '...' if len(plain_text) > 250 else plain_text
        
        article_item_html = f"""        <article>
            <time class="article-meta">{date_str}</time>
            <h2 class="article-title" lang="{lang}"><a href="/posts/{post_id}/">{title}</a></h2>
            <div class="article-content" lang="{lang}">
                <p>{preview_text}</p>
            </div>
            <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
                <a href="/posts/{post_id}/" class="read-more">Read article <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg></a>
                {index_translate_link_html}
            </div>
        </article>"""
        articles_html.append(article_item_html)

        # Build RSS item
        description = post.get('description', f"{title} குறித்த ஒரு கட்டுரை.")
        pub_date_rfc = format_rfc822_date(date_str)
        rss_item = f"""    <item>
        <title>{title}</title>
        <link>{canonical_post_url}</link>
        <description>{description}</description>
        <pubDate>{pub_date_rfc}</pubDate>
    </item>"""
        rss_items.append(rss_item)

    # Generate index.html
    combined_articles = "\n".join(articles_html)
    final_index_html = index_template.replace('{{POSTS_LIST}}', combined_articles)
    with open(os.path.join(BASE_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(final_index_html)
    print("Generated homepage: /index.html")

    # Generate rss.xml
    combined_rss_items = "\n".join(rss_items)
    rss_xml_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>The Writings of Vishravars</title>
    <link>https://www.vishravars.me</link>
    <description>Personal blog of Vishravars.</description>
{combined_rss_items}
</channel>
</rss>
"""
    with open(os.path.join(BASE_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss_xml_content)
    print("Generated RSS feed: /rss.xml")

if __name__ == '__main__':
    main()
