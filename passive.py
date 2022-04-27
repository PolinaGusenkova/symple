from utils import *

### Passive voice ###

# Example:
# do	did	V;PST
# do	does	V;3;SG;PRS
# do	doing	V;V.PTCP;PRS
# do	done	V;V.PTCP;PST
# do	do	V;NFIN

def get_active_tense(subj, auxv, aux):
    plural, i = get_subj_form(subj)

    if auxv:
        auxv_form = re.sub(r'\W+', '', auxv[0].form)
    aux_form = re.sub(r'\W+', '', aux.form)

    if aux_form == 'been':
        if auxv_form in ['will', 'would', "ll", "d"]:
            # future perfect
            return 'will have ', 'V;V.PTCP;PST'
        if auxv_form in ['has', 'have', "s", "ve"]:
            # present perfect
            if plural or i:
                return 'have ', 'V;V.PTCP;PST'
            else:
                return 'has ', 'V;V.PTCP;PST'
        if auxv_form in ['had', "d"]:
            # past perfect
            return 'had ', 'V;V.PTCP;PST'
    if aux_form == 'being':
        if auxv_form in ['is', 'am', 'are', "m", "re", "s"]:
            # present continuous
            if i:
                return 'am ', 'V;V.PTCP;PRS'
            if plural:
                return 'are ', 'V;V.PTCP;PRS'
            return 'is ', 'V;V.PTCP;PRS'
        if auxv_form in ['was', 'were']:
            # past continuous
            if plural:
                return 'were ', 'V;V.PTCP;PRS'
            return 'was ', 'V;V.PTCP;PRS'
    if aux_form in ['was', 'were']:
        # past simple
        return '', 'V;PST'
    if aux_form in ['am', 'are', 'is', "m", "re", "s"]:
        # present simple
        if i:
            return 'am ', 'V;NFIN'
        if plural:
            return 'are ', 'V;NFIN'
        return '', 'V;3;SG;PRS'
    if aux_form in ['will', 'would', "ll", "d"]:
        # future simple
        return 'will ', 'V;NFIN'
    return '', ''


def change_passive_tense(subj, verb, auxv, aux):
    # print(subj, auxv, aux)
    aux, vtag = get_active_tense(subj, auxv, aux)
    word = unimorph.analyze_word(verb.form, lang=lang).split('\t')[0]
    # print(verb.form)
    # print(unimorph.inflect_word(word, lang=lang, features=vtag).split('\t'))
    new_vform = unimorph.inflect_word(word, lang=lang, features=vtag).split('\t')
    if len(new_vform) > 1:
        new_vform = new_vform[1]
    else:
        new_vform = word
    return aux + new_vform


# TBD: NOT TESTED
def passive_to_active(root, auxpass, agent, nsubjpass):
    aux_verbs = root.select_by("deprel", "aux")
    verb = auxpass.parent

    obj = nsubjpass.get_subtree_text()

    case = agent.get_by("deprel", "case")[0]
    case.parent.remove_child(case)
    subj = agent.get_subtree_text()

    new_verb_form = change_passive_tense(agent, verb, aux_verbs, auxpass)
    # change pronoun
    if subj in pronoun_pairs_en.keys():
        subj = pronoun_pairs_en[subj.lower()]

    # build sentence
    sentence = ''
    children = root.children[0].children
    linear = root.linear()
    parts = [node for node in linear if node in children]
    for child in parts:
        if child.deprel == 'nsubj:pass':
            sentence += ' ' + subj
        elif child.deprel == 'obl' or child.deprel == 'obl:agent':
            sentence += ' ' + obj
        elif child.deprel == 'aux:pass':
            sentence += ' ' + new_verb_form
        elif child.deprel == 'punct':
            sentence += child.form
        elif child.deprel != 'aux':
            sentence += ' ' + child.get_subtree_text()
    return sentence.strip()