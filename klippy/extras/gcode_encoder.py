# Support for executing gcode when a hardware button is pressed or released.
#
# Copyright (C) 2019 Alec Plumb <alec@etherwalker.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

class GCodeEncoder:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split(' ')[-1]
        self.pin_button = config.get('pin_button')
        self.pin_a = config.get('pin_a')
        self.pin_b = config.get('pin_b')
        self.steps_per_detent = config.getint('steps_per_detent')
        self.last_state = 0
        buttons = self.printer.load_object(config, "buttons")

        buttons.register_buttons([self.pin_button], self.button_callback)
        buttons.register_rotary_encoder(self.pin_a, self.pin_b, self.cw_callback,
                                        self.ccw_callback, self.steps_per_detent)

        gcode_macro = self.printer.load_object(config, 'gcode_macro')
        self.cw_template = gcode_macro.load_template(config, 'cw_gcode')
        self.ccw_template = gcode_macro.load_template(config, 'ccw_gcode')
        self.press_template = gcode_macro.load_template(config, 'press_gcode')
        self.release_template = gcode_macro.load_template(config,
                                                          'release_gcode', '')
        self.gcode = self.printer.lookup_object('gcode')

    # cmd_QUERY_BUTTON_help = "Report on the state of a button"
    # def cmd_QUERY_BUTTON(self, gcmd):
    #     gcmd.respond_info(self.name + ": " + self.get_status()['state'])

    def button_callback(self, eventtime, state):
        self.last_state = state
        template = self.press_template
        if not state:
            template = self.release_template
        try:
            self.gcode.run_script(template.render())
        except:
            logging.exception("Script running error")

    def cw_callback(self, eventtime):
        template = self.cw_template
        try:
            self.gcode.run_script(template.render())
        except:
            logging.exception("Script running error")
    
    def ccw_callback(self, eventtime, state):
        self.last_state = state
        template = self.ccw_template
        try:
            self.gcode.run_script(template.render())
        except:
            logging.exception("Script running error")

    def get_status(self, eventtime=None):
        if self.last_state:
            return {'state': "PRESSED"}
        return {'state': "RELEASED"}

def load_config_prefix(config):
    return GCodeEncoder(config)
