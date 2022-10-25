from code_names_bot_dictionary_compiler.download.caches import OxfordDefinitionsCache, OxfordSentencesCache
from code_names_bot_dictionary_compiler.oxford_utils.sense_iterator import iterate_senses
from config import OXFORD_FILTERED_2, OXFORD_FILTERED_3

import json
from collections import defaultdict

def get_sense_sentence_counts():
    sentences_cache = OxfordSentencesCache()
    query_to_result = sentences_cache.get_key_to_value()
    sentence_counts = defaultdict(lambda: 0)

    for results_str in query_to_result.values():
        results = json.loads(results_str)
        for result in results["results"]:
            for lexical_entry in result["lexicalEntries"]:
                for sentence in lexical_entry["sentences"]:
                    for sense_id in set(sentence["senseIds"]):
                        sentence_counts[sense_id] += 1

    return sentence_counts

def extract_sense_data(lemma, sense_json):
    synonyms, domains, variant_forms, classes = [], [], [], []

    if "domainClasses" in sense_json:
        domains = [domain_class["text"].replace("_", " ").lower() for domain_class in sense_json["domainClasses"]]

    if "semanticClasses" in sense_json:
        classes = [semantic_class["text"].replace("_", " ").lower() for semantic_class in sense_json["semanticClasses"]]

    if "synonyms" in sense_json:
        synonyms = [synonym["text"] for synonym in sense_json["synonyms"]]
        if lemma in synonyms:
            synonyms.remove(lemma)
    
    if "variantForms" in sense_json:
        variant_forms = [ variant_form["text"] for variant_form in sense_json["variantForms"] ]
    
    return synonyms, domains, variant_forms, classes


def get_entry_variants(entry):
    variants = []
    if "inflections" in entry:
        variants += [
            inflection["inflectedForm"]
            for inflection in entry["inflections"]
        ]
    
    if "variantForms" in entry:
        variants += list(
            set(
                [
                    variantForm["text"]
                    for variantForm in entry["variantForms"]
                ]
            )
        )

    return variants


def enhance_sense(entry, sense, meta, dictionary, sentence_counts):
    sense_id = sense["id"]
    if sense_id not in dictionary:
        return
    
    lemma = dictionary[sense_id]["lemma"]

    variants = get_entry_variants(entry)

    synonyms, domains, sense_variants, classes = extract_sense_data(lemma, sense)

    variants = set(variants + sense_variants)
    if lemma in variants:
        variants.remove(lemma)
    variants = list(variants)

    sense_idx, is_subsense = meta
    
    dictionary[sense_id].update({
        "variants": variants + sense_variants,
        "synonyms": synonyms,
        "domains": domains,
        "classes": classes,
        "meta": {
            "sense_idx": sense_idx,
            "is_subsense": is_subsense,
            "sentence_count": sentence_counts[sense_id]
        }
    })


def main():
    with open(OXFORD_FILTERED_2, "r") as file:
        dictionary = json.loads(file.read())

    definitions_cache = OxfordDefinitionsCache()
    sentence_counts = get_sense_sentence_counts()

    for _, entry, sense, meta in iterate_senses(definitions_cache):
        enhance_sense(entry, sense, meta, dictionary, sentence_counts)

    with open(OXFORD_FILTERED_3, "w+") as file:
        file.write(json.dumps(dictionary, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()