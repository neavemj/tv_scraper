#!/usr/bin/env python

## script to check what movies are on in KAUST
# Matthew J. Neave & Carolin Neave 5.6.15

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

output = open("tv_schedule.pl", "w")

# get http from websites for scedudule

mbc_max = requests.get("http://www.mbc.net/en/mbc-max.html")
mbc_2 = requests.get("http://www.mbc.net/en/mbc2.html")
mbc_action = requests.get("http://www.mbc.net/en/mbc-action.html")
fox = requests.get("http://www.foxmoviestv.com/english/schedule/weekly")
dubai = requests.get("http://www.dcn.ae/dubaione/Schedule.asp")
zdf = requests.get("http://www.zdf.de/epg/programm-4100.html?action=filter&senderToFilter=allWithoutRadio&datum=Mo&woche=diese&ansicht=horizontal&showAllSenders=false")


# parser for mbc channels - they're all the same format

def get_mbc_movies(channel):
    channel_bs = BeautifulSoup(channel.text)
    title_list = []
    time_list = []
    blurb_list = []
    for movie in channel_bs.select('div.archttl'):
        if len(movie.select('h3')) > 0:     # some of these classes are empty       
            title_list.append(movie.select('h3')[0].get_text().replace(" ", "_").replace("'", ""))
            time_list.append(movie.select('li')[2].get_text().strip())
            try:                            # some movies don't have a summary / blurb
                blurb_list.append(movie.select('p')[0].get_text().strip())
            except:
                blurb_list.append("none found")
    movie_list = zip(title_list, time_list, blurb_list)
    return movie_list
    
mbc_max_schedule = get_mbc_movies(mbc_max)
mbc_2_schedule = get_mbc_movies(mbc_2)
mbc_action_scedule = get_mbc_movies(mbc_action)


# parser for fox movies channel

def get_fox_movies(channel):
    channel_bs = BeautifulSoup(channel.text)
    title_list = []
    time_list = []
    blurb_list = []
    for movie in channel_bs.findAll('div', {'class': 'pop_right_social'}):         
        movie_parts = str(movie.select('a')[0]).split("'")
        title = movie_parts[3].replace(" ", "_").replace("'", "")
        if title not in title_list:
            title_list.append(title)
            time_list.append(movie_parts[5].strip())
            blurb_list.append(movie_parts[7].strip())       
    movie_list = zip(title_list, time_list, blurb_list)
    return movie_list

fox_schedule = get_fox_movies(fox)


# parser for german zdf channel

def get_zdf_movies(channel):
    channel_bs = BeautifulSoup(channel.text)
    title_list = []
    time_list = []
    blurb_list = []
    # 'broadcasts zdf_neo clearfix'
    zdf_broadcasts = channel_bs.findAll('ul', {'class': ['broadcasts zdf clearfix', 'broadcasts zdf_neo clearfix']})
    print zdf_broadcasts
    for movie in zdf_broadcasts[0].select('a'):
        if len(movie.select('h3')) > 0:
            title_list.append(movie.select('h3')[0].get_text().replace(" ", "_").replace("'", ""))
            time_list.append(movie.findAll('div', {'class', 'col_l'})[0].get_text())
            try:
                blurb_list.append(movie.select('h5')[0].get_text())
            except:
                blurb_list.append("none found")             
    movie_list = zip(title_list, time_list, blurb_list)
    return movie_list
    
#zdf_schedule = get_zdf_movies(zdf)


# parser for dubai one channel

def get_dubai_movies(channel):
    channel_bs = BeautifulSoup(channel.text)
    title_list = []
    time_list = []
    blurb_list = []
    dubai_broadcasts = channel_bs.findAll('tr', {'class': ['bg3', 'bg5']})
    
    for movie in dubai_broadcasts:
        if len(movie.select('h3')) > 0:
            title_list.append(movie.select('h3')[0].get_text().strip().replace(" ", "_").replace("'", ""))
            time_list.append(movie.findAll('span', {'class', 'bold1'})[0].get_text().strip())
            try:
                blurb_list.append(movie.select('td')[3].get_text().split("\n")[6].strip())
            except:
                blurb_list.append("none found")
                
    movie_list = zip(title_list, time_list, blurb_list)
    return movie_list
    
dubai_schedule = get_dubai_movies(dubai)


# print off schedule nicely

#channels = {'mbc_max: 106' : mbc_max_schedule, 'mbc_2: 105' :  mbc_2_schedule, 
#'mbc_action: 129' : mbc_action_scedule, 'fox_movies: 102': fox_schedule, 
#'zdf: 62': zdf_schedule, 'dubai_one: 103': dubai_schedule}

#channels = [('zdf: 62', zdf_schedule), 
channels = [('fox_movies: 102', fox_schedule), 
('dubai_one: 103', dubai_schedule), ('mbc_2: 105',  mbc_2_schedule), 
('mbc_max: 106', mbc_max_schedule), ('mbc_action: 129', mbc_action_scedule)]


for channel in channels:
    output.write('"' * 50 + "\n")
    shows_printed = 0
    started = False                 # this boolean becomes true once current time is reached
    for show in channel[1]:
        time_now = datetime.strptime(str((datetime.now()
        - timedelta(minutes=60)).time())[:5], "%H:%M")      # minus off 60 minutes to see what shows have already started         
  
        if channel[0] == 'fox_movies: 102':              # fox has a weird time format
            output.write(channel[0] + "\n@ " + "\n# ".join(show).encode('utf-8') + "\n\n")
            break      
        if channel[0] == 'zdf: 62':                      # take off an hour for German time
            show_time = datetime.strptime(show[1][:5], "%H:%M") - timedelta(hours=1)
        if channel[0] == 'dubai_one: 103':               # plus an hour for Dubai time
            show_time = datetime.strptime(show[1][:5], "%H:%M") + timedelta(hours=1)  
        else:
            show_time = datetime.strptime(show[1][:5], "%H:%M")

        if show_time > time_now and shows_printed < 3:
            started = True
            shows_printed += 1           
            output.write(channel[0] + "\n@ " + "\n# ".join(show).encode('utf-8') + "\n\n")
        if started:
            shows_printed += 1