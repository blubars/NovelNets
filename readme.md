# Analyze Books as Networks
This tool processes a book and outputs a network!

Nodes are the book's characters, and edges are weighted interactions between the characters.

The network is saved as snapshots per chapter/section, so you can see how the book's character network changes as the book progresses!

## Usage
Input a book. Output a network!
Infinite Jest is included as an example.

    python3 src/main.py -t "Infinite Jest"

The code will run through the following steps:
1. **Preprocessing**: split text into sections [TODO]
    * for now, you must provide a directory with the book already split into sections
2. **Named Entity Recognition (NER)**:
    * Launches an interactive named entity session. Spacy is used to identify likely characters, then prompts you to confirm and resolve any aliases where it is uncertain.
    * Known character entities are stored in a entities.json file, so this step only has to be run once.
3. **Graphify**: section texts and known entities are used to identify character interactions by section! 
4. **Analysis** [optional]: analysis and algorithms can be run on the final NetworkX graph.
    * Example analysis was done for Infinite Jest, and is included in src/ directory
5. **Visualization**: the final graph is shown using webweb for you to play with!

### More Usage Examples

```bash
# Book already pre-processed. 
# preprocess & output dirs would be inferred from title:
#   - sections looked for in ./preprocess/infinite-jest/sections/
#   - NER saved in ./preprocess/infinite-jest/ner/
#   - graph output saved in ./graphs/infinite-jest/

python3 src/main.py -t "Infinite Jest"
```

```bash
# specify pre-process directory (with sections)
# specify output directory

python3 src/main.py -t "Infinite Jest" -p preprocess/infinite-jest -s output_dir
```

## Dependencies
1. [Webweb](https://webwebpage.github.io/) is used for the graph visualization: 

```bash
pip install webweb
```

2. [Spacy](https://spacy.io/) is used for NLP processing of the book:

```bash
pip install spacy
python3 -m spacy download en_core_web_md
```

3. [NetworkX](https://networkx.github.io/) is used for internal graph representation and analysis.

```bash
pip install networkx
```

## Infinite Jest Nets Analysis
Analysis was done on David Foster Wallace's <i>Infinite Jest</i>
### Static-Network Analysis:
1. small-world property
1. Centralities
2. Assortativities
3. Modularity:
   * community structure (greedy agg), Normalized Mutual Information
   * assortativity: degree, gender, association.
3. ccdf of degree distribution, time vs degree: preferential attachment? probably not...

### Dynamic-Network Analysis:
1. changepoint detection
   * need function to determine changepoint
   * statistics to feed function: all centralities, diam or avg geodesic, num triangles, avg degree 
2. attachment: sparsification vs densification
3. temporal analysis:
     - how long do edges last?
     * how does structure vary over time?
        - vary aggregation window
     * how stable are local neighborhoods?
        - compute adjacenty correlation over time.
     - how does discrete time impact our measurements?
        - perhaps try varying definition of discrete time: sections/pages/tokens

### Other:
- Coreference resolution
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

[data](https://raisuman123.files.wordpress.com/2013/05/david-foster-wallace-infinite-jest-v2-0.pdf)
