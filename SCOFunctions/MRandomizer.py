import random

from SCOFunctions.SC2Dictionaries import amon_player_ids


def randomize(commander_dict, mastery_all_in=True):
    """
    Returns a random commander and prestige from `commander_dict`.
    Random mastery, map and enemy race are returned as well.
    If `mastery_all_in`== True then all mastery points go into one choice.
    Map is always chosen from all maps.
    """

    # Delete commanders with no prestige options
    for commander in list(commander_dict.keys()):
        if len(commander_dict[commander]) == 0:
            del commander_dict[commander]

    # Randomly choose commander, prestige, map and race
    commander = random.choice(list(commander_dict.keys()))
    prestige = random.choice(list(commander_dict[commander]))
    mmap = random.choice(list(amon_player_ids.keys()))
    race = random.choice(['Terran','Protoss','Zerg'])

    # Mastery is different for the two cases
    mastery = list()
    if mastery_all_in:
        for i in range(6):
            if i % 2 == 0:
                chosen = random.randint(0, 1)
            chosen += i % 2
            if chosen % 2:
                mastery.append(30)
            else:
                mastery.append(0)
    else:
        for i in range(6):
            if i % 2 == 0:
                chosen = random.randint(0, 30)
                mastery.append(chosen)
            else:
                mastery.append(30 - chosen)

    return (commander, prestige, mastery, mmap, race)