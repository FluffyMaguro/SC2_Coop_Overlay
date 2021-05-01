from SCOFunctions.MLogging import logclass, catch_exceptions

logger = logclass('COUNT', 'INFO')
base_costs = dict()


class DroneIdentifier:
    """ Class for identifying when vespene drones were created and calculating bonus vespene rate"""
    def __init__(self, com1: str, com2: str):
        self.commanders = [com1, com2]
        self.recently_used = False  # Whether the ability was recently used and is now retargeting other Refineries
        self.drones = 0  # Number of Vespene Drones
        self.refineries = set()  # Locations of refineries with drones

    def event(self, event: dict):
        """ Checks the event if a Vespene Drone was used. """
        if event['_event'] not in {'NNet.Game.SCmdEvent', 'NNet.Game.SCmdUpdateTargetUnitEvent'}:
            return
        if self.commanders[event['_userid']['m_userId']] != 'Swann':
            return

        if event['_event'] == 'NNet.Game.SCmdEvent':
            self.recently_used = False
            if event['m_abil'] is not None and event['m_abil'].get('m_abilLink', None) == 2536:
                self.recently_used = True
                target_refinery = tuple(event['m_data']['TargetUnit']['m_snapshotPoint'].values())
                # Don't count it when drones are created on the same refinery (after death)
                # Unfortunately, collection rate will be reported higher while the refinery is dead
                # This only prevents it reporting more drones when they are rebuild
                if target_refinery not in self.refineries:
                    self.drones += 1
                    self.refineries.add(target_refinery)

        elif self.recently_used and event['_event'] == 'NNet.Game.SCmdUpdateTargetUnitEvent':
            target_refinery = tuple(event['m_target']['m_snapshotPoint'].values())
            if target_refinery not in self.refineries:
                self.drones += 1
                self.refineries.add(target_refinery)

    def update_commanders(self, idx: int, commander: str):
        if idx in {1, 2}:
            self.commanders[idx - 1] = commander

    def get_bonus_vespene(self) -> float:
        """Returns bonus gas from Vespene Drones"""
        # One Vespene Drone mines 19.055 gas per minute (ingame time)
        return self.drones * 19.055


class StatsCounter:
    """ For counting player stats (army value, resource collection rate)"""
    def __init__(self, masteries: tuple, unit_dict: dict, commander_level: int, commnader: str, drone_counter: DroneIdentifier):
        self.masteries = list(masteries)
        self.unit_dict = unit_dict
        self.commander = commnader
        self.commander_level = commander_level
        self.drone_counter = drone_counter
        self.prestige = None

        self.kills = []
        self.army_value = []
        self.collection_rate = []

    def update_mastery(self, idx: int, count: int):
        if self.masteries[idx] != count:
            self.masteries[idx] = count
            logger.info(f"Updated mastery: {self.masteries}")

    def update_prestige(self, prestige: int):
        if self.prestige != prestige:
            self.prestige = prestige

    def update_commander(self, commander: str):
        if self.commander != commander:
            self.commander = commander
            logger.info(f"Updated commander: {self.commander}")

    def add_stats(self, kills: int, collection_rate):
        """ Calculates and adds new stats"""
        self.kills.append(kills)
        self.army_value.append(self.calculate_army_value())
        self.collection_rate.append(self.calculate_collection_rate(collection_rate))

    def calculate_army_value(self) -> int:
        return 0

    def calculate_collection_rate(self, collection_rate: int) -> float:
        return collection_rate + self.drone_counter.get_bonus_vespene()

    @staticmethod
    def rolling_average(data: list) -> list:
        """ Computes a rolling average on mining data """
        new = []
        for i, d in enumerate(data):
            if i > 1:
                v = 0.5 * d + 0.35 * data[i - 1] + 0.15 * data[i - 2]
                new.append(v)
            else:
                new.append(d)
        return new

    def get_stats(self, player_name: str) -> dict:
        return {'name': player_name, 'killed': self.kills, 'army': self.army_value, 'mining': self.rolling_average(self.collection_rate)}