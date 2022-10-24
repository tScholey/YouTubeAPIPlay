
api_key = ""

from apiclient.discovery import build
import re
import markovify

youtube = build('youtube','v3', developerKey=api_key)

def get_channel_videos(channel_name,isUsername=True):

    #get id for 'uploads' playlist:
    if isUsername is False:
        res = youtube.channels().list(id = channel_name,
                                  part = 'contentDetails').execute()
    else:
        res = youtube.channels().list(forUsername = channel_name,
                                  part = 'contentDetails').execute()

    #format of result:
    #res = { kinds, etag, pageInfo, items  }
    #       items = [ {kind, etag, id, contentDetails} ]
    #           contentDetails = { relatedPlaylists }
    #               relatedPlaylists = { uploads, watchHistory, watchLater }
    
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = [ ]
    next_page_token = None

    while True:
                res = youtube.playlistItems().list(playlistId = playlist_id,
                                           part = 'snippet',
                                           maxResults = 50,
                                           pageToken = next_page_token).execute()

        #format:
        #res = { kind, etag, nextPageToken, pageInfo, items }
        #       pageInfo = { totalResults, resultsPerPage }
        #       items = [ { kind, etag, id, snippet } ]
        #           snippet = { publishedAt,
        #                       channelId,
        #                       title,
        #                       description,
        #                       thumbnails,
        #                       channelTitle,
        #                       playlistId,
        #                       position,
        #                       resourceId}
        #               thumbnails = {  default,
        #                               medium,
        #                               high,
        #                               standard,
        #                               maxres}
        #                   ...  = {        url,
        #                                   width,
        #                                   height}
        #               resourceId = {  kind,
        #                               videoId}
        
        #add wanted info (title, description, date, url) to videos list,
        # removing character incompatible with csv (that I've found),
        # and truncating long descriptions
        
        def cleanup(text):
            return re.sub('[♪♫►♥●♦ﾉヽ༼ຈل͜ຈ༽◄☼]','',text)
        
        for item in res['items']:
            videos.append(cleanup(item['snippet']['title']))
        next_page_token = res.get('nextPageToken')


        if next_page_token is None:
            break
    return videos


def listToMarkIn(listIn):
    out = ""
    for i in listIn:
        out += (i + "\n")
    return out

def getAvLen(listIn):
    ovLen = 0
    for i in listIn:
        ovLen += len(i)
    return int(ovLen/len(listIn))

def titleGen(channelName, repeat=1, isUsername = True, senLen = 0):
    channelTitles = get_channel_videos(channelName, isUsername)
    markIn = listToMarkIn(channelTitles)
    text_model = markovify.NewlineText(markIn)
    markTitle = text_model.make_sentence()
    titles = []
    if senLen != 0:
        while len(titles) < repeat:
            markTitle = text_model.make_short_sentence(senLen)
            if type(markTitle) != str:
                markTitle = text_model.make_short_sentence(senLen)
            else:
                titles.append(markTitle)
                markTitle = text_model.make_short_sentence(senLen)
        for i in range(repeat):
            print(str(i+1) + ". " + titles[i])
    else:
        while len(titles) < repeat:
            if type(markTitle) != str:
                markTitle = text_model.make_sentence()
            else:
                titles.append(markTitle)
                markTitle = text_model.make_sentence()
        for i in range(repeat):
            print(str(i+1) + ". " + titles[i])
    return titles
