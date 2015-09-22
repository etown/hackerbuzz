import urllib2
import json
import datetime
import time
import pytz
import psycopg2
import pandas as pd
from pandas import DataFrame

params = {
  'database': '',
  'user': 'postgres',
  'password': os.environ['DBPASSWORD'],
  'host': os.environ['DBHOST'],
  'port': 5432
}


ts = str(int(time.time()))
df = DataFrame()
hitsPerPage = 1000
requested_keys = ["title","url","points","num_comments","author","created_at_i","objectID"]

i = 0

while True :
	try:
		url = 'https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=%s&numericFilters=created_at_i<%s' % (hitsPerPage, ts)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		data = json.loads(response.read())
		last = data["nbHits"] < hitsPerPage
		data = DataFrame(data["hits"])[requested_keys]
		df = df.append(data,ignore_index=True)
		ts = data.created_at_i.min()
		print i * 1000
		if (last):
			break
		time.sleep(3.6)
		i += 1

	except Exception, e:
		print e
df["created_at"] = df["created_at_i"].map(lambda x: datetime.datetime.fromtimestamp(int(x), tz=pytz.timezone('America/New_York')).strftime('%Y-%m-%d %H:%M:%S'))
try:
    conn = psycopg2.connect(**params)
except:
    print "I am unable to connect to the database."

cur = conn.cursor()
for index, row in df.iterrows():

	try:
	    cur.execute('INSERT INTO items ("id", "title", "url", "points", "num_comments", "author", "created_at") VALUES(%s, %s, %s, %s, %s, %s, %s);',(row['objectID'],row['title'],row['url'],row['points'],row['num_comments'],row['author'],row['created_at']))
	except Exception as e:
	    print e
conn.commit()