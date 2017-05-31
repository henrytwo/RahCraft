
with open('tools.rah', 'r') as block_lookup:
    block_list = block_lookup.read().strip().split('\n')

block_list = [block.split(' // ') for block in block_list]

block_lookup = {block_list[i][0]: (i) for i in range(len(block_list))}

with open('tools.json','w') as block_json:

    block_json.write('{\n')

    for block in block_list:
        block_json.write('''
    	%s:{
		    "name":"%s",
	    	"texture":"%s",
        	"bonus":%s,
        	"speed":%s,
        	"type":"%s",
        '''%(block_list.index(block),block[0], block[1],block[2], block[3], block[4]))

        if block != block_list[-1]:
            block_json.write('},\n')
        else:
            block_json.write('}\n')

    block_json.write('\n}')
