#RAHCRAFT
#COPYRIGHT 2017 (C) RAHMISH EMPIRE, MINISTRY OF RAHCRAFT DEVELOPMENT
#DEVELOPED BY RYAN ZHANG, HENRY TU, SYED SAFWAAN

#installer.py

import traceback
from urllib.request import urlretrieve, Request, urlopen
import zipfile
import os
import glob
from shutil import copyfile, copy2, rmtree
import subprocess
import platform

if platform.system() == 'Windows':
    p = subprocess.Popen('pip.bash', shell=True, stdout=subprocess.PIPE)

else:
    subprocess.call(['pip.sh'])


#Copy a directory for software updates
#Courtesy of:
#https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(src, dst, symlinks=False, ignore=None):

    #If the directory doesn't exist, make it
    if not os.path.exists(dst):
        os.makedirs(dst)

    #Copy all folders int he directory
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        #If it is another directory
        if os.path.isdir(s):

            #Run the function recursively
            copytree(s, d, symlinks, ignore)
        else:
            #Copy the file
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                copy2(s, d)

#Get progress of a file downloaded from the internet
#Courtesy of:
#http://www.dreamincode.net/forums/topic/258621-console-progress-for-download-over-http/
def progress(block_no, block_size, file_size):

    global update_progress #Using a global variable to keep track of progress easier

    update_progress += block_size #Updates var with amount of file downloaded

    print("Downloading.... [%s%% (%iMB/%iMB)]"%(int(update_progress/file_size * 100), round(update_progress/1000000, 2), round(file_size/1000000, 2)))

#Function for updating the game software
def software_update():
    global screen, size, update_progress #Global variables to make modifying values easier

    #Try to connect to update server
    try:
        #Reads a text file on website to look for latest version
        req = Request('https://rahcraft.github.io/rahcraft.txt', headers={'User-Agent': 'Mozilla/5.0'})

        #Splits the file into its components
        with urlopen(req) as response:
            extracted_file = str(response.read())[2:][:-3].split('\\n')

        latest_version = int(extracted_file[0])
        latest_build = extracted_file[1]
        update_location = extracted_file[2]

        print('Download RahCraft v%s? [Y/n]: '%latest_build)

        #Proceed with update
        if input() == 'y':

            # Deletes any existing update files to prevent conflict
            if os.path.exists('update.zip'):
                os.remove("update.zip")

            if os.path.exists('update'):
                rmtree("update")

            #Downloads the latest version of the game while calling the progress function so progress is kept track
            urlretrieve(url=update_location, filename='update.zip', reporthook=progress)

            #Extracts the update in root project directory
            with zipfile.ZipFile('update.zip','r') as zip_file:
                zip_file.extractall('update')

            #Deletes the zip to save space
            os.remove("update.zip")

            #Indexes folder for directories and files
            dir_list = glob.glob('update/*/*')

            #Iterates through each directory
            for dir in dir_list:
                file_name = dir.split('/')[-1] #Gets the last portion of full file location (file name)

                #Checks if file name contains a period, indicating it is a file not directory
                if len(file_name.split('.')) == 2:
                    copyfile(dir, file_name) #Copies file with function
                else:
                    copytree(dir, file_name) #Copies directory with function

            rmtree("update") #Deletes the update directory to save space

            #Updates version variables
            current_build, current_version = latest_build, latest_version

            #Updates version file
            with open('CLIENT/data/ver.rah', 'w') as version_file:
                version_file.write('%s\n%s'%(current_version, current_build))

            print('RahCraft downloaded successfully')

        #Exit the program
        else:
            print('Download cancelled')
            return ''


    except:
        #If something went wrong and update could not be completed
        print('Something went wrong...\n'+traceback.format_exc())

if __name__ == '__main__':
    size = 0
    update_progress = 0

    software_update()

    raise SystemExit
