# Infinite Jest Nets

# WebWeb Install
Please follow the instructions for installing webweb locally via a git repo:
https://github.com/hneutr/webweb

# Todo:
## Static-Network Analysis:
1. small-world property (meh, used in dynamic analysis)
2. modularity: 
    a. community structure (greedy agg), Normalized Mutual Information
    b. assortativity: degree, gender, association.
3. ccdf of degree distribution, time vs degree: preferential attachment? probably not...

## Dynamic-Network Analysis:
1. changepoint detection
   a. need function to determine changepoint
   b. statistics to feed function: all centralities, diam or avg geodesic, num triangles, avg degree 
2. attachment: sparsification vs densification
3. temporal analysis:
     - how long do edges last?
     * how does structure vary over time?
        - vary aggregation window
     * how stable are local neighborhoods?
        - compute adjacenty correlation over time.
     - how does discrete time impact our measurements?
        - perhaps try varying definition of discrete time: sections/pages/tokens

## Other:
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
Analyses:
  Static:
    1. Centralities
    2. Assortativities
    3. Modularity
  Dynamic:

[data](https://raisuman123.files.wordpress.com/2013/05/david-foster-wallace-infinite-jest-v2-0.pdf)
