import os
import Vid_manage_test
import Violet

#video to frames
def video_to_frames(vid):
    print("Converting file (" + str(vid) + ") to frames...")

    # this so far only extracts the frames and converts them into annex B
    # it cannot, as of now, manage the video stream and extract frames 
    Vid_manage_test.read_file(vid)

def encrypt(key, s_message):
    print("Encrypting your message...")
    Violet.vtl(key,s_message,0)

def decrypt(key, s_message):
    print("Decrypting your message...")
    Violet.vtl(key, s_message, 1)

#frames to video
def frames_to_video(vid):
    print("Converting frames into a file named" + str(vid) + " ...")