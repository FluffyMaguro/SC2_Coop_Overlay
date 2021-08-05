from typing import NamedTuple


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
    
    weekly: str = None
    amon_units: dict = None
    bonus: tuple = None
    comp: str = None
    full_analysis: bool = False
    hash: str = None
    player_stats: list = None