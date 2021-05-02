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
        'ZealotAiur': (100, 0)
    },
    'Dehaka': {
        'DehakaGuardian': (0, 100, 150, 150),
        'DehakaHydraliskLevel2': (100, 50),
        'DehakaMutaliskLevel3FightMorph': (0, 25, 200, 125),
        'DehakaMutaliskReviveEgg': (0,0,200,125),
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
        'HHMercStarportUpgraded': (150, 0),
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
        'ImmortalAiur': (325, 130),
        'Interceptor': (0, 0),
        'KhaydarinMonolith': (300, 100),
        'PhoenixPurifier': (195, 130),
        'PhotonCannon': (150, 0),
        'SentryPurifier': (65, 130),
        'ShieldBattery': (100, 0),
        'Observer': (25, 75),
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
        'ZerglingStetmann': (25, 0)
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
        'VoidRayShakuras': (250, 150),
        'ZealotShakuras': (100, 0)
    },
    'Zagara': {
        'Baneling': (25, 25, 50, 25),
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