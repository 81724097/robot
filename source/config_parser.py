#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser

def ReadConfig(config_file):
    try:
        config_reader = ConfigParser.ConfigParser()
        config_reader.read(config_file)
        config_dict = {}
        for section in config_reader.sections():
            config_dict[section] = {}
            for option in config_reader.options(section):
                value = config_reader.get(section, option)
                config_dict[section][option] = value
        return config_dict
    except Exception,e:
        print "Read config file exception:[%s]" % str(e)
        return {}
