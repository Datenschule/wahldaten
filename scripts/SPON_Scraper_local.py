
# coding: utf-8


#Importing Libraries
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
from newspaper import Article 
from sqlalchemy import create_engine
import pymysql

df_db = pd.read_csv('/Users/Waspish/Documents/OKF/wahldaten-ds/SPON_Politics.csv', sep=";")




#Media-Sources for obtaining Feeds
Newspaper = {
			"spiegel" : "http://www.spiegel.de/politik/index.rss",
			}

Summary = []
Link = []
Title = []
Datum = []
Base = []


All_feeds = []

#Get all current feeds
for key, value in Newspaper.items():
    feeds = feedparser.parse(value)
    articles = {key:feeds}
    All_feeds.append(feeds)

#Convert to DataFrame
for feeds in All_feeds:
    for f in feeds.entries:
        article_summary = f['summary']
        article_base = f['title_detail']['base']
        #article_newspaper = [feeds+len(article_summary)]
        article_link = f['link']
        article_title = f['title_detail']['value']
        #article_terms = f['tags'][0]['term']
        article_publish = f['published']

        Summary.append(article_summary)
        Link.append(article_link)
        Title.append(article_title)
        Datum.append(article_publish)
        Base.append(article_base)

df = pd.DataFrame({'Titles': Title,
                             'Newspaper':Base,
                             'Dates': Datum,
                             'Links': Link,
                             'Summary': Summary
                            })



#Check if Article is already in CSV
df = df[df.Links.isin(df_db.Links)== False]

#Define Function for scraping new articles
def get_info(s):
    article = Article(s)
    article.download()
    article.parse()
    authors = str(article.authors)
    text = article.text
    top_image = article.top_image
    movies = article.movies
    soup = BeautifulSoup(article.html,'lxml')
    keywords = soup.findAll('meta', {'name':'news_keywords'})
    info = soup.select('#js-article-column > p > i')
    
    if not info and not keywords:
        return(text,authors,top_image,movies,None,None)
    elif not keywords:
        return(text,authors,top_image,movies,None,info[0].string) 
    elif not info:
        return(text,authors,top_image,movies,keywords[0]['content'],None)       
    else:
        return(text,authors,top_image,movies,keywords[0]['content'],info[0].string)


#If new articles were found. Concat new articles with csv of already scraped articles. Replace old csv
if len(df) > 0:
    df["Fulltexts"], df["Author"], df['Top_image_link'], df['Movie_link'], df['Keywording'],df['Sources'] = zip(*df["Links"].apply(get_info))
    df = df.replace( {'Author' :
                            { "[" : '', 
                              "]": '',
                              "'Spiegel Online',":'',
                              "'Hamburg',":'',
                              "'Hamburg'":'',
                              "'Twitter'":'',
                              "'E-Mail',":'',
                              "'E-Mail',":'',
                              "'Google',":'',
                              "'Google'" :'',
                              "'Facebook'":'',
                              "'Blog'":'',
                              "'Pgp'":''

                              }})
    df['Author'] = df.Author.str.split(',')
    #df['Author'] = df.Author.str.replace('[' ']',None)
    #df['Movie_link'] = df.Movie_link.str.replace('[]',None)
    frames = [df_db,df]
    Export = pd.concat(frames)
    Export.to_csv('/Users/Waspish/Documents/OKF/wahldaten-ds/SPON_Politics.csv', sep=";",index=False, line_terminator="\n")
    print(len(df), ' were added to database')
else:
    print('no new articles found at SPON/Politics')