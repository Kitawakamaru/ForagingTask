import numpy as np

#load npz files
npz = np.load('20221019T163431_R7DV5T2RSFalseRFFalse_log.npz', allow_pickle = True)

#Confirm npz files
#print(npz.files)
header = npz['header']
data = npz['data']
id = npz['id']
t_ends = npz['t_ends']

#0:ticks_in_task_state, 1:ticks_in_social_state, 2:ticks_in_terrain_state, 3:n_visits_to_food, 4:n_visits_to_home, 5:n_ticks_not_moving
#6:n_total_ticks, 7:n_success_tunnel_passages, 8:n_fail_tunnel_passages, 9:n_tunnel_entry, 10:n_tunnel_exit, 11n_derc_point_lv1
a = 4
#number of agent
N = data.shape[1]

#for j in range(7):
#    print('agent', j)
#    for i in range(1):
#        print(data[i, j, 8])
#        print(data[i, j, 11])


#for i in range(N):
#    print(data[0, i, a])


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
