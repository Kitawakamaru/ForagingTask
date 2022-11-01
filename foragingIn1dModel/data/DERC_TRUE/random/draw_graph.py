from pydoc import pathdirs
from re import I
from unicodedata import name
import numpy as np
import os
import statistics


def GetPath():
    path = os.getcwd()
    path_dir = R"{}".format(path)

    return path_dir
    #end function

#Load npz files in folder
def Loadnpz(path_dir):
    files = os.listdir(path_dir)
    files_npz = []
    N_files = 0

    for file in files:
        base, ext = os.path.splitext(file)
        if ext == '.npz':
            files_npz.append(file)

    return files_npz
    #end function


def GetNumberofFiles(path_dir):
    files_npz = Loadnpz(path_dir)
    N_files = len(files_npz)

    return N_files
    #end function


#Create whlole data list
def CreateWholeDataList(path_dir):
    files_npz = Loadnpz(path_dir)
    data = []
    
    for file_npz in files_npz:
        npz = np.load('{}'.format(file_npz), allow_pickle = True)
        #header = npz['header']
        data_temp = npz['data']
        #id = npz['id']
        #t_ends = npz['t_ends']
        data.append(data_temp)

    return data
    #end function


#create a special data list of number of agents and data
#[premise] No files more than 8 in folder 
def CreateSpecialDataListperAgent(path_dir, N_agents, n_data):
    '''
    return the data list which is divided into the list per a agent
    can use for the analitics of each agents
    '''
    files_npz = Loadnpz(path_dir)
    data_list_temp = []
    data_list = []

    for file_npz in files_npz:
        npz = np.load('{}'.format(file_npz), allow_pickle = True)
        data_npz = npz['data']
        if data_npz.shape[1] == N_agents:
            header = npz['header']
            data_name = header[n_data]
            N_repeat = data_npz.shape[0]
            for i in range(N_agents):
                for j in range(N_repeat):
                    data_list_temp.append(data_npz[j, i, n_data])
                data_list.append(data_list_temp)
                #empty the temporary list
                data_list_temp = []
    
    return data_name, data_list
    #end function


#create a special data list of number of agents and data
#[premise] No files more than 8 in folder 
def CreateSpecialDataListperSimulation(path_dir, N_agents, n_data):
    '''
    return the data list which is divided into the list per a agent
    can use for the analitics of each agents
    '''
    files_npz = Loadnpz(path_dir)
    data_list_temp = []
    data_list = []

    for file_npz in files_npz:
        npz = np.load('{}'.format(file_npz), allow_pickle = True)
        data_npz = npz['data']
        if data_npz.shape[1] == N_agents:
            header = npz['header']
            data_name = header[n_data]
            N_repeat = data_npz.shape[0]
            for i in range(N_repeat):
                for j in range(N_agents):
                    data_list_temp.append(data_npz[i, j, n_data])
                data_list.append(data_list_temp)
                #empty the temporary list
                data_list_temp = []
    
    return data_name, data_list, N_repeat
    #end function


#calculate total number of data per simulations 
#ex)return the data list of "food collected" in a simulation
def CalcTotalNumberofData(path_dir, N_agents, n_data):
    _, data_list, N_repeat = CreateSpecialDataListperSimulation(path_dir, N_agents, n_data)
    data_list_total = []
    data_total_temp = 0
    average_in_simulation = 0
    
    #calculate total per simulation
    for i in range(N_repeat):
        data_total_temp = sum(data_list[i])
        data_list_total.append(data_total_temp)

    #calculate average through a simulation
    average_in_simulation = statistics.mean(data_list_total)

    return data_list_total, average_in_simulation 
    #end function


#draw a single boxplot
def DrawBoxplot(path_dir, N_agents, n_data):
    import matplotlib.pyplot as plt
    data_list, _ = CalcTotalNumberofData(path_dir, N_agents, n_data)

    fig, ax = plt.subplots()
    bp = ax.boxplot(data_list)
    plt.title('food collected')
    plt.grid()

    plt.show()
    #end function


#draw multiple boxplots
def DrawMultipleBoxplot(path_dir, n_data, graph_title, y_label):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list = []
    data_list_temp = []
    for N_agent in range(2, N_agents+2):
        data_list_temp, _ = CalcTotalNumberofData(path_dir, N_agent, n_data)
        data_list.append(data_list_temp)
        #empty the list
        data_list_temp = []

    #draw boxplots
    x_label = []
    fig, ax = plt.subplots()
    bp = ax.boxplot(data_list)
    plt.grid()
    for i in range(2, N_agents+2):
        x_label.append('{}'.format(i))
    ax.set_xticklabels(x_label)
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    plt.title(graph_title)
    plt.show()
    #end function



#config===================================================================
#the path of current directry is got automatically by the function GetPath 
#path_dir = R"C:\Users\川北　拓穂\Desktop\採餌タスクプログラム\foragingIn1dModel\data\DERC_TRUE\speed"
N_agents = 4
n_data = 11
graph_title = 'random'
y_label = 'DERC signal'
'''
data number list!
0:ticks_in_task_state, 1:ticks_in_social_state, 2:ticks_in_terrain_state, 3:n_visits_to_food, 4:n_visits_to_home, 5:n_ticks_not_moving
#6:n_total_ticks, 7:n_success_tunnel_passages, 8:n_fail_tunnel_passages, 9:n_tunnel_entry, 10:n_tunnel_exit, 11n_derc_recieved_lv1
'''
#================================================================================
#main============================================================================
path_dir = GetPath()

DrawMultipleBoxplot(path_dir, n_data, graph_title, y_label)
#data_name, data_list = CreateSpecialDataListperAgent(path_dir, N_agents, n_data)
#print(data_name, data_list)