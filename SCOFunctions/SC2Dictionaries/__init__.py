"""SC2Dictionaries

All imports and local names relevant only to this file are _implied_private.
"""

import functools as _functools
import os as _os

from ._data_utils import (csv_to_dictitems as _csv_to_dictitems, txt_to_iter as _txt_to_iter, csv_to_comastery_dict as _csv_to_comastery_dict,
                          get_file_path)

_DATADIR = 'SCOFunctions/SC2Dictionaries'
_joinDATA = _functools.partial(get_file_path, subfolder=_DATADIR)

UnitNameDict = _csv_to_dictitems(_joinDATA('UnitNames.csv'))
UnitAddKillsTo = _csv_to_dictitems(_joinDATA('UnitAddKillsTo.csv'))
CommanderMastery = _csv_to_comastery_dict(_joinDATA('CommanderMastery.csv'))
COMasteryUpgrades = _csv_to_comastery_dict(_joinDATA('COMasteryUpgrades.csv'))

# Set of all units in waves (excluding Medivac)
UnitsInWaves = _txt_to_iter(_joinDATA('UnitsInWaves.txt'))
HFTS_Units = _txt_to_iter(_joinDATA('HFTS_Units.txt'))
TUS_Units = _txt_to_iter(_joinDATA('TUS_Units.txt'))

prestige_upgrades = {
    'Abathur': {
        'CommanderPrestigeAbathurBiomass': 'Essence Hoarder',
        'CommanderPrestigeAbathurDeepTunnel': 'Tunneling Horror',
        'CommanderPrestigeAbathurUltEvo': 'The Limitless'
    },
    'Alarak': {
        'CommanderPrestigeAlarakMech': 'Artificer of Souls',
        'CommanderPrestigeAlarakEmpowerMe': 'Tyrant Ascendant',
        'CommanderPrestigeAlarakDeathFleet': 'Shadow of Death',
    },
    'Artanis': {
        'CommanderPrestigeArtanisCombatAbilities': 'Valorous Inspirator',
        'CommanderPrestigeArtanisPowerField': 'Nexus Legate',
        'CommanderPrestigeArtanisOrbitalStrikes': 'Arkship Commandant',
    },
    'Dehaka': {
        'CommanderPrestigeDehakaDevour': 'Devouring One',
        'CommanderPrestigeDehakaPackLeaders': 'Primal Contender',
        'CommanderPrestigeDehakaClone': 'Broodbrother',
    },
    'Fenix': {
        'CommanderPrestigeFenixSuitSwap': 'Akhundelar',
        'CommanderPrestigeFenixDataWeb': 'Network Administrator',
        'CommanderPrestigeFenixAvenger': 'Unconquered Spirit',
    },
    'Horner': {
        'CommanderPrestigeHornerMagMines': 'Chaotic Power Couple',
        'CommanderPrestigeHornerStarport': 'Wing Commanders',
        'CommanderPrestigeHornerBombingPlatforms': 'Galactic Gunrunners',
    },
    'Karax': {
        'CommanderPrestigeKaraxStructures': 'Architect of War',
        'CommanderPrestigeKaraxArmy': 'Templar Apparent',
        'CommanderPrestigeKaraxTopBar': 'Solarite Celestial',
    },
    'Kerrigan': {
        'CommanderPrestigeKerriganCreep': 'Malevolent Matriarch',
        'CommanderPrestigeKerriganAbilities': 'Folly of Man',
        'CommanderPrestigeKerriganAssimilationAura': 'Desolate Queen'
    },
    'Mengsk': {
        'CommanderPrestigeMengskArtillery': 'Toxic Tyrant',
        'CommanderPrestigeMengskRoyalGuard': 'Principal Proletariat',
        'CommanderPrestigeMengskTroopers': 'Merchant of Death'
    },
    'Nova': {
        'CommanderPrestigeNovaBio': 'Soldier of Fortune',
        'CommanderPrestigeNovaAirlift': 'Tactical Dispatcher',
        'CommanderPrestigeNovaSuperCloak': 'Infiltration Specialist'
    },
    'Raynor': {
        'CommanderPrestigeRaynorBio': 'Backwater Marshal',
        'CommanderPrestigeRaynorMechAfterburners': 'Rough Rider',
        'CommanderPrestigeRaynorAir': 'Rebel Raider',
    },
    'Stetmann': {
        'CommanderPrestigeStetmannStetellites': 'Signal Savant',
        'CommanderPrestigeStetmannGary': 'Best Buddy',
        'CommanderPrestigeStetmannCombatBuff': 'Oil Baron',
    },
    'Stukov': {
        'CommanderPrestigeStukovMech': 'Frightful Fleshwelder',
        'CommanderPrestigeStukovBanshees': 'Plague Warden',
        'CommanderPrestigeStukovBunkers': 'Lord of the Horde',
    },
    'Swann': {
        'CommanderPrestigeSwannDrill': 'Heavy Weapons Specialist',
        'CommanderPrestigeSwannTurrets': 'Grease Monkey',
        'CommanderPrestigeSwannHercules': 'Payload Director',
    },
    'Tychus': {
        'CommanderPrestigeTychusSquadAbilities': 'Technical Recruiter',
        'CommanderPrestigeTychusLoneWolf': 'Lone Wolf',
        'CommanderPrestigeTychusOdin': 'Dutiful Dogwalker',
    },
    'Vorazun': {
        'CommanderPrestigeVorazunEmergencyRecall': 'Spirit of Respite',
        'CommanderPrestigeVorazunStasis': 'Withering Siphon',
        'CommanderPrestigeVorazunTimeStop': 'Keeper of Shadows'
    },
    'Zagara': {
        'CommanderPrestigeZagaraMaxSupply': 'Scourge Queen',
        'CommanderPrestigeZagaraCorruptorsAberrations': 'Mother of Constructs',
        'CommanderPrestigeZagaraZagara': 'Apex Predator'
    },
    'Zeratul': {
        'CommanderPrestigeZeratulVoidSeeker': "Anakh Su'n",
        'CommanderPrestigeZeratulArtifactFragments': 'Knowledge Seeker',
        'CommanderPrestigeZeratulTornadoes': 'Herald of the Void',
    }
}

prestige_names = {
    'Abathur': {
        0: 'Evolution Master',
        1: 'Essence Hoarder',
        2: 'Tunneling Horror',
        3: 'The Limitless'
    },
    'Alarak': {
        0: "Highlord of the Tal'darim",
        1: 'Artificer of Souls',
        2: 'Tyrant Ascendant',
        3: 'Shadow of Death'
    },
    'Artanis': {
        0: 'Hierarch of the Daelaam',
        1: 'Valorous Inspirator',
        2: 'Nexus Legate',
        3: 'Arkship Commandant'
    },
    'Dehaka': {
        0: 'Primal Pack Leader',
        1: 'Devouring One',
        2: 'Primal Contender',
        3: 'Broodbrother'
    },
    'Fenix': {
        0: 'Purifier Executor',
        1: 'Akhundelar',
        2: 'Network Administrator',
        3: 'Unconquered Spirit'
    },
    'Horner': {
        0: 'Mercenary Leader and Dominion Admiral',
        1: 'Chaotic Power Couple',
        2: 'Wing Commanders',
        3: 'Galactic Gunrunners'
    },
    'Karax': {
        0: 'Khalai Phase-Smith',
        1: 'Architect of War',
        2: 'Templar Apparent',
        3: 'Solarite Celestial'
    },
    'Kerrigan': {
        0: 'Queen of Blades',
        1: 'Malevolent Matriarch',
        2: 'Folly of Man',
        3: 'Desolate Queen'
    },
    'Mengsk': {
        0: 'Emperor of the Dominion',
        1: 'Toxic Tyrant',
        2: 'Principal Proletariat',
        3: 'Merchant of Death'
    },
    'Nova': {
        0: 'Dominion Ghost',
        1: 'Soldier of Fortune',
        2: 'Tactical Dispatcher',
        3: 'Infiltration Specialist'
    },
    'Raynor': {
        0: 'Renegade Commander',
        1: 'Backwater Marshal',
        2: 'Rough Rider',
        3: 'Rebel Raider'
    },
    'Stetmann': {
        0: 'Hero Genius (Henius)',
        1: 'Signal Savant',
        2: 'Best Buddy',
        3: 'Oil Baron'
    },
    'Stukov': {
        0: 'Infested Admiral',
        1: 'Frightful Fleshwelder',
        2: 'Plague Warden',
        3: 'Lord of the Horde'
    },
    'Swann': {
        0: 'Chief Engineer',
        1: 'Heavy Weapons Specialist',
        2: 'Grease Monkey',
        3: 'Payload Director'
    },
    'Tychus': {
        0: 'Legendary Outlaw',
        1: 'Technical Recruiter',
        2: 'Lone Wolf',
        3: 'Dutiful Dogwalker'
    },
    'Vorazun': {
        0: 'Matriarch of the Nerazim',
        1: 'Spirit of Respite',
        2: 'Withering Siphon',
        3: 'Keeper of Shadows'
    },
    'Zagara': {
        0: 'Swarm Broodmother',
        1: 'Scourge Queen',
        2: 'Mother of Constructs',
        3: 'Apex Predator'
    },
    'Zeratul': {
        0: 'Dark Prelate',
        1: "Anakh Su'n",
        2: 'Knowledge Seeker',
        3: 'Herald of the Void'
    }
}

# Unit types present in different waves. Each enemy comp has a list of waves based on tech level.
UnitCompDict = {
    'Brooding Corruption': [{'Zergling'}, {'Mutalisk', 'Zergling'}, {'Baneling', 'Mutalisk', 'Zergling'}, {'Mutalisk', 'Infestor', 'Zergling'},
                            {'Mutalisk', 'Corruptor', 'Infestor', 'Zergling'}, {'Mutalisk', 'Infestor', 'Zergling', 'BroodLord'},
                            {'Mutalisk', 'Corruptor', 'Infestor', 'BroodLord'}],
    'Classic Infantry': [{'Marine'}, {'Marine', 'Medic'}, {'Marine', 'Firebat', 'Medic'}, {'Marine', 'SiegeTank', 'Medic'},
                         {'Marine', 'SiegeTank', 'Ghost', 'Medic'}, {'Firebat', 'Marine', 'Medic', 'ScienceVessel', 'SiegeTank'},
                         {'Ghost', 'Marine', 'Medic', 'ScienceVessel', 'SiegeTank'}],
    'Classic Mech': [{'Vulture'}, {'Vulture', 'Goliath'}, {'Wraith', 'Vulture', 'Goliath'}, {'SiegeTank', 'Wraith', 'Vulture', 'Goliath'},
                     {'SiegeTank', 'Vulture', 'Battlecruiser', 'Goliath'}, {'ScienceVessel', 'Battlecruiser', 'Goliath'},
                     {'SiegeTank', 'Battlecruiser', 'ScienceVessel', 'Goliath'}],
    'Devouring Scourge': [{'Zergling'}, {'Mutalisk', 'Zergling'}, {'Scourge', 'QueenClassic', 'Mutalisk', 'Zergling'},
                          {'Scourge', 'Mutalisk', 'Zergling', 'Guardian'}, {'Devourer', 'Mutalisk', 'Guardian'},
                          {'Devourer', 'QueenClassic', 'Mutalisk', 'Guardian'}, {'Devourer', 'QueenClassic', 'Guardian', 'Scourge'}],
    'Disruptive Artillery': [{'Adept'}, {'Adept', 'Sentry'}, {'Adept', 'Immortal'}, {'Adept', 'Scout', 'Immortal'},
                             {'Adept', 'Sentry', 'Disruptor', 'Reaver'}, {'Adept', 'Disruptor', 'Scout', 'Reaver'},
                             {'Sentry', 'Disruptor', 'Immortal', 'Reaver'}],
    'Dominion Battlegroup': [{'VikingFighter'}, {'VikingFighter', 'Banshee'}, {'VikingFighter', 'Marine', 'Banshee'},
                             {'VikingFighter', 'Marine', 'Banshee', 'Liberator'}, {'VikingFighter', 'Raven', 'Banshee', 'Liberator'},
                             {'Banshee', 'Battlecruiser', 'Liberator', 'Marine', 'Raven', 'VikingFighter'},
                             {'Banshee', 'Battlecruiser', 'Liberator', 'Raven', 'VikingFighter'}],
    'Explosive Threats': [{'Zergling'}, {'Baneling', 'Zergling'}, {'InfestedAbomination', 'Mutalisk', 'Scourge', 'Viper', 'Zergling'},
                          {'InfestedAbomination', 'Mutalisk', 'Scourge', 'SwarmHostMP', 'Zergling'},
                          {'Baneling', 'InfestedAbomination', 'Mutalisk', 'Scourge', 'Viper', 'Zergling'},
                          {'Baneling', 'Mutalisk', 'Scourge', 'SwarmHostMP', 'Viper', 'Zergling'},
                          {'Baneling', 'InfestedAbomination', 'Mutalisk', 'Scourge', 'SwarmHostMP', 'Viper'}],
    'Fleet of the Matriarch': [{'Zealot'}, {'Scout', 'Zealot'}, {'CorsairMP', 'Scout', 'Zealot'}, {'CorsairMP', 'Scout'}, {'Scout', 'Carrier'},
                               {'ArbiterMP', 'Scout', 'Carrier'}, {'ArbiterMP', 'CorsairMP', 'Scout', 'Carrier'}],
    'Hope of the Khalai': [{'Zealot'}, {'Scout', 'Zealot'}, {'Stalker', 'Scout'}, {'Scout', 'Oracle', 'Zealot'}, {'VoidRay', 'Zealot'},
                           {'Oracle', 'Carrier', 'Zealot'}, {'VoidRay', 'Oracle', 'Carrier', 'Zealot'}],
    'Invasionary Swarm': [{'Zergling'}, {'Zergling', 'Hydralisk'}, {'LurkerMP', 'Zergling', 'Hydralisk'}, {'LurkerMP', 'Hydralisk'},
                          {'LurkerMP', 'QueenClassic', 'Hydralisk'}, {'Ultralisk', 'Zergling', 'Hydralisk'},
                          {'Hydralisk', 'LurkerMP', 'QueenClassic', 'Ultralisk', 'Zergling'}],
    'Machines of War': [{'Hellion'}, {'WarHound', 'Hellion', 'Goliath'}, {'HellionTank', 'SiegeTank', 'WarHound', 'Goliath'},
                        {'Goliath', 'HellionTank', 'SiegeTank', 'WarHound', 'WidowMine'},
                        {'Goliath', 'ScienceVessel', 'SiegeTank', 'WarHound', 'WidowMine'},
                        {'Goliath', 'ScienceVessel', 'Thor', 'WarHound', 'WidowMine'}, {'Thor', 'SiegeTank', 'ScienceVessel'}],
    'Masters and Machines': [{'Zealot'}, {'Stalker', 'Zealot'}, {'Stalker', 'HighTemplar', 'Zealot'}, {'Stalker', 'HighTemplar', 'Immortal'},
                             {'Stalker', 'Zealot', 'HighTemplar', 'Archon'}, {'Stalker', 'Zealot', 'Archon', 'Colossus'},
                             {'Colossus', 'HighTemplar', 'Immortal', 'Stalker', 'Zealot'}],
    'Raiding Party': [{'Marine', 'Medic'}, {'Marine', 'Marauder', 'Medic'}, {'Firebat', 'Marauder', 'Medic'},
                      {'Marine', 'Medivac', 'SiegeTank', 'Ghost'}, {'Marauder', 'Marine', 'Medivac', 'SiegeTank'},
                      {'Ghost', 'Marauder', 'Marine', 'ScienceVessel', 'SiegeTank'},
                      {'Battlecruiser', 'Ghost', 'Marine', 'ScienceVessel', 'SiegeTank'}],
    'Ravaging Infestation': [{'Roach'}, {'Roach', 'Zergling'}, {'Roach', 'Hydralisk'}, {'Ravager', 'LurkerMP', 'Roach', 'Hydralisk'},
                             {'LurkerMP', 'Roach', 'Infestor', 'Hydralisk'}, {'Hydralisk', 'Infestor', 'Ravager', 'Roach', 'Ultralisk'},
                             {'Hydralisk', 'Infestor', 'Ravager', 'Roach', 'Ultralisk'}],
    'Shadow Disruption': [{'Adept'}, {'Adept', 'Stalker'}, {'Adept', 'Sentry', 'Stalker'}, {'DarkTemplar', 'Stalker', 'Adept', 'Sentry'},
                          {'DarkTemplar', 'Adept', 'Phoenix', 'Sentry'}, {'Adept', 'DarkTemplar', 'Disruptor', 'Sentry', 'Stalker'},
                          {'Adept', 'DarkTemplar', 'Disruptor', 'Phoenix', 'Sentry'}],
    'Shadow Tech': [{'Reaper'}, {'Marauder', 'Reaper'}, {'Liberator', 'Marauder', 'Reaper'}, {'Cyclone', 'Liberator', 'Marauder', 'Reaper'},
                    {'Marauder', 'Raven', 'Liberator', 'Cyclone'}, {'Marauder', 'Raven', 'Cyclone', 'Battlecruiser'},
                    {'Battlecruiser', 'Cyclone', 'Liberator', 'Marauder', 'Raven'}],
    'Siege of Storms': [{'Adept'}, {'Adept', 'Phoenix'}, {'Adept', 'Phoenix'}, {'Stalker', 'Phoenix', 'Oracle'}, {'Adept', 'VoidRay'},
                        {'Adept', 'Oracle', 'Tempest'}, {'Adept', 'VoidRay', 'Oracle', 'Tempest'}],
    'Towering Walkers': [{'Zealot'}, {'Sentry', 'Zealot'}, {'Sentry', 'Immortal'}, {'Scout', 'Immortal', 'Zealot'},
                         {'Sentry', 'Scout', 'Zealot', 'Colossus'}, {'Scout', 'Zealot', 'Colossus'}, {'Sentry', 'Zealot', 'Immortal', 'Colossus'}],
    'Vanguard of Aiur': [{'Zealot'}, {'Dragoon', 'Zealot'}, {'Dragoon', 'HighTemplar', 'Zealot'}, {'Dragoon', 'Reaver'},
                         {'Reaver', 'Archon', 'HighTemplar', 'Zealot'}, {'ArbiterMP', 'Dragoon', 'HighTemplar', 'Zealot'},
                         {'ArbiterMP', 'Archon', 'Dragoon', 'HighTemplar', 'Reaver', 'Zealot'}]
}

# Units to show in unit stats
units_to_stats = {
    'Medic', 'Havoc', 'Mecha Infestor', 'SCV', 'Probe', 'Drone', 'Mecha Drone', 'Primal Drone', 'Infested SCV', 'Probius', 'Dominion Laborer',
    'Imperial Intercessor', 'Overseer', 'Theia Raven', 'Stasis Ward', 'Mecha Overseer', 'Shield Battery', 'MULE', 'Imperial Witness',
    "Xel'Naga Void Array", "Raven Type-II", "War Prism", "Dark Pylon", "Swarm Queen", "Queen", "Hercules", "Science Vessel", 'Defensive Drone',
    'Revitalizer', 'Mecha Overlord', 'Overlord', 'Medivac Platform', 'Omega Worm', 'Nydus Worm'
}

# Different map names: local_name : {english_name, editor_name}
map_names = {
    'Apunta y carga': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Archange mécanique': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Bariery na Ulnarze': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Bedrohung auf Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Berceau de mort': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Berço da Morte': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Cadena de ascensión': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    "Catena dell'Ascensione": {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Chain of Ascension': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Chaîne de l’Ascension': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'La chaîne de l’Ascension': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Ciberguerra': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Cible verrouillée': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Cierre de filas': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Comboio da Aniquilação': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Congegni contesi': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Cradle of Death': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Culla mortale': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Cuna de la muerte': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Cuna de muerte': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Cyfrowa wojna': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Dead of Night': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Demoliendo vacíos': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Der Himmel fällt uns auf den Kopf': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'Devastação do Vazio': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Die Wiege des Todes': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Ekspres do Otchłani': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'El problema Bermellón': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'El problema de Vermillion': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Elektronische Kriegsführung': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Envíos letales': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Evacuación de mineros': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Evacuación minera': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Evacuazione dei minatori': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Evacuação dos Mineiros': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Ewakuacja górników': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Expreso del olvido': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Expreso hacia la extinción': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Express pour l’Oubli': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Falce di Amon': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Fallas a Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Faux d’Amon': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Faz Parte': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Fissuras de Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Fisuras a Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Foice de Amon': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Geißel Amons': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Guadaña de Amon': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Guadaña de Amón': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Guerra de malware': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Guerra informatica': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Guerre cybernétique': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Guerrilha Tecnológica': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Hierarquia da Ascensão': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Im Dienste der Wissenschaft': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Kette des Aufstiegs': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Kolebka Śmierci': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'La caduta del cielo': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'La caída del cielo': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'La route de Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Lacération du Vide': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Lancio del Vuoto': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Lanzamiento al vacío': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Lanzamiento del Vacío': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Lançamento do Vazio': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Le ciel nous tombe sur la tête': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'Le problème Vermillion': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Leerentumult': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Lock & Load': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Los cielos se derrumban': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'Malwarfare': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Mandando Bala': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Materialschlacht': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Miner Evacuation': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Mist Opportunities': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Molochy na Char': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Nacht des Grauens': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Navettes pour le Vide': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Nicht ohne meinen Kumpel': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Noc zainfekowanych': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Noche de los muertos': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Noche mortal': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Noite Morta': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Notte oscura': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'O Céu está Caindo': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'O problema de Vermillion': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Oblio Express': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Oblivion Express': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Oportunidades etéreas': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Oportunidades na Névoa': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Oportunidades nebulosas': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Opportunità sfumate': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Opresión del vacío': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Part and Parcel': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Parte por parte': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Problem Vermilliona': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Prosto w Otchłań': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Questione scottante': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    "Rak'Shir na Slayn": {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Rifts to Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Robots dans la brume': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Rottami pericolosi': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Schloss und Riegel': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Scythe of Amon': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Shuttle zu Schutt': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Stetmann w oparach': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Szczeliny na Korhalu': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Tempel der Vergangenheit': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Tempio del passato': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Temple du passé': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Temple of the Past': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Templo del pasado': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Templo do Passado': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Terreurs nocturnes': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'The Sky is Falling': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'The Vermillion Problem': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Transtarsonische Eisenbahn': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    'Upadek z nieba': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'Varchi per Korhal': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'Vermillion Live': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Void Launch': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Void Thrashing': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Vuoto abominevole': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Złomuj i rządź': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Évacuation minière': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Świątynia przeszłości': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Żniwa Amona': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Битва гигантов': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    'Вермиллион проблем': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    'Вирусная война': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    'Древний храм': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    'Колыбель смерти': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    'Коса Амуна': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    'Мертвые в ночи': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    'Надежный затвор': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    'Падающие небеса': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    'Пришествие Пустоты': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    'Разломы на Корхале': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    'С миру по нитке': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    'Туманные перспективы': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    'Цепь вознесения': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    'Эвакуация шахтеров': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    'Экспресс забвения': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    '亞蒙之鐮': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    '亡者之夜': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    '克哈裂痕': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    '克哈裂隙': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    '净网行动': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    '升格之链': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    '古老神殿': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    '天界封锁': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    '天穹坠落': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    '天降危機': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    '往日神庙': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    '惡意程式': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    '控制天星鎖': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    '机会渺茫': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    '死亡搖籃': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    '死亡摇篮': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    '求生无路': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    '湮灭快车': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    '滅絕特快車': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    '熔火危机': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    '礦工疏散行動': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    '聚铁成兵': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    '营救矿工': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    '虚空撕裂': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    '虚空降临': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    '虛空躍傳': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    '護艇大作戰': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    '赤色危機': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    '迎戰虛空': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    '關鍵零件': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    },
    '飛升之鍊': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    '黑暗杀星': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    '공허 분쇄': {
        'EN': 'Void Thrashing',
        'ID': 'AC_CharThrasher'
    },
    '공허의 출격': {
        'EN': 'Void Launch',
        'ID': 'AC_KaldirShuttle'
    },
    '과거의 사원': {
        'EN': 'Temple of the Past',
        'ID': 'AC_ShakurasTemple'
    },
    '광부 대피': {
        'EN': 'Miner Evacuation',
        'ID': 'AC_JarbanPointCapture'
    },
    '망각행 고속열차': {
        'EN': 'Oblivion Express',
        'ID': 'AC_TarsonisTrain'
    },
    '버밀리언의 특종': {
        'EN': 'The Vermillion Problem',
        'ID': 'AC_VeridiaCourier'
    },
    '승천의 사슬': {
        'EN': 'Chain of Ascension',
        'ID': 'AC_SlaynPayload'
    },
    '아몬의 낫': {
        'EN': 'Scythe of Amon',
        'ID': 'AC_AiurSiege'
    },
    '안갯속 표류기': {
        'EN': 'Mist Opportunities',
        'ID': 'AC_BelshirEscort'
    },
    '잘못된 전쟁': {
        'EN': 'Malwarfare',
        'ID': 'AC_CybrosEscort'
    },
    '죽음의 밤': {
        'EN': 'Dead of Night',
        'ID': 'AC_MeinhoffDayNight'
    },
    '죽음의 요람': {
        'EN': 'Cradle of Death',
        'ID': 'AC_CradleOfDeath'
    },
    '천상의 쟁탈전': {
        'EN': 'Lock & Load',
        'ID': 'AC_UlnarLocks'
    },
    '코랄의 균열': {
        'EN': 'Rifts to Korhal',
        'ID': 'AC_KorhalRift'
    },
    '하늘이 무너져도': {
        'EN': 'The Sky is Falling',
        'ID': 'AC_KorhalSkyGuard'
    },
    '핵심 부품': {
        'EN': 'Part and Parcel',
        'ID': 'AC_PartAndParcel'
    }
}

# Which players are on Amon's side
amon_player_ids = {
    'Chain of Ascension': {3, 4, 5, 6, 9, 10},
    'Cradle of Death': {3, 4, 5, 6},
    'Dead of Night': {3, 4, 5, 7},
    'Lock & Load': {3, 4},
    'Malwarfare': {3, 4},
    'Miner Evacuation': {3, 4, 5, 6, 7, 9, 11},
    'Mist Opportunities': {3, 4},
    'Oblivion Express': {3, 4, 5, 6, 7},
    'Part and Parcel': {3, 4, 8},
    'Rifts to Korhal': {3, 4, 7, 8},
    'Scythe of Amon': {3, 4, 5, 6, 7},
    'Temple of the Past': {3, 4, 5, 6, 8},
    'The Vermillion Problem': {3, 4, 5, 6, 9},
    'Void Launch': {3, 4, 5, 6},
    'Void Thrashing': {3, 4, 5}
}

# Number of bonus objectives per mission
bonus_objectives = {
    'Chain of Ascension': 2,
    'Cradle of Death': 2,
    'Dead of Night': 1,
    'Lock & Load': 1,
    'Malwarfare': 2,
    'Miner Evacuation': 2,
    'Mist Opportunities': 2,
    'Oblivion Express': 2,
    'Part and Parcel': 2,
    'Rifts to Korhal': 2,
    'Scythe of Amon': 3,
    'Temple of the Past': 3,
    'The Vermillion Problem': 1,
    'Void Launch': 3,
    'Void Thrashing': 1
}

# Mind-controlling units. In mass replay analysis kills of MC-ed units are added to these.
mc_units = {'Tychus': 'Vega', 'Vorazun': 'Dark Archon', 'Zeratul': 'Dark Archon', 'Karax': 'Energizer', 'Stukov': 'Aleksander'}

Mutators = {
    "Random":
    "Applies a random Mutator that has not yet been chosen for this game.",
    "Walking Infested":
    "Enemy units spawn Infested Terran upon death in numbers according to the unit&apos;s life.",
    "Outbreak":
    "Enemy Infested Terrans spawn continuously around the map.",
    "Darkness":
    "Previously explored areas remain blacked out on the minimap while outside of player vision.",
    "Time Warp":
    "Enemy Time Warps are periodically deployed throughout the map.",
    "Speed Freaks":
    "Enemy units have increased movement speed.",
    "Mag-nificent":
    "Mag Mines are deployed throughout the map at the start of the mission.",
    "Mineral Shields":
    "Mineral clusters at player bases are periodically encased in a shield which must be destroyed for gathering to continue.",
    "Barrier":
    "Enemy units and structures gain a temporary shield upon the first time they take damage.",
    "Avenger":
    "Enemy units gain increased attack speed, movement speed, armor, life, and life-regeneration when nearby enemy units die.",
    "Evasive Maneuvers":
    "Enemy units teleport a short distance away upon taking damage.",
    "Scorched Earth":
    "Enemy units set the terrain on fire upon death.",
    "Lava Burst":
    "Lava periodically bursts from the ground at random locations and deals damage to player air and ground units.",
    "Self Destruction":
    "Enemy units explode and deal damage to nearby player units upon death.",
    "Aggressive Deployment":
    "Additional enemy units are periodically deployed onto the battlefield.",
    "Alien Incubation":
    "All enemy units spawn Broodlings upon death.",
    "Laser Drill":
    "An enemy Laser Drill constantly attacks player units within enemy vision.",
    "Long Range":
    "Enemy units and structures have increased weapon and vision range.",
    "Shortsighted":
    "Player units and structures have reduced vision range.",
    "Mutually Assured Destruction":
    "Enemy Hybrid units detonate a Nuke upon death.",
    "We Move Unseen":
    "All enemy units are permanently cloaked.",
    "Nap Time":
    "Player worker units periodically fall asleep and must be awoken via the Wake Up ability on their command card.",
    "Slim Pickings":
    "Player worker units gather resources at a reduced rate, but resource pickups spawn throughout the map.",
    "Concussive Attacks":
    "Player units are slowed by all enemy attacks.",
    "Stone Zealots":
    "The enemy has deployed Stone Zealots.",
    "Just Die!":
    "Enemy units are automatically revived upon death.",
    "Temporal Field":
    "Enemy Temporal Fields are periodically deployed throughout the map.",
    "Void Rifts":
    "Void Rifts periodically appear in random locations and spawn enemy units until destroyed.",
    "Twister":
    "Tornadoes move across the map, damaging and knocking back player units in their path.",
    "Orbital Strike":
    "Enemy Orbital Strikes are periodically fired throughout the map.",
    "Purifier Beam":
    "An enemy Purifier Beam moves across the map toward nearby player units.",
    "Blizzard":
    "Storm clouds move across the map, damaging and freezing player units in their path.",
    "Fear":
    "Player units will occasionally stop attacking and run around in fear upon taking damage.",
    "Photon Overload":
    "All enemy structures attack nearby hostile units.",
    "Minesweeper":
    "Groups of Widow Mines and Spider Mines are buried throughout the battlefield.",
    "Chaos Studios":
    "Mutators are chosen at random and periodically cycle throughout the mission.",
    "Void Reanimators":
    "Void Reanimators wander the battlefield, bringing your enemies back to life.",
    "Going Nuclear":
    "Nukes are launched at random throughout the map.",
    "Life Leech":
    "Enemy units and structures steal life or shields whenever they do damage.",
    "Power Overwhelming":
    "All enemy units have energy and use random abilities.",
    "Micro Transactions":
    "Giving commands to your units costs resources based on the unit&apos;s cost.",
    "Missile Command":
    "Endless missile bombardments target your structures and must be shot down throughout the mission.",
    "Vertigo":
    "Your camera randomly changes positions.",
    "Undying Evil":
    "A monster is deployed against you.  Each time you kill it, it will gather more power and return even stronger.",
    "Polarity":
    "Each enemy unit is immune to either your units or your ally&apos;s units.",
    "Transmutation":
    "Enemy units have a chance to transform into more powerful units whenever they deal damage.",
    "Afraid of the Dark":
    "Vision provided by all sources is extremely limited except when in view of your camera.",
    "Trick or Treat":
    "Civilians visit your Candy Bowl looking for treats, which are generated by spending minerals. If no treats are available, the civilians transform into random enemy units.",
    "Turkey Shoot":
    "Supply can only be generated by killing turkeys that wander throughout the map. Doing so may anger the turkeys that remain.",
    "Sharing Is Caring":
    "Supply is shared between you and your partner, and units from both armies contribute to your combined supply cap.",
    "Diffusion":
    "Damage dealt to enemies is split evenly across all nearby units, including your own.",
    "Black Death":
    "Some enemy units carry a plague that deals damage over time and spreads to other nearby units. The plague spreads to your units when the enemy unit is killed.",
    "Eminent Domain":
    "Enemies gain control of your structures after destroying them.",
    "Gift Exchange":
    "Gifts are periodically deployed around the map.  If you don&apos;t claim them, Amon will!",
    "Naughty List":
    "Player units and structures take increased damage for each enemy they&apos;ve killed.",
    "Extreme Caution":
    "Your units will not obey any command placed in areas they cannot see.",
    "Insubordination":
    "Your units don&apos;t follow orders exactly.",
    "Heroes from the Storm":
    "Attack waves will be joined by heroes of increasing power.",
    "Inspiration":
    "Enemy Heroic units increase the attack speed and armor of all enemies within a small range. ",
    "Hardened Will":
    "Enemy Heroic units reduce all incoming damage to a maximum of 10 when any non-heroic enemy unit is near them.",
    "Fireworks":
    "Enemies launch a dazzling fireworks display upon death, dealing damage to your nearby units.",
    "Lucky Envelopes":
    "Festive envelopes containing resource pickups are dropped at random throughout the map.",
    "Sluggishness":
    "Your units accelerate and turn slowly.",
    "Double-Edged":
    "Your units also receive all the damage they deal, but they are healed over time.",
    "Fatal Attraction":
    "When enemy units and structures die, any of your nearby units are pulled to their location.",
    "Propagators":
    "Shapeless lifeforms creep toward your base, transforming all of the units and structures they touch into copies of themselves.",
    "Moment Of Silence":
    "When a Heroic enemy dies, all player units around it will reflect on their transgressions, leaving them unable to attack or use abilities.",
    "Kill Bots":
    "Offensive robots of a mysterious origin have been unleashed on the Koprulu sector, intent on destruction. Through cunning engineering, they are invincible until their pre-programmed kill counter has been filled. After that occurs, they will shut down. But can you survive for that long?",
    "Boom Bots":
    "Uncaring automatons carry a nuclear payload toward your base. One player must discern the disarming sequence and the other player must enter it.",
    "The Mist":
    "Mists roll over battlefield while unseen terrors lurk inside. Desperate warriors will fall and rise again.",
    "The Usual Suspects":
    "Enemy attacks will be led by dark reflections of Heroes in the service of Amon",
    "Supreme Commander":
    r"Massive units gain 25% life and are bigger, the rest of units have 25% less life and are smaller. All units gain +2 weapon range.",
    "Shapeshifters":
    "Shapeshifters spawn with enemy attacks and in enemy bases. These creatures can transform into any unit of yours.",
    "Rip Field Generators":
    "Rip-Field Generators are deployed throughout the map. They will burn any unit that comes into their range.",
    "Repulsive Field":
    "Enemy attacks will push your units away.",
    "Old Times":
    "We are traveling back in time. Unit selection is limited to 12 units. There is no worker auto-mine, no smart cast, no multiple building select, etc.",
    "Nuclear Mines":
    "Nuclear Mines have been placed around the battlefield.",
    "Necronomicon":
    "Killed player units will rise again at enemy bases.",
    "Mothership":
    "Enemy Mothership roams the map and attacks player units.",
    "Matryoshka":
    "Enemy units will spawn mini-self upon death. This can trigger several times for larger units.",
    "Level Playing Field":
    "All weapons and abilities can hit both air and ground targets.",
    "Infestation Station":
    "Damaging any structure can cause infestation.",
    "I Collect, I Change":
    "When a non-heroic unit kills a hostile unit, it becomes the unit it killed. Units can only evolve into more expensive units.",
    "Great Wall":
    "Enemy begins massive effort to construct defensive structures around the battlefield.",
    "Endurance":
    "Player and enemy units and structures have 3x more health and shields.",
    "Dark Mirror":
    "Enemy attack waves will contain player units.",
    "Bloodlust":
    "Enemy units gain increased attack speed, movement speed, acceleration and damage reduction as their health gets lower.",
    "BlizzCon Challenge":
    "The BlizzCon Challenge starts with a single Mutator. As time passes, more Mutators will be added, until TEN Mutators are running wild at the same time."
}

mutator_ids = {
    'AfraidOfTheDark': 'Extreme Caution',
    'AllEnemiesCloaked': 'We Move Unseen',
    'Avenger': 'Avenger',
    'Barrier': 'Barrier',
    'BlackFog': 'Darkness',
    'BlizzConChallenge': 'BlizzCon Challenge',
    'Blizzard': 'Blizzard',
    'Bloodlust': 'Bloodlust',
    'BoomBots': 'Boom Bots',
    'ConcussiveAttacks': 'Concussive Attacks',
    'CycleRandom': 'Chaos Studios',
    'DamageBounce': 'Diffusion',
    'DamageReflect': 'Double-Edged',
    'DarkMirror': 'Dark Mirror',
    'DeathAOE': 'Self Destruction',
    'DeathPull': 'Fatal Attraction',
    'DropPods': 'Aggressive Deployment',
    'Endurance': 'Endurance',
    'Entomb': 'Mineral Shields',
    'Evolve': 'Transmutation',
    'Fear': 'Fear',
    'FireFight': 'Scorched Earth',
    'Fireworks': 'Fireworks',
    'FoodHunt': 'Turkey Shoot',
    'GiftFight': 'Gift Exchange',
    'GreatWall': 'Great Wall',
    'HardenedWill': 'Hardened Will',
    'HeroesFromTheStorm': 'Heroes from the Storm',
    'HeroesfromtheStormOld': 'Heroes from the Storm (old)',
    'HybridNuke': 'Mutually Assured Destruction',
    'ICollectIChange': 'I Collect, I Change',
    'InfestationStation': 'Infestation Station',
    'InfestedTerranSpawner': 'Outbreak',
    'Inspiration': 'Inspiration',
    'Insubordination': 'Insubordination',
    'JustDie': 'Just Die!',
    'KillBots': 'Kill Bots',
    'KillKarma': 'Naughty List',
    'LaserDrill': 'Laser Drill',
    'LavaBurst': 'Lava Burst',
    'LazyWorkers': 'Nap Time',
    'LevelPlayingField': 'Level Playing Field',
    'LifeLeech': 'Life Leech',
    'LongRange': 'Long Range',
    'Magnificent': 'Mag-nificent',
    'Matryoshka': 'Matryoshka',
    'MissileBarrage': 'Missile Command',
    'MomentOfSilence': 'Moment Of Silence',
    'Mothership': 'Mothership',
    'Necronomicon': 'Necronomicon',
    'NoResources': 'Slim Pickings',
    'NuclearMines': 'Nuclear Mines',
    'Nukes': 'Going Nuclear',
    'OldTimes': 'Old Times',
    'OopsAllCasters': 'Power Overwhelming',
    'OrbitalStrike': 'Orbital Strike',
    'OrderCosts': 'Micro Transactions',
    'PhotonOverload': 'Photon Overload',
    'Plague': 'Black Death',
    'Polarity': 'Polarity',
    'Propagate': 'Propagators',
    'PurifierBeam': 'Purifier Beam',
    'Random': 'Random',
    'Reanimators': 'Void Reanimators',
    'RedEnvelopes': 'Lucky Envelopes',
    'ReducedVision': 'Shortsighted',
    'RepulsiveField': 'Repulsive Field',
    'RipFieldGenerators': 'Rip Field Generators',
    'Shapeshifters': 'Shapeshifters',
    'SharedSupply': 'Sharing Is Caring',
    'SideStep': 'Evasive Maneuvers',
    'Sluggish': 'Sluggishness',
    'SpawnBroodlings': 'Alien Incubation',
    'SpiderMines': 'Minesweeper',
    'StoneZealots': 'Stone Zealots',
    'StructureSteal': 'Eminent Domain',
    'SupremeCommander': 'Supreme Commander',
    'TemporalField': 'Temporal Field',
    'TheMist': 'The Mist',
    'TheUsualSuspects': 'The Usual Suspects',
    'TimeWarp': 'Time Warp',
    'Tornadoes': 'Twister',
    'TrickOrTreat': 'Trick or Treat',
    'UberDarkness': 'Afraid of the Dark',
    'UndyingEvil': 'Undying Evil',
    'UnitSpeed': 'Speed Freaks',
    'Vertigo': 'Vertigo',
    'VoidRifts': 'Void Rifts',
    'WalkingInfested': 'Walking Infested'
}

cached_mutators = {
    "01a686a72bc7913e88372836fa4927fc030065a2a5975f9890e8639f8ac3d675": "Just Die!",
    "01cca5a8f4bcc06cc4aca3af8c2f821894d3b15fe7ebc20721c514fb7613484f": "Life Leech",
    "04b1c156186ea45b806a1240f7b0afff5fb28ed7a84544eef2df69b04624e498": "Purifier Beam",
    "05275a4be121ff1934bb97c0c9c971116eb23e395795281bb3b04f70143c48e9": "Photon Overload",
    "057876296486c3b308c07a5bd381edb2902535a8aaedc98d370ec8f21491146f": "Eminent Domain",
    "05d65f9a393acd2cb0bd0e75dba1d6d768fca9a880b026a007b0e1b3a9a7b222": "Purifier Beam",
    "073559502b43a55be5fafad13b3f113b22b312644aa1f61be23e194b937e0cf1": "Temporal Field",
    "0c7a3c1df15deb6380b31f4fe6124c05557dce68b349e61e2a3d7caad2fbe597": "Power Overwhelming",
    "11f3007dd11366aae688078f4b6470aae78943f92b8632151189854ca668207c": "Aggressive Deployment",
    "135c8a611dc7c91a4c392158ec1da835ef91aa2c3145ce1eb44012e8f3f16e20": "Orbital Strike",
    "139009a1a3b1432d8bf52ebdba1cc17eefa9b51c8b95be66b82d003cc72028c7": "Heroes from the Storm",
    "15d4ef2a6a9ab20f48ea5c36322b5fb7cf8a34ad00219e12d6bd6865a59e8617": "Blizzard",
    "16a74784e2b890fb3955405a0ed5da266e94970782a51234588adb53be509e87": "Black Death",
    "19240574419b3a0c4c56a81043194ea30ac9486bee787dc964e1dd17e995242e": "Evasive Maneuvers",
    "22000af68d0b8fce00e931ee5caf18e52886525b93987d81f07b04ccc62fdcc7": "Shortsighted",
    "231959a75ae730a340bfe1791b4989d32ed3ce2f798639d06c9ac66c72230d19": "Barrier",
    "23e28fcf77f92c5376d250e4c48a53663bd34c1da7aba6f22e4fe9c46fbe0ec8": "Fatal Attraction",
    "23f251c7b3f2e2d1900fc6722e60381c96d261d6bc57ff0a7be9f6c1f0fe1b02": "Aggressive Deployment",
    "24c8d951cd7aeb1896aa0684bf4d63b201d3b558e05d3d6fce68a0d4124c9050": "Long Range",
    "2a8a05a8aea5c9278d811461f4faf61391be6be096e67cced155cbbbc692d59b": "Mutually Assured Destruction",
    "2a9359177ea18344962bfd53c0b4cbcdd7ee2cd9691788b043f59d06878acbb3": "Void Rifts",
    "2b806bca81c5bd59092c37f07731687b94ae1cfe9a5a68fa325d8beae9d9ce7b": "Naughty List",
    "2cd183b2254d32bd39bfb01ca9687d4b11ad2c3e48f24d2ab4ae548d78d59119": "Laser Drill",
    "30b659e179ec71f3d448f79122bb601758b49d742367a96a81c990c418350a57": "Self Destruction",
    "330fbb2f261fc3edd7346d00e86dede446aeeb4f7b547ab548c9a1e2400fc3bc": "We Move Unseen",
    "3359f53ad879edcff3d4bd945975ff790c447997ac87258c26b50ee18ff8a81a": "Going Nuclear",
    "34ab17060764007330aa1d25407ee48058f14c105834ce21ac8f61023ab2b8b8": "Darkness",
    "353280ab221016bea49cadd5a493e614843eb8117a8142431c8cc49e1de83838": "Naughty List",
    "35418762f6f1a9cec710a2b481e4a47065dafadacf6fe62b6fe0c49ea3782be7": "Minesweeper",
    "361997222a115f9ee1ed7c27370c159beca493418bdb384671d43ff4ac4dbcf4": "Temporal Field",
    "3665c3000883575d1ab334c926335a43ef893c313dd296ce687d055755e57e64": "Boom Bots",
    "380cffaed4a624f82aecd3f92321c9547ccb952b91c73c947547ba462d2993fd": "Moment Of Silence",
    "39e5523cacdc7fd597b729a34af41722d826ec1d728fd094ba16e0a0550d9f5d": "Blizzard",
    "39ed258e07ca1aab0f28415393dc3a9f5cfa229722bdc4e4d4f7ea2bac97bcfa": "Inspiration",
    "3e85ae0f03dc0fe9954a3266187425b6c218dafc04871011d814ed847536c48b": "Void Reanimators",
    "42646741c98fc211e77a5357f9baa16e0401bbbaf0a475f01c7a8ee3b8485b6a": "Minesweeper",
    "4265c9017c7e11372ab47e41c89d23ac89a13a8ffe63d2b62d1d7e593f56b0be": "Self Destruction",
    "45607c339ce8ea56abc7f3a3e07bfc5e737ab3d0bb9fed8a13367ffd221c92c1": "Propagators",
    "4735f7b1ed07157e2f3dbee234f155a0db945e6e428c5e71caf121c36cc50667": "Scorched Earth",
    "486cdc9772e53fee1063fd44c51b46915ffad23ea90d6a6437d1bba084da0374": "Time Warp",
    "4a3565eadab6188fbfa89538cb36f9d87d5d4cbe5b3c260a39e636279eb9b0c7": "Inspiration",
    "4b7c358c83c6e1c23e134fc475d1c7f18712eae93677330041d0173bcb614a3c": "Photon Overload",
    "4b96dd7899570bcd7f886793a385c369b42585d343b7d1133aea3ff0f67a7d3e": "Fireworks",
    "4e937d1296733abe274a86b9d4f9752f0c244e17f4f520eb7e06229c08c6cb85": "Avenger",
    "4eb8d8cf889d99d4291e539442a2d5b199766533e456c89f07fdebb27ac29e77": "Alien Incubation",
    "51fe1911136825003b8149444f40b47bdda1ff62f7e0410ea0d3cfbb67cea34c": "Mag-nificent",
    "55dcd1ad7564f7235fd5b7ef4151cfbb601682c4880b860a912d1d89e71ecb4e": "Gift Exchange",
    "573904e360c1978352e7235b04c606f9ce93b2c789004e18528e33ed2666a2f1": "Void Reanimators",
    "5b99dc312bd27de3f0fd2115c0d7b29986b6e925cdc10f4a1169ebf86a0cd45c": "Lava Burst",
    "5d3604662f09aa88691abb410741f24955d7854a785423680e1ec8e4f8d0286b": "Polarity",
    "5f453a5e06b72d2be29730c6b7ed37221bfccc2b840af50cfe485f02159a1c99": "Fatal Attraction",
    "5fe8c5f010244aadabb9eb4f749d3fb3fb9b3fcc6821325e5c5e29431229fc8c": "Heroes from the Storm",
    "627cb556b957d5e3f9dff1a3ff2236b0ee1392b9f392941d8b0421775afd6ea7": "Mag-nificent",
    "63e5915486c1cdbc63a28646d277820cc2728533e4524d5bf10270e816ff3981": "Turkey Shoot",
    "672ed864d3a40045d09a33ff44ef2619302bef85ec6bfde815a8978a818fcd1e": "Sharing Is Caring",
    "676917264327fc3aa738f5538d68709900f42eb45c4437f3e264336696355a32": "Alien Incubation",
    "6bd271a193e8a2948f0ffbe1c3c4ac1299ed3b6d5d93e47b0a356f0cb92dadb0": "Mutually Assured Destruction",
    "6f74552abecb937eb191943d61b5df5165d0b2a4ab90a692f9a879b78d23d3f9": "Polarity",
    "7100a707c844ad47b403313c4d857206695c61ed34894cac8fd13d18a1b3ee9b": "Fear",
    "724a310a640016b5d1c9e5d90007c7eddd13b6ffea3ede41da2a1af272baf2e5": "Barrier",
    "7250739c04cf4cdc34b9b42bcbfd9d7fd1cdd5a2e5aab13a85ab9805eaab4205": "Micro Transactions",
    "747fb5fc02eac0e9d8a34dff85d9c3adb12e5420cd0eab8b92ee17acd4ade7c6": "Barrier",
    "74d264e9d22d069c541a3de9a3cbf93207f6bce6f94caf8b0cfe88cb38cef96e": "Transmutation",
    "7571681bad2c3855fe138b6741ab696bfdd956410ba0e0bb2dc63942b5bf746d": "Just Die!",
    "762e1b46b87e64de180ed6187f5b93bab49654365d84c8ecafe3135d5ed576a5": "Double-Edged",
    "81e1b6fb131ee8efe7fda4f9dd398129f4f73adb3dcfa09cf74bb9442957f9e9": "Twister",
    "836eb09ed0f8b223316518f962c55ade38c64b59022c1e24648009568603b769": "Missile Command",
    "85f23fb5419b07e5c9f738a4781ae0427adfd3adedf7e7a19b2e01277776ee1a": "Self Destruction",
    "87b2415ef829362ea8e287c58511bd043f50cbd84309c45be44c159afb04a78f": "Concussive Attacks",
    "89b1506ea744a569e820ab56e5517a9f8d0c7c9ccace3c76d270e9986e42b339": "Power Overwhelming",
    "89bb9a5dff0ef30c5279c593d20304c17b1c59ae444dc7f17cd4526ef1c7563c": "Twister",
    "89df2f030e8d1684d5b3ff85634d65789a5eb96ee1a61c5996139fdcee7bdf7f": "Fear",
    "8acd1a202e3ce9f542bd2c699d85c937e7a11608d9bd992964ccfbe304d77679": "Black Death",
    "8b7f59a24415e44296a59985f435dd5e65cf2a14f79f927f631570887d5bbe1e": "Diffusion",
    "91500217f1d70365e465bfd33c10cae2dd208bf9b389a85c2cbe261c4f54f1c0": "Long Range",
    "91a2a2260fd5238977c16bf436354e6b1f9e2c9af0f9386bdfbc7e1c892a200b": "Avenger",
    "939d9467f8f2e8163d0772a548c6f6d071357e93544c551b14a0e1ea7bbc3ba2": "We Move Unseen",
    "9416f0b431e55a7add319a146c7f684440ffbaf6e3bd2ecbcd1189b9035e5f7f": "Lucky Envelopes",
    "943da7cbc62db37b2a721139b06f9c3d2b80ab01686a6fec06945854bd2dfa0b": "Boom Bots",
    "94c6d4c733da8ab37f04ff8d1d34c329ed18d7afe434570b375f6f2537e5b8f3": "Boom Bots",
    "94d9ee1f9a695d3e8f79e1f69f12da8ebac4e28e06e2ae989e76c30465bd4201": "Void Rifts",
    "972dd6be6c8c5cdf6909c79dce0017fb06ff1ca82348a7632813b47a691a1a76": "Kill Bots",
    "9c1933c65cfefef1d351c13bdf7bd8a2d9da90a94a9c1f4e87a16c5f5917f715": "Slim Pickings",
    "9dd04be65e744421161c6f342f42a0cfa28b814d874a311c7ae926a37cae39b2": "Lucky Envelopes",
    "a3677ada7c848d88e40c0ba3dffa878f9458c9cec7d4736914cc6441d1b2364e": "Vertigo",
    "a38d57e425d106c78d08ae6ab58b0c55616bac2f00c54daa0b7b3564c961bab8": "Void Rifts",
    "a5108d473ab82cb159666cd272107cf66fcf85e603db8d96a432c62018dbfc05": "Scorched Earth",
    "abe0fe81744894b85ccde58d5feea8a72e8683039986eb52958c4ab55179f4be": "Temporal Field",
    "ad2a5483bdd6fbfaeffad5602e6988dc4fddf864e26dd7f7b40232fc253b7a38": "Orbital Strike",
    "af1e64bec5061b3c5d8fbfaae31fd465dcd69f9fd9e173cbef27c69b13873b9c": "Kill Bots",
    "b2d409fb570d0850cde8ac9a5ddd6033526cd6b393e6f99adac7ab5e2cddc108": "Double-Edged",
    "b61435616364f1948dd2badf180f4bb1a1b010f61a07bb34b7b87a9152a1b1bd": "Evasive Maneuvers",
    "b90db34f92ed389b3efd21049b1b7d8f6da2b7adf7d4fe5511dc145350ae02dd": "Going Nuclear",
    "ba0c578a12808f284cff10c61d81075c8b3755d7cc748e2ef5accb9b2bf69aa5": "Trick or Treat",
    "ba56c8f9ab538637f8d536b4558aed2a8fd6164c27276e0c2bb1ac62a6ea43d2": "Hardened Will",
    "ba9a4241a65b523f07cec24032049e3d08cbf448a10fc293c8f5a4b3bd1498a3": "Missile Command",
    "bd8ba5c834e3aec3c900917f31acfe8fe5b48f3f1b416d053045894a34f8d229": "Speed Freaks",
    "bdfee67384ca83e0f6f5a4941823694fa4029a2c08d22620b461613274b44dbe": "Walking Infested",
    "bfff57aae44d80060026078f0f8ba836a5264e122bdb607ad057fa2eee5361f6": "Darkness",
    "c2684800616d9b68db92b665c7f2d1c298c63666edcf07042573c8fa4d50862e": "Avenger",
    "c59426825f7a70fc2c3d68e8ae5e13de20df2c09bbc3cf7e7e98fd19e1bdeb4e": "Concussive Attacks",
    "c639c63aafa49c0d206433da3eb101ebd1236bead6483e18f4f9894c29b6ec9a": "Moment Of Silence",
    "c72b95868184c274f69dc6d63c8ebcae0a26ee75ad7ec7c72904576e3350c1c1": "Time Warp",
    "caff0773c64bdc9ea0c25eaec78319240a578ca8b12be465790c79ed162ddf08": "Lava Burst",
    "cb69aa314adaa650a1a677058b312241ac7dbb7b0c9e9e8dd02c68d93a1a7d92": "Transmutation",
    "cb9e4cd5318dc2dee26cc88aeb25b80bb59ac85c037f015f74bd88f3c09e2e0e": "Speed Freaks",
    "ce24a7a91025aac72c0568e1d0968ef93b56d4ac3144bf6d6ed0e32ab6157bc5": "Photon Overload",
    "d327ce560c0099d0f6af620a76bebf6d1e2a24cb33477e4fae63d358d841c3e4": "Concussive Attacks",
    "d61aa23015ecaa00bf1d416544c87dd4ecc9e3b2f23b6d380cc9cb33749c2320": "Shortsighted",
    "d638c2e3de426df7c3037600d5235af5db406890d5923c89e29ffe967d358945": "Outbreak",
    "d7a53f3436cf617c0087fa2a977f4546213d7abf95c84ef7aaf50d00cab49e69": "Void Reanimators",
    "daa178a93fdb5d61e5ed04f8fc46a461aa3caeabd4e6910099cdf318bc20b458": "Hardened Will",
    "ddb453e56f03519989bfe734b90d8d66f93b1cf79c4ac849124160c9264cc2f7": "Life Leech",
    "df14b92bcd8aefdcb69f05fe95c1b15c4bf6f55a030067c70c181617d5089efb": "Mag-nificent",
    "e126d99d28e3a5ebd252dddfacdfd5f2885fdca719ac86a8a37f43eae90ee394": "Chaos Studios",
    "e36811e8d4005e6a88833216051a0e2807473bee9659871e88a01a0ef71c677c": "Fear",
    "e50aae1226eba30382b1463e94728a30b8413a5df5c695e3bfff25aa52110d4c": "Afraid of the Dark",
    "e51a59ef0e0db779d580a7efea27e8f5d99d33131630f0317b4dee2ac325f7d8": "Hardened Will",
    "eb039312a203c28cf1c592ce34e85b595d576f17e120de1d4db3a0ca50295a46": "Purifier Beam",
    "f113cf92052fe818456d7e78c8a0ac64933333d1b0c4fa92f41fa451e32fce38": "Polarity",
    "f3c495d59a04d3b329ecf2764829366a8a4bc311b2011f367835bd5aa6db7e89": "Orbital Strike",
    "f4dd9e55307f83a6c2d6d237b72ab4a930fd4d25e27fce0d470ec217f58a1703": "Propagators",
    "f5bdce6e9cb9c0cd6d05092cb86b02c149ae93b5f9913d3fa351ba0176fe05d8": "Walking Infested",
    "f690f113c4b463daaa942bf4b7c94a71a4c2d6e3f6eaaa83eeeb27da5c308bca": "Chaos Studios",
    "f791a2dc2ed066a941e279a58dd7efe9de4442fe08ecfd8fa10409b848ec7b9c": "Aggressive Deployment",
    "f86c47a2fd0812da7767becaceeebd33f9a2c8ec7f4a9fb82d3abd677ed618ba": "Mineral Shields",
    "f93f73e5118bfee7875dd9cd30e026e8eb20db73561d7c361311fc78b893afda": "We Move Unseen",
    "fbfbc4a5020812dc75655c5ee70484cbf1fd73854c34231e06aee2ad2497508f": "Minesweeper",
    "fc9f09f8e7df2d63222991af3aea68482963181c7423291ce8fdfe53f65d95fc": "Darkness",
    "fec1e2ac7b4b0a478dd02fb2350bcaaa60a5023c9e970ee4634b928ab32214d1": "Time Warp"
}

# Base unit costs for commanders
# Morphs show the added cost first, and full cost later.
unit_base_costs = {
    'Abathur': {
        'Brutalisk': (0, 0, 100, 0),
        'Devourer': (75, 25, 175, 125),
        'GuardianMP': (25, 50, 125, 150),
        'HotSLeviathan': (0, 0, 100, 100),
        'Mutalisk': (100, 100),
        'Queen': (150, 50),
        'RavagerAbathur': (13, 38, 113, 38),
        'RavagerAbathurCocoon': (0, 0, 100, 0),
        'Roach': (100, 0),
        'RoachVile': (100, 0),
        'SpineCrawler': (150, 0),
        'SporeCrawler': (125, 0),
        'SwarmHost': (200, 100),
        'Overseer': (50, 50),
        'Viper': (100, 200)
    },
    'Alarak': {
        'ColossusTaldarim': (300, 200),
        'HighTemplarTaldarim': (50, 150),
        'ImmortalTaldarim': (250, 100),
        'PhotonCannon': (150, 0),
        'SOAMothershipv4': (0, 0),
        'Stalker': (125, 50),
        'Supplicant': (75, 0),
        'VoidRayTaldarim': (0, 0),
        'WarpPrismTaldarim': (200, 0),
        'Monitor': (50, 100)
    },
    'Artanis': {
        'Archon': (0, 0, 100, 300),
        'Dragoon': (125, 50),
        'HighTemplar': (50, 150),
        'ImmortalAiur': (250, 100),
        'PhoenixAiur': (150, 100),
        'PhotonCannon': (150, 0),
        'Reaver': (300, 200),
        'Tempest': (300, 200),
        'Zealot': (100, 0),
        'Observer': (25, 75),
        'Zealot': (100, 0),
        'ZealotAiur': (100, 0)
    },
    'Dehaka': {
        'DehakaGuardian': (0, 100, 150, 150),  # This one is lost
        'DehakaGuardianFightMorph': (0, 100, 150, 150),  # This one is actually created
        'DehakaHydraliskLevel2': (100, 50),
        'DehakaMutaliskLevel3': (0, 25, 200, 125),  # This one is lost
        'DehakaMutaliskLevel3FightMorph': (0, 25, 200, 125),  # This one is actually created
        'DehakaMutaliskReviveEgg': (0, 0, 200, 125),  # Revive egg
        'DehakaNydusDestroyer': (300, 0),
        'DehakaRavasaur': (0, 0, 100, 0),
        'DehakaRoachLevel2': (75, 25),
        'DehakaRoachLevel3': (0, 0, 150, 50),
        'DehakaUltraliskLevel2': (300, 200),
        'DehakaUltraliskLevel3': (0, 0, 600, 400),
        'DehakaSwarmHost': (100, 75),
        'DehakaPrimalSwarmHost': (0, 0, 200, 150),
        'DehakaZerglingLevel2': (50, 0),
        'ImpalerDehaka': (0, 0, 200, 100),
    },
    'Fenix': {
        'AdeptFenix': (100, 40),
        'ColossusPurifier': (240, 160),
        'Disruptor': (120, 120),
        'Immortal': (200, 80),
        'Interceptor': (0, 0),
        'PhotonCannon': (150, 0),
        'Observer': (20, 60),
        'Carrier': (280, 200),
        'Scout': (180, 60),
        'SentryFenix': (40, 80),
        'ZealotPurifier': (160, 0),
        'FenixTalisAdept': (0, 0, 100, 40),
        'FenixKaldalisZealot': (0, 0, 160, 0),
        'FenixWarbringerColossus': (0, 0, 240, 160),
        'FenixTaldarinImmortal': (0, 0, 200, 80),
        'FenixMojoScout': (0, 0, 180, 60),
        'FenixClolarionCarrier': (0, 0, 280, 200)
    },
    'Horner': {
        'HHBattlecruiser': (1000, 800),
        'HHBomberPlatform': (100, 100),
        'HHHellion': (100, 0),
        'HHHellionTank': (100, 0),
        'HHMercStarportUpgraded': (0, 0, 150, 0),  # Normal Galleon
        'HHMercStarportNoArmy': (150, 0),  # Galleon under construction
        'HHReaper': (50, 0),
        'HHReaperFlying': (0, 0),
        'HHVikingFighter': (400, 250),
        'HHWidowMine': (100, 0),
        'HHWraith': (400, 200),
        'HHRaven': (100, 200),
        'MissileTurret': (100, 0)
    },
    'Karax': {
        'ColossusPurifier': (390, 260),
        'Colossus': (390, 260),
        'ImmortalAiur': (325, 130),
        'Interceptor': (0, 0),
        'KhaydarinMonolith': (300, 100),
        'PhoenixPurifier': (195, 130),
        'PhotonCannon': (150, 0),
        'SentryPurifier': (65, 130),
        'ShieldBattery': (100, 0),
        'Observer': (25, 75),
        'Carrier': (455, 325),
        'CarrierAiur': (455, 325),
        'ZealotPurifier': (130, 0)
    },
    'Kerrigan': {
        'BroodLord': (150, 150, 250, 250),
        'HotSRaptor': (25, 0),
        'HotSTorrasque': (300, 200),
        'TorrasqueChrysalis': (0, 0, 300, 200),
        'HydraliskLurker': (100, 50),
        'Lurker': (50, 100, 150, 150),
        'MutaliskBroodlord': (100, 100),
        'QueenCoop': (150, 0),
        'SpineCrawler': (150, 0),
        'SporeCrawler': (125, 0),
        'Ultralisk': (300, 200),
        'Overseer': (50, 50),
        'Zergling': (25, 0)
    },
    'Mengsk': {
        'ArtilleryMengsk': (150, 100),
        'BattlecruiserMengsk': (320, 720),
        'GhostMengsk': (160, 400),
        'MarauderMengsk': (100, 280),
        'MissileTurretMengsk': (100, 0),
        'SiegeTankMengsk': (120, 340),
        'ThorMengsk': (240, 480),
        'TrooperMengsk': (40, 0),
        'TrooperMengskAA': (160, 0, 200, 0),
        'TrooperMengskFlamethrower': (160, 0, 200, 0),
        'TrooperMengskImproved': (160, 0, 200, 0),
        'VikingMengskFighter': (120, 300),
        'RavenMengsk': (100, 100),
        'MedivacMengsk': (100, 50),
    },
    'Nova': {
        'Banshee_BlackOps': (350, 187.5),
        'GhostFemale_BlackOps': (500, 250),
        'Ghost_BlackOps': (500, 250),
        'Goliath_BlackOps': (375, 125),
        'HellbatBlackOps': (250, 0),
        'HellionBlackOps': (250, 0),
        'LiberatorAG_BlackOps': (375, 375),
        'Liberator_BlackOps': (375, 375),
        'Marauder_BlackOps': (250, 65),
        'Marine_BlackOps': (150, 0),
        'MissileTurret': (100, 0),
        'NovaACLaserTurret': (0, 0),
        'Raven_BlackOps': (100, 200),
        'SiegeTankSieged_BlackOps': (400, 300),
        'SiegeTank_BlackOps': (400, 300),
        'SpiderMine': (16.666, 0)
    },
    'Raynor': {
        'Banshee': (150, 80),
        'Battlecruiser': (400, 240),
        'Bunker': (100, 0),
        'Firebat': (100, 25),
        'Marauder': (100, 25),
        'Marine': (50, 0),
        'MissileTurret': (100, 0),
        'SiegeTank': (150, 100),
        'SpiderMine': (15, 0),
        'VikingAssault': (150, 60),
        'Medic': (75, 50),
        'Vulture': (75, 0)
    },
    'Stetmann': {
        'BanelingStetmann': (25, 15, 50, 15),
        'BroodLordStetmann': (300, 250, 450, 350),
        'CorruptorStetmann': (150, 100),
        'HydraliskStetmann': (100, 50),
        'InfestorStetmann': (100, 150),
        'LurkerStetmann': (50, 100, 150, 150),
        'SpineCrawlerStetmann': (150, 0),
        'SporeCrawlerStetmann': (125, 0),
        'UltraliskStetmann': (300, 200),
        'OverseerStetmann': (50, 50),
        'ZerglingStetmann': (25, 0),
        'BroodLordStetmannCocoon': (0, 0, 150, 100),
        'BanelingStetmannCocoon': (0, 0, 25, 0),
        'LurkerStetmannCocoon': (0, 0, 100, 50)
    },
    'Stukov': {
        'SIInfestedBunker': (400, 0),
        'SIInfestedMarine': (15, 0),
        'SILiberator': (150, 125),
        'SIMissileTurret': (100, 0),
        'SIQueen': (100, 100),
        'Overseer': (50, 50),
        'StukovInfestedBanshee': (150, 100),
        'StukovInfestedDiamondBack': (225, 75),
        'StukovInfestedSiegeTank': (200, 100),
    },
    'Swann': {
        'Cyclone': (150, 100),
        'Goliath': (150, 50),
        'Hellion': (100, 0),
        'HellionTank': (100, 0),
        'Hercules': (100, 50),
        'KelMorianGrenadeTurret': (150, 0),
        'KelMorianMissileTurret': (100, 0),
        'PerditionTurret': (75, 0),
        'PerditionTurretUnderground': (75, 0),
        'ScienceVessel': (100, 200),
        'SiegeTank': (150, 125),
        'SiegeTankWreckage': (0, 0, 150, 0),
        'Thor': (300, 200),
        'ThorWreckageSwann': (0, 0, 300, 0),
        'Wraith': (150, 50)
    },
    'Tychus': {
        'TychusFirebat': (1000, 200),
        'TychusMedic': (1000, 200),
        'TychusGhost': (1000, 200),
        'TychusHERC': (1000, 200),
        'TychusMarauder': (1000, 200),
        'TychusReaper': (1000, 200),
        'TychusSCVAutoTurret': (150, 0),
        'TychusSpectre': (1000, 200),
        'TychusWarhound': (1000, 200),
    },
    'Vorazun': {
        'CorsairMP': (150, 100),
        'DarkArchon': (175, 275),
        'DarkTemplarShakuras': (125, 75),
        'Oracle': (100, 75),
        'PhotonCannon': (150, 0),
        'StalkerShakuras': (125, 50),
        'Stalker': (125, 50),
        'VoidRayShakuras': (250, 150),
        'VoidRay': (250, 150),
        'ZealotShakuras': (100, 0)
    },
    'Zagara': {
        'Baneling': (22, 14, 36.666, 14),
        'BanelingCocoon': (0, 0, 14.666, 0),
        'BileLauncherZagara': (150, 100),
        'HotSSplitterlingBig': (22, 14, 36.666, 14),
        'HotSSplitterlingMedium': (0, 0),
        'HotSSwarmling': (14.666, 0),
        'InfestedAbomination': (180, 68),
        'QueenCoop': (150, 0),
        'Scourge': (11.5, 9),
        'Overseer': (50, 50),
        'SpineCrawler': (100, 0),
        'SporeCrawler': (125, 0),
        'ZagaraCorruptor': (135, 90),
        'Zergling': (25, 0)
    },
    'Zeratul': {
        'ZeratulObserver': (25, 75),
        'ZeratulDarkTemplar': (375, 225),
        'ZeratulDisruptor': (450, 450),
        'ZeratulImmortal': (750, 300),
        'ZeratulPhotonCannon': (300, 0),
        'ZeratulSentry': (75, 150),
        'ZeratulStalker': (300, 50),
        'ZeratulWarpPrism': (150, 0),
    }
}

royal_guards = {
    'BattlecruiserMengsk', 'GhostMengsk', 'MarauderMengsk', 'SiegeTankMengsk', 'SiegeTankMengskSieged', 'ThorMengsk', 'ThorMengskSieged',
    'VikingMengskFighter', 'VikingMengskAssault'
}

horners_units = {'HHBattlecruiser', 'HHVikingAssault', 'HHVikingFighter', 'HHWraith', 'HHRaven', 'HHRavenSiegeMode'}

tychus_base_upgrades = {
    'TychusMedicDoubleBeam', 'TychusHercGrappleArmor', 'TychusMedicAdvancedHealingSpray', 'TychusMedicSuperHealing', 'TychusACImplosionGrenades',
    'TychusFirebatIncendiaryPetroleum', 'TychusGhostDominateBuff', 'TychusMarauderSuperStim', 'TychusACRageGrenades', 'TychusWarhoundDeathExplosion',
    'TychusSpectreVisionSuit', 'TychusMarauderHealingWardBuff', 'TychusSpectreSuperUltrasonicPulse', 'TychusACPiercingRounds',
    'TychusMarauderHealingWardSpeedBuff', 'TychusWarhoundHaywireMissiles', 'TychusHercRage', 'TychusFirebatPremiumPetroleum', 'TychusReaperBombStun',
    'TychusGhostDominatingDomination', 'TychusGhostPsychicSnare', 'TychusHercGrappleStun', 'TychusReaperEvasionBuff', 'TychusWarhoundFear',
    'TychusSpectreExtendedPulseGun', 'TychusFirebatBlueFlameOil', 'TychusReaperBombDamage'
}

tychus_ultimate_upgrades = {
    'TychusWarhoundTurretUpgrade', 'TychusMedicDefensiveMatrix', 'TychusReaperBombCharges', 'TychusSpectreBrillianceAura',
    'TychusGhostConcentrationHelmet', 'TychusFirebatShield', 'TychusMarauderAttackSplash', 'TychusHercCrit', 'TychusACBandofBrothers'
}

outlaws = {'TychusFirebat', 'TychusGhost', 'TychusHERC', 'TychusMarauder', 'TychusReaper', 'TychusSpectre', 'TychusWarhound', 'TychusMedic'}

weekly_mutations = {
    'Aggressive Recriutment': {
        'map': 'Malwarfare',
        'mutators': {'Speed Freaks', 'We Move Unseen', 'Propagators'}
    },
    'And Drops and Rifts': {
        'map': 'Part and Parcel',
        'mutators': {'Aggressive Deployment', 'Void Rifts'}
    },
    'Assembly of Vengeance': {
        'map': 'Temple of the Past',
        'mutators': {'Heroes from the Storm', 'Avenger'}
    },
    'Astigmatism': {
        'map': 'Malwarfare',
        'mutators': {'Long Range', 'We Move Unseen', 'Shortsighted'}
    },
    'Attrition Warfare': {
        'map': 'Void Thrashing',
        'mutators': {'Minesweeper', 'Diffusion'}
    },
    'Bad Weather': {
        'map': 'Rifts to Korhal',
        'mutators': {'Void Rifts', 'Twister'}
    },
    'Bannable Offense': {
        'map': 'Malwarfare',
        'mutators': {'Power Overwhelming', 'Evasive Maneuvers'}
    },
    'Barrier to Entry': {
        'map': 'Lock & Load',
        'mutators': {'Just Die!', 'Mineral Shields', 'Barrier'}
    },
    'Battle Hardened': {
        'map': 'Chain of Ascension',
        'mutators': {'Inspiration', 'Missile Command', 'Hardened Will'}
    },
    "Beggars Can't be Choosers": {
        'map': 'Lock & Load',
        'mutators': {'Mag-nificent', 'Minesweeper', 'Slim Pickings'}
    },
    'Binary Choice': {
        'map': 'Malwarfare',
        'mutators': {'Polarity', 'Void Reanimators'}
    },
    'Blast from the Past': {
        'map': 'Temple of the Past',
        'mutators': {'Eminent Domain', 'Mutually Assured Destruction'}
    },
    'Blasting Off Again': {
        'map': 'Void Launch',
        'mutators': {'Power Overwhelming', 'Going Nuclear', 'Lava Burst'}
    },
    'Blind Tribute': {
        'map': 'Chain of Ascension',
        'mutators': {'Kill Bots', 'Shortsighted'}
    },
    'Boom Town': {
        'map': 'Oblivion Express',
        'mutators': {'Self Destruction', 'Fear', 'Going Nuclear'}
    },
    'Breath of Destruction': {
        'map': 'Mist Opportunities',
        'mutators': {'Speed Freaks', 'Aggressive Deployment', 'Avenger'}
    },
    'Bubble Pop': {
        'map': 'Cradle of Death',
        'mutators': {'Mineral Shields', 'Barrier', 'Time Warp'}
    },
    'Burning Evacuation': {
        'map': 'Miner Evacuation',
        'mutators': {'Eminent Domain', 'Avenger', 'Scorched Earth'}
    },
    'Burning Legion': {
        'map': 'Lock & Load',
        'mutators': {'Avenger', 'Void Rifts', 'Scorched Earth'}
    },
    'By Fire Be Purged': {
        'map': 'Oblivion Express',
        'mutators': {'Lava Burst', 'Going Nuclear', 'Scorched Earth'}
    },
    'Call it a Comeback': {
        'map': 'Temple of the Past',
        'mutators': {'Eminent Domain', 'Just Die!', 'Avenger'}
    },
    'Call of the Void': {
        'map': 'Void Thrashing',
        'mutators': {'Void Reanimators', 'Void Rifts'}
    },
    'Catch the Train': {
        'map': 'Oblivion Express',
        'mutators': {'Afraid of the Dark', 'Speed Freaks', 'Shortsighted'}
    },
    'Certain Demise': {
        'map': 'Chain of Ascension',
        'mutators': {'Avenger', 'Void Reanimators'}
    },
    'Cold Adaptation': {
        'map': 'Miner Evacuation',
        'mutators': {'Transmutation', 'Blizzard'}
    },
    'Cold is the Void': {
        'map': 'Oblivion Express',
        'mutators': {'Blizzard', 'Void Reanimators', 'Void Rifts'}
    },
    'Conflagration': {
        'map': 'Temple of the Past',
        'mutators': {'Walking Infested', 'Alien Incubation', 'Scorched Earth'}
    },
    'Coordinated Defense': {
        'map': 'The Vermillion Problem',
        'mutators': {'Polarity', 'Missile Command'}
    },
    'Cremation': {
        'map': 'Miner Evacuation',
        'mutators': {'Void Reanimators', 'Scorched Earth'}
    },
    'Dance Dance Evolution': {
        'map': 'Mist Opportunities',
        'mutators': {'Speed Freaks', 'Moment Of Silence', 'Transmutation'}
    },
    'Dark Ritual': {
        'map': 'Temple of the Past',
        'mutators': {'Power Overwhelming', 'Speed Freaks'}
    },
    'Dead Heat': {
        'map': 'The Vermillion Problem',
        'mutators': {'Fatal Attraction', 'Self Destruction', 'Walking Infested'}
    },
    'Death and Taxes': {
        'map': 'Dead of Night',
        'mutators': {'Micro Transactions', 'Black Death', 'Slim Pickings'}
    },
    'Death from Below': {
        'map': 'Miner Evacuation',
        'mutators': {'Minesweeper', 'Lava Burst', 'Scorched Earth'}
    },
    'Death is Fleeting': {
        'map': 'Dead of Night',
        'mutators': {'Just Die!', 'Void Reanimators'}
    },
    'Decade of Decadence': {
        'map': 'Rifts to Korhal',
        'mutators': {'Gift Exchange', 'Fireworks', 'Lucky Envelopes'}
    },
    'Delivery Guaranteed': {
        'map': 'Void Launch',
        'mutators': {'Just Die!', 'Barrier', 'Going Nuclear'}
    },
    'Die Together': {
        'map': 'Scythe of Amon',
        'mutators': {'Just Die!', 'Polarity'}
    },
    'Diplomatic Immunity': {
        'map': 'Oblivion Express',
        'mutators': {'Polarity', 'Barrier', 'Evasive Maneuvers'}
    },
    'Distant Threat': {
        'map': 'Dead of Night',
        'mutators': {'Purifier Beam', 'Long Range', 'Time Warp'}
    },
    'Dodge This': {
        'map': 'Scythe of Amon',
        'mutators': {'Orbital Strike', 'Going Nuclear', 'Darkness'}
    },
    'Doomsday Report': {
        'map': 'The Vermillion Problem',
        'mutators': {'Orbital Strike', 'Propagators', 'Going Nuclear'}
    },
    'Double Trouble': {
        'map': 'Void Launch',
        'mutators': {'Propagators', 'Kill Bots'}
    },
    'Encroaching Madness': {
        'map': 'Mist Opportunities',
        'mutators': {'Eminent Domain', 'Purifier Beam', 'Void Rifts'}
    },
    'Endless Infection': {
        'map': 'Void Launch',
        'mutators': {'Black Death', 'Walking Infested', 'Alien Incubation'}
    },
    'Endless Sparkles': {
        'map': 'Miner Evacuation',
        'mutators': {'Self Destruction', 'Alien Incubation'}
    },
    'Enhanced Defenses': {
        'map': 'Cradle of Death',
        'mutators': {'Barrier', 'Photon Overload', 'Going Nuclear'}
    },
    'Enter the Nexus': {
        'map': 'Cradle of Death',
        'mutators': {'Blizzard', 'Heroes from the Storm'}
    },
    'Equivalent Exchange': {
        'map': 'Void Thrashing',
        'mutators': {'Just Die!', 'Diffusion'}
    },
    'Experimental Artillery': {
        'map': 'Part and Parcel',
        'mutators': {'Laser Drill', 'Photon Overload', 'Long Range'}
    },
    'Explosive Hunt': {
        'map': 'Part and Parcel',
        'mutators': {'Slim Pickings', 'Minesweeper'}
    },
    'Explosive Results': {
        'map': 'Void Thrashing',
        'mutators': {'Mutually Assured Destruction', 'Self Destruction', 'Going Nuclear'}
    },
    'Fear and Lava': {
        'map': 'The Vermillion Problem',
        'mutators': {'Void Rifts', 'Fear'}
    },
    'Field of Screams': {
        'map': 'Mist Opportunities',
        'mutators': {'Polarity', 'Minesweeper'}
    },
    'Fire in the Hole': {
        'map': 'Miner Evacuation',
        'mutators': {'Boom Bots', 'Missile Command'}
    },
    'Firewall': {
        'map': 'Malwarfare',
        'mutators': {'Minesweeper', 'Lava Burst', 'Barrier'}
    },
    'First Strike': {
        'map': 'Chain of Ascension',
        'mutators': {'Laser Drill', 'Long Range', 'Shortsighted'}
    },
    'Flip My Base': {
        'map': 'Mist Opportunities',
        'mutators': {'Eminent Domain', 'Purifier Beam', 'Missile Command'}
    },
    'Flipping Out': {
        'map': 'Chain of Ascension',
        'mutators': {'Vertigo', 'Fear', 'Evasive Maneuvers'}
    },
    'Fowl Play': {
        'map': 'Oblivion Express',
        'mutators': {'Turkey Shoot', 'Sharing Is Caring'}
    },
    'Fright Night': {
        'map': 'Rifts to Korhal',
        'mutators': {'Afraid of the Dark', 'Trick or Treat'}
    },
    'Frostbite': {
        'map': 'Dead of Night',
        'mutators': {'Mag-nificent', 'Blizzard'}
    },
    'Futile Resistance': {
        'map': 'Lock & Load',
        'mutators': {'Propagators', 'Concussive Attacks', 'Temporal Field'}
    },
    'Get Out More': {
        'map': 'Dead of Night',
        'mutators': {'Mineral Shields', 'Eminent Domain', 'Self Destruction'}
    },
    'Getting Along': {
        'map': 'The Vermillion Problem',
        'mutators': {'Polarity', 'Sharing Is Caring'}
    },
    'Grave Danger': {
        'map': 'Temple of the Past',
        'mutators': {'Transmutation', 'Walking Infested', 'Void Reanimators'}
    },
    'Graveyard Shift': {
        'map': 'Dead of Night',
        'mutators': {'Purifier Beam', 'Afraid of the Dark'}
    },
    'Growing Threat': {
        'map': 'Mist Opportunities',
        'mutators': {'Transmutation', 'Mutually Assured Destruction', 'Alien Incubation'}
    },
    'Hard Target': {
        'map': 'Void Thrashing',
        'mutators': {'Polarity', 'Barrier', 'Hardened Will'}
    },
    'Hardware Malfunction': {
        'map': 'Malwarfare',
        'mutators': {'Laser Drill', 'Minesweeper', 'Kill Bots'}
    },
    'Hell Train': {
        'map': 'Oblivion Express',
        'mutators': {'Just Die!', 'Scorched Earth'}
    },
    'Hello My Old Friend': {
        'map': 'Scythe of Amon',
        'mutators': {'Moment Of Silence', 'Black Death', 'Darkness'}
    },
    'Hostile Takeover': {
        'map': 'Rifts to Korhal',
        'mutators': {'Eminent Domain', 'Laser Drill', 'Missile Command'}
    },
    'Hostile Territory': {
        'map': 'Dead of Night',
        'mutators': {'Photon Overload', 'Power Overwhelming', 'Barrier'}
    },
    "Hot 'n' Cold": {
        'map': 'Void Launch',
        'mutators': {'Blizzard', 'Lava Burst', 'Scorched Earth'}
    },
    'Chain Explosions': {
        'map': 'Chain of Ascension',
        'mutators': {'Walking Infested', 'Lava Burst'}
    },
    'Charnel House': {
        'map': 'Miner Evacuation',
        'mutators': {'Photon Overload', 'Black Death', 'Darkness'}
    },
    'Choices Choices': {
        'map': 'Temple of the Past',
        'mutators': {'Mutually Assured Destruction', 'Inspiration', 'Hardened Will'}
    },
    'In the Name of Love': {
        'map': 'Cradle of Death',
        'mutators': {'Purifier Beam', 'Concussive Attacks', 'Time Warp'}
    },
    'Infection Detected': {
        'map': 'Malwarfare',
        'mutators': {'Self Destruction', 'Alien Incubation', 'Outbreak'}
    },
    'Inner Power': {
        'map': 'Temple of the Past',
        'mutators': {'Power Overwhelming', 'Alien Incubation'}
    },
    'Inordinate Response': {
        'map': 'Scythe of Amon',
        'mutators': {'Power Overwhelming', 'Avenger'}
    },
    'Instant Karma': {
        'map': 'Chain of Ascension',
        'mutators': {'Double-Edged', 'Mutually Assured Destruction', 'Self Destruction'}
    },
    'Kill Bot Wars': {
        'map': 'Mist Opportunities',
        'mutators': {'Moment Of Silence', 'Kill Bots'}
    },
    'Knock Knock': {
        'map': 'Dead of Night',
        'mutators': {'Avenger', 'Propagators'}
    },
    'Like Swatting Insects': {
        'map': 'Cradle of Death',
        'mutators': {'Missile Command', 'Alien Incubation', 'Outbreak'}
    },
    'Locked and Loaded': {
        'map': 'Lock & Load',
        'mutators': {'Mineral Shields', 'Kill Bots', 'Temporal Field'}
    },
    'Magnetic Attraction': {
        'map': 'Void Thrashing',
        'mutators': {'Mag-nificent', 'Fatal Attraction', 'We Move Unseen'}
    },
    'Mass Manufacturing': {
        'map': 'Part and Parcel',
        'mutators': {'Propagators', 'Void Rifts'}
    },
    'Masters of Midnight': {
        'map': 'Part and Parcel',
        'mutators': {'Shortsighted', 'Life Leech', 'Fear'}
    },
    'Media Blackout': {
        'map': 'The Vermillion Problem',
        'mutators': {'We Move Unseen', 'Missile Command', 'Darkness'}
    },
    'Medieval Times': {
        'map': 'Scythe of Amon',
        'mutators': {'Transmutation', 'Black Death'}
    },
    'Memorable Boss': {
        'map': 'Void Launch',
        'mutators': {'Moment Of Silence', 'Heroes from the Storm'}
    },
    'Miner Concerns': {
        'map': 'Rifts to Korhal',
        'mutators': {'Mag-nificent', 'Slim Pickings', 'Fear'}
    },
    'Moths to the Flame': {
        'map': 'Rifts to Korhal',
        'mutators': {'Fatal Attraction', 'Purifier Beam', 'Alien Incubation'}
    },
    'Moving Fees': {
        'map': 'Cradle of Death',
        'mutators': {'Micro Transactions', 'Scorched Earth'}
    },
    'Multitasking Trainer': {
        'map': 'Malwarfare',
        'mutators': {'Micro Transactions', 'Void Rifts'}
    },
    'My Bots!': {
        'map': 'Mist Opportunities',
        'mutators': {'Boom Bots', 'Kill Bots'}
    },
    'Negative Reinforcement': {
        'map': 'Part and Parcel',
        'mutators': {'Fatal Attraction', 'Avenger'}
    },
    'Never Say Die': {
        'map': 'Mist Opportunities',
        'mutators': {'Just Die!', 'Life Leech', 'Barrier'}
    },
    'Night Drive': {
        'map': 'Cradle of Death',
        'mutators': {'Afraid of the Dark', 'Mag-nificent'}
    },
    'No Money, More Problems': {
        'map': 'The Vermillion Problem',
        'mutators': {'Slim Pickings', 'Self Destruction', 'Twister'}
    },
    'Nuclear Family': {
        'map': 'Chain of Ascension',
        'mutators': {'Mutually Assured Destruction', 'Hardened Will', 'Outbreak'}
    },
    'Of Mines and Miners': {
        'map': 'Miner Evacuation',
        'mutators': {'Mag-nificent', 'Minesweeper', 'Missile Command'}
    },
    'Of One Mind': {
        'map': 'Rifts to Korhal',
        'mutators': {'Boom Bots', 'Polarity', 'Sharing Is Caring'}
    },
    'One for All': {
        'map': 'Temple of the Past',
        'mutators': {'Transmutation', 'Inspiration', 'Hardened Will'}
    },
    'Onslaught': {
        'map': 'Dead of Night',
        'mutators': {'Aggressive Deployment', 'Void Reanimators', 'Outbreak'}
    },
    'Operation Cooperation': {
        'map': 'Lock & Load',
        'mutators': {'Polarity', 'Propagators'}
    },
    'Opportunities Unleashed': {
        'map': 'Mist Opportunities',
        'mutators': {'Power Overwhelming', 'Speed Freaks', 'Barrier'}
    },
    'Out of Order': {
        'map': 'The Vermillion Problem',
        'mutators': {'Micro Transactions', 'Darkness', 'Time Warp'}
    },
    'Out of Sight': {
        'map': 'Miner Evacuation',
        'mutators': {'Purifier Beam', 'We Move Unseen'}
    },
    'Overclocked': {
        'map': 'Malwarfare',
        'mutators': {'Speed Freaks', 'Photon Overload', 'Avenger'}
    },
    'Perfect Storm': {
        'map': 'Chain of Ascension',
        'mutators': {'Blizzard', 'Twister', 'Shortsighted'}
    },
    'Portal Power': {
        'map': 'Void Thrashing',
        'mutators': {'Power Overwhelming', 'Void Rifts'}
    },
    'Power Trip': {
        'map': 'The Vermillion Problem',
        'mutators': {'Power Overwhelming', 'Long Range', 'Photon Overload'}
    },
    'Price of Progress': {
        'map': 'Malwarfare',
        'mutators': {'Micro Transactions', 'Kill Bots'}
    },
    'Quick Killers': {
        'map': 'Temple of the Past',
        'mutators': {'Kill Bots', 'Inspiration', 'Speed Freaks'}
    },
    'Radiation Zone': {
        'map': 'Rifts to Korhal',
        'mutators': {'Black Death', 'Going Nuclear', 'Outbreak'}
    },
    'Railroad Switch': {
        'map': 'Oblivion Express',
        'mutators': {'Just Die!', 'Polarity'}
    },
    'Resilient Rifts': {
        'map': 'Rifts to Korhal',
        'mutators': {'Just Die!', 'Void Rifts'}
    },
    'Rest in Peace': {
        'map': 'Void Thrashing',
        'mutators': {'Moment Of Silence', 'Propagators'}
    },
    'Retribution': {
        'map': 'Mist Opportunities',
        'mutators': {'Double-Edged', 'Void Rifts'}
    },
    'Rise from Ashes': {
        'map': 'Scythe of Amon',
        'mutators': {'Void Reanimators', 'Lava Burst', 'Self Destruction'}
    },
    'Robotic Revival': {
        'map': 'Part and Parcel',
        'mutators': {'Laser Drill', 'Just Die!', 'Fear'}
    },
    'Rubber and Glue': {
        'map': 'Void Launch',
        'mutators': {'Double-Edged', 'Temporal Field', 'Diffusion'}
    },
    'Rumble in the Jungle': {
        'map': 'Mist Opportunities',
        'mutators': {'Aggressive Deployment', 'Temporal Field', 'We Move Unseen'}
    },
    'Safety Violation': {
        'map': 'Miner Evacuation',
        'mutators': {'Mag-nificent', 'Laser Drill', 'Self Destruction'}
    },
    'Scary Scavengers': {
        'map': 'Dead of Night',
        'mutators': {'Slim Pickings', 'Outbreak'}
    },
    'Season of Giving': {
        'map': 'Cradle of Death',
        'mutators': {'Gift Exchange', 'Blizzard', 'Naughty List'}
    },
    'Secret Storm': {
        'map': 'Lock & Load',
        'mutators': {'Aggressive Deployment', 'Twister', 'We Move Unseen'}
    },
    'Shared Pain': {
        'map': 'Part and Parcel',
        'mutators': {'Fatal Attraction', 'Diffusion'}
    },
    'Shields Up!': {
        'map': 'Void Launch',
        'mutators': {'Diffusion', 'Mineral Shields', 'Shortsighted'}
    },
    'Shining Bright': {
        'map': 'Mist Opportunities',
        'mutators': {'Laser Drill', 'Purifier Beam', 'Concussive Attacks'}
    },
    'Shir Chaos': {
        'map': 'Chain of Ascension',
        'mutators': {'Speed Freaks', 'Just Die!', 'Outbreak'}
    },
    'Sick Micro': {
        'map': 'Mist Opportunities',
        'mutators': {'Micro Transactions', 'Black Death'}
    },
    'Slow and Steady': {
        'map': 'Mist Opportunities',
        'mutators': {'Speed Freaks', 'Concussive Attacks', 'Time Warp'}
    },
    'Spear of Your Doom': {
        'map': 'Lock & Load',
        'mutators': {'Purifier Beam', 'Orbital Strike', 'Temporal Field'}
    },
    'Special Delivery': {
        'map': 'Void Launch',
        'mutators': {'Aggressive Deployment', 'Self Destruction', 'Alien Incubation'}
    },
    'Specter of Death': {
        'map': 'Part and Parcel',
        'mutators': {'We Move Unseen', 'Void Reanimators'}
    },
    'Survival of the Fittest': {
        'map': 'Void Thrashing',
        'mutators': {'Transmutation', 'Barrier'}
    },
    'Tax Day': {
        'map': 'Void Launch',
        'mutators': {'Micro Transactions', 'Fear'}
    },
    'Temple of Pain': {
        'map': 'Temple of the Past',
        'mutators': {'Mineral Shields', 'Barrier', 'Avenger'}
    },
    'Temple of Rebirth': {
        'map': 'Temple of the Past',
        'mutators': {'Just Die!', 'Life Leech', 'Barrier'}
    },
    'Temple of Terror': {
        'map': 'Temple of the Past',
        'mutators': {'Afraid of the Dark', 'Fear', 'Alien Incubation'}
    },
    'The Ascended': {
        'map': 'Chain of Ascension',
        'mutators': {'Transmutation', 'Inspiration'}
    },
    'The Injustice League': {
        'map': 'Rifts to Korhal',
        'mutators': {'Heroes from the Storm', 'Inspiration', 'Hardened Will'}
    },
    'The League of Vermillains': {
        'map': 'The Vermillion Problem',
        'mutators': {'Heroes from the Storm', 'Evasive Maneuvers'}
    },
    'The Longest Night': {
        'map': 'Dead of Night',
        'mutators': {'Long Range', 'Just Die!', 'Photon Overload'}
    },
    'The Quick and the Dead': {
        'map': 'Dead of Night',
        'mutators': {'Speed Freaks', 'Black Death'}
    },
    'The Quick and the Undead': {
        'map': 'Scythe of Amon',
        'mutators': {'Speed Freaks', 'Void Reanimators'}
    },
    'The Ultimate Price': {
        'map': 'Lock & Load',
        'mutators': {'Mineral Shields', 'Missile Command', 'Micro Transactions'}
    },
    'Think Fast': {
        'map': 'Rifts to Korhal',
        'mutators': {'Speed Freaks', 'Propagators'}
    },
    'Thunder Dome': {
        'map': 'Lock & Load',
        'mutators': {'Mag-nificent', 'Heroes from the Storm'}
    },
    'Time Lock': {
        'map': 'Lock & Load',
        'mutators': {'Mag-nificent', 'Speed Freaks', 'Time Warp'}
    },
    'Timely Reinforcements': {
        'map': 'Miner Evacuation',
        'mutators': {'Void Rifts', 'Temporal Field'}
    },
    'Together Forever': {
        'map': 'Chain of Ascension',
        'mutators': {'Just Die!', 'Polarity'}
    },
    'Train of Pain': {
        'map': 'Oblivion Express',
        'mutators': {'Double-Edged', 'Going Nuclear', 'Mutually Assured Destruction'}
    },
    'Train of the Dead': {
        'map': 'Oblivion Express',
        'mutators': {'Outbreak', 'Walking Infested', 'Darkness'}
    },
    'Triple Threat': {
        'map': 'Void Launch',
        'mutators': {'Laser Drill', 'Orbital Strike', 'Outbreak'}
    },
    'Ulnar New Year': {
        'map': 'Lock & Load',
        'mutators': {'Fireworks', 'Lucky Envelopes'}
    },
    'Undermined': {
        'map': 'Rifts to Korhal',
        'mutators': {'Minesweeper', 'Void Rifts'}
    },
    'Unstable Environment': {
        'map': 'Scythe of Amon',
        'mutators': {'Lava Burst', 'Twister', 'Time Warp'}
    },
    'Urban Warfare': {
        'map': 'Rifts to Korhal',
        'mutators': {'We Move Unseen', 'Minesweeper', 'Photon Overload'}
    },
    'Violent Night': {
        'map': 'Void Launch',
        'mutators': {'Gift Exchange', 'Naughty List'}
    },
    'War is Hell': {
        'map': 'Void Thrashing',
        'mutators': {'Lava Burst', 'Evasive Maneuvers', 'Scorched Earth'}
    },
    'Warp Zone': {
        'map': 'Lock & Load',
        'mutators': {'Temporal Field', 'Twister', 'Time Warp'}
    },
    'Watch the Skies': {
        'map': 'Void Launch',
        'mutators': {'Aggressive Deployment', 'Missile Command', 'Orbital Strike'}
    },
    'Well Trained': {
        'map': 'Oblivion Express',
        'mutators': {'Aggressive Deployment', 'Inspiration', 'Avenger'}
    },
    'What Goes Around': {
        'map': 'Scythe of Amon',
        'mutators': {'Double-Edged', 'Mutually Assured Destruction'}
    },
    'What We Do in the Shadows': {
        'map': 'Void Thrashing',
        'mutators': {'We Move Unseen', 'Darkness', 'Shortsighted'}
    },
    'Wheel of Misfortune (Thrashers)': {
        'map': 'Void Thrashing',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Misfortune (Lava)': {
        'map': 'The Vermillion Problem',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Misfortune (Train)': {
        'map': 'Oblivion Express',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Misfortune (Launch)': {
        'map': 'Void Launch',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Misfortune (Locks)': {
        'map': 'Lock & Load',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Stupidity (Cradle)': {
        'map': 'Cradle of Death',
        'mutators': {'Chaos Studios'}
    },
    'Wheel of Stupidity (Evac)': {
        'map': 'Miner Evacuation',
        'mutators': {'Chaos Studios'}
    },
    'Whiteout': {
        'map': 'Void Launch',
        'mutators': {'Blizzard', 'Slim Pickings'}
    },
    'World on Fire': {
        'map': 'The Vermillion Problem',
        'mutators': {'Purifier Beam', 'Missile Command', 'Going Nuclear'}
    },
    'Worn Out Welcome': {
        'map': 'Temple of the Past',
        'mutators': {'Just Die!', 'Inspiration', 'Long Range'}
    }
}
