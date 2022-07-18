from googleapiclient.discovery import build
from matplotlib import pyplot as plt
import googleapiclient.errors
from numpy import dtype
import pandas as pd
import seaborn as sns

api_key = 'AIzaSyAQQlmJxtg7FHEPu6l8XgkVl812PLj9uiw'

channels_id = [
    'UCHnyfMqiRRG1u-2MsSQLbXA', #veritasium
    'UC6nSFpj9HTCZ5t-N3Rm3-HA', #vsouse
    'UCsooa4yRKGN_zEE8iknghZA', #ted-ed
    'UCX6b17PVsYBQ0ip5gyeme-Q', #CrashCourse
    'UCIkgmKjE5Q9qZEDnfrwoaXw', #CGP Grey
    'UCC552Sd-3nyi_tk2BudLUzA', #AsapSCIENCE
    'UC4a-Gbdw7vOaccHmFo40b9g', # Khan Academy
    'UCvQECJukTDE2i6aCoMnS-Vg' #Big think 
    ]

youtube = build('youtube', 'v3', developerKey=api_key)

def info_api(youtube,channels_id):
    '''get information about youtube channels and transform it into dictionary and list'''
    request = youtube.channels().list(
        part = 'snippet, contentDetails, statistics',
        id = ','.join(channels_id))
    response =  request.execute()
    all_data = [{'channel_name': response ['items'][i]['snippet']['title'], 
                'subscribers': response ['items'][i]['statistics']['subscriberCount'], 
                'views': response ['items'][i]['statistics']['viewCount'],
                'total': response ['items'][i]['statistics']['videoCount'],
                'playlist_id': response ['items'][i]['contentDetails']['relatedPlaylists']['uploads']}
                for i in range(len(response['items']))]
    return all_data

info_edu_chanel = info_api(youtube, channels_id)

# Work with pandas

pandas_info = pd.DataFrame(info_edu_chanel)                 
pandas_info['subscribers'] = pd.to_numeric(pandas_info['subscribers'])
pandas_info['views'] = pd.to_numeric(pandas_info['views'])
pandas_info['total'] = pd.to_numeric(pandas_info['total'])

#dataviz

sns.set(rc={'figure.figsize':(12, 10)}, palette="colorblind")
total_videos = sns.barplot(x='channel_name', y = 'total', data = pandas_info)
plt.show()

sns.set(rc={'figure.figsize':(12, 10)}, palette="bright")
total_subscribers = sns.barplot(x='channel_name', y = 'subscribers', data = pandas_info)
plt.show() #for VS code

#analysis of videos from some channel

playlist_id = pandas_info.loc[pandas_info['channel_name'] == 'Veritasium','playlist_id'].iloc[0]

def video_id(youtube,playlist_id):
    '''get ids of all videos on the channel'''

    request = youtube.playlistItems().list(
        part = 'contentDetails',
        playlistId = playlist_id,
        maxResults = 50)
    response = request.execute()

    video_ids =  [response['items'][i]['contentDetails']['videoId'] for i in range(len(response['items']))]

    next_page = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page is None:
            more_pages = False
        else: 
            request = youtube.playlistItems().list(
                part = 'contentDetails',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken = next_page)
            response = request.execute()
            video_ids =  [response['items'][i]['contentDetails']['videoId'] for i in range(len(response['items']))]

            next_page = response.get('nextPageToken')

    return video_ids

#statistics of each video on the channel

video_ids = video_id(youtube,playlist_id)

def get_video_details(youtube,video_ids):
    '''get information about likes, comments and views from certain video'''
    for i in range(0, len(video_ids), 25):
        request = youtube.videos().list(
            part = 'snippet, statistics',
            id = ','.join(video_ids[i:i+25]))
        response = request.execute()
        all_video_stats = [{'Title':video['snippet']['title'],
                            'Published_date': video['snippet']['publishedAt'],
                            'Views':video['statistics']['viewCount'],
                            'Likes': video['statistics']['likeCount'],
                            'Comments': video['statistics']['commentCount']}
                            for video in response['items']]
    return all_video_stats 

video_details = get_video_details(youtube,video_ids)

# work with pandas

video_data = pd.DataFrame(video_details)

video_data['Published_date'] = pd.to_datetime(video_data['Published_date'])
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])

top10_videos = video_data.sort_values(by = 'Views', ascending = False).head(10)

#dataviz

sns.set(rc={'figure.figsize':(15, 10)}, palette="pastel")
tpo10_viz = sns.barplot(x= 'Views', y= 'Title', data  = top10_videos)
plt.subplots_adjust(left = 0.295)
plt.show()