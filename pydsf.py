#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import csv

try:
    import matplotlib as mpl

    mpl.use('Qt5Agg')
    import matplotlib.ticker as ticker
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    raise ImportError('----- Matplotlib must be installed. -----')

try:
    import peakutils
except ImportError:
    raise ImportError('----- PeakUtils must be installed. -----')

try:
    import numpy as np
except ImportError:
    raise ImportError('----- NumPy must be installed. -----')

try:
    from scipy.signal import filtfilt, butter, find_peaks_cwt
    from scipy import interpolate
except ImportError:
    raise ImportError('----- SciPy must be installed. -----')


class Well:
    def __init__(self, owner):
        self.owner = owner
        self.name = None
        self.raw = np.zeros(self.owner.reads, dtype=np.float)
        self.filtered = np.zeros(self.owner.reads, dtype=np.float)
        self.derivatives = np.zeros((4, self.owner.reads))
        self.splines = {"raw": None,
                        "filtered": None,
                        "derivative1": None}
        self.tm = np.NaN
        self.tm_sd = np.NaN
        self.baseline_correction = owner.baseline_correction
        self.baseline = None

    def filter_raw(self):
        """
        Apply a filter to the raw data
        """
        b, a = butter(3, 0.3)
        self.filtered = filtfilt(b, a, self.raw)

    def calc_spline(self, y):
        """
        Calculate a spline that represents the smoothed data points
        """
        spline = interpolate.InterpolatedUnivariateSpline(self.owner.temprange, y)
        return spline

    def calc_derivatives(self, spline='filtered'):
        for t in self.owner.temprange:
            temp = self.splines[spline].derivatives(t)
            for i in range(4):
                self.derivatives[i, t - self.owner.t1] = temp[i]

    @staticmethod
    def calc_baseline(y):
        try:
            baseline = peakutils.baseline(y)
            return baseline
        except:
            return np.NaN

    def calc_tm(self):
        """
        Calculate the Tm of the well. Returns either the Tm or 'np.NaN'.
        """
        # Check if the well has already been flagged as denatured
        if self in self.owner.denatured_wells:
            return np.NaN  # Return 'NaN' if true

        # First assume that the well is denatured
        self.owner.denatured_wells.append(self)

        if self.owner.tm_cutoff_low != self.owner.t1 or self.owner.tm_cutoff_high != self.owner.t1:
            x = np.arange(self.owner.tm_cutoff_low, self.owner.tm_cutoff_high + 1, self.owner.dt, dtype=np.dtype(np.float))

        x = self.owner.temprange
        y = self.derivatives[1]

        if self.baseline_correction:
            y = y - self.baseline

        try:
            peak_indexes = peakutils.indexes(y, thres=0.3)

            # loop over results to find maximum value for peak candidates
            max_y = None
            max_i = None
            for peak in peak_indexes:
                if not max_y or y[peak] > max_y:
                    max_y = y[peak]
                    max_i = peak

            if y[max_i] > 0: # if value of second derivative is positive, choose identified position as peak candidate
                tm = x[max_i]
            else:
                return np.NaN # else discard
        except:
            return np.NaN  # In case of error, return no peak

        try:
            if tm and tm >= self.owner.tm_cutoff_low and tm <= self.owner.tm_cutoff_high:
                tm = round(peakutils.interpolate(x, y, width=3, ind=[max_i])[0], 2)
                self.owner.denatured_wells.remove(self)  # If everything is fine, remove the denatured flag
                return tm  # and return the Tm
            else:
                return np.NaN  # otherwise, return NaN
        except:
            return np.NaN  # In case of error, return NaN

    def is_denatured(self):
        """
        Check if the well is denatured. Returns true if the well has been already flagged as
        denatured, no Tm was found, or if the initial signal intensity is above a user definded
        threshold.
        """
        denatured = True  # Assumption is that the well is denatured

        if self in self.owner.denatured_wells:  # check if the well is already flagged as denatured
            return denatured  # return true if it is

        if self.tm and (self.tm <= self.owner.tm_cutoff_low or self.tm >= self.owner.tm_cutoff_high):
            denatured = True
            return denatured

        for i in self.derivatives[1]:  # Iterate over all points in the first derivative
            if i > 0:  # If a positive slope is found
                denatured = False  # set denatured flag to False

        reads = int(round(self.owner.reads / 10))  # How many values should be checked against the signal threshold:
        # 1/10 of the total number of data point
        read = 0  # Initialize running variable representing the current data point

        if not denatured:
            for j in self.filtered:  # Iterate over the filtered data
                if self.owner.signal_threshold:  # If a signal threshold was defined
                    if j > self.owner.signal_threshold and read <= reads:  # iterate over 1/10 of all data points
                        # and check for values larger than the threshold.
                        denatured = True  # Set flag to True if a match is found
                        print("{}: {}".format(self.name, j))
                        return denatured  # and return
            read += 1

        return denatured

    def analyze(self):
        self.filter_raw()
        self.splines["raw"] = self.calc_spline(self.raw)
        self.splines["filtered"] = self.calc_spline(self.filtered)

        self.calc_derivatives()
        if self.baseline_correction:
            self.baseline = self.calc_baseline(self.derivatives[1])
        if self.is_denatured():
            self.owner.denatured_wells.append(self)

        self.splines["derivative1"] = self.calc_spline(self.derivatives[1])

        self.tm = self.calc_tm()
        if self.tm is None:
            self.tm = np.NaN


class Experiment:
    def __init__(self, type, gui=None, files=None, replicates=None, t1=25, t2=95, dt=1, cols=12, rows=8,
                 cutoff_low=None, cutoff_high=None, signal_threshold=None, color_range=None, baseline_correction=False):
        self.replicates = replicates
        self.cols = cols
        self.rows = rows
        self.t1 = t1
        self.t2 = t2
        self.dt = dt
        self.temprange = np.arange(self.t1, self.t2 + 1, self.dt, dtype=float)
        self.reads = int(round((t2 + 1 - t1) / dt))
        self.wellnum = self.cols * self.rows
        self.files = files
        self.type = type
        self.wells = []
        self.max_tm = None
        self.min_tm = None
        self.replicates = None
        self.gui = gui
        self.signal_threshold = signal_threshold
        self.avg_plate = None
        self.baseline_correction = baseline_correction
        if cutoff_low:
            self.tm_cutoff_low = cutoff_low
        else:
            self.tm_cutoff_low = self.t1
        if cutoff_high:
            self.tm_cutoff_high = cutoff_high
        else:
            self.tm_cutoff_high = self.t2
        if color_range:
            self.color_range = color_range
        else:
            self.color_range = None

        self.plates = []

        i = 1
        for file in files:
            plate = Plate(type=self.type, owner=self, filename=file, t1=self.t1, t2=self.t2, dt=self.dt, cols=self.cols,
                          rows=self.rows, cutoff_low=self.tm_cutoff_low, cutoff_high=self.tm_cutoff_high,
                          signal_threshold=self.signal_threshold, color_range=self.color_range)
            plate.id = i
            self.plates.append(plate)
            i += 1
        if len(files) > 1:
            self.avg_plate = Plate(type=self.type, owner=self, filename=None, t1=self.t1, t2=self.t2, dt=self.dt,
                                   cols=self.cols, rows=self.rows, cutoff_low=self.tm_cutoff_low,
                                   cutoff_high=self.tm_cutoff_high, signal_threshold=self.signal_threshold,
                                   color_range=self.color_range)
            self.avg_plate.id = 'average'

    def analyze(self):
        for plate in self.plates:
            plate.analyze(gui=self.gui)

        if len(self.plates) > 1:

            # self.tm_replicates = np.zeros( self.wellnum, dtype=float )
            # self.tm_replicates_sd = np.zeros( self.wellnum, dtype=float )


            for i in range(self.wellnum):
                tmp = []
                for plate in self.plates:
                    tm = plate.wells[i].tm
                    self.avg_plate.wells[i].name = plate.wells[i].name
                    if plate.wells[i] not in plate.denatured_wells:
                        tmp.append(tm)
                if len(tmp) > 0:
                    # self.avg_plate.wells[i].tm = (sum(tmp)/len(tmp))
                    self.avg_plate.wells[i].tm = np.mean(tmp)
                    self.avg_plate.wells[i].tm_sd = np.std(tmp)
                    # self.tm_replicates[i] = (sum(tmp)/len(tmp))
                else:
                    self.avg_plate.denatured_wells.append(self.avg_plate.wells[i])


class Plate:
    def __init__(self, type, owner, id=None, filename=None, replicates=None, t1=None, t2=None, dt=None, cols=12, rows=8,
                 cutoff_low=None, cutoff_high=None, signal_threshold=None, color_range=None):
        self.cols = cols
        self.rows = rows
        self.owner = owner
        if t1:
            self.t1 = t1
        else:
            self.t1 = owner.t1
        if t1:
            self.t2 = t2
        else:
            self.t2 = owner.t2
        if t1:
            self.dt = dt
        else:
            self.dt = owner.dt
        self.temprange = np.arange(self.t1, self.t2 + 1, self.dt, dtype=float)
        self.reads = int(round((t2 + 1 - t1) / dt))
        self.wellnum = self.cols * self.rows
        self.filename = filename
        self.type = type
        self.wells = []
        self.max_tm = None
        self.min_tm = None
        self.replicates = None
        self.signal_threshold = signal_threshold
        self.id = id
        self.baseline_correction = owner.baseline_correction
        if cutoff_low:
            self.tm_cutoff_low = cutoff_low
        else:
            self.tm_cutoff_low = self.t1
        if cutoff_high:
            self.tm_cutoff_high = cutoff_high
        else:
            self.tm_cutoff_high = self.t2
        if color_range:
            self.color_range = color_range
        else:
            self.color_range = None

        self.denatured_wells = []
        self.tms = []

        for i in range(self.wellnum):
            well = Well(owner=self)
            self.wells.append(well)


    def analytikJena(self):
        """
        Data processing for Analytik Jena qTower 2.0 export files
        """
        with open(self.filename, 'r') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)

            i = 0
            for row in reader:
                temp = np.zeros(self.reads, dtype=float)
                for read in range(self.reads + 1):
                    if read > 0:
                        try:
                            temp[read - 1] = row[read]
                        except:
                            temp[read - 1] = 0.0
                    elif read == 0:
                        self.wells[i].name = row[read]
                self.wells[i].raw = temp
                i += 1

    def analyze(self, gui=None):
        try:
            # Try to access data file in the given path
            with open(self.filename) as f:
                pass
        except IOError as e:
            # If the file is not found, or not accessible: abort
            print('Error accessing file: {}'.format(e))

        if self.type == 'Analytik Jena qTOWER 2.0/2.2':
            self.analytikJena()
            if gui:
                update_progress_bar(gui.pb, 1)
        else:
            # Raise exception, if the instrument's name is unknown
            raise NameError('Unknown instrument type: {}'.format(self.type))

        for well in self.wells:
            well.analyze()
            if gui:
                update_progress_bar(gui.pb, 15)

            self.tms.append(well.tm)

        if self.replicates:
            if self.replicates == 'rows':
                print("rows")
            if self.replicates == 'cols':
                print("cols")
        # print(self.tms)
        self.max_tm = max(self.tms)
        self.min_tm = min(self.tms)

    def write_tm_table(self, filename):
        with open(filename, 'w') as f:
            f.write('#{:<4s}{:>13s}\n'.format('ID', '"Tm [°C]"'))
            for well in self.wells:
                if np.isnan(well.tm) or well in self.denatured_wells:
                    f.write('{:<5s}{:>12s}\n'.format(well.name, 'NaN'))
                else:
                    f.write('{:<5s}{:>12s}\n'.format(well.name, str(well.tm)))

    def write_avg_tm_table(self, filename):
        with open(filename, 'w') as f:
            f.write('#{:<4s}{:>13s}{:>13s}\n'.format('"ID"', '"Tm [°C]"', '"SD"'))
            for well in self.wells:
                if np.isnan(well.tm) or well in self.denatured_wells:
                    f.write('{:<5s}{:>12s}{:>12s}\n'.format(well.name, 'NaN', 'NaN'))
                else:
                    f.write('{:<5s}{:>12s}{:>12s}\n'.format(well.name, str(well.tm), str(well.tm_sd)))

    def write_raw_table(self, filename):
        with open(filename, 'w') as f:
            f.write('#"Raw data"\n')
            f.write('#{:<10s}'.format('"T [°C]"'))
            for well in self.wells:
                f.write('{:>15s}'.format(well.name))
            f.write('\n')

            i = 0
            for t in self.temprange:
                f.write('{:<10s}'.format(str(t)))
                for well in self.wells:
                    d = well.raw[i]
                    f.write('{:>-15.3f}'.format(float(np.round(d, decimals=3))))
                f.write('\n')
                i += 1

    def write_filtered_table(self, filename):
        with open(filename, 'w') as f:
            f.write('#"Filtered data" \n')
            f.write('#{:<10s}'.format('"T [°C]"'))
            for well in self.wells:
                f.write('{:>15s}'.format(well.name))
            f.write('\n')

            i = 0
            for t in self.temprange:
                f.write('{:<10s}'.format(str(t)))
                for well in self.wells:
                    d = well.filtered[i]
                    f.write('{:>-15.3f}'.format(float(np.round(d, decimals=3))))
                f.write('\n')
                i += 1

    def write_derivative_table(self, filename):
        with open(filename, 'w') as f:
            f.write('#"Derivative dI/dT"\n')
            f.write('#{:<10s}'.format('"T [°C]"'))
            for well in self.wells:
                f.write('{:>15s}'.format(well.name))
            f.write('\n')

            i = 0
            for t in self.temprange:
                f.write('{:<10s}'.format(str(t)))
                for well in self.wells:
                    d = well.derivatives[1][i]
                    f.write('{:>-15.3f}'.format(float(np.round(d, decimals=3))))
                f.write('\n')
                i += 1

    # TODO: Implement 'write_baseline_corrected_table()

    def write_baseline_corrected_table(self, filename):
        raise NotImplementedError


def update_progress_bar(bar, value):
    bar.setValue(value)

class PlotResults():

    def __init__(self, experiment):
        self.experiment = experiment

    def plot_tm_heatmap_single(self, plate, widget):
        """
        Plot Tm heatmap (Fig. 1)
        """
        x = 1  # Position in columns
        y = 1  # Position in rows
        x_values = []  # Array holding the columns
        y_values = []  # Array holding the rows
        c_values = []  # Array holding the color values aka Tm
        dx_values = []
        dy_values = []
        dc_values = []
        canvas = widget.canvas
        canvas.clear()
        for well in plate.wells:  # Iterate over all wells
            if well not in plate.denatured_wells:  # Check if well is denatured (no Tm found)
                c = well.tm  # If not, set color to Tm
                if c < plate.tm_cutoff_low:  # Check if Tm is lower that the cutoff
                    c = plate.tm_cutoff_low  # If it is, set color to cutoff
                elif c > plate.tm_cutoff_high:  # Check if Tm is higher that the cutoff
                    c = plate.tm_cutoff_high  # If it is, set color to cutoff
            else:  # If the plate is denatured
                c = plate.tm_cutoff_low  # Set its color to the low cutoff
                dx_values.append(x)
                dy_values.append(y)
            x_values.append(x)  # Add values to the respective arrays
            y_values.append(y)
            c_values.append(c)
            x += 1  # Increase column by one
            if x > plate.cols:  # If maximum column per row is reached
                x = 1  # reset column to one
                y += 1  # and increase row by one

        fig1 = canvas.fig  # new figure
        ax1 = fig1.add_subplot(1, 1, 1)  # A single canvas
        ax1.autoscale(tight=True)  # Scale plate size
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(plate.cols + 1))  # n columns
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(plate.rows + 1))  # n rows
        if plate.color_range:
            cax = ax1.scatter(x_values, y_values, s=305, c=c_values, marker='s', vmin=plate.color_range[0],
                              vmax=plate.color_range[1])  # plot wells and color using the colormap
        else:
            cax = ax1.scatter(x_values, y_values, s=305, c=c_values, marker='s')  # plot wells and color using the colormap

        cax2 = ax1.scatter(dx_values, dy_values, s=80, c='white', marker='x', linewidths=(1.5,))
        ax1.invert_yaxis()  # invert y axis to math plate layout
        cbar = fig1.colorbar(cax)  # show colorbar
        ax1.set_xlabel('Columns')  # set axis and colorbar label
        ax1.set_ylabel('Rows')

        if str(plate.id) == 'average':
            title = '$T_m$ heatmap (average)'
        else:
            title = '$T_m$ heatmap (plate #{})'.format(str(plate.id))
        ax1.set_title(title)
        cbar.set_label(u"Temperature [°C]")

        canvas.draw()

    def plot_derivative(self, plate, widget):
        """
        Plot derivatives (Fig. 2)
        """
        canvas = widget.canvas
        canvas.clear()
        fig2 = canvas.fig  # new figure
        fig2.suptitle('Individual Derivatives (plate #{})'.format(str(plate.id)))  # set title

        for plot_num in range(1, plate.wellnum + 1):  # iterate over all wells
            well = plate.wells[plot_num - 1]  # get single well based on current plot number
            ax = fig2.add_subplot(plate.rows, plate.cols, plot_num)  # add new subplot
            ax.autoscale(tight=True)  # scale to data
            ax.set_title(well.name, size='xx-small')  # set title of current subplot to well identifier

            if well in plate.denatured_wells:
                ax.patch.set_facecolor('#FFD6D6')

            if plot_num == plate.wellnum - plate.cols + 1:  # add axis label to the subplot in the bottom left corner of the figure
                ax.set_xlabel(u'T [°C]', size='xx-small')
                ax.set_ylabel('dI/dT', size='xx-small')

            x = plate.temprange  # set values for the x axis to the given temperature range
            if well.baseline_correction:
                print(well.baseline)
                y = well.derivatives[1] - well.baseline
            else:
                y = well.derivatives[1]  # grab y values from the first derivative of the well

            ax.xaxis.set_major_locator(ticker.MaxNLocator(4))  # only show three tickmarks on both axes
            ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
            if well not in plate.denatured_wells:  # check if well is denatured (without determined Tm)
                tm = well.tm  # if not, grab its Tm
            else:
                tm = np.NaN  # else set Tm to np.NaN
            if tm:
                ax.axvline(x=tm)  # plot vertical line at the Tm
            ax.axvspan(plate.t1, plate.tm_cutoff_low, facecolor='0.8', alpha=0.5)  # shade lower cutoff area
            ax.axvspan(plate.tm_cutoff_high, plate.t2, facecolor='0.8', alpha=0.5)  # shade higher cutoff area
            for label in ax.get_xticklabels() + ax.get_yticklabels():  # set fontsize for all tick labels to xx-small
                label.set_fontsize('xx-small')

            cax = ax.plot(x, y)  # plot data to the current subplot
        canvas.draw()


    def plot_raw(self, plate, widget):
        """
        Plot raw data (Fig. 3)
        """
        canvas = widget.canvas
        canvas.clear()
        fig3 = canvas.fig  # new figure
        fig3.suptitle('Raw Data (plate #{})'.format(str(plate.id)))  # set title

        for plot_num in range(1, plate.wellnum + 1):  # iterate over all wells
            well = plate.wells[plot_num - 1]  # get single well based on current plot number
            ax = fig3.add_subplot(plate.rows, plate.cols, plot_num)  # add new subplot
            ax.autoscale(tight=True)  # scale to data
            ax.set_title(well.name, size='xx-small')  # set title of current subplot to well identifier

            if well in plate.denatured_wells:
                ax.patch.set_facecolor('#FFD6D6')

            if plot_num == plate.wellnum - plate.cols + 1:  # add axis label to the subplot in the bottom left corner of the figure
                ax.set_xlabel(u'T [°C]', size='xx-small')
                ax.set_ylabel('I', size='xx-small')

            x = plate.temprange  # set values for the x axis to the given temperature range
            y = well.raw  # grab y values from the raw data of the well

            ax.xaxis.set_major_locator(ticker.MaxNLocator(4))  # only show three tickmarks on both axes
            ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
            ax.axvspan(plate.t1, plate.tm_cutoff_low, facecolor='0.8', alpha=0.5)  # shade lower cutoff area
            ax.axvspan(plate.tm_cutoff_high, plate.t2, facecolor='0.8', alpha=0.5)  # shade higher cutoff area
            for label in ax.get_xticklabels() + ax.get_yticklabels():  # set fontsize for all tick labels to xx-small
                label.set_fontsize('xx-small')

            cax = ax.plot(x, y)  # plot data to the current subplot
        canvas.draw()


    # def _plot_wrapper(self, plot, plate):
    #
    #     if plot == 'raw':
    #         fig, ax = self._plot_raw(plate)
    #     elif plot == 'derivative':
    #         fig, ax = self._plot_derivative(plate)
    #     elif plot == 'tm_heatmap':
    #         fig, ax = self._plot_tm_heatmap_single(plate)
    #     else:
    #         raise NotImplementedError
    #         fig = None
    #         ax = None
    #     return (fig, ax)
    #
    # def plot_all(self):
    #
    #     figures = []
    #
    #     for plate in self.experiment.plates:
    #
    #         figures.append(self._plot_wrapper('raw', plate))
    #         figures.append(self._plot_wrapper('derivative', plate))
    #         figures.append(self._plot_wrapper('tm_heatmap', plate))
    #
    #     if len(self.experiment.plates) > 1:
    #         figures.append(self._plot_wrapper('tm_heatmap', self.experiment.avg_plate))
    #
    #     return figures



