import pandas as pd
import os
from prettytable import PrettyTable


muss = pd.read_csv(os.path.join("data", "muss_scores.csv"))
syn = pd.read_csv(os.path.join("data", "syn_scores.csv"))
lex = pd.read_csv(os.path.join("data", "lex_scores.csv"))
synlex = pd.read_csv(os.path.join("data", "synlex_scores.csv"))

t = PrettyTable(['System',
                 'BERTSimilarity', 'BERTSimilarity split',
                 'QuestEval', 'QuestEval split',
                 'BLEU', 'BLEU split'])
t.add_row(['MUSS',
           round(muss['BERTSimilarity'].mean(), 4), round(muss['avg split BERTSimilarity'].mean(), 4),
           round(muss['QuestEval'].mean(), 4), round(muss['avg split QuestEval'].mean(), 4),
           round(muss['BLEU'].mean(), 4), round(muss['avg split BLEU'].mean(), 4)   ])
t.add_row(['SYmpLE', '---', '---', '---', '---', '---', '---'])
t.add_row(['synlex',
           round(synlex['BERTSimilarity'].mean(), 4), round(synlex['avg split BERTSimilarity'].mean(), 4),
           round(synlex['QuestEval'].mean(), 4), round(synlex['avg split QuestEval'].mean(), 4),
           round(synlex['BLEU'].mean(), 4), round(synlex['avg split BLEU'].mean(), 4)])
t.add_row(['syn',
           round(syn['BERTSimilarity'].mean(), 4), round(syn['avg split BERTSimilarity'].mean(), 4),
           round(syn['QuestEval'].mean(), 4), round(syn['avg split QuestEval'].mean(), 4),
           round(syn['BLEU'].mean(), 4), round(syn['avg split BLEU'].mean(), 4)])
t.add_row(['lex',
           round(lex['BERTSimilarity'].mean(), 4), round(lex['avg split BERTSimilarity'].mean(), 4),
           round(lex['QuestEval'].mean(), 4), round(lex['avg split QuestEval'].mean(), 4),
           round(lex['BLEU'].mean(), 4), round(lex['avg split BLEU'].mean(), 4)])
print(t)

t = PrettyTable(['System',
                 'ROUGE 1', 'ROUGE 1 split',
                 'ROUGE 2', 'ROUGE 2 split',
                 'ROUGE L', 'ROUGE L split'])
t.add_row(['MUSS',
           round(muss['ROUGE 1'].mean(), 4), round(muss['avg split ROUGE 1'].mean(), 4),
           round(muss['ROUGE 2'].mean(), 4), round(muss['avg split ROUGE 2'].mean(), 4),
           round(muss['ROUGE L'].mean(), 4), round(muss['avg split ROUGE L'].mean(), 4)])
t.add_row(['SYmpLE', '---', '---', '---', '---', '---', '---'])
t.add_row(['synlex',
           round(synlex['ROUGE 1'].mean(), 4), round(synlex['avg split ROUGE 1'].mean(), 4),
           round(synlex['ROUGE 2'].mean(), 4), round(synlex['avg split ROUGE 2'].mean(), 4),
           round(synlex['ROUGE L'].mean(), 4), round(synlex['avg split ROUGE L'].mean(), 4)])
t.add_row(['syn',
           round(syn['ROUGE 1'].mean(), 4), round(syn['avg split ROUGE 1'].mean(), 4),
           round(syn['ROUGE 2'].mean(), 4), round(syn['avg split ROUGE 2'].mean(), 4),
           round(syn['ROUGE L'].mean(), 4), round(syn['avg split ROUGE L'].mean(), 4)])
t.add_row(['lex',
           round(lex['ROUGE 1'].mean(), 4), round(lex['avg split ROUGE 1'].mean(), 4),
           round(lex['ROUGE 2'].mean(), 4), round(lex['avg split ROUGE 2'].mean(), 4),
           round(lex['ROUGE L'].mean(), 4), round(lex['avg split ROUGE L'].mean(), 4)])
print(t)