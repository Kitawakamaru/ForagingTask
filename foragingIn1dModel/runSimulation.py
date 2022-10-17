
def run_simulation(robot_range, aggro_range):
    '''itterates through each permuation of robot_range and aggro_range list elements,
    runs a simulation with the permutation and saves the results to a log file.
    logfiles are saved in the base directory in numpy compressed format and are named something like "20220510T231650_R2DV10T2RSFalseRFFalse_log"'''

    import config
    import simulation as corridor_sim
    import numpy as np

    #convert input to a list if only a single integer is provided
    if isinstance(robot_range, int):
        robot_range = [robot_range]

    data_logs = []
    t_final = []
    #load the config (this gets updated with the number of robots and conflict resolution mechnism later)
    cfg = config.Config()

    #loop through each conflict resolution mechanism
    for aggro_type in aggro_range:
        #set the conflict resolution mechanism in the config
        cfg.aggression_type = aggro_type

        #loop through each number of robots
        for n_robots in robot_range:
            #set the number of robots in the config
            cfg.N_ROBOTS = n_robots
            #generate the elements of the config which depend on conflict resolution mechanism and #robots
            cfg.generateConfig()

            data_logs = []
            #loop through the desired number of repeats of the simulation 
            for i in range(cfg.N_REPEATS):
                session_id, header, data, ticks_end = corridor_sim.main(cfg)
                #do some logging
                data_logs.append(data)
                t_final.append(ticks_end)
                print(f"Completed {i} / {cfg.N_REPEATS} for {n_robots}")
            
            #save the logged data for all repeats with n_robots and conflict resolution mechanism aggro_type to file
            data = np.array(data_logs)
            header = np.array(header)
            id = np.array(session_id)
            t_ends = np.array(t_final)
            print(f"size of data is {data.shape}")
            with open(session_id + "_R" + str(cfg.N_ROBOTS) + "DV" + str(cfg.DV) + "T" + str(cfg.aggression_type) + "RS" + str(cfg.RAND_SPEEDS_B) + 
                        "RF" + str(cfg.RAND_FIGHT_RANGE_B) + "_log.npz", "wb") as f:
                np.savez_compressed(f, header=header, data=data, id=id, t_ends = t_ends)
            f.close()
#end function


def main(robot_range=range(2,8), aggro_range = [0,1,2,3]):
    '''Runs a set of simulations where each is a unique permutation of the inputs
    inputs:
    robot_range: a list where each entry is the #agents to simulation (accepted values: 2 to 9)
    aggro_range: a list where each entry is a conflict resolution mechanisms (accepted values: 0 to 7)
    '''
    run_simulation(robot_range, aggro_range)
    
#end function

if __name__=='__main__':
    main()



