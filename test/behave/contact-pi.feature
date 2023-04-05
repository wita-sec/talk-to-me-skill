Feature: contact-pi

  Scenario Outline: need someone to talk
    Given an english speaking user
     When the user says "<talk to me>"
     Then "talk-to-me" should reply with dialog from "me.to.talk.dialog"

  Examples: talk to me intent                        # Table heading  - name of the table
             | Is someone out there              |   # Column heading - refers to the When clause <...> above
             | Are you online                    |   # First value    - now all Scenarios follow that the user may use
             | Have you got some time for a talk |   # Second value
             | Talk to me                        |   # Third value



#           Scenario Outline: set a timer for an unspecified duration
#             Given an english speaking user
#               And no timers are previously set
#               When the user says "<set a timer for unspecified duration>"
#               Then "mycroft-timer" should reply with dialog from "ask.how.long.dialog" #How long of a timer?
#               And the user replies with "5 minutes"
#               And "mycroft-timer" should reply with dialog from "started.timer.dialog" #Timer started for {duration}
#
#              Examples: set a timer for an unspecified duration
#                | set a timer for unspecified duration |
#                | set a timer |
#                | start a timer |
#                | timer |
