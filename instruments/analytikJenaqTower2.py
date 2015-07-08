#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import numpy as np


class AnalytikJenaqTower2:

    def __init__(self):
        self.name = "Analytik Jena qTower 2.0/2.2"
        self.providesTempRange = False
        self.providesDeltaT = False

    def loadData(self, filename, reads, wells):
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
            i = 0
            for row in reader:
                temp = np.zeros(reads, dtype=float)
                for read in range(reads + 1):
                    if read > 0:
                        try:
                            temp[read - 1] = row[read]
                        except (IndexError, ValueError):
                            temp[read - 1] = 0.0
                    elif read == 0:
                        wells[i].name = row[read]
                wells[i].raw = temp
                i += 1
        return wells
