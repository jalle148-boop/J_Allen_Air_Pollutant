# -*- coding: utf-8 -*-
"""
Helpers
"""

import pickle
import zipfile


# loading a single dataset

def load_single_pkl(file_path):

    with open(file_path, "r") as f:
        data = pickle.load(f)