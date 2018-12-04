# Infinite Jest Nets

# WebWeb Install
Please follow the instructions for installing webweb locally via a git repo:
https://github.com/hneutr/webweb

# Todo:
    - Coreference resolution
    - start adding entity attributes
    - CENTRAL QUESTIONS:
      - why is the book structured this way?
      - does the graph's structure reflect common knowledge about the book?
          - e.g. criticisms: gender power imbalance
    - ANALYSIS to address above questions:
      - Centralities: main characters
      - Assortativity: degree, gender, age
          - modularity: community structures
      - Dynamics: 
          - graph avg degree vs mean geodesic path per section
            - compare chronological vs authored order
          - compare dynamics across different windows & smoothing?
      - momentum -- what causes it?

# Done!
- find entities by section:
    - run graphify for a given section (1-192)
        - brian: 1-50
        - hunter: 51-100
        - carl: 101-150
    - entity tool:
        - for unfound entities, ask if it's in list
            - if yes, use #
            - if not, type name
- text_io,py:
    - import section by id with option to remove endnote tags
    - function to interpolate endnote text into section text with option to exclude endnotes by ID.
      - this will remove endnote tags for any exlcuded endnotes not interpolated into text.
    - function to retrieve endnotes as a dictionary of ID:endnote_text key values. Option to exclude 
      if so desired.

[data](https://raisuman123.files.wordpress.com/2013/05/david-foster-wallace-infinite-jest-v2-0.pdf)
