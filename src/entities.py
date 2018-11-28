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
        [{'LOWER': 'hal'}],
        [{'LOWER': 'harold'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'harold'}]
    ]},
    {'id':'OrinIncandenza', 'patterns': [
        [{'LOWER': 'orin'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'orin'}]
    ]},
    {'id':'AvrilIncandenza', 'patterns': [
        [{'LOWER': 'avril'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'avril'}, {'ORTH': 'I.'}],
        [{'LOWER': 'the'}, {'ORTH': 'Moms'}],
    ]},
    {'id':'JamesIncandenza', 'patterns': [ #Hal's father
        [{'ORTH': 'Himself'}],
        [{'ORTH': 'James'}, {'LOWER': 'incandenza'}],
        [{'ORTH': 'James'}, {'ORTH': 'O.'}, {'LOWER': 'incandenza'}],
    ]},
    {'id':'MarioIncandenza', 'patterns': [
        [{'LOWER': 'mario'}, {'LOWER': 'incandenza'}],
        [{'LOWER': 'mario'}],
        [{'ORTH': 'Booboo'}]
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
    {'id': 'Wardine', 'patterns': [
        [{'LOWER': 'wardine'}],
    ]},
    {'id': 'DoloresEpps', 'patterns': [
        [{'LOWER': 'dolores'}, {'LOWER': 'epps'}],
    ]},
    {'id': 'CharlesTavis', 'patterns': [
        [{'LOWER': 'uncle'}, {'LOWER': 'charles'}],
        [{'LOWER': 'charles'}, {'LOWER': 'tavis'}],
        [{'LOWER': 'tavis'}],
        [{'ORTH': 'C.T.'}],
        #[{'ORTH': 'Chuck'}], # too broad?
    ]},
    {'id': 'CoachWhite', 'patterns': [
        [{'LOWER': 'coach'}, {'LOWER': 'white'}],
        [{'LOWER': 'kirk'}, {'LOWER': 'white'}],
        [{'LOWER': 'kirk'}],
        [{'ORTH': 'White'}], # for section 4. too broad?
    ]},
    {'id': 'DoloresEpps', 'patterns': [
        [{'LOWER': 'dolores'}, {'LOWER': 'epps'}],
    ]},
    {'id': 'DirectorOfComposition', 'patterns': [
        [{'ORTH': 'Director'}, {'LOWER': 'of'}, {'ORTH': 'Composition'}],
        [{'ORTH': 'Dir'}, {'LOWER': 'of'}, {'ORTH': 'Comp'}],
        [{'ORTH': 'Director'}, {'LOWER': 'of'}, {'ORTH': 'Comp'}],
        [{'ORTH': 'Comp'}, {'ORTH': 'Director'}],
    ]},
    {'id': 'DeanOfAthleticAffairs', 'patterns': [
        [{'ORTH': 'Dean of Athletic Affairs'}],
        [{'ORTH': 'Athletic'}, {'ORTH': 'Affairs'}],
        [{'ORTH': 'Athletics'}]
        #[{'ORTH': 'bill'}], # too broad to use
    ]},
    {'id': 'DeanOfAcademicAffairs', 'patterns': [
        [{'ORTH': 'Dean of Academic Affairs'}],
        [{'ORTH': 'Academic'}, {'ORTH': 'Affairs'}],
        [{'ORTH': 'Dean'}, {'LOWER': 'at'}, {'LOWER': 'center'}],
        [{'LOWER': 'middle'}, {'ORTH': 'Dean'}],
        #[{'ORTH': 'bill'}], # too broad to use
    ]},
    {'id': 'DeanOfAdmissions', 'patterns': [
        [{'ORTH': 'Dean'}, {'LOWER': 'at'}, {'LOWER': 'left'}],
        [{'LOWER': 'yellow'}, {'LOWER': 'dean'}],
        [{'LOWER': 'dean'}, {'LOWER': 'sawyer'}],
    ]},
    {'id': 'AubreyDeLint', 'patterns': [
        [{'LOWER': 'mr'}, {'LOWER': 'a'}, {'ORTH': 'deLint'}], # Mr. A. deLint
        [{'LOWER': 'mr'}, {'ORTH': 'deLint'}], # Mr. deLint
        [{'LOWER': 'aubrey'}, {'LOWER': 'f'}, {'LOWER': 'delint'}],
        [{'LOWER': 'aubrey'}, {'LOWER': 'delint'}],
        [{'ORTH': 'Aubrey'}],
        [{'ORTH': 'deLint'}],
    ]},
    {'id': 'JohnWayne', 'patterns': [
        #[{'LOWER': 'john n. r. wayne'}],
        [{'ORTH': 'Wayne'}],
    ]},
    {'id': 'Stice', 'patterns': [
        [{'ORTH': 'Stice'}],
    ]},
    {'id': 'PetropolisKahn', 'patterns': [
        [{'ORTH': 'Petropolis'}, {'ORTH': 'Kahn'}],
    ]},
    {'id': 'Dymphna', 'patterns': [
        [{'ORTH': 'Dymphna'}],
    ]},
    {'id': 'CosgroveWatt', 'patterns': [
        [{'ORTH': 'Cosgrove'}, {'ORTH': 'Watt'}],
    ]},
    {'id': 'KenErdedy', 'patterns': [
        [{'ORTH': 'Erdedy'}],
    ]},
    {'id': 'MedicalAttache', 'patterns': [
        [{'LOWER': 'medical'}, {'LOWER': 'attache'}],
    ]},
    {'id': 'PrinceQ---------', 'patterns': [
        [{'ORTH': 'Prince'}, {'ORTH': 'Q---------'}],
        [{'LOWER': 'minister'}, {'LOWER': 'of'}, {'LOWER': 'home'}, {'LOWER': 'entertainment'}],
    ]},
    {'id': 'Reginald', 'patterns': [
        [{'ORTH': 'Reginald'}],
    ]},
    {'id': 'RoyTony', 'patterns': [
        [{'ORTH': 'Roy'}, {'ORTH': 'Tony'}],
    ]},
    {'id': 'ColumbusEpps', 'patterns': [# S10, killed 4 yrs ago by Roy Tony?
        [{'ORTH': 'Columbus'}, {'ORTH': 'Epps'}],
    ]},
    {'id': 'Clenette', 'patterns': [ #S10, 1st person narrator?
        [{'ORTH': 'Clenette'}],
    ]},
    {'id': 'BruceGreen', 'patterns': [ #S11
        [{'ORTH': 'Bruce'}, {'ORTH': 'Green'}],
    ]},
    {'id': 'MildredBonk', 'patterns': [ #S11
        [{'ORTH': 'Mildred'}, {'ORTH': 'Bonk'}],
        [{'ORTH': 'Mildred'}, {'ORTH': 'L.'}, {'ORTH': 'Bonk'}],
    ]},
    {'id': 'TommyDoocey', 'patterns': [ #S11 harelipped pot dealer
        [{'ORTH': 'Tommy'}, {'ORTH': 'Doocey'}],
    ]},
    {'id': 'DoloresRusk', 'patterns': [
        [{'ORTH': 'Dolores'}, {'ORTH': 'Rusk'}],
        [{'ORTH': 'Dr.'}, {'ORTH': 'Rusk'}],
    ]},
    {'id': 'MichaelPemulis', 'patterns': [
        [{'ORTH': 'Michael'}, {'ORTH': 'Pemulis'}],
        [{'ORTH': 'Pemulis'}],
    ]},
    {'id': 'JimStruck', 'patterns': [
        [{'ORTH': 'Jim'}, {'ORTH': 'Struck'}],
        [{'ORTH': 'James'}, {'ORTH': 'Struck'}],
        [{'ORTH': 'Struck'}],
    ]},
    {'id': 'BridgetBoone', 'patterns': [
        [{'ORTH': 'Bridget'}, {'ORTH': 'C.'}, {'ORTH': 'Boone'}],
        [{'ORTH': 'Boone'}],
    ]},
    {'id': 'JimTroeltsch', 'patterns': [
        [{'ORTH': 'Jim'}, {'ORTH': 'Troeltsch'}],
        [{'ORTH': 'Troeltsch'}],
    ]},
    {'id': 'TedSchacht', 'patterns': [
        [{'ORTH': 'Ted'}, {'ORTH': 'Schacht'}],
        [{'ORTH': 'Schacht'}],
    ]},
    {'id': 'TrevorAxford', 'patterns': [
        [{'ORTH': 'Trevor'}, {'ORTH': 'Axford'}],
        [{'ORTH': 'Axford'}],
    ]},
    {'id': 'KyleCoyle', 'patterns': [
        [{'ORTH': 'Kyle'}, {'ORTH': 'D.'}, {'ORTH': 'Coyle'}],
    ]},
    {'id': 'PaulShaw', 'patterns': [
        [{'ORTH': 'Paul'}, {'ORTH': 'Shaw'}],
    ]},
    {'id': 'FrannieUnwin', 'patterns': [
        [{'ORTH': 'Frannie'}, {'ORTH': 'Unwin'}],
    ]},
    {'id': 'BernadetteLongley', 'patterns': [
        [{'ORTH': 'Bernadette'}, {'ORTH': 'Longley'}],
    ]},
    {'id': 'KeithFreer', 'patterns': [
        [{'ORTH': 'Keith'}, {'ORTH': 'Freer'}],
        [{'ORTH': 'K.'}, {'ORTH': 'Freer'}],
    ]},
    {'id': 'OrthoStice', 'patterns': [
        [{'ORTH': 'Ortho'}, {'LOWER': "('the"}, {'LOWER': "darkness')"}],
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


