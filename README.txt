# SYmpLE
A syntactic and lexical sentence simplification tool based on dependency trees and WordNet for English.
Initially this is a tool to simplify the process of Information Extraction.

For syntactic simplification, the algorithm is similar to DEPSYM from (Chatterjee, 2021) with modifications related to the final research goal.
The dependency parsing is done with the multilingual parser MultiCOMBO: https://github.com/KoichiYasuoka/MultiCOMBO

The lexical simplification is based on the number of occurrences of a word in a particular sense. The source of the word frequencies is Wikipedia.
The word senses were extracted from randomly sampled pages, their occurrences counted.
This version simplifies only verbs. The reason behind it is that relation triples extraction requires a limited number of possible relations, but needs to preserve the initial meaning (as it changes even among synonyms).

Total (synset_word_counts.txt)
Pages: 10000
Word senses: 66342

Total (synset_verb_counts.txt)
Pages: 16200
Verbs: 18297


Citations:
Chatterjee, Niladri & Agarwal, Raksha. (2021).
DEPSYM: A Lightweight Syntactic Text Simplification Approach using Dependency Trees.
Paper: http://ceur-ws.org/Vol-2944/paper3.pdf
GitHub: https://github.com/RakshaAg/DEPSYMSum