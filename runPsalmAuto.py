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

from fpdf import FPDF

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
    if 'b' in voi:
        bflag = 1
        voi = voi.strip("b")
    else:
        bflag = 0

    for i in range(1,len(pdf)):
        page = pdf[i]
        # print(page)
        if voi in page:
            return i + bflag

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
        if "am" in df["Date"].lower():
            pdfName = "AM"
        elif "pm" in df["Date"].lower():
            pdfName = "PM"
        else:
            pdfName = "Psalms"



        outFile = savePath + "/" + df["Sermon"] + "/"+ pdfName +".pdf"
        with open(outFile,'wb') as out:
            pdf_writer.write(out) 
    
print("Finished")
print("YouTube Title")
print("{} - {} - {}".format(df["Date"],df["Passage"],df["Sermon"]))

with open(savePath + "/" + df["Sermon"] + "/"+ "YT-Title.txt","w") as f:
    f.write("{} - {} - {}".format(df["Date"],df["Passage"],df["Sermon"]))



font = ImageFont.truetype("Seravek.ttc",size = 65)
# font = ImageFont.truetype("impact.ttf",size = 65)

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
img.save(savePath + "/" + df["Sermon"] +  "/" +"YT-Thumbnail.jpg")


with open(savePath + "/" + df["Sermon"] +  "/" +"Precentor.txt","w") as f:
    tod = "morning" if "am" in df["Date"].lower() else "afternoon" if "pm" in df["Date"].lower() else "service"
    f.write("Dear ..., the psalms for the {} are:\n".format(tod))
    for i in range(len(df["Psalms"])):
        f.write("Psalm {num}:{verses}\n".format(num=df["Psalms"][i]["number"],verses=df["Psalms"][i]["verses"]))

if "Outline" in df.keys() and "Reading" in df.keys():
    pdf = FPDF(format = 'A5')
    pdf.add_page()
    pdf.set_font("Arial",size = 15)
    print("OUTILNE AVAILABLE")
    #print Passage to PDF
    print(df["Passage"])
    pdf.cell(200, 10, txt = "GeeksforGeeks", ln = 1, align = 'C') 

    #print Sermon title to PDF
    print(df["Sermon"])
    # 
    # Print Reading for
    for i in range(len(df["Reading"])): print(df["Reading"][i])
    # Print Psalms for
    for i in range(len(df["Psalms"])): 
        print("{Ps}{version}:{verses}, {book}".format(Ps = df["Psalms"][i]["number"],version = df["Psalms"][i]["version"],verses = df["Psalms"][i]["verses"],book = df["Psalms"][i]["book"]))


    # Print Outline points for
    for i in range(len(df["Outline"])): print("{}. {}".format(i+1,df["Outline"][i]))

    pdf.output("GFG.pdf")   