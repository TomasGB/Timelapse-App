import os
import shutil
from cv2 import cv2
import datetime
import time
import glob
import imageProcessing

def ConvertToVideo(result,imgs_direc):
        list_imgs = glob.glob(f"{imgs_direc}/*.jpg")
        imgs_ordered = sorted(list_imgs, key=os.path.getmtime)

        for file in imgs_ordered:
            image_frame = cv2.imread(file)
            print('processing photos...')
            result.write(image_frame)

def createTimelapse(durationG,photosInterval,Resolution,procPhotosKeep,device):
    if Resolution == '720':
        width = 1280
        height = 720
    elif Resolution == '1080':
        width = 1920
        height = 1080
    elif Resolution == '2k':
        width = 2560
        height = 1440
    elif Resolution == '4k':
        width = 3840
        height = 2160
    else:
        Resolution == '480'
        width = 640
        height = 480

    video = cv2.VideoCapture(device, cv2.CAP_DSHOW) 
    video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if (video.isOpened() == False):  
        print("Error reading video file")
        return quit


    frame_width = int(video.get(3)) 
    frame_height = int(video.get(4)) 
    size = (frame_width, frame_height)
    print(size)

    actualTime=datetime.datetime.now()

    file_name = str(datetime.date.today())+'_'+f'{actualTime.hour}hs{actualTime.minute}min{actualTime.second}sec'

    os.mkdir(file_name)

    #cv2.VideoWriter('filename',  cv2.VideoWriter_fourcc(*'Codec'), fps, resolution)
    #0x7634706d codec code for mp4 format

    result = cv2.VideoWriter(f'{file_name}/timelapse.mp4', 0x7634706d , 24.97, size)
    resultCorr = cv2.VideoWriter(f'{file_name}/timelapse_processed.mp4',  0x7634706d, 24.97, size)

    #Timelapse parameters config
    procPhotosKeep = procPhotosKeep.lower()
    delete_imgs = False

    if procPhotosKeep == 'y' : 
        delete_processed_imgs = False 
    elif procPhotosKeep == 'n' :
        delete_processed_imgs = True
    else:
        print('There was an error')

    duration = durationG * 60

    imgs_direc = f'{file_name}/timelapse_imgs'
    if not os.path.exists(imgs_direc):
        os.mkdir(imgs_direc)

    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=duration)

    i = 0

    #takes the photos in the specified duration
    while datetime.datetime.now() < end:
        ret, frame = video.read()
        print('Time left:',end-datetime.datetime.now())
        filename = f"{imgs_direc}/{i}.jpg"
        i+=1
        cv2.imwrite(filename, frame)
        time.sleep(photosInterval)
        if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

    processed_imgs =f'{file_name}/hsv_imgs'
    eq_direc=f'{file_name}/eq_imgs'

    #Exports the timelapse without processing
    ConvertToVideo(result,imgs_direc)

    #timelapse processing
    imageProcessing.gamma_correct(imgs_direc,processed_imgs)
    imageProcessing.Histogram_EQ(processed_imgs,eq_direc)

    #Exports the timelapse with processing
    ConvertToVideo(resultCorr,eq_direc)

    if delete_processed_imgs:
        shutil.rmtree(eq_direc)

    video.release() 
    result.release()
    resultCorr.release() 
    print("The Timelapse it's finished.")
