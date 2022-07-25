import argparse
import nodevectors
import csrgraph as cg
from time import time

def main(args):
    print("Loading graph...")
    G = cg.read_edgelist(args.input, directed=False, sep=' ')  # all graphs are undirected
    print("Done.")
    node_model = nodevectors.ProNE(n_components=300)
    start_time = time()
    print("Starting node embedding...")
    node_model.fit(G)
    print("Done.")
    total_minutes = (time() - start_time)/60
    print(str(total_minutes) + " total minutes for node embedding process.")
    node_model.save(args.output)
    print("Saved model to " + args.output)

def parse_args():
    '''
    Parses the ProNE arguments.
    '''
    parser = argparse.ArgumentParser(description="Run ProNE.")

    parser.add_argument('--input', nargs='?', default='dummy.edgelist', help='Input graph path')

    parser.add_argument('--output', nargs='?', default='dummy', help='ProNE .zip path')

    parser.add_argument('--dimensions', type=int, default=300,
                        help='Number of dimensions. Default is 300 to match fastText.')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
