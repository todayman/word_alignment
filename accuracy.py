#! /usr/bin/env python3

import argparse
from itertools import chain


# Returns a dictionary from source index -> set of all target indices
# aligned to that source index
def make_alignments_from_line(line):
    alignments = {}
    words = line.split()
    for w in words:
        numerals = list(chain.from_iterable([x.split('-') for x in w.split('?')]))
        first_num = int(numerals[0])
        if first_num not in alignments:
            alignments[first_num] = set()
        alignments[first_num].add(int(numerals[-1]))
    return alignments

parser = argparse.ArgumentParser(
    description='Compute the accuracy of an aligment against a reference')

parser.add_argument('reference',
                    type=argparse.FileType('r'), help='reference alignment')
parser.add_argument('test_alignment',
                    type=argparse.FileType('r'), help='alignment to evaluate')

args = parser.parse_args()


success_count = 0
total_count = 0
for (ref_line, test_line) in zip(args.reference, args.test_alignment):
    ref_aligns = make_alignments_from_line(ref_line)
    test_aligns = make_alignments_from_line(test_line)

    for (ref_source, ref_target) in ref_aligns.items():
        test_targets = test_aligns[ref_source]
        if test_targets == ref_target:
            success_count += len(ref_target)
        else:
            for particular_align in ref_target:
                if particular_align in test_targets:
                    success_count += 1
        total_count += len(ref_target)


print('Matched ' + str(success_count) + ' out of ' +
      str(total_count) + ' alignments')
print(str(float(success_count) / float(total_count) * 100) + '%')
