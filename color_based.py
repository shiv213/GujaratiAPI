import pdfplumber
import json
from tqdm import tqdm

extracted = {}

with pdfplumber.open("guj-dict.pdf") as pdf:
    counter = 0
    last = 5
    word = ""
    ipa = ""
    graphemic_transcription = ""
    part_of_speech = ""
    gloss = ""
    # States:
    # 0 - Hitarth
    # 1 - IPA
    # 2 - Graphemic Transcription
    # 3 - Part of Speech
    # 4 - Gloss
    check_indices = []
    for x in tqdm(range(11, 236)):
        page = pdf.pages[x]
        for char in page.chars:
            if char['text'] != '' and char['size'] < 12.5 and char['fontname'] == "LPDJPP+HitarthGujPrachiNormal":
                if last != 0:
                    t = [word.strip(), ipa.strip(), graphemic_transcription.strip(),
                         part_of_speech.strip(), gloss.replace("<>", "").strip()]
                    if 1 <= t.count("") < 4:
                        if t[0] != "" and t[1] != "" and t[2] == "" and t[3] != "" and t[4] != "":
                            check_indices.append(counter)
                    if t[0] != "" and t[1] != "" and t[2] != "" and t[3] != "":
                        extracted[counter] = t
                        counter += 1
                    word = ""
                    ipa = ""
                    graphemic_transcription = ""
                    part_of_speech = ""
                    gloss = ""
                last = 0
                word += char['text']
            elif char['non_stroking_color'] == [1, 0, 0] and (
                    char['fontname'] == "LPDDKK+TimesNewRoman" or char['fontname'] == "LPDLOD+IPAPhonRoman"):
                last = 1
                ipa += char['text']
            elif char['non_stroking_color'] == [0, 0, 0] and char['fontname'] == "LPDLOD+IPAPhonRoman":
                last = 2
                graphemic_transcription += char['text']
            elif char['non_stroking_color'] == [0, 0.502, 0]:
                last = 3
                part_of_speech += char['text']
            elif char['non_stroking_color'] == [0, 0, 0] and (char['fontname'] == "LPDDKK+TimesNewRoman" or char['fontname'] == "LPDIJO+TimesNewRoman,Italic"):
                last = 4
                gloss += char['text']
print(len(extracted))
json_object = json.dumps(extracted, indent=4)
with open("data.json", "w") as outfile:
    outfile.write(json_object)
print(check_indices)
print(len(check_indices))
