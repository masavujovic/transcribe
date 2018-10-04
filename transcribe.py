"""
Masa Vujovic 2017
PsychoPy2 v1.84.2 (Python 2.7)

This program takes a random sample of stimuli and presents to participant,
whose task is to transcribe the stimuli. The stimuli can be audio files,
videos, or pictures. The program outputs a csv file with participant ID, session number,
the file name of the target stimulus, and participant response.

INSTRUCTIONS:
    1. This file (coding_stims.py) must be in the same folder as the files you want to transcribe.
    2. In the same folder, create a newfolder called CODED before you run the script for the firs time.
    3. When you run the script, a dialog box will appear, with the following fields:
        CODER ID = can be anything (numbers, letters, etc)
        SESSION NUMBER = if this is your first batch of coding, enter 1, etc.
        NUMBER OF FILES = number of files you want to transcribe in one go. I would keep this 
        small if possible, because if the program crashes (which it shouldnt!) your input will not be saved.
        FILE TYPE = audio, picture, or video.
"""

from psychopy import core, visual, event, gui, sound
import pyglet
import os
import random
import csv
import datetime
import shutil 
from collections import OrderedDict

my_dir = os.getcwd()
sub_dir = my_dir + '/CODED'
date = datetime.datetime.today().strftime("%d %B %Y")

#########################################################
################### OPENING GUI #########################
#########################################################
# Displays gui to take user input.
# Number of files: random sample size.
# File type: audio, video or picture. 

session_info = OrderedDict([('Coder ID', ''), ('Session', ''), ('Number of files', ''), ('File type', ('audio','video','picture')),])
dlg = gui.DlgFromDict(dictionary = session_info, order=list(session_info.keys()), title="Session info")
if dlg.OK:
    coder_ID = session_info['Coder ID']
    session = session_info['Session']
    n = int(session_info['Number of files'])
    file_type = session_info['File type']
else:
    core.quit()
    print('User Cancelled')


#########################################################
################# PSYCHOPY WINDOW #######################
#########################################################

win = visual.Window(size = (1440, 900), fullscr = True, allowGUI = True, allowStencil = False, color = [1,1,1])

#########################################################
################### GET ALL FILES #######################
#########################################################
def get_files(file_type):
    """
    Searches though current working directory for all files of certain file_type.
    file_type could be "audio", "video", or "picture".
    Returns a list of strings. 
    """
    all_files = os.listdir(my_dir)
    if file_type == "audio":
        extension = '.wav'
    elif file_type == "video":
        extension = '.mp4'
    elif file_type == "picture":
        extension = '.jpg'
    current_files = [x for x in all_files if x.endswith(extension)]
    return current_files

#########################################################
#################### INSTRUCTIONS #######################
#########################################################
def begin_instruction():
    """
    Displays instructions and waits for button press.
    """
    instr = "Press ENTER to replay stimuli.\n \nPress RIGHT ARROW key to go to next page.\n \nNow press ENTER to begin."
    instruction = visual.TextStim(win, text = instr, wrapWidth = 1.5, color = 'black')
    received_return = False
    event.clearEvents('keyboard')
    while not (received_return):
        letter_list = event.getKeys(keyList = ['return'])
        for l in letter_list:
            if l == 'return':
                received_return = True
        instruction.draw()
        win.flip()

def end_instruction():
    """
    Displays closing message.
    """
    msg = "The end! Thank you."
    message = visual.TextStim(win, text = msg, pos =[ 0,0], wrapWidth = None, color = "black")
    message.draw()
    win.flip()
    core.wait(2)

#########################################################
################# DISPLAYING TRIALS #####################
#########################################################
def get_text(target, file_type, count, win):
    """
    Collects text input from participant and draws it as they are typing it.
    Returns a string.
    """
    typed_text = ''
    received_right = False
    event.clearEvents('keyboard')
    while not(received_right):
        letter_list = event.getKeys(keyList=['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m',
        'backspace', 'return', 'right','slash','1','2','3','4'])
        for l in letter_list:
            if l == 'right':
                received_right = True
            elif l =='backspace':
                if len(typed_text) > 0:
                    typed_text = typed_text[:-1] # take the last letter off the string
            elif l == 'slash':
                typed_text += '?'
            elif l == 'return':
                target()
            else: typed_text += l # if key isn't backspace, add key pressed to the string
            # continually redraw intructions, ppt response, and target stimulus onscreen until return pressed
        instr = visual.TextStim(win, text="Type your response here:", color = "black", pos=(0,-0.3), wrapWidth=None)
        response = visual.TextStim(win, text=typed_text,color="black",pos=(0,-0.5),wrapWidth=1.5)
        c = visual.TextStim(win, text=count, color="black", pos=(0.9, -0.9), wrapWidth=None)
        if file_type == "picture" or file_type == "video":
            target()
            [item.draw() for item in [response] + [instr] + [c]]
        elif file_type == "audio":
            [item.draw() for item in [instr] + [response] + [c]]
        win.flip()
    return typed_text

def get_target(file_name, file_type, win):
    """
    Creates a PsychoPy object for given stimulus.
    file_name = stimulus file name
    Returns a list containing the PsychoPy object (f) and filename without the extension (name[0]).
    """
    if file_type == "audio":
        f = sound.Sound(value = my_dir + '/' + file_name).play
    elif file_type == "picture":
        f = visual.ImageStim(win, image = my_dir + '/' + file_name, pos = [0,0.2]).draw
    elif file_type == "video":
        f = visual.MovieStim3(win, filename = my_dir + '/' + file_name, pos = [0,0.2], units = "norm", size=(0.8,0.8), loop = True).draw
    name = file_name
    return [f, name]


#########################################################
################ RUNNING EXPERIMENT #####################
#########################################################
def display_and_write(trial, transcribed_csv, sub_sample):
    target = get_target(sub_sample[trial], file_type, win) 
    target[0]() 
    win.flip()
    ppt_response = get_text(target[0], file_type, trial+1, win)
    response_dict = {"coder_ID": coder_ID, "date": date, "session": session, "file_name": target[1], "coded_as": ppt_response}
    with open(transcribed_csv, "ab") as csvfile:
        fieldnames = ["coder_ID", "date", "session", "file_name", "coded_as"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(response_dict) 
        print [target[1], ppt_response]
    csvfile.close()
    shutil.move(my_dir + "/" + sub_sample[trial], sub_dir + "/" + sub_sample[trial])

    
def task():
    # Display instructions
    begin_instruction()
    win.flip()
    # Get relevant files
    current_files = get_files(file_type)
    # Take a random sample of files size n 
    sub_sample = random.sample(current_files, n)
    # Open a csv file in which to write participants' responses
    transcribed_csv = "%s_transcribed_stimuli.csv" %(coder_ID)
    file_exists = os.path.isfile(transcribed_csv)
    with open(transcribed_csv, "ab") as csvfile:
        fieldnames = ["coder_ID", "date", "session", "file_name", "coded_as"]
        # Write header
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
    csvfile.close()
    for trial in xrange(n):
        display_and_write(trial, transcribed_csv, sub_sample)
    end_instruction()

task()
