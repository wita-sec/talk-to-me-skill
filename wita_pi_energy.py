#!/usr/bin/python

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


"""energy data provider for the Picroft talk-to-me skill
   data provided are used by the Pi skill to inform about WITA PV and HP measures
   data is retrieved from json files which are expected to be avaliable in the
   energy-files folder of the skill
"""

################################################################################
#
#  changelog
#  pvm_version = "1.0/10/20230110"
#  initial version
#
#
################################################################################
pvm_version = "1.1/10/20230123"

import sys
import os
from os.path import exists
from os.path import abspath
import datetime
import time
import json
import pwd
from pprint import pprint

################################################################################
class pi_energy:
    """ purpose of this class is to answer queries about items in json files
        json files are provided in the the  path_to_energy_files folder.
        They include items about WITA Energy.
        The concept is open for any other items in any other json files.
    """
    ############################################################################
    def __init__(self, path_to_energy_files):
        user = pwd.getpwuid( os.getuid() ).pw_name
        self.path_to_energy_files = path_to_energy_files
        self.user = user

        j_dict = {} # empty json dict to initialie json_files hash
        mod_time = 0
        self.json_files = {
        # hash of index to jfile_ctl: (json filename, json load dict, and file modification time.
        #                              if file modification time is 0, jfile was not loaded yet
        #   index  JSON-File-Type   json filename      json dict, jfile modification time
        #
            "1" : ["HPH", "hpm-out-header.json",       j_dict, mod_time],
            "2" : ["HPS", "hpm-out-shortterm.json",    j_dict, mod_time],
            "3" : ["HPP", "hpm-out-longterm.json",     j_dict, mod_time],
            "4" : ["PVM", "pv_meter.json",             j_dict, mod_time],
            "5" : ["PVT", "pvm-out-meter-total.json",  j_dict, mod_time],
            "6" : ["CH",  "charger.json",              j_dict, mod_time],
            "7" : ["V",   "vehicle.json",              j_dict, mod_time],
            }
        # JSON-File-Type: points to the structure of the respective json file
        #                 HPH, HPS, HPP, PVM, PVT, CH, V
        #
        # this hash maps ENU et al vocs to DE vocs
        self.TTS_dict = {
            "degree"    : "Grad",
            "kWh"       : "Kilowattstunden",
            "%%Tactive" : "aktiv",
            "%%Factive" : "nicht aktiv",
            "%%Twork"   : "läuft zur Zeit",
            "%%Fwork"   : "läuft zur Zeit nicht",
            "%%Pload"   : "bezogen",
            "%%Nload"   : "nicht bezogen sondern eingespeist",
            "%%Pcons"   : "verbraucht",
            "%%Ncons"   : "nicht verbraucht sondern eingespeist",
            "C"         : "ein Fahrzeug verbunden und wird geladen",
            "A"         : "kein Fahrzeug verbunden",
            "B"         : "ein Fahrzeug verbunden. Es wird aber nicht geladen",
            "%"         : "Prozent",
            "km"        : "Kilometern",

        }
        # TTS variable format:  as used in pi_query_items (below)
        #   if empty, the DY text in the json file is used
        #   placeholders:
        #      $$V for value,
        #      %%U for unit,
        #      %%<voc>,
        #        for bool units the dict includes a T_<voc> and a F_<voc> entry
        #
        #  any %%___ vocs must have a translation in self.dict

        # this hash provides all items that can be queried
        self.pi_query_items = {
            # searchkey that is looked up in json file
            #   |            self.json_files index
            #   |            |      TTS template
            #   |            |      |  if empty, the DY text in the json file is used

            #   placeholders in TTS template:
            #        $$V for value, ENU 12,345.67 is mapped to 12345,67
            #        %%U for unit,  gets translated via self.TTS_dict
            #                       thereby bool %%B<voc> is mapped to %%T<voc> for true, %%F<voc> for false
            #        %%T for value  gets translated via self.TTS_dict, example: %%T value C --> charging / wird geladen



            ### items for json type HPP HPS HPP
            "outdoor":    ( "3", "Die Aussentemperatur beträgt $$V %%U"),
            "dhw_active": ( "2", "Der Warmwasserkreislauf ist %%Bactive"),
            "compressor_active": ( "3", "Der Kompressor der Wärmepumpe %%Bwork"),
            "power_input_total_today": ("3", "Die Wärmepumpe hat heute $$V %%U verbraucht"),
            "power_input_dhw_today": ("3", "Für Warmwasser wurden heute $$V %%U verbraucht"),
            ### items for json type PVT

            ### items for json type CH
            "charger Identifier": ("6", "Die Seriennummer der Wallbox lautet $$V, bitte auswendig lernen"),
            "charger Charge status": ("6", "Mit der Wallbox ist zur Zeit $$T"),
            "charger Charged": ("6", "Beim letzten Ladevorgang hat die Wallbox $$V %%U geladen"),
            "charger Energy": ("6", "Über alle Ladevorgänge hat die Wallbox bis heute $$V %%U geladen"),

            ### items json type V
            "vehicle Odometer": ("7", "Das Auto hat eine Kilometerleistung von $$V %%U erreicht"),
            "vehicle Soc": ("7", "Die Batterie des Fahrzeugs ist zu $$V %%U geladen"),
            "vehicle Range": ("7", "Das Fahrzeug hat eine aktuelle Reichweite von $$V %%U"),

            ### items json type PVM ($$Sload: $$V >= 0: geladen, $$V < 0: eingespeist)
            "netzbezug-aktuell Energy": ("4", "Aktueller Energie Netzbezug ist $$V %%U Strom %%Sload"),
            "netzeinspeisung-total Energy": ("4", "Bisher wurden insgesamt $$V %%U Strom eingespeist"),
            "pv-total Energy": ("4", "Die Photovoltaik hat insgesamt bisher $$V %%U Strom erzeugt"),
            "netzbezug-total Energy": ("4", "Es wurden bisher insgesamt $$V %%U Strom aus dem Netz bezogen"),
            "pv-aktuell Energy": ("4", "Photovoltaik aktuell Enerie ist $$V %%U Strom"),
            "stromspeicher Soc": ("4", "Die Stromspeicher ist aktuell zu $$V %%U gefüllt"),
            }

            # This hash is a patch for self.pi_query_items
            # Note: most search items are mapped 1:1 and can be handled with
            #       self.pi_query_items
            #       however there are some exceptions that require this kind of a patch
            #       The reason is that there are different json files which have the same
            #       search key, but with different meaning. So we need to map some items to
            #       their appropriate search keys and json files
        self.pi_query_items_patch = {
            # search item exposed by Picroft  search key in json         file
            "netzbezug-total Energy_Today": ("netzbezug-total Energy", ("5", "Heute wurden bisher $$V %%U Strom %%Sload")),
            "netzeinspeisung-total Energy_Today": ("netzeinspeisung-total Energy", ("5", "Heute wurden bisher $$V %%U Strom in das Netz eingespeist")),
            "pv-total Energy_Today":        ("pv-total Energy", ("5", "Die Photovoltaik hat heute bisher $$V %%U Strom erzeugt")),

            }

        # This hash controls query items that cannot be answered 1:1 by WITA_energy
        # json files. They rather are the result of specific calculations by functions
        # However the values of the json files are the basis for these calculations
        self.pi_query_items_functions = {
            # search item                function                       unit   TTS template
            #   how much energy was consumed today (including pv and grid)?
            "energy_consumption_today": (self.calc_energy_consumption, ("kWh", "In der Energiebilanz wurden heute $$V %%U Strom %%Scons")),
            #   what is the degree of autonomy today
            "energy_autonomy_today":    (self.calc_autonomy_degree,    ("%",   "Der Autonomiegrad in der Energiebilanz heute beträgt $$V %%U")),
        }

        # These lists  provide queries (pi_query_items, pi_query_items_patch, pi_query_items_functions)
        # that are bundled to specific reports
        #    summary report
        self.pi_query_report_summary = [
            "outdoor",
            "energy_consumption_today",
            "pv-total Energy_Today",
            "energy_autonomy_today",
            "netzeinspeisung-total Energy_Today",
            "netzbezug-total Energy_Today",
            "power_input_total_today",
            "power_input_dhw_today",
            "charger Energy",
            "charger Charge status",
            "charger Charged",
            "vehicle Odometer",
            "vehicle Range",
        ]
        #    vehicle report
        self.pi_query_report_vehicle = [
            "vehicle Odometer",
            "vehicle Soc",
            "vehicle Range",
        ]
        #    charger report
        self.pi_query_report_charger = [
            "charger Identifier",
            "charger Energy",
            "charger Charge status",
            "charger Charged",
        ]
        #    heatpump report
        self.pi_query_report_heatpump = [
            "outdoor",
            "power_input_total_today",
            "power_input_dhw_today",
            "compressor_active",
            "dhw_active",
        ]
        #    grid report
        self.pi_query_report_grid = [
            "energy_consumption_today",
            "energy_autonomy_today",
            "netzbezug-total Energy_Today",
            "netzeinspeisung-total Energy_Today",
            "netzbezug-total Energy",
            "netzeinspeisung-total Energy",
        ]
        #    photovoltaik report
        self.pi_query_report_pv = [
            "pv-total Energy_Today",
            "stromspeicher Soc",
            "energy_autonomy_today",
        ]
        # This hash controls the Energy Reports
        self.pi_query_items_reports = {
            # report name    pointer to the list of report items
            "summary":      (self.pi_query_report_summary),
            "vehicle":      (self.pi_query_report_vehicle),
            "charger":      (self.pi_query_report_charger),
            "heatpump":     (self.pi_query_report_heatpump),
            "grid":         (self.pi_query_report_grid),
            "photovoltaik": (self.pi_query_report_pv),
        }


    #############################################
    def calc_energy_consumption(self):
        """ calculate energy consumption of the current day
            energy_consumption today is:
                 + PV Production today      --> pv-total Energy_Today (self.pi_query_items)
                 + Grid consumption today   --> netzbezug-total Energy_Today (self.pi_query_items_patch)
                 - Grid feed-in today       --> netzeinspeisung-total Energy_Today  (self.pi_query_items_patch)
        """
        fct = " pi_energy.calc_energy_consumption() "
        rc = 0
        rc_msg = "success"
        r_value = 42
        # retrive required basic measures
        r_1, r_msg_1, r_unit_1, r_value_1, r_descr_1, r_tts_1 = self.query_item("pv-total Energy_Today")
        r_2, r_msg_2, r_unit_2, r_value_2, r_descr_2, r_tts_2 = self.query_item("netzbezug-total Energy_Today")
        r_3, r_msg_3, r_unit_3, r_value_3, r_descr_3, r_tts_3 = self.query_item("netzeinspeisung-total Energy_Today")
        if r_1 == 0 and r_2 == 0 and r_3 == 0:
            if self.is_float(r_1) and self.is_float(r_2) and self.is_float(r_3):
                r_value = float(r_value_1) + float(r_value_2) - float(r_value_3)
            else:
                rc_msg = fct + " failed, at least one of the basic measures retrieved is not a float! "
                rc = 1
        else:
            rc_msg = fct + " failed by " + str(r_1) + " " + r_msg_1 + str(r_2) + " " + r_msg_2 + str(r_3) + " " + r_msg_3 + "!"
            rc = 2
        #print(fct + " r_value=" + str(r_value))
        return rc, rc_msg, str(r_value)

    #############################################
    def calc_autonomy_degree(self):
        """ calculate degree of autonomy for the current day
            automomy_degree is:
                energy_consumption = PV production + Grid import - Grid feed-in
                Eigenverbrauch     = PV production - Grid feed-in
                autonomy_degree    = Eigenverbrauch/energy_consumption *100
        """
        fct = " pi_energy.calc_autonomy_degree() "
        rc = 0
        rc_msg = "success"
        r_value = 42
        # retrive required basic measures
        r_1, r_msg_1, r_unit_1, r_value_1, r_descr_1, r_tts_1 = self.query_item("pv-total Energy_Today")
        r_2, r_msg_2,           r_value_2                     = self.calc_energy_consumption()
        r_3, r_msg_3, r_unit_3, r_value_3, r_descr_3, r_tts_1 = self.query_item("netzeinspeisung-total Energy_Today")
        if r_1 == 0 and r_2 == 0 and r_3 == 0:
            if self.is_float(r_1) and self.is_float(r_2) and self.is_float(r_3):
                r_value = round((float(r_value_1) - float(r_value_3)) / float(r_value_2) *100, 2)
            else:
                rc_msg = fct + " failed, at least one of the basic measures retrieved is not a float!"
                rc = 1
        else:
            rc_msg = fct + " failed by " + str(r_1) + " " + r_msg_1 + str(r_2) + " " + r_msg_2 + str(r_3) + " " + r_msg_3 + "!"
            rc = 2
        #print(fct + " r_value=" + str(r_value))
        return rc, rc_msg, str(r_value)

    ############################################################################
    def load_json_files(self):
        fct = " pi_energy.load_json_files() "
        for index, jfile_ctl in self.json_files.items():
            path_to_file = self.path_to_energy_files + '/' + jfile_ctl[1]
            if os.path.isfile(path_to_file):
                # jfile exists
                jfile_mtime = os.stat(path_to_file).st_mtime
                if not jfile_ctl[3] == jfile_mtime:
                    #jfile modification time is different to last load, or jfile was not yet loaded
                    with open(path_to_file) as j_handle:
                        jfile_ctl[2] = json.load(j_handle)
                        jfile_ctl[3] = jfile_mtime
                        j_handle.close()
                        #print('\n')
                        #print(fct + " json file loaded: " + jfile_ctl[0])
            else:
                print(fct + " json file could not be loaded: " + jfile_ctl[1])
        #print('\n')
        #print(fct + " json_files hash: \n")
        #pprint(self.json_files)

    ############################################################################
    def lookup_PV_item(self, item_key, jdict):
        fct = " pi_energy.lookup_PV_item() "
        rc = 1
        rc_m = fct + " item " + item_key + " not found!"
        unit = ""
        value = ""
        descr = ""
        key1, key2 = item_key.split()
        for index, pv_ctl in jdict.items():
            if pv_ctl[0] == key1 and pv_ctl[1] == key2:
                unit = pv_ctl[2]
                value = pv_ctl[3]
                desc = pv_ctl[0] + ' ' + pv_ctl[1]
                rc = 0
                rc_m = fct + " success!"
        return rc, rc_m, unit, value, descr

    ############################################################################
    def lookup_HP_item(self, item_key, jdict):
        fct = " pi_energy.lookup_HP_item() "
        rc = 1
        rc_m = fct  +" item " + item_key + " not found!"
        unit = ""
        value = ""
        descr = ""
        if item_key in jdict:
            item = jdict[item_key]
            unit = item[0]
            value = item[1]
            descr = item[2]
            rc = 0
            rc_m = fct + " success!"
        return rc, rc_m, unit, value, descr

    ############################################################################
    def lookup_V_item(self, item_key, jdict):
        fct = " pi_energy.lookup_V_item() "
        rc = 1
        rc_m = fct + " item " + item_key + " not found!"
        unit = ""
        unit = ""
        value = ""
        descr = ""
        key1, key2 = item_key.split(' ', 1)
        for index, v_ctl in jdict.items():
            if v_ctl[0] == key1 and v_ctl[1] == key2:
                unit = v_ctl[2]
                value = v_ctl[3]
                desc = v_ctl[0] + ' ' + v_ctl[1]
                rc = 0
                rc_m = fct + " success!"
        return rc, rc_m, unit, value, descr

    ############################################################################
    def lookup_CH_item(self, item_key, jdict):
        fct = " pi_energy.lookup_CH_item() "
        rc = 1
        rc_m = fct + " item " + item_key + " not found!"
        unit = ""
        unit = ""
        unit = ""
        value = ""
        descr = ""
        #print("lookup_CH_item " + item_key)
        #pprint(jdict)
        key1, key2 = item_key.split(' ', 1)
        for index, ch_ctl in jdict.items():
            if ch_ctl[0] == key1 and ch_ctl[1] == key2:
                unit = ch_ctl[2]
                value = ch_ctl[3]
                desc = ch_ctl[0] + ' ' + ch_ctl[1]
                rc = 0
                rc_m = fct + " success!"
        return rc, rc_m, unit, value, descr

    ############################################################################
    def lookup_item(self, item_key, jtype, jdict):
        """ lookup item_key in json dictionary jdict and return parameters
                unit, value, description
            jtype specifies the type of the dict:  HPH, HPS, HPP, PVM, PVT, CH, V
            searching item_key and retrieving parameters depends on the jtype

            return: rc:      return code 0=ok else error
                    rc_m:    return message
                    unit:    unit of the searched item
                    value:   value of the searched item
                    descr:   description of the searched item
        """
        fct = " pi_energy.lookup_item() "
        rc = 0
        rc_m = fct + " success!"
        unit = ""
        value = ""
        descr = ""

        if jtype == "PVT" or jtype == "PVM":
            rc, rc_m, unit, value, descr = self.lookup_PV_item(item_key, jdict)
        elif jtype == "CH":
            rc, rc_m, unit, value, descr = self.lookup_CH_item(item_key, jdict)
        elif jtype == "V":
            rc, rc_m, unit, value, descr = self.lookup_V_item(item_key, jdict)
        elif jtype == "HPH" or jtype == "HPS" or jtype == "HPP":
            rc, rc_m, unit, value, descr = self.lookup_HP_item(item_key, jdict)
        else:
            rc = 99
            rc_m = fct + " invalid jtype " + jtype + " !"
        return rc, rc_m, unit, value, descr

    ############################################################################

    def is_float(self, value):
        if value is None:
            return False
        try:
            float(value)
            return True
        except:
            return False

    ############################################################################
    def markup_item(self, TTS_template, unit, value, description):
        """ markup a TTS_template for TTS speach output.
            unit, value, description are formatted into the TTS_template
            template examples:
                "Die Aussentemperatur beträgt $$V %%U"
                "Der Warmwasserkreislauf ist %%Bactive"
                "Das Auto wird %%Bloaded"
                 $$V is a placeholder for value,
                 %%U is a placeholder for unit,  as a %% placeholder it needs translation via the self.TTS_dict
                 %%Bactive and %%Bloaded are placeholders for bool values, they needs tranlation:
                         look for %%Tactive resp. %%Factive in the self.TTS_dict and  for
                                  %%Tloaded resp. %%Floaded
                 NOTE: per TTS_template at most one $$V, one %%U and one %%Bxxx placeholder is supported

            return: r = 0 ok, else error,
                    rc_m return message,
                    rc_TTS = TTS-ready speach output
        """
        fct = " pi_energy.markup_item() "
        r = 0
        rc_msg = fct + " success!"
        rc_TTS = ""
        rc_TTS = TTS_template

        if self.is_float(str(value)):
            v = round(float(str(value)), 2)
            value = str(v)
        index = rc_TTS.find('$$V')
        if index != -1:
            index2 = rc_TTS.find('%%S')
            if index2 != -1:
                # markup verb for a signed (positiv/negative) value rc_TTS string
                terms = rc_TTS[index2+3:].split(' ', 1)
                if self.is_float(str(value)):
                    if float(str(value)) >= 0:
                        tmp1 = '%%P' + terms[0]
                    else:
                        tmp1 = '%%N' + terms[0]
                        # value is negativ, switch to positiv
                        v = float(str(value))
                        value = str(-v)
                    if tmp1 in self.TTS_dict:
                        term_translated = self.TTS_dict[tmp1]
                        rc_TTS = rc_TTS.replace('%%S'+ terms[0], term_translated)
                    else:
                        rc_TTS = rc_TTS.replace('%%S'+ terms[0], terms[0])
            # markup value in rc_TTS string
            value = str(value).replace(',', '')
            value = str(value).replace('.', ',')
            rc_TTS = rc_TTS.replace('$$V', value)

        index = rc_TTS.find('$$T')
        if index != -1:
            # markup translatable value in rc_TTS string
            if value in self.TTS_dict:
                value_translated = self.TTS_dict[value]
                rc_TTS = rc_TTS.replace('$$T', value_translated)
            else:
                rc_TTS = rc_TTS.replace('$$T', value)

        index = rc_TTS.find('%%U')
        if index != -1:
            # markup unit in rc_TTS string
            if unit in self.TTS_dict:
                unit_translated = self.TTS_dict[unit]
                rc_TTS = rc_TTS.replace('%%U', unit_translated)
            else:
                rc_TTS = rc_TTS.replace('%%U', unit)

        index = rc_TTS.find('%%B')
        if index != -1:
            # markup bool expression in rc_TTS string
            terms = rc_TTS[index+3:].split(' ', 1)
            if str(value) == 'true':
                tmp1 = '%%T' + terms[0]
            else:
                tmp1 = '%%F' + terms[0]
            if tmp1 in self.TTS_dict:
                term_translated = self.TTS_dict[tmp1]
                rc_TTS = rc_TTS.replace('%%B'+ terms[0], term_translated)
            else:
                rc_TTS = rc_TTS.replace('%%B'+ terms[0], terms[0])

        return r, rc_msg, rc_TTS

    ############################################################################
    def query_report(self, report):
        """ report about several energy items.
            "report" points to a list of item to be reported.
        """
        fct = " pi_energy.query_report() "
        rc = 0
        rc_msg = fct + "success!"
        rc_TTS_array = []
        if report in self.pi_query_items_reports:
            report_ctl = self.pi_query_items_reports[report]
            for item in report_ctl:
                r_c = 0
                if item in self.pi_query_items_functions:
                    pi_query_fct_ctrl = self.pi_query_items_functions[item]
                    r_tts_template = pi_query_fct_ctrl[1][1]
                    r_unit = pi_query_fct_ctrl[1][0]
                    r_descr = ""
                    r_c, rc_m, r_value = pi_query_fct_ctrl[0]()
                else:
                    r_c, r_msg, r_unit, r_value, r_descr, r_tts_template = self.query_item(item)

                if r_c == 0:
                    # markup answer TTS
                    #                                     TTS_template,     unit, value, description
                    r_c, r_msg, rc_TTS = self.markup_item(r_tts_template, r_unit, r_value, r_descr)
                    rc_TTS_array.append(rc_TTS)
                #else:
                #    print(fct + " could not find item " + item + " for report " + report)
        else:
            rc = 1
            rc_msg = fct + " rc= " + str(rc) + " requested report is not available!"
        return rc, rc_msg, rc_TTS_array

    ############################################################################
    def query_item(self, item):
        """ search item in json files and return its value, unit and description
            searched item must be one of self.pi_query_items or self.pi_query_items_patch
            return rc = 0 ok, else error
                   rc_msg return message
                   r_unit unit of the item
                   r_value value of the item (as string)
                   r_descr of the item
                   r_tts_template  template for the text to speach output
        """
        fct = " pi_energy.query_item() "
        rc = 0
        rc_msg = fct + " success!"
        r_unit = "None"
        r_value = 42
        r_descr = "None"
        pi_query_ctrl = None
        r_tts_template = " "
        # lookup requested item in "patch" hash pi_query_items_patch
        if item in self.pi_query_items_patch:
            pi_query_ctrl = self.pi_query_items_patch[item][1]
            search_item = self.pi_query_items_patch[item][0]
        else:
            # lookup requested item in pi_query_items and according json file
            if item in self.pi_query_items:
                # example: "outdoor": ( "3", "Die Aussentemperatur beträgt $$V %%U"),
                # item exists
                pi_query_ctrl = self.pi_query_items[item]
                search_item = item
            # get item measures from according json file
        if pi_query_ctrl != None:
            r_tts_template = pi_query_ctrl[1]
            if pi_query_ctrl[0] in self.json_files:
                jfile_ctl = self.json_files[pi_query_ctrl[0]]
                if jfile_ctl[3] != 0:
                    # json file was loaded
                    # lookup item in json dict (jfile_ctl[2]) and return parameters
                    #                                              item,        jtype,        jdict
                    r, rc_m, unit, value, descr = self.lookup_item(search_item, jfile_ctl[0], jfile_ctl[2])
                    if r == 0:
                        r_unit = unit
                        r_value = value
                        r_desc = descr
                    else:
                        rc = 1
                        rc_msg = fct + " cannot retriev item: lookup_item failed by rc=" + str(r) + " rc_msg=" + rc_m + "!"
                else:
                    rc = 2
                    rc_msg = fct + " cannot retriev item: json file was not loaded!"
            else:
                rc = 3
                rc_msg = fct + " cannot retriev item: programming error!"
        else:
            rc = 4
            rc_msg = fct + " item " + item + " not found in pi_query_items or pi_query_items_patch!"
        return rc, rc_msg, r_unit, str(r_value), r_descr, r_tts_template

    ############################################################################
    def query(self, item):
        """ search item in json files and markup an according answer TTS (text-to-speach) for Picroft
            return: rc = 0, ok else error
                    rc_msg  return message
                    rc_TTS  single text-to-speech answer to the query or
                    rc_TTS_array an array of answers
        """
        fct = " pi_energy.query() "
        rc = 1
        rc_msg = fct + " success!"
        rc_TTS = ""
        rc_TTS_array = []

        # load json files that have not been loaded yet or have been updated since last query
        self.load_json_files()

        # lookup requested item in "reports" hash pi_query_items_reports
        if item in self.pi_query_items_reports:
            rc, rc_msg, rc_TTS_array = self.query_report(item)
            return rc, rc_msg, rc_TTS_array

        # lookup requested item in "functional" hash pi_query_items_functions
        if item in self.pi_query_items_functions:
            pi_query_fct_ctrl = self.pi_query_items_functions[item]
            r, rc_m, r_value = pi_query_fct_ctrl[0]()
            if r != 0:
                rc_msg = fct + " cannot calculate item: " + item + " function failed by rc=" + str(r) + " rc_msg= " + rc_m + "!"
            else:
                #                                  TTS template             unit                     value    descr
                r, rc_m, rc_TTS = self.markup_item(pi_query_fct_ctrl[1][1], pi_query_fct_ctrl[1][0], r_value, rc_m)
                if r != 0:
                    rc_msg = fct + " cannot markup calculated item " + " markup failed by rc=" + str(r) + " rc_msg= " + rc_m + "!"
                else:
                    rc = 0
            return rc, rc_msg, rc_TTS

        # lookup requested item in pi_query_items and pi_query_items_patch
        r, r_msg, r_unit, r_value, r_descr, r_tts_template = self.query_item(item)
        if r != 0:
            rc_msg = fct + " cannot retriev item: query_item failed by rc= " + str(r) + " r_msg= " + r_msg + "!"
        else:
            # markup answer TTS
            #                                  TTS_template,     unit, value, description
            r, rc_m, rc_TTS = self.markup_item(r_tts_template, r_unit, r_value, r_descr)
            if r != 0:
                rc_msg = fct + " cannot markup item " + rc_m + "!"
            else:
                rc = 0
        # return results
        return rc, rc_msg, rc_TTS

# class  pi_energy
###############################################################################
# here starts main program (for testing)

if __name__ == "__main__":

    """ __main__ is used for testing
        __main__ takes following arguments:
          TODO

    """

    def print_help():
        print("wita_pi_energy help:\n")
        h1  = "wita_pi_energy.py -h | --help"
        h2  = "                  -p | --path <path> absolute path to energy files (json)"
        h21 = "                         default: /opt/mycroft/skills/talk-to-me-skill/energy-files"
        h3  = "                  -q | --query <query> ask for a WITA Energy item "
        h31 = "                         default: outdoor "
        h32 = "                         -q AUTOTEST runs all supported queries"
        h33 = "                         -q summary creates a summary report "
        h99 = "wita_pi_energy.py version is: " + pvm_version
        print(h1)
        print(h2)
        print(h21)
        print(h3)
        print(h31)
        print(h32)
        print(h33)
        print(h99)
        print("\n")

        # list of queries for automated testing
    test_queries = [
            "outdoor",
            "dhw_active",
            "compressor_active",
            "power_input_total_today",
            "power_input_dhw_today",
            "charger Identifier",
            "charger Charge status",
            "charger Charged",
            "charger Energy",
            "vehicle Odometer",
            "vehicle Soc",
            "vehicle Range",
            "netzbezug-total Energy",
            "netzbezug-total Energy_Today",
            "netzeinspeisung-total Energy",
            "netzeinspeisung-total Energy_Today",
            "pv-total Energy",
            "pv-total Energy_Today",
            "netzbezug-aktuell Energy",
            "pv-aktuell Energy",
            "stromspeicher Soc",
            "energy_consumption_today",
            "energy_autonomy_today",
            "summary", # summary report about energy items
            "vehicle", # vehicle report
            "charger", # charger report
            "heatpump",# heatpump report
            "grid",    # grid report
            "photovoltaik", # photovoltaik report
        ]

    import traceback

    def print_TTS(tts):
        #pprint(tts)
        #if isinstance(tts, collections.abc.Sequence):
        if isinstance(tts, list):
            # tts is an array of TTS
            for t in tts:
                print(t)
        else:
            print(tts)

    try:
        # default path
        path_to_energy_files = "/opt/mycroft/skills/talk-to-me-skill/energy-files"
        query = "outdoor"
        for i in range(len(sys.argv)):
            if sys.argv[i] == "-h" or sys.argv[i] == "--help" or sys.argv[i] == "-?":
                print_help()
                os._exit(1)
            if sys.argv[i] == "-p" or sys.argv[i] == "--path":
                path_to_energy_files = sys.argv[i+1]
            if sys.argv[i] == "-q" or sys.argv[i] == "--query":
                query = sys.argv[i+1]

        print("\nwita_pi_energy: launching query " + query + " \n     for path_to_energy_files " + path_to_energy_files + "\n")

        pi_e = pi_energy(path_to_energy_files)

        if query == "AUTOTEST":
            for query in test_queries:
                rc, rc_msg, rc_TTS = pi_e.query(query)
                print ("\n")
                print (query + ": pi_e.query() " + "rc= " + str(rc) + " rc_msg= " + rc_msg + "\n ")
                print_TTS(rc_TTS)
        else:
            rc, rc_msg, rc_TTS = pi_e.query(query)
            print ("\n")
            print (query + ": pi_e.query() " + "rc= " + str(rc) + " rc_msg= " + rc_msg + "\n")
            print_TTS(rc_TTS)

    except:
        tb = traceback.format_exc()
        print("\nexception caught at", str(datetime.datetime.now()), tb)
