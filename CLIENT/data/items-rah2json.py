with open('items.rah', 'r') as item_lookup:
    items = item_lookup.read().strip().split('\n')

item_list = [item.split(' // ') for item in items]

item_lookup = {item_list[i][0]: (i,) for i in range(len(item_list))}

with open('item.json', 'w') as item_json:
    item_json.write('{\n')

    for item in item_list:
        item_json.write('''
    	%s:{
		    "name":"%s",
        	"icon":"%s",
        	"maxstack":%s
        ''' % (str(item_list.index(item) + 400), item[0], item[1], item[2]))

        if item != item_list[-1]:
            item_json.write('},\n')
        else:
            item_json.write('}\n')

    item_json.write('\n}')

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
"""
