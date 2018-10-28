from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io
import os
import re


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
        sections = re.compile("[\r\n]{3,}").split(data)
    for i, section in enumerate(sections):
        with open(output_path + '/' + filename_leader + "-section-{}.txt".format(i), "wb") as f:
            f.write(section.encode())


if __name__ == "__main__":
    # split_pdf_into_pages("./data/pdf/infinite-jest.pdf", "./data/pdf")
    # pdfparser("./data/pdf/infinite-jest-page-1.pdf", './data/txt')
    split_sections("./data/txt/infinite-jest.txt", './data/txt', filename_leader="infinite-jest")