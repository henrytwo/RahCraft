# RAHCRAFT
# COPYRIGHT 2017 (C) RAHMISH EMPIRE, MINISTRY OF RAHCRAFT DEVELOPMENT
# DEVELOPED BY RYAN ZHANG, HENRY TU, SYED SAFWAAN

# main.py

from pygame import *
import pickle
import socket
import hashlib
import traceback

import components.rahma as rah
import components.menu as menu
import Game as Game
import webbrowser
import json
from random import *
from multiprocessing import *
from urllib.request import urlretrieve, Request, urlopen
import zipfile
import os
import glob
from shutil import copyfile, copy2, rmtree

# Statistics
import platform
import datetime
import requests
import time as t
import getpass


# Function for collecting system info for analytics
def collect_system_info(current_build, current_version):
    sys_information = [
        current_version,
        current_build,
        platform.machine(),
        platform.version(),
        platform.platform(),
        platform.uname(),
        platform.system(),
        platform.processor(),
        getpass.getuser(),
        datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'),
        requests.get('http://ip.42.pl/raw').text]

    return sys_information


# Copy a directory for software updates
# Courtesy of:
# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(src, dst, symlinks=False, ignore=None):
    # If the directory doesn't exist, make it
    if not os.path.exists(dst):
        os.makedirs(dst)

    # Copy all folders int he directory
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        # If it is another directory
        if os.path.isdir(s):

            # Run the function recursively
            copytree(s, d, symlinks, ignore)
        else:
            # Copy the file
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                copy2(s, d)


# Get progress of a file downloaded from the internet
# Courtesy of:
# http://www.dreamincode.net/forums/topic/258621-console-progress-for-download-over-http/
def progress(block_no, block_size, file_size):
    global update_progress  # Using a global variable to keep track of progress easier

    update_progress += block_size  # Updates var with amount of file downloaded

    # Draws progress bar
    draw.rect(screen, (0, 0, 0), (size[0] // 4, (size[1] // 2) + 50, size[0] // 2, 10))
    draw.rect(screen, (0, 255, 0), (size[0] // 4, (size[1] // 2) + 50, int((size[0] // 2) * update_progress / file_size), 10))

    # Progress text
    status_text = rah.text("%s%% (%iMB/%iMB)" % (int(update_progress / file_size * 100), round(update_progress / 1000000, 2), round(file_size / 1000000, 2)), 13)

    # Fills region of screen so that text can be updated
    draw.rect(screen, (150, 150, 150), (size[0] // 4, size[1] // 2 + 65, size[0] // 2, 20))

    # Blits status text
    screen.blit(status_text, (size[0] // 2 - status_text.get_width() // 2, size[1] // 2 + 65))

    # Updates screen
    display.flip()


# Function for updating the game software
def software_update():
    global screen, current_version, current_build, size, update_progress  # Global variables to make modifying values easier

    display.set_caption("RahCraft Update Service")

    # Sets background
    rah.wallpaper(screen, size)

    # Main caption
    title_text = rah.text("Welcome to RahCraft! Let's get you up to date", 20)
    screen.blit(title_text, (size[0] // 2 - title_text.get_width() // 2, size[1] // 4 - title_text.get_height() - 50))

    # Sets update to null value since user hasn't decided on whether or not to proceed
    update = None

    # Try to connect to update server
    try:
        # Reads a text file on website to look for latest version
        req = Request('https://rahcraft.github.io/rahcraft.txt', headers={'User-Agent': 'Mozilla/5.0'})

        # Splits the file into its components
        with urlopen(req) as response:
            extracted_file = str(response.read())[2:][:-3].split('\\n')

        latest_version = int(extracted_file[0])
        latest_build = extracted_file[1]
        update_location = extracted_file[2]

        # If the current version is out of date
        if current_version < latest_version:

            # Set captions
            update_text = rah.text("Good news! RahCraft v%s is now available!" % latest_build, 18)

            # Draws the 'window'
            draw.rect(screen, (0, 0, 0),
                      (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20), size[1] // 2 - 90, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

            draw.rect(screen, (150, 150, 150),
                      (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20), size[1] // 2 - 100, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

            screen.blit(update_text,
                        (size[0] // 2 - update_text.get_width() // 2, size[1] // 2 - update_text.get_height() - 50))

            # Create the buttons
            exit_button = menu.Button(size[0] // 4, size[1] // 2 + 200, size[0] // 2, 40, 'exit', 'Exit game')
            update_button = menu.Button(size[0] // 4, size[1] // 2 - 20, size[0] // 2, 40, 'do_update', 'Update now')
            skip_button = menu.Button(size[0] // 4, size[1] // 2 + 30, size[0] // 2, 40, 'skip_update', 'Skip')

            while True:

                # Mouse state
                release = False

                for e in event.get():
                    if e.type == QUIT:
                        return 'exit'

                    if e.type == MOUSEBUTTONUP and e.button == 1:
                        release = True

                    # If the screen is resized, call function again to redraw everything
                    if e.type == VIDEORESIZE:
                        screen = display.set_mode((e.w, e.h), RESIZABLE)
                        return 'update'

                mx, my = mouse.get_pos()
                m_press = mouse.get_pressed()

                # Skip update
                if skip_button.update(screen, mx, my, m_press, 15, release):

                    return 'login'

                # Proceed with update
                elif update_button.update(screen, mx, my, m_press, 15, release):

                    # Draws background
                    rah.wallpaper(screen, size)

                    # Changes captions
                    update_text = rah.text("Downloading updates", 18)
                    subupdate_text = rah.text("This shouldn't take long...", 18)

                    # Draws windows
                    draw.rect(screen, (0, 0, 0),
                              (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20),
                               size[1] // 2 - 90, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

                    draw.rect(screen, (150, 150, 150),
                              (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20),
                               size[1] // 2 - 100, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

                    # Blit text
                    screen.blit(update_text,
                                (size[0] // 2 - update_text.get_width() // 2,
                                 size[1] // 2 - update_text.get_height()))

                    screen.blit(subupdate_text,
                                (size[0] // 2 - subupdate_text.get_width() // 2,
                                 size[1] // 2 - subupdate_text.get_height() + 30))

                    # Update screen
                    display.flip()

                    # Deletes any existing update files to prevent conflict
                    if os.path.isfile('update.zip'):
                        os.remove("update.zip")

                    if os.path.isfile('../update'):
                        rmtree("../update")

                    # Downloads the latest version of the game while calling the progress function so progress is kept track
                    urlretrieve(url=update_location, filename='update.zip', reporthook=progress)

                    # Extracts the update in root project directory
                    with zipfile.ZipFile('update.zip', 'r') as zip_file:
                        zip_file.extractall('../update')

                    # Deletes the zip to save space
                    os.remove("update.zip")

                    # Indexes folder for directories and files
                    dir_list = glob.glob('../update/*/*')

                    # Iterates through each directory
                    for dir in dir_list:
                        file_name = dir.split('/')[-1]  # Gets the last portion of full file location (file name)

                        # Checks if user files exists
                        # These files are usually not touched in a software update since they contain personal information
                        user_files_intact = os.path.isfile('user_data/servers.json') and os.path.isfile('user_data/session.json')

                        # Copy user files ONLY if they don't exist, otherwise copy as normal
                        if (user_files_intact and file_name != 'user_data') or not user_files_intact:

                            # Checks if file name contains a period, indicating it is a file not directory
                            if len(file_name.split('.')) == 2:
                                copyfile(dir, '../' + file_name)  # Copies file with function
                            else:
                                copytree(dir, '../' + file_name)  # Copies directory with function

                    rmtree("../update")  # Deltes the update directory to save space

                    # Updates version variables
                    current_build, current_version = latest_build, latest_version

                    # Updates version file
                    with open('data/ver.rah', 'w') as version_file:
                        version_file.write('%s\n%s' % (current_version, current_build))

                    # Confirms update is completed
                    return ['information', '\n\n\nRahCraft has updated successfully\nPlease restart game to apply changes', 'exit']

                # Exit the program
                elif exit_button.update(screen, mx, my, m_press, 15, release):
                    return 'exit'

                display.update()

        else:
            # No software update is needed, proceed to game
            return 'login'

    except:
        # If something went wrong and update could not be completed
        print(traceback.format_exc())
        return ['information', '\n\n\n\n\nUnable to perform update software', 'login']


# This function logs the user into the game
def login():
    display.set_caption("RahCraft Authentication Service")

    global username, password, host, port, token, screen  # Global var used to make modifying easier

    # Function to hash a given string
    def hash_creds(target):
        return hashlib.sha512(target.encode('utf-8')).hexdigest()

    # Draws background
    rah.wallpaper(screen, size)

    # Sets title
    title_text = rah.text('Welcome to RahCraft! Login to continue', 20)
    screen.blit(title_text, (size[0] // 2 - title_text.get_width() // 2, size[1] // 4 - title_text.get_height() - 50))

    try:  # Try and except since the state of session file is known
        with open('user_data/session.json', 'r') as session_file:

            # Load the session info
            session = json.load(session_file)

            # If the session has content
            if session['name'] and session['token']:
                # Loads into memory
                token = session['token']
                username = session['name']

                # Attempt to authenticate with token
                return 'auth'

    except ValueError:  # If not valid json or does not exist
        # Create empty session file
        with open('user_data/session.json', 'w') as session_file:
            json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

    # Resets credential vars
    username, password = '', ''

    # Field accepting entry
    field_selected = 'Username'

    # List with field objects
    fields = {'Username': [menu.TextBox(size[0] // 4, size[1] // 2 - 100, size[0] // 2, 40, 'Username'), username],
              'Password': [menu.TextBox(size[0] // 4, size[1] // 2 - 30, size[0] // 2, 40, 'Password'), password]}

    # Button objects
    exit_button = menu.Button(size[0] // 4, size[1] // 2 + 200, size[0] // 2, 40, 'exit', 'Exit game')
    auth_button = menu.Button(size[0] // 4, size[1] // 2 + 50, size[0] // 2, 40, 'auth', 'Login')
    signup_button = menu.Button(size[0] // 4, size[1] // 2 + 100, size[0] // 2, 40, 'signup', 'Need an account? Signup here')

    while True:

        # Resets mouse vars
        click = False
        release = False

        # Var to pass the event to text field
        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                # Shift enter to bypass auth
                if key.get_mods() & KMOD_CTRL and key.get_mods() & KMOD_SHIFT:
                    if e.key == K_RETURN and username:
                        return 'menu'

                # Enter to auth with credentials
                elif e.key == K_RETURN and username and password:
                    return 'auth'

                # Tab to alternate between fields
                if e.key == K_TAB:
                    if field_selected == 'Username':
                        field_selected = 'Password'
                    else:
                        field_selected = 'Username'

            # If resize, recall the function to redraw
            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'login'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Get values from textfields
        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        # Draws and updates textfields
        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and click:
                field_selected = field

        # Create account, redirect to website
        if signup_button.update(screen, mx, my, m_press, 15, release):
            webbrowser.open('http://rahmish.com/join.php')

        # Authenticate with credentials
        nav_update = auth_button.update(screen, mx, my, m_press, 15, release)
        if nav_update and username:
            return nav_update

        # Exit game
        nav_update = exit_button.update(screen, mx, my, m_press, 15, release)
        if nav_update:
            return nav_update

        # Hash password and set as var for security + match server
        username, password = fields['Username'][1], hash_creds(
            hash_creds(fields['Password'][1]) + hash_creds(fields['Username'][1]))

        display.update()


# Function to get auth token from server using credentials
def authenticate():
    global username, password, online, token, current_build, current_version  # Global vars to edit easier

    # Background
    rah.wallpaper(screen, size)
    connecting_text = rah.text("Authenticating...", 30)
    screen.blit(connecting_text,
                rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    display.update()

    # Address of authentication server hardcoded
    host, port = 'rahmish.com', 1111

    socket.setdefaulttimeout(10)  # Timeout incase server is not accessible
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Start TCP server
    SERVERADDRESS = (host, port)  # Binds to AUTH server
    socket.setdefaulttimeout(None)  # Resets timeout to not affect other connections

    try:  # Try except incase connection fails
        server.connect(SERVERADDRESS)  # Connects to auth server

        if token:  # If token is being used

            # Send token with system information for analytics
            server.send(pickle.dumps([1, [username, token], collect_system_info(current_build, current_version)]))

        else:
            # Sends credentials and sys infromation for analyics
            credentials = [username, password]
            server.send(pickle.dumps([0, credentials, collect_system_info(current_build, current_version)]))

        while True:

            # Receive message from server
            first_message = pickle.loads(server.recv(10096))

            # If connection approved
            if first_message[0] == 1:

                # If token is being used
                if token:
                    # Confirm username and token
                    token = first_message[1][1]
                    username = first_message[1][0]

                else:
                    # Get the token from server
                    token = str(first_message[1])

                # Write the new token to file for future use
                with open('user_data/session.json', 'w') as session_file:
                    json.dump({"token": "%s" % token, "name": "%s" % username}, session_file, indent=4, sort_keys=True)

                # Flags client as online
                online = True

                # Closes connection and proceeds to menu
                server.close()
                return 'menu'

            # If rejected
            else:
                server.close()

                # Clears fields
                username = ''
                token = ''

                # Resets file
                with open('user_data/session.json', 'w') as session_file:
                    json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

                return 'reject'

    except:  # If something goes wrong
        server.close()

        # Clears session
        with open('user_data/session.json', 'w') as session_file:
            json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

        # Displays message
        return "information", '\n\n\n\n\nUnable to connect to authentication servers\nTry again later\n\n\nVisit rahmish.com/status.php for help', "login"


# Function for the about screen
def about():
    global screen  # Global variable so that screen object can be modified if resized

    # Starts playing keith music
    music_object = mixer.Sound('sound/menu_music/about.wav')
    music_object.play(0)

    # Starts the backgound
    rah.wallpaper(screen, size)

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    # Contents of about screen
    about_list = ['RahCraft',
                  '',
                  '',
                  'The Zen of Python, by Tim Peters',
                  'Beautiful is better than ugly.',
                  'Explicit is better than implicit.',
                  'Simple is better than complex.',
                  'Complex is better than complicated.',
                  'Flat is better than nested.',
                  'Sparse is better than dense.',
                  'Readability counts.',
                  'Special cases aren\'t special enough to break the rules.',
                  'Although practicality beats purity.',
                  'Errors should never pass silently.',
                  'Unless explicitly silenced.',
                  'In the face of ambiguity, refuse the temptation to guess.',
                  'There should be one-- and preferably only one --obvious way to do it.',
                  "Although that way may not be obvious at first unless you're Dutch.",
                  'Now is better than never.',
                  'Although never is often better than *right* now.',
                  'If the implementation is hard to explain, it\'s a bad idea.',
                  'If the implementation is easy to explain, it may be a good idea.',
                  'Namespaces are one honking great idea -- let\'s do more of those!',
                  '',
                  '',
                  '',
                  'rahmish.com',
                  '',
                  'RahCraft (C) Rahmish Empire, All Rahs Reserved',
                  '',
                  'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                  'ICS3U 2017',
                  '',
                  'Vincent Massey Secondary School',
                  '',
                  '',
                  'Honourable mentions:',
                  'Mr. McKenzie and Mr. Macanovik (Comp Sci gods)',
                  'Her Majesty Rahma Gillan (Dear Leader)',
                  'Dr J Bruce White (Motivation)',
                  'Adam Mehdi (Math Getterer)',
                  'Edward Snowden (Security Expert)',
                  'Vahnessa Vuong (Meme maker)',
                  'Megan Yang (Kpop person)',
                  'The Lord himself, Weith Kong (God)',
                  'Comrade Vladimir Lenin (Rolemodel)',
                  '',
                  '',
                  '',
                  '                 !#########       #                 ',
                  '               !########!          ##!              ',
                  '            !########!               ###            ',
                  '         !##########                  ####          ',
                  '       ######### #####                ######        ',
                  '        !###!      !####!              ######       ',
                  '          !           #####            ######!      ',
                  '                        !####!         #######      ',
                  '                           #####       #######      ',
                  '                             !####!   #######!      ',
                  '                                ####!########       ',
                  '             ##                   ##########        ',
                  '           ,######!          !#############         ',
                  '         ,#### ########################!####!       ',
                  "       ,####'     ##################!'    #####     ",
                  "     ,####'            #######              !####!  ",
                  "    ####'                                      #####",
                  '    ~##                                          ##~',
                  '',
                  '%rah%',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  '',
                  'Rah save the Queen!',
                  '']
    scroll_y = size[1]

    # Imports and resizes Keith
    keith_meme = transform.scale(image.load('textures/keith.png'), (size))
    keith_surface = Surface(size)
    keith_surface.blit(keith_meme, (0, 0))
    keith_surface.set_alpha(1)  # Makes him transparent for meme effect

    rahma_meme = image.load('textures/rahma.png')

    # Clock to maintain frame rate
    clock = time.Clock()

    while True:

        # If all contents of about screen are off screen, exit
        if scroll_y < -20 * len(about_list):
            music_object.stop()
            return 'menu'

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            # If window is resized, call function again to redraw
            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                music_object.stop()
                return 'about'

            # Escape key to skip
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    music_object.stop()

                    return 'menu'

        # Wall paper
        rah.wallpaper(screen, size)

        # Keith
        screen.blit(keith_surface, (0, 0))

        # Changes alpha
        keith_surface.set_alpha(100 * (scroll_y / (-20 * len(about_list))))

        # Draws all the text
        for y in range(0, len(about_list)):

            if about_list[y] != '%rah%':
                about_text = normal_font.render(about_list[y], True, (255, 255, 255))
                screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20 + scroll_y))

            else:
                screen.blit(rahma_meme, (size[0] // 2 - rahma_meme.get_width() // 2, 50 + y * 20 + scroll_y))

        # Scrolls screen
        scroll_y -= 1

        # Updates display
        display.update()
        clock.tick(30)


# Function if credentials are rejected by authentication server
def reject():
    global screen  # Global variable to make resizing easier

    # Background
    rah.wallpaper(screen, size)

    # Creates button object
    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'login', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    # Text contents
    auth_list = ['',
                 '',
                 '',
                 'AUTHENTICATION FAILED',
                 '',
                 'Username or Password is invalid',
                 'Ensure capslock is disabled and credentials',
                 'match those provided at time of account creation',
                 '',
                 'If you forget your password, reset it at',
                 'rahmish.com/management.php',
                 '',
                 '',
                 'RahCraft (C) Rahmish Empire, All Rahs Reserved',
                 '',
                 'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                 'ICS3U 2017'
                 ]

    while True:
        # Mouse state
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            # Updates mouse state
            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            # Recall function on resize to redraw everything
            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'reject'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Draws text on screen
        for y in range(0, len(auth_list)):
            about_text = normal_font.render(auth_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

        # Updates buttons
        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        # Redirects if needed
        if nav_update is not None:
            return nav_update

        # Updates screen
        display.update()


# Function to display a formatted crash screen instead of stopping entire program
def crash(error, previous):
    global screen  # Global variable to make resizing easier

    # Blue tint
    tint = Surface(size)
    tint.fill((0, 0, 255))
    tint.set_alpha(99)
    screen.blit(tint, (0, 0))

    # Creates button object
    back_button = menu.Button(size[0] // 4, size[1] - 200, size[0] // 2, 40, previous, "Return")

    # Converts the traceback to list
    error_message = list(map(str, error.split('\n')))

    # Joins the error message from traceback
    about_list = ['',
                  '',
                  ':( Whoops, something went wrong',
                  '', ] + error_message + ['RahCraft (C) Rahmish Empire, All Rahs Reserved',
                                           '',
                                           'Note: If clicking the button below doesnt',
                                           'do anything, the game is beyond broken',
                                           'and needs to be restarted',
                                           '',
                                           '',
                                           '',
                                           'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                                           'ICS3U 2017',
                                           '']

    while True:
        release = False  # Mouse state

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            # Update mouse state
            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            # Recall function on resize
            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'crash', error, previous

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Draws text
        for y in range(0, len(about_list)):
            about_text = rah.text(about_list[y], 15)
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 10 + y * 20))

        # Update button
        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        # Changes page is necessary
        if nav_update is not None:
            return nav_update

        display.update()


# Displays information in a formatted page (Much like crash)
def information(message, previous):
    global screen

    # Background
    rah.wallpaper(screen, size)

    # Creates button object
    back_button = menu.Button(size[0] // 4, size[1] - 200, size[0] // 2, 40, previous, "Okay")

    # Converts the message string into a list
    message_list = list(map(str, message.split('\n')))

    while True:
        release = False  # MOuse state

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            # Update mouse state
            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            # Update display if resized
            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'information', message, previous

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Draws text
        for y in range(0, len(message_list)):
            about_text = rah.text(message_list[y], 15)
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 10 + y * 20))

        # Update button
        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        # Update page
        if nav_update is not None:
            return nav_update

        display.update()


def death(message):
    global screen

    tint = Surface(size)
    tint.fill((50, 0, 0))
    tint.set_alpha(99)

    screen.blit(tint, (0, 0))

    buttons = [menu.Button(size[0] // 4, size[1] - 200, size[0] // 2, 40, 'game', "Respawn"),
               menu.Button(size[0] // 4, size[1] - 150, size[0] // 2, 40, 'menu', "Rage quit")]

    # Load the graphics first so there is no delay for sound
    kill_text = rah.text(message, 40)
    screen.blit(kill_text, rah.center(0, 0, *size, *kill_text.get_size()))

    display.flip()

    # Sound effects
    rah.load_sound(['sound/random/classic_hurt.ogg'])

    sound_object = mixer.Sound('sound/sadviolin.ogg')
    sound_object.play(0)

    while True:
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'death', message

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        kill_text = rah.text(message, 40)
        screen.blit(kill_text, rah.center(0, 0, *size, *kill_text.get_size()))

        for button in buttons:

            nav_update = button.update(screen, mx, my, m_press, 15, release)

            if nav_update is not None:
                sound_object.stop()

                return nav_update

        display.update()


def assistance():
    global screen

    rah.wallpaper(screen, size)
    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'menu', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = ['HELP',
                  '------------------------------------',
                  'BOIII',
                  'SO YOU WANNA PLAY DIS GAME HUH?',
                  'WELL ITS RLLY EZ ACTUALLY',
                  'LEGIT',
                  'YOU TAKE UR FAT FINGERS',
                  'PRESS DOWN',
                  'ON UR KEYBOARD',
                  'AND UR DONE.',
                  'DO U SEE THAT PERIOD????',
                  'IT MEANS *MIC DROP*',
                  '',
                  'THATS RIGHT',
                  'ANYWAYS, GOD SAVE THE QUEEN',
                  'LONG LIVE THE RAHMISH EMPIRE',
                  '']

    while True:

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'assistance'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def options():
    global screen

    rah.wallpaper(screen, size)
    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'menu', "Back")

    life_switch = menu.Switch(size[0] // 4, size[1] // 2 - 20, size[0] // 2, 40, False, 'Dank memes')
    music_slider = menu.Slider(size[0] // 4, size[1] // 2 - 80, size[0] // 2, 40, music_object.get_volume(), 'Music')

    while True:

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'assistance'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        music_slider.update(screen, mx, my, m_press, 15, release)

        music_object.set_volume(music_slider.pos)
        life_switch.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def receive_message(message_queue, server):
    rah.rahprint('Ready to receive command...')

    while True:
        msg = server.recvfrom(163840)
        message_queue.put(pickle.loads(msg[0]))


def status_screen(status, size, screen):
    rah.wallpaper(screen, size)

    connecting_text = rah.text("Updating servers...", 30)
    screen.blit(connecting_text,
                rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    status_text = rah.text(status, 15)
    screen.blit(status_text, rah.center(0, 50, size[0], size[1], status_text.get_width(), status_text.get_height()))

    display.flip()


def server_picker():
    global screen, host, port

    status_screen('Indexing servers', size, screen)

    with open('user_data/servers.json', 'r') as servers:
        server_dict = json.load(servers)

    server_list = []

    for server in server_dict:
        server_list.append([int(server), server_dict[server]['name'], server_dict[server]['host'], server_dict[server]['port'], '', 501])

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_queue = Queue()

    receiver = Process(target=receive_message, args=(message_queue, server))
    receiver.start()

    status_screen('Pinging servers', size, screen)

    for server_info in server_list:
        try:
            SERVERADDRESS = (server_info[2], int(server_info[3]))
            server.sendto(pickle.dumps([102, ]), SERVERADDRESS)

        except:
            pass

    rah.wallpaper(screen, size)

    connecting_text = rah.text("Updating servers...", 30)
    screen.blit(connecting_text,
                rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    clock = time.Clock()

    draw.rect(screen, (0, 0, 0), (size[0] // 4, size[1] // 2 + 50, size[0] // 2, 10))

    for check_cycle in range(500):

        draw.rect(screen, (0, 255, 0), (size[0] // 4, size[1] // 2 + 50, (size[0] // 2) * (check_cycle / 500), 10))
        display.flip()

        try:
            message = message_queue.get_nowait()

            if message[0] == 102:
                for server_info in server_list:
                    if server_info[2:4] == list(message[2:4]):
                        server_info[4] = message[1]
                        server_info[5] = check_cycle

        except:
            pass

        clock.tick(500)

    receiver.terminate()

    server_menu = menu.ScrollingMenu(server_list, 0, 0, size[0])

    button_list = [
        menu.Button((size[0] * 7) // 9 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'custom_server_picker',
                    'Direct Connect'),
        menu.Button(size[0] // 2 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'add_server', 'Add Server'),
        menu.Button((size[0] * 2) // 9 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'menu', 'Back')]

    y_offset = 50
    percent_visible = 0

    while True:

        rah.wallpaper(screen, size)

        release = False
        right_release = False

        for e in event.get():

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    release = True
                elif e.button == 3:
                    right_release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'server_picker'

            if e.type == MOUSEBUTTONDOWN:

                if e.button == 4:

                    y_offset += 40

                elif e.button == 5:

                    y_offset -= 40

            if e.type == KEYDOWN:
                if e.key == K_r:
                    return 'server_picker'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Scrolling menu----------------------------------------------------

        page_h = size[1] - 80

        button_h = 75

        if (button_h * len(server_list)) > page_h:
            if y_offset < -button_h * (len(server_list) + 1 - page_h // button_h):
                y_offset = -button_h * (len(server_list) + 1 - page_h // button_h)
            elif y_offset > 50:
                y_offset = 50
        else:
            y_offset = 50

        scroll_pos = int((y_offset / (-button_h * len(server_list))) * page_h)
        percent_visible = page_h / (len(server_list) * button_h)

        bar_rect = Rect(size[0] - 20, 0, 20, page_h)

        draw.rect(screen, (100, 100, 100), bar_rect)
        draw.rect(screen, (230, 230, 230), (size[0] - 18, scroll_pos, 14, (percent_visible * page_h)))

        if bar_rect.collidepoint(mx, my) and m_press[0] == 1:
            y_offset = int((my - (percent_visible * page_h) // 2) / page_h * -button_h * len(server_list))

        # ---------------------------------------------------------------------

        nav_update = server_menu.update(screen, release, right_release, mx, my, m_press, y_offset, size)

        if nav_update:
            if nav_update[0] == 'remove':

                server_update = json.load(open('user_data/servers.json'))

                for server in server_update:
                    if server_update[server]['name'] == nav_update[1] and server_update[server]['host'] == nav_update[
                        2] and server_update[server]['port'] == nav_update[3]:
                        destroy_index = server
                        break

                del server_update[destroy_index]

                with open('user_data/servers.json', 'w') as servers:
                    json.dump(server_update, servers, indent=4, sort_keys=True)

                return 'server_picker'

            elif nav_update[0] == 'remove fail':
                return 'information', "\n\n\n\n\nCouldn't delete server shortcut\nPermission denied", 'server_picker'

            else:
                host, port = nav_update[1], nav_update[2]
                return nav_update[0]

        server_bar = Surface((size[0], 80))
        server_bar.fill((200, 200, 200))
        server_bar.set_alpha(90)
        screen.blit(server_bar, (0, size[1] - 80))

        for button in button_list:
            nav_update = button.update(screen, mx, my, m_press, 15, release)

            if nav_update:
                return nav_update

        display.update()


def custom_server_picker():
    global host, port, screen

    rah.wallpaper(screen, size)

    buttons = [[0, 'game', "Connect"],
               [0, 'server_picker', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    field_selected = 'Host'

    field_list = ['Port', 'Host']

    fields = {'Host': [menu.TextBox(size[0] // 4, size[1] // 4, size[0] // 2, 40, 'Host'), host],
              'Port': [menu.TextBox(size[0] // 4, size[1] // 4 + 80, size[0] // 2, 40, 'Port'), port]}

    while True:

        release = False

        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                if e.key == K_RETURN and host and port:
                    host, port = fields['Host'][1], int(fields['Port'][1])
                    return 'game'

                if e.key == K_TAB:
                    field_list.insert(0, field_list[-1])
                    del field_list[-1]
                    field_selected = field_list[0]

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'custom_server_adder'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'game' and host and port:
                host, port = fields['Host'][1], int(fields['Port'][1])
                return nav_update

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and release:
                field_selected = field

        display.update()


def server_adder():
    global screen

    clock = time.Clock()

    rah.wallpaper(screen, size)

    buttons = [[0, 'server_picker', "Add"],
               [0, 'server_picker', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    name, host, port = '', '', None

    field_list = ['Name', 'Port', 'Host']

    field_selected = 'Name'

    fields = {'Name': [menu.TextBox(size[0] // 4, size[1] // 4, size[0] // 2, 40, 'Name'), name],
              'Host': [menu.TextBox(size[0] // 4, size[1] // 4 + 70, size[0] // 2, 40, 'Host'), host],
              'Port': [menu.TextBox(size[0] // 4, size[1] // 4 + 140, size[0] // 2, 40, 'Port'), port]}

    while True:

        release = False

        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                if e.key == K_RETURN and fields['Name'][1] and fields['Host'][1] and fields['Port'][1]:

                    if not fields['Port'][1].isdigit():
                        return 'information', "\n\n\n\n\nCouldn't add server\nInvalid entry for port", 'add_server'

                    server_update = json.load(open('user_data/servers.json'))

                    for server in server_update:
                        if server_update[server]['name'] == fields['Name'][1]:
                            return 'information', "\n\n\n\n\nCouldn't add server\nName conflicts with previous entry", 'add_server'

                    name, host, port = fields['Name'][1], fields['Host'][1], int(fields['Port'][1])

                    server_update.update({str(len(server_update)): {"name": name, "host": host, "port": port}})

                    with open('user_data/servers.json', 'w') as servers:
                        json.dump(server_update, servers, indent=4, sort_keys=True)

                    return 'server_picker'

                if e.key == K_TAB:
                    field_list.insert(0, field_list[-1])
                    del field_list[-1]
                    field_selected = field_list[0]

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'add_server'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'server_picker' and fields['Name'][1] and fields['Host'][1] and fields['Port'][1]:

                if not fields['Port'][1].is_digit():
                    return 'information', "\n\n\n\n\nCouldn't add server\nInvalid entry for port", 'add_server'

                server_update = json.load(open('user_data/servers.json'))

                for server in server_update:
                    if server_update[server]['name'] == fields['Name'][1]:
                        return 'information', "\n\n\n\n\nCouldn't add server\nName conflicts with previous entry", 'add_server'

                name, host, port = fields['Name'][1], fields['Host'][1], int(fields['Port'][1])

                server_update.update({str(len(server_update)): {"name": name, "host": host, "port": port}})

                with open('user_data/servers.json', 'w') as servers:
                    json.dump(server_update, servers, indent=4, sort_keys=True)

                return 'server_picker'

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and release:
                field_selected = field

        display.update()


def menu_screen():
    global current_version

    rotation = 10
    rotation_v = 1

    display.set_caption("RahCraft")

    global username, online, token, screen

    clock = time.Clock()

    menu_list = [[0, 'server_picker', "Connect to server"],
                 [1, 'options', "Options"],
                 [2, 'about', "About"],
                 [2, 'assistance', "Help"],
                 [3, 'exit', "Exit"],
                 [4, 'logout', "Logout"]]

    main_menu = menu.Menu(menu_list, 0, 0, size[0], size[1])

    with open('data/splashes.txt') as splashes:
        motd = choice(splashes.read().strip().split('\n'))

    logo = transform.scale(image.load("textures/menu/logo.png"), (size[0] // 3, int(size[0] // 3 * 51 / 301)))

    minecraft_font = font.Font("fonts/minecraft.ttf", 20)
    text_surface = minecraft_font.render(motd, True, (255, 255, 0))
    text_shadow = minecraft_font.render(motd, True, (0, 0, 0))

    shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
    shadow_surface.blit(text_shadow, (0, 0))
    shadow_surface.set_alpha(100)

    while True:

        rah.wallpaper(screen, size)

        text_surface_final = Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), SRCALPHA)

        screen.blit(logo, (size[0] // 2 - logo.get_width() // 2, size[1] // 2 - 120 - logo.get_height()))
        text_surface_final.blit(text_shadow, (2, 2))
        text_surface_final.blit(text_surface, (0, 0))

        rotation += rotation_v

        if rotation < 0 or rotation > 10:
            rotation_v *= -1

        text_surface_final = transform.rotate(text_surface_final, rotation)

        screen.blit(text_surface_final, (size[0] // 2 - text_surface_final.get_width() // 2 + 100, size[1] // 2 - 170))

        normal_font = font.Font("fonts/minecraft.ttf", 14)

        version_text = normal_font.render("RahCraft v%s" % current_build, True, (255, 255, 255))
        screen.blit(version_text, (10, size[1] - 20))

        about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
        screen.blit(about_text, (size[0] - about_text.get_width(), size[1] - 20))

        user_text = normal_font.render("Logged in as: %s" % username, True, (255, 255, 255))
        screen.blit(user_text, (20, 20))

        if online:
            user_text = normal_font.render("AUTH ID: %s" % token, True, (255, 255, 255))
            screen.blit(user_text, (20, 50))

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return 'login'

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'menu'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = main_menu.update(screen, release, mx, my, m_press)

        if nav_update:
            if nav_update == 'logout':
                username = ''
                token = ''

                with open('user_data/session.json', 'w') as session_file:
                    session_file.write('')

                return 'login'


            else:
                return nav_update

        display.update()


if __name__ == "__main__":

    size = (960, 540)
    screen = display.set_mode(size, DOUBLEBUF + RESIZABLE)

    display.set_caption("RahCraft")
    display.set_icon(transform.scale(image.load('textures/gui/icon.png'), (32, 32)))

    rah.rah_screen(screen)

    with open('data/ver.rah') as version_file:
        version_components = version_file.read().strip().split('\n')

    current_version, current_build = int(version_components[0]), version_components[1]

    host = "127.0.0.1"
    port = 5276

    mixer.pre_init(44100, -16, 1, 4096)
    init()

    online = False

    username = ''
    token = ''

    navigation = 'update'
    update_progress = 0

    font.init()

    click_cursor = ["      ..                ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX...             ",
                    "     .XX.XX...          ",
                    "     .XX.XX.XX.         ",
                    "     .XX.XX.XX...       ",
                    "     .XX.XX.XX.XX.      ",
                    "     .XX.XX.XX.XX.      ",
                    "...  .XX.XX.XX.XX.      ",
                    ".XX...XXXXXXXXXXX.      ",
                    ".XXXX.XXXXXXXXXXX.      ",
                    " .XXX.XXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "   .XXXXXXXXXXXXX.      ",
                    "    .XXXXXXXXXXX.       ",
                    "    .XXXXXXXXXXX.       ",
                    "     .XXXXXXXXX.        ",
                    "     .XXXXXXXXX.        ",
                    "     ...........        "]

    click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))
    mouse.set_cursor(*cursors.tri_left)

    UI = {'login': login,
          'menu': menu_screen,
          'about': about,
          'options': options,
          'assistance': assistance,
          'game': menu_screen,
          'server_picker': server_picker,
          'custom_server_picker': custom_server_picker,
          'add_server': server_adder,
          'information': information,
          'auth': authenticate,
          'reject': reject,
          'update': software_update,
          'death': death
          }

    music_object = mixer.Sound('sound/menu_music/menu.ogg')
    music_object.play(-1, 0)

    while navigation != 'exit':
        size = (screen.get_width(), screen.get_height())

        try:

            if navigation == 'game':
                music_object.stop()
                game_nav = Game.game(screen, username, token, host, port, size)

                navigation = game_nav

            elif navigation[0] == 'crash':
                navigation = crash(navigation[1], navigation[2])

            elif navigation[0] == 'information':
                navigation = information(navigation[1], navigation[2])

            elif navigation[0] == 'death':
                navigation = death(navigation[1])

            else:
                navigation = UI[navigation]()

        except:
            navigation = 'menu'
            crash(traceback.format_exc(), 'menu')

    mixer.music.stop()
    display.quit()
    raise SystemExit
