import udon2
import re
import multicombo
import spacy
import uuid
import os
import unimorph

thisis_conj_en = ["before", "after", "once", "since", "when"]
keep_conj_en = ["although", "whereas", "however", "because", "as", "to"]
pass_list = ["aux:pass", "agent", "nsubj:pass"]
tag_list = ["appos", "amod", "conj", "advcl", "parataxis", "ccomp", "acl:relcl", "rcmod"]
descriptive_clause_markers_en = ['that']
ignore_en = ['which']

tag_dict = {
        "appos": "appositive",
        "amod": "appositive",
        "conj": "conjoint",
        "advcl": "conjoint",
        "parataxis": "conjoint",
        "ccomp": "conjoint",
        "acl:relcl": "relative",
        "rcmod": "relative"
    }
pronoun_pairs_en = {
    'me': 'I',
    'you': 'you',
    'her': 'she',
    'him': 'he',
    'them': 'they',
    'it': 'it',
    'us': 'we',
    'one': 'one'
    }
tense_to_tags = {
    'past simple': {'aux': '', 'verb': 'V;PST'},
    'present simple': {'aux': '', 'verb': 'V;NFIN', 'verb2': 'V;3;SG;PRS'},
    'future simple': {'aux': 'will', 'verb': 'V;NFIN'},
    'past continuous': {'aux': 'was', 'aux2': 'were', 'verb': 'V;V.PTCP;PRS'},
    'present continuous': {'aux': 'am', 'aux2': 'are', 'aux3': 'is', 'verb': 'V;V.PTCP;PRS'},
    'future continuous': {'aux': 'will be', 'verb': 'V;V.PTCP;PRS'},
    'past perfect simple': {'aux': 'had', 'verb': 'V;V.PTCP;PST'},
    'present perfect simple': {'aux': 'have', 'aux2': 'has', 'verb': 'V;V.PTCP;PST'},
    'future perfect simple': {'aux': 'will have', 'verb': 'V;V.PTCP;PST'},
    'past perfect continuous': {'aux': 'had been', 'verb': 'V;V.PTCP;PRS'},
    'present perfect continuous': {'aux': 'have been', 'aux2': 'has been', 'verb': 'V;V.PTCP;PRS'},
    'future perfect continuous': {'aux': 'will have been', 'verb': 'V;V.PTCP;PRS'},
}

lang = 'eng'
filenames = []
sent_file = {}



try:
    nlp=multicombo.load("en")
except:
    nlp = spacy.load("en_core_web_sm")


class ContinueI(Exception):
    pass


def get_prev_node(root, node):
    id_prev = int(node.id-1)
    prev = root.select_by("id", str(id_prev))
    if prev:
        return prev[0]
    return False


def get_next_node(root, node):
    id_next = int(node.id+1)
    next = root.select_by("id", str(id_next))
    if next:
        return next[0]
    return False


def remove_punct(root, node):
    if not node:
        return

    # removing SpaceAfter=No
    misc = str(get_prev_node(root, node).misc)
    misc = re.sub(r'(^SpaceAfter=No\|)|(\|SpaceAfter=No$)|(\|SpaceAfter=No\|)', '', misc)
    misc = re.sub(r'^SpaceAfter=No$', '_', misc)
    get_prev_node(root, node).misc = misc

    # node.parent.remove_child(node)
    node.ignore()


# removes surrounding punctuation
def clean(root, node):
    nodes = node.linear()

    first_node = nodes[0]
    last_node = nodes[-1]


    if first_node.deprel == "punct":
        remove_punct(root, first_node)
    else:
        prev_node = get_prev_node(root, first_node)
        if prev_node and prev_node.deprel == "punct":
            remove_punct(root, prev_node)

    if last_node.deprel == "punct":
        remove_punct(root, last_node)
    else:
        next_node = get_next_node(root, last_node)
        if next_node and next_node.deprel == "punct":
            remove_punct(root, next_node)


def find_subj(root):
    subj_list = root.get_by("deprel", "nsubj")
    if not subj_list:
        subj_list = root.get_by("deprel", "nsubj:pass")
    if not subj_list:
        return False
    # print('SUBJ_list', subj_list)
    return subj_list[0]


def get_subj_form(subj):
    plural = False
    i = False

    if not subj:
        return plural, i
    if type(subj) == udon2.core.NodeList:
        subj = subj[0]

    if subj.form in ['you', 'them', 'they', 'us', 'we']:
        plural = True
    elif subj.form in ['me', 'I']:
        i = True
    elif subj.select_by("upos", "CCONJ"):
        plural = True
    # TBD: detect plurality (we don't have NNS tags)
    # elif subj.tag == 'NNS':
    #     plural = True

    return plural, i


# Language dependent!
def get_to_be(root, clause_type):
    auxv = root.select_by("deprel", "aux")
    verb = root.select_by("upos", "VERB")

    subj = root.select_by("deprel", "nsubj")
    plural, i = get_subj_form(subj)
    tag = unimorph.analyze_word(verb[0].form, lang=lang)
    if tag:
        tag = tag.split('\n')[0].split('\t')[2].strip()
    else:
        tag = ''
    # return to_be_form(auxv, tag, clause_type, plural, i)
    if tag == 'V;NFIN':
        plural = True

    if not auxv:
        if tag == 'V;PST':
            if clause_type == 'appositive' and plural:
                return 'were'
            return 'was'
        if clause_type == 'appositive':
            if i:
                return 'am'
            if plural:
                return 'are'
        return 'is'

    auxv_form = re.sub(r'\W+', '', auxv[0].form)

    if auxv_form in ['will', "ll"]:
        if clause_type == 'appositive':
            if i:
                return 'am'
            if plural:
                return 'are'
            return 'is'
        return 'will be'

    if clause_type == 'conjoint':
        if auxv_form in ['was', 'were', 'had', "d"]:
            return 'was'
        return 'is'

    if auxv_form in ['was', 'were', 'is', 'are', 'am', "m", "re", "s"]:
        return auxv_form
    if auxv_form in ['had', "d"]:
        if plural:
            return 'were'
        return 'was'
    if auxv_form in ['have', "ve"]:
        if i:
            return 'am'
        return 'are'
    if auxv_form == 'has':
        return 'is'

    return 'is'


def time_inflect(verb_form, aux, verbs):
    add = ''
    word = verb_form
    tag = 'V;NFIN'
    if aux:
        if aux[0] in ['was', 'were', 'had']:
            tag = 'V;PST'
        elif aux[0] in ['is', 'has']:
            tag = 'V;3;SG;PRS'
        elif aux[0] in ['will', 'would']:
            add = aux[0] + ' '
    else:
        for verb in verbs:
            word = unimorph.analyze_word(verb.form, lang=lang).split('\n')[0].split('\t')
            if len(word) > 2 and word[2] not in ['V;V.PTCP;PRS', 'V;V.PTCP;PST']:
                tag = word[2]
                break

    new_vform = unimorph.inflect_word(verb_form, lang=lang, features=tag).split('\n')[0].split('\t')
    if len(new_vform) > 1:
        new_vform = new_vform[1]
    else:
        new_vform = word

    return add + new_vform


def sent_to_tree(sentence):
    # annotate and create conll
    doc = nlp(sentence.strip())

    filename = '{}_conllu.txt'.format(uuid.uuid4().hex)
    # print(filename)
    filenames.append(filename)
    sent_file[sentence.strip().lower()] = filename

    with open(os.path.join('data', filename), 'w', encoding='utf-8') as f:
        f.write(multicombo.to_conllu(doc))

    # with open(os.path.join('data', filename), 'r', encoding='utf-8') as f:
    #     print('---------file:')
    #     print(f.read())
    #     print('---------EOF')

    roots = udon2.Importer.from_conll_file(os.path.join('data', filename))
    return roots


def remove_tmp_files():
    for file in filenames:
        if os.path.exists(os.path.join('data', file)):
            os.remove(os.path.join('data', file))


def get_last_filename():
    return filenames[-1]


def get_sent_file():
    return sent_file


def get_passive_elems(root):
    auxpass = root.select_by("deprel", 'aux:pass')
    agent = root.select_by("deprel", 'obl:agent')
    if not agent:
        agent = root.select_by("deprel", 'obl')
        # passive_to_active reduced to very obvious cases with pronouns
        if agent and agent[0].form not in pronoun_pairs_en.keys():
            agent = None

    nsubjpass = root.select_by("deprel", 'nsubj:pass')

    return auxpass, agent, nsubjpass


def pretty_print(orig_sentence, sentences):
    print("========================")
    print("__Original sentence:__")
    print(orig_sentence)
    print("__Simplified sentences:__")
    for sentence in sentences:
        print(sentence)
    print("========================")
    print()
