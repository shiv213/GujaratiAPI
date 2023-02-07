from io import StringIO

import re
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import PyPDF2
import csv


def convert_pdf_to_string(file_path):
    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()


def convert_title_to_filename(title):
    filename = title.lower()
    filename = filename.replace(' ', '_')
    return filename


def split_to_title_and_pagenum(table_of_contents_entry):
    title_and_pagenum = table_of_contents_entry.strip()

    title = None
    pagenum = None

    if len(title_and_pagenum) > 0:
        if title_and_pagenum[-1].isdigit():
            i = -2
            while title_and_pagenum[i].isdigit():
                i -= 1

            title = title_and_pagenum[:i].strip()
            pagenum = int(title_and_pagenum[i:].strip())

    return title, pagenum


# x = convert_pdf_to_string("guj-engdictionary.pdf")


reader = PyPDF2.PdfFileReader('guj-dict.pdf')
print(reader.documentInfo)
db = {}
# for x in range(reader.numPages):
x = 14
text = ' '.join(reader.getPage(x).extractText().split()).split(" / / ")
for l in text:
    db[l.split(" ")[-1]] = l[:-len(l.split(" ")[-1])].split()
    # words.append(l.split(" ")[-1])

print(db)
num_of_pages = reader.numPages
print('Number of pages: ' + str(num_of_pages))
