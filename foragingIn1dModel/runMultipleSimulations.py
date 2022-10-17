'''Simple script to parse a set of command line input arguments and then call the runSimulation module'''


# Initialize parser
import argparse
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-s", "--Scenario", help = "Scenario to simulate in range 0,1,2,3", nargs="*", type=int)
parser.add_argument("-n", "--Number", help = "Number of agents to simulate in range 2,3,4,5,6,7", nargs="*", type=int)
 
# Read arguments from command line
args = parser.parse_args()

#call the runSimulation module.  Defaults if no command line arguments are given are 7 agents running conflict resolution mechanism 2
import runSimulation
if args.Scenario:
    #loop though each
    scenario = [int(s) for s in args.Scenario]
else: 
    scenario = [2]

if args.Number:
    number = [int(n) for n in args.Number] 
else:
    #number = [2,3,4,5,6,7]
    number = [7]

runSimulation.main(robot_range=number, aggro_range = scenario)
