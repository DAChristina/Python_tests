# Adapted from https://github.com/MahdiNavaei/Google-Scholar-Scraper
import random
from scholarly import ProxyGenerator, scholarly
import pandas as pd
import time
import sys
import os

os.chdir(sys.path[0])
data = pd.read_csv('Strep_INV104_Ref_geneBank_annotations_peak_phandango_compiled.csv', usecols=[0]) + " Streptococcus" # ignore column 2 & 3 (py index start with 0), add Strep keyword for each proteins

data['protein_sequence'] = data['protein_sequence'].str.replace('/', '', regex=False)

proteins = data.iloc[:, 0].tolist()
# proteins = list(compiled_phandango_peak)


output_dir = "outputs_phandango_literature_proteins"
os.makedirs(output_dir, exist_ok=True)

# Using tor according to https://github.com/scholarly-python-package/scholarly/issues/139
# test_tor = scholarly.launch_tor('usr/bin/tor',
#                                 tor_sock_port=random.randint(9000, 9499),
#                                 tor_control_port=random.randint(9500, 9999))

# Iteration

# Use proxy generator according to: https://pypi.org/project/scholarly/
# This needs to be done only once per session
pg = ProxyGenerator()
if not pg.FreeProxies():
    print("Failed to set up FreeProxies. Trying with Tor...")
    # Use Tor if free proxies are not working
    tor_path = "/usr/bin/tor"  # Adjust the path to the tor executable
    if not pg.Tor_Internal(tor_cmd=tor_path):
        raise Exception("Failed to set up Tor proxy.")
scholarly.use_proxy(pg)

for query in proteins:
    print(f"Searching for: {query}")
    
    try:
        search_query = scholarly.search_pubs(query)
    except Exception as e:
        print(f"Error: {e}")
        continue
    
    # Empty list to hold the data
    data = []
    
    # Top 10 papers
    for i in range(10):
        try:
            paper = next(search_query)
            
            # Check if 'bib' attribute exists in paper object
            if 'bib' in paper:
                title = paper['bib'].get('title', 'N/A')
                year = paper['bib'].get('pub_year', 'N/A')
                abstract = paper['bib'].get('abstract', 'N/A')
                file_name = query
                data.append([title, year, abstract, file_name])
            else:
                print(f"Paper object for '{query}' does not have 'bib' attribute.")
                break
                
        except StopIteration:
            print(f"Less than 5 results found for query: {query}")
            break
        except Exception as e:
            print(f"Error fetching paper: {e}")

            continue


    # Data to a DataFrame
    df = pd.DataFrame(data, columns=["Title", "Year", "Abstract", "file_name"])
    filename = f"{query.replace(' ', '_')}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    time.sleep(10)
    print(f"CSV file '{filepath}' created successfully!")

print("SEE 'outputs_phandango_literature_proteins'!")


