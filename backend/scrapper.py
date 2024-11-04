import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import re

def clean_filename(text):
    """Clean text to make it suitable for filenames"""
    # Remove special characters and replace spaces with underscores
    return re.sub(r'[^\w\s-]', '', text).replace(' ', '_')

def parse_date(date_str):
    """Parse date string to consistent format"""
    try:
        # Extract date part if author name is included
        # Example: "By Nadine PEREIRA10/31/2024" -> "10/31/2024"
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', date_str)
        if date_match:
            date_str = date_match.group(1)
            
        # Parse date (assuming format "MM/DD/YYYY")
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        return date_obj.strftime("%Y%m%d")  # Return as YYYYMMDD
    except (ValueError, AttributeError):
        return "00000000"  # Return placeholder if parsing fails

def scrape_articles(url, output_dir):
    """Scrape articles from the given URL"""
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all article containers
        articles = soup.find_all('div', class_='styles_container__zdTXi')
        
        for article in articles:
            try:
                # Extract title
                title_element = article.find('div', class_='styles_title__1L5aY')
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # Extract date and author
                date_element = article.find('div', class_='styles_subtitle__NDNZ4')
                date_text = date_element.text.strip() if date_element else ''
                formatted_date = parse_date(date_text)
                
                # Extract content
                content_element = article.find('div', class_='styles_content__fcopH')
                content = content_element.text.strip() if content_element else ''
                
                # Create filename
                clean_title = clean_filename(title)
                filename = f"news_{formatted_date}_{clean_title[:50]}.txt"  # Limit title length
                full_path = os.path.join(output_dir, filename)

                # Create content structure with proper formatting
                article_content = f"""header: {title}
date: {date_text}
content: {content}
"""
                
                # Check if file already exists
                if os.path.exists(full_path):
                    print(f"File already exists, skipping: {filename}")
                    continue
                
                # Save to file
                print(f"Creating file: {filename}")
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(article_content)
                print(f"Successfully saved: {filename}")
                
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    # Get the absolute path to the articles directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    articles_dir = os.path.join(project_root, 'articles')
    
    # Create output directory if it doesn't exist
    os.makedirs(articles_dir, exist_ok=True)
    
    # URL to scrape
    url = "https://www.swissquote.com/en-ch/private/inspire/expert-insights/morning-news"
    
    print("Starting article scraping...")
    print(f"Saving articles to: {articles_dir}")
    scrape_articles(url, articles_dir)
    print("Scraping completed!")

if __name__ == "__main__":
    main()