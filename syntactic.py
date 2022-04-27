from utils import *
from passive import passive_to_active

### Simplification ###
# Example:
# do	did	V;PST
# do	does	V;3;SG;PRS
# do	doing	V;V.PTCP;PRS
# do	done	V;V.PTCP;PST
# do	do	V;NFIN


def extract_clause(root, clause_node, clause_type):
    sentences = []

    # for clause_node in clause_nodes:
    clean(root, clause_node)

    # print('extract_clause')
    # print(clause_node)
    # print(clause_type)

    verbs = clause_node.select_by('upos', 'VERB')
    for verb in verbs:
        if not verb.get_by('upos', 'AUX'):
            infl = unimorph.analyze_word(verb.form, lang=lang).split('\n')[0].split('\t')
            if infl and len(infl) > 2 and infl[2] == 'V;V.PTCP;PRS':
                verb.form = time_inflect(infl[0], root.select_by('upos', 'AUX'), root.select_by('upos', 'VERB'))

    verbs = None

    np = ""
    if clause_type == "conjoint":
        # if the clause has no subject it is given the subject of the main clause
        clause_subj = find_subj(clause_node)
        # print('in conjoint')
        if not clause_subj:
            # print('look for subj')
            subj = find_subj(clause_node.parent)
            if subj:
                if subj.form in descriptive_clause_markers_en and clause_node.parent.parent:
                    subj = find_subj(clause_node.parent.parent)
                if subj and subj.form not in ignore_en+descriptive_clause_markers_en:
                    # print('subj found:', subj, subj.linear())
                    np = subj.get_subtree_text() + " "

                    # if the clause has no verb it is given the verb of the main clause
                    if not subj.select_by('upos', 'VERB') and not subj.select_by('upos', 'AUX'):
                        # print('look for verbs')
                        verbs = clause_node.parent.get_by('upos', 'VERB')
                        if not verbs:
                            verbs = clause_node.parent.get_by('upos', 'AUX')

    else:
        # print()
        # print('-NP-')
        # a noun phrase (NP) is the left sub-tree of the parent of the clause token
        np_node = clause_node.parent
        # print(np_node)
        if np_node.deprel == 'root':
            # print('ROOT IS FOUND')
            np_node = find_subj(clause_node.parent)
        if np_node:
            np_id = np_node.id
            np_children = np_node.children

            # print(np_node)
            # print(np_id)
            # print(np_children)

            for child in np_children:
                if child.id > np_id and child.deprel != 'conj':
                    # print('ignore', child)
                    child.ignore_subtree()
                    # np_node.remove_child(child)

            if clause_type != "appositive":
                case = np_node.select_by('deprel', 'case')
                if case:
                    case[0].ignore()
            # end if

            np = np_node.get_subtree_text() + " "
            np_node.hard_reset_subtree()
        # print()

    connector = ""
    if clause_type == "appositive":
        connector = get_to_be(root, clause_type) + ' '
    elif clause_type == "conjoint":
        if verbs:
            connector = verbs[0].get_subtree_text() + ' '
        # find the conjunction term or adverbial modifier
        mark_list = clause_node.get_by("deprel", "cc")
        if not mark_list:
            mark_list = clause_node.get_by("deprel", "advmod")
            if not mark_list:
                mark_list = clause_node.get_by("deprel", "mark")

        if mark_list:
            mark = mark_list[0]
            if mark.form in thisis_conj_en:
                connector = "This {} ".format(get_to_be(root, clause_type))
            else:
                if mark.form not in thisis_conj_en + keep_conj_en:
                    # mark.parent.remove_child(mark)
                    mark.ignore()

    # if relcl and PRON+VERB, remove the PRON (will be new)
    if clause_type == "relative":
        verbs = clause_node.select_by('upos', 'VERB')
        for verb in verbs:
            pron = verb.get_by('upos', 'PRON')
            if pron:
                for p in pron:
                    if p.form in ignore_en or p.deprel != 'nsubj':
                        p.ignore()
                # pron[0].parent.remove_child(pron[0])

    # a clause is the subtree of the clause token
    clause_node.make_root()
    clause = clause_node.get_subtree_text()

    # new sentence from the clause
    # specific sentence order is not implemented
    # print('np', np)
    # print('connector', connector)
    # print('clause', clause)
    if connector.strip() == clause.strip():
        connector = ''

    sentences.append(np + connector + clause + ".")

    # clause_node.parent.remove_child(clause_node)
    clause_node.ignore_subtree()
    # print('LINEAR ---', root.linear())

    # new sentence without clauses
    if root.select_by('upos', 'VERB') or root.select_by('upos', 'AUX'):
        sentences.append(root.get_subtree_text())

    # print(sentences)

    return list(set(sentences))


def simplify(complex, simplified=None, tags=tag_list, count=0):
    # print(complex)
    if count > 5:
        return [complex]

    roots = sent_to_tree(complex)
    if not roots:
        return [complex]

    # print(complex)
    root = roots[0]

    # print(root.linear())

    if simplified is None:
        simplified = []

    auxpass, agent, nsubjpass = get_passive_elems(root)

    clauses = []
    for tag in tags:
        clauses = root.select_by("deprel", tag)
        # print('clauses ----', clauses)
        simplified = []
        for clause in clauses:
            # print()
            # print(clause)
            # print()
            if not root.select_by('upos', 'VERB'):
                continue
            if tag in ['advcl', 'parataxis', 'ccomp'] and \
                    root.children[0].upos == 'AUX' and root.children[0].select_by('upos', 'PRON'):
                continue
            elif tag == 'advcl' and auxpass and agent and nsubjpass:
                continue
            # elif tag == 'appos' and not clause[0].get_by('deprel', 'punct'):
            #     continue
            elif tag == 'amod' and clause.deprel != "nsubj":
                continue
            elif tag == 'acl:relcl':
                continue_i = ContinueI()
                # print()
                # print('rel')
                try:
                    for pron in clause.select_by('upos', 'PRON'):
                        # print('pron', pron)
                        if pron.form in descriptive_clause_markers_en:
                            # print('markers')
                            # print()
                            raise continue_i
                except ContinueI:
                    continue

            clause_type = tag_dict[clause.deprel]
            # print('clause type', clause_type)

            if clause_type == 'conjoint' and ( \
                            not root.select_by("upos", "VERB") or \
                            not clause.select_by("upos", "VERB") and not clause.select_by("upos", "AUX") or \
                            clause.parent.deprel in ['nsubj', 'nsubj:pass']
                    ):
                continue

            # print('end:', clause)
            sents = extract_clause(root, clause, clause_type)
            if complex in sents:
                return [complex]
            # print('sents ----', sents)
            for sent in sents:
                simplified += simplify(sent, simplified, tags, count + 1)
            return simplified

    if not clauses and auxpass and agent and nsubjpass:
        simplified.append(passive_to_active(root, auxpass[0], agent[0], nsubjpass[0]))
        return simplified

    simplified.append(root.get_subtree_text())
    return simplified