#!/usr/bin/env python3
import requests
import pandas as pd
from xml.etree import ElementTree

# Define search terms
search_terms = [
    'Brunei', 'Cambodia', 'Indonesia', 'Malaysia', 'Myanmar', 'Laos', 'Philippines', 
    'Singapore', 'Thailand', 'Timor', 'Vietnam', 'SE Asia', 'South East Asia', 'Southeast Asia', 
    'Southeastern Asia', 'Streptococcus pneumoniae', 'S pneumoniae', 'pneumococc', 'pneumonia'
]

# Create the search query for region and terms
region_terms = " OR ".join(search_terms)

# Add the additional condition for "whole genome" or "whole genome sequencing"
search_query = f"({region_terms}) AND (\"whole genome\" OR \"genome\")"

# Define the PubMed URL for search (e.g., PubMed, PubMed Central)
pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    'db': 'pubmed',  # either pubmed or pmc
    'term': search_query,  # The search query
    # 'retmax': 1000,  # Number of results to return (reasonable limit)
    'retmode': 'xml',  # Format of the result
    'datetype': 'pdat',  # Date of publication
    'maxdate': '2024',  # Maximum publication date
}

# Send the request to PubMed API
response = requests.get(pubmed_url, params=params)

# Debugging response
if response.status_code == 200:
    print("Request successful!")
    print(response.content.decode('utf-8'))  # Debugging: print raw response content
    try:
        # Parse the XML response to get article IDs
        tree = ElementTree.fromstring(response.content)
        article_ids = [id_elem.text for id_elem in tree.findall(".//Id")]
        print(f"Found {len(article_ids)} articles matching the search.")
    except ElementTree.ParseError as e:
        print(f"XML Parse Error: {e}")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print(response.content.decode('utf-8'))  # Debugging: inspect response content


# Function to fetch article details
def fetch_article_details(article_ids):
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        'db': 'pubmed',
        'id': ','.join(article_ids),
        'retmode': 'xml'
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)
    articles = []

    if fetch_response.status_code == 200:
        # Parse and extract details
        fetch_tree = ElementTree.fromstring(fetch_response.content)
        for article in fetch_tree.findall(".//PubmedArticle"):
            title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"
            pub_date = article.find(".//PubDate/Year").text if article.find(".//PubDate/Year") is not None else "N/A"
            authors = ', '.join([
                (author.find(".//LastName").text if author.find(".//LastName") is not None else "") + " " +
                (author.find(".//ForeName").text if author.find(".//ForeName") is not None else "")
                 for author in article.findall(".//Author")
                 if author.find(".//LastName") is not None or author.find(".//ForeName") is not None
               ]) or "N/A"
            abstract = article.find(".//AbstractText").text if article.find(".//AbstractText") is not None else "N/A"

            articles.append({
                'Title': title,
                'Published Date': pub_date,
                'Authors': authors,
                'Abstract': abstract
            })

    return articles

# Fetch details for the articles
articles = fetch_article_details(article_ids)

# Convert to a DataFrame and output to CSV
df = pd.DataFrame(articles)
df.to_csv('pubmed_articles.csv', index=False)
print("CSV file saved.")



