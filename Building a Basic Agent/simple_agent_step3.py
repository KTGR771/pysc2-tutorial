from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

import time

# Functions
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_TERRAN_BARRACKS = 21
_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_SCV = 45

# Parameters
_PLAYER_SELF = 1
_SUPPLY_USED = 3
_SUPPLY_MAX = 4
_SCREEN = [0]
_MINIMAP = [1]
_QUEUED = [1]

class SimpleAgent(base_agent.BaseAgent):
    base_top_left = None
    supply_depot_built = False
    scv_selected = False
    barracks_built = False
    barracks_selected = False
    barracks_rallied = False
    
    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        
        return [x + x_distance, y + y_distance]
    
    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        
        time.sleep(0)
        
        if self.base_top_left is None:
            player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
            self.base_top_left = player_y.mean() <= 31
            
        if not self.supply_depot_built:
            if not self.scv_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                
                target = [unit_x[0], unit_y[0]]
                
                self.scv_selected = True
                
                return actions.FunctionCall(_SELECT_POINT, [_SCREEN, target])
            elif _BUILD_SUPPLYDEPOT in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
                
                target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)
                
                self.supply_depot_built = True
                
                return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_SCREEN, target])
        elif not self.barracks_built:
            if _BUILD_BARRACKS in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
                
                target = self.transformLocation(int(unit_x.mean()), 20, int(unit_y.mean()), 0)
                
                self.barracks_built = True
                
                return actions.FunctionCall(_BUILD_BARRACKS, [_SCREEN, target])
        elif not self.barracks_rallied:
            if not self.barracks_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
                
                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]
                
                    self.barracks_selected = True
                
                    return actions.FunctionCall(_SELECT_POINT, [_SCREEN, target])
            else:
                self.barracks_rallied = True
                
                if self.base_top_left:
                    return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_MINIMAP, [29, 21]])
                
                return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_MINIMAP, [29, 46]])
        elif obs.observation["player"][_SUPPLY_USED] < obs.observation["player"][_SUPPLY_MAX] and _TRAIN_MARINE in obs.observation["available_actions"]:
            return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])

        return actions.FunctionCall(_NOOP, [])
