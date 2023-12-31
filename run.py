# Import necessary libraries
from tkinter import *
import pygame
from PIL import ImageTk, Image
import os
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk

# Define color constants
bgBlack = "#171D1C"
fgWhite = "#EFE9F4"
accentBlue = "#3695F5"

# Create the main Tkinter window
screen = Tk()
screen.title("Melodia")
screen.configure(bg=bgBlack)

# Import and display program icon
img = PhotoImage(file="./sources/icon.gif")
screen.tk.call("wm", "iconphoto", screen._w, img)
screen.iconphoto(True, img)

# Set window properties
screen.resizable(0, 0)
#Default 330x550
screen.geometry("330x550")

# Initialize the Pygame mixer
pygame.mixer.init()

# Load control button images
playBtnImg = PhotoImage(file="./sources/ctrlbtn/play.png")
pauseBtnImg = PhotoImage(file="./sources/ctrlbtn/pause.png")
stopBtnImg = PhotoImage(file="./sources/ctrlbtn/stop.png")
frontBtnImg = PhotoImage(file="./sources/ctrlbtn/front.png")
backBtnImg = PhotoImage(file="./sources/ctrlbtn/back.png")

# Initialize global variable for play state, as well as what play state means
global playState
SONG_NOT_PLAYING = 0
SONG_IS_PLAYING = 1
SONG_IS_PAUSED = 2

# Initially, we dont want teh song to be playing
playState = SONG_NOT_PLAYING


# Function to change song duration (and auto play)
def changeDur():
    global tracks
    #Grab current time, edit the duration text (as integer)
    currentDur = pygame.mixer.music.get_pos()/1000

    #Sometimes there is a error when song is played, so fix it
    if currentDur < 0:
        currentDur = 0

    #Convert it into proper format
    convCurrentDur = time.strftime("%M:%S", time.gmtime(currentDur))

    #::: Getting the total time :::

    # Get file path of currently playing song
    track = trackBox.get(ACTIVE)    
    track = track.replace(" ", "_")
    curTrack = f"./music/{track}.mp3"

    #Read song length with mutagen
    songMutagen = MP3(curTrack)
    songLength= songMutagen.info.length
    #Convert to proper format
    convTotLen = time.strftime("%M:%S", time.gmtime(songLength))

    # :::PIGGYBACK:::
    #If the song ended, autoplay
    if convCurrentDur==convTotLen:
        nextTrack(1)

    #Change text 
    durLabel.config(text=f"{convCurrentDur} / {convTotLen}")


    #Run this again and again after 1 second
    durLabel.after(1000,changeDur)

# Function to change name of track
def changeName():
    currentPlaying = trackBox.get(ACTIVE)
    name = getSongName(currentPlaying)
    curTitle.configure(text=name)

# Function to stop the music
def stop():
    print("Stop pressed")
    pygame.mixer.music.stop()
    global playState
    playState = SONG_NOT_PLAYING
    mainBtn.configure(image=playBtnImg)
    mainBtn.photo = playBtnImg

#A function that controls teh working of the main play button
def mainBtnFunc(mainQuery):
    global playState, tracks
    
    # Copy the current play state to the local variable mainQuery
    mainQuery = playState
    
    # If the play state is 0 (initial or stopped)
    if playState == SONG_NOT_PLAYING:
        #Run the song duration fucntion when first played
        changeDur() 

        # Pause the music (if playing), print a message, and get the selected track
        pygame.mixer.music.pause()
        print("Play pressed first time")
        track = trackBox.get(ACTIVE)
        
        # Modify track name for file path and find its index in the tracks list
        track = track.replace(" ", "_")
        track = f"./music/{track}.mp3"
        trackIndex = tracks.index(track.replace("./music/", ""))
        
        # Load and play the selected track, update play state, and change album cover
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(loops=0)
        playState = SONG_IS_PLAYING
        changeCover(trackIndex)

        mainBtn.configure(image=pauseBtnImg)
        mainBtn.photo = pauseBtnImg

        # Change the current title name
        changeName()
    
    # If the play state is 1 (playing)
    elif playState == SONG_IS_PLAYING:
        # Pause the music, print a message, update play state, and change button image
        pygame.mixer.music.pause()
        print("Paused")
        playState = SONG_IS_PAUSED
        mainBtn.configure(image=playBtnImg)
        mainBtn.photo = playBtnImg
    
    # If the play state is 2 (paused)
    elif playState == SONG_IS_PAUSED:
        # Unpause the music, print a message, update play state, and change button image
        pygame.mixer.music.unpause()
        print("Unpaused")
        playState = SONG_IS_PLAYING
        mainBtn.configure(image=pauseBtnImg)
        mainBtn.photo = pauseBtnImg

# Function to play the next or previous track
def nextTrack(move):
    global playState

    # Get the index of the currently selected track in the listbox
    curTrack = trackBox.curselection()[0]
    
    # Calculate the index of the next track based on the movement direction
    if curTrack == 0 and move == -1:
        nextTrack = trackBox.size() - 1
    elif curTrack == (trackBox.size() - 1) and move == 1:
        nextTrack = 0
    else:
        nextTrack = trackBox.curselection()[0] + move
    
    # Print the index of the current song
    print("Current song is number", nextTrack)
    
    # Get the name of the next track, modify for file path, and update listbox selection
    playTrack = trackBox.get(nextTrack)
    playTrack = playTrack.replace(" ", "_")
    playTrack = f"./music/{playTrack}.mp3"
    
    trackBox.selection_clear(0, END)
    trackBox.activate(nextTrack)
    trackBox.selection_set(nextTrack, last=None)
    
    # Change the album cover based on the selected track
    changeCover(nextTrack)
    
    # Reset play state and simulate a button click to start playing the new track
    playState = 0
    mainBtnFunc(0)

    # Change the current title name
    changeName()

# Function to change the album cover image based on the selected track
def changeCover(trackNum):
    global curCover
    albumCover = tracks[trackNum].replace(".mp3", "")
    albumCover = f"./music/albumCover/{albumCover}-cover.jpg"
    curCover = Image.open(albumCover)
    curCover = curCover.resize((250, 250), Image.LANCZOS)
    curCover = ImageTk.PhotoImage(curCover)
    curCoverLabel.configure(image=curCover)

# Function to get song name
def getSongName(path):
    name = path.replace(".mp3", "")
    name = name.replace("_", " ")
    return name

# Function to get song path
def getSongPath(name):
    name = name.replace(" ", "_")
    path = f"./music/{name}.mp3"
    return path

# Function to get song album path
def getSongCov(name):
    path = name.replace(".mp3", "")
    path = path.replace(" ", "_")
    path = f"./music/albumCover/{path}-cover.jpg"
    return path

# Create a listbox to display tracks
trackBox = Listbox(
    screen,
    bg=bgBlack,
    fg=fgWhite,
    width=30,
    height=5,
    borderwidth=0,
    highlightthickness=0,
    selectbackground=accentBlue,
    selectborderwidth=0,
)

# Defualt to the first track in the listbox
trackBox.activate(0)
trackBox.selection_set(0)

# Fetch list of tracks
global tracks
tracks = []
for name in os.listdir("./music"):
    if name in [".gitignore", "albumCover"]:
        continue
    tracks.append(name)
tracks = sorted(tracks)

# Fill the listbox with track names
for name in tracks:
    name = name.replace(".mp3", "")
    name = name.replace("_", " ")
    trackBox.insert("end", name)

# Load the initial album cover
# albumCover = tracks[0].replace(".mp3", "")
# albumCover = f"./music/albumCover/{albumCover}-cover.jpg"

albumCover = getSongCov(trackBox.get(0))
global curCover
curCover = Image.open(albumCover)
curCover = curCover.resize((250, 250), Image.LANCZOS)
curCover = ImageTk.PhotoImage(curCover)

# Create a label to display the album cover
curCoverLabel = Label(image=curCover, borderwidth=0, highlightthickness=0)
curCoverLabel.pack(pady=10)

# Display the song duration
durLabel = Label(
    screen, 
    text="00:00",
    borderwidth=0,
    highlightthickness=0,
    bd=0,
    bg=bgBlack,
    fg=fgWhite,
    width=20,
    height=1,
    font=("Arial", 16)
    )

durLabel.pack()

# Slider for song duration
slider = ttk.Scale(
    screen,
    from_=0, 
    to=100,
    orient=HORIZONTAL,
    value=0,
    length = 330
    )
slider.pack(pady=20)

# Text box for song length
firstTrack = getSongName(trackBox.get(0))

# Display the current song name
curTitle = Label(screen, text=firstTrack, bd=1, bg=accentBlue, fg=bgBlack)
curTitle.pack(fill=X, ipady=5, pady=10)

# Pack the listbox (Under the cover)
trackBox.pack()

# Create a frame for control buttons
btnDiv = Frame(screen, bg=bgBlack, pady=10, bd=0)
btnDiv.pack()

# Create control buttons
mainBtn = Button(
    btnDiv,
    image=playBtnImg,
    borderwidth=0,
    command=lambda: mainBtnFunc(playState),
    bg=bgBlack,
    highlightthickness=0,
    bd=0,
)
stopBtn = Button(
    btnDiv,
    image=stopBtnImg,
    borderwidth=0,
    command=stop,
    bg=bgBlack,
    highlightthickness=0,
    bd=0,
)
backBtn = Button(
    btnDiv,
    image=backBtnImg,
    borderwidth=0,
    command=lambda: nextTrack(-1),
    bg=bgBlack,
    highlightthickness=0,
    bd=0,
)
frontBtn = Button(
    btnDiv,
    image=frontBtnImg,
    borderwidth=0,
    command=lambda: nextTrack(1),
    bg=bgBlack,
    highlightthickness=0,
    bd=0,
)

# Grid layout for control buttons
backBtn.grid(row=0, column=0, padx=20)
mainBtn.grid(row=0, column=1, padx=20)
frontBtn.grid(row=0, column=2, padx=20)
stopBtn.grid(row=1, column=1, pady=10)

# Start the Tkinter event loop
screen.mainloop()
