"""
Test script
"""

import pickle
import zipfile

zip_path = r"C:\Users\denis\Downloads\shapelets_bulk.zip"
pkl_name = r"North Carolina_Beaufort_6_shapelets.pkl_2004_000.pkl"   # exact path inside the zip

with zipfile.ZipFile(zip_path, "r") as z:
    with z.open(pkl_name) as f:
        data = pickle.load(f)