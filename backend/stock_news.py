from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime

def get_news_from_motley_fool(ticker: str = None):
    """
    Get news articles from Motley Fool
    Args:
        ticker: Optional stock symbol to filter news (if None, returns all news)
    """
    # Base URL for Motley Fool news
    url = "https://www.fool.com/investing-news"
    if ticker:
        url = f"https://www.fool.com/quote/{ticker}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Find all article links
            for article in soup.find_all('a', href=True):
                try:
                    href = article['href']
                    # Only process article links
                    if '/investing/' in href or '/earnings/' in href or '/market-news/' in href:
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            href = f"https://www.fool.com{href}"
                            
                        # Get the article title if available
                        title = article.text.strip()
                        if not title and article.find('h2'):
                            title = article.find('h2').text.strip()
                            
                        if title and href not in [a['link'] for a in articles]:  # Avoid duplicates
                            article_data = {
                                'title': title,
                                'link': href,
                                'source': 'Motley Fool'
                            }
                            articles.append(article_data)
                except Exception as e:
                    print(f"Error processing article link: {str(e)}")
                    continue
                    
            return articles
        else:
            print(f"Error: Failed to fetch page. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
        return []

def visit_link(link: str):
    """
    Visit the article link and extract the content
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'aside']):
                element.decompose()
            
            # Try to get the article content
            article = soup.find('div', {'id': 'article-body'}) or \
                     soup.find('div', {'class': 'article-body'}) or \
                     soup.find('div', {'class': 'content-block'})
            
            if article:
                return article.get_text(separator='\n', strip=True)
            
            # If no specific content found, return cleaned page text
            text = soup.get_text(separator='\n', strip=True)
            return text
        else:
            return f"Error: Could not fetch content. Status code: {response.status_code}"
            
    except requests.Timeout:
        return "Error: Request timed out"
    except requests.RequestException as e:
        return f"Error: Failed to fetch content - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"

class Article:
    def __init__(self, title: str, link: str, source: str):
        self.title = title
        self.link = link
        self.source = source
    
    def get_article_data(self):
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source
        }

# Example usage
if __name__ == "__main__":
    # Get all news articles
    articles = get_news_from_motley_fool()
    # Or filter by ticker
    # articles = get_news_from_motley_fool("AAPL")
    
    if articles:
        print(f"Found {len(articles)} articles from Motley Fool:")
        for article in articles:
            print("\n" + "="*80)
            print(f"Title: {article['title']}")
            print(f"Link: {article['link']}")
            print("\nArticle preview:")
            content = visit_link(article['link'])
            print(content[:500] + "..." if len(content) > 500 else content)
            print("="*80)
            time.sleep(1)  # Be nice to the server
    else:
        print("No articles found")
