import re
import os

#BOOK_SECTION_PATH = '/../books/infinite_jest/sections/'
#BOOK_ENDNOTE_PATH = '/../books/infinite_jest/endnotes/'

class TextIOReader:
    def __init__(self, section_path, endnote_path=None):
        self.section_path = section_path
        self.endnote_path = endnote_path

    def interpolate_section_endnotes(self, section_txt, exclusions=[]):
        basepath = self.endnote_path
        if basepath:
            pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>', re.MULTILINE)
            matches = re.finditer(pattern, section_txt)
            for match in matches:
                result = re.search(re.compile(r'[0-9]{1,3}'), match.group())
                value = result.group()
                if int(value) not in exclusions:
                    path = os.path.join(basepath, 'endnote-{0:0=3d}.txt'.format(int(value)))
                    with open(path, 'r') as f:
                        endnote = f.read()
                    # interpolate
                    section_txt = section_txt[:match.start()] + endnote + section_txt[match.end():]
            pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>')
            section_txt = re.sub(pattern, ' ', section_txt)
        return section_txt


    def interpolate_pov_name(self, section_id, name="Jack the Ripper"):
        section_txt = get_section(1, remove_endnote_tags=True)
        inner_pattern = r"(?:^I|^i|^me|^Me|^my|^My|^I'd|^i'd|^I'll|^i'll|^I've|^i've|^mine|^Mine)|\(?<=[^a-zA-Z])(?:I|i|me|Me|my|My|I'd|i'd|I'll|i'll|I've|i've|mine|Mine)(?=[^a-zA-Z])"
        outer_pattern = "(?:[“]{}[”])|(?:[‘]{}[’])".format(inner_pattern, inner_pattern)
        regex = re.compile(outer_pattern, re.MULTILINE)
        new_text = re.sub(regex, ' {} '.format(name), section_txt)
        return new_text


    def retrieve_section_endnotes(self, section_txt, exclusions=[]):
        basepath = os.path.dirname(os.path.realpath(__file__))
        pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>', re.MULTILINE)
        matches = re.finditer(pattern, section_txt)
        endnotes = {}
        for match in matches:
            result = re.search(re.compile(r'[0-9]{1,3}'), match.group())
            value = result.group()
            if int(value) not in exclusions:
                with open(basepath + self.endnote_path + 'endnote-{0:0=3d}.txt'.format(int(value)), 'r') as f:
                    endnote = f.read()
                    endnotes[int(value)] = endnote
        return endnotes


    def get_section(self, section_number, remove_endnote_tags=False):
        path = os.path.join(self.section_path, 'section-{0:0=3d}.txt'.format(int(section_number)))
        with open(path, 'r') as f:
            section = f.read()
            if remove_endnote_tags is True:
                pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>')
                section = re.sub(pattern, ' ', section)
        return section



if __name__ == '__main__':
    text = get_section(73)
    assert 112 not in list(retrieve_section_endnotes(text, [112]).keys())
    assert 112 in list(retrieve_section_endnotes(text, []).keys())
