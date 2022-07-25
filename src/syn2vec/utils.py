import os
import joblib
import numpy as np
from tqdm import tqdm
import os
import json
import importlib
from tokenizers import Tokenizer
import argparse
from easydict import EasyDict as edict
import yaml
from pprint import pprint
from nltk.corpus import wordnet
from copy import deepcopy
import fasttext.util
from scipy.spatial.distance import cosine
import torch.nn as nn
import torch
import networkx
import igraph
import re
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer


def get_config():
    config = edict(yaml.load(open('config.yml'), Loader=yaml.SafeLoader))
    return config

def collect_files(directory):
    all_files = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            filename = os.path.join(path, name)
            all_files.append(filename)
    return all_files

def get_multisimlex(lang):
    file1 = None
    print('Getting MultiSimLex data...')
    if lang == 'en':
        file1 = open('datasets/multisimlex/ENG.csv', 'r')
    elif lang == 'ar':
        file1 = open('datasets/multisimlex/ARA.csv', 'r')
    elif lang == 'zh':
        file1 = open('datasets/multisimlex/CMN.csv', 'r')
    elif lang == 'fi':
        file1 = open('datasets/multisimlex/FIN.csv', 'r')
    elif lang == 'fr':
        file1 = open('datasets/multisimlex/FRA.csv', 'r')
    elif lang == 'he':
        file1 = open('datasets/multisimlex/HEB.csv', 'r')
    elif lang == 'pl':
        file1 = open('datasets/multisimlex/POL.csv', 'r')
    elif lang == 'ru':
        file1 = open('datasets/multisimlex/RUS.csv', 'r')
    elif lang == 'es':
        file1 = open('datasets/multisimlex/SPA.csv', 'r')

    Lines = file1.readlines()
    word_pairs = {}
    unique_words = []
    messed_up_annotation_count = 0
    for line in tqdm(Lines[1:]):
        line = line[:-1]  # remove the newline character
        pieces = line.split(',')
        ID = pieces[0]
        word_pairs[ID] = {'word1': pieces[1],
                          'word2': pieces[2],
                          'POS_tag': pieces[3],
                          'annotator_scores': pieces[4:]}
        try:
            score_list = []
            for x in word_pairs[ID]['annotator_scores']:
                try:
                    score_list.append(float(x))
                except:
                    """"""
            total_score = np.mean(np.asarray(score_list))
            # total_score = sum([float(x) for x in word_pairs[ID]['annotator_scores']])
            for word in [word_pairs[ID]['word1'], word_pairs[ID]['word2']]:
                if word not in unique_words:
                    unique_words.append(word)
            word_pairs[ID]['total_score'] = total_score
        except:
            """There was a missing score"""
            messed_up_annotation_count += 1
    print("Messed up annotation count: " + str(messed_up_annotation_count))
    return word_pairs, unique_words

def get_crosslingual_multisimlex(lang_pair):
    config = get_config()
    file1 = None
    print('Getting Cross-Lingual MultiSimLex data...')
    multisimlex_code_dict = {'ar': 'ARA', 'en': 'ENG', 'es': 'SPA', 'fi': 'FIN', 'fr': 'FRA',
                             'he': 'HEB', 'pl': 'POL', 'ru': 'RUS', 'zh': 'CMN'}
    flip_code_dict = {'ARA': 'ar', 'ENG': 'en', 'SPA': 'es', 'FIN': 'fi', 'FRA': 'fr', 'HEB': 'he',
                      'POL': 'pl', 'RUS': 'ru', 'CMN': 'zh'}
    lang1, lang2 = lang_pair.split('_')
    # lang1, lang2 = sorted([lang1, lang2])
    file1_ending = multisimlex_code_dict[lang1] + "-" + multisimlex_code_dict[lang2] + '.csv'
    file2_ending = multisimlex_code_dict[lang2] + "-" + multisimlex_code_dict[lang1] + '.csv'
    cross_lingual_file1 = os.path.join(config.directories.cross_lingual_multisimlex, file1_ending)
    cross_lingual_file2 = os.path.join(config.directories.cross_lingual_multisimlex, file2_ending)
    if os.path.exists(cross_lingual_file1):
        file1 = open(cross_lingual_file1, 'r')
        src = lang1
        tgt = lang2
    elif os.path.exists(cross_lingual_file2):
        file1 = open(cross_lingual_file2, 'r')
        src = lang2
        tgt = lang1
    else:
        return None, None, None, None, None

    Lines = file1.readlines()
    word_pairs = {}
    unique_words_src = []
    unique_words_tgt = []
    messed_up_annotation_count = 0
    header = Lines[0]
    src_lang = flip_code_dict[header.split(",")[1]]
    tgt_lang = flip_code_dict[header.split(",")[2]]
    assert src == src_lang
    assert tgt == tgt_lang
    for line in tqdm(Lines[1:]):
        line = line[:-1]  # remove the newline character
        pieces = line.split(',')
        ID = pieces[0]
        word_pairs[ID] = {'word1': pieces[1],
                          'word2': pieces[2],
                          'POS_tag': pieces[3],
                          'annotator_score': pieces[4]}
        try:
            total_score = float(word_pairs[ID]['annotator_score'])
            # for word in [word_pairs[ID]['word1'], word_pairs[ID]['word2']]:
            if word_pairs[ID]['word1'] not in unique_words_src:
                unique_words_src.append(word_pairs[ID]['word1'])
            if word_pairs[ID]['word2'] not in unique_words_tgt:
                unique_words_tgt.append(word_pairs[ID]['word2'])
            word_pairs[ID]['total_score'] = total_score
        except:
            """There was a missing score"""
            messed_up_annotation_count += 1
    print("Messed up annotation count: " + str(messed_up_annotation_count))
    return word_pairs, unique_words_src, unique_words_tgt, src, tgt

def dynamic_import(module):
    module_path, module_class = module.rsplit('.', maxsplit=1)
    module = importlib.import_module(module_path)
    module_class = getattr(module, module_class)
    return module_class

def load(file_path, file_type=None):
    if file_type == 'json' or file_path.endswith('.json'):
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
    elif file_type == 'pkl' or file_path.endswith('.pkl'):
        import pickle
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
    else:
        raise ValueError('file type {file_path} not implemented')

    return data

def dump(data, file_path, file_type=None):
    if file_type == 'json' or file_path.endswith('.json'):
        import json
        with open(file_path, 'w') as f:
            json.dump(data, f)
    elif file_type == 'pkl' or file_path.endswith('.pkl'):
        import pickle
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    else:
        raise ValueError('file type {file_path} not implemented')

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def divide_index(size, n):
    # evenly divide the index set to n parts
    chunk_size = size // n + 1
    x = [list(range(i, min(i+chunk_size, size))) for i in range(0, size, chunk_size)]
    return x

def parse_config(args):
    config_path = args.config
    config = edict(yaml.load(open(config_path), Loader=yaml.SafeLoader))
    config.specific_args = edict(vars(args))
    if args.use_half:
        config.use_half = args.use_half
    pprint(config)
    return config

def write_file_from_list(list, path):
    with open(path, 'w') as f:
        for item in list:
            f.write("%s\n" % item)

def wordnet_lang_converter(lang):
    if lang == 'en':
        return "eng"
    elif lang == 'ar':
        return "arb"
    elif lang == 'zh':
        return "cmn"
    elif lang == 'fi':
        return "fin"
    elif lang == 'fr':
        return "fra"
    elif lang == 'he':
        return "heb"
    elif lang == 'pl':
        return "pol"
    elif lang == 'ru':
        return "rus"
    elif lang == 'es':
        return "spa"

def read_edgelist(edgelist_file, weighted=True):
    '''
    Reads the input edgelist_file into a dictionary.
    '''
    file1 = open(edgelist_file, 'r')
    Lines = file1.readlines()
    edgelist = {}  # initialize edgelist
    for line in tqdm(Lines):
        line = line[:-1]  # remove the newline character
        pieces = line.split(" ")
        node1 = pieces[0]
        node2 = pieces[1]
        weight = float(pieces[2])
        edge = node1 + "_" + node2
        if weighted:
            edge_weight = weight
        else:
            edge_weight = 1.0
        edgelist[edge] = edge_weight
    return edgelist






