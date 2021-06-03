import requests, os
from pytube import YouTube as youtube
import cv2 as cv
import glob
from PIL import Image # i dont think the try..catch is necessary but we'll see
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
videolist = {} # dict of names of videos to find frames. video names are the shortened youtube ids
pid = "PLRD7N-Zrj2DMOLTG7t9E-vJo35BzeTwVG"
key = "AIzaSyD-sdVOrxbI2Rhoy3gAsieTadYI_sgh6KM" # this is an issue
fpt = 0 # first page token

jpglist = glob.glob("./*.jpg")
mp4list = glob.glob("./*.mp4")
for filePath in jpglist:
    try:
        os.remove(filePath)
    except:
        print("couldnt remove %s" % filePath)

for filePath in mp4list:
    try:
        os.remove(filePath)
    except:
        print("couldnt remove %s" % filePath)

def getPlaylistItems(npt=None):
    global fpt
    if npt == fpt: # next page token is first one, we're done!!
        print("finished!")
    load = {
        "key": key,
        "playlistId": pid,
        "part": "id,snippet",
        "maxResults": 50,
        "pageToken": npt
    }
    result = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params=load)
    json = result.json()
    for i in json["items"]:
        id = i["snippet"]["resourceId"]["videoId"]
        thumb = i["snippet"]["thumbnails"]["default"]["url"] # omg dicts are so disgusting
        title = i["snippet"]["title"].replace("Moist Meter | ", "")
        video = youtube("https://youtu.be/%s" % id)
        video = video.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first().download() # get highest res mp4
        os.rename(video, "%s.mp4"%id)

        vidcap = cv.VideoCapture("%s.mp4"%id) # can i use the actual video from video here? or does it have to be a filename smh
        success,image = vidcap.read()
        count = 0
        fps = 24 # i dont know the fps but 24 is reasonable
        increment_seconds = 3

        # ok so i figured out why its not working -- im stupid and need to process the image beforehand so its not looking at colors
        # https://stackoverflow.com/questions/59124487/how-to-extract-text-or-numbers-from-images-using-python

        while success: # stolen code lol
            if count % (fps * increment_seconds) == 0:
                cv.imwrite("frame%d.jpg" % count, image)
                print(pytesseract.image_to_string(Image.open("frame%d.jpg"%count), config="--psm 13"))
            success,image = vidcap.read()
            count += 1
        framelist = glob.glob("./*.jpg") # clear em all when we're done
        for frame in framelist:
            try:
                os.remove(frame)
            except:
                print("couldnt remove frame %s" % frame)
        videolist[id] = {
            "thumb": thumb,
            "title": title,
            "id": id
        }
    if "nextPageToken" in json:
        getPlaylistItems(npt=json["nextPageToken"])


getPlaylistItems()