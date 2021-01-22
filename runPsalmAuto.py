# import pdfgrep.pdfgrep as grep
import os
import pypdftk
import glob
import pdftotext
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import json
import shutil
import easygui

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

savePath = 'LordsDay'
if not os.path.exists(savePath):
    os.makedirs(savePath)

tmpDir = 'tmp'
if not os.path.exists(tmpDir):
    os.makedirs(tmpDir)


fileJson = easygui.fileopenbox()

f = open(fileJson)
# df = f.read()
# print(x)
df = json.loads(f.read())

## Read in and print sermon title etc
print(df["Sermon"])
print(df["Passage"])
print(df["Date"])
#TODO Automate Youtube thumbnail
if os.path.exists(savePath + "/" + df["Sermon"]):
    shutil.rmtree(savePath + "/" + df["Sermon"])
os.makedirs(savePath + "/" + df["Sermon"])

def findPageWithString_start(pdf,voi):
    for i in range(1,len(pdf)):
        page = pdf[i]
        # print(page)
        if voi in page:
            return i

def findPageWithString_end(pdf,voi):
    for i in range(1,len(pdf)):
        page = pdf[i]
        # print(page)
        if voi in page:
            #Determine if verse ends on page it starts on
            #last page
            if i+1 not in range(1,len(pdf)):
                return i
                #verse finishes on page
            if any(map(str.isdigit,pdf[i+1])):
                return i
                #verse continies over page
            else:
                return i+1



nPsalms = len(df["Psalms"])
pdf_writer = PdfFileWriter()

for i in range(nPsalms):
    psalm = df["Psalms"][i]
    fileSpec = "Psalms/" + psalm["book"] + "/*{ps_:03d}*{ver_}*.pdf".format(ps_ = psalm["number"],ver_ = psalm["version"])
    # print(fileSpec)

    files = glob.glob(fileSpec)
    # print(files)
    assert len(files) == 1,"{str} does not have exactly one matching file.:{filess}".format(str = fileSpec,filess = files)
    pdfFile = files[0]
    # print(pdfFile)
    with open(files[0], "rb") as f:
        pdf = pdftotext.PDF(f)
    # print(pdf[1])
    # continue
    verses = psalm["verses"].split(',')
    PageVec = [0]
    for j in range(len(verses)):
        if '-' in verses[j]:
            verRan = verses[j].split('-')
            assert(len(verRan))==2
            lv = verRan[0]
            uv = verRan[1]
            lp = findPageWithString_start(pdf,lv)
            up = findPageWithString_end(pdf,uv)
            PageVec += list(range(lp,up+1))
        elif len(verses[j]) == 0:
            lp = 1
            up = len(pdf)-1
            PageVec += list(range(lp,up+1))
        else:
            ver = verses[j]
            lp = findPageWithString_start(pdf,ver)
            up = findPageWithString_end(pdf,ver)
            # PageVec += list(range(pp,pp+1))
            PageVec += list(range(lp,up+1))


    # print(PageVec)
    # pdf_writer = PdfFileWriter()
    with open(pdfFile, "rb") as f:
        pdf_read = PdfFileReader(f)

        for pagenum in PageVec:
            pdf_writer.addPage(pdf_read.getPage(pagenum))
        # outFile = "tmp/out_{pnum:d}.pdf".format(pnum = i)
        outFile = savePath + "/" + df["Sermon"] + "/Psalms.pdf"
        with open(outFile,'wb') as out:
            pdf_writer.write(out) 
    
print("Finished")
print("YouTube Title")
print("{} - {} - {}".format(df["Date"],df["Passage"],df["Sermon"]))


font = ImageFont.truetype("Seravek.ttc",size = 65)
img = Image.open('wmark_text_drawn.jpg')
draw = ImageDraw.Draw(img)

msg = df["Date"]#" - "+df["Passage"]
w,h = draw.textsize(msg,font = font)
draw.text(((1920-w)/2,200),msg,(255,255,255),font = font)
msg = df["Passage"]
w,h = draw.textsize(msg,font = font)
draw.text(((1920-w)/2,300),msg,(255,255,255),font = font)
msg = df["Sermon"]
w,h = draw.textsize(msg,font = font)
draw.text(((1920-w)/2,400),msg,(255,255,255),font = font)

# draw.text((1920/2,500),df["Passage"],(255,255,255),font = font,align="right")
ytTitle = "{} - {}".format(df["Passage"],df["Sermon"])
img.save(savePath + "/" + df["Sermon"] +  "/" +"YT.jpg")