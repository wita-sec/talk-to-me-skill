#
# Mycroft Skill Talk-to-me
#  TAGS: skill prototpye, learning skill programming, available for Picroft
#  Version 2.0.20210803
#
#  Skill idea
#  in a loop Pi replies to a number of spoken user intents
#  until user stops the conversation
#  or when user did not speak for a timeout period
#

import os
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler, intent_file_handler
from mycroft.skills.context import adds_context, removes_context
from mycroft.util.parse import normalize


class TalkToMe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.S_skill = "TalkToMe"
        self.S_version = "V20210922.45"
    # trigger on user intent "me.to.talk.intent"
    # note, decorators must be on top of the function call
    @intent_handler( 'me.to.talk.intent' )
    @adds_context("Context_Conversation")
    def handle_me_to_talk_intent(self, message):
        self.S_hostname = "chuck  from  " + os.uname().nodename
        self.log.info("executing me.to.talk.intent" + " " + self.S_version)
        self.speak_dialog('me.to.talk', data={ 'hostname': self.S_hostname }, expect_response=False)
        self.speak_dialog('query.want.a.talk', expect_response=True)


    # trigger on user intent "no I dont want a talk with you"
    @intent_handler( IntentBuilder('DontWantATalk').require('nope').require("Context_Conversation").build() )
    @removes_context("Context_Conversation")
    def handle_dont_want_a_talk_intent(self, message):
        self.log.info("executing DontWantATalk.intent")
        self.speak_dialog('dont.want.a.talk', expect_response=False)
        self.speak_dialog('byebye', expect_response=True)


    # trigger on user intent "yes I want a talk with you"
    @intent_handler( IntentBuilder('YesWantATalk').require('yes').require("Context_Conversation").build() )
    @adds_context("Context_YourDay")
    @removes_context("Context_Conversation")
    def handle_yes_want_a_talk_intent(self, message):
        self.log.info("executing YesWantATalk.intent")
        self.speak_dialog('yes.want.a.talk', expect_response=True)

    # trigger on user intent "I had a good day"
    @intent_handler( IntentBuilder('GoodDay').require('great').require("Context_YourDay").build() )
    @removes_context("Context_YourDay")
    def handle_good_day_intent(self, message):
        self.log.info("executing GoodDay.intent")
        self.speak_dialog('good.day', expect_response=True)

    # trigger on user intent "I had a bad day"
    @intent_handler( IntentBuilder('BadDay').require('bad').require("Context_YourDay").build() )
    @removes_context("Context_YourDay")
    def handle_bad_day_intent(self, message):
        self.log.info(" executing BadDay.intent")
        self.speak_dialog('bad.day', expect_response=True)

    # trigger to play an mp3 file
    # the mp3 file will be selected ramdomly from a list of available files
    # the selected mp3 file is addressed via its URI file://<host>/<path>/<file>
    # player needs to be set in mycroft config: play_mp3_cmd = config.get("play_mp3_cmdline")
    # i.g. omxplayer file.mp3
    # TODO


    # DONE



    # trigger on user byebye intent anytime
    def converse(self, message):
        self.log.info("executing converse()")
        #TypeError: 'NoneType' object is not subscriptable
        #utt = normalize(message.data.get('utterances', "")[0].lower())

        #index error: string index out of range
        #utt = normalize(message.data.get('utterance', "")[0].lower())

        #TypeError: 'NoneType' object is not subscriptable
        #utt = normalize(message.data['utterances'][0]).lower()
        #mmm = message.data['utterances'][0]
        #nmmm = normalize(mmm)
        #utt = nmmm.lower()
        #self.log.info("executing converse()" + " mmm: " + mmm )
        #self.log.info("executing converse()" + " mmm type: " + str( type(mmm) ) )
        #self.log.info("executing converse()" + " nmmm: " + nmmm )
        #self.log.info("executing converse()" + " nmmm type: " + str( type(nmmm) ) )
        #self.log.info("executing converse()" + " utt: " + utt )
        #self.log.info("executing converse()" + " utt type: " + str( type(utt) ) )
        #if self.voc_match(utt, 'byebye'):

        #this log will be written but it causes an exception
        #  TypeError: 'NoneType' object is not subscriptable

        #self.log.info("executing converse()" + " utt: " + normalize(message.data['utterances'][0]).lower() )
        #however this call of voc_match runs well, without an exception
        if self.voc_match(normalize(message.data['utterances'][0]).lower(), 'byebye'):
            self.speak_dialog('byebye')
            return True

        return False

    def stop(self):
        self.log.info("running stop()")
        pass


def create_skill():
    return TalkToMe()
