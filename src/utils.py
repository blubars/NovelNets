import io
import os
import re
import glob
import errno


def get_sections_path():
    return '../data/current/sections/'

def get_entities_path():
    return '../data/entities.json'


def path_leaf(path):
    """ Get the file name from path (no extensions, just the name) """
    return os.path.splitext(os.path.basename(path))[0]


def pdfparser(input_path, output_path):
    """
    Convert .pdf file to text and save as .txt file
    """
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    file_name = path_leaf(input_path)
    fp = open(input_path, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data = retstr.getvalue()

    with open(output_path + '/' + file_name + ".txt", "w+") as f:
        f.write(data)


def split_pdf_into_pages(input_path, output_path, filename_leader="infinite-jest"):
    from PyPDF2 import PdfFileWriter, PdfFileReader
    inputpdf = PdfFileReader(open(input_path, "rb"))

    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(output_path + '/' + filename_leader + "-page-{}.pdf".format(i), "wb") as outputStream:
            output.write(outputStream)


def split_sections(filepath, output_path, split_on_string, filename_leader="infinite-jest"):
    with open(filepath, 'r') as f:
        data = f.read()
        sections = re.compile(split_on_string).split(data)
        print(len(sections))
    for i, section in enumerate(sections):
        with open(output_path + '/' + filename_leader + "-section-{0:0=3d}.txt".format(i + 1), "wb") as f:
            section = section.strip()
            f.write(section.encode())


def merge_txt_sections(directory_path, output_path, filename_leader="infinite-jest"):
    files = glob.glob(directory_path + '/*.txt')
    files.sort()
    print(files)
    with open(output_path + '/' + filename_leader + ".txt", 'w') as outfile:
        for fname in files:
            with open(fname) as infile:
                outfile.write('\n\n' + infile.read())


def append_section_breaks_to_sections(directory_path):
    files = glob.glob(directory_path + '/*.txt')
    for file in files:
        with open(file, "a") as f:
            f.write("\n\n<section></section>\n\n")


def get_section_text(path):
    sections = {}
    files = glob.glob(path)
    for file in files:
        try:
            with open(file, "r") as f:
                key = int(re.sub('[^0-9]', '', file))
                sections[key] = f.read()
        except IOError as exc:
            if exc.errno != errno.EISDIR:
                raise  # Propagate other kinds of IOError.
    return sections


def get_all_regex_matches(text, regex_pattern):
    # pattern = re.compile(r'.{0,20}(?=(\s<font(.*?)<a href="#[0-9]{1,3}))')
    pattern = re.compile(regex_pattern)
    matches = re.findall(pattern, text)
    cleanr = re.compile('<.*?>|>|<')
    matches = [re.sub(cleanr, '', m) for m in matches]
    return matches


def find_and_replace_endnotes():
    with open('../data/output.html') as f:
        data = f.read()
        f.close()
    matches = get_all_regex_matches(data, r'[\S\s]{1,30}(?=<font color(?:.*?)(?:<a href="#)(?:.*?)>(?:[0-9]{1,3})<)')
    matches = [m for m in matches if len(m) > 0]
    with open('../data/txt/Infinite Jest - Wallace, David Foster.txt') as f:
        text = f.read()
        f.close()
    for match in matches:
        index = text.find(match.replace('\n', ' '))
        if index != -1:
            start = index + len(match)
            chunk = text[start:start + 3]
            value = re.match(r'[0-9]{1,3}', chunk).group()
            new_chunk = re.sub(r'[0-9]{1,3}', '<endnote>' + value + '</endnote>', chunk)
            text = text[:start] + new_chunk + text[start + 3:]
    with open('infinite-jest-new.txt', 'w') as f:
        f.write(text)


def find_and_replace_sections():
    with open('../data/txt/infinite-jest-v2-0.txt') as f:
        data = f.read()
        f.close()
    matches = get_all_regex_matches(data, r'[\S\s]{1,30}(?=<section></section)')
    with open('./infinite-jest-new-endnotes.txt') as f:
        text = f.read()
        f.close()
    for match in matches:
        newmatch = re.sub(r'\n{1,3}', ' ', match).strip()
        newmatch = re.sub(r'[0-9]{1,3}', ' ', newmatch).strip()
        index = text.find(newmatch)
        if index != -1 and len(newmatch) > 10:
            idx = index + len(newmatch)
            text = text[:idx] + "\n\n<section></section>" + text[idx:]
        else:
            print(newmatch)
    with open('infinite-jest-new-sectioned-1.txt', 'w') as f:
        f.write(text)


def split_endnotes(filepath, output_path, regex, filename_leader="infinite-jest"):
    with open('../data/current/Infinite Jest-Notes.txt') as f:
        data = f.read()
        f.close()
    pattern = re.compile(regex, re.MULTILINE)
    matches = re.findall(pattern, data)
    for i, section in enumerate(matches):
        with open(output_path + '/' + filename_leader + "-endnote-{0:0=3d}.txt".format(i + 1), "wb") as f:
            section = section.strip()
            f.write(section.encode())
