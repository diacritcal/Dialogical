# -*- coding: utf-8 -*-

"""
Topic: Simple NLG utility for an error mitigation module
Author: Tom Dean <tld@google.com> Date: August 21, 2014
"""

# Provides: choose, expand - import zanax_NLG as nlg

from re import search

from random import randint

# ********************************************************************* #

# class and registration service for applying linguistic variants.
class variant():
    """A variant is just a set of different ways to say the same thing"""
    def __init__(self,name,strs):
        self.name = name
        self.strs = strs
        variant.register[name] = self
    def choose(self):
        return self.strs[randint(0,len(self.strs) - 1)]

# register variants in a dictionary associated with variant class.
variant.register = dict()

def get_variant(key):
    if key in variant.register:
        return variant.register[key]
    else:
        return variant.register['default']
    
# generate random instance from variants and bindings.
def select(lst_or_str,rest=[],variable_bindings={}):
    if not isinstance(lst_or_str,basestring):
        # recursive operation on previously expanded string.
        if isinstance(lst_or_str,list):
            # pass the rest of the list to allow for lookahead.
            return [ select(lst_or_str[n],
                            lst_or_str[n+1:],variable_bindings)
                     for n in range(0,len(lst_or_str)) ]
        else:
            raise ValueError('Expecting strings {}!'.format(lst_or_str))
    elif search(r'\$',lst_or_str):
        # instantiate schema variables using supplied bindings.
        return instantiate(lst_or_str,variable_bindings)
    elif lst_or_str[0] == '[' and lst_or_str[-1] == ']':
        # embedded lists allow for simple lightweight variants.
        return choose(eval(lst_or_str))
    elif lst_or_str[0] == '{' and lst_or_str[-1] == '}':
        # embedded dictionaries allow for arbitrary operations.
        return deploy(eval(lst_or_str),rest,variable_bindings)
    elif lst_or_str in variant.register:
        # recursive expansion enabling choices within variants.
        return expand(variant.register[lst_or_str].choose(),bindings,False)
    else:
        return lst_or_str

# reimplement using import 'partial' from 'functools'.
def deploy(deployment_bindings,next_tokens,variable_bindings):
    if 'function' in deployment_bindings and \
           'arguments' in deployment_bindings:
        return deployment_bindings['function'](
            deployment_bindings['arguments'], next_tokens, variable_bindings)
    else:
        raise ValueError('Expecting function field: {}'.format(bindings))

# instantiate one or zero variables within a string.
def instantiate(string,variable_bindings):
    match = search(r'\$[a-zA-Z]+',string)
    if match:
        var = match.group(0)
        if var[1:] in variable_bindings:
            # variable instantiation precedes embedded deployment.
            return select(string.replace(var,variable_bindings[var[1:]]))
        else:
            raise ValueError('Expecting binding for {}!'.format(var))
    else:
        return string
    
# expand a list of strings, variants and variables.
def expand(str,bindings={},capitalize=True):
    str = ' '.join(select(str.split(),[],bindings))
    if not capitalize:
        return single(str)
    else:
        return single(str[0].upper() + str[1:])

def single(str):
    # remove double/start/end spaces in a string.
    return ' '.join(str.split())

# simple utility selecting a random entry in list.
def choose(lst):
    return lst[randint(0,len(lst) - 1)]

# heuristics to determine if a string is plural.
def plural(lst_or_str):
    if isinstance(lst_or_str,basestring):
        if str[-1] == 's' or search(r' and ',lst_or_str):
            return True
        else: 
            return False
    elif isinstance(lst_or_str,list):
        if 'and' in lst_or_str:
            return True
        else: 
            return False
    else:
        raise ValueError('Expecting string or list: {}'.format(lst_or_str))

# create conjunction or disjunction from tokens
def join(tokens,operator='and'):
    if len(tokens) == 0:
        raise ValueError('Expecting a nonempty list!')
    elif len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return '{} {} {}'.format(tokens[0],operator,tokens[1])
    else: 
        conjunction = tokens[0]
        for token in tokens[1:-1]:
            conjunction += ', {}'.format(token)
        return '{} {} {}'.format(conjunction,operator,tokens[-1])

# ********************************************************************* #

# An application-and-task-specific payload is a dictionary containing
# utterances appropriate to an application. payloads can also contain
# variable bindings that can be used for passing run-time information 
# into an application-independent component, e.g., error-mitigation.

# class and registration service for application-specific payloads.
class payload():
    """A payload is used to customize an application-independent module."""
    def __init__(self,caller,callee,schemata,bindings={}):
        self.name = caller + "+" + callee
        # schema are strings containing variant keys and variables.
        self.schemata = schemata
        # bindings are common to all schema, but can be overridden.
        self.bindings = bindings
        # payloads indexed by calling and called task identifiers.
        if not caller in payload.register:
            payload.register[caller] = {}
        if not callee in payload.register[caller]:
            payload.register[caller][callee] = self
        else:
            raise KeyError('Registered payload exists: {}!'.format(callee))
    def load(self,selector,bindings=None):
        if not bindings:
            bindings = self.bindings
        if not selector in self.schemata:
            raise KeyError('Missing schema selector: {}!'.format(selector))
        return expand(self.schemata[selector],bindings)
    def peek(self,selector):
        return selector in self.schemata

# register payloads in a dictionary associated with payload class.
payload.register = dict()

def get_payload(caller,callee):
    if not callee:
        return {}
    elif isinstance(caller,payload):
        return payload
    elif caller in payload.register and \
             callee in payload.register[caller]:
        return payload.register[caller][callee]

# Examples:

if True:
    # in each of the following cases, the calling task is 'music', 
    # but the language is different depending on whether the callee
    # is recovering from a non-understanding or resolving ambiguity:
    payload('music',
            'recover',
            {'leader':"I didn't catch mention of any music.",
             'prompt':"What music would you like to hear?"})

    payload('music',
            'resolve',
            {'leader':"There's an artist and a song by that name.",
             'prompt':"Was it the song or the artist you meant?"})

# ********************************************************************* #

# Greetings:
variant('SIMPLE_HELLO', ['hey there', 'hi', 'hi there', 'hello', "what's up?", 'yo'])

variant('SIMPLE_GOODBYE', ['later', 'bye', 'adieu', 'au revoir', 'ciao', 'adios'])

variant('SORRY_GOODBYE', ['perhaps another time. bye.','you seem busy. Maybe Later.'])

# Abilities:
variant('I_CAN_PLAY', ['I can play particular artists, songs or categories.', 
                       "maybe you have a favorite band you'd like to hear?", 
                       "just let me know what sort of music you're interested in.", 
                       "we can do songs, artists, bands, genres. Just let me know what you like."])

variant('I_CAN_SUGGEST', ['I can also just suggest something for you.', 
                          'if you want I can just play something random.', 
                          'would you like me to just play something for you?'])

variant('ILL_REMEMBER', ["I'll make a note of it.", "I'll remember that for next time.",  "I'm learning."])

# Nonunderstanding:
variant('ADMIT_NONUNDERSTANDING', ["sorry, but I just don't understand what you're saying.", "I guess I haven't learned enough to understand what you're saying."])

variant('MISSED_GENERAL', ["I didn't get what you said.", "I missed that.", "I didn't get that."])

variant('MISSED_GENERAL_AGAIN', ["I didn't get that either.", "I missed that too.", "I stll didn't get that."])

variant('MISSED_AGAIN', ["I still didn't get what you said.", "I missed it again.", "I didn't get that either."])

variant('MISSED_PARTIAL', ["I didn't get all of what you said.", "I missed part of what you said.", "I might have missed part of that."])

variant('REPHRASE_THAT', ["if you don't mind, try saying it a different way.", "could you rephrase it for me?"])

variant('LETS_START_OVER', ["I'm not getting it. let's try again.", "I'm pretty confused. let's start over.", "I'm kinda wedged. How about we restart?"])

# note this is a slot-specific error prompt.
variant('ERROR_MISSED_MUSIC', ["I didn't get what you wanted me to play", "I got that you wanted me to play something, but I missed which music or artist."])

# note this is a slot-specific error prompt.
variant('ERROR_MISSED_SENTIMENT', ["I didn't get whether you liked it or not", "I didn't understand if you're saying you like it or dislike it."])  

# Acknowledge:
variant('ACK_COMPRENHENSION', ["okay", "OK", "sure", "got it", "no problem", "right on"])

# Confirmation:
variant('ASK_WAS_MUSIC', ["does that refer to the music you want to hear?", 
                          "is that the music you want me to play?", 
                          "was that an artist, album, song title or genre?"])

variant('ASK_WAS_PLAY', ["do you mean play it?",
                         "are you asking me to play it?",
                         "is that another way to say play it?"])

variant('ASK_WHAT_PLAY', ["what do you want to hear?", 
                          "what can I play for you?",
                          "tell me what you'd like to hear?"])

variant('IS_WAY_SAY', ['does that roughly mean'])
# variant('IS_WAY_SAY', ['is this how you say','is this the way you say','are you trying to say','do you mean','is this the same as'])

# Idiomatic:
variant('HERES', ["here's", "here is", "here goes", "introducing"])

variant('I_GOT', ["I got", "got", "I understand"])

# Specialiized:
variant('WHEN_YOU_SAY', ['by', 'when you say'])
# variant('WHEN_YOU_SAY', ['when you say','when you say to me','by telling me','by','in saying to me','in telling me','when you tell me'])

variant('MISSED_MUSIC', ["I didn't get what you wanted me to play", 
                         "I got that you wanted me to play something, but I missed which music or artist."])

# examples with embedded choices.
variant('DOES_THAT_MEAN', ["does that mean ['that','']",
                           "are you saying ['that','']",
                           "do you mean ['that','']",
                           "does that imply ['that','']",
                           "are you telling me ['that','']"])

variant('HAVE_YOU_HEARD', ["have you heard ['that','']",
                           "have you listened to ['that','']",
                           "what about ['that','']",
                           "are you familiar with ['that','']"])
        
variant('DO_YOU_KNOW', ["do you know ['that','']",
                        "are you aware ['that','']",
                        "do you realize ['that','']"])

# ********************************************************************* #

# if subject is plural then use "are" otherwise use "is".
def is_or_are(args,rest,bdgs):
    if isinstance(args,list) and isinstance(args[0],basestring):
        if plural(args[0]):
            return args[0] + ' are'
        else:
            return args[0] + ' is'
    else:
        raise ValueError('Expecting one-item list {}!'.format(args))

# Examples:

if True:
    bindings = {'THIS':'\"spin it up\"', 'THAT':'\"play\"'}
    str = 'WHEN_YOU_SAY $THIS IS_WAY_SAY $THAT?'
    for i in range(10):
        print expand(str,bindings)

    bindings = {'THIS':'spin it up', 'THAT':'play'}
    str = "WHEN_YOU_SAY ['that',''] \"$THIS\" IS_WAY_SAY \"$THAT?\""
    for i in range(10):    
        print expand(str,bindings)

    bindings = {'SLOTS':join(['artist','genre'])}
    str = "The {'function':is_or_are,'arguments':['$SLOTS']} assigned."
    print expand(str,bindings)

# ********************************************************************* #

