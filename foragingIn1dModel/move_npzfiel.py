

import os
import glob
import shutil

path_dir = R"C:\Users\t94ka\OneDrive\デスクトップ\Foragin Task\ForagingTask\foragingIn1dModel"
move_dir = R"C:\Users\t94ka\OneDrive\デスクトップ\Foragin Task\ForagingTask\foragingIn1dModel\data"
files = os.listdir(path_dir)
files_npz = []

#make the list is consisted from only npz files
for file in files:
    base, ext = os.path.splitext(file)
    if ext == '.npz':
        files_npz.append(file)

for file_npz in files_npz:
    join_path = os.path.join(path_dir, file_npz)
    move_path = os.path.join(move_dir, file_npz)

    shutil.move(join_path, move_path)






