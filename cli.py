import json, datetime, os


file = "inventory.json"
run = True
filterUsed = []
size = os.get_terminal_size().columns


helpText = "\
Commands:                             \n\
LS              - list all components \n\
CATS            - list all categories    \n\
ADD <cat> <val> - add filter by category & value \n\
RM <cat> <val>  - clear filter by category & value \n\
FILTERS         - list current filters \n\
CLR             - clear whole filter\n\
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

def getNum(txt):
    num = ""
    txt = txt.replace(">","").replace("<","").replace("~","")
    i = 0
    while i < len(txt) and txt[i].isdigit():
        num += txt[i]
        i += 1
    return int(num)

# count total component stocks
cpNum = 0
for cp in data:
    if "stock" in cp:
        if cp["stock"] == "a few":
            cpNum += 3
        else:
            cpNum += getNum(cp["stock"])
    else:
        cpNum += 3 # just add some standard number

# count total component types
types = []
for cp in data:
    if cp["component"] not in types:
        types.append(cp["component"])

# count total different components
diffCpNum = len(data)

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
                if cp[pair[0]].lower() == pair[1].lower():
                    found += 1
        if found == len(filterUsed):
            finalData.append(cp)
    selection = finalData

def getStrList(lst):
    i = 0
    finalText = ""
    while i < len(lst):
        line = ""
        while i < len(lst):
            newLine = line + ", " + lst[i]
            if len(newLine) < size-3:
                line = newLine
            else:
                break
            i += 1
        finalText += line[2:] + "\n"
    return finalText[:-1]


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
        
def removeFilter(category, value = ""):
    global filterUsed
    if value == "":
        i = 0
        while i < len(filterUsed):
            if filterUsed[i][0] == category:
                del filterUsed[i]
            else:
                i += 1
    else:
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
        if f[0] in keys:
            keys.remove(f[0])
            vals.remove(cp[f[0]])
    
    text = ""
    for i in range(len(vals)):
        text += str(keys[i]) + ":" + str(vals[i])
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

welcome = "\
\033[0;37;48m---------------------------------------------\n\
\033[1;31;40mWELCOME TO YOUR COMPONENTS\033[0;37;48m\n\
\033[1;31;40mBrowse {} components ({} different types) in {} categories:\033[0;37;48m\n\
{}\n\
---------------------------------------------\n\
Enter 'help' for ideas".format(cpNum,diffCpNum, len(categories), getStrList(types))

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
        for i in range(2,len(cmdText)):
            cmdText[i] = cmdText[i].replace("-", " ")
        cmd(*cmdText[1::])
    except TypeError as t:
        print("Wrong argument count:", t)