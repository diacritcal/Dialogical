# -*- coding: utf-8 -*-

"""
Support for hierarchical task planner dialog management 
Author: Tom Dean <tld@google.com> Date: August 17, 2014
"""

# Provides: assign, complete, history, interact, interject, match, lookup, patience, platonic - import zanax_NLU as nlu

import select, sys

from random import randint

# interject first of several utterances:
def interject(utterance,continuation=False):
    if continuation:
        sys.stdout.write('\n')
    print('{}: {}'.format(zinn_name,utterance))

# keep a history of past user input.
def history(index=0,input=False):
    # negative index means reset.
    if index < 0:
        history.queue = []
        return True
    # check for a valid index .
    elif index > len(history.queue):
        raise IndexError('Ancient History!')
    # no input means return item.
    elif not input:
        return history.queue[index]
    # otherwise append the input.
    else:
        if not input.endswith('\n'):
            history.queue.insert(0,input)
        else:
            history.queue.insert(0,input[:-1])
        return True
# history is a funcion attribute.
history.queue = []

# basic mode of interacting with a user:
def interact(utterance,continuation=False):
    if continuation:
        sys.stdout.write('\n')
    input = raw_input('{}: {}\n{}: '.format(zinn_name,utterance,user_name))
    history(0,input)
    return input

# variation on interact featuring timeout:
def patience(utterance,pause,continuation=False):
    if continuation:
        sys.stdout.write('\n')
    print('{}: {}'.format(zinn_name,utterance))
    sys.stdout.write('{}: '.format(user_name))
    sys.stdout.flush()
    return select.select([sys.stdin], [], [], pause)[0]

# above can interrupt the user in the midst
# of typing; might want to 'peek' to see if
# the user has started typing an input and
# if so, give her a little extra time; use
# os.isatty or sys.stdin.isatty to 'peek'.

# if patience waits on user, rewarded wins:
def rewarded():
    input = sys.stdin.readline()
    history(0,input)
    return input

# allow definition of aliases as lists of slots.
def complete(slots):
    # normalizes slot arguments as slot lists.
    if isinstance(slots,basestring):
        slots = [slots]
    result = []
    for slot in slots:
        if not slot in complete.alias:
            result.append(slot)
        else:
            result += complete.alias[slot]
    return result
# define alias dictionary as function attribute.
complete.alias = {'media':['song','album'],
                  'music':['artist','genre']}

# ugly hack to keep error-handling generic:
def assign(state,field,key,val):
    if field == 'user':
        state.user[key] = val
    elif field == 'last':
        state.last[key] = val
    elif field == 'sent':
        state.sent[key] = val
    elif field == 'comp':
        state.comp[key] = val
    else:
        print('Unknown field: {}'.format(field))

# general keyword spotting categories:
pos_words = ['yes','yep','sure','fine','ok','okay','right','positive','awesome']

neg_words = ['no','nada','nope','noway','nope','nothin','not','but','negative']

any_words = ['anything','something','whatever','surprise','sure','choose','all']

hey_words = ['hi','hello','hey','wuzup','lo','cheers','morning','gday','howdy']

dig_words = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

num_words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

nym_words = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth']

why_words = ['why', 'what', 'which', 'when', 'where']

usr_words = ['tom','peter','sudeep','johnny','gabe','anja','luheng','xin', 'jay',
             'shalini','larry','sergey','alan','alfred','kannan','ravi', 'blaise']

# music related keyword spotting categories:
play_words = ['play', 'pick', 'spin', 'listen', 'hear']

album_words = ['bad', 'thriller', 'nevermind', 'tapestry']

artist_words = ['sting', 'beatles', 'prince', 'jackson']

genre_words = ['rock', 'jazz', 'blues', 'pop', 'classical']

song_words = ['yesterday', 'satisfaction', 'macarena']

# library for approximate string matching:
from difflib import get_close_matches, SequenceMatcher

def match_words(words,category,thresh=0.8):
    if thresh == 0.0:
        return [word for word in words if word in category]
    else:
        matches = []
        for word in words:
            matches += get_close_matches(word,category,n=2,cutoff=thresh)
        return matches

def match_numbers(words,thresh=0.0):
    matches = match_words(words,num_words,thresh)
    if not matches == []:
        return num_words.index(matches[0])
    else:
        matches = match_words(words,dig_words,thresh)
        if not matches == []:
            return dig_words.index(matches[0])
        else:
            matches = match_words(words,nym_words,thresh)
            if not matches == []:
                return nym_words.index(matches[0])
            else: 
                return False

# proxy for the zinn feature matcher.
def lookup(input,category):
    if isinstance(input,basestring):
        words = input.lower().split()
    else:
        raise ValueError('Expecting base string input!')
    if category is 'positive':
        return match_words(words,pos_words,0.8)
    elif category is 'negative':
        return match_words(words,neg_words,0.8)
    elif category is 'name':
        return match_words(words,usr_words,0.5)
    elif category is 'forall':
        return match_words(words,any_words,0.8)
    elif category is 'hello':
        return match_words(words,hey_words,0.8)
    elif category is 'play':
        return match_words(words,play_words,0.8)
    elif category is 'why':
        return match_words(words,why_words,0.8)
    elif category is 'album':
        return match_words(words,album_words,0.8)
    elif category is 'artist':
        return match_words(words,artist_words,0.8)
    elif category is 'song':
        return match_words(words,song_words,0.8)
    elif category is 'genre':
        return match_words(words,genre_words,0.8)
    elif category is 'number':
        return match_numbers(words)
    else:
        print "Unknown category:", category
        return False

# application specific feature matcher.
def match(input):
    matched = {'input':input}
    if isinstance(input,basestring):
        words = input.lower().split()
    else:
        raise ValueError('Expecting base string input!')
    matches, discard = match_alt(words,album_words,0.8)
    words = [word for word in words if word not in discard]
    matched['album'] = matches
    matches, discard = match_alt(words,artist_words,0.8)
    words = [word for word in words if word not in discard]
    matched['artist'] = matches
    matches, discard = match_alt(words,genre_words,0.8)
    words = [word for word in words if word not in discard]
    matched['genre'] = matches
    matches, discard = match_alt(words,song_words,0.8)
    words = [word for word in words if word not in discard]
    matched['song'] = matches
    matches, discard = match_alt(words,play_words,0.8)
    words = [word for word in words if word not in discard]
    matched['play'] = matches
    # return the unmatched words along with original input.
    matched['residue'] = words
    return matched

# helper function for the slot matcher.
def match_alt(words,category,thresh):
    discard = []
    matches = []
    for word in words:
        match = get_close_matches(word,category,n=2,cutoff=thresh)
        if match:
            discard.append(word)
            matches += match
    return matches, discard

# how similar are two text strings.
def similarity(a,b):
    sm = SequenceMatcher(None,a,b)
    return sm.ratio()

# default system (Zinn) and user name.
zinn_name = "Zinn"
user_name = "User"

# 'play' on Plato's Dialog on Virtue:
def platos_socratic_dialogue_menos_paradox():
    global zinn_name
    global user_name
    zinn_name = "Meno"
    user_name = "Plato"

def menos_version_of_the_learners_paradox():
    "And how will you inquire into a thing when you " + \
    "are wholly ignorant of what it is? Even if you " + \
    "happen to bump right into it, how will you know " + \
    "it is the thing you didn't know?"

def platonic():
    if platonic.not_already_tried_flag and not randint(0,2):
        interject("Impasse! I'll play Meno to your Plato.")
        platos_socratic_dialogue_menos_paradox()
        input = interact("Perhaps you've heard of 'Meno's Paradox''")
        if lookup(input,'positive'):
            interject("It's also called the 'Learner's Paradox'.")
        elif lookup(input,'negative'):
            interject("No? Check out 'Plato's Dialogue on Virtue'?")
        else:
            interject("Well, you can't learn what you don't know.")
        platonic.not_already_tried_flag = False
        return True
    else:
        return False

# initialize function attribute after definition:
platonic.not_already_tried_flag = True

# Example:

if False:
    matches, residue = match('play some stingy')
    print matches
    print residue
