from mycroft import MycroftSkill, intent_file_handler


class TalkToMe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('me.to.talk.intent')
    def handle_me_to_talk(self, message):
        hostname = ''

        self.speak_dialog('me.to.talk', data={
            'hostname': hostname
        })


def create_skill():
    return TalkToMe()

