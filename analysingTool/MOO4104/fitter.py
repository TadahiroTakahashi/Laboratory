# coding: UTF-8
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ptick
import commands
import scipy.optimize as opt
from lmfit import minimize, Parameters, Parameter, report_fit, fit_report
import seaborn as sns
sns.set_style("whitegrid")
argv = sys.argv



absPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(absPath)
from viewer import data_from_MDO4104

class data_for_fitting(object):
    def __init__(self, arr_x, arr_y, x_start=False, x_end=False, arr_dy=False):
        self.arr_x = arr_x
        self.arr_y = arr_x
        self.dy_const = 0.002  # [V]
        if arr_dy is False:
            arr_dy = np.ones(np.size(arr_x)) * self.dy_const
        
        if x_start is False:
            self.x_start = arr_x[0]
        else:
            self.x_start = x_start

        if x_end is False:
            self.x_end = arr_x[-1]
        else:
            self.x_end = x_end

        self.x_start_index = np.argmin((self.arr_x - self.x_start) ** 2)
        self.x_end_index =  np.argmin((self.arr_x - self.x_end) ** 2)
        self.arr_x = arr_x[self.x_start_index: self.x_end_index]
        print self.arr_x
        self.arr_y = arr_y[self.x_start_index: self.x_end_index]
        self.arr_dy = arr_dy[self.x_start_index: self.x_end_index]


    def fitting_sin(self, model_name='normal'):
        def sin(t, A, freq, vol_offset, ph_offset):
            return vol_offset + A * np.sin(2. * np.pi * freq * t + ph_offset)

        def sin_with_dump(t, A, B, freq_0, tau, vol_offset, ph_offset, t_offset):
            freq = (freq_0 - B / tau * np.exp(-(t - t_offset) / tau))
            return vol_offset + A * np.sin(2. * np.pi * freq  * t + ph_offset)
        
        def sin_with_dump_lin(t, A,freq_0, vol_offset, ph_offset, tilt, f_at_t_equalsTo_0):
            freq = freq_0 + tilt * t + f_at_t_equalsTo_0
            return vol_offset + A * np.sin(2. * np.pi * freq * t + ph_offset)

        def func2min(prms, t, data, eps):
            A = prms['A'].value
            freq_0 = prms['freq_0'].value
            vol_offset = prms['vol_offset'].value
            ph_offset = prms['ph_offset'].value
            if 'B' in prms:  #  means that model_name == with_dump_exp
                B = prms['B'].value
                tau = prms['tau'].value
                t_offset = prms['t_offset'].value
                model = sin_with_dump(t, A, B, freq_0, tau, vol_offset, ph_offset, t_offset)
            elif 'tilt' in prms:  # means that model_name == with_dump_lin
                tilt = prms['tilt'].value
                f_at_t_equalsTo_0 = prms['f_at_t_equalsTo_0'].value
                model = sin_with_dump_lin(t, A, freq_0, vol_offset, ph_offset, tilt, f_at_t_equalsTo_0)
            else:
                model =sin(t, A, freq_0, vol_offset, ph_offset)

            return (model - data) / eps

        def params_edible(result):
            params_out = {}
            params_out['chisqr'] = result.chisqr
            params_out['redchi'] = result.redchi
            for k, param in result.params.items():
                params_out[k] = np.array([param.value, param.stderr])
            return params_out
        
        # initialize
        prms = Parameters()
        prms.add('A', value=0.07)
        prms.add('freq_0', value=1./1.5e-5)
        prms.add('vol_offset', value=0.02)
        prms.add('ph_offset', value=0.)
        if model_name == 'with_dump_exp':
            prms.add('B', value=0.001)
            prms.add('tau', value=0.0001)
            prms.add('t_offset', value=0.0002, min = 0.)
        if model_name == 'with_dump_lin':
            prms.add('tilt', value=0.)
            prms.add('f_at_t_equalsTo_0', value=0., vary=False)

        # do fit, here with leastsq model
        result = minimize(func2min, prms, args=(self.arr_x, self.arr_y, self.arr_dy))
        residual = result.residual
        #print result.params['offset'].stderr
        #print result.params['offset']
        report_dict = params_edible(result)
        diff = residual * self.arr_dy

        # write error report
        report = fit_report(result)

        #print report
        self.diff = diff
        self.fitting_result = self.arr_y + diff
        self.report = report
        self.report_dict = report_dict


def main():
    raw_data = data_from_MDO4104(argv)
    # reading data
    raw_data.readingFile()
    data_dict = raw_data.assigningData()
    time, ch2 = data_dict['time'], data_dict['ch2']

    aquired_data = data_for_fitting(time, ch2, 0.5e-5, 3.0e-5)
    aquired_data.fitting_sin()
    fitting_result = aquired_data.fitting_result
    print aquired_data.report_dict
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
        ax2.plot(aquired_data.arr_x, fitting_result, label="ch4 measured", linewidth=1)
        #ax2.plot(time, np.arcsin((ch2 +0.02)/0.2), label="ch4 measured", linewidth=0.5)
        #plt.show()
        
        # saving data and fitting report
        plt.show()
        #graph_save_name = raw_data.filename + "_fitted.png"
        #plt.savefig(graph_save_name)
        #writefile(FILENAME, osilo_fit_result[1])
        #writeout_analysis(directory, sys.argv[2], {"phase_diff" : phase_diff})

if __name__ == '__main__':
    main()
