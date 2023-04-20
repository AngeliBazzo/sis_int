##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim

import os
import random
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstractAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.plan = []              # a list of planned actions
        self.rtime = self.TLIM      # for controlling the remaining time
        
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.body.set_state(PhysAgent.IDLE)

    
    def go_save_victims(self, mapa, victims):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""
        self.mapa = mapa
        self.victims = victims
        self.body.set_state(PhysAgent.ACTIVE)

        # planning
        self.__planner()
        
    def optimizePath(self, path):
        return path
    
    def __planner(self):
        """ A private method that calculates the walk actions to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""
        
        #calcula a prioridade de cada vitima
        orderly_victims = list()
        for victim in self.victims:
            self.mapa[victim]["prioridade"] = self.mapa[victim]["custo"]/ self.mapa[victim]["gravidade"]

        orderly_victims = sorted(self.victims, key=lambda victim: self.mapa[victim]["prioridade"])

        #checa se esta ordenada
        '''for victim in orderly_victims:
            print(self.mapa[victim]["prioridade"])'''

        #lista os caminhos feitos pelo explorador ate a vitima 
        list_orig_paths = list()
        for victim in orderly_victims:
            path = list()
            pos = victim

            if pos != (0,0):
                in_start = False
            else:
                in_start = True
            while in_start == False:
                pos_pai = self.mapa[pos]["pos_anterior"]
                path.insert(0, pos)
                pos = pos_pai
                if pos != (0,0):
                    in_start = False
                else:
                    path.insert(0, pos)
                    in_start = True
            list_orig_paths.append(path)
        #print(list_orig_paths)   

        print(list_orig_paths)
        list_orig_paths.reverse()
        for i, path in enumerate(list_orig_paths):
            if i != len(list_orig_paths)-1:
                found = False
                final_1 = list_orig_paths[i+1][len(list_orig_paths[i+1])-1]
                k=-1
                path_aux = list()
                while not found:
                    for j, element in enumerate(path):
                        if found == True:
                            break 
                        if element == final_1:
                            found = True
                            #remove a parte anterior da lista
                            del path[:j+1]
                    #se nao encontrou
                    if not found:
                        k-=1
                        path_aux.append(list_orig_paths[i+1][len(list_orig_paths[i+1])+k])
                        for j, element in enumerate(path):
                            if element == path_aux[len(path_aux)-1]:
                                found = True
                                #remove a parte anterior da lista
                                del path[:j+1]
                                print('---------------------------------------')
                                print(path_aux)
                                print(path)
                                list_orig_paths[i] = path_aux + path
                                print(list_orig_paths[i])
                                print('---------------------------------------')
                                
        

        list_orig_paths.reverse()
        print(list_orig_paths)

        #otimiza os caminhos

        #concatena os caminhos
        path_final = list()
        for path in list_orig_paths:
            for pos in path:
                path_final.append(pos)

        #adiciona ao plano
        for i, pos in enumerate (path_final):
            if i != len(path_final)-1:
                self.plan.append((path_final[i+1][0]-pos[0],path_final[i+1][1]-pos[1]))

    
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.plan.pop(0)

        # Walk - just one step per deliberation
        result = self.body.walk(dx, dy)

        # Rescue the victim at the current position
        if result == PhysAgent.EXECUTED:
            # check if there is a victim at the current position
            seq = self.body.check_for_victim()
            if seq >= 0:
                res = self.body.first_aid(seq) # True when rescued             

        return True

