# CORD-19
Code and data for the https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/

* Question n°1: Where and how to find relevant information?
  - Build: papers metadata file
  - Build: authors metadata file
  - Build: authors network
  - Build: paper network

## Structure

### Scrape

I scrape articles by source. For now I use the paper urls in the dataframe
'metadata.csv'.
For now, I also only scrape papers from 'bioRxiv' as I have only written the code
for that html page.

Scraped articles are saved in .json format to the data folder under respective
sources for clarity.

**Scraping and storage Ideas:**
* Scrape all sources
* Manage all exceptions
* Store articles and authors with Neo4J

### Analysis

- For each article, I want to extract keywords, key sentences and key paragraphs.
- I want to get statistics of articles: # authors, # references and so on.
- I want to compare articles with each other to find relevant terms and
similarities and differences.

**Analysis Ideas:**
* Build authors / co-authors network
* Build article references network
* Find isolated articles and articles that are highly connected
* [!] *Compare articles using word vector in addition to network structure*
* Recommend article reading and in-depth human analysis

### Visualization

- I want to visualize each article in HTML format in the browser.
- I want to visualize keywords, sentences and paragraphs with highlighting.

**Visualization Ideas:**
* Build research article navigator, display list of articles available and choose
articles to view.
* View article statistics and content.
* Click on author to display author information
* Click on reference (if data available) to open reference in new window
* Click on highlighted term to see associated information: similar articles, etc.
* Visualize references network
* Visualize authors network
