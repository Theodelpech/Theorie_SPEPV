import solar_mod as sm
import numpy as np
import pandas as pd
from itertools import count
from matplotlib.pyplot import plot
import matplotlib.pyplot as plt
# following line needed for plotting in 3d:
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import scipy.optimize as opt
import warnings
import re
from inverse import *
from errors import *
from function_models import *

class MotPompeDC (object):

    def __init__(self, path):

        # retrieve pump data from txt datasheet given by path
        self.path = path
        self.specs, metadata = get_data_pump(self.path)
        self.voltage_list = self.specs.voltage.drop_duplicates()
        if 'efficiency' not in self.specs.columns or \
                self.specs.efficiency.isna().any():
            # Case with 1 curve Q vs TDH , but only 1 (I,V) point given
            if (self.specs.current == self.specs.current.max()).all() and \
                    (self.specs.voltage == self.specs.voltage.max()).all():
                self.specs = _extrapolate_pow_eff_with_cst_efficiency(
                        self.specs, efficiency_coeff=1)
            # Case with Q&P vs TDH given at 1 or multiple voltage
            else:
                # complete column 'power' if needed
                if 'power' not in self.specs.columns or \
                        self.specs.power.isna().any():
                    self.specs['power'] = self.specs.voltage \
                        * self.specs.current
                # complete column 'efficiency'
                self.specs['efficiency'] = (
                    ((self.specs.flow/60000) * self.specs.tdh * 9.81 * 1000)
                    / self.specs.power)

        # compute the ranges for each parameters of the specs
        self.range = pd.DataFrame([self.specs.max(), self.specs.min()],
                                  index=['max', 'min'])

        self.data_completeness = specs_completeness(
                self.specs)
        self.coeffs = _curves_coeffs_Arab06(
                    self.specs, self.data_completeness)
    def iv_curve_data(self, head, nbpoint=40):
        """
        Function returning the data needed for plotting the IV curve at
        a given head.

        Parameters
        ----------
        head: float
            Total dynamic head at pump output [m]
        appoint: integer, default 40
            Number of data point wanted

        Return
        ------
        dict
            with following couples keys-values:
                I: list of current [A]
                V: list of voltage [V]
        """

        fctI, intervals = self.functIforVH_Arab()

        Vvect = np.linspace(min(intervals['V'](head)),
                            max(intervals['V'](head)),
                            nbpoint)
        Ivect = np.zeros(nbpoint)

        for i, V in enumerate(Vvect):
            Ivect[i] = fctI(V, head)

        return {'I':  Ivect, 'V': Vvect}
    
        
    def functIforVH_Arab(self): 
        """
        Function using Hadj Arab model for modeling I vs V of pump.

        Check out :py:func:`_curves_coeffs_Arab06` for more details.
        """
        
        coeffs = self.coeffs['coeffs_f1']

        if self.data_completeness['data_number'] >= 12 \
                and self.data_completeness['voltage_number'] >= 3:
            funct_mod = compound_polynomial_1_3
        else:
            funct_mod = compound_polynomial_1_2

        # domain of V and tdh and gathering in one single variable
        dom = _domain_V_H(self.specs, self.data_completeness)
        intervals = {'V': dom[0],
                     'H': dom[1]}

        def functI(V, H, error_raising=True):
            """Function giving voltage V according to current I and tdh H.

            Error_raising parameter allows to check the given values
            according to the possible intervals and to raise errors if not
            corresponding.
            """
            if error_raising is True:
                # check if the head is available for the pump
                v_max = intervals['V'](0)[1]
                if not 0 <= H <= intervals['H'](v_max)[1]:
                    raise HeadError(
                            'H (={0}) is out of bounds for this pump. '
                            'H should be in the interval {1}.'
                            .format(H, intervals['H'](v_max)))
                # check if there is enough current for given head
                if not intervals['V'](H)[0] <= V <= intervals['V'](H)[1]:
                    raise VoltageError(
                            'V (={0}) is out of bounds. For this specific '
                            'head H (={1}), V should be in the interval {2}'
                            .format(V, H, intervals['V'](H)))
            return funct_mod([V, H], *coeffs)

        return functI, intervals
    def functQforVH(self):
        """
        Function redirecting to functQforPH. It first computes P with
        functIforVH(), and then reinjects it into functQforPH().
        """

        def functQ(V, H):
            f1, _ = self.functIforVH_Arab()
            f2, _ = self.functQforPH_Arab()
            try:
                cur = f1(V, H)
            except (VoltageError, HeadError):
                cur = np.nan
            return f2(V*cur, H)

        dom = _domain_V_H(self.specs, self.data_completeness)
        intervals = {'V': dom[0],
                     'H': dom[1]}

        return functQ, intervals
            

def functQforPH_Arab(self):
        """
        Function using Hadj Arab model for output flow rate modeling.

        Check out :py:func:`_curves_coeffs_Arab06` for more details.

        """

        coeffs = self.coeffs['coeffs_f2']
        if len(coeffs) == 12:
            funct_mod = compound_polynomial_2_3
        elif len(coeffs) == 9:
            funct_mod = compound_polynomial_2_2
        elif len(coeffs) == 8:
            funct_mod = compound_polynomial_1_3

        # domain of V and tdh and gathering in one single variable
        dom = _domain_P_H(self.specs, self.data_completeness)
        intervals = {'P': dom[0],
                     'H': dom[1]}

        def functQ(P, H):
            # check if head is in available range (NOT redundant with rest)
            if H > intervals['H'](P)[1]:
                Q = 0
                P_unused = P
            # check if P is insufficient
            elif P < intervals['P'](H)[0]:
                Q = 0
                P_unused = P
            # if P is in available range
            elif intervals['P'](H)[0] <= P <= intervals['P'](H)[1]:
                Q = funct_mod([P, H], *coeffs)
                P_unused = 0
                if Q < 0:  # Case where extrapolation from curve fit is bad
                    Q = 0
            # if P is more than maximum
            elif intervals['P'](H)[1] < P:
                Pmax = intervals['P'](H)[1]
                Q = funct_mod([Pmax, H], *coeffs)
                P_unused = P - Pmax
            # if P is NaN or other
            else:
                Q = np.nan
                P_unused = np.nan
            return {'Q': Q, 'P_unused': P_unused}

        return functQ, intervals
def get_data_pump(path):
    # open in read-only option
    with open(path, 'r') as csvdata:

        metadata = {}
        header = True
        while header is True:
            # get metadata
            line = csvdata.readline()

            # check that it is still header
            if line.startswith('# '):
                header is False
                break

            # remove carriage return and split at ':'.
            # .strip() removes leading or trailing whitespace
            content = re.split(':|#', line.rstrip('\n'))
            metadata[content[0].lower().strip()] = content[1].strip()

        # Import data
        # header=0 because firstline already read before
        data_df = pd.read_csv(csvdata, sep='\t', header=0, comment='#')

    return data_df, metadata


def specs_completeness(specs):
    """
    Evaluates the data completeness of a motor-pump.

    Parameters
    ----------
    specs: pandas.DataFrame
        Dataframe with specifications of motor-pump

    motor_electrical_architecture: str
        Can be 'permanent_magnet', 'series_excited', 'shunt_excited',
        'separately_excited'.

    Returns
    -------
    dict
        * voltage_number: float
            number of voltage for which data are given
        * data_number: float
            number of points for which lpm, current, voltage and head are
            given
        * head_number: float
            number of head for which other data are given
        * lpm_min: float
            Ratio between min flow_rate given and maximum.
            Should be ideally 0.
        * head_min:float
            Ratio between min head given and maximum.
            Should be ideally 0.
        * elec_archi: boolean
            A valid electrical architecture for the motor is given
    """

    # nb voltages
    voltages = specs.voltage.drop_duplicates()
    volt_nb = len(voltages)

    # flow data completeness (ideally goes until zero)
    lpm_ratio = []
    for v in voltages:
        lpm_ratio.append(min(specs[specs.voltage == v].flow)
                         / max(specs[specs.voltage == v].flow))
    mean_lpm_ratio = np.mean(lpm_ratio)

    # nb heads
    heads = specs.tdh.drop_duplicates()
    heads_nb = len(heads)

    # head data completeness (minimum tdh should be 0 ideally)
    head_ratio = min(specs.tdh)/max(specs.tdh)

    data_number = 0
    for v in voltages:
        for i in specs[specs.voltage == v].flow:
            data_number += 1

    return {'voltage_number': volt_nb,
            'lpm_min': mean_lpm_ratio,
            'head_min': head_ratio,
            'head_number': heads_nb,
            'data_number': data_number}


# TODO: add way to use it with only very few data point in the case of mppt
def _curves_coeffs_Arab06(specs, data_completeness):
    """
    Compute curve-fitting coefficient with method of Hadj Arab [1] and
    Djoudi Gherbi [2].

    It uses a 3rd order polynomial to model Q(P) and
    a 1st order polynomial to model I(V). Each corresponding
    coefficient depends on TDH through a 3rd order polynomial.

    Parameters
    ----------
    specs: pd.DataFrame
        DataFrame with specs.

    Returns
    -------
    dict
        Coefficients resulting from linear regression under
        keys 'coeffs_f1' and 'coeffs_f2', and statistical figures on
        goodness of fit (keys: 'rmse_f1', 'nrmse_f1', 'r_squared_f1',
        'adjusted_r_squared_f1', 'rmse_f2', 'nrmse_f2',
        'r_squared_f2', 'adjusted_r_squared_f2')

    References
    ----------
    [1] Hadj Arab A., Benghanem M. & Chenlo F.,
    "Motor-pump system modelization", 2006, Renewable Energy

    [2] Djoudi Gherbi, Hadj Arab A., Salhi H., "Improvement and validation
    of PV motor-pump model for PV pumping system performance analysis",
    2017, Solar Energy

    """
    # TODO: add check on number of head available (for lin. reg. of coeffs)

    # TODO: add attribute forcing the use of one particular model
    # ex: force_model='djoudi' (or 'arab', or 'alternative'...)

    # Original model from [2]
    if data_completeness['data_number'] >= 12 \
            and data_completeness['voltage_number'] >= 3:
        funct_mod_1 = compound_polynomial_1_3
        funct_mod_2 = compound_polynomial_2_3
    # Original model from [1]
    elif data_completeness['data_number'] >= 9 \
            and data_completeness['voltage_number'] >= 3:
        funct_mod_1 = compound_polynomial_1_2
        funct_mod_2 = compound_polynomial_2_2
    # Other alternative for more restricted pump specifications
    elif data_completeness['data_number'] >= 8 \
            and data_completeness['voltage_number'] >= 2:
        funct_mod_1 = compound_polynomial_1_2
        funct_mod_2 = compound_polynomial_1_3
    else:
        raise InsufficientDataError('Lack of information on lpm, '
                                           'current or tdh for pump.')

    # f1: I(V, H)
    dataxy = [np.array(specs.voltage),
              np.array(specs.tdh)]
    dataz = np.array(specs.current)

    param_f1, covmat_f1 = opt.curve_fit(funct_mod_1, dataxy, dataz)
    # computing of statistical figures for f1
    stats_f1 = correlation_stats(funct_mod_1, param_f1,
                                                 dataxy, dataz)

    # f2: Q(P, H)
    dataxy = [np.array(specs.power),
              np.array(specs.tdh)]
    dataz = np.array(specs.flow)

    param_f2, covmat_f2 = opt.curve_fit(funct_mod_2, dataxy, dataz)
    # computing of statistical figures for f2
    stats_f2 = correlation_stats(funct_mod_2, param_f2,
                                                 dataxy, dataz)

    return {'coeffs_f1': param_f1,
            'rmse_f1': stats_f1['rmse'],
            'nrmse_f1': stats_f1['nrmse'],
            'r_squared_f1': stats_f1['r_squared'],
            'adjusted_r_squared_f1': stats_f1['adjusted_r_squared'],
            'coeffs_f2': param_f2,
            'rmse_f2': stats_f2['rmse'],
            'nrmse_f2': stats_f2['nrmse'],
            'r_squared_f2': stats_f2['r_squared'],
            'adjusted_r_squared_f2': stats_f2['adjusted_r_squared']}

def _domain_V_H(specs, data_completeness):
    """
    Function giving the range of voltage and head in which the pump will
    work.

    Parameters
    ----------
    specs: pandas.DataFrame,
        Specifications typically coming from Pump.specs

    data_completeness: dict,
        Typically comes from specs_completeness() function.

    Returns
    -------
    tuple
        Two lists, the domains on voltage V [V] and on head [m]
    """
    funct_mod = polynomial_2

    data_v = specs.voltage.drop_duplicates()
    tdh_tips = []
    for v in data_v:
        tdh_tips.append(max(specs[specs.voltage == v].tdh))

    if data_completeness['voltage_number'] > 2 \
            and data_completeness['lpm_min'] == 0:
        # case working fine for SunPumps - not sure about complete data from
        # other manufacturer
        param_tdh, pcov_tdh = opt.curve_fit(funct_mod,
                                            data_v, tdh_tips)
        param_v, pcov_v = opt.curve_fit(funct_mod,
                                        tdh_tips, data_v)

        def interval_vol(tdh):
            "Interval on v depending on tdh"
            return [max(funct_mod(tdh, *param_v), min(data_v)),
                    max(data_v)]

        def interval_tdh(v):
            "Interval on tdh depending on v"
            return [0, min(max(funct_mod(v, *param_tdh), 0),
                           max(specs.tdh))]

    else:
        # Would need deeper work to fully understand what are the limits
        # on I and V depending on tdh, and how it affects lpm
        def interval_vol(*args):
            "Interval on vol, independent of tdh"
            return [min(data_v), max(data_v)]

        def interval_tdh(*args):
            "Interval on tdh, independent of vol"
            return [0, max(specs.tdh)]

    return interval_vol, interval_tdh


def _domain_P_H(specs, data_completeness):
    """
    Function giving the range of power and head in which the pump will
    work.

    Parameters
    ----------
    specs: pandas.DataFrame,
        Specifications typically coming from Pump.specs

    data_completeness: dict,
        Typically comes from specs_completeness() function.

    Returns
    -------
    tuple
        Two lists, the domains on power P [W] and on head [m]

    """
    funct_mod = polynomial_1

    if data_completeness['voltage_number'] >= 2 \
            and data_completeness['lpm_min'] == 0:
        # case working fine for SunPumps - not sure about complete data from
        # other manufacturer
        df_flow_null = specs[specs.flow == 0]

        datapower_df = df_flow_null['power']
        datatdh_df = df_flow_null['tdh']

        datapower_ar = np.array(datapower_df)
        datatdh_ar = np.array(datatdh_df)

        param_tdh, pcov_tdh = opt.curve_fit(funct_mod,
                                            datapower_ar, datatdh_ar)
        param_pow, pcov_pow = opt.curve_fit(funct_mod,
                                            datatdh_ar, datapower_ar)

        def interval_power(tdh):
            "Interval on power depending on tdh"
            power_max_for_tdh = max(specs[specs.tdh <= tdh].power)
            return [max(funct_mod(tdh, *param_pow), min(datapower_ar)),
                    power_max_for_tdh]

        def interval_tdh(power):
            "Interval on tdh depending on v"
            return [0, min(max(funct_mod(power, *param_tdh), 0),
                           max(datatdh_ar))]

    elif data_completeness['voltage_number'] >= 2:
        tdhmax_df = specs[specs.tdh == max(specs.tdh)]
        power_min_tdhmax = min(tdhmax_df.power)
        tdhmin_df = specs[specs.tdh == min(specs.tdh)]
        power_min_tdhmin = min(tdhmin_df.power)

        datapower_ar = np.array([power_min_tdhmin, power_min_tdhmax])
        datatdh_ar = np.array(
            [float(specs[specs.power == power_min_tdhmin].tdh),
             float(specs[specs.power == power_min_tdhmax].tdh)])
        param_tdh, pcov_tdh = opt.curve_fit(funct_mod,
                                            datapower_ar, datatdh_ar)
        param_pow, pcov_pow = opt.curve_fit(funct_mod,
                                            datatdh_ar, datapower_ar)

        def interval_power(tdh):
            "Interval on power depending on tdh"
            power_max_for_tdh = max(specs[specs.tdh <= tdh].power)
            return [max(funct_mod(tdh, *param_pow), min(datapower_ar)),
                    power_max_for_tdh]

        def interval_tdh(power):
            "Interval on tdh depending on v"
            return [0, min(max(funct_mod(power, *param_tdh), 0),
                           max(datatdh_ar))]

    else:
        # Would need deeper work to fully understand what are the limits
        # on I and V depending on tdh, and how it affects lpm
        # -> relates to function starting characteristics
        datax_ar = np.array(specs.power)
        datay_ar = np.array(specs.tdh)

        def interval_power(*args):
            "Interval on power, independent of tdh"
            return [min(datax_ar), max(datax_ar)]

        def interval_tdh(*args):
            "Interval on tdh, independent of power"
            return [0, max(datay_ar)]

    return interval_power, interval_tdh
def _extrapolate_pow_eff_with_cst_efficiency(specs, efficiency_coeff=1):
    """
    Adapt/complete specifications of a limite pump datasheet.
    Used in '__init__()'

    Works on the assumption that the available (I, V, Q, TDH) point is the
    rated operating point, and that the efficiency is constant then
    (oversimplification!). In order to mitigate this last assumption,
    a coeff can be used to consider the mean efficiency as a ratio
    of the rated efficiency.

    Parameters
    ----------
    specs: pandas.DataFrame
        Attribute specs of Pump().

    efficiency_coeff: float, in range [0, 1]
        The ratio between the mean efficiency and the rated efficiency
        -> mean_efficiency = efficiency_coeff * rated_efficiency

    Returns
    -------
    pandas.DataFrame
        Attribute specs of Pump().
    """
    # computes all the hydraulic power through tdh and Q
    hydrau_power = specs.flow/60000 * specs.tdh * 9810
    # keep the data where hydraulic power is the highest, and
    # assumes that this is the rated flowrate point
    rated_data = specs[hydrau_power == hydrau_power.max()]
    rated_power = rated_data.voltage * rated_data.current
    rated_efficiency = float(hydrau_power.max()/rated_power)
    # check consistency:
    if not 0 < rated_efficiency < 1:
        raise ValueError('The rated efficiency is found to be '
                         'out of the range [0, 1].')
    # arbitrary coeff
    efficiency_coeff = 1
    mean_efficiency = efficiency_coeff * rated_efficiency
    specs['efficiency'] = mean_efficiency
    warnings.warn('Power and current data will be recomputed '
                  'with constant efficiency assumption.')
    specs.power = hydrau_power / mean_efficiency
    specs.current = specs.power / specs.voltage
    return specs