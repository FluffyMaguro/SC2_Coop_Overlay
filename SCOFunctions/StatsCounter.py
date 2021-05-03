"""
Few classes used for collection stats later used in graphs.
Army value is an estimation based on the current number of units, and calculating based on commanders, masteries, prestiges.

Few exceptions:
- Tychus' gear upgrades are counted towards army value so it more reflects the investement
- Static defenses are generally counted towards army
- Detectors are counted
- Normal upgrades and research are not counted
- Mind-controlled units are not counted
- Calldowns and heroes don't have resource cost and aren't counted

Inaccuracies:
- Units killed while morphing will not reduce the army value cost (could be fixed, but very messy since how different
implementations are used in SC2. Sometimes coccons are killed at the end of transformation, and sometimes not.)
- Dehaka army values can be a bit "spiky" because the parser is accounting for deaths of units in primal combat 
a bit faster (leading to bonus army value). These spikes are removed with a function.

"""

from SCOFunctions.MLogging import logclass, catch_exceptions
from SCOFunctions.SC2Dictionaries import unit_base_costs, royal_guards, horners_units, tychus_base_upgrades, tychus_ultimate_upgrades, outlaws

logger = logclass('COUNT', 'INFO')
debug_units_without_costs = set()
debug_negative_members = set()


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
    def __init__(self, masteries: tuple, unit_dict: dict, commander_level: int, commander: str, drone_counter: DroneIdentifier):
        self.masteries = list(masteries)
        self.unit_dict = unit_dict
        self.commander = 'Horner' if commander == 'Han & Horner' else commander
        self.commander_level = commander_level
        self.drone_counter = drone_counter
        self.prestige = None
        self.enable_updates = False  # For MM maps enable ingame updating of data
        self.salvaged_units = []
        self.unit_costs = dict()  # Caching calculate unit costs
        self.army_value_offset = 0  # Offset for army value (upgrades, mengsk infantry morphs)
        self.trooper_weapon_cost = (160, 0)
        self.tychus_gear_cost = (750, 1600)  # Normal gear cost, ultimate gear cost
        self.tychus_has_first_outlaw = False  # Track if we have an outlaw, if yes, give discount on the first one
        self.zagara_free_banelings = 0  # Tracking the number of free Banelings spawned for Zagara

        self.kills = []
        self.army_value = []
        self.supply = []
        self.collection_rate = []

    def update_mastery(self, idx: int, count: int):
        if self.enable_updates and self.masteries[idx] != count:
            self.masteries[idx] = count
            logger.info(f"Updated mastery: {self.masteries}")

    def update_prestige(self, prestige: int):
        if self.prestige != prestige:
            self.prestige = prestige

            if prestige == 'Merchant of Death':
                self.trooper_weapon_cost = (40, 20)

            if self.prestige == 'Lone Wolf':
                self.tychus_gear_cost = (self.tychus_gear_cost[0] * 1.25, 0)

    def update_commander(self, commander: str):
        if self.enable_updates and self.commander != commander:
            self.commander = 'Horner' if commander == 'Han & Horner' else commander
            logger.info(f"Updated commander: {self.commander}")

    def unit_change_event(self, unit: str, old_unit: str):
        """ Tracks necessary unit changes"""
        # Main analysis doesn't track morphs between Mengsk infantry.
        # Only troopers created and deaths for all types.
        # So let's adjust army_valie_offset based on their morhps.

        # Trooper → Upgrade Trooper
        if old_unit == 'TrooperMengsk' and unit in {'TrooperMengskAA', 'TrooperMengskFlamethrower', 'TrooperMengskImproved'}:
            self.army_value_offset += sum(self.trooper_weapon_cost)

        # Trooper → Labourer
        elif old_unit == 'TrooperMengsk' and unit == 'SCVMengsk':
            self.army_value_offset -= 40

        # Labourer → Trooper
        elif old_unit == 'SCVMengsk' and unit == 'TrooperMengsk':
            self.army_value_offset += 40

        # Upgraded Trooper → Labourer
        elif old_unit in {'TrooperMengskAA', 'TrooperMengskFlamethrower', 'TrooperMengskImproved'} and unit == 'SCVMengsk':
            self.army_value_offset -= 40 + sum(self.trooper_weapon_cost)

        # Thor → wreckage
        elif old_unit == 'Thor' and unit == 'ThorWreckageSwann':
            self.army_value_offset -= 200

        # Wreckage → Thor
        elif old_unit == 'ThorWreckageSwann' and unit == 'Thor':
            self.army_value_offset += 200

        # Siege Tank → wreckage
        elif old_unit == 'SiegeTank' and unit == 'SiegeTankWreckage':
            self.army_value_offset -= 125

        # Wreckage → Siege Tank
        elif old_unit == 'SiegeTankWreckage' and unit == 'SiegeTank':
            self.army_value_offset += 125

    def upgrade_event(self, upgrade):
        """ Tracks upgrade events"""
        # Add army value for Tychus when gear is purchased
        if upgrade in tychus_base_upgrades:
            self.army_value_offset += self.tychus_gear_cost[0]
        elif upgrade in tychus_ultimate_upgrades:
            self.army_value_offset += self.tychus_gear_cost[1]

    def unit_created_event(self, unit_type, event):
        """ Tracking when a unit was created"""
        # Save the number of free Banelings.
        # Otherwise we would substract too much value when they are killed.
        if self.commander == 'Zagara' \
            and unit_type in {'Baneling', 'HotSSplitterlingBig'} \
            and event['m_creatorAbilityName'].decode() == 'ZagaraVoidCoopBanelingSpawnerTrain':
            self.zagara_free_banelings += 1

    def add_stats(self, kills: int, supply_used: int, collection_rate: int):
        """ Calculates and adds new stats"""
        self.kills.append(kills)
        self.army_value.append(self.calculate_army_value())
        self.supply.append(supply_used)
        self.collection_rate.append(self.calculate_collection_rate(collection_rate))

    def calculate_army_value(self) -> int:
        """ Sums army value for all units for the player"""
        total = 0
        for unit in self.unit_dict:
            # Calculate unit cost
            if unit not in self.unit_costs:
                self.unit_costs[unit] = self.calculate_unit_cost(unit)
            # Add the cost of all alive units
            total += self.calculate_total_unit_value(unit, self.unit_costs[unit])

        logger.debug(f"Total for units {total}\n")
        # Add offset
        total += self.army_value_offset

        # Check for the first Tychus outlaw discout
        if self.commander == 'Tychus' and not self.tychus_has_first_outlaw and len(set(self.unit_dict.keys()).intersection(outlaws)) > 0:
            self.tychus_has_first_outlaw = True
        if self.tychus_has_first_outlaw:
            total -= 600

        return total

    @staticmethod
    def update_cost(cost: tuple, min_mult: float, gas_mult: float) -> tuple:
        if len(cost) == 2:
            return (cost[0] * min_mult, cost[1] * gas_mult)
        elif len(cost) == 4:
            return (cost[0] * min_mult, cost[1] * gas_mult, cost[2] * min_mult, cost[3] * gas_mult)
        else:
            raise Exception('Invalid length of unit cost tuple')

    def calculate_total_unit_value(self, unit: str, cost: tuple) -> float:
        """ Calculates unit value based on how many are alive, dead and cost.
        The secondary cost is used for morhped unit so it can be substracted properly
        Total cost = mineral cost + vespene cost."""

        if sum(cost) == 0:
            return 0

        unit_alive = self.unit_dict[unit][0]
        unit_dead = self.unit_dict[unit][1]

        # Substract units that has been salvaged
        if unit in self.salvaged_units:
            unit_alive -= self.salvaged_units.count(unit)

        # Save those that have negative alive
        if unit_alive - unit_dead < 0:
            debug_negative_members.add(unit)

        # Special case for Zagara's Banelings
        if self.commander == 'Zagara' and unit in {'Baneling', 'HotSSplitterlingBig'}:
            # Bonus value of those created normally (addition)
            result = (unit_alive - self.zagara_free_banelings) * (cost[0] + cost[1])
            # Value of free banes (full)
            result += self.zagara_free_banelings * (cost[2] + cost[3])
            # Value of dead banes (full)
            result -= unit_dead * (cost[2] + cost[3])

            logger.debug(f"{unit_alive:3}/{unit_dead:3}/{self.zagara_free_banelings} {unit:10} ({sum(cost):3}) → {result}")
            return result

        # Calculate current value
        elif len(cost) == 2:
            result = (unit_alive - unit_dead) * sum(cost)
            logger.debug(f"{unit_alive:3}/{unit_dead:3} {unit:10} ({sum(cost):3}) → {result}")
            return result
        # For morhps we have to substract full unit cost when it dies. And add only the additive cost when build.
        elif len(cost) == 4:
            result = unit_alive * (cost[0] + cost[1]) - unit_dead * (cost[2] + cost[3])
            logger.debug(f"{unit_alive:3}/{unit_dead:3} {unit:10} ({sum(cost):3}) → {result}")
            return result
        else:
            raise Exception('Invalid length of unit cost tuple')

    def calculate_unit_cost(self, unit: str) -> tuple:
        """ Calculate army cost for units of given type.
        This takes into account commander, mastery, prestige and upgrades. """
        if self.commander == '':
            return (0, 0)

        if unit in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit]
        elif unit.endswith('Burrowed') and unit.replace('Burrowed', '') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('Burrowed', '')]
        elif unit.endswith('Phasing') and unit.replace('Phasing', '') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('Phasing', '')]
        elif unit.endswith('Uprooted') and unit.replace('Uprooted', '') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('Uprooted', '')]
        elif unit.endswith('Sieged') and unit.replace('Sieged', '') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('Sieged', '')]
        elif unit.endswith('SiegeMode') and unit.replace('SiegeMode', '') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('SiegeMode', '')]
        elif unit.endswith('Fighter') and unit.replace('Fighter', 'Assault') in unit_base_costs[self.commander]:
            cost = unit_base_costs[self.commander][unit.replace('Fighter', 'Assault')]
        else:
            debug_units_without_costs.add(unit)
            return (0, 0)

        # Add modification for commanders, prestiges, masteries, upgrades
        # Cocoons are completely ignored
        # The cost of burrowed units is substracted (if they die burrowed)
        if self.commander == 'Abathur' and self.prestige == 'Essence Hoarder':
            cost = (cost[0], cost[1] * 1.2)
        elif self.commander == 'Alarak' and self.prestige == 'Shadow of Death':
            if unit == 'SOAMothershipv4':
                cost = (400, 400)
            elif unit == 'VoidRayTaldarim':
                cost = (125, 75)

        # Skip if the total cost is zero
        if sum(cost) == 0:
            return (0, 0)

        # Combat unit cost +30%
        if self.commander == 'Artanis' and self.prestige == 'Valorous Inspirator' and unit not in {'PhotonCannon', 'Observer'}:
            cost = self.update_cost(cost, 1.3, 1.3)

        # Combat unit cost -50%
        elif self.commander == 'Fenix' and self.prestige == 'Network Administrator' and unit not in {'PhotonCannon', 'Observer'}:
            cost = self.update_cost(cost, 0.5, 0.5)

        # Horner | Hangar Bay is not counted for Horner as both units are the samy unit class
        elif self.commander == 'Horner':
            # Horner's units cost 30% more
            if self.prestige == 'Chaotic Power Couple' and unit in horners_units:
                cost = self.update_cost(cost, 1.3, 1.3)

            # Horner's units cost -20% less gas
            elif self.prestige == 'Wing Commanders' and unit in horners_units:
                cost = self.update_cost(cost, 1, 0.8)

            # Bombing platform cost +100%
            elif self.prestige == 'Galactic Gunrunners' and unit == 'HHBomberPlatform':
                cost = self.update_cost(cost, 2, 2)

        # Combat unit cost -40%
        elif self.commander == 'Karax' and self.prestige == 'Templar Apparent' and unit not in {
                'ShieldBattery', 'KhaydarinMonolith', 'PhotonCannon', 'Observer'
        }:
            cost = self.update_cost(cost, 0.6, 0.6)

        # Unit gas cost up to -30%
        elif self.commander == 'Kerrigan' and self.masteries[2] > 0:
            cost = self.update_cost(cost, 1, 1 - self.masteries[2] / 100)

        elif self.commander == 'Mengsk':
            # Royal guard cost up to -20%
            if self.masteries[3] > 0 and unit in royal_guards:
                coef = 1 - 20 * self.masteries[3] / 3000
                cost = self.update_cost(cost, coef, coef)

            # Royal guard cost +100% minerals, -25% gas
            if self.prestige == 'Principal Proletariat' and unit in royal_guards:
                cost = self.update_cost(cost, 2, 0.75)

        elif self.commander == 'Raynor':
            # Mechanical units no longer cost 20% less
            if self.prestige == 'Rough Rider' and unit in {
                    'Banshee', 'Battlecruiser', 'VikingAssault', 'VikingFighter', 'SiegeTank', 'SiegeTankSieged'
            }:
                cost = self.update_cost(cost, 1, 1.25)

            # Air units cost -30% gas. All combat units cost +50% minerals
            elif self.prestige == 'Rebel Raider':
                if unit in {'Banshee', 'Battlecruiser', 'VikingAssault', 'VikingFighter'}:
                    cost = self.update_cost(cost, 1.5, 0.7)
                elif unit not in {'Bunker', 'MissileTurret', 'SpiderMine'}:
                    cost = self.update_cost(cost, 1.5, 1)

        # Combat units cost +40% minerals
        elif self.commander == 'Stetmann' and self.prestige == 'Oil Baron' and unit not in {
                'SpineCrawlerStetmann', 'SporeCrawlerStetmann', 'OverseerStetmann'
        }:
            cost = self.update_cost(cost, 1.4, 1)

        # Mechanic combat units cost 30% less
        elif self.commander == 'Stukov' and self.prestige == 'Frightful Fleshwelder' and unit in {
                'SILiberator', 'StukovInfestedBanshee', 'StukovInfestedBansheeBurrowed', 'StukovInfestedDiamondBack', 'StukovInfestedSiegeTank',
                'StukovInfestedSiegeTankUprooted'
        }:
            cost = self.update_cost(cost, 0.7, 0.7)

        elif self.commander == 'Swann':
            # Combat units cost +50% gas (inlcuding Science Vessels and Hercules)
            if self.prestige == 'Grease Monkey' and unit not in {
                    'KelMorianGrenadeTurret', 'KelMorianMissileTurret', 'PerditionTurret', 'PerditionTurretUnderground'
            }:
                cost = self.update_cost(cost, 1, 1.5)

        elif self.commander == 'Tychus':
            # Outlaw cost increased +50%
            if self.prestige == 'Technical Recruiter' and unit != 'TychusSCVAutoTurret':
                cost = self.update_cost(cost, 1.5, 1.5)

        elif self.commander == 'Zagara':
            # Abberation and Corruptors cost 25% less
            if self.prestige == 'Mother of Constructs' and unit in {'ZagaraCorruptor', 'InfestedAbomination'}:
                cost = self.update_cost(cost, 0.75, 0.75)

            # Combat units cost 25% more
            elif self.prestige == 'Apex Predator' and unit not in {'BileLauncherZagara', 'QueenCoop', 'Overseer', 'SpineCrawler', 'SporeCrawler'}:
                cost = self.update_cost(cost, 1.25, 1.25)

        # Combat units cost +25% more
        elif self.commander == 'Zeratul' and self.prestige == 'Knowledge Seeker' and unit not in {
                'ZeratulObserver', 'ZeratulPhotonCannon', 'ZeratulWarpPrism'
        }:
            cost = self.update_cost(cost, 1.25, 1.25)

        return cost

    def calculate_collection_rate(self, collection_rate: int) -> float:
        return collection_rate + self.drone_counter.get_bonus_vespene()

    @staticmethod
    def rolling_average(data: list) -> list:
        """ Computes a rolling average on mining data """
        new = []
        for i, d in enumerate(data):
            if i > 0:
                v = 0.5 * d + 0.5 * data[i - 1]
                new.append(v)
            else:
                new.append(d)
        return new

    @staticmethod
    def remove_upward_spikes(data: list):
        """ Removes upward spikes. This only alters data if there is an upward 
        change that goes down the next tick. Note: changes the data in the argument!"""
        for i, d in enumerate(data):
            if i > 0 and d > data[i - 1] and i < len(data) - 1 and d > data[i + 1]:
                data[i] = (data[i - 1] + data[i + 1]) / 2

    def get_stats(self, player_name: str) -> dict:
        """ Returns collected stats as a dictionary"""
        # logger.debug(f'\n{debug_units_without_costs=}\n')
        # logger.debug(f'\n{debug_negative_members=}\n')
        if self.commander == 'Dehaka':
            self.remove_upward_spikes(self.army_value)
        return {
            'name': player_name,
            'killed': self.kills,
            'army': self.army_value,
            'supply': self.supply,
            'mining': self.rolling_average(self.collection_rate)
        }
