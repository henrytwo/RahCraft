
with open('session.rah', 'r') as block_lookup:
    block_list = block_lookup.read().strip().split('\n')

#block_lookup = {block_list[i][0]: (i) for i in range(len(block_list))}

print(block_list)

with open('session.json','w') as block_json:

        block_json.write('''
{
    "token":"%s",
    "name":"%s"
}'''%(block_list[0], block_list[1]))

