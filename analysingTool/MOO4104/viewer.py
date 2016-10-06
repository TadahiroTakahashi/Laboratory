# coding: UTF-8
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ptick
import commands
import seaborn as sns
import os
sns.set_style("whitegrid")
argv = sys.argv

### information of input data required###
class data_from_MDO4104(object):
    def __init__(self, argv):
        ## in future, directory etc should be set by new function.
        self.directory = "/Users/tadahiro/Documents/data/20161005/"
        self.filetype = argv[1]
        self.priminal_parameter = argv[2]
        self.filename = str(self.directory) + str(self.filetype)

        #### fitting_parameter ####
        self.freq = 40.E6  # [Hz]
        self.err_vol = 1.E-2  # [V]
        self.MODEL_NAME = 'normal'
        self.assign_array = ['time', 'ch2']

        self.plotter = True


    def assigningData(self):
        assign_array = self.assign_array
        data_dict = {}
        for num, name in enumerate(assign_array):
            data_dict[name] = self.data[:, num]
        return data_dict


    def readingFile(self):
        # ref: http://python.civic-apps.com/file-io/
        # genfromtxt: http://docs.scipy.org/doc/numpy/reference/generated/numpy.genfromtxt.html
        # memoryを調べたい時は，https://divide-et-impera.org/archives/1572
        fileN = self.filename
        inputfileN = str(fileN) + '.csv'
        preamble = []
        with open(inputfileN, "r") as file:
            for string in file:
                contents = string.strip()
                if contents is '':
                    continue
                preamble.append(contents)
                if len(contents) - contents.count(',') == 0:
                    break
        data = np.genfromtxt(inputfileN, comments='##', delimiter=',', skip_header= 21)

        self.preamble = preamble
        self.data = data
        


def main():
    raw_data = data_from_MDO4104(argv)
    # reading data
    raw_data.readingFile()
    data_dict = raw_data.assigningData(raw_data.data)
    time, ch2 = data_dict['time'], data_dict['ch2']

    if raw_data.plotter is True:
        # ploting data
        fig = plt.figure()
        ax1 = plt.axes([0.1, 0.6, 0.8, 0.3])
        ax2 = plt.axes([0.1, 0.1, 0.8, 0.3])

        ax1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        ax2.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))

        #ax1.set_xlim([100, 0.5e-5+0.8e-5])
        #ax1.set_ylim([-0.05, 0.01])

        ax1.set_xlabel("time[s]")
        ax1.set_ylabel("voltage[V]")

        ax2.set_xlabel("time[s]")
        ax2.set_ylabel("voltage[V]")

        ax1.set_xlim([0.07e-5, 0.2e-5])
        ax1.set_ylim([-0.20, 0.20])
        ax1.plot(time, ch2, label="ch4 measured", linewidth=0.5)
        ax2.plot(time, ch2, label="ch4 measured", linewidth=0.5)
        #ax2.plot(time, np.arcsin((ch2 +0.02)/0.2), label="ch4 measured", linewidth=0.5)
        #plt.show()
        
        # saving data and fitting report
        graph_save_name = raw_data.filename + "_fitted.png"
        plt.savefig(graph_save_name)
        #writefile(FILENAME, osilo_fit_result[1])
        #writeout_analysis(directory, sys.argv[2], {"phase_diff" : phase_diff})
    


if __name__ == '__main__':
    calc = main()
