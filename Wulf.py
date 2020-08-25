import pyautogui
import random
import pathlib
import sys
import os
sys.path.append(".")
import base64
import tkinter as tk
import requests
import datetime
import json
import spotipy
from functools import partial
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from tkinter import ttk
from PIL import ImageTk, Image, GifImagePlugin
from urllib.parse import urlencode

os.environ['SPOTIPY_CLIENT_ID'] = '161da30d264d45a6b6dbc66ed4d25960'
os.environ['SPOTIPY_CLIENT_SECRET']='aee09fb7280e43b994def38a7174804c'
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

WIDTH_OFFSET = 1800
HEIGHT_OFFSET = 980

#Animation constants, add in new animations here
IDLE_ANIMATION = 0
DANCE_ANIMATION = 1

#Animal constants, add new animals to animate here
WULF = 0
RAO = 1
RIGBY = 2

BACKGROUND_COLOR = '#0f00ff'

WINDOW_SIZE = '48x60+'#Todo make this dynamic

#TODO: Cache this after application closes?, along with current animal
lastClickX = 0
lastClickY = 0

window_on_top = True
currently_draggin_window = False

currentAnimationFrame = 0
currentAnimation = 0
currentAnimal = 0

nextAnimationNumber = 0

animationSpeed = 50 #framechanges in miliseconds

animal_idle_num = 11
animal_dance_num = 23

#Add more file names here
houndour_idle_filename = "ImageSource/Houndour.gif"
houndour_bark_filename = "ImageSource/Houndour_Bark.gif"

animationToPlay = IDLE_ANIMATION

dirPath = pathlib.Path(__file__).parent.absolute()
impath = str(dirPath)+"/"

#TODO: Need the idle animation, the email animtation, need the talking animation
#TODO: Optional polish -> make animation speed correlate to sound volume/bpm
#TODO: Mac and Linux compatibile
#############################################################################################################
def exit_wulf():
	sys.exit()
#############################################################################################################

#############################################################################################################
def popup(event):
	try:
		aMenu.tk_popup(event.x_root, event.y_root,0)
	finally:
		aMenu.grab_release()
#############################################################################################################

#############################################################################################################
def save_last_click_pos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y
#############################################################################################################

#############################################################################################################
def dragging(event):
    x, y = event.x - lastClickX + window.winfo_x(), event.y - lastClickY + window.winfo_y()
    window.geometry("+%s+%s" % (x , y))
    global currently_draggin_window
    currently_draggin_window = True
#############################################################################################################

#############################################################################################################
def test_print():
	print('Button was pressed')
#############################################################################################################

#############################################################################################################
#transfer random no. to event
def event(currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET): #Add in new animations here
 if animationToPlay == IDLE_ANIMATION:
  currentAnimation = IDLE_ANIMATION
  window.after(animationSpeed,update,currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET) #no. 1,2,3,4 = idle

 elif animationToPlay == DANCE_ANIMATION:
  currentAnimation = DANCE_ANIMATION
  window.after(animationSpeed,update,currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET) #no. 5 = idle to sleep
#############################################################################################################

#############################################################################################################
#making gif work 
def gif_work(currentAnimationFrame,animationClip,animationToPlay, newEventIncoming):
 if currentAnimationFrame < animationClip -1:
  currentAnimationFrame+=1
 else:
  currentAnimationFrame = 0
  animationToPlay = newEventIncoming
 return currentAnimationFrame,animationToPlay
#############################################################################################################

#############################################################################################################
def update(currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET): #Add in new animations here
 #idle
 if currentAnimation == IDLE_ANIMATION:
  frame = animal_idle[currentAnimationFrame]
  currentAnimationFrame ,animationToPlay = gif_work(currentAnimationFrame,animal_idle_num,animationToPlay,nextAnimationNumber)
  
 #bark
 elif currentAnimation == DANCE_ANIMATION:
  frame = animal_dance[currentAnimationFrame]
  currentAnimationFrame ,animationToPlay = gif_work(currentAnimationFrame,animal_dance_num,animationToPlay,nextAnimationNumber)

 #label.configure(image=frame) #The current image of the thingy
 button.configure(image=frame)
 window.after(1,event,currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET)
#############################################################################################################

#############################################################################################################
def get_next_animation():
	return
#############################################################################################################

#############################################################################################################
def previous_track():
	current_track = sp.current_user_playing_track()
	global nextAnimationNumber
	if current_track == None:
		return 
	sp.previous_track()
	nextAnimationNumber = DANCE_ANIMATION
	return
#############################################################################################################

#############################################################################################################
def next_track():
	current_track = sp.current_user_playing_track()
	global nextAnimationNumber
	if current_track == None:
		return 
	sp.next_track()
	nextAnimationNumber = DANCE_ANIMATION
	return
#############################################################################################################

#############################################################################################################
def start_or_pause_music():
	global currently_draggin_window
	if currently_draggin_window:
		currently_draggin_window = False
		return

	current_track = sp.current_user_playing_track()
	global nextAnimationNumber

	if current_track == None:
		nextAnimationNumber = IDLE_ANIMATION 
		return 
	if current_track['is_playing']:
		nextAnimationNumber = IDLE_ANIMATION
		sp.pause_playback()
	else:
		sp.start_playback()
		nextAnimationNumber = DANCE_ANIMATION 
	return
#############################################################################################################

#############################################################################################################
def toggle_window_priority():
	global window_on_top
	if window_on_top:
		window.attributes("-topmost",False)
		window_on_top = False
		return
	elif not window_on_top:
		window.attributes("-topmost",True)
		window_on_top = True
	return
#############################################################################################################

#############################################################################################################
def setup():
	animal_in_file = read_file()
	setup_animations(animal_in_file)


	current_track = sp.current_user_playing_track()
	global nextAnimationNumber
	if current_track == None:
		nextAnimationNumber = IDLE_ANIMATION 
		return
	if current_track['is_playing']:
		nextAnimationNumber = DANCE_ANIMATION 
	else:
		nextAnimationNumber = IDLE_ANIMATION 
	return
#############################################################################################################

#############################################################################################################
def spotify_update():
	current_track = sp.current_user_playing_track()
	global nextAnimationNumber
	if current_track == None:
		nextAnimationNumber = IDLE_ANIMATION 
		return
	if current_track['is_playing']:
		nextAnimationNumber = DANCE_ANIMATION 
	else:
		nextAnimationNumber = IDLE_ANIMATION 

	window.after(2000,spotify_update)
	return
#############################################################################################################

#############################################################################################################
def setup_animations(animal_chosen): #Add in more animations here
	global animal_dance_num, animal_idle_num, animal_dance, animal_idle

	if animal_chosen == WULF:
		animal_idle_num, animal_idle = extract_image_data(houndour_idle_filename)
		animal_dance_num, animal_dance = extract_image_data(houndour_bark_filename)
		print("Wulf Chosen")
		try:
			f=open("Settings.txt", "r+")
			f.truncate(0)
			f.write("CurrentAnimal=Wulf")
			f.close()
			return
			pass
		except IOError as e:
			f=open("Settings.txt", "w+")
			f.write("CurrentAnimal=Wulf")
			f.close()
			return
			pass

	elif animal_chosen == RAO:
		animal_idle_num, animal_idle = extract_image_data(houndour_idle_filename)
		animal_dance_num, animal_dance = extract_image_data(houndour_bark_filename)
		print("Rao Chosen")
		try:
			f=open("Settings.txt", "r+")
			f.truncate(0)
			f.write("CurrentAnimal=Rao")
			f.close()
			return
			pass
		except IOError as e:
			f=open("Settings.txt", "w+")
			f.write("CurrentAnimal=Rao")
			f.close()
			return
			pass

	elif animal_chosen == RIGBY:
		animal_idle_num, animal_idle = extract_image_data(houndour_idle_filename)
		animal_dance_num, animal_dance = extract_image_data(houndour_bark_filename)
		print("Rigby Chosen")
		try:
			f=open("Settings.txt", "r+")
			f.truncate(0)
			f.write("CurrentAnimal=Rigby")
			f.close()
			return
			pass
		except IOError as e:
			f=open("Settings.txt", "w+")
			f.write("CurrentAnimal=Rigby")
			f.close()
			return
			pass

	else:
		animal_idle_num, animal_idle = extract_image_data(houndour_idle_filename)
		animal_dance_num, animal_dance = extract_image_data(houndour_bark_filename)
		print("Invalid Animal")
		try:
			f=open("Settings.txt", "r+")
			f.truncate(0)
			f.write("CurrentAnimal=Wulf")
			f.close()
			return
			pass
		except IOError as e:
			return
			pass

#############################################################################################################

#############################################################################################################
def extract_image_data(file_name):
	image_object = Image.open(str(impath)+file_name)
	num_of_frames = image_object.n_frames
	temp_frames = [tk.PhotoImage(file=str(impath)+file_name,format = 'gif -index %i' %(i)) for i in range(num_of_frames)]
	return num_of_frames, temp_frames
#############################################################################################################

#############################################################################################################
def read_file():
	try:
		f=open("Settings.txt", "r+")
		pass
	except IOError as e:
		print("File not found :(")
		f=open("Settings.txt", "w+")
		f.write("CurrentAnimal=Wulf")
		f.close()
		return WULF
		pass
	else:
		lineRead = f.readline()
		if(len(lineRead)<5):
			f.truncate(0)
			f.write("CurrentAnimal=Wulf")
			f.close()
			return WULF
		tempLine = lineRead.split("=")
		animal_chosen = tempLine[1]
		animal_chosen = animal_chosen.lower()
		animal_chosen = animal_chosen.strip()
		f.close()

		#This makes me want to vomit, but i'm too lazy to make this better
		if animal_chosen == "wulf":
			return WULF
		elif animal_chosen =="rao":
			return RAO
		elif animal_chosen =="rigby":
			return RIGBY
		else:
			return WULF
#############################################################################################################

#############################################################################################################


#Main
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
OAuth = SpotifyOAuth(scope=scope, redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'], cache_path=impath+"TempCache")
sp = spotipy.Spotify(auth_manager=OAuth)
sp.me()

#Gets the screen resolution
root = tk.Tk()
root.update_idletasks()
root.attributes('-fullscreen', True)
root.state('iconic')
WIDTH_OFFSET = root.winfo_screenwidth() - 100
HEIGHT_OFFSET = root.winfo_screenheight() - 100
root.destroy()

window = tk.Tk()#This is where the window actually is written
button = tk.Button(window,bd=0,bg="white",highlightcolor=BACKGROUND_COLOR,highlightthickness=0,relief='flat',command=start_or_pause_music, compound='bottom')
button.pack()

#Making the rightclick menu
window.bind('<Button-3>', popup)
aMenu = tk.Menu(window, tearoff=0)

aMenu.add_command(label='Next Track', command=next_track)
aMenu.add_command(label='Last Track', command=previous_track)
aMenu.add_command(label='Toggle Window Priority', command=toggle_window_priority)
aMenu.add_command(label='Change to Wulf', command=partial(setup_animations, WULF))
aMenu.add_command(label='Change to Rao', command=partial(setup_animations, RAO))
aMenu.add_command(label='Change to Rigby', command=partial(setup_animations, RIGBY))
aMenu.add_command(label='Exit', command=exit_wulf)

#call buddy's action gif
houndour_idle = [tk.PhotoImage(file=str(impath)+houndour_idle_filename,format = 'gif -index %i' %(i)) for i in range(11)]
houndour_bark = [tk.PhotoImage(file=str(impath)+houndour_bark_filename,format = 'gif -index %i' %(i)) for i in range(23)]

animal_from_file = read_file()

setup_animations(animal_from_file)

#window configuration
window.config(highlightbackground=BACKGROUND_COLOR)#This should be even more dynamic
label = tk.Label(window,bd=0,bg=BACKGROUND_COLOR) #This lets the animation be movable and show

window.overrideredirect(True)
window.geometry(WINDOW_SIZE+str(WIDTH_OFFSET)+'+'+str(HEIGHT_OFFSET)) #Actually sets up the thing on location
window.wait_visibility(window)
window.wm_attributes('-transparentcolor',BACKGROUND_COLOR)
window.bind('<Button-1>', save_last_click_pos)
window.bind('<B1-Motion>', dragging)
window.attributes("-topmost",True)
label.pack(expand = True)

#loop the program
window.after(1,update,currentAnimationFrame,currentAnimation,animationToPlay,WIDTH_OFFSET)
window.after(2000,spotify_update)
window.mainloop()
