# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

import numpy as np


class IRTECONAxis:
    def __init__(self, line: str = ''):
        self.name: str = ''
        self.unit: str = ''
        self.min: float = 0.
        self.max: float = 1.
        self.axis: int = 0

        if line:
            words = line.split()
            self.axis = int(words[0])
            self.min = float(words[1].replace(',', '.'))
            self.max = float(words[2].replace(',', '.'))
            if len(words) == 10:
                self.name = words[9]
            elif len(words) > 10:
                self.unit = words[9]
                self.name = ' '.join(words[10:])

    def __repr__(self):
        return 'IRTECONAxis(' + ', '.join(f'{key}={repr(value)}' for key, value in self.__dict__.items()) + ')'


class IRTECONCurve:
    def __init__(self):
        self.time: datetime = datetime.fromtimestamp(0)
        self.duration: float = 0.
        self.legend_key: str = ''
        self.data: np.ndarray = np.empty(0)

    def __repr__(self):
        return 'IRTECONCurve(' + ', '.join(f'{key}={repr(value)}' for key, value in self.__dict__.items()) + ')'


def parse_date(date: str) -> datetime:
    hour: int
    minute: int
    second: int
    day: int
    month: int
    year: int
    time, date = date.split(maxsplit=1)
    hour, minute, second = tuple(map(int, time.split(':')))
    day_str, month_str, year_str = date.split('-')
    day, year = tuple(map(int, (day_str, year_str)))
    month = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec').index(month_str) + 1
    return datetime(year, month, day, hour, minute, second)


class IRTECONFile:
    def __init__(self, file_content: str = ''):

        self.program: str = ''
        self.configuration_file: str = ''
        self.sample_name: str = ''
        self.axes: List[IRTECONAxis] = []
        self.curves: List[IRTECONCurve] = []

        if file_content:
            axis_description_found: bool = False
            curve_found: bool = False
            curve_data: List[np.ndarray] = []
            curve_data_found: bool = False
            for line in file_content.splitlines():
                if not axis_description_found and not curve_found and line.startswith(' Program     :'):
                    self.program = line[14:]
                elif not axis_description_found and not curve_found and line.startswith(' Config      :'):
                    self.configuration_file = line[14:]
                elif not axis_description_found and not curve_found and line.startswith(' Sample name :'):
                    self.sample_name = line[14:]
                elif axis_description_found and line == '#END axis description':
                    axis_description_found = False
                elif curve_found and line.startswith('#END Curve ') and line.endswith('-' * 16):
                    curve_found = False
                    curve_data_found = False
                    if curve_data:
                        self.curves[-1].data = np.array(curve_data)
                elif axis_description_found and line.startswith('  '):
                    self.axes.append(IRTECONAxis(line))
                elif curve_data_found:
                    curve_data.append(np.array(list(map(float, line.replace(',', '.').split()))))
                elif not axis_description_found and not curve_found and line == '#START axis description':
                    axis_description_found = True
                elif not axis_description_found and not curve_found and line.startswith('#START Curve description '):
                    self.curves.append(IRTECONCurve())
                    curve_found = True
                    curve_data = []
                elif curve_found and line.startswith('#START Date:'):
                    self.curves[-1].time = parse_date(line[12:])
                elif curve_found and line.startswith('#START Time:'):
                    self.curves[-1].duration = sum(float(x.replace(',', '.')) * (2 * i - 1)
                                                   for i, x in enumerate(line[12:].split(maxsplit=1)))
                elif curve_found and line.startswith('#START Curve Legend '):
                    self.curves[-1].legend_key = line.split(':', maxsplit=1)[-1]
                elif curve_found and line == '#START Curve Data':
                    curve_data_found = True
