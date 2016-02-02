#! /usr/bin/env python

from bs4 import BeautifulSoup
import string
import time
import urllib2
import random
import sqlite3 as lite
import sqlite3

def get_source(url):
    """gets the source"""

    try:
        response = urllib2.urlopen(url)
        source = response.read()
        response.close()
        return source
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

def archive(link):
    """Will store all links and if it is 'interesting' then it will store the paste"""
   
    database = "ghostdb.db"

    con = lite.connect(database)
  
    cur = con.cursor()

    cur.execute(
             'CREATE TABLE IF NOT EXISTS ghostbin( date_added TEXT, link TEXT PRIMARY KEY NOT NULL, interesting BOOLEAN NOT NULL, paste TEXT)')
    
    interesting = 0

    # Insert the link into the database
    cur.execute(
        "INSERT INTO ghostbin(link, interesting) VALUES( ?, ?);", (link, interesting))
    cur.execute(
        "UPDATE ghostbin SET date_added = date('now') WHERE link == (?);", (link,))

    con.commit()

    if con:
        con.close()

    print link + " has been added to the database."


def checkdups(link):
    """Opens the database quick and checks if the link exists already of not."""

    database = "ghostdb.db"
    try:
        con = lite.connect(database)
        
        cur = con.cursor()

        cur.execute(
             'CREATE TABLE IF NOT EXISTS ghostbin( date_added TEXT, link TEXT PRIMARY KEY NOT NULL, interesting BOOLEAN NOT NULL, paste TEXT)')
   
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

def addPaste(link, paste):
    database = "ghostdb.db"
    try:
        con = lite.connect(database)
        
        cur = con.cursor()

        cur.execute(
                "UPDATE ghostbin SET paste = (?)  WHERE link == (?);", (paste, link))

        cur.execute(
                "UPDATE ghostbin SET interesting = 1 WHERE link == (?);", (link,))
        
        con.commit()

    except Exception, e:
        "Could not ipdate the db"

    finally:
        if con:
            con.close()

    print "paste added"

def main():
    """Main function"""

    while True:
        #Generate a link
        link = genUri()
        #link = "https://ghostbin.com/paste/qecxy"
        #print link
        
        #Check if it was already used
        dup = checkdups(link)
        if dup == True:
            print "Duplicate found, skipping"
            continue
            #exit()
        else:
            archive(link)
       
        #Get the source code
        source = get_source(link)
        if source == False: #This means the link was bad
            time.sleep(10)
            continue 
            #exit()
        #print source
   
        #Get the paste
        title, paste = parse(source)

        addPaste(link, paste)
        #Find good shit
        #have to create this yet
        time.sleep(10)

    print "end :)"


if __name__ == '__main__':
    main()
