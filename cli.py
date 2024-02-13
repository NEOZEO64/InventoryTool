import json, datetime, os
  


file = "inventory.json"
run = True
filterUsed = []
size = os.get_terminal_size().columns

welcome = "\033[0;37;48m---------------------------------------------\n\033[1;31;40mWELCOME TO YOUR COMPONENTS\033[0;37;48m\n---------------------------------------------\nEnter 'help' for ideas"
helpText = "\
Commands:                             \n\
LS              - list all components \n\
CATS            - list all categories    \n\
ADD <cat> <val> - add filter by category & value \n\
RM <cat> <val>  - clear filter by category & value \n\
FILTERS         - list current filters \n\
CLR             - clear whole filter\n\
SLC <num>       - select component by number in list\n\
help            - print this text\n\
stop            - exit the program & save \n\
save            - save \n\
"

# LOAD data
with open(file, "r") as read_file:
    data = json.load(read_file) # data is now a dictionary containing EVERYTHING

categories = {}
for cp in data:
    for k in cp.keys():
        if k not in categories.keys():
            categories[k] = 1
        else:
            categories[k] += 1
categories = dict(sorted(categories.items(), key=lambda item: item[1], reverse=True)) # sort categories

# Tool functions
def printNormal():
    print("\033[0;37;48m",end="")

def printHighlight():
    print("\033[1;31;40m",end="")

def save():
    with open("file.json", "w") as write_file:
        json.dump(data, write_file)

def help():
    print(helpText)

def quit():
    global run
    run = False

def getTimeStr():
    now = datetime.datetime.now()
    text = now.strftime("%d.%m.%y, %H:%M")
    return text

def getCategories():
    text = ""
    for c in categories:
        text += c 
        text += "  "
    print(text)

def filterData():
    global data, selection
    finalData = []
    for cp in data:
        found = 0
        for pair in filterUsed:
            if pair[0] in cp.keys():
                if cp[pair[0]] == pair[1]:
                    found += 1
        if found == len(filterUsed):
            finalData.append(cp)
    selection = finalData

def addFilter(category, value):
    global filterUsed, selection
    if category not in categories:
        print("category does not exist")
        return

    filterUsed.append([category,value.lower()])

    selectionCopy = selection
    filterData()
    if selection == []:
        filterUsed.remove([category,value.lower()])
        selection = selectionCopy
        print("no resulting items")
        
def removeFilter(category, value):
    global filterUsed
    filterUsed.remove([category,value.lower()])
    filterData()

def listFilters():
    for f in filterUsed:
        print("{} == {}".format(*f))

def printComponent(i):
    global selection
    text = ""
    cp = selection[i]
    keys = list(cp.keys())
    vals = list(cp.values())
    if "comment" in keys: # put the "comment" column to the right
        iComment = keys.index("comment")
        keys[-1], keys[iComment] = keys[iComment], keys[-1]
        vals[-1], vals[iComment] = vals[iComment], vals[-1]
    for f in filterUsed: # hide all the obvious columns that is filtered after
        if f[1] in vals:
            vals.remove(f[1])
    
    text = ""
    for v in vals:
        text += str(v)
        text += "\t"
    if len(text) > size:
        text = text[:size]
    print(text)

def listSelection():
    for i in range(len(selection)):
        printComponent(i)
    print("Shows {} results".format(len(selection)))



cmdMap = {
    "help" : help,
    "stop" : quit,
    "exit" : quit,
    "quit" : quit,
    "q" : quit,
    "cats": getCategories,
    "add": addFilter,
    "rm": removeFilter,
    "ls": listSelection,
    "filters" : listFilters
}

selection = data

printNormal()
print()
print(welcome)
while run:
    printHighlight()
    cmdText = input(">").lower().split(" ")
    printNormal()
    try:
        cmd = cmdMap[cmdText[0]]
    except KeyError:
        print("Command not found")
        continue
    try:
        cmd(*cmdText[1::])
    except TypeError as t:
        print("Wrong argument count:", t)