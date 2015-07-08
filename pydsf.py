#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Import csv library; Part of python standard libs
import csv

# Import 3rd party packages. Check if installed and die with error message
# if not.
try:
    import matplotlib as mpl
    import mpl_toolkits.axes_grid1

    mpl.use('Qt5Agg')
    mpl.interactive(True)
    import matplotlib.ticker as ticker
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
    from scipy.signal import filtfilt, butter
    from scipy import interpolate
except ImportError:
    raise ImportError('----- SciPy must be installed. -----')

try:
    from PyQt5.QtCore import QCoreApplication
except:
    raise ImportError('----- PyQt5 must be installed -----')

_translate = QCoreApplication.translate


class Well:
    """
    Represents a well in a microtiter plate.
    Owned by an object of type 'Plate'.
    """

    def __init__(self, owner, name=None):
        self.owner = owner
        self.name = name
        self.raw = np.zeros(self.owner.reads, dtype=np.float)
        self.filtered = np.zeros(self.owner.reads, dtype=np.float)
        self.derivatives = np.zeros((4, self.owner.reads))
        self.splines = {"raw": None, "filtered": None, "derivative1": None}
        self.tm = np.NaN
        self.tm_sd = np.NaN
        self.baseline_correction = owner.baseline_correction
        self.baseline = None

    def filter_raw(self):
        """
        Apply a filter to the raw data
        """
        try:
            b, a = butter(3, 0.3, output='ba')
            self.filtered = filtfilt(b, a, self.raw)
        except Exception as err:
            print('Filtering of raw data failed!', err)

    def calc_spline(self, y):
        """
        Calculate a spline that represents the smoothed data points
        """
        try:
            t_range = self.owner.temprange
            spline = interpolate.InterpolatedUnivariateSpline(t_range, y)
            return spline
        except Exception as err:
            print('Calculation of spline failed! ', err)

    def calc_derivatives(self, spline='filtered'):
        """
        Calculates derivatives of a function, representing the raw data.
        Defaults to using the filtered raw data.
        """
        try:
            # iterate over temperature range (x values)
            for t in self.owner.temprange:
                temp = self.splines[spline].derivatives(t)
                for i in range(4):
                    self.derivatives[i, t - self.owner.t1] = temp[i]
        except Exception as err:
            print('Calculation of derivatives failed!', err)

    @staticmethod
    def calc_baseline(y):
        """
        Calculate baseline of the well. Used for peak identification.
        """
        try:
            baseline = peakutils.baseline(y)
            return baseline
        except Exception:
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

        # If a temperatur cutoff has been set and the minimum/maximum
        # temperature values of the provided data is not within that range,
        # cut data accordingly.
        if (self.owner.tm_cutoff_low != self.owner.t1 or
                self.owner.tm_cutoff_high != self.owner.t1):
            x = np.arange(self.owner.tm_cutoff_low,
                          self.owner.tm_cutoff_high + 1, self.owner.dt,
                          dtype=np.dtype(np.float))
        # Otherwise use the whole temperature range of the data
        else:
            x = self.owner.temprange

        # Use second derivative as y
        y = self.derivatives[1]

        # Substract baseline from y
        if self.baseline_correction:
            y = y - self.baseline

        # Run peak finding; return NaN in case of error
        try:
            peak_indexes = peakutils.indexes(y, thres=0.3)

            # loop over results to find maximum value for peak candidates
            max_y = None  # current maximum
            max_i = None  # index of current maximum
            for peak in peak_indexes:
                # if current peak is larger than old maximum and its
                # second derivative is positive, replace maximum with
                # current peak
                if (not max_y or y[peak] > max_y) and y[peak] > 0:
                    max_y = y[peak]
                    max_i = peak

            # If a global maximum is identified, return use its x value as
            # melting temperature
            if max_y and max_i:
                tm = x[max_i]
            # if no maximum is found, return NaN
            else:
                return np.NaN

        except Exception:
            return np.NaN  # In case of error, return no peak

        try:
            if (tm and tm >= self.owner.tm_cutoff_low and
                    tm <= self.owner.tm_cutoff_high):
                tm = round(peakutils.interpolate(x, y,
                                                 width=3,
                                                 ind=[max_i])[0], 2)
                self.owner.denatured_wells.remove(self)
                # If everything is fine, remove the denatured flag
                return tm  # and return the Tm
            else:
                return np.NaN  # otherwise, return NaN
        except Exception:
            return np.NaN  # In case of error, return NaN

    def is_denatured(self):
        """
        Check if the well is denatured. Returns true if the well has been
        already flagged as denatured, no Tm was found, or if the initial
        signal intensity is above a user definded threshold.
        """
        denatured = True  # Assumption is that the well is denatured

        if self in self.owner.denatured_wells:
            # check if the well is already flagged as denatured
            return denatured  # return true if it is

        if self.tm and (self.tm <= self.owner.tm_cutoff_low or
                        self.tm >= self.owner.tm_cutoff_high):
            denatured = True
            return denatured

        for i in self.derivatives[1]:
            # Iterate over all points in the first derivative
            if i > 0:  # If a positive slope is found
                denatured = False  # set denatured flag to False

        reads = int(round(self.owner.reads / 10))
        # How many values should be checked against the signal threshold:
        # 1/10 of the total number of data point
        read = 0
        # Initialize running variable representing the current data point

        if not denatured:
            for j in self.filtered:  # Iterate over the filtered data
                if self.owner.signal_threshold:
                    # If a signal threshold was defined
                    if j > self.owner.signal_threshold and read <= reads:
                        # iterate over 1/10 of all data points
                        # and check for values larger than the threshold.
                        denatured = True
                        # Set flag to True if a match is found
                        print("{}: {}".format(self.name, j))
                        return denatured  # and return
            read += 1

        return denatured

    def analyze(self):
        """
        Analyse data of the well. Takes care of the calculation of derivatives,
        fitting of splines to derivatives and calculation of melting point.
        """
        # apply signal filter to raw data to filter out some noise
        self.filter_raw()
        # fit a spline to unfiltered and filtered raw data
        self.splines["raw"] = self.calc_spline(self.raw)
        self.splines["filtered"] = self.calc_spline(self.filtered)
        # calculate derivatives of filtered data
        self.calc_derivatives()
        # if baseline correction is requested, calculate baseline
        if self.baseline_correction:
            self.baseline = self.calc_baseline(self.derivatives[1])
        # do an initial check if data suggest denaturation
        if self.is_denatured():
            # if appropriate, append well to denatured wells of the plate
            self.owner.denatured_wells.append(self)
        # fit a spline to the first derivative
        self.splines["derivative1"] = self.calc_spline(self.derivatives[1])
        # calculate and set melting point
        self.tm = self.calc_tm()
        # fallback: set melting point to NaN
        if self.tm is None:
            self.tm = np.NaN


class Experiment:
    def __init__(self, exp_type,
                 gui=None,
                 files=None,
                 replicates=None,
                 t1=25,
                 t2=95,
                 dt=1,
                 cols=12,
                 rows=8,
                 cutoff_low=None,
                 cutoff_high=None,
                 signal_threshold=None,
                 color_range=None,
                 baseline_correction=False):
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
        self.type = exp_type
        self.wells = []
        self.max_tm = None
        self.min_tm = None
        self.replicates = None
        self.gui = gui
        self.signal_threshold = signal_threshold
        self.avg_plate = None
        self.baseline_correction = baseline_correction
        # use cuttoff if provided, otherwise cut at edges
        if cutoff_low:
            self.tm_cutoff_low = cutoff_low
        else:
            self.tm_cutoff_low = self.t1
        if cutoff_high:
            self.tm_cutoff_high = cutoff_high
        else:
            self.tm_cutoff_high = self.t2
        # use a specified color range, if provided, otherwise set to None
        if color_range:
            self.color_range = color_range
        else:
            self.color_range = None
        # Initialize self.plates as empty list. New plates will be added to
        # this list
        self.plates = []

        # populate self.plates with data in provided files list
        i = 1
        for file in files:
            plate = Plate(plate_type=self.type,
                          owner=self,
                          filename=file,
                          t1=self.t1,
                          t2=self.t2,
                          dt=self.dt,
                          cols=self.cols,
                          rows=self.rows,
                          cutoff_low=self.tm_cutoff_low,
                          cutoff_high=self.tm_cutoff_high,
                          signal_threshold=self.signal_threshold,
                          color_range=self.color_range)
            plate.id = i
            self.plates.append(plate)
            i += 1
        # if more than one file is provied, assume that those are replicates
        # and add a special plate representing the average results
        if len(files) > 1:
            self.avg_plate = Plate(plate_type=self.type,
                                   owner=self,
                                   filename=None,
                                   t1=self.t1,
                                   t2=self.t2,
                                   dt=self.dt,
                                   cols=self.cols,
                                   rows=self.rows,
                                   cutoff_low=self.tm_cutoff_low,
                                   cutoff_high=self.tm_cutoff_high,
                                   signal_threshold=self.signal_threshold,
                                   color_range=self.color_range)
            self.avg_plate.id = 'average'

    def analyze(self):
        """
        Triggers analyzation of plates.
        """
        for plate in self.plates:
            plate.analyze(gui=self.gui)
        # if more than one plate is present, calculate average values for the
        # merged average plate
        if len(self.plates) > 1:
            # iterate over all wells in a plate
            for i in range(self.wellnum):
                tmp = []
                # iterate over all plates
                for plate in self.plates:
                    tm = plate.wells[i].tm
                    self.avg_plate.wells[i].name = plate.wells[i].name
                    if plate.wells[i] not in plate.denatured_wells:
                        # if well is not denatured, add to collection of tm
                        # values
                        tmp.append(tm)
                if len(tmp) > 0:
                    # if at least one tm is added, calculate average
                    # and standard deviation
                    self.avg_plate.wells[i].tm = np.mean(tmp)
                    self.avg_plate.wells[i].tm_sd = np.std(tmp)
                else:
                    # otherwise add to denatured wells
                    append_well = self.avg_plate.wells[i]
                    self.avg_plate.denatured_wells.append(append_well)


class Plate:
    def __init__(self, plate_type, owner,
                 plate_id=None,
                 filename=None,
                 replicates=None,
                 t1=None,
                 t2=None,
                 dt=None,
                 cols=12,
                 rows=8,
                 cutoff_low=None,
                 cutoff_high=None,
                 signal_threshold=None,
                 color_range=None):
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
        self.type = plate_type
        self.wells = []
        self.max_tm = None
        self.min_tm = None
        self.replicates = replicates
        self.signal_threshold = signal_threshold
        self.id = plate_id
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
                        except (IndexError, ValueError):
                            temp[read - 1] = 0.0
                    elif read == 0:
                        self.wells[i].name = row[read]
                self.wells[i].raw = temp
                i += 1

    def analyze(self, gui=None):
        try:
            # Try to access data file in the given path
            with open(self.filename) as f:
                f.close()
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

    def write_tm_table(self, filename, avg=False):
        with open(filename, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            header = ['ID', 'Tm [°C]']
            if avg:
                header.append('SD [°C]')
            writer.writerow(header)
            for well in self.wells:
                row = [well.name, well.tm]
                if avg:
                    row.append(well.tm_sd)
                writer.writerow(row)

    def write_data_table(self, filename, dataType='raw'):
        with open(filename, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            header = ['Tm [°C]']
            for well in self.wells:
                header.append(well.name)
            writer.writerow(header)

            i = 0
            row = []
            for t in self.temprange:
                row.append(str(t))
                for well in self.wells:
                    if dataType == 'raw':
                        d = well.raw[i]
                    elif dataType == 'filtered':
                        d = well.filtered[i]
                    elif dataType == 'derivative':
                        d = well.derivatives[1][i]
                    else:
                        raise ValueError('Valid dataTypes are "raw", "filtered", and "derivative"! dataType provided was:{}'.format(dataType))
                    d_rounded = float(np.round(d, decimals=3))
                    row.append(d_rounded)
                writer.writerow(row)
                row = []
                i += 1

    # TODO: Implement 'write_baseline_corrected_table()

    def write_baseline_corrected_table(self, filename):
        raise NotImplementedError


def update_progress_bar(bar, value):
    bar.setValue(value)


class PlotResults():
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
        canvas = widget.canvas
        canvas.clear()
        for well in plate.wells:  # Iterate over all wells
            if well not in plate.denatured_wells:
                # Check if well is denatured (no Tm found)
                c = well.tm  # If not, set color to Tm
                if c < plate.tm_cutoff_low:
                    # Check if Tm is lower that the cutoff
                    c = plate.tm_cutoff_low
                    # If it is, set color to cutoff
                elif c > plate.tm_cutoff_high:
                    # Check if Tm is higher that the cutoff
                    c = plate.tm_cutoff_high
                    # If it is, set color to cutoff
            else:  # If the plate is denatured
                c = plate.tm_cutoff_low
                # Set its color to the low cutoff
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
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(plate.cols + 1))
        # n columns
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(plate.rows + 1))
        # n rows
        if plate.color_range:
            # plot wells and color using the colormap
            cax = ax1.scatter(x_values, y_values,
                              s=305,
                              c=c_values,
                              marker='s',
                              vmin=plate.color_range[0],
                              vmax=plate.color_range[1])
        else:
            # plot wells and color using the colormap
            cax = ax1.scatter(x_values, y_values,
                              s=305,
                              c=c_values,
                              marker='s')

        ax1.scatter(dx_values, dy_values,
                    s=80,
                    c='white',
                    marker='x',
                    linewidths=(1.5, ))
        ax1.invert_yaxis()  # invert y axis to math plate layout
        cbar = fig1.colorbar(cax)  # show colorbar
        ax1.set_xlabel(_translate('pydsf',
                                  'Columns'))  # set axis and colorbar label
        ax1.set_ylabel(_translate('pydsf', 'Rows'))

        if str(plate.id) == 'average':
            title = _translate('pydsf', '$T_m$ heatmap (')
        else:
            title = _translate('pydsf', '$T_m$ heatmap (plate #')
        ax1.set_title(title + str(plate.id) + ')')
        cbar.set_label(_translate('pydsf', u"Temperature [°C]"))

        canvas.draw()

    def plot_derivative(self, plate, widget):
        """
        Plot derivatives (Fig. 2)
        """
        canvas = widget.canvas
        canvas.clear()
        fig = canvas.fig  # new figure
        # set title
        title = _translate('pydsf', "Individual Derivatives (plate #")
        fig.suptitle(title + str(plate.id) + ')')

        grid = mpl_toolkits.axes_grid1.Grid(
            fig, 111,
            nrows_ncols=(plate.rows, plate.cols),
            axes_pad=(0.15, 0.25),
            add_all=True,
            share_all=True)

        for i in range(plate.wellnum):
            well = plate.wells[i]
            # set values for the x axis to the given temperature range
            x = plate.temprange
            # grab y values from the raw data of the well
            if well.baseline_correction:
                print(well.baseline)
                y = well.derivatives[1] - well.baseline
            else:
                # grab y values from the first derivative of the well
                y = well.derivatives[1]
            ax = grid[i]
            # set title of current subplot to well identifier
            ax.set_title(well.name, size=6)
            if well in plate.denatured_wells:
                ax.patch.set_facecolor('#FFD6D6')
            # only show three tickmarks on both axes
            ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
            ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
            # check if well is denatured (without determined Tm)
            if well not in plate.denatured_wells:
                tm = well.tm  # if not, grab its Tm
            else:
                tm = np.NaN  # else set Tm to np.NaN
            if tm:
                ax.axvline(x=tm)  # plot vertical line at the Tm
            ax.axvspan(plate.t1, plate.tm_cutoff_low,
                       facecolor='0.8',
                       alpha=0.5)  # shade lower cutoff area
            ax.axvspan(plate.tm_cutoff_high, plate.t2,
                       facecolor='0.8',
                       alpha=0.5)  # shade higher cutoff area
            # set fontsize for all tick labels to xx-small
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(6)
            ax.plot(x, y)
            # if plot_num == plate.wellnum - plate.cols + 1:
            #     ax.set_xlabel(u'T [°C]', size='xx-small')
            #     ax.set_ylabel(u'dI/dT', size='xx-small')
        fig.tight_layout()
        canvas.draw()

    def plot_raw(self, plate, widget):
        """
        Plot raw data (Fig. 3)
        """
        canvas = widget.canvas
        canvas.clear()

        fig = canvas.fig
        title = _translate('pydsf', "Raw Data (plate #")
        fig.suptitle(title + str(plate.id) + ')')

        grid = mpl_toolkits.axes_grid1.Grid(
            fig, 111,
            nrows_ncols=(plate.rows, plate.cols),
            axes_pad=(0.15, 0.25),
            add_all=True,
            share_all=True)
        for i in range(plate.wellnum):
            well = plate.wells[i]
            # set values for the x axis to the given temperature range
            x = plate.temprange
            # grab y values from the raw data of the well
            y = well.raw
            ax = grid[i]
            # set title of current subplot to well identifier
            ax.set_title(well.name, size=6)
            if well in plate.denatured_wells:
                ax.patch.set_facecolor('#FFD6D6')
            # only show three tickmarks on both axes
            ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
            ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
            ax.axvspan(plate.t1, plate.tm_cutoff_low,
                       facecolor='0.8',
                       alpha=0.5)  # shade lower cutoff area
            ax.axvspan(plate.tm_cutoff_high, plate.t2,
                       facecolor='0.8',
                       alpha=0.5)  # shade higher cutoff area
            # set fontsize for all tick labels to xx-small
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(6)
            ax.plot(x, y)
        fig.tight_layout()
        canvas.draw()
