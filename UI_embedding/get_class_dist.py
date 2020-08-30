from sentence_transformers import SentenceTransformer
import json
import numpy as np
import argparse
import torch
import os
from dataset.rico_utils import get_all_texts_from_rico_screen, get_all_labeled_uis_from_rico_screen, ScreenInfo
from dataset.rico_dao import load_rico_screen_dict


parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dataset", required=True, type=str, help="dataset to precompute embeddings for")

args = parser.parse_args()


classes_dict = {}
for i in range(32):
    classes_dict[i] = 0

other_classes_dict = {}

for package_dir in os.listdir(args.dataset):
    if os.path.isdir(args.dataset + '/' + package_dir):
        # for each package directory
        for trace_dir in os.listdir(args.dataset + '/' + package_dir):
            if os.path.isdir(args.dataset + '/' + package_dir + '/' + trace_dir) and (not trace_dir.startswith('.')):
                for view_hierarchy_json in os.listdir(args.dataset + '/' + package_dir + '/' + trace_dir + '/' + 'view_hierarchies'):
                    if view_hierarchy_json.endswith('.json') and (not view_hierarchy_json.startswith('.')):
                        json_file_path = args.dataset + '/' + package_dir + '/' + trace_dir + '/' + 'view_hierarchies' + '/' + view_hierarchy_json
                        try:
                            with open(json_file_path) as f:
                                rico_screen = load_rico_screen_dict(json.load(f))
                                labeled_uis = get_all_labeled_uis_from_rico_screen(rico_screen, True)
                                for ui in labeled_uis:
                                    classes_dict[ui[1]] += 1
                                    if ui[1]==0:
                                        the_class = ui[3].split(".")[-1]
                                        if the_class in other_classes_dict:
                                            other_classes_dict[the_class] += 1
                                        else:
                                            other_classes_dict[the_class] = 1
                        except TypeError as e:
                            print(str(e) + ': ' + args.dataset)
                            labeled_text = []
print(classes_dict)

for key,value in other_classes_dict.items():
    if value > 1000:
        print(key)