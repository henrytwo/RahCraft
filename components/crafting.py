# with open("crafting","r") as crafting:
crafting_lookup = {"[[1, 2, 3], [4, 5, 6], [7, 8, 9]]": 12}


def craft(crafting_input):
    if str(crafting_input) in crafting_lookup:
        return crafting_lookup[str(crafting_input)]


while True:
    print(craft([list(map(int, row.split(","))) for row in input("Crafting >>> ").split("//")]))
