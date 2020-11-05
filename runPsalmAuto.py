# import pdfgrep.pdfgrep as grep
import os
import pypdftk
import glob
import pdftotext
import os

book = "16x9_b_w_underlined/Sing Psalms"
psalm = 8
verse = [1,6]
strr = "{book_}/*{ps_:03d}*.pdf".format(book_ = book,ps_ = psalm)

files = glob.glob(strr)

assert len(files) == 1

# gen = grep.do_grep(files[0],'[a]',ignore_case = True)
# outputs = [output for output in gen]
# print(outputs)

# Load your PDF
with open(files[0], "rb") as f:
    pdf = pdftotext.PDF(f)

# How many pages?
print(len(pdf))

for j in range(2):
    # Iterate over all the pages
    voi = "{ver:d}".format(ver = verse[j])
    for i in range(len(pdf)):
        page = pdf[i]
        # print(page)
        if voi in page:
            print(f"verse {verse[j]:d} is on page {i+1:d}")
            # print(page)
            break