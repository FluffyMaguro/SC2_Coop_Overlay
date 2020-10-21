from SCOFunctions.SC2Dictionaries import Mutators

# Create mutator list by removing my mutators and those that are not in custom mutations
mutators = list(Mutators.keys())[:-19]
for item in ('Nap Time',
             'Stone Zealots',
             'Chaos Studios',
             'Undying Evil',
             'Afraid of the Dark',
             'Trick or Treat',
             'Turkey Shoot',
             'Sharing Is Caring',
             'Gift Exchange',
             'Naughty List',
             'Extreme Caution',
             'Insubordination',
             'Fireworks',
             'Lucky Envelopes',
             'Sluggishness'):
    mutators.remove(item)


def get_mutator(button, panel):
    """ Returns mutator based on button (41-83) and currently selected panel (1-4) """
    button = (button - 41)//3 + (panel-1)*15
    return mutators[button]


def identify_mutators(events):
    """ Identify mutators based on dirty STriggerDialogControl events
    This work only in custom mutations, and random mutator isn't decided."""

    # Get a list of dialog items used
    actions = list()
    for event in events:
        if event['_gameloop'] > 0 and event['_event'] == 'NNet.Game.STriggerDialogControlEvent' and event['_userid']['m_userId'] == 0:
            actions.append(event['m_controlId'])

        # Break on game starting
        elif event['_event'] == 'NNet.Game.STriggerCutsceneBookmarkFiredEvent':
           break

    mutators = list()
    panel = 1 # Currently visible mutator panel
    for action in actions:
        # Mutator clicked
        if 41 <= action <= 83:
            mutators.append(get_mutator(action, panel))

        # Panel Changed
        if action == 123 and panel > 1:
            panel -= 1
        if action == 124 and panel < 4:
            panel += 1

        # Mutator removed
        if 88 <= action <= 106:
            del mutators[(action-88)//2]

    return mutators