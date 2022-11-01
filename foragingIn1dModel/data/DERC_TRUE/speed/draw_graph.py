from pydoc import pathdirs
from re import I
from unicodedata import name
import numpy as np
import os
import statistics
import math

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


#calculate personal data per agent
def CalcPersonalData(path_dir, N_agents, n_data):
    _, data_list = CreateSpecialDataListperAgent(path_dir, N_agents, n_data)
    data_total_temp = 0
    data_average_temp = 0
    data_list_total = []
    data_list_average = []

    #calculate total data of each agent
    for i in range(N_agents):
        data_total_temp = sum(data_list[i])
        data_average_temp = statistics.mean(data_list[i])
        data_list_total.append(data_total_temp)
        data_list_average.append(data_average_temp)

    return data_list_total, data_list_average


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


#calculate average of an agent in one simulation by using CalcTotalNumberofData
def CalcAverageofData(path_dir, N_agents, n_data):
    _, average_in_simulation = CalcTotalNumberofData(path_dir, N_agents, n_data)

    data_average = average_in_simulation/N_agents

    return data_average


def CalcDsipersionofData(path_dir, N_agents, n_data):
    _, data_list, N_repeat = CreateSpecialDataListperSimulation(path_dir, N_agents, n_data)
    #data list of dsipersion
    ds_list = []
    ds_temp = 0
    average_in_simulation = 0

    #calculate dsipersion of data
    for i in range(N_repeat):
        ds_temp = statistics.pvariance(data_list[i])
        ds_list.append(ds_temp)
    
    #calculate average
    average_in_simulation = statistics.mean(ds_list)

    return ds_list, average_in_simulation


#calculate 2D data(ticks in tunnel)
def CalcTotalDataof2DList(path_dir, N_agents, n_data):
    _, data_list, N_repeat = CreateSpecialDataListperSimulation(path_dir, N_agents, n_data)
    data_total_index_0 = 0
    data_total_index_1 = 0
    data_average_index_0 = []
    data_average_index_1 = []

    #calculate average of each index per agent in one simulation
    for i in range(N_repeat):
        for j in range(N_agents):
            data_total_index_0 += data_list[i][j][0]
            data_total_index_1 += data_list[i][j][1]
    data_average_index_0 = data_total_index_0/( N_agents * N_repeat )
    data_average_index_1 = data_total_index_1/( N_agents * N_repeat )

    print(data_average_index_0, data_average_index_1)

    return data_average_index_0, data_average_index_1


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
def DrawMultipleBoxplot(path_dir, n_data, graph_title, y_label, y_min, y_max):
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
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    plt.title(graph_title)
    plt.show()
    #end function


#draw a single boxplot
def DrawDsipersionBoxplot(path_dir, N_agents, n_data, graph_title, y_label):
    import matplotlib.pyplot as plt
    data_list, _ = CalcDsipersionofData(path_dir, N_agents, n_data)

    fig, ax = plt.subplots()
    bp = ax.boxplot(data_list)
    plt.title('{}'.format(graph_title))
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    plt.grid()

    plt.show()
    #end function


#draw multiple boxplots
def DrawDsipersionMultipleBoxplot(path_dir, n_data, graph_title, y_label):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list = []
    data_list_temp = []
    for N_agent in range(2, N_agents+2):
        data_list_temp, _ = CalcDsipersionofData(path_dir, N_agent, n_data)
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


#plot data
def PlotData(path_dir, n_data, graph_title, y_label, y_min, y_max):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list_x = []
    data_list_y = []
    for N_agent in range(2, N_agents+2):
        average = CalcAverageofData(path_dir, N_agent, n_data)
        data_list_y.append(average)

    #create the list for x axis
    for i in range(2, N_agents+2):
        data_list_x.append(i)
    
    #plot data
    fig, ax = plt.subplots()
    bp = ax.plot(data_list_x, data_list_y, '.', markersize=10)
    plt.grid()
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    ax.set_ylim(y_min, y_max)
    plt.title(graph_title)
    plt.show()
    #end function

#plot Dsipersion of data
def PlotDsipersion(path_dir, n_data, graph_title, y_label, y_min, y_max):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list_x = []
    data_list_y = []
    for N_agent in range(2, N_agents+2):
        _, average = CalcDsipersionofData(path_dir, N_agent, n_data)
        data_list_y.append(average)

    #create the list for x axis
    for i in range(2, N_agents+2):
        data_list_x.append(i)
    
    #plot data
    fig, ax = plt.subplots()
    bp = ax.plot(data_list_x, data_list_y, '.', markersize=10)
    plt.grid()
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    plt.title(graph_title)
    ax.set_ylim(y_min, y_max)
    plt.show()
    #end function


#draw bar graph of data
def DrawBar(path_dir, n_data, graph_title, y_label):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list = []
    x_label = []
    _, data_list_average = CalcPersonalData(path_dir, N_agents, n_data)

    #draw graph
    fig, ax = plt.subplots()
    bp = ax.bar(data_list_average)
    plt.grid()
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    for i in range(2, N_agents+2):
        x_label.append('{}'.format(i))
    ax.set_xticklabels(x_label)
    plt.title(graph_title)
    plt.show()
    #end function


def DrawMultipleBar(path_dir, n_data, graph_title, y_label, y_min, y_max, index0_label, index1_label):
    import matplotlib.pyplot as plt

    N_agents = GetNumberofFiles(path_dir)
    data_list_0 = []
    data_list_1 = []
    data_0_temp = 0
    data_1_temp = 0
    x_label = []
    data_x = []

    #create data list
    for N_agent in range(2, N_agents+2):    
        data_0_temp, data_1_temp = CalcTotalDataof2DList(path_dir, N_agent, n_data)
        data_list_0.append(data_0_temp)
        data_list_1.append(data_1_temp)
    for N_agent in range(2, N_agents+2):
        data_x.append(N_agent)

    #draw graph
    fig, ax = plt.subplots()
    bp1 = ax.bar(data_x, data_list_1,label='{}'.format(index1_label))
    bp2 = ax.bar(data_x, data_list_0, bottom=data_list_1, label='{}'.format(index0_label))
    plt.grid()
    ax.set_xlabel("number of agents")
    ax.set_ylabel("{}".format(y_label))
    for i in range(2, N_agents+2):
        x_label.append('{}'.format(i))
    ax.set_ylim(y_min, y_max)
    #ax.set_xticklabels(x_label)
    ax.legend()
    plt.title(graph_title)
    plt.show()
    #end function


#config===================================================================
#the path of current directry is got automatically by the function GetPath 
#path_dir = R"C:\Users\川北　拓穂\Desktop\採餌タスクプログラム\foragingIn1dModel\data\DERC_TRUE\speed"
N_agents = 9
n_data = 4

graph_title = 'DERC'
y_label = 'Dsipersion of food collected'
y_min = 0
y_max = 100
index0_label = 'not in tunnel'
index1_label = 'in tunnel'
'''
data number list!
0:ticks_in_task_state, 1:ticks_in_social_state, 2:ticks_in_terrain_state, 3:n_visits_to_food, 4:n_visits_to_home, 5:n_ticks_not_moving
#6:n_total_ticks, 7:n_success_tunnel_passages, 8:n_fail_tunnel_passages, 9:n_tunnel_entry, 10:n_tunnel_exit, 11n_derc_recieved_lv1
'''
#================================================================================
#main============================================================================
path_dir = GetPath()

#DrawMultipleBar(path_dir, n_data, graph_title, y_label, y_min, y_max, index0_label, index1_label)
#PlotData(path_dir, n_data,graph_title, y_label, y_min, y_max)
PlotDsipersion(path_dir, n_data,graph_title, y_label, y_min, y_max)