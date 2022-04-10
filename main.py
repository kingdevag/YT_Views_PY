from time import sleep
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

import logging

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', config.YOUTUBE_READ_WRITE_SCOPE)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, config.YOUTUBE_READ_WRITE_SCOPE)
        creds = flow.run_console(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
youtube = googleapiclient.discovery.build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION, credentials=creds)

def getVideoInfo(videoID):
    video = youtube.videos().list(id=config.VIDEO_ID, part="snippet,statistics").execute()
    return video["items"][0]

def createThumbnail(views):
    image = Image.open(config.BLANK_THUMBNAIL_FILENAME)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(config.FONT_VIEWS, config.FONT_VIEWS_SIZE)
    fontVideo = ImageFont.truetype(config.FONT_TEXTS, config.FONT_TEXTS_SIZE)

    imageWidth, imageHeigth = (1366,768)
        
    widthTextUpper, heightTextUpper = draw.textsize(config.VIDEO_UPPER_TEXT, font=fontVideo)
    widthTextViews, heightTextViews = draw.textsize(views, font=font)
    widthTextBottom, heightTextBottom = draw.textsize(config.VIDEO_BOTTOM_TEXT, font=fontVideo)
        
    draw.text(((imageWidth-widthTextUpper)/2,(imageHeigth-heightTextUpper)/2-210),config.VIDEO_UPPER_TEXT,(0,0,0),font=fontVideo)
    draw.text(((imageWidth-widthTextViews)/2,(imageHeigth-heightTextViews-107)/2),views,(255,0,0),font=font) #107 = 400(font size) *32(text without baseline bigger than size 120) / 120
    draw.text(((imageWidth-widthTextBottom)/2,(imageHeigth-heightTextBottom)/2+220),config.VIDEO_BOTTOM_TEXT,(0,0,0),font=fontVideo)
        
    image.save(config.FINAL_THUMBNAIL_FILENAME)

while True:
    videoInfo = getVideoInfo(config.VIDEO_ID)
    newVideoTitle = config.VIDEO_TITLE.format(views=videoInfo["statistics"]["viewCount"])
    if newVideoTitle == videoInfo["snippet"]["title"]:
        sleep(config.TIME_PER_UPDATE)
        continue

    youtube.videos().update(
        part="snippet",
        body={
          "id": config.VIDEO_ID,
          "snippet": {
            "title": newVideoTitle,
            "categoryId":videoInfo["snippet"]["categoryId"]
          }
        }
    ).execute()

    createThumbnail(videoInfo["statistics"]["viewCount"])

    youtube.thumbnails().set(
        videoId=config.VIDEO_ID,
        media_body=config.FINAL_THUMBNAIL_FILENAME
    ).execute()
    logger.info(f'UPDATE WITH {videoInfo["statistics"]["viewCount"]}: {newVideoTitle}')