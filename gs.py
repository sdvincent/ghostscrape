#! /usr/bin/env python

from bs4 import BeautifulSoup
import string
import urllib2
import random
import sqlite3 as lite
import sqlite3

def get_source(uri):
    """gets the source"""

    url = "https://ghostbin.com/paste/qecxy"
    try:
        response = urllib2.urlopen(url)
        source = response.read()
        response.close()
        return source
    except urllib2.HTTPError, e:
        return False
    except urllib2.URLError, e:
        return False
    except httplib.HTTPException, e:
        return False
    except Exception, e:
        return False
        

def parse(source):
    """Pulls out the paste"""

    soup = BeautifulSoup(source, "html5lib")
    soup.encode("utf8")
    uri = soup.find("title")
    uri = uri.encode("utf-8")
    uri = uri[7:-19] 
    #print uri
    title =  soup.find('div', {'class': 'modal-body'}).get_text().strip()
    newline = title.index('\n')
    title = title[38:newline-1]
    paste = soup.find('div', {'id': 'code'}).get_text().strip()

    return title, paste

def archive(url, paste, interesting):
    """Will store all links and if it is 'interesting' then it will store the paste"""
   
    
    database = "ghostdb.db"

    if interesting == True:
        interesting = 1
    else:
        interesting = 0

    con = lite.connect(database)
  
    cur = con.cursor()

    cur.execute(
             'CREATE TABLE IF NOT EXISTS ghostbin( date_added TEXT, link TEXT PRIMARY KEY NOT NULL, scraped BOOLEAN NOT NULL, interesting BOOLEAN NOT NULL, paste TEXT)')
    
    scraped = 1

    
    # Insert the link into the database
    cur.execute(
        "INSERT INTO ghostbin(link,scraped,interesting) VALUES( ?, ?, ? );", (url, scraped, interesting))
    cur.execute(
        "UPDATE ghostbin SET date_added = date('now') WHERE link == (?);", (url,))

    if interesting == True:
        cur.execute(
            "UPDATE ghostbin SET paste = (?) WHERE link == (?);", (paste, url))
        
    con.commit()

    if con:
        con.close()

    print url + " has been added to the database."


def checkdups(link):
    """Opens the database quick and checks if the link exists already of not."""

    database = "ghostdb.db"
    try:
        con = lite.connect(database)
        
        cur = con.cursor()

        cur.execute("SELECT date_added FROM ghostbin WHERE link = ?", (link,))
        data=cur.fetchone()

        if data == None:
            print "New link"
            return False
        else:
            return True
    
    finally:
        if con:
            cur.close()

def genUri():
    """Generates a random uri 5 characters long consisting of numbers and letters"""

    uri =  ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(5))
    link = "https://ghostbin.com/paste/" + uri
    return link

def main():
    """Main function"""
    print "hello world"

    #Generate a link
    link = genUri()
    link = "https://ghostbin.com/paste/qecxy"
    print link
    
    #Check if it was already used
    dup = checkdups(link)
    if dup == True:
        print "Duplicate found, skipping"
        #continue
        exit()
   
    #Get the source code
    source = get_source(link)
    if source == False: #This means the link was bad
        print "nope. Must be blocked. :/"
        #continue 
        exit()
    #print source
   
    #Get the paste
    title, paste = parse(source)

    print paste

    #Find good shit
    #have to create this yet
    

    #Archive the link so we don't use it again
    interesting = False
    archive(link, paste, interesting)

    print "end :)"


if __name__ == '__main__':
    main()
