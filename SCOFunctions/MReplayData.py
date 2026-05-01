from typing import NamedTuple

"""APPVERSION of the last revision to `replay_data`

This can be used to invalidate the pickled cache in `MassReplayAnalysis.py`.
"""
REPLAY_DATA_VERSION = 248

class replay_data(NamedTuple):
    """ Data structure for storing information for replays in a more memory efficient way. 
    Although this data isn't the memory hog for this app."""
    accurate_length: float
    brutal_plus: int
    build: dict
    date: str
    difficulty: tuple
    enemy_race: str
    ext_difficulty: str
    extension: bool
    file: str
    form_alength: str
    length: int
    map_name: str
    messages: tuple
    mutators: tuple
    players: tuple
    region: str
    result: str
    version: int
    # NOTE: version cannot be defaulted or else pickle will reconstruct a replay_data that does
    # not have the version field with the new default. In this case MassReplayAnalysis will not
    # detect the cache is old.

    amon_units: dict = None
    bonus: tuple = None
    comp: str = None
    full_analysis: bool = False
    hash: str = None
    player_stats: list = None
    weekly: bool = False