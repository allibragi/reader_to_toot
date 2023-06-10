from datetime import datetime
import requests
from bs4 import BeautifulSoup
from mastodon import Mastodon

# variables
WF_URL = "https://writefreely.istance/read" # writefreely istance reader address
MST_URL = "https://mastondon.istance" # mastodon istance address
MST_TOKEN = "<token>" # mastodon app token
LR_PATH = "/path/last_run.txt" # file that store the last run

# save current execution datetime
new_date = datetime.now()
dt_string = new_date.strftime("%d/%m/%Y %H:%M:%S")

# read last execution datetime
f = open(LR_PATH)
last_date_str = f.readline()
last_date = datetime.strptime(last_date_str.strip(), "%d/%m/%Y %H:%M:%S")

# get the reader page
page = requests.get(WF_URL)
# get the "wrapper" section (where the article previews are)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="wrapper")
# get the list of the single posts
articles = results.find_all("article")

# initialize toot list
toot_list = []
index_toot = 0 # to handle the character limit
toot_list.append("📣 NEW POST 📣") #initialize the first toot with the "header"
new_posts = 0

for art in articles:
    # get the post title
    title_element = art.find("h2", class_="p-name") # title of the post
    body_element = art.find("div", class_="e-content preview").find("p").text[:50] # if the post doesn't have a title take the first 50 char of the body
    if title_element is None: 
        post_title = body_element.strip()
    else:
        post_title = title_element.find("a").text.strip()
    # get publish datetime
    publish_date_tmp = art.find("time", class_="dt-published")  
    publish_date = datetime.strptime(publish_date_tmp.get("content")[:19], "%Y-%m-%d %H:%M:%S")
    # get hautor
    author = art.find("p", class_="source").text.strip()[5:]
    # create the toot list
    # if the publish date is > the last script execution include the post in the toot
    if publish_date > last_date:
         if new_posts == 0:
             new_posts = 1
         new_text = '- ' + post_title + ' (' + author +')'
         temp_toot = toot_list[index_toot]+'\n'+new_text
         if index_toot == 0 and len(temp_toot) > 470: #for the first toot leave some space for the wf link
            toot_list[index_toot] = toot_list[index_toot]+'\n\n' + WF_URL
            toot_list.append(new_text)
            index_toot = index_toot+1
         elif len(temp_toot) > 499:
            toot_list.append(new_text)
            index_toot = index_toot+1
         else:
            toot_list[index_toot] = toot_list[index_toot]+'\n'+new_text

# if there's only one toot add the wf link
if len(toot_list) == 1:
    toot_list[0] = toot_list[0]+'\n\n' + WF_URL

# send te toots
if new_posts == 1:
    m = Mastodon(access_token=MST_TOKEN, api_base_url=MST_URL)
    reply_to = None
    for toot in toot_list:
        if reply_to is None:
            reply_to = m.status_post (toot )
        else: #if isn't the firs toot it's a reply to the previous and the visibility is unlisted to keep the feed clean
            reply_to = m.status_post (toot, visibility='unlisted', in_reply_to_id= reply_to.id)

# write the execution datetime for the next run
f = open(LR_PATH, "w")
f.write(dt_string)