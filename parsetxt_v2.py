import json

dict_data = {}
i = 499
temp = ""
l = []
with open('guj-dict.txt') as f:
    for line in f:
        if line.__contains__("/\\"):
            if len(l) < 4 and len(temp) > 0:
                l += temp.split()[:4 - len(l)]
                temp = ' '.join(temp.split()[5 - len(l):])

            if len(l) > 4:
                temp += " " + ' '.join(l[4:]) + " "

            if len(l) >= 4 and len(temp) > 0:
                temp.replace("  ", " ")
                temp += " " + ' '.join(l[4:])
                print(l[:4])
                print(temp)
                dict_data[l[0]] = temp
                temp = ""
                l = []
            l += line.strip("\n").split()
        else:
            temp += line.replace("\n", " ")
        if i == 0:
            break
        i -= 1

print(dict_data)

json_data = json.dumps(dict_data).replace("\\", "")
with open('json_data.json', 'w') as outfile:
    json.dump(json_data, outfile)
