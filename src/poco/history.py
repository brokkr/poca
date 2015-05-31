# Copyright 2010, 2011 Mads Michelsen (madchine@gmail.com)
# 
# This file is part of Poca.
# Poca is free software: you can redistribute it and/or modify it under the terms \
# of the GNU General Public License as published by the Free Software Foundation, \
# either version 3 of the License, or (at your option) any later version.


from multiprocessing import Process, Queue
from pysqlite2 import dbapi2 as sqlite


def librarian(paths_dic, q):
    '''subprocess dealing with the database'''
    connection = sqlite.connect(paths_dic['history_log'])
    cursor = connection.cursor()
    create_tables(cursor)
    while True:
        catch = q.get()
        if catch == 'quit':
            connection.close()
            break
        print catch
        sub_dic, entry_dic = catch
        query = '''INSERT INTO entries (title url pubdate length filename sub active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)'''
        data = (entry_dic['title'], entry_dic['url'], entry_dic['pubdate'], \
        entry_dic['length'], entry_dic['filename'], sub_dic['title'], 1)
        cursor.execute(query, data)
        connection.commit()


# cursor.execute("insert into subs (title, url, max_mb, artist, album, genre) values ('newshour', 'http://downloads.bbc.co.uk/podcasts/worldservice/newshour/rss.xml', 60, 'BBC', 'Newshour', 'podcast')")


def create_librarian(paths_dic):
    '''Creates a sub-process with a standard FIFO queue'''
    q = Queue()
    p = Process(target=librarian, args=(paths_dic, q,))
    p.start()
    return (p, q)
    
def stuff_it(q, it):
    q.put(it)

def end_it(p, q):
    q.put('quit')
    p.join()

def create_tables(cursor):
    try:
        cursor.execute('CREATE TABLE global (version NUMBER(1,1))')
    except sqlite.OperationalError:
        print 'no global table :('
        pass
    try:
        cursor.execute('''CREATE TABLE subs 
        (title VARCHAR(100), url VARCHAR(300), max_mb NUMBER(5), last_update DATE)''')
    except sqlite.OperationalError:
        print 'no subs table :('
        pass
    try:
        cursor.execute('''CREATE TABLE entries 
        (title VARCHAR(100), url VARCHAR(300), pubdate DATE, filename VARCHAR(100), 
        length NUMBER(12), sub VARCHAR(100), active NUMBER(1))''')
    except sqlite.OperationalError:
        print 'no entries table :('
        pass

def add_entry(q, sub_dic, entry_dic):
    q.put((sub_dic, entry_dic))
    
