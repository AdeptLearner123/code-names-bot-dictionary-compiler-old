from code_names_bot_dictionary_compiler.utils.spacy_utils import merge_compounds

from code_names_bot_dictionary_compiler.utils.spacy_utils import get_children_by_dep, get_auxilary
from .wiki_utils import format_title
import spacy

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("merge_entities")
tokenizer = nlp.tokenizer

EXCLUDE_ENT_TYPES = set(
    ["CARDINAL", "DATE", "MONEY", "ORDINAL", "PERCENT", "QUANTITY", "TIME"]
)


def get_child_entities(token):
    ents = [child.text for child in token.children if is_entity(child) and check_dep(child)]
    for child in token.children:
        if child.dep_ == "agent":
            continue
        ents += get_child_entities(child)
    return ents


def is_entity(token):
    return (len(token.ent_type_) > 0 and token.ent_type_ not in EXCLUDE_ENT_TYPES) or token.pos_ == "PROPN"


def check_dep(token):
    dep = token.dep_
    head = token.head
    while dep == "conj":
        dep = head.dep_
        head = head.head
    return (dep == "pobj" and head.text == "as") or dep == "oprd"


def get_sentence_variants(sentence):
    auxilary = get_auxilary(sentence)

    if auxilary is None:
        return []

    nsubj_children = get_children_by_dep(auxilary, ["nsubj", "nsubjpass"])
    if len(nsubj_children) == 0:
        return []
    nsubj = nsubj_children[0]

    acl_children = get_children_by_dep(nsubj, ["acl", "appos"])
    ents = [nsubj.text] if is_entity(nsubj) else []
    for child in acl_children:
        ents += get_child_entities(child)
    return ents


def get_tokens(str):
    return set([token.text for token in tokenizer(str)])


def get_acronym(title):
    words = title.split(" ")
    letters = [word[0] for word in words]
    letters = list(filter(lambda letter: letter.isupper(), letters))
    return "".join(letters)


def extract_variants(title, summary, redirects):
    formatted_title = format_title(title)

    variants = list()
    variants.append(formatted_title)

    doc = nlp(summary.strip().replace("\n", " "))
    doc = merge_compounds(doc)

    if len(list(doc.sents)) > 0:
        sentence = list(doc.sents)[0]
        variants += get_sentence_variants(sentence)

    variants_tokenized = [get_tokens(variant) for variant in variants]
    redirects = [format_title(redirect) for redirect in redirects]
    redirect_variants = []
    for redirect in redirects:
        redirect_tokens = get_tokens(redirect)

        if any(
            redirect_tokens.issubset(variant_tokens)
            for variant_tokens in variants_tokenized
        ):
            redirect_variants.append(redirect)

    acronym = get_acronym(formatted_title)
    if acronym in redirects:
        variants.append(acronym)

    variants += redirect_variants
    variants = list(set(variants))
    return variants
