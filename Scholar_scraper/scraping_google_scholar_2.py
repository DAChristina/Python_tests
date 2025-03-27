#!/usr/bin/env python3
from scholarly import scholarly, ProxyGenerator
import pandas as pd

# Define the query
query = '(("Brunei" OR "Cambodia" OR "Indonesia" OR "Malaysia" OR "Myanmar" OR "Laos" OR "Philippines" OR "Singapore" OR "Thailand" OR "Timor" OR "Vietnam" OR "SE Asia" OR "South East Asia" OR "Southeast Asia" OR "Southeastern Asia") AND ("S pneumoniae")) AND ("whole genome sequencing")'

# Configure proxy settings
pg = ProxyGenerator()

# Attempt to use free proxies
if not pg.FreeProxies():
    print("Failed to set up FreeProxies. Trying with Tor...")
    # Use Tor if free proxies are not working
    tor_path = "/usr/bin/tor"  # Adjust the path to your Tor executable
    if not pg.Tor_Internal(tor_cmd=tor_path):
        raise Exception("Failed to set up Tor proxy.")
scholarly.use_proxy(pg)

# Fetch results from Google Scholar
articles = []
search_query = scholarly.search_pubs(query)

# Process the results
for article in search_query:
    # Extract details
    title = article.get("bib", {}).get("title", "N/A")
    pub_date = article.get("bib", {}).get("pub_year", "N/A")
    authors = ", ".join(article.get("bib", {}).get("author", []))
    abstract = article.get("bib", {}).get("abstract", "N/A")
    
    # Append to articles list
    articles.append({
        'Title': title,
        'Published Date': pub_date,
        'Authors': authors,
        'Abstract': abstract
    })

# Convert to DataFrame and save to CSV
df = pd.DataFrame(articles)
df.to_csv("google_scholar_results.csv", index=False)
print("Scraping completed. Results saved to 'google_scholar_results.csv'.")

