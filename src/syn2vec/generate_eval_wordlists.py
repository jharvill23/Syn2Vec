import argparse
import os.path
import utils

def main(args):
    config = utils.get_config()
    langs = config.eval_languages
    os.makedirs(args.output_dir, exist_ok=True)
    for lang in langs:
        word_pairs, unique_words = utils.get_multisimlex(lang=lang)
        dump_path = os.path.join(args.output_dir, lang + ".txt")
        utils.write_file_from_list(unique_words, dump_path)

def parse_args():
    parser = argparse.ArgumentParser(description="Save evaluation words to text file to query BabelNet.")
    parser.add_argument('--output_dir', nargs='?',
                        default='/ws/ifp-54_2/hasegawa/harvill2/Summer_2022/Syn2Vec_private/src/syn2vec/query_word_lists',
                        help='Directory to dump the evaluation words for each language.')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
