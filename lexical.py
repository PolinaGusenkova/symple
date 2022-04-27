import nltk
import ssl
import os
import pandas as pd
from nltk import WordNetLemmatizer

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

from nltk.wsd import lesk
from nltk.tokenize import sent_tokenize, word_tokenize
from conllu import parse
from utils import get_sent_file, sent_to_tree
from collections import Counter


def simplify_lexic(sentence):
    key = sentence.strip().lower()
    sent_file = get_sent_file()
    if key not in sent_file.keys():
        sent_to_tree(sentence)

    with open(os.path.join('data', sent_file[key]), 'r', encoding='utf-8') as f:
        sent_pos = parse(f.read())[0]

    freq_df = get_most_freq_lemmas_per_synset()
    lemmatizer = WordNetLemmatizer()

    tokenized = word_tokenize(sentence)
    words = []
    for t in tokenized:
        if t.isalpha():
            words.append(t)
        else:
            words += t.split('-')

    count_change = 0

    for i, word in enumerate(words):
        if i > 0 and word[0].isupper():
            continue
        pos = sent_pos.filter(form=word)
        if not pos:
            continue
        pos = pos[0]['upos']

        if pos == 'VERB': # in ['NOUN', 'ADJ', 'ADV', 'VERB']:
            synset = lesk(words, word)

            if not synset:
                continue

            try:
                subs = freq_df.loc[freq_df['synset'] == synset.name()]["lemma"].item()
            except:
                max = 0
                for l in synset.lemmas():
                    if l.count() > max:
                        max = l.count()
                most_freq = [l.name() for l in synset.lemmas() if l.count() == max]
                min = 100
                for l in most_freq:
                    if len(l) < min:
                        min = len(l)
                        subs = l

            lemma = lemmatizer.lemmatize(word.lower(), synset.pos())
            if subs != lemma:
                count_change += 1
                # TBD: change substitute's form
                words[i] = subs

    # if count_change > 0:
    #     print('CHANGE COUNT', count_change)

    return ' '.join(words), count_change


def count_freq():
    from mediawiki import MediaWiki
    # nltk.download('omw-1.4')
    # nltk.download('universal_tagset')
    from nltk import pos_tag, WordNetLemmatizer
    from nltk.corpus import wordnet

    freq = read_freq(os.path.join('data', 'word_counts.txt'))
    noun_counter = freq['NOUN']
    adj_counter = freq['ADJ']
    adv_counter = freq['ADV']
    verb_counter = freq['VERB']

    # noun_counter = Counter({})
    # adj_counter = Counter({})
    # adv_counter = Counter({})
    # verb_counter = Counter({})

    succeeded = 0

    wikipedia = MediaWiki(user_agent='goose-agent-string')
    pages = wikipedia.random(pages=8)

    for i, name in enumerate(pages):
        try:
            page = wikipedia.page(name)
        except:
            continue
        succeeded += 1
        page_tokens = word_tokenize(page.content)
        pos_tagged = pos_tag(page_tokens, tagset='universal')
        lemmatizer = WordNetLemmatizer()

        for pos in pos_tagged:
            if not pos[0].isalpha():
                continue
            if pos[1] == 'NOUN':
                lemma = lemmatizer.lemmatize(pos[0].lower(), wordnet.NOUN)
                noun_counter.update([lemma])
            elif pos[1] == 'ADJ':
                lemma = lemmatizer.lemmatize(pos[0].lower(), wordnet.ADJ)
                adj_counter.update([lemma])
            elif pos[1] == 'ADV':
                lemma = lemmatizer.lemmatize(pos[0].lower(), wordnet.ADV)
                adv_counter.update([lemma])
            elif pos[1] == 'VERB':
                lemma = lemmatizer.lemmatize(pos[0].lower(), wordnet.VERB)
                verb_counter.update([lemma])

        # if i % 100 == 0:
        #     print(i, 'pages processed')

    print('Total')
    print('Pages:', 4992+succeeded)

    noun = 0
    adj = 0
    adv = 0
    verb = 0
    with open(os.path.join('data', 'word_counts.txt'), 'w', encoding='utf-8') as f:
        for lemma, count in noun_counter.items():
            if count > 1:
                f.write(lemma + '\tNOUN\t' + str(count) + '\n')
                noun += 1
        for lemma, count in adj_counter.items():
            if count > 1:
                f.write(lemma + '\tADJ\t' + str(count) + '\n')
                adj += 1
        for lemma, count in adv_counter.items():
            if count > 1:
                f.write(lemma + '\tADV\t' + str(count) + '\n')
                adv += 1
        for lemma, count in verb_counter.items():
            if count > 1:
                f.write(lemma + '\tVERB\t' + str(count) + '\n')
                verb += 1

    print('Words:', noun+adj+adv+verb)
    print('Nouns:', noun)
    print('Adjectives:', adj)
    print('Adverbs:', adv)
    print('Verbs:', verb)


def read_freq(path):
    noun_counter = Counter({})
    adj_counter = Counter({})
    adv_counter = Counter({})
    verb_counter = Counter({})

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    for line in lines:
        cols = line.split('\t')
        if len(cols) > 2:
            if cols[1] == 'NOUN':
                noun_counter[cols[0]] = int(cols[2])
            if cols[1] == 'ADJ':
                adj_counter[cols[0]] = int(cols[2])
            if cols[1] == 'ADV':
                adv_counter[cols[0]] = int(cols[2])
            if cols[1] == 'VERB':
                verb_counter[cols[0]] = int(cols[2])

    freqs = {'NOUN': noun_counter,
             'ADJ': adj_counter,
             'ADV': adv_counter,
             'VERB': verb_counter}

    return freqs


def count_freq_synset():
    from mediawiki import MediaWiki
    # nltk.download('omw-1.4')
    # nltk.download('universal_tagset')
    from nltk import pos_tag, WordNetLemmatizer
    from nltk.corpus import wordnet

    lemmatizer = WordNetLemmatizer()
    wordnet_pos = {'NOUN': wordnet.NOUN, 'ADJ': wordnet.ADJ, 'ADV': wordnet.ADV, 'VERB': wordnet.VERB}

    try:
        counter = read_freq_synset(os.path.join('data', 'synset_verb_counts.txt'))
        print('Read successfully')
    except:
        counter = Counter({})

    succeeded = 0

    wikipedia = MediaWiki(user_agent='goose-agent-string')
    pages = wikipedia.random(pages=2)

    for name in pages:
        try:
            page = wikipedia.page(name)
        except:
            continue
        succeeded += 1

        page_sentences = sent_tokenize(page.content)
        for sentence in page_sentences:
            tokenized = word_tokenize(sentence)
            words = []
            for t in tokenized:
                if t.isalpha():
                    words.append(t)
                elif '-' in t and len(t) > 1:
                    words += t.split('-')

            pos_tagged = pos_tag(words, tagset='universal')

            for i, word in enumerate(words):
                if word and i > 0 and word[0].isupper():
                    continue

                pos = pos_tagged[i][1]
                if pos == 'VERB': # in ['NOUN', 'ADJ', 'ADV', 'VERB']:
                    synset = lesk(words, word)

                    if not synset:
                        continue

                    lemma = lemmatizer.lemmatize(word.lower(), wordnet_pos[pos])
                    tuple = (lemma, synset.name())
                    counter.update([tuple])

    print('Writing...')
    with open(os.path.join('data', 'synset_verb_counts.txt'), 'w', encoding='utf-8') as f:
        for tuple, count in counter.items():
            f.write(tuple[0] + '\t' + tuple[1] + '\t' + str(count) + '\n')

    print('Total')
    print('Pages:', 16200+succeeded)
    print('Words:', len(counter))
    get_most_freq_lemmas_per_synset()
    # 17414 -> 17518 -> 17613 -> 17685 -> 17759 -> 17816 -> 17867 -> 17915 -> 17973 -> 18049 -> 18125 -> 18183 -> 18297


def read_freq_synset(path):
    counter = Counter({})

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    for line in lines:
        cols = line.split('\t')
        if len(cols) > 2:
            counter[(cols[0], cols[1])] = int(cols[2])

    return counter


def get_most_freq_lemmas_per_synset():
    df = pd.read_csv(os.path.join('data', 'synset_verb_counts.txt'), sep="\t", header=None)
    df.columns = ["lemma", "synset", "count"]
    df = df[df["synset"].str.contains('\.v\.')]
    # print('Verbs:', df.shape)
    freqs = df.loc[df.groupby('synset')['count'].idxmax()]
    return freqs


# sentence = 'The huge cat devoured a belittled rat.'
# print(simplify_lexic(sentence))
# count_freq()
# count_freq_synset()
# get_most_freq_lemmas_per_synset()