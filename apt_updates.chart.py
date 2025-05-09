# -*- coding: utf-8 -*-
# Description: apt updates netdata python.d module
# Author: Christian Hofstede (christian@hofstede.it)

import re
import os
from bases.FrameworkServices.ExecutableService import ExecutableService

# default module values (can be overridden per job in `config`)
update_every = 1800
priority = 60000
retries = 60
# set command: "/bin/false" in config to disable

# list of chart ids
ORDER = ['apt_updates']

CHARTS = {
    # id -> {options: [], lines: [[]]}
    'apt_updates': {
        # [name, title, units, family, context, charttype],
        'options': [None, "Available apt updates", "available updates", "updates", "apt-updates", "line"],
        'lines': [
            # [unique_dimension_name, name, algorithm, multiplier, divisor]
            ['apt_updates', None, 'absolute']
        ]}
}

class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.command = "apt-get -s upgrade"
        self.order = ORDER
        self.definitions = CHARTS
        # conf access: self.configuration.get('host', '127.0.0.1')

    def _get_data(self):
        """
        returns dict {unique_dimention_name -> value} or None
        """
        os.environ["LANG"] = "C"
        raw_data = self._get_raw_data()
        if not raw_data:
            return None
        # Find line in apt-get output that contains number of updates
        update_line = list(filter(lambda x: 'newly installed' in x, raw_data))
        if not update_line:
            return None
        # Get first field from line (seperated by ', ')
        nr_updates = update_line[0].split(', ')[0]
        if not nr_updates:
            return None
        # Return only the number of updates
        update_count = re.search("\\d+", nr_updates).group()
        updates = {'apt_updates': str(update_count)}
        self.debug("Found update count '{0}' in text '{1}'".format(update_count, update_line[0]))
        return updates
