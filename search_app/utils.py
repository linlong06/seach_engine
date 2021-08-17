# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# function to crawl web content and save it into the database with a given root url and max depth
def crawl(root_url, max_depth = 2):
    
    # initiate database connection
    client = MongoClient('localhost', 27017)
    db = client.crawler
    
    # initiate visited url set and url queue for BFS
    seen_url = set()
    seen_url.add(root_url)
    queue_url = [root_url]
    depth = 0
    
    # use BFS to crawl through all links within max_depth of the root url
    while queue_url and depth < max_depth:
        depth += 1
        size = len(queue_url)
        
        for i in range(size):      
            url = queue_url.pop(0)      
            try:
                response = requests.get(url)
            except:
                continue
            
            content = BeautifulSoup(response.text, 'lxml')
            try:
                title = content.find('title').text
            except:
                title = 'N/A'
            description = content.get_text().strip().replace('\n', ' ')
            
            # save the web content in result object
            result = {
                'url': url,
                'title': title,
                'description': description
                }
            
            entry = db.websites.find_one({'url': url})
            if entry:
                db.websites.update_one(
                    {'url': url},
                    {'$set': {'title': title, 'description': description}})
            else:
                db.websites.insert_one(result)
            
            links = content.find_all('a')
            for link in links:
                url_next = link.get('href')
                if (url_next and url_next not in seen_url):
                    if not url_next.startswith('http'):
                        url_next = url + url_next
                    seen_url.add(url_next)
                    queue_url.append(url_next)
        

# function to query a word and return list of links with scores
def query(word):
    result = []
    
    if word is None or len(word) == 0:
        return result
    
    # initiate database connection
    client = MongoClient('localhost', 27017)
    db = client.crawler 
    
    # covert query to lower case for exact matching
    word = word.lower()
    
    records = db.websites.find({})
    for record in records:
        score = 0;
        if word in record['title'].lower():
            score += 1000
        score += record['description'].lower().count(word)
        
        if score > 0:
            result.append({'score': score, 'url': record['url']})
    
    result.sort(key = lambda x: x['score'], reverse = True)
    return result[0 : min(10, len(result))]

def query_sentence(sentence):
    result = []
    
    if sentence is None or len(sentence) == 0:
        return result
    
    # initiate database connection
    client = MongoClient('localhost', 27017)
    db = client.crawler 
    
    # covert query to lower case for exact matching
    sentence = sentence.lower()
    words = sentence.split()
    
    records = db.websites.find({})
    for record in records:
        score = 0
        
        if sentence in record['title'].lower():
            score += 10000000
        score += record['description'].lower().count(sentence) * 1000
        
        if (len(words) > 1):
            for word in words:
                if word in record['title'].lower():
                    score += 1000
                score += record['description'].lower().count(word)
            
        if score > 0:
            result.append({'score': score, 'url': record['url']})
    
    result.sort(key = lambda x: x['score'], reverse = True)
    return result[0 : min(10, len(result))]
    

if __name__ == '__main__':  
    root_url = 'https://en.wikipedia.org/wiki/Main_Page'
    crawl(root_url, 3)
    results = query('world')
    for result in results:
        print (str(result['score']) + ': ' + result['url'])

