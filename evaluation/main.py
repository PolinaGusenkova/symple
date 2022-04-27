import os
import pandas as pd
import BERTSimilarity.BERTSimilarity as bertsimilarity
from sumeval.metrics.bleu import BLEUCalculator
from sumeval.metrics.rouge import RougeCalculator
from QuestEval.questeval.questeval_metric import QuestEval


def sentences_to_dataframe(original_doc, simplified_doc, label):
    """Return dataframe with original and simplified sentences

    Each sentence should be on a separate line.
    label -- a string to identify the source (e.g., a filename)
    """

    with open(original_doc, 'r') as f:
        original = f.read().splitlines()
    with open(simplified_doc, 'r') as f:
        simplified = f.read().splitlines()

    df = pd.DataFrame(data = list(zip(original, simplified)),
                      columns = ['original', 'simplified'])
    df['split'] = df['simplified'].str.split('\. ')
    df.insert(loc = 0,
              column = 'label',
              value = label)

    return df


def docs_to_dataframe(original_dir, simplified_dir):
    """Return dataframe with original and simplified sentences from all sources"""

    df = pd.DataFrame()

    files = os.listdir(original_dir)
    for doc in files:
        doc_df = sentences_to_dataframe(original_doc = os.path.join(original_dir, doc),
                                        simplified_doc = os.path.join(simplified_dir, doc),
                                        label = doc)
        df = df.append(doc_df)

    return df


def calculate_bertsimilarity(df):
    """Calculate BERTSimilarity score"""

    bertsim = bertsimilarity.BERTSimilarity()

    df['BERTSimilarity'] = df.apply(lambda row:
                                    bertsim.calculate_distance(row['original'], row['simplified']),
                                    axis=1)
    df['split BERTSimilarity'] = df.apply(lambda row:
                                          [bertsim.calculate_distance(row['original'], sent)
                                           for sent in row['split']
                                           ], axis=1)
    df['avg split BERTSimilarity'] = df.apply(lambda row:
                                              sum(row['split BERTSimilarity']) / len(row['split BERTSimilarity']),
                                              axis=1)


def calculate_bleu(df):
    """Calculate BLEU score"""

    bleu = BLEUCalculator()

    df['BLEU'] = df.apply(lambda row:
                          bleu.bleu(row['original'], row['simplified']),
                          axis=1)
    df['split BLEU'] = df.apply(lambda row:
                                [bleu.bleu(row['original'], sent)
                                 for sent in row['split']
                                 ], axis=1)
    df['avg split BLEU'] = df.apply(lambda row:
                                    sum(row['split BLEU']) / len(row['split BLEU']),
                                    axis=1)


def calculate_rouge(df):
    """Calculate ROUGE score

    ROUGE-1 and ROUGE-2 is based on uni- and bigrams overlap accordingly.
    ROUGE-L is based on the longest common subsequence.
    """

    rouge = RougeCalculator(stopwords=True, lang="en")
    # ROUGE-1
    df['ROUGE 1'] = df.apply(lambda row:
                             rouge.rouge_n(row['original'], row['simplified'], n=1),
                             axis=1)
    df['split ROUGE 1'] = df.apply(lambda row:
                                   [rouge.rouge_n(row['original'], sent, n=1)
                                    for sent in row['split']
                                    ], axis=1)
    df['avg split ROUGE 1'] = df.apply(lambda row:
                                       sum(row['split ROUGE 1']) / len(row['split ROUGE 1']),
                                       axis=1)
    # ROUGE-2
    df['ROUGE 2'] = df.apply(lambda row:
                             rouge.rouge_n(row['original'], row['simplified'], n=2),
                             axis=1)
    df['split ROUGE 2'] = df.apply(lambda row:
                                   [rouge.rouge_n(row['original'], sent, n=2)
                                    for sent in row['split']
                                    ], axis=1)
    df['avg split ROUGE 2'] = df.apply(lambda row:
                                       sum(row['split ROUGE 2']) / len(row['split ROUGE 2']),
                                       axis=1)
    # ROUGE-L
    df['ROUGE L'] = df.apply(lambda row:
                             rouge.rouge_l(row['original'], row['simplified']),
                             axis=1)
    df['split ROUGE L'] = df.apply(lambda row:
                                   [rouge.rouge_l(row['original'], sent)
                                    for sent in row['split']
                                    ], axis=1)
    df['avg split ROUGE L'] = df.apply(lambda row:
                                       sum(row['split ROUGE L']) / len(row['split ROUGE L']),
                                       axis=1)


def calculate_questeval(df):
    """Calculate QuestEval score without references"""

    questeval = QuestEval()

    df['QuestEval'] = df.apply(lambda row:
                               questeval.corpus_questeval([row['original']], [row['simplified']])['corpus_score'],
                               axis=1)
    df['split QuestEval'] = df.apply(lambda row:
                                     [questeval.corpus_questeval([row['original']], [sent])['corpus_score']
                                      for sent in row['split']
                                      ], axis=1)
    df['avg split QuestEval'] = df.apply(lambda row:
                                         sum(row['split QuestEval']) / len(row['split QuestEval']),
                                         axis=1)


def calculate_scores(df):
    """Return dataframe expanded with similarity scores:
    BERTSimilarity, BLEU, ROUGE-1, ROUGE-2, ROUGE-L.

    A sentence is compared to its simplified version
    and, if multiple, to each sentence of the simplified version (split score).
    """

    calculate_bertsimilarity(df)
    calculate_bleu(df)
    calculate_rouge(df)
    calculate_questeval(df)

    return df


original_dir = "/Users/pg/Documents/work/data/original"
simplified_dir = "/Users/pg/Documents/work/data/SYmpLE/synlex"

df_docs = docs_to_dataframe(original_dir, simplified_dir)

df_docs = calculate_scores(df_docs)
df_docs.to_csv("/Users/pg/Documents/work/data/synlex_scores.csv")