***************************************************************************
Original author: Chris Bennett (ORCiD 0000-0002-6325-1662)

Title: Foraging in 1D

Version: model_26_02_2022_e

Description: A simple simulation model used to investigate the use of intrinsic traits as a means to resolve 
spatial interference between 2 or more agents passing back and forth along a route with narrow tunnels. 

This work was funded and delivered in partnership between the Thales Group and the University of Bristol, 
and with the support of the UK EPSRC Grant Award EP/R004757/1.
***************************************************************************

Files:
=================================
The simulation files are found in the folder "foragingIn1dModel"

    - Agent.py : a superclass derived from a pygame sprite. 
    - Robot.py : a subclass of Agent, each ant in the simulation is an instance of Robot.py.
    - config.py : an object which contains the parameters used in the simulation.
    - runMultipleSimulations.py : a simple script to turn command line arguments into commands to run the simulations.  Calls runSimulation.py
    - runSimulation.py :the script which runs a set of simulations.  
                        Each simulation can have a different combination of the #ants and conflict resolution mechanism
    - simulation.py :   the model which simulates a population of ants moving back and between a home and food location.  
                        Ants will move into conflict when 2 or more meet traveling in opposite directions through a narrow tunnel
    - readme.txt : this file

Languages:
=================================
    - tested on Python 3.6.13

Necessary libraries:
=================================
    - numpy
    - pygame
    - argparse

Operating System:
=================================
- tested on Windows 10 and Linux (centos 7)

Instructions to get started:
=================================
To run a set of simulations using config.py with [2,3,4] robots and conflict resolution mechanism 3 (random_preassigned):
    at command line type: python runMultipleSimulations.py -s 3 -n 2 3 4