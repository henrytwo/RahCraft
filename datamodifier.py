"""
with open('data/block.rah', 'r') as block_lookup:
    block_list = block_lookup.read().strip().split('\n')

block_list = [block.split(' // ') for block in block_list]

block_lookup = {block_list[i][0]: (i) for i in range(len(block_list))}

with open('data/block.json','w') as block_json:

    block_json.write('{\n')

    for block in block_list:
        block_json.write('''
    "%s"{
        "texture":"%s"
        "icon":"%s"
        "collison":"%s"
        "sound":"%s"
        "hardness":"%s"
    }\n
        '''%(block[0], block[3],block[3], block[6], block[5], block[4]))

    block_json.write('\n}')



"""
with open('data/block.json','r+') as block_json:

    while True:
        name = input("Name: ")
        icon = input("Texture: ")
        sound = input("Sound: ")
        hardness = input("Hardness: ")
        collision = input("Collision <N>: ")

        if not collision:
            collision = 'pass'

        block = [name, icon, icon, collision, sound, hardness]

    block_json.write('{\n')

    for block in block_list:
        block_json.write('''
    "%s"{
        "texture":"%s"
        "icon":"%s"
        "collison":"%s"
        "sound":"%s"
        "hardness":"%s"
    }\n
        '''%(block[0], block[3],block[3], block[4], block[5], block[6]))

    block_json.writ



