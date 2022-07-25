"""
   Big steps to code:
   (1) Get list of languages to iterate over
   (2) Get all lemmas from each language and store as a list
   (3) Create syn2id and id2syn dictionaries
   (4) Build the graph
   """
import json
import os
import argparse
import matplotlib.pyplot as plt
import utils
from utils import *
import numpy as np
from tqdm import tqdm


def get_ignore_lemmas():
    """These lemmas have thousands of synsets and are removed for colexification processing."""
    ignore_lemmas = ["", " ", "список_астероидов", "աստերոիդների_ցանկ"]
    return ignore_lemmas

def get_languages_from_synset_text_files(args):
    lemma_savedir = os.path.join(args.exp_dir, args.lemma_savedir)
    if not os.path.isdir(lemma_savedir):
        os.mkdir(lemma_savedir)
    text_files = collect_files(args.synset_text_files_dir)
    languages = []
    for file in text_files:
        """"""
        file1 = open(file, 'r')
        Lines = file1.readlines()
        for line in tqdm(Lines):
            line = line.replace("\n", "")
            line_info = line.split("~")  # we have to write some code because unfortunately some lemmas contain '~'
            lang = line_info[0]
            if lang not in languages:
                languages.append(lang)
            if len(languages) >= 500:
                break
        file1.close()
        if len(languages) >= 499:  # seems like there are only 499 languages, yep only 499
            break
    return languages

def get_concept_syns(args):
    if not os.path.exists(os.path.join(args.exp_dir, 'concept_syns.pkl')):
        files = collect_files(args.synset_types_files_dir)
        concept_syns = []
        total_syns = []
        for file in tqdm(files):
            file1 = open(file, 'r')
            Lines = file1.readlines()
            for line in Lines:
                line = line.replace("\n", "")
                syn = line.split("~")[0]
                syn_type = line.split("~")[1].lower()
                if syn_type == 'concept':
                    concept_syns.append(syn)
                total_syns.append(syn)
        print("Total synsets: " + str(len(total_syns)))
        print("Concept synsets: " + str(len(concept_syns)))
        dump(concept_syns, os.path.join(args.exp_dir, 'concept_syns.pkl'))
    else:
        concept_syns = load(os.path.join(args.exp_dir, 'concept_syns.pkl'))
    return concept_syns

def get_lemmasyns(args):
    """The server can't hold the entire dictionary in memory, so you must only save 10 languages at a time and
       load the files many times --> This step takes ~24 hours."""
    lemma_savedir = os.path.join(args.exp_dir, args.lemma_savedir)
    if not os.path.isdir(lemma_savedir):
        os.mkdir(lemma_savedir)
    text_files = collect_files(args.synset_text_files_dir)
    languages = get_languages_from_synset_text_files(args)
    """Check which languages have already been done."""
    completed_langs = [x.upper() for x in get_language_list(args)]
    languages = list(set(languages).difference(set(completed_langs)))
    language_chunks = utils.divide_index(len(languages), 50)
    for chunk in language_chunks:
        temp_languages = [languages[x] for x in chunk]
        lang_lamma_dict = {}
        dummy_counter = 0
        for file in text_files:
            """"""
            file1 = open(file, 'r')
            Lines = file1.readlines()
            for line in tqdm(Lines):
                line = line.replace("\n", "")
                line_info = line.split("~")  # we have to write some code because unfortunately some lemmas contain '~'
                lang = line_info[0]
                syn = line_info[1]
                lemma = "~".join(line_info[2:])
                lemma = lemma.lower()
                if lemma != "" and lang in temp_languages:
                    if lang not in lang_lamma_dict:
                        lang_lamma_dict[lang] = {lemma: syn}
                    elif lemma not in lang_lamma_dict[lang]:
                        lang_lamma_dict[lang][lemma] = syn  # to save memory we keep list as "_" delimited string!!!
                    elif syn not in lang_lamma_dict[lang][lemma]:
                        lang_lamma_dict[lang][lemma] = lang_lamma_dict[lang][lemma] + "_" + syn
            file1.close()
            dummy_counter += 1

        for lang, lemmasyns in tqdm(lang_lamma_dict.items()):
            dump_path = os.path.join(args.exp_dir, args.lemma_savedir, lang + ".pkl")
            utils.dump(lemmasyns, dump_path)

def get_language_list(args):
    """Get list of languages that have already been preprocessed."""
    files = collect_files(os.path.join(args.exp_dir, args.lemma_savedir))
    langs = []
    for file in files:
        lang_name = file.split('/')[-1].split('.')[0].lower()
        langs.append(lang_name)
    return langs

def get_syn2id_and_id2syn(args, languages, concept_syns):
    """Create syn2id and id2syn dictionaries and save to disk. Or load existing dictionaries."""
    id2syn_path = os.path.join(args.exp_dir, 'id2syn.pkl')
    syn2id_path = os.path.join(args.exp_dir, 'syn2id.pkl')
    if not os.path.exists(id2syn_path) or not os.path.exists(syn2id_path):
        if not os.path.exists(os.path.join(args.exp_dir, "concept_syns.pkl")) or not args.filter_syns_by_concept:
            """Collect all synsets from each language dictionary by iterating through the word2syn files"""
            syns = []
            for lang in languages:
                word2syn_file = os.path.join(args.exp_dir, args.lemma_savedir, lang.upper() + '.pkl')
                word2syn = utils.load(word2syn_file)
                for lemma, synset_str in tqdm(word2syn.items()):
                    synset_list = synset_str.split("_")
                    for syn in synset_list:
                        if args.filter_syns_by_concept:
                            if syn in concept_syns:
                                syns.append(syn)
                        else:
                            syns.append(syn)
                syns = list(set(syns))
        else:
            syns = load(os.path.join(args.exp_dir, "concept_syns.pkl"))
        print(len(syns))
        syns = sorted(syns)
        id2syn = {}
        syn2id = {}
        for i, syn in tqdm(enumerate(syns)):
            id2syn[i] = syn
            syn2id[syn] = i
        dump(id2syn, id2syn_path)
        dump(syn2id, syn2id_path)
    else:
        id2syn = load(id2syn_path)
        syn2id = load(syn2id_path)
    return syn2id, id2syn

def get_lemmas(args, languages, syn2id, id2syn, concept_syns):
    """We already have the original files pairing lemmas with their list of synsets,
       but we do this method so that we keep the structure consistent with wordnet version of code. Here,
       just load the original language json file, and replace the synset keys with their corresponding
       id."""
    concept_syn_dict = {}  # convert list to dummy dictionary for really fast checking if item is in list!!! (insanely slow without this)
    for syn in concept_syns:
        concept_syn_dict[syn] = ""
    lemma_folder = os.path.join(args.exp_dir, args.lemma_synIDdir)
    os.makedirs(lemma_folder, exist_ok=True)
    lemmas = {}
    lem_counter = 0
    for lang in tqdm(languages):
        lemma_path = os.path.join(lemma_folder, lang.upper() + ".pkl")
        if not os.path.exists(lemma_path):
            local_lemmas = {}
            word2syn_file = os.path.join(args.exp_dir, args.lemma_savedir, lang.upper() + '.pkl')
            word2syn = utils.load(word2syn_file)
            lang_lemma_count = len(word2syn)
            for lemma, synset_str in tqdm(word2syn.items()):
                synset_list = synset_str.split("_")
                """Filter synset list for concepts if we choose that option"""
                if args.filter_syns_by_concept:
                    new_list = []
                    for syn_ in synset_list:
                        try:
                            dum = concept_syn_dict[syn_]
                            new_list.append(syn_)
                        except:
                            """"""
                        # if syn_ in concept_syns:
                        #     new_list.append(syn_)
                    synset_list = new_list
                if lemma != "" and len(synset_list) >= 1:  # for some reason empty string leaked through and has over 5000 synsets from BabelNet!!!
                    synIDs = [syn2id[x] for x in synset_list]
                    local_lemmas[lemma] = synIDs
                elif lemma == "":
                    print(len(synset_list))
            print("Total lemmas in " + lang + ": " + str(lang_lemma_count))
            print("Lemmas in " + lang + " with concept synsets: " + str(len(local_lemmas)))
            lemmas[lang] = local_lemmas
            dump(local_lemmas, lemma_path)
        else:
            local_lemmas = load(lemma_path)
            lemmas[lang] = local_lemmas
            lem_counter += 1
            print(lem_counter)
    return lemmas

def get_all_edges_per_lang(args, languages):
    if not os.path.isdir(os.path.join(args.exp_dir, args.all_edges_dicts)):
        os.mkdir(os.path.join(args.exp_dir, args.all_edges_dicts))
    lemma_folder = os.path.join(args.exp_dir, args.lemma_synIDdir)
    ignore_lemmas = get_ignore_lemmas()
    global_max_syns = -1
    for lang in languages:
        lemma_path = os.path.join(lemma_folder, lang.upper() + ".pkl")
        lem_list = load(lemma_path)
        lang_edges = {}
        syn_counter = 0
        two_or_more_counter = 0
        dump_path = os.path.join(args.exp_dir, args.all_edges_dicts, lang + '.pkl')
        max_num_syns = -1
        for lem, syns in tqdm(lem_list.items()):
            if len(syns) >= 2 and lem not in ignore_lemmas:
                if len(syns) > max_num_syns:
                    max_num_syns = len(syns)
                """Get all pairwise combinations of synsets as edges"""
                edges = get_pairwise_edges(syns)
                for edge in edges:
                    """Actually we should just sort the edges based on number and always have that order!"""
                    edge = sorted(edge)
                    possibility1 = str(edge[0]) + '_' + str(edge[1])
                    if possibility1 in lang_edges:
                        lang_edges[possibility1] += 1
                    else:
                        lang_edges[possibility1] = 1
                two_or_more_counter += 1
            syn_counter += 1
        print(str(two_or_more_counter) + " lemmas with 2 or more...")
        print(len(lang_edges))
        print(max_num_syns)
        if max_num_syns > global_max_syns:
            global_max_syns = max_num_syns
        utils.dump(lang_edges, dump_path)
    print("Maximum number of synsets in a lexeme for (filtered) data is " + str(global_max_syns) + ".")

def build_colex_all_graph(args):
    """"""
    lang_edge_files = collect_files(os.path.join(args.exp_dir, args.all_edges_dicts))
    """Step 1: Load all edge files. Then DO NOT check for cross-lingual colexification. DO NOT filter by edges
     that don't occur with any other language.  WE KEEP ALL EDGES ACROSS ALL LANGUAGES. Set ALL weights to 1."""
    per_lang_binary_edges = {}
    for lang_file in tqdm(lang_edge_files):
        lang_edges = utils.load(lang_file)
        for edge in lang_edges:
            if edge in per_lang_binary_edges:
                per_lang_binary_edges[edge] += 1
            else:
                per_lang_binary_edges[edge] = 1
    print(str(len(per_lang_binary_edges)) + " total edges.")
    """Set all weights to 1."""
    for edge, weight in tqdm(per_lang_binary_edges.items()):
        per_lang_binary_edges[edge] = 1
    return per_lang_binary_edges

def write_edgelist_dict_to_edgelist(args, edge_dict):
    edgelist = []
    dump_path = os.path.join(args.exp_dir, args.edgelist_savename)
    for edgekey, weight in edge_dict.items():
        line = str(edgekey.split('_')[0]) + ' ' + str(edgekey.split('_')[1]) + ' ' + str(weight)
        edgelist.append(line)
    utils.write_file_from_list(edgelist, dump_path)

def synset_list_to_string_list(syns):
    strings = []
    for syn in syns:
        strings.append(syn._name)
    return strings

def get_pairwise_edges(overlap):
    """"""
    edges = []
    for i, node1 in enumerate(overlap):
        remaining_nodes = overlap[i + 1:]
        for node2 in remaining_nodes:
            edges.append([node1, node2])
    return edges

def get_word_embeddings_nodevectors(args, wordlist, lang, embed_filepath,
                                    model_type="ProNE", word2syn_dir="word2syns_by_lang"):
    import nodevectors
    node_model = None
    if model_type == 'ProNE':
        node_model = nodevectors.ProNE.load(embed_filepath)
    elif model_type == 'GGVec':
        node_model = nodevectors.GGVec.load(embed_filepath)
    elif model_type == 'Node2Vec':
        node_model = nodevectors.Node2Vec.load(embed_filepath)

    languages = get_language_list(args)
    concept_syns = get_concept_syns(args)
    syn2id, id2syn = get_syn2id_and_id2syn(args, languages, concept_syns)

    word2syn_file = os.path.join(word2syn_dir, lang.upper() + ".json")
    with open(word2syn_file) as json_file:
        word2syn = json.load(json_file)

    """For each word, we want to grab the syn embeddings and sum them up."""
    word_embs = {}
    for word in tqdm(wordlist):
        try:
            synsets = word2syn[word]
            word_exists = True
        except:
            word_exists = False
            synsets = None
        """Get the embedding"""
        if word_exists:
            word_emb = []  # reset to something
            for i, syn in enumerate(synsets):
                """Not all words are in BabelNet."""
                try:
                    syn_id = syn2id[syn]
                    temp_emb = node_model.predict(syn_id)
                    if len(word_emb) == 0:
                        word_emb = temp_emb
                    else:
                        word_emb += temp_emb
                except:
                    """Skip this sense"""

            if len(word_emb) >= 1:
                """Normalize the embedding"""
                word_emb = word_emb / np.linalg.norm(word_emb)
                word_embs[word] = word_emb
            else:
                word_embs[word] = None
        else:
            word_embs[word] = None
    return word_embs


def main(args):
    """"""
    if not os.path.exists(args.exp_dir):
        os.mkdir(args.exp_dir)
    if args.compute_edges:
        """Step 0: Create lemmasyns from BabelNet text files --> takes ~24 hours"""
        if args.get_lemmasyns:
            get_lemmasyns(args)
        concept_syns = get_concept_syns(args)
        """ Step 1: Get list of languages to check overlap with"""
        languages = get_language_list(args)
        """ Step 2: Create syn2id and id2syn dictionaries"""
        syn2id, id2syn = get_syn2id_and_id2syn(args, languages, concept_syns)

        if args.specific_languages != "":
            languages = args.specific_languages
            languages = languages.split("_")

        """ Step 3: Get all lemmas from each language and store as a dictionary with their synset ids"""
        if args.get_lemmas:
            lemmas = get_lemmas(args, languages, syn2id, id2syn, concept_syns)
        """ Step 4: Get edges"""
        get_all_edges_per_lang(args, languages)
        """Step 5: Build colexification graph."""
        all_edges = build_colex_all_graph(args)
        write_edgelist_dict_to_edgelist(args, all_edges)
    else:
        """Step 5: Build colexification graph."""
        all_edges = build_colex_all_graph(args)
        write_edgelist_dict_to_edgelist(args, all_edges)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Arguments to build colexification graph from BabelNet')
    parser.add_argument('--exp_dir', type=str, default='/ws/ifp-54_2/hasegawa/harvill2/Summer_2022/Syn2Vec_private/src/syn2vec/colex_test_run')
    parser.add_argument('--specific_languages', type=str, default='')  # just for fixing problems with specific langs, ru_hy had issues
    parser.add_argument('--filter_syns_by_concept', type=str2bool, default=True)  # only keep synsets that are concepts
    parser.add_argument('--synset_text_files_dir', type=str, default='/ws/ifp-54_2/hasegawa/harvill2/Fall_2021/NAACL2022/synset_text_files/')
    parser.add_argument('--synset_types_files_dir', type=str, default='/ws/ifp-54_2/hasegawa/harvill2/Fall_2021/NAACL2022/BabelNet_Synset_Types/')
    parser.add_argument('--lemma_savedir', type=str, default='lemmas')
    parser.add_argument('--lemma_synIDdir', type=str, default='lemmas_synID')
    parser.add_argument('--all_edges_dicts', type=str, default='all_edges')
    parser.add_argument('--get_lemmasyns', type=str2bool, default=True)  # get lemmasyns first (takes ~24 hours)
    parser.add_argument('--get_lemmas', type=str2bool, default=True)  # get lemmas (False after doing it once)
    parser.add_argument('--compute_edges', type=str2bool, default=True)  # set to False if you've run that part already, very fast now
    parser.add_argument('--edgelist_savename', type=str, default='colex_all.edgelist')
    args = parser.parse_args()
    main(args)