import re
import os


def interpolate_section_endnotes(section_txt, exclusions=[]):
    basepath = os.path.dirname(os.path.realpath(__file__))
    pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>', re.MULTILINE)
    matches = re.finditer(pattern, section_txt)
    for match in matches:
        result = re.search(re.compile(r'[0-9]{1,3}'), match.group())
        value = result.group()
        if int(value) not in exclusions:
            with open(basepath + '/../data/current/endnotes/infinite-jest-endnote-{0:0=3d}.txt'.format(int(value)), 'r') as f:
                endnote = f.read()
            # interpolate
            section_txt = section_txt[:match.start()] + endnote + section_txt[match.end():]
    pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>')
    section_txt = re.sub(pattern, ' ', section_txt)
    return section_txt


def retrieve_section_endnotes(section_txt, exclusions=[]):
    basepath = os.path.dirname(os.path.realpath(__file__))
    pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>', re.MULTILINE)
    matches = re.finditer(pattern, section_txt)
    endnotes = {}
    for match in matches:
        result = re.search(re.compile(r'[0-9]{1,3}'), match.group())
        value = result.group()
        if int(value) not in exclusions:
            with open(basepath + '/../data/current/endnotes/infinite-jest-endnote-{0:0=3d}.txt'.format(int(value)), 'r') as f:
                endnote = f.read()
                endnotes[int(value)] = endnote
    return endnotes


def get_section(section_number, remove_endnote_tags=False):
    basepath = os.path.dirname(os.path.realpath(__file__))
    with open(basepath + '/../data/current/sections/infinite-jest-section-{0:0=3d}.txt'.format(int(section_number)), 'r') as f:
        section = f.read()
        if remove_endnote_tags is True:
            pattern = re.compile(r'<endnote>[0-9]{1,3}</endnote>')
            section = re.sub(pattern, ' ', section)
    return section


if __name__ == '__main__':
    text = get_section(73)
    assert 112 not in list(retrieve_section_endnotes(text, [112]).keys())
    assert 112 in list(retrieve_section_endnotes(text, []).keys())

    print(get_section(73, remove_endnote_tags=True))
