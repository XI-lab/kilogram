from __future__ import division
import argparse


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gold-file', required=True,
                    help='path to the file with the ground truth')
parser.add_argument('--eval-file', required=True,
                    help='path to the file to evaluate')
parser.add_argument('--out-file', default="not_ranked.txt",
                    help='path to the file to output non-ranked items')

args = parser.parse_args()


gold_data = {}

for line in open(args.gold_file):
    correct, uri_equals, full_url, token, uri, sentence = line.strip().split('\t')
    gold_data[(token, uri, sentence)] = int(correct)


not_ranked_file = open(args.out_file, 'w')


labels = []
for line in open(args.eval_file):
    token, uri, sentence = line.strip().split('\t')
    if (token, uri, sentence) in gold_data:
        labels.append(gold_data[(token, uri, sentence)])
    else:
        not_ranked_file.write('\t'.join([token, uri, sentence])+'\n')

not_ranked_file.close()

print('Precision:', sum(labels)/len(labels))
