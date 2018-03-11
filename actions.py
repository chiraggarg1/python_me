import os
import os.path
from gtts import gTTS
import commands
from playsound import playsound
import pygame
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import Translator
import json
import pafy

import subprocess
google_cloud_api_key='AIzaSyCXC9VTL3Gwxk6rdD4EH3Fu6hlPSJ7dxQ4'
DEVELOPER_KEY=google_cloud_api_key
YOUTUBE_API_SERVICE_NAME='youtube'
YOUTUBE_API_VERSION='v3'
translator=Translator()
language='en'
ttsfilename="/tmp/say.mp3"

def say(words):
	words= translator.translate(words, dest=language)
	words=words.text
	words=words.replace("Text, ",'',1)
	words=words.strip()
	print(words)
	tts = gTTS(text=words, lang=language)
	tts.save(ttsfilename)
	os.system("mpg123 "+ttsfilename)
	os.remove(ttsfilename)

def YouTube_No_Autoplay(phrase):
    urllist=[]
    idx=phrase.find('stream')
    track=phrase[idx:]
    track=track.replace("'}", "",1)
    track = track.replace('stream','',1)
    track=track.strip()
    say("Getting youtube link")
    fullurl,urlid=youtube_search(track)
    urllist.append(fullurl)
    print(urllist)
    with open('/home/chirag/Desktop/snehil/youtubeurllist.json', 'w') as output_file:
        json.dump(urllist, output_file)
    if os.path.isfile("/home/chirag/Desktop/snehil/.youtubeplayer.json"):
        os.remove('/home/chirag/Desktop/snehil/.youtubeplayer.json')
    youtubeplayer()
def youtube_search(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  req=query
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part='id,snippet'
  ).execute()

  videos = []
  channels = []
  playlists = []
  videoids = []
  channelids = []
  playlistids = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.

  for search_result in search_response.get('items', []):

    if search_result['id']['kind'] == 'youtube#video':
      videos.append('%s (%s)' % (search_result['snippet']['title'],
                                 search_result['id']['videoId']))
      videoids.append(search_result['id']['videoId'])

    elif search_result['id']['kind'] == 'youtube#channel':
      channels.append('%s (%s)' % (search_result['snippet']['title'],
                                   search_result['id']['channelId']))
      channelids.append(search_result['id']['channelId'])

    elif search_result['id']['kind'] == 'youtube#playlist':
      playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                    search_result['id']['playlistId']))
      playlistids.append(search_result['id']['playlistId'])

  #Results of YouTube search. If you wish to see the results, uncomment them
  # print 'Videos:\n', '\n'.join(videos), '\n'
  # print 'Channels:\n', '\n'.join(channels), '\n'
  # print 'Playlists:\n', '\n'.join(playlists), '\n'

  #Checks if your query is for a channel, playlist or a video and changes the URL accordingly
  if 'channel'.lower() in  str(req).lower() and len(channels)!=0:
      urlid=channelids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+channelids[0])
  elif 'playlist'.lower() in  str(req).lower() and len(playlists)!=0:
      urlid=playlistids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+playlistids[0])
  else:
      urlid=videoids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+videoids[0])

  return YouTubeURL,urlid

def youtubeplayer():

    if os.path.isfile("/home/chirag/Desktop/snehil/.youtubeplayer.json"):
        with open('/home/chirag/Desktop/snehil/.youtubeplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/chirag/Desktop/snehil/.youtubeplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/chirag/Desktop/snehil/.youtubeplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    if os.path.isfile("/home/chirag/Desktop/snehil/youtubeurllist.json"):
        with open('/home/chirag/Desktop/snehil/youtubeurllist.json','r') as input_file:
            tracks= json.load(input_file)
            numtracks=len(tracks)
            print(tracks)
    else:
        tracks=""
        numtracks=0

    startingvol=mpvvolmgr()

    if not tracks==[]:
        if currenttrackid<numtracks:
            audiostream,videostream=youtube_stream_link(tracks[currenttrackid])
            streamurl=videostream
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/chirag/Desktop/snehil/.youtubeplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            audiostream,videostream=youtube_stream_link(tracks[currenttrackid])
            streamurl=videostream
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")
def youtube_stream_link(videourl):
    url=videourl
    video = pafy.new(url)
    bestvideo = video.getbest()
    bestaudio = video.getbestaudio()
    audiostreaminglink=bestaudio.url
    videostreaminglink=bestvideo.url
    return audiostreaminglink,videostreaminglink
def mpvvolmgr():
    if os.path.isfile("/home/pi/.mediavolume.json"):
        with open('/home/pi/.mediavolume.json', 'r') as vol:
            oldvollevel = json.load(vol)
        print(oldvollevel)
        startvol=oldvollevel
    else:
        startvol=50
    return startvol



def Action(phrase):
	
	# if 'reboot' or 'restart' in phrase:
	# 	if 'laptop' or 'ubuntu' in phrase:
	# 		os.system('reboot')
	# if 'shutdown' or 'bandh' in phrase:
	# 	if 'laptop' or 'ubuntu' in phrase:
	# 		os.system('shutdown now')
	if 'chrome' in phrase:
		if 'open' or 'khol' in phrase:
			# os.system('xdotool key ctrl+shift+n')
			os.system('google-chrome')
	if 'install' in phrase:
		if 'python' in phrase:
			if 'package' in phrase:
				word = phrase.split()
				out2='pip install'+' '+word[-1]
				os.system(out2)
		else :
			word=phrase.split()
			out2='sudo apt-get install'+' '+word[-1]
			os.system('sudo apt-get update')
			os.system(out2)
	if 'mozilla' in phrase:
		if 'open' or 'khol' in phrase:
			#os.system('xdotool key ctrl+shift+n')
			os.system('firefox')
	if 'facebook' in phrase:
		if 'open' or 'khol' in phrase:
			os.system('python -m webbrowser "http://www.facebook.com/"')
	if 'website' in phrase:
		if 'open' in phrase:
			word=phrase.split()
			out2='python -m webbrowser"http://www.'+word[-1]+'.com/"'
			os.system(out2)
	if 'terminal' in phrase:
		if 'open' in phrase:
			os.system('xdotool key ctrl+shift+n')
	if 'file' in phrase:
		if 'open' in phrase:
			if 'titan' in phrase:
				word = phrase.split()
				ccmd='locate'+' '+word[-1]+'.py'
				out=commands.getoutput(ccmd)
				keylines=out.splitlines()
				i=0
				while 'Trash' in keylines[i]:
					i=i+1
				# a1='/'+word[-1]
				# ccmd2='cd'+' '+keylines[i].split(a1)[0].strip()
				os.system('gedit'+' '+keylines[i])
				# out2='subl'+' '+word[-1]+'.py'
				# os.system(out2)
				# os.system('cd ~')
			if 'text' in phrase:
				word = phrase.split()
				ccmd='locate'+' '+word[-1]+'.txt'
				out=commands.getoutput(ccmd)
				keylines=out.splitlines()
				i=0
				while 'Trash' in keylines[i]:
					i=i+1
				# a1='/'+word[-1]
				# ccmd2='cd'+' '+keylines[i].split(a1)[0].strip()
				# os.system(ccmd2)
				out2='gedit'+' '+keylines[i]
				os.system(out2)
				# os.system('cd ~')
	if 'music' in phrase:
		if 'play' in phrase:
			word=phrase.split()
			ccmd='locate'+' '+ word[-1]+'.mp3'
			out=commands.getoutput(ccmd)
			keylines=out.splitlines()
			out2 ='ffplay'+' '+keylines[0]
			os.system(out2)
	if 'video' in phrase:
		if 'play' in phrase:
			word =phrase.split()
			ccmd='locate'+' '+word[-1]
			out=commands.getoutput(ccmd)
			keylines=out.splitlines()
			subprocess.Popen(['vlc','-vvv','keylines[0]'])
	if 'image' in phrase:
		if 'show' in phrase:
			word=phrase.split()
			ccmd='locate'+' '+word[-1]
			out=commands.getoutput(ccmd)
			keylines=out.splitlines()
			out2='eog -f'+' '+keylines[0]
			os.system(out2)
	if 'youtube'in phrase:
		os.system('pkill mpv')
		if os.path.isfile("/home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py"):
			os.system('rm /home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py')
			os.system('echo "from actions import youtubeplayer\n\n" >> /home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py')
			os.system('echo "youtubeplayer()\n" >> /home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py')
			YouTube_No_Autoplay(phrase)
		else:
			os.system('echo "from actions import youtubeplayer\n\n" >> /home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py')
			os.system('echo "youtubeplayer()\n" >> /home/chirag/Desktop/snehil/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/grpc/trackchange.py')
			YouTube_No_Autoplay(phrase)
  if 'document' in phrase:
    if 'open' in phrase:
      word=phrase.split()
      ccmd='loacte'+' '+word[-1]+'.docx'
      out=commands.getoutput(ccmd)
      keylines=out.splitlines()
      out2='xdg-open'+' '+keylines[0]
      os.system(out2)
  if 'text' in phrase:
    if 'document' in phrase:
      if 'open' in phrase:
        if 'new' in phrase:
          out2='libreoffice'+' '+'--writer'
          os.system(out2)
  if 'spreadsheet' in phrase:
    if 'open' in phrase:
      if 'new' in phrase:
        out2='libreoffice'+' '+'--calc'
        os.system(out2)
  if 'drawing' in phrase:
    if 'open' in phrase:
      if 'new' in phrase:
        out2='libreoffice'+' '+'--draw'
  if 'presentation' in phrase:
    if 'open' in phrase:
      if 'new' in phrase:
        out2='libreoffice'+' '+'--impress'
  if 





	




