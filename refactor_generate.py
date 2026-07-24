import os
import json
import re

BASE_DIR = '/Users/vishravars/code/ezhuthu'
gen_path = os.path.join(BASE_DIR, 'generate.py')

with open(gen_path, 'r', encoding='utf-8') as f:
    content = f.read()

# REWRITE the post loop
post_loop_start = """    for post in posts:
        post_id = post['id']"""

new_post_loop = """    for post in posts:
        post_id = post['id']
        date_str = post['date']
        
        # We will loop twice, once for Tamil and once for English
        for current_lang in ['ta', 'en']:
            is_english = (current_lang == 'en')
            
            title = post.get('title_en', post['title']) if is_english else post['title']
            src_file = post.get('src_en', post['src']) if is_english else post['src']
            if is_english:
                src_file = "en/" + src_file
                
            # Read post text content
            src_path = os.path.join(BASE_DIR, 'raw_posts', src_file)
            if not os.path.exists(src_path):
                print(f"Error: Source file {src_path} not found for post {post_id}")
                continue
                
            with open(src_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Render paragraphs
            paragraphs_raw = re.split(r'\\n\\s*\\n', text_content.strip())
            paragraphs = []
            for p in paragraphs_raw:
                p_stripped = p.strip()
                if p_stripped:
                    if p_stripped.startswith('<'):
                        paragraphs.append(p_stripped)
                    else:
                        p_formatted = p_stripped.replace('\\n', '<br>')
                        p_formatted = linkify(p_formatted)
                        paragraphs.append(f"<p>{p_formatted}</p>")
            content_html = "".join(paragraphs)

            # Word count & reading time
            word_count = len(text_content.strip().split())
            reading_time = max(1, (word_count + 199) // 200)
            read_time_str = f"{reading_time} min read"

            # Canonical post URLs
            base_url = f"https://www.vishravars.me/posts/{post_id}/"
            canonical_post_url = f"https://www.vishravars.me/posts/{post_id}/en/" if is_english else base_url
            encoded_live_url = __import__('urllib').parse.quote_plus(canonical_post_url)
            encoded_title = __import__('urllib').parse.quote_plus(title)

            # Pre-rendered translate link
            if is_english:
                translate_link_html = f'''<a href="../" class="translate-link post-meta-separator">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                    தமிழில் படிக்க
                </a>'''
            else:
                translate_link_html = f'''<a href="en/" class="translate-link post-meta-separator">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                    Read in English
                </a>'''
            
            # index.html translate link (bottom row next to read article)
            if not is_english:
                index_translate_link_html = f'''<a href="/posts/{post_id}/en/" class="translate-link">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                                        Read in English
                                    </a>'''

            # Description and dynamic SEO properties
            description = post.get('description_en') if is_english else post.get('description')
            if not description:
                clean_text = re.sub(r'\\s+', ' ', text_content).strip()
                description = clean_text[:155].strip() + '...' if len(clean_text) > 155 else clean_text
            
            description_escaped = html.escape(description)
            
            og_image_url = f"https://www.vishravars.me/images/{post['image']}" if post.get('image') else "https://www.vishravars.me/images/banner.png"

            # Parse ISO date for post sitemap and JSON-LD
            iso_date = latest_date_iso
            try:
                dt = datetime.datetime.strptime(date_str, "%B %d, %Y")
                iso_date = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

            # Generate JSON-LD for post
            post_json_ld = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": title,
                "datePublished": iso_date,
                "dateModified": iso_date,
                "description": description,
                "image": og_image_url,
                "author": {
                    "@type": "Person",
                    "name": "Vishravars",
                    "url": "https://www.vishravars.me/"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "The Writings of Vishravars",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://www.vishravars.me/images/banner.png"
                    }
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": canonical_post_url
                }
            }
            json_ld_str = json.dumps(post_json_ld, ensure_ascii=False, indent=2)

            # Populate post page template
            post_html = post_template
            
            # Render featured image if present
            featured_image_html = ""
            if post.get('image'):
                img_name = post['image']
                featured_image_html = f'<div class="featured-image-container" style="text-align: center; margin-bottom: 2.5rem;"><img src="/images/{img_name}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"></div>'

            post_html = post_html.replace('{{TITLE}}', title)
            post_html = post_html.replace('{{DATE}}', date_str)
            post_html = post_html.replace('{{LANG}}', current_lang)
            post_html = post_html.replace('{{READ_TIME}}', read_time_str)
            post_html = post_html.replace('{{TRANSLATE_LINK_HTML}}', translate_link_html)
            post_html = post_html.replace('{{FEATURED_IMAGE}}', featured_image_html)
            post_html = post_html.replace('{{CONTENT}}', content_html)
            post_html = post_html.replace('{{SHARE_URL}}', encoded_live_url)
            post_html = post_html.replace('{{SHARE_TEXT}}', encoded_title)
            
            # New SEO replacements
            post_html = post_html.replace('{{META_DESCRIPTION}}', description_escaped)
            post_html = post_html.replace('{{CANONICAL_URL}}', canonical_post_url)
            post_html = post_html.replace('{{OG_IMAGE_URL}}', og_image_url)
            post_html = post_html.replace('{{JSON_LD}}', json_ld_str)

            # Create output directory for post
            post_output_dir = os.path.join(POSTS_DIR, post_id, 'en') if is_english else os.path.join(POSTS_DIR, post_id)
            if not os.path.exists(post_output_dir):
                os.makedirs(post_output_dir)
                
            with open(os.path.join(post_output_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(post_html)
            print(f"Generated post page: /posts/{post_id}{'/en' if is_english else ''}/index.html")

            # Create index.html preview (only for Tamil, with the link to English)
            if not is_english:
                plain_text = re.sub(r'\\s+', ' ', text_content).strip()
                preview_text = plain_text[:250].strip() + '...' if len(plain_text) > 250 else plain_text
                
                article_item_html = f'''        <article>
                    <time class="article-meta">{date_str}</time>
                    <h2 class="article-title" lang="{current_lang}"><a href="/posts/{post_id}/">{title}</a></h2>
                    <div class="article-content" lang="{current_lang}">
                        <p>{preview_text}</p>
                    </div>
                    <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
                        <a href="/posts/{post_id}/" class="read-more">Read article <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg></a>
                        {index_translate_link_html}
                    </div>
                </article>'''
                articles_html.append(article_item_html)

            # Add post to sitemap
            sitemap_items.append(f'''    <url>
            <loc>{canonical_post_url}</loc>
            <lastmod>{iso_date}</lastmod>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>''')

        # Build RSS item (only once per post, point to Tamil)
        pub_date_rfc = format_rfc822_date(date_str)
        rss_item = f'''    <item>
        <title>{post['title']}</title>
        <link>https://www.vishravars.me/posts/{post_id}/</link>
        <description>{post.get('description', '')}</description>
        <pubDate>{pub_date_rfc}</pubDate>
    </item>'''
        rss_items.append(rss_item)"""

# Find where the original loop ends.
# It ends right before "# Generate index.html"
end_of_loop_marker = "    # Generate index.html"

# Extract parts
before_loop = content.split("    for post in posts:\n        post_id = post['id']")[0]
after_loop = end_of_loop_marker + content.split(end_of_loop_marker)[1]

# Now for pages
# REWRITE the page loop
page_loop_start = """    # Process Static Pages
    for page in pages:
        page_id = page['id']"""

new_page_loop = """    # Process Static Pages
    for page in pages:
        page_id = page['id']
        
        for current_lang in ['ta', 'en']:
            is_english = (current_lang == 'en')
            
            title = page.get('title_en', page['title']) if is_english else page['title']
            src_file = page.get('src_en', page['src']) if is_english else page['src']
            if is_english:
                src_file = "en/" + src_file
                
            description = page.get('description_en') if is_english else page.get('description', '')
            
            src_path = os.path.join(PAGES_DIR, src_file)
            if not os.path.exists(src_path):
                print(f"Warning: Source file for page {page_id} not found at {src_path}")
                continue
                
            with open(src_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
                
            paragraphs_raw = re.split(r'\\n\\s*\\n', text_content.strip())
            paragraphs = []
            for p in paragraphs_raw:
                p_stripped = p.strip()
                if p_stripped:
                    if p_stripped.startswith('<') and p_stripped.endswith('>'):
                        paragraphs.append(p_stripped)
                    else:
                        p_formatted = p_stripped.replace('\\n', '<br>')
                        p_formatted = linkify(p_formatted)
                        paragraphs.append(f'<p>{p_formatted}</p>')
                        
            page_content_html = "\\n".join(paragraphs)
            
            base_url = f"https://www.vishravars.me/{page_id}/"
            canonical_url = f"https://www.vishravars.me/{page_id}/en/" if is_english else base_url
            
            # Pre-rendered translate link
            if is_english:
                translate_link_html = f'''<a href="../" class="translate-link post-meta-separator">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                    தமிழில் படிக்க
                </a>'''
            else:
                translate_link_html = f'''<a href="en/" class="translate-link post-meta-separator">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" style="display: inline-block; vertical-align: middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.006 1.896-.46 3.657-1.251 5.201M12.751 5a17.9 17.9 0 00-3.336-3M9 9a14.57 14.57 0 01-2.588-3M6 9h4.948"></path></svg>
                    Read in English
                </a>'''
            
            # Build JSON-LD
            json_ld = {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "description": description,
                "url": canonical_url,
                "publisher": {
                    "@type": "Person",
                    "name": "Vishravars"
                }
            }
            json_ld_str = json.dumps(json_ld, ensure_ascii=False, indent=2)
            
            page_html = page_template.replace('{{TITLE}}', __import__('html').escape(title))
            page_html = page_html.replace('{{LANG}}', current_lang)
            page_html = page_html.replace('{{META_DESCRIPTION}}', __import__('html').escape(description))
            page_html = page_html.replace('{{CANONICAL_URL}}', canonical_url)
            page_html = page_html.replace('{{TRANSLATE_LINK_HTML}}', translate_link_html)
            page_html = page_html.replace('{{OG_IMAGE_URL}}', "https://www.vishravars.me/images/banner.png")
            page_html = page_html.replace('{{JSON_LD}}', json_ld_str)
            page_html = page_html.replace('{{CONTENT}}', page_content_html)
            # FEATURED_IMAGE isn't implemented for static pages right now, remove template var
            page_html = page_html.replace('{{FEATURED_IMAGE}}', '')
            
            page_output_dir = os.path.join(BASE_DIR, page_id, 'en') if is_english else os.path.join(BASE_DIR, page_id)
            if not os.path.exists(page_output_dir):
                os.makedirs(page_output_dir)
                
            with open(os.path.join(page_output_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"Generated page: /{page_id}{'/en' if is_english else ''}/index.html")
            
            # Add page to sitemap
            sitemap_items.append(f'''    <url>
            <loc>{canonical_url}</loc>
            <lastmod>{latest_date_iso}</lastmod>
            <changefreq>monthly</changefreq>
            <priority>0.8</priority>
        </url>''')"""

# Find where page loop starts and ends
before_page_loop = after_loop.split(page_loop_start)[0]
end_of_page_loop_marker = "    # Generate rss.xml"
after_page_loop = end_of_page_loop_marker + after_loop.split(end_of_page_loop_marker)[1]

new_content = before_loop + new_post_loop + "\n\n" + before_page_loop + new_page_loop + "\n\n" + after_page_loop

with open(gen_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
