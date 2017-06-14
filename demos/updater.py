import urllib.request
import traceback

current_version = 0

try:
    req = urllib.request.Request('http://henrytu.me/rahcraft.txt', headers={'User-Agent': 'Mozilla/5.0'})

    with urllib.request.urlopen(req) as response:
        extracted_file = str(response.read())[2:][:-3].split('\\n')

    latest_version = int(extracted_file[0])
    update_location = extracted_file[1]

    if current_version < latest_version:
        #<Prompt that new update is available>
        print('An update is available')

        #<Ask user if they want to update>

        update = int(input('>'))

        if update:
            print('Downloading update')
            with urllib.request.urlopen(update_location) as update_file, open('update.zip', 'wb') as out_file:
                out_file.write(update_file.read())

            print('Download completed')


except:
    print('Unable to update :/')
    print(traceback.format_exc())