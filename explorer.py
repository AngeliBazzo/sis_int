## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


class Explorer(AbstractAgent):
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore     

        #print(self.rtime)

        self.pos_agent = (0,0)

        self.mapa = dict()
        
        dados = dict()
        dados["pos_anterior"] = (0,0)
        dados["custo"] = 0
        dados["tipo"] = 0   # 0 normal, 1 parede, 2 vitima

        self.mapa[self.pos_agent] = dados 

        self.victim = list()

    def decidesMove(self, voltar):
        #movimentos possiveis
        poss_movs = [(0,-1),(0,1),(1,0),(-1,0),(1,-1),(1,1),(-1,-1),(-1,1)]
        aux = [(0,-1),(0,1),(1,0),(-1,0),(1,-1),(1,1),(-1,-1),(-1,1)]
        x_agent, y_agent= self.pos_agent
        #print("--------------------------------------------")
        #checa se o movimento leva a uma posicao ja visitada

        for mov in poss_movs:
            x, y= mov
            if (x_agent + x, y_agent+y) in self.mapa.keys():
                aux.remove(mov)
                
        
        
        #lista de mov vazias ==>ja conhece todos os movimentos possiveis  ao redor
        ##retorna a posicao anterior a atual
        if len(aux) == 0 or voltar == True:
            x, y= self.mapa[self.pos_agent]["pos_anterior"]
            move = (x-x_agent, y-y_agent)
            return True, move
        
        return False , aux[0]
    


    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        # No more actions, time almost ended
        if self.rtime < 5.0 and self.pos_agent==(0,0): 
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.resc.go_save_victims(self.mapa, self.victim)
            return False
        
        #checa se e preciso comecar a voltar ou nao
        if self.rtime <= self.mapa[self.pos_agent]["custo"] + self.COST_DIAG + 0.5:
            voltar = True
        else :
            voltar = False

        #agente decide entre os movimentos
        voltar, move = self.decidesMove(voltar)

        dx, dy = move
        result = self.body.walk(dx, dy)    
        new_position = (self.pos_agent[0]+dx, self.pos_agent[1]+dy)
        # Moves the body to another position
        custo = self.mapa[self.pos_agent]["custo"]
        
        # Update remaining time and calculate custo
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
            custo += self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE
            custo+=self.COST_LINE
       
       
        #se ele decide explorar uma nova posicao
        if voltar == False:

            # Test the result of the walk action
            #se bateu na parede
            if result == PhysAgent.BUMPED:
                #atualiza o mapa 
                dados = dict()
                dados["pos_anterior"] = self.pos_agent
                dados["custo"] = custo
                dados["tipo"] = 1   # 0 normal, 1 parede, 2 vitima
                
                self.mapa[new_position] = dados
                #mantem a posicao (nao altera o self.pos)


            #um espaco normal possivel de caminhar
            elif result == PhysAgent.EXECUTED:
                # check for victim returns -1 if there is no victim or the sequential
                # the sequential number of a found victim
                seq = self.body.check_for_victim()
                #encontrou uma vitima
                if seq >= 0:
                    tipo = 2
                    #adiciona a vitima na lista de vitimas
                    self.victim.append(new_position)
                    vit_grav =int(4)
                    if self.rtime >= custo + self.COST_READ:
                        vs = self.body.read_vital_signals(seq)
                        self.rtime -= self.COST_READ
                        #print("aquiiiiiiiiiiiiiiiiiiiiiiii", vs)
                        vit_grav =int(vs[7])
                    
                    # print("exp: read vital signals of " + str(seq))
                    # print(vs)

                #nao encontrou nada
                else:
                     tipo = 0
                     vit_grav = 0

                #atualiza o mapa 
                dados = dict()
                dados["pos_anterior"] = self.pos_agent
                dados["custo"] = custo
                dados["tipo"] = tipo   # 0 normal, 1 parede, 2 vitima
                dados["gravidade"] = vit_grav

                self.mapa[new_position] = dados
                #atualiza a posicao 
                self.pos_agent = new_position

        #se ele decide voltar
        if voltar == True:
            #nenhuma informação é atualizada além da posição
            self.pos_agent = new_position
        
        return True

        
       

