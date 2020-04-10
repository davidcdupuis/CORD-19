# A script to scrape research articles online

import requests
import json
import pandas as pd

from bs4 import BeautifulSoup
from itertools import chain
from utils import get_file_names, generate_sha

def scrape_biorxiv(paper):
    print('Fetching paper data at {}'.format(paper['url']))
    html = session.get(paper['url'])
    tmp_soup = BeautifulSoup(html.content, 'html.parser')
    paper_webdata = biorxiv_html_paper_data_extractor(tmp_soup)
    paper = dict(chain(paper.items(),paper_webdata.items()))
    return paper

def get_biorxiv_authors(authors_html):
    ''' HTML list of authors
    '''
    authors = []
    for author in authors_html:
        try:
            given_name = author.find('span',attrs={'class':'nlm-given-names'}).text
        except:
            given_name = ''
        try:
            surname = author.find('span',attrs={'class':'nlm-surname'}).text
        except:
            surname = ''
        authors.append(given_name + ' ' + surname)
    return authors

def process_paragraph(paragraph):
    ''' Removes and modifies html tags in paragraphs
    '''
    for anchor in paragraph.find_all('a'):
        anchor.replace_with('[' + anchor['href'].strip('#') + ',' + anchor.text + ']')
    return paragraph.text

def explore_section(root_tag):
    '''Recursively explore section and all subsections for content
    '''
    content = {}
    content['title'] = ''
    content['content'] = []
    for child in root_tag.findChildren(recursive=False):
        if child.name == 'h2' or child.name == 'h3' or child.name == 'h4':
            content['title'] = child.text
        elif child.name == 'p':
            content['content'].append(process_paragraph(child))
        if child.name == 'div':
            if 'class' in child.attrs:
                if 'subsection' in child['class']:
                    # if subsection explore recursively
                    content['content'].append(explore_section(child))
            elif 'id' in child.attrs.keys():
                if 'T' in child['id']:
                    content.append({'id':child['id'],'type':'table'})
                elif 'F' in child['id']:
                    content.append({'id':child['id'],'type':'figure'})
    else:
        return content

def get_biorxiv_sections(sections_html):
    '''
    '''
    sections = []
    for section in sections_html:
        # ignore references
        if 'ref-list' not in section.attrs['class'] :
            sections.append(explore_section(section))
    return sections

def get_biorxiv_tables(html_tables):
    tables = []
    for html_table in html_tables:
        table = {}
        table['id'] = html_table['id']

        table_label = html_table.find('span',attrs={'class':'table-label'})
        if table_label:
            table['label'] = table_label.text

        table_caption = html_table.find('span',attrs={'class':'caption-title'})
        if table_caption:
            table['caption'] = table_caption.text

        table['description'] = ''
        for p in html_table.find_all('p'):
            table['description'] += p.text + '\n'
        table['image'] = None
        tables.append(table)
    return tables

def get_biorxiv_figures(figures_html):
    figures = []
    for html_figure in figures_html:
        figure = {}

        figure_label = html_figure.find('span',attrs={'class':'fig-label'})
        if figure_label:
            figure['label'] = figure_label.text

        figure_title = html_figure.find('span',attrs={'class':'caption-title'})
        if figure_title:
            figure['title'] = figure_title.text

        figure['description'] = ''
        figure_ps = html_figure.find_all('p')
        for p in figure_ps:
            figure['description'] += p.text + '\n'
        figures.append(figure)
        figure_img = html_figure.find('img')
        if figure_img:
            figure['img'] = figure_img['data-src']
    return figures

def get_biorxiv_references(references_html):
    ''' HTML list of references
    soup.find('div',attrs={'class':'section ref-list'}).find_all('li')
    '''
    references = []
    for ref in references_html:
        reference = {}
        # label
        try:
            reference['label'] = ref.find('span',attrs={'class':'ref-label'}).text
        except:
            reference['label'] = None

        # authors
        author_names = []
        try:
            authors = ref.find('cite').find_all('span',attrs={'class':'cit-auth'})
            for author in authors:
                surname = author.find('span',attrs={'class':'cit-name-surname'}).text
                given_names = author.find('span',attrs={'class':'cit-name-given-names'}).text
                author_name = surname + ' ' + given_names
                author_names.append(author_name)
            reference['authors'] = author_names
        except:
            reference['authors'] = author_names

        # date
        try:
            reference['date'] = ref.find('cite').find('span',attrs={'class':'cit-pub-date'}).text
        except:
            reference['date'] = None

        # title
        try:
            reference['title'] = ref.find('cite').find('span',attrs={'class':'cit-article-title'}).text
        except:
            reference['title'] = ''

        # links
        ref_links = []
        try:
            links = ref.find('div',attrs={'class':'cit-extra'}).find_all('a')
            for link in links:
                if link.text != 'OpenUrl':
                    link_name = link.text
                    link_url = link['href']
                    ref_links.append((link_name,link_url))
            reference['links'] = ref_links
        except:
            reference['links'] = ref_links
        references.append(reference)
    return references

def biorxiv_html_paper_data_extractor(soup):
    '''
        Extract paper information from html webpage of biorxiv
    '''
    paper = {}
    paper['title'] = soup.h1.text

    authors_html = soup.find('span',attrs={'class':'highwire-citation-authors'}) \
                       .find_all('span',attrs={'class':'highwire-citation-author'})
    paper['authors'] = get_biorxiv_authors(authors_html)

    sections_html = soup.find_all('div',attrs={'class':'section'})
    paper['sections'] = get_biorxiv_sections(sections_html)

    tables_html = soup.find_all('div',attrs={'class':'table'})
    paper['tables'] = get_biorxiv_tables(tables_html)

    # get figures
    figures_html = soup.find_all('div',attrs={'class':'fig'})


    paper['figures'] = get_biorxiv_figures(figures_html)

    # get references
    references_html = soup.find('div',attrs={'class':'section ref-list'}).find_all('li')
    paper['references'] = get_biorxiv_references(references_html)

    return paper

if __name__ == "__main__":
    source = 'biorxiv'
    print("\nThis script only scrapes articles from {}, if not already downloaded.".format(source))

    session = requests.session()

    # import list of articles in data folder
    existing_shas = [name.strip('.json') for name in get_file_names('data/{}'.format(source))]

    # import metadata dataframe
    df_meta = pd.read_csv('metadata.csv')

    '''
    sources = df_meta['source_x'].unique()
    for source in sources:
        papers_df = df_meta[df_meta['source_x']==source][['sha','doi']]
        papers_array = papers_df.to_numpy()
        print('There are {} papers ids from {}.'.format(len(papers_array), source))
    '''

    missing_articles = df_meta[(df_meta['source_x']==source)&(~df_meta['sha'].isin(existing_shas))]
    print("{} articles to scrape".format(missing_articles.shape[0]))

    papers_df = missing_articles[['sha','doi']]
    papers_array = papers_df.to_numpy()
    indexes = papers_df.index.to_numpy()

    # keep track of index
    i = 0
    for row in papers_array:
        paper = {}
        paper['source'] = source
        # if no sha => generate one that doesn't exist.
        if str(row[0]) == 'nan':
            paper['id'] = generate_sha(existing_shas)
            # save new hash and add to existing_shas
            existing_shas.append(paper['id'])
            df_meta.loc[indexes[i], 'sha'] = paper['id']
            df_meta.to_csv('new_metadata.csv')
        else:
            paper['id'] = row[0]
        paper['url'] = 'https://biorxiv.org/content/' + row[1].strip('doi.org') + 'v1.full'
        if source == 'biorxiv':
            paper = scrape_biorxiv(paper)
        else:
            print('Error source not biorxiv. ({})'.format(source))
        with open('data/{}/{}.json'.format(source,paper['id'])):
            json.dump(paper, fp, indent=4)
        print('Paper ID: {} saved to data/{}'.format(paper['id'], source))
        print('-'*60)
        i += 1


    print("")
