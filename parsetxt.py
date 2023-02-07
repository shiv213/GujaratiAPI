import json

dict_data = {}
i = 500
temp = ""
l = []
with open('guj-dict.txt') as f:
    for line in f:
        print(repr(line))
        if len(l) == 0:
            temp = ""
        if line == "\n" and len(l) > 0:
            # print(l)
            fl = []
            fl.append(l[1:])
            fl.append(temp.strip())
            dict_data[l[0]] = fl
            temp = ""
        elif line.__contains__("/\\"):
            l = line.strip("\n").split()[:4]
            temp += ' '.join(line.strip("\n").split()[4:])
            temp += " "
        else:
            temp += line.strip("\n") + " "
        if i == 0:
            break
        i -= 1

print(dict_data)

json_data = json.dumps(dict_data)
with open('json_data.json', 'w') as outfile:
    json.dump(json_data, outfile)
