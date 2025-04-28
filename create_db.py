#!/usr/bin/env python
# coding: utf-8

# In[15]:


# create_db.py
import sqlite3

def create_db():
    # This will create hw13.db (or overwrite it)
    conn = sqlite3.connect('hw13.db')
    # Read your schema + initial data from schema.sql
    with open('schema.sql', 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.close()
    print("hw13.db created successfully!")

if __name__ == '__main__':
    create_db()

