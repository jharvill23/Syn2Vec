import os
import argparse
import utils
from utils import *
import colexAllBabelNet


def get_colex_all_embeddings(wordlist, lang, args):
    local_save_folder = os.path.join(args.local_save_folder, lang)
    embed_filepath = os.path.join(args.exp_dir, args.embed_file)
    print("####################")
    print("######## " + lang.upper() + " ########")
    print("####################")
    print(len(wordlist))
    print("Getting word embeddings from synset embeddings...")
    embeddings = colexAllBabelNet.get_word_embeddings_nodevectors(args, wordlist, lang=lang,
                                                                  embed_filepath=embed_filepath,
                                                                  model_type=args.NODE_MODEL_TYPE,
                                                                  word2syn_dir=args.word2syn_dir)
    print(len(embeddings))
    os.makedirs(local_save_folder, exist_ok=True)
    print("Writing word embeddings to disk...")
    num_words_with_embeds = 0
    for word in tqdm(wordlist):
        embed = embeddings[word]
        if not embed is None:
            dump_path = os.path.join(local_save_folder, word + '.pkl')
            dump(embed, dump_path)
            num_words_with_embeds += 1
    print(num_words_with_embeds)
    print("Done.")


def main(args):
    languages = args.languages
    languages = languages.split("_")
    if not os.path.isdir(args.local_save_folder):
        os.mkdir(args.local_save_folder)
    """First, get the set of words to grab vectors for based on the options"""
    for lang in languages:
        unique_words = None
        word_pairs, unique_words = get_multisimlex(lang)
        """Next, get the vectors"""
        get_colex_all_embeddings(unique_words, lang, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Arguments to get word embedding vectors')
    parser.add_argument('--languages', type=str, default='en_ar_es_fi_fr_he_pl_ru_zh')  # en_ar_es_fi_fr_he_pl_ru_zh
    parser.add_argument('--embed_file', type=str, default='colex_all.zip')
    parser.add_argument('--local_save_folder', type=str, default='word_vectors')
    parser.add_argument('--NODE_MODEL_TYPE', type=str, default='ProNE')
    parser.add_argument('--exp_dir', type=str, default='colex_test_run')
    parser.add_argument('--word2syn_dir', type=str, default='word2syns_by_lang')
    parser.add_argument('--synset_text_files_dir', type=str, default='/ws/ifp-54_2/hasegawa/harvill2/Fall_2021/NAACL2022/synset_text_files/')
    parser.add_argument('--synset_types_files_dir', type=str, default='/ws/ifp-54_2/hasegawa/harvill2/Fall_2021/NAACL2022/BabelNet_Synset_Types/')
    parser.add_argument('--lemma_savedir', type=str, default='lemmas')
    parser.add_argument('--lemma_synIDdir', type=str, default='lemmas_synID')
    args = parser.parse_args()
    main(args)