# ./Dialogical/README.txt

# ./Dialogical/zanax_DOC.dir/index.html

Interaction and Negotiation in Learning and Understanding Dialog

Interaction and negotiation are an essential component of natural language understanding in conversation. We argue this is particularly the case in building artificial agents that rely primarily on language to interact with humans. Rather than thinking about misunderstanding—thinking the user said one thing when he said another—and non-understanding—not having a clue what the user was talking about—as a problem to be overcome, it makes more sense to think of such events as opportunities to learn something and a natural part of understanding that becomes essential when the agent trying to understand has a limited language understanding capability. Moreover, many of the same strategies that are effective in situations in which the agent’s limited language facility fails also apply to the agent actively engaging the user in an unobtrusive manner to collect data and ground truth in order to extend its repertoire of services that it can render and to improve its existing language understanding capabilities. In the case of developing an agent to engage users in conversations about music, actively soliciting information from users about their music interests and resolving misunderstandings on both sides about what services the application can offer and what service in particular the user wants now is already a natural part of the conversation. Data collected from thousands or millions of users would provide an invaluable resource for training NLP components that could be used to build more sophisticated conversational agents.

# ./Dialogical/zanax_DOC.dir/README

# -*- coding: utf-8 -*-

# Zanax - A Dialog Error Handling Module for Zinn

The word Zanax is a made-up name that happens to correspond to a common misspelling - but correct pronunciation - of Xanax, the trade name for the drug alprazolam.  Alprazolam is a short-acting benzodiazepine used to treat anxiety disorders and panic attacks.  Zanox incorporates the Z in Zinn - as Zinn employs similar error-handling strategies in its dialog manager - as well as a nod to Xanax for Zanax's targeted calming - don't panic - effect. 

Zanax includes very simple NLU and NLG components that rely primarily on, respectively, keyword spotting and simple schema-based phrase generators. It also includes a complete hierarcial ordered planner (HOP) developed by Dana Nau. The actual error handling module is implemented as a set primitive actions, tasks relating to dialog, and plans for carrying out said tasks. The complete prototype consists of four file and fewer than 1500 lines of code. The error handling part consists of less than 500 lines excluding comments, and the planner is elegantly simple consisting of fewer than 200 lines excluding comments.

% wc -l zanax_*.py
     252 zanax_HOP.py
     582 zanax_HTN.py
     307 zanax_NLG.py
     275 zanax_NLU.py
    1416 total
% cat zanax_HOP.py | grep -v "#" | wc -l
     193
% cat zanax_HTN.py | grep -v "#" | wc -l
     430
% cat zanax_*.py | grep -v "#" | wc -l
    1121

zanax_HOP.py - Basic Hierarchical Ordered Planner 
zanax_HTN.py - Hierarchical Task Network for Dialog
zanax_NLG.py - Simple Natural Language Generation
zanax_NLU.py - Simple Natural Language Understanding

To experiment with Zanax decant the tarball in a directory, launch python and just type: import zanax_HTN

This will load the whole system, run some tests and then start a conversation with you. To avoid needless disappointment read the following and check out the examples below:

The NLU is as thin as it can be and still illustrate Zinn's ambiguity resolution and non-understanding recovery strategies.  It is best to use words selected from the following categories to convey your intentions. There will still be plenty of opportunities to introduce ambiguity and obfuscation.  For example, type "sting" or "stig" when you mean "play sting", or type "I really like jazz but not classical" when you're asked for your favorite genre.  Misspellings that are still relatively close in edit distance to the correct spellings, shortcuts like "sting" in the context of a request for some music to play, and providing too much information as in the case: "I like Michael Jackson but only his early stuff and I don't mean the albums he did with the Jackson Five" are fair game, whether or not the current system handles them gracefully. The full version of Zinn with its larger vocabulary and more sophisticated key-word and key-phrase spotting capability based on embedding models will do a much better job on examples like these, but that's not what this implementation is designed to demonstrate. The objective shouldn't be just to confuse Zinn, or reveal the limitations of its vocabulary; you'll have an easy time of it in pursuing these entertainments. The objective should be to give Zinn at least a fighting chance and observe how it manages to recover the meaning of your utterances by asking simple questions as part of a natural dialog. See the examples below:

General word categories:

positive words / positive sentiment, e.g., yes, yep, sure, fine, okay, right, awesome, etc.
negative words / negative sentiment, e.g., no, nope, not, nada, noway, nothin, etc.
quantifier words, e.g., anything, something, whatever, all, etc.
greetings, e.g., hi, hello, cheers, howdy, morning, evening, afternoon, etc.
numbers, digits, ordering, e.g., last, next, previous, and indexing words, e.g., first, third, etc.

Music-related categories:

play words, e.g., play, pick, spin, listen, hear, perform, etc.
album words, e.g., bad, thriller, nevermind, tapestry, etc.
genre words, e.g., classical, blues, jazz, pop, rock, etc.
artist words, e.g., sting, beatles, prince, jackson, etc.
song words, e.g., yesterday, satisfaction, macarena, etc.
first names, e.g., tom, peter, sudeep, johnny, gabe, anja, luheng, xin, jay, shalini, larry, sergey, alan, alfred, kannan, ravi, blaise, etc.

Here's an example of interacting with Zinn:

Demonstrate play start patiently waiting for input:
Zinn: What can I play for you?
User: ....
Zinn: I can play particular artists, songs or categories.
User: ........
Zinn: If you want I can just play something random.
User: play some sting
Zinn: Got that you want me to play sting. correct?
User: yep
Zinn: Thanks. I got it now.
User: huh!
Zinn: I didn't get all of what you said.
Zinn: Give me one genre.
User: classical
Zinn: Thanks. I got your genre.

Run 'select genre' assuming no prior confirmation:
# 1. The user input is clear enough to proceed directly:

Zinn: What is your favorite type of music?
User: not pop
Zinn: Not my favorite, but I'm open to learn.
Zinn: I think you said that you don't like pop?
User: yes
Zinn: I'll take that as a 'yes' and not play any pop.
Zinn: How about one of: blues, rock, pop or jazz?
User: jazz
Zinn: Jazz is my favorite next to classical.
Zinn: Great. Let's talk about some jazz artists.

# 2. The user input is too confused to proceed directly:
Zinn: Do you have a favorite type of music?
User: not pop
Zinn: Not my favorite, but I'm open to learn.
Zinn: I think you said that you don't like pop?
User: nada
Zinn: Were you (1) confirming or (2) denying your dislike?
User: one
Zinn: Sounds good. I won't be playing any pop.
Zinn: How about one of: blues, rock, pop or jazz?
User: blues
Zinn: I like delta and Chicago blues styles.
Zinn: Great. Let's talk about some blues artists.

Simple tests of "confirm play" with a contrived state:

# 1. The user input is sufficiently different from the default:
User: Just play me some sting
Zinn: When you say "just play me some sting" does that roughly mean "play sting"?
User: yes
Zinn: Thanks. I got it now.

2. The user input is sufficiently similar to the default:
User: Ply some stig
Zinn: Got that you want me to play sting. correct?
User: yep
Zinn: Thanks. I understand it now.

Trying "recover artist" with domain-specific payload:
Zinn: I didn't catch mention of any music.
Zinn: What music would you like to hear?
User: maybe blues
Zinn: I didn't get that either.
Zinn: Could you say that a different way?
User: some blues
Zinn: Sorry. I'm totally confused.

Run "recover artist" with the default language option:
Zinn: I didn't get all of what you said.
Zinn: Give me one artist.
User: beatles
Zinn: Thanks. I got your artist.

Run "recover artist or genre" with default language:
Zinn: I didn't get all of what you said.
Zinn: Give me one artist or genre.
User: some blues
Zinn: Thanks. I got your genre.
>>> 
