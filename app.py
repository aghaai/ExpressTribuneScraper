# scraper-tribune.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_tribune_world():
    url = 'https://tribune.com.pk/world'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    for card in soup.select('a[href*="/story/"]'):
        title = card.get_text(strip=True)
        link = card['href']
        if not link.startswith('http'):
            link = 'https://tribune.com.pk' + link
        if title and link not in [a['link'] for a in articles]:
            # Fetch article content
            content = ""
            try:
                article_resp = requests.get(link)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                for selector in [
                    'div.story-area p',
                    'div.story__content p',
                    'div.article-content p',
                    'div.news-story p',
                    'article p',
                    '.story-detail p'
                ]:
                    paragraphs = article_soup.select(selector)
                    if paragraphs:
                        content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                        break
                if not content:
                    paragraphs = article_soup.find_all('p')
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            except Exception as e:
                content = f"Error fetching article content: {e}"
            articles.append({'title': title, 'link': link, 'content': content})

    # Print results (optional)
    for art in articles:
        print(f"Title: {art['title']}")
        print(f"Link: {art['link']}")
        print("Summary/Content:")
        print(art['content'][:500] + ("..." if len(art['content']) > 500 else ""))
        print('-' * 60)

    # Save to Excel
    save_to_excel(articles)

def save_to_excel(articles, filename="tribune_news.xlsx"):
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}")

if __name__ == '__main__':
    while True:
        scrape_tribune_world()
        print("Sleeping for 10 minutes...")
        time.sleep(600)  # 600 seconds = 10 minutes
