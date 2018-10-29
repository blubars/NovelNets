import spacy

nlp = spacy.load('en_core_web_md')
doc = nlp(u"displaCy uses JavaScript, SVG and CSS.")
spacy.displacy.serve(doc, style='dep')

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)