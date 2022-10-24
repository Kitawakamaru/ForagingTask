from re import I
import numpy as np
import os

'''
#code for a single file
#load npz files
npz = np.load('20221020T171715_R2DV5T0RSFalseRFFalse_log.npz', allow_pickle = True)

#Confirm npz files
#print(npz.files)
header = npz['header']
data = npz['data']
id = npz['id']
t_ends = npz['t_ends']

#0:ticks_in_task_state, 1:ticks_in_social_state, 2:ticks_in_terrain_state, 3:n_visits_to_food, 4:n_visits_to_home, 5:n_ticks_not_moving
#6:n_total_ticks, 7:n_success_tunnel_passages, 8:n_fail_tunnel_passages, 9:n_tunnel_entry, 10:n_tunnel_exit, 11n_derc_recieved_lv1
a = 4
#number of agent
N = data.shape[1]

N_recived = 0
N_send = 0

for j in range(7):
    print('agent', j)
    for i in range(1):
        print(data[i, j, 8])
        print(data[i, j, 11])
        print(data[i, j, 12])
'''

#code for multiple files
path_dir = R"C:\Users\t94ka\OneDrive\デスクトップ\Foragin Task\ForagingTask\foragingIn1dModel"
files = os.listdir(path_dir)
files_npz = []

#make the list is consisted from only npz files
for file in files:
    base, ext = os.path.splitext(file)
    if ext == '.npz':
        files_npz.append(file)

n_solution = 0
for file_npz in files_npz:
    npz = np.load('{}'.format(file_npz), allow_pickle = True)
    
    data = npz['data']

    N_agents = data.shape[1]
    N_simulation = data.shape[0]
    if N_agents == 2:
        print('=================Solution number is', n_solution, '=====================')
        n_solution += 1
    for i in range(N_agents):
        print('agent num is', i)
        for j in range(N_simulation):
            print(data[j, i, 8])
            print(data[j, i, 11])
            print(data[j, i, 12])
            



