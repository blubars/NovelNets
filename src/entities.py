import spacy
from spacy.matcher import Matcher

# hand-made patterns and maybe future methods to make patterns 
# automatically

# docs: https://spacy.io/usage/linguistic-features#rule-based-matching

# format: id, list of patterns (each pattern is a list of dicts)
people = [
#    id:'HelloWorld', patterns: [
#        [{'LOWER': 'hello'}, {'IS_PUNCT': True}, {'LOWER': 'world'}],
#        [{'LOWER': 'hello'}, {'LOWER': 'world'}])
#    ],
    {'id':'HalIncandenza', 'patterns': [
        [{'LOWER': 'hal'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'hal'}]
    ]},
    {'id':'OrinIncandenza', 'patterns': [
        [{'LOWER': 'orin'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'orin'}]
    ]},
    {'id':'MarioIncandenza', 'patterns': [
        [{'LOWER': 'mario'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'mario'}]
    ]},
    {'id':'HaroldIncandenza', 'patterns': [
        [{'LOWER': 'harold'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'harold'}]
    ]},
    {'id':'MauryKlamkin', 'patterns': [
        [{'LOWER': 'maury'}, {'LOWER': 'klamkin'}],
        [{'LOWER': 'maury'}],
        [{'LOWER': 'klamkin'}]
    ]},
    {'id':'Schtitt', 'patterns': [
        [{'LOWER': 'gerhardt'}, {'LOWER': 'schtitt'}],
        [{'LOWER': 'schtitt'}],
    ]},
    {'id':'DeanSawyer', 'patterns': [
        [{'LOWER': 'dean'}, {'LOWER': 'sawyer'}],
    ]},
    {'id':'JoelleVanDyne', 'patterns': [
        [{'LOWER': 'joelle'}, {'LOWER': 'van'}, {'LOWER': 'dyne'}],
        [{'LOWER': 'joelle'}],
    ]},
    {'id':'DonaldGately', 'patterns': [
        [{'LOWER': 'donald'}, {'LOWER': 'gately'}],
        [{'LOWER': 'donald'}], 
    ]},
    {'id':'RandyLenz', 'patterns': [
        [{'LOWER': 'randy'}, {'LOWER': 'lenz'}],
        [{'LOWER': 'randy'}],
        [{'LOWER': 'lenz'}]
    ]},
]

def get_matcher(nlp):
    matcher = Matcher(nlp.vocab)
    # TODO: how do we do this in an automated fashion?
    #  ...or all by hand i guess.
    load_patterns(matcher)
    return matcher

def on_match(matcher, doc, i, matches):
    # callback when entity pattern matched
    # unused.
    pass

def load_patterns(matcher):
    # possible automated method:
    #nlp = spacy.load('en_core_web_sm')
    #matcher = PhraseMatcher(nlp.vocab)
    #terminology_list = ['Barack Obama', 'Angela Merkel', 'Washington, D.C.']
    #patterns = [nlp(text) for text in terminology_list]
    #matcher.add('TerminologyList', None, *patterns)

    # load from above hand-made patterns
    for p in people:
        matcher.add(p['id'], None, *p['patterns'])
