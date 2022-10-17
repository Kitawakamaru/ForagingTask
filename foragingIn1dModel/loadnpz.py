import numpy as np

#load npz files
npz = np.load('20221014T114805_R7DV10T2RSFalseRFFalse_log.npz', allow_pickle = True)

#Confirm npz files
#print(npz.files)
header = npz['header']
data = npz['data']
id = npz['id']
t_ends = npz['t_ends']

#0:ticks_in_task_state, 1:ticks_in_social_state, 2:ticks_in_terrain_state, 3:n_visits_to_food, 4:n_visits_to_home, 5:n_ticks_not_moving
#6:n_total_ticks, 7:n_success_tunnel_passages, 8:n_fail_tunnel_passages, 9:n_tunnel_entry, 10:n_tunnel_exit
a = 4
#number of agent
N = data.shape[1]

for i in range(N):
    print(data[0, i, a])