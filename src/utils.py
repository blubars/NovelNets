from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io
import os
import re
import glob
import errno


def path_leaf(path):
    """
    Get the file name from path (no extensions, just the name)
    """
    return os.path.splitext(os.path.basename(path))[0]


def pdfparser(input_path, output_path):
    """
    Convert .pdf file to text and save as .txt file
    """
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
    inputpdf = PdfFileReader(open(input_path, "rb"))

    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(output_path + '/' + filename_leader + "-page-{}.pdf".format(i), "wb") as outputStream:
            output.write(outputStream)


def split_sections(filepath, output_path, filename_leader="infinite-jest"):
    with open(filepath, 'r', encoding="ISO-8859-1") as f:
        data = f.read()
        sections = re.compile("<section></section>").split(data)
        print(len(sections))
    for i, section in enumerate(sections):
        with open(output_path + '/' + filename_leader + "-section-{0:0=3d}.txt".format(i + 1), "wb") as f:
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


if __name__ == "__main__":
    split_sections("../data/txt/infinite-jest-v2-0.txt", "../data/txt/split_sections/", filename_leader="infinite-jest")