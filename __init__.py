# Copyright 2023 MMWolf-Photovoltaik GbR
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Picroft Skill Talk-to-me
TAGS: skill prototpye, learning skill programming, available for Picroft
Version 3.1.20230320

Skill idea: have some small talk with Picroft
            questions and answers about photovoltaik, heatpump, soc, grid, electric vehicle
            you ask, Picroft answers to your questions
            Data is read from json files, examples attached.
            Date collection and json file generation is not part of this project.
"""
# Changelog
# Version 3.0.20230110 added new feature: query Pi about WITA-Energy data
# Version 3.1.20230320 added more vehicle queries

import os
from os.path import exists
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler, intent_file_handler
from mycroft.skills.context import adds_context, removes_context
from mycroft.util.parse import normalize

# note the relative '.'
from .wita_pi_energy import pi_energy

class TalkToMe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.S_skill = "TalkToMe"
        self.S_version = "V20230306"

    def initialize(self):
        # IHaveAQuestion
        self.register_intent_file("question.intent", self.handle_question_intent)
        # CarRange (tested: 1)
        self.register_intent_file("query.vehicle.range.intent", self.handle_car_range_query)
        # CarSoc (tested: 1)
        self.register_intent_file("query.vehicle.soc.intent", self.handle_car_soc_query)
        # CarOdo (tested: 1)
        self.register_intent_file("query.vehicle.odometer.intent", self.handle_car_odometer_query)



        # CarLeaseStartDate
        self.register_intent_file("query.vehicle.lease.start.date.intent", self.handle_car_lease_start_date_query)
        # CarLeaseKmCommittedPerYear
        self.register_intent_file("query.vehicle.lease.km.committed.per.year.intent", self.handle_car_lease_km_committed_per_year_query)
        # CarDaysLeasedNow
        self.register_intent_file("query.vehicle.days.leased.now.intent", self.handle_car_days_leased_now)
        # CarKmCommittedNow
        self.register_intent_file("query.vehicle.km.committed.now.intent", self.handle_car_km_committed_now)
        # CarKmToleranceNow
        self.register_intent_file("query.vehicle.km.tolerance.now.intent", self.handle_car_km_tolerance_now)
        #





        # OutdoorTemperature (tested: 1)
        self.register_intent_file("query.outdoor.temperature.intent", self.handle_outdoor_temperature_query)
        # DhwActive (tested: 1)
        self.register_intent_file("query.dhw.active.intent", self.handle_dhw_active_query)
        # HpCompressorActive (tested: 1)
        self.register_intent_file("query.hp.compressor.active.intent", self.handle_hp_compressor_active_query)
        # HPPowerConsumptionToday (tested: 1)
        self.register_intent_file("query.hp.power.consumption.today.intent", self.handle_hp_power_consumption_today_query)
        # DhwPowerConsumptionToday (tested: 1)
        self.register_intent_file("query.dhw.power.consumption.today.intent", self.handle_dhw_power_consumption_today_query)
        # ChargerID (tested: 1)
        self.register_intent_file("query.charger.id.intent", self.handle_charger_id_query)
        # ChargerChargeStatus (tested: 1)
        self.register_intent_file("query.charger.charge.status.intent", self.handle_charger_charge_status_query)
        # ChargerCharged (tested: 1)
        self.register_intent_file("query.charger.charged.intent", self.handle_charger_charged_query)
        # ChargerEnergy  (tested: 1)
        self.register_intent_file("query.charger.energy.intent", self.handle_charger_energy_query)
        # GridPowerConsumptionToday (tested: 1 intent ok but wrong query results)
        self.register_intent_file("query.grid.power.consumption.today.intent", self.grid_power_consumption_today_query)
        # GridPowerConsumptionTotal  (tested: 1)
        self.register_intent_file("query.grid.power.consumption.total.intent", self.grid_power_consumption_total_query)
        # GridPowerSupplyTotal (tested: 1)
        self.register_intent_file("query.grid.power.supply.total.intent", self.grid_power_supply_total_query)
        # PVPowerProductionTotal (tested: 1)
        self.register_intent_file("query.pv-power.production.total.intent", self.pv_power_production_total_query)
        # PVPowerProductionToday (tested: 1)
        self.register_intent_file("query.pv-power.production.today.intent", self.pv_power_production_today_query)
        # PVSocPercentageLoaded (tested: 1)
        self.register_intent_file("query.pv.soc.percentage.loaded.intent", self.pv_soc_percentage_loaded_query)
        # GridPowerFeedInToday
        self.register_intent_file("query.grid.power.feedin.today.intent", self.grid_power_feedin_today_query)
        # OverallPowerConsumptionToday
        self.register_intent_file("query.overall.power.consumption.today.intent", self.overall_power_consumption_today_query)
        # OverallPowerAutonomyToday
        self.register_intent_file("query.overall.power.autonomy.today.intent", self.overall_power_autonomy_today_query)
        # SummaryReport
        self.register_intent_file("query.summary.report.intent", self.summary_report_query)
        # VehicleReport
        self.register_intent_file("query.vehicle.report.intent", self.vehicle_report_query)
        # VehicleLeaseReport
        self.register_intent_file("query.vehicle.lease.report.intent", self.vehicle_lease_report_query)
        # ChargerReport
        self.register_intent_file("query.charger.report.intent", self.charger_report_query)
        # HeatpumpReport
        self.register_intent_file("query.heatpump.report.intent", self.heatpump_report_query)
        # GridReport
        self.register_intent_file("query.grid.report.intent", self.grid_report_query)
        # PVReport
        self.register_intent_file("query.pv.report.intent", self.pv_report_query)

        self.skill_path = "/opt/mycroft/skills/talk-to-me-skill"
        #self.lang = "de-de"
        self.pi_e = pi_energy("/opt/mycroft/skills/talk-to-me-skill/energy-files")

        self.query_hash = {
        #   search_key                   WITA_query_item                  not_found_dialog file
            # car range
            "CarRange":                  ("vehicle Range",                "query_vehicle_range_not_known"),
            # car soc percentage loaded
            "CarSoc":                    ("vehicle Soc",                  "query_vehicle_soc_not_known"),
            # car odometer
            "CarOdo":                    ("vehicle Odometer",             "query_vehicle_odometer_not_known"),


            # car when was the lease started
            "CarLeaseStartDate":         ("vehicle lease_start_date_spoken", "query_vehicle_lease_start_date_spoken_not_known"),
            # car how many km to go are committed per year
            "CarLeaseKmCommittedPerYear":("vehicle lease_km_committed_per_year", "query_vehicle_km_committed_per_year_not_known"),
            # car how many days was the car leased as of today
            "CarDaysLeasedNow":          ("vehicle_days_leased_now", "query_vehicle_days_leased_now_not_known"),
            # car how many km to go are committed as of today
            "CarKmCommittedNow":         ("vehicle_km_committed_now", "query_vehicle_km_committed_now_not_known"),
            # car how many km have we gone above or beyond the limit
            "CarKmToleranceNow":         ("vehicle_km_tolerance_now", "query_vehicle_km_tolerance_now_not_known"),


            # outdoor temperature at heatpump location
            "OutdoorTemperature":        ("outdoor",                      "query_outdoor_temperature_not_known"),
            # domestic hot water activ?
            "DhwActive":                 ("dhw_active",                   "query_dhw_active_not_known"),
            # heatpump compressor activ?
            "HpCompressorActive":        ("compressor_active",            "query_hp_compressor_active_not_known"),
            # today's total power consumption of the heatpump
            "HPPowerConsumptionToday":   ("power_input_total_today",      "query_power_input_total_today_not_known"),
            # today's power consumption for heatpump dhw
            "DhwPowerConsumptionToday":  ("power_input_dhw_today",        "power_input_dhw_today_not_known"),
            # charger serialnumber
            "ChargerID":                 ("charger Identifier",           "charger_identifier_not_known"),
            # charger charge status (C,B,A)
            "ChargerChargeStatus":       ("charger Charge status",        "charger_charge_status_not_known"),
            # power charger has charged
            "ChargerCharged":            ("charger Charged",              "charger_charged_not_known"),
            # power charger has charged
            "ChargerEnergy":             ("charger Energy",               "charger_energy_not_known"),
            # Power consumption from grid today
            "GridPowerConsumptionToday": ("netzbezug-total Energy_Today", "netzbezug_aktuell_energy_not_known"),
            # Power consumption from grid in total
            "GridPowerConsumptionTotal": ("netzbezug-total Energy",       "netzbezug_total_energy_not_known"),
            # Power supply to grid in total
            "GridPowerSupplyTotal":      ("netzeinspeisung-total Energy", "netzeinspeisung_total_energy_not_known"),
            # PV Power production in total
            "PVPowerProductionTotal":    ("pv-total Energy",              "pv_total_energy_not_known"),
            # PV Power production today
            "PVPowerProductionToday":    ("pv-aktuell Energy",            "pv_aktuell_energy_not_known"),
            # PV Soc percentage loaded
            "PVSocPercentageLoaded":     ("stromspeicher Soc",            "stromspeicher_soc_not_known"),
            # Grid Power FeedIn Today
            "GridPowerFeedInToday":     ("netzeinspeisung-total Energy_Today", "netzeinspeisung_total_Energy_Today_not_known"),
            # Overall Power Consumption Today
            "OverallPowerConsumptionToday": ("energy_consumption_today",       "energy_consumption_today_not_known"),
            # Overall Power Autonomy Today
            "OverallPowerAutonomyToday":    ("energy_autonomy_today",          "energy_autonomy_today_not_known"),
            # SummaryReport
            "SummaryReport":                ("summary",                        "summary_report_not_known"),
            # VehicleReport
            "VehicleReport":                ("vehicle",                        "vehicle_report_not_known"),
            # VehicleLeaseReport
            "VehicleLeaseReport":           ("lease",                          "vehicle_lease_report_not_known"),
            # ChargerReport
            "ChargerReport":                ("charger",                        "charger_report_not_known"),
            # HeatpumpReport
            "HeatpumpReport":               ("heatpump",                       "heatpump_report_not_known"),
            # GridReport
            "GridReport":                   ("grid",                           "grid_report_not_known"),
            # PVReport
            "PVReport":                     ("photovoltaik",                   "pv_report_not_known"),
        }


    def query(self, search_item):
        """ query the WITA Energy item "search_item" and send returned text to picroft speach.
            "search_item" is mapped via self.query_hash to a WITA_energy query which
            in turn is directed to the pi_energy object instanciated in initialize()
            error handling is performed by writing logs and sending an error message
            to picroft speach.

            return: none.
        """
        if search_item not in self.query_hash:
            self.speak_dialog('query_not_supported', expect_response=True)
            return
        query_ctrl = self.query_hash[search_item]
        rc, rc_msg, rc_TTS = self.pi_e.query(query_ctrl[0])
        self.log.info(" executed query " + query_ctrl[0])
        self.log.info(" rc= " + str(rc)  + " rc_msg= " + rc_msg)
        if rc != 0:
            if not exists(self.skill_path + "/locale/" + self.lang + "/" + query_ctrl[1] + ".dialog"):
                dialog = "query_default_not_known"
            else:
                dialog = query_ctrl[1]
            self.speak_dialog(dialog, expect_response=True)
        else:
            if isinstance(rc_TTS, list):
                for t in rc_TTS:
                    self.speak_dialog(t, expect_response=True)
            else:
                self.speak_dialog(rc_TTS, expect_response=True)
        return

    # trigger on user intent "me.to.talk.intent"
    # note, decorators must be on top of the function call
    @intent_handler( 'me.to.talk.intent' )
    @adds_context("Context_Conversation")
    def handle_me_to_talk_intent(self, message):
        #self.S_hostname = "chuck  from  " + os.uname().nodename
        self.S_hostname = os.uname()[1]
        self.log.info("executing me.to.talk.intent" + " " + self.S_version)
        self.speak_dialog('me.to.talk', data={ 'hostname': self.S_hostname }, expect_response=False)
        self.speak_dialog('query.want.a.talk', expect_response=True)


    # trigger on user intent "no I dont want a talk with you"
    @intent_handler( IntentBuilder('DontWantATalk').require('nope').require("Context_Conversation").build() )
    #@intent_handler( IntentBuilder('DontWantATalk').require('nope').build() )
    @adds_context("Context_YourDay")
    @removes_context("Context_Conversation")
    def handle_dont_want_a_talk_intent(self, message):
        self.log.info("executing DontWantATalk.intent")
        self.speak_dialog('dont.want.a.talk', expect_response=False)
        self.speak_dialog('byebye', expect_response=True)


    # trigger on user intent "yes I want a talk with you"
    #@intent_handler( IntentBuilder('YesWantATalk').require('yes').require('talk').require("Context_Conversation").build() )
    @intent_handler( IntentBuilder('YesWantATalk').require('yes_talk').require("Context_Conversation").build() )
    @adds_context("Context_YourDay")
    @removes_context("Context_Conversation")
    def handle_yes_want_a_talk_intent(self, message):
        self.log.info("executing YesWantATalk.intent")
        self.speak_dialog('yes.want.a.talk', expect_response=True)

    # trigger on user intent "I had a good day"
    #@intent_handler( IntentBuilder('GoodDay').require('great').require("Context_YourDay").build() )
    @intent_handler( 'good.day.intent' )
    @removes_context("Context_YourDay")
    def handle_good_day_intent(self, message):
        self.log.info("executing GoodDay.intent")
        self.speak_dialog('good.day', expect_response=True)

    # trigger on user intent "I had a bad day"
    #@intent_handler( IntentBuilder('BadDay').require('bad').require("Context_YourDay").build() )
    @intent_handler( 'bad.day.intent' )
    @removes_context("Context_YourDay")
    def handle_bad_day_intent(self, message):
        self.log.info(" executing BadDay.intent")
        self.speak_dialog('bad.day', expect_response=True)

    # trigger on user intent "I have a question"
    #@intent_handler( IntentBuilder('Question').require('question').require("Context_Conversation").build() )
    #@intent_handler( 'question.intent' )
    #@removes_context("Context_YourDay")
    #@adds_context("Context_Question")
    #def handle_question_intent(self, message):
    #   self.log.info(" executing question.intent")
    #   self.speak_dialog('question', expect_response=True)

    @intent_handler( IntentBuilder('IHaveAQuestion').build() )
    def handle_question_intent(self, message):
        self.log.info(" executing question.intent")
        self.speak_dialog('question', expect_response=True)

    # trigger on user intent "I need help"
    @intent_handler( 'help.intent' )
    @removes_context("Context_YourDay")
    @adds_context("Context_Help")
    def handle_help_intent(self, message):
        self.log.info(" executing help.intent")
        self.speak_dialog('help', expect_response=True)
        self.speak_dialog('help02', expect_response=True)

    # trigger on user intent "I need help -- continued"
    #@intent_handler( IntentBuilder('Help_Continued').require('helpme').require("Context_Help").build() )
    #def handle_question_intent(self, message):
    #    self.log.info(" executing help_continued.intent")
    #    self.speak_dialog('help02', expect_response=True)

    # trigger on user intent "Bye Bye"
    @intent_handler( IntentBuilder('ByeBye').require('byebye').build() )
    @removes_context("Context_Conversation")
    @removes_context("Context_YourDay")
    def handle_byebye_intent(self, message):
        self.log.info(" executing byebye.intent")
        self.speak_dialog('byebye', expect_response=False)

    # following are triggers about WITA_Energy queries

    @intent_handler( IntentBuilder('CarRange').build() )
    def handle_car_range_query(self, message):
        self.query('CarRange')

    @intent_handler( IntentBuilder('CarSoc').build() )
    def handle_car_soc_query(self, message):
        self.query('CarSoc')

    @intent_handler( IntentBuilder('CarOdo').build() )
    def handle_car_odometer_query(self, message):
        self.query('CarOdo')

    @intent_handler( IntentBuilder('CarLeaseStartDate').build() )
    def handle_car_lease_start_date_query(self, message):
        self.query('CarLeaseStartDate')

    @intent_handler( IntentBuilder('CarLeaseKmCommittedPerYear').build() )
    def handle_car_lease_km_committed_per_year_query(self, message):
        self.query('CarLeaseKmCommittedPerYear')

    @intent_handler( IntentBuilder('CarDaysLeasedNow').build() )
    def handle_car_days_leased_now(self, message):
        self.query('CarDaysLeasedNow')

    @intent_handler( IntentBuilder('CarKmCommittedNow').build() )
    def handle_car_km_committed_now(self, message):
        self.query('CarKmCommittedNow')

    @intent_handler( IntentBuilder('CarKmToleranceNow').build() )
    def handle_car_km_tolerance_now(self, message):
        self.query('CarKmToleranceNow')

    @intent_handler( IntentBuilder('OutdoorTemperature').build() )
    def handle_outdoor_temperature_query(self, message):
        self.query('OutdoorTemperature')

    @intent_handler( IntentBuilder('DhwActive').build() )
    def handle_dhw_active_query(self, message):
        self.query('DhwActive')

    @intent_handler( IntentBuilder('HpCompressorActive').build() )
    def handle_hp_compressor_active_query(self, message):
        self.query('HpCompressorActive')

    @intent_handler( IntentBuilder('HPPowerConsumptionToday').build() )
    def handle_hp_power_consumption_today_query(self, message):
        self.query('HPPowerConsumptionToday')

    @intent_handler( IntentBuilder('DhwPowerConsumptionToday').build() )
    def handle_dhw_power_consumption_today_query(self, message):
        self.query('DhwPowerConsumptionToday')

    @intent_handler( IntentBuilder('ChargerID').build() )
    def handle_charger_id_query(self, message):
        self.query('ChargerID')

    @intent_handler( IntentBuilder('ChargerChargeStatus').build() )
    def handle_charger_charge_status_query(self, message):
        self.query('ChargerChargeStatus')

    @intent_handler( IntentBuilder('ChargerCharged').build() )
    def handle_charger_charged_query(self, message):
        self.query('ChargerCharged')

    @intent_handler( IntentBuilder('ChargerEnergy').build() )
    def handle_charger_energy_query(self, message):
        self.query('ChargerEnergy')

    @intent_handler( IntentBuilder('GridPowerConsumptionToday').build() )
    def grid_power_consumption_today_query(self, message):
        self.query('GridPowerConsumptionToday')

    @intent_handler( IntentBuilder('GridPowerConsumptionTotal').build() )
    def grid_power_consumption_total_query(self, message):
        self.query('GridPowerConsumptionTotal')

    @intent_handler( IntentBuilder('GridPowerSupplyTotal').build() )
    def grid_power_supply_total_query(self, message):
        self.query('GridPowerSupplyTotal')

    @intent_handler( IntentBuilder('PVPowerProductionTotal').build() )
    def pv_power_production_total_query(self, message):
        self.query('PVPowerProductionTotal')

    @intent_handler( IntentBuilder('PVPowerProductionToday').build() )
    def pv_power_production_today_query(self, message):
        self.query('PVPowerProductionToday')

    @intent_handler( IntentBuilder('PVSocPercentageLoaded').build() )
    def pv_soc_percentage_loaded_query(self, message):
        self.query('PVSocPercentageLoaded')

    @intent_handler( IntentBuilder('GridPowerFeedInToday').build() )
    def grid_power_feedin_today_query(self, message):
        self.query('GridPowerFeedInToday')

    @intent_handler( IntentBuilder('OverallPowerConsumptionToday').build() )
    def overall_power_consumption_today_query(self, message):
        self.query('OverallPowerConsumptionToday')

    @intent_handler( IntentBuilder('OverallPowerAutonomyToday').build() )
    def overall_power_autonomy_today_query(self, message):
        self.query('OverallPowerAutonomyToday')

    @intent_handler( IntentBuilder('SummaryReport').build() )
    def summary_report_query(self, message):
        self.query('SummaryReport')

    @intent_handler( IntentBuilder('VehicleReport').build() )
    def vehicle_report_query(self, message):
        self.query('VehicleReport')

    @intent_handler( IntentBuilder('VehicleLeaseReport').build() )
    def vehicle_lease_report_query(self, message):
        self.query('VehicleLeaseReport')

    @intent_handler( IntentBuilder('ChargerReport').build() )
    def charger_report_query(self, message):
        self.query('ChargerReport')

    @intent_handler( IntentBuilder('HeatpumpReport').build() )
    def heatpump_report_query(self, message):
        self.query('HeatpumpReport')

    @intent_handler( IntentBuilder('GridReport').build() )
    def grid_report_query(self, message):
        self.query('GridReport')

    @intent_handler( IntentBuilder('PVReport').build() )
    def pv_report_query(self, message):
        self.query('PVReport')

    # trigger to play an mp3 file
    # the mp3 file will be selected ramdomly from a list of available files
    # the selected mp3 file is addressed via its URI file://<host>/<path>/<file>
    # player needs to be set in mycroft config: play_mp3_cmd = config.get("play_mp3_cmdline")
    # i.g. omxplayer file.mp3
    # TODO
    # DONE



    # trigger on user byebye intent anytime
    """
    def converse(self, message):
        self.log.info("executing converse()")
        #TypeError: 'NoneType' object is not subscriptable
        utt = normalize(message.data.get('utterances', "")[0].lower())
        self.log.info(" utterance= " + str(utt))
        #utt = normalize(message.data.get('utterance', "")[0].lower())
        #utt = normalize(message.data['utterances'][0]).lower()
        if self.voc_match(utt, 'byebye'):
        #this log will be written but it causes an exception
        #however this call of voc_match runs well, without an exception
        #if self.voc_match(normalize(message.data['utterances'][0]).lower(), 'byebye'):
            self.speak_dialog('byebye')
            return True
        return False
    """

    def stop(self):
        self.log.info("running stop()")
        pass


def create_skill():
    return TalkToMe()
