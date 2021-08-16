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

class TalkToMe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    # trigger on user intent "me.to.talk.intent"
    @intent_handler( 'me.to.talk.intent' )
    @adds_context('Context_Conversation')
    def handle_me_to_talk_intent(self, message):
        self.B_conv = False
        #self.S_hostname = "Chuck"
        self.S_hostname = os.uname().nodename
        self.speak_dialog('me.to.talk', data={ 'hostname': self.S_hostname }, expect_response=False)
        self.speak_dialog('query.want.a.talk', expect_response=True)

    # trigger on user intent "yes I want a talk with you"
    @intent_handler( IntentBuilder('yes.want.a.talk.intent').require('yes').require('Context_Conversation').build() )
    @removes_context('Context_Conversation')
    @adds_context('Context_YourDay')
    def handle_yes_want_a_talk_intent(self, message):
        self.speak_dialog('yes.want.a.talk', expect_response=True)

    # trigger on user intent "I had a good day"
    @intent_handler( IntentBuilder('good.day.intent').require('great').require('Context_YourDay').build() )
    def handle_good_day_intent(self, message):
        self.speak_dialog('good.day', expect_response=True)

    # trigger on user intent "I had a bad day"
    @intent_handler( IntentBuilder('bad.day.intent').require('bad').require('Context_YourDay').build() )
    def handle_bad_day_intent(self, message):
        self.speak_dialog('bad.day', expect_response=True)

    # trigger on user intent "no I dont want a talk with you"
    @intent_handler( IntentBuilder('dont.want.a.talk.intent').require('no').require('Context_Conversation').build() )
    @removes_context('Context_Conversation')
    def handle_dont_want_a_talk_intent(self, message):
        self.speak_dialog('dont.want.a.talk', expect_response=False)
        self.speak_dialog('byebye', expect_response=False)

    # trigger on user intent "bye bye"
    @intent_handler( IntentBuilder('byebye.intent').require('byebye').require('Context_YourDay').build() )
    @removes_context('Context_Conversation')
    @removes_context('Context_YourDay')
    def handle_dont_want_a_talk_intent(self, message):
        self.speak_dialog('byebye', expect_response=False)


    def stop(self):
        pass


def create_skill():
    return TalkToMe()
