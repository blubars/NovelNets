import entities
import json

with open('entities.json', 'r') as f:
    entities = json.load(f)

dictified = {}
for e in entities:
    dictified[e['id']] = e['patterns']

with open('dictified_entities.json', 'w') as f:
    json.dump(dictified, f)
