import os
import argparse
import utils
from utils import *
import numpy as np
from scipy.spatial.distance import cosine
import scipy
from sklearn.decomposition import PCA


def post_process(embed, mean_center=False, normalize=True):
    # we had mean_center=True, but changed to False for latest experiments
    if normalize:
        embed = embed / np.linalg.norm(embed)
    if mean_center:
        embed = embed - np.mean(embed)
    if normalize:
        embed = embed / np.linalg.norm(embed)
    return embed

def get_PCA_(x, num_components, mean_center=True):
    """Shape is batch, feat"""
    if mean_center:
        mean = np.mean(x, axis=0)
        x = x - mean[None, :]
    pca = PCA(n_components=num_components, svd_solver='full')
    new_x = pca.fit_transform(x)
    return new_x

def get_PCA(embeddings):
    """"""
    vectors = []
    for word, embed in embeddings.items():
        vectors.append(embed)
    """Let's replace the vectors with first N PCA components"""
    vectors = np.asarray(vectors)
    num_components = np.min((vectors.shape[1], vectors.shape[0]))
    vectors = get_PCA_(vectors, num_components=num_components)
    count = 0
    new_embeds = {}
    for word, embed in embeddings.items():
        new_embeds[word] = vectors[count]
        count += 1
    return new_embeds

def get_embeddings(args, unique_words, lang, do_PCA=True):
    embed_dir = os.path.join(args.word_vectors_dir, lang)
    embedding_files = collect_files(embed_dir)
    embeddings = {}
    for file in embedding_files:
        word = file.split('/')[-1].split('.')[0]
        if word in unique_words:
            embed = load(file)
            embed = post_process(embed)
            embeddings[word] = embed
    if do_PCA:
        embeddings = get_PCA(embeddings)
    return embeddings

def spearman_rank_correlation(LSIM_pairs, embeddings, rank_method):
    """Now we want to get the cosine distance between the embeddings for each pair"""
    multisimlex_list = []
    ground_truth_scores = []
    our_scores = []
    no_embedding_count = 0
    saved_similarity_scores = {}
    for key, dictionary in LSIM_pairs.items():
        try:
            word1 = dictionary['word1']
            word2 = dictionary['word2']
            embedding1 = embeddings[word1]
            embedding2 = embeddings[word2]
            embed_similarity = 1 - cosine(embedding1, embedding2)
            dictionary['embed_similarity'] = embed_similarity
            multisimlex_list.append(dictionary)
            ground_truth_scores.append(dictionary['total_score'])
            our_scores.append(embed_similarity)
            save_key = word1 + "_" + word2
            saved_similarity_scores[save_key] = {"ground_truth": dictionary['total_score'],
                                                 "our_score": embed_similarity}
        except:
            no_embedding_count += 1
    total_pairs = len(LSIM_pairs)
    completed_pairs = total_pairs - no_embedding_count
    print(str(completed_pairs) + " / " + str(total_pairs) + " pairs had embeddings for both words.")
    ground_truth_scores = np.asarray(ground_truth_scores)
    our_scores = np.asarray(our_scores)
    ground_truth_ranks = scipy.stats.rankdata(ground_truth_scores, method=rank_method)
    our_ranks = scipy.stats.rankdata(our_scores, method=rank_method)
    spearman = scipy.stats.spearmanr(ground_truth_ranks, our_ranks).correlation
    return spearman, completed_pairs, saved_similarity_scores


def main(args):
    languages = args.languages
    languages = languages.split("_")
    results = {}
    all_sim_scores = {}
    for lang in languages:
        word_pairs, unique_words = get_multisimlex(lang)
        embeddings = get_embeddings(args, unique_words, lang=lang, do_PCA=args.PCA)
        print(len(embeddings))
        """Compute spearman rank for each layer number in each method"""
        score, num_completed_pairs, sim_scores = spearman_rank_correlation(LSIM_pairs=word_pairs,
                                                                           embeddings=embeddings,
                                                                           rank_method=args.rank_method)
        print(lang + ": " + str(score))
        local_result = {"spearman_rank_corr": score, "num_pairs": num_completed_pairs}
        results[lang] = local_result
        all_sim_scores[lang] = sim_scores



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Arguments to evaluate on LSIM task')
    parser.add_argument('--eval_word_type', type=str, default='LSIM')
    parser.add_argument('--languages', type=str, default='ar_en_es_fi_fr_he_pl_ru_zh')  # ar_en_es_fi_fr_he_pl_ru_zh
    parser.add_argument('--word_vectors_dir', type=str, default='word_vectors')
    parser.add_argument('--rank_method', type=str, default='average')
    parser.add_argument('--PCA', type=str2bool, default=True)
    args = parser.parse_args()
    main(args)


