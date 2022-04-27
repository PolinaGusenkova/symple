import deplacy
from syntactic import simplify
from lexical import simplify_lexic
from utils import remove_tmp_files, pretty_print, nlp
import re
import os


def simplify_sentence(sentence, lexical=False):
    if sentence:
        sentences = simplify(sentence)
        # sentences = [sentence]

        # capitalize and dot sentences
        for i, sentence in enumerate(sentences):
            if len(sentence) < 2:
                continue
            if lexical:
                sentence, count_change = simplify_lexic(sentence)
            sentence = re.sub(r'[^\w\s-]', '', sentence).strip()
            sentence = re.sub(r'\s+', ' ', sentence)
            sentences[i] = sentence[0].upper() + sentence[1:] + "."

        remove_tmp_files()
        return list(set(sentences)), count_change
    return [''], 0


def simplify_docs(inpath, outpath, lexical=False):
    """Create files with simplified sentences

    inpath -- input dir; input files must have each sentence on a separate line.
    outpath -- output dir
    """

    files = os.listdir(inpath)
    for name in files:
        with open(os.path.join(inpath, name), 'r', encoding='utf-8') as f:
            sentences = f.read().splitlines()

        data = ''
        count = 0
        for sentence in sentences:
            simpl, count_change = simplify_sentence(sentence, lexical)
            count += count_change
            # pretty_print(sentence, simpl)
            data += ' '.join(simpl) + '\n'

        with open(os.path.join(outpath, name), 'w', encoding='utf-8') as f:
            f.write(data)
        print("WORDS CHANGED:", count)


simplify_docs("/Users/pg/Documents/work/data/original", "/Users/pg/Documents/work/data/SYmpLE/synlex", lexical=True)

#
# sents = [
#     "The clock is one of the oldest human inventions, meeting the need to measure intervals of time shorter than the natural units: the day, the lunar month, year and galactic year."
#     ]
# for s in sents:
#     simpl = simplify_sentence(s)
#     pretty_print(s, simpl)

# doc=nlp(
#     "This object can be a pendulum, a tuning fork, a quartz crystal, or the vibration of electrons in atoms as they emit microwaves."
# )
# deplacy.render(doc)

