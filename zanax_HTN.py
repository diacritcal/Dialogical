# -*- coding: utf-8 -*-

"""
Support for hierarchical task planner dialog management 
Author: Tom Dean <tld@google.com> Date: August 17, 2014
"""

# make canopy load external modules.
execfile('/Users/tld/Drive/code/python/zinn/pathfix.py')

from random import randint

import sys

from zanax_HOP import *

from zanax_NLG import expand, get_payload, instantiate, join

from zanax_NLU import assign, complete, interact, interject, \
     lookup, match, patience, platonic, rewarded, history, similarity

# set to True to run experiments:
run_dialog_unit_test = True

# initialize all state variables:
def initialize_starting_state(flag=False):
    start = State('start')
    start.var = {}
    # initialice all of the state variables:
    start.var['profile'] = {'name':None, 'email':None, 'artists':[], 'albums':[], 'genres':[]} # user profile fields
    start.var['premise'] = {'artist':None, 'album':None, 'genre':None, 'play':None, 'song':None} # inferred selections
    start.var['confirm'] = {'artist':None, 'album':None, 'genre':None, 'play':None, 'song':None} # confirmation status
    start.var['scratch'] = {'track':None, 'played':[], 'positive':[], 'negative':[], 'neutral':[]} # miscellaneous stuff
    # reset the user input history to empty:
    history(-1)
    if flag:
         print_state(start)
    return start

# instantiate the starting state.
start = initialize_starting_state()

# simulate loading a user profile.
start.var['profile']['genres'].append('classical')

# ********************************************************************* #

# GREET_INTRO:

#    (if turn is first)
# Z:    I'm Zinn, what's your name?
#       (if turn is second)
# Z:       Let's try again. Your name?

# ********************************************************************* #

def greet_intro_m(state,turn):
    if state.user['name'] == None:
        if turn == 'first':
            input = interact("I'm Zinn. What's your name?")
        else:
            input = interact("Let's try again. Your name?")
        names = lookup(input,'name')
        if names:
            input = interact('Hi {}. Did I get that right?'.format(names[0]))
            if lookup(input,'negative'):
                return [('confirm', 'negative', names, 'user', 'name')]
            elif lookup(input,'positive'):
                return [('confirm', 'positive', names, 'user', 'name')]
            else:
                interject("Not sure, but I'll take that as a 'no'.")
                return [('recover', 'greet')]
        elif turn == 'first':
            return [('greet', 'second')]
        else:
            return False
    else:
        return False

# ********************************************************************* #

# GREET_HELLO:

# ********************************************************************* #

def greet_hello_m(state,ignore):
    name = state.profile['name']
    genre = state.profile['genre']
    if name:
        if genre:
            input = interact('Hi {}. How about some {}?'.format(name,genre))
        else:
            input = interact('Hi {}. Interest in some music?'.format(name))
        if lookup(input,'hello') or lookup(input,'positive'):
            return [('play', 'start')]
        else:
            interject("Didn't get that. I'm kinda dense right out of the box.")
            interject("You might want to use simple words and short sentences.")
            return []
    else:
        return False

declare_methods('greet', greet_hello_m, greet_intro_m)

# ********************************************************************* #

# SELECT_GENRE:

# ********************************************************************* #

# Here's an example of a selection task. note that some branches result in
# commitments. these should be recorded so later we can notice if the user
# doesn't like a song from a genre we previously thought to be a favorite.
# There are opportunities for both misunderstanding and non-understanding:
# non-understandings we have to deal with immediately; misunderstandings
# could easily slip by unheeded and have to be dealt with at a later time.

def select_genre_m(state, type, turn):
    if type == 'genre':
        if turn == 'first':
            input = interact(
                ['What sort of music do you listen to?',
                 'Is there a particular genre you like?',
                 'What is your favorite type of music?',
                 'Do you have a favorite type of music?'][randint(0,3)])
        else:
            input = interact('How about one of: blues, rock, pop or jazz?')
        # whether 'first' or 'second' we are expecting mention of a genre.
        genres = lookup(input,'genre')
        if genres and genres[0] == 'jazz':
            interject('Jazz is my favorite next to classical.')
        elif genres and genres[0] == 'classical':
            interject('I love classical, especially baroque.')
        elif genres and genres[0] == 'blues':
            interject('I like delta and Chicago blues styles.')
        elif genres and genres[0] == 'rock':
            interject('I occasionally listen to some hard rock.')
        elif genres and genres[0] == 'pop':
            interject("Not my favorite, but I'm open to learn.")
        else:
            # this is a non-understanding and so let's try to resolve it.
            interject("I'm afraid I didn't understand you.")
            return [('resolve', input, 'select', 'genre')]
        # we haven't committed to an interpretation; check for sentiment.
        if lookup(input,'negative'):
            input = interact("I think you said that you don't like {}?".format(genres[0]))
            if lookup(input,'positive'):
                # need an additional field in the user profile to record this:
                interject("I'll take that as a 'yes' and not play any {}.".format(genres[0]))
                if turn == 'second':
                    # no genre, but it's time to move on and not annoy the user.
                    return [('select', 'artist', 'first')]
                else:
                    # try again if this is the first attempt at selecting a genre.
                    return [('select', 'genre', 'second')]
            elif lookup(input,'negative'):
                # signal is ambiguous since a 'no' could affirm or deny the probe.
                input = interact("Were you (1) confirming or (2) denying your dislike?")
                if lookup(input,'number') == 0:
                    interject("Sounds good. I won't be playing any {}.".format(genres[0]))
                    return [('select', 'genre', 'second')]
                elif lookup(input,'number') == 1:
                    # an implicit probe to confirm the interpretation of genre input.
                    interject("Is there a particular {} artist you like?".format(genres[0]))
                    return [('confirm', 'genre'), ('select', 'artist', 'first')]
                else:
                    # we gave it a good shot but the user is not coooerating with us.
                    interject("I didn't understand you. Let's try another tack.")
                    return [('recover', 'genre')]
            else:
                # getting a little tedious; it's time for some more draconian steps.
                return [('recover', 'genre')]
        else:
            # if we ended here, we can be pretty sure the user likes selected genre.
            interject("Great. Let's talk about some {} artists.".format(genres[0]))
            return [('select', 'artist', 'first'), ('commit','premise',{'genre':genres[0]})]
    else:
        # wasn't a 'genre' selection task and so signal planner to try another method.
        return False

# ********************************************************************* #

# SELECT_[TBD]_M:

# ********************************************************************* #

def select_artist_m(state, type, turn='first'):
    if type == 'artist':
        return []
    else:
        return False

def select_album_m(state, type, turn='first'):
    if type == 'album':
        return []
    else:
        return False

def select_song_m(state, type, turn='first'):
    if type == 'song':
        return []
    else:
        return False

declare_methods('select', select_artist_m, select_album_m, select_genre_m, select_song_m)


# ********************************************************************* #

# PLAY_START: assumes GREET_INTRO or GREET_HELLO

# Z: OPEN, ASK_WHAT_TO_PLAY
#    (if no input after 4 secs)
# Z:    I_CAN_PLAY
#       (if no input after 8 secs)
# Z:       I_CAN_SUGGEST
#          (if no input after 12 secs)
# Z:          SORRY_GOODBYE

# ********************************************************************* #

def play_start_m(state,type):
    """
    Initial 'play' task invoked by [('play','start')]
    Demonstrates the use of timers in selecting music.
    """
    if type == 'start':
        # zinn gives the user increasingly more time.
        input = False
        if patience(expand('ASK_WHAT_PLAY'),4,False):
            input = rewarded()
        else:
            if patience(expand('I_CAN_PLAY'),8,True):
                input = rewarded()
            else:
                if patience(expand('I_CAN_SUGGEST'),12,True):
                    input = rewarded()
        if input:
            matches = match(input)
            if matches['artist'] or matches['genre']:
                # user intent implied by music mention.
                return [('commit', 'premise', matches),
                        ('confirm', 'play'),
                        ('confirm', 'music'),
                        ('perform', 'music')]
            elif matches['play']:
                # explicit intent but no music mention.
                return [('commit', 'premise', matches),
                        ('confirm', 'play'),
                        ('select', 'music'),
                        ('perform', 'music')]
            else:
                # unsure the user wants to hear music at all.
                return [('recover', 'music')]
        else:
            interject(expand('SORRY_GOODBYE'),True)
            # if no user response, terminate session.
            return False
    else:
        # if 'play' type isn't 'start', backtrack.
        return False

# ********************************************************************* #

declare_methods('play', play_start_m)

# ********************************************************************* #

def commit(state, partition, matches):
    """
    This operator instantiates the notion of committing 
    (assigning) a state variable in partitioned memory.
    """
    bindings = state.var[partition]
    for key in matches:
        if key in bindings and matches[key]:
            if isinstance(matches[key],list):
                # ignore all but first match.
                bindings[key] = matches[key][0]
            else:
                # otherwise assign the value.
                bindings[key] = matches[key]
    state.var[partition] = bindings
    return state

declare_operators(commit)

# ********************************************************************* #

# CONFIRM_PLAY_AND_MUSIC: assumes PLAY_START or PLAY_CONTINUE

# U: $play $artist|genre|track (single or combo of the $artist|genre|track)
# Z: (if artist)
# Z:    ACK HERES <song>
#    (else)
# Z:    ACK HERES <song> BY <artist>

# ********************************************************************* #

# CONFIRM_ONLY_PLAY: assumes PLAY_START or PLAY_CONTINUE

# U: $play: i.e. could be no $artist|genre|track phrase is matched
# U: e.g. "Please play me monkeys jazz skinny sinatra"
#    (if rest of tokens < 5 AND contiguous) 
# Z: WHEN_YOU_SAY <rest of tokens> ASK_IS_MUSIC
#    (if $yes) 
# Z:    ACK ILL_REMEMBER
#    (if $no)
# Z:    ASK_WHAT_TO_PLAY
#    (else) 
# Z:    RECOVER_SLOTS

# ********************************************************************* #

def confirm_play_m(state, type):
    if type == 'play':
        if state.var['confirm']['play']:
            # it's already confirmed!
            interject(expand('I_GOT you want me to play some music.'))
            return []
        elif state.var['premise']['play']:
            # it needs to be confirmed.
            bindings = {'input':history(), 'music':got_music(state)}
            if similarity(bindings['input'],
                          instantiate('play $music', bindings)) > 0.65:
                utterance = 'I_GOT that you want me to play $music. correct?'
            else:
                utterance = 'WHEN_YOU_SAY "$input" IS_WAY_SAY "play $music"?'
            # ask for confirmation.
            input = interact(expand(utterance,bindings))
            if lookup(input,'positive'):
                # yay, play is confirmed.
                interject(expand('Thanks. I_GOT it now.'))
                return [('commit', 'confirm', {'play':True})]
            else:
                # uh oh, gonna be complicated.
                return [('recover', 'play')]
        else:
            # this is totally unexpected!
            return [('recover', 'play')]
    else:
        return False

# extract premised artist or genre from state or return 'music'.
def got_music(state):
    if state.var['premise']['artist']:
        return state.var['premise']['artist']
    elif state.var['premise']['genre']:
        return state.var['premise']['genre']
    else:
        return 'music'

# ********************************************************************* #

# CONFIRM_ONLY_MUSIC: assumes PLAY_START or PLAY_CONTINUE

# U: $artist|genre|track: i.e. could be no $play phrase is matched
#    (if rest of tokens < 5 AND contiguous)  e.g. "Spin me up some Police"
# Z:    ACK I_GOT <$artist|genre|track>  (if multiple connect with "AND").
# Z:    WHEN_YOU_SAY <rest of tokens> IS_WAY_SAY_PLAY
#    (else)
#       (if artist)
# Z:       ACK HERES <song>
#       (else)
# Z:       ACK HERES <song> by <artist>

# ********************************************************************* #

def confirm_music_m(state, type):
    if type == 'music':
        artist = state.var['confirm']['artist'] 
        genre  = state.var['confirm']['genre']
        if artist or genre: 
            # it's already confirmed!
            if artist:
                interject(expand('NYI'))
                return []
            elif genre: 
                interject(expand('NYI'))
                return []
        artist = state.var['premise']['artist'] 
        genre  = state.var['premise']['genre']
        if artist or genre: 
            # it needs to be confirmed.
            if artist:
                bindings = {'this':history(), 'artist':artist}
                utterance = 'NYI'
            else:
                bindings = {'this':history(), 'artist':genre}
                utterance = 'NYI'                
            # request for confirmation.
            input = interact(expand(utterance,bindings))
            if lookup(input,'positive'):
                # yay, play is confirmed.
                if artist:
                    interject(expand('NYI'))
                    return []
                else:
                    interject(expand('NYI'))
                    return []
            else:
                return [('recover', 'music')]
        else:
            return [('recover', 'music')]
    else:
        return False

# ********************************************************************* #

# CONFIRM_SELECT_NEGATIVE:

# ********************************************************************* #

def confirm_select_negative_m(state, type, options=None, field=None, key=None):
    if type == 'negative' and options and field and key:
        if len(options) > 1:
            input = interact('Is it one of these: {}?'.format(options))
            index = lookup(input,'number')
            if index and index < len(options):
                interject('Thanks {}. Hopefully I got it this time.'.format(options[index]))
                return [('commit', 'profile', {'name':options[index]})]
            else:
                # we're here because options[0] didn't work, try options[1].
                input = interact('One more guess. Is it {}?'.format(options[1]))
                if lookup(input,'positive'):
                    interject("Excellent! I'll go with that.")
                    return [('commit', 'profile', {'name':options[1]})]
                else:
                    interject(["Damn! I thought I had it.",
                               "I'll take that as a 'no'.",
                               "Ah well, maybe next time.",
                               "I'm out of suggestions."][randint(0,3)])
                    return []
        else:
            # we have either zero options or only one incorrect option.
            return [('recover', 'greet')]
    else:
        return False
        
# ********************************************************************* #

# CONFIRM_SELECT_POSITIVE:

# ********************************************************************* #
def confirm_select_positive_m(state, type, options=None, field=None, key=None):
    if type == 'positive':
        interject("Great! Thanks for being patient with me.")
        return [('commmit', 'profile', {'name':options[0]})]
    else:
        return False

declare_methods('confirm', confirm_play_m, confirm_music_m, \
                           confirm_select_positive_m, confirm_select_negative_m)

# ********************************************************************* #

# RECOVER_SLOTS: assumes failed CONFIRM tasks

# Z: FIRST CORRECTION ATTEMPT
#      (if specific slot error prompt:)
#         play specific error prompt: e.g. "I didn't get the music part."
#      (else)
#         play partial error prompt: e.g. "I didn't get all of what you said.
#    followed by general prompt: e.g. What would you like to hear?"
# Z: SECOND CORRECTION ATTEMPT
#    play AGAIN-style general error prompt: e.g. "I didn't get that either."
#    play REPHRASE: e.g., "Could you say that a different way?"
# Z: THIRD CORRECTION ATTEMPT
#       ADMIT NON_UNDERSTANDING

# ********************************************************************* #

def recover_slots_m(state, slots, caller=None):
    # check for caller-callee specific payload language.
    if not caller:
        pay = None
    else:
        pay = get_payload(caller,'recover')
    # normalize and expand aliases in the list of slots.
    slots = complete(slots)
    # check to see if the slots have already been filled. 
    unfilled = [slot for slot in slots if not state.var['premise'][slot]]
    if not unfilled:
        return []
    else:
        # try twice to recover and then admit failure.
        if pay and pay.peek('leader'):
            # if there's a domain-specific leader use it.
            interject(pay.load('leader'))
        else:
            # otherwise display a partial-error leader.
            interject("I didn't get all of what you said.")
        # last opportunity for customizing this task.
        if pay and pay.peek('prompt'):
            # if there's a domain-specific prompt use it.
            input = interact(pay.load('prompt'))
        else:
            input = interact('Give me one {}.'.format(join(unfilled,'or')))
        matches = match(input)
        filled = [slot for slot in unfilled if matches[slot]]
        if filled:
            interject('Thanks. I got your {}.'.format(join(filled,'and')))
            return [('commit', 'confirm', matches)]
        else:
            # try another general error prompt noting earlier.
            interject("I didn't get that either.")
            input = interact('Could you say that a different way?')
            matches = match(input)
            filled = [slot for slot in unfilled if matches[slot]]
            if filled:
                interject('I got your {} that time.'.format(join(filled)))
                return [('commit', 'confirm', matches)]
            else:
                interject("Sorry. I'm totally confused.")
                return False

# ********************************************************************* #

# RECOVER_[TBD]_M:

# ********************************************************************* #

def recover_greet_m(state, type, caller=None):
    if type == 'greet':
        return []
    else:
        return False

declare_methods('recover', recover_slots_m, recover_greet_m)

# ********************************************************************* #

# Examples:

if run_dialog_unit_test:
    print('\nPrint updated state resulting from a commit action:')
    print_state(commit(initialize_starting_state(),
                       'premise', match('play me some sting')))
if run_dialog_unit_test:    
    print('\nDemonstrate play start patiently waiting for input:')
    pyhop(initialize_starting_state(),[('play','start')])

# ********************************************************************* #

# Examples:

if run_dialog_unit_test:
    print("\nRun 'select genre' assuming no prior confirmation:")
    schema = '\n# {}. The user input is {} to proceed directly:'
    insert = [ 'clear enough', 'too confused' ]
    for index in range(len(insert)):
        print(schema.format(index + 1,insert[index]))
        pyhop(initialize_starting_state(),[('select','genre','first')])

if run_dialog_unit_test:
    print('\nSimple tests of "confirm play" with a contrived state:')
    schema = '\n# {}. The user input is sufficiently {} the default:'
    insert = [ 'different from', 'similar to' ]
    for index, input in enumerate(['just play me some sting','ply some stig']):
        print(schema.format(index + 1,insert[index]))
        start = commit(initialize_starting_state(),'premise',match(input))
        print('User: {}'.format(input.capitalize()))
        history(0,input)
        confirm_play_m(start, 'play')

# ********************************************************************* #

# Examples:

if run_dialog_unit_test:
    print('\nTrying "recover artist" with domain-specific payload:')
    pyhop(initialize_starting_state(),[('recover','artist','music')])

if run_dialog_unit_test:
    print('\nRun "recover artist" with the default language option:')
    pyhop(initialize_starting_state(),[('recover','artist')])

if run_dialog_unit_test:
    print('\nRun "recover artist or genre" with default language:')
    pyhop(initialize_starting_state(),[('recover',['artist','genre'])])

# ********************************************************************* #
