from functions import *
import pandas as pd

def chi_test(_c1, _i1, _c2, _i2, return_value = 'p'):
    import numpy as np
    from scipy import stats
    _c1 = int(_c1)
    _i1 = int(_i1)
    _c2 = int(_c2)
    _i2 = int(_i2)
    obs = np.array([[_c1, _i1-_c1], [_c2,_i2-_c2]])
    chi2, p, dof, expected = stats.chi2_contingency(obs)
    if return_value == 'p':
        return(p)
    else:
        return(chi2, p, dof, expected)


def nCr (n, r):
    import math
    f = math.factorial
    return int(f(n) / f(r) / f(n-r))


def pairwise_test(_data=None, _metric=None, _test_var=None):
    from statsmodels.stats import proportion
    if _metric == 'lpvr':
        num = 'lpv'
        denum = 'impressions'
    elif _metric == 'cpc':
        num = 'spend'
        denum = 'link_clicks'
    elif _metric == 'atcr':
        num = 'atc'
        denum = 'impressions'
    elif _metric == 'ctra':
        num = 'clicks_all'
        denum = 'impressions'
    else:
        _metric = 'ctr'
        num = 'link_clicks'
        denum = 'impressions'

    if _test_var is None:
        _test_var = 'ad_name'

    endrow = len(_data.index)
    bonf_corr = .1 / (2 * nCr(endrow, 2))
    df = []
    columns = [_test_var, _metric, 'lower', 'upper']
    print("Bonferonni Correction brings p-value significance to", round(bonf_corr, 5), "\n")
    for i in range(0, endrow):
        c1_low, c1_upp = proportion.proportion_confint(int(_data.iloc[i, :][num]), int(_data.iloc[i, :][denum]),
                                                       alpha=0.1, method='normal')
        df.append(
            [_data.iloc[i, :][_test_var], int(_data.iloc[i, :][num]) / int(_data.iloc[i, :][denum]), c1_low, c1_upp])
        for j in range(i, endrow):
            if i != j:
                c1 = float(_data.iloc[i, :][num])
                i1 = float(_data.iloc[i, :][denum])
                c2 = float(_data.iloc[j, :][num])
                i2 = float(_data.iloc[j, :][denum])
                ctr1 = c1 / i1
                ctr2 = c2 / i2
                chi2, p, dof, expected = chi_test(c1, i1, c2, i2, 'All')
                c1_low, c1_upp = proportion.proportion_confint(c1, i1, alpha=0.1, method='normal')
                c2_low, c2_upp = proportion.proportion_confint(c2, i2, alpha=0.1, method='normal')
                # print(c1_low, c1_upp, c2_low, c2_upp)
                if p < bonf_corr:
                    if ctr1 > ctr2:
                        print(_data.iloc[i, :][_test_var], "---VS---", _data.iloc[j, :][_test_var])
                        print('\t ' + str(round(ctr1 * 100, 2)) + '%', ">>>", str(round(ctr2 * 100, 2)) + '%')
                    else:
                        print(_data.iloc[i, :][_test_var], "---VS---", _data.iloc[j, :][_test_var])
                        print('\t ' + str(round(ctr1 * 100, 2)) + '%', "<<<", str(round(ctr2 * 100, 2)) + '%')
                    print('\t', 'p = ', '%.15f' % p, "\n")
                else:
                    print(_data.iloc[i, :][_test_var], "---VS---", _data.iloc[j, :][_test_var])
                    print('\t ' + str(round(ctr1 * 100, 2)) + '%', "=?=", str(round(ctr2 * 100, 2)) + '%')
                    print('\t', 'Not Significant, p =', round(p, 4), "\n")
    return (pd.DataFrame(df, columns=columns))


def plot_cis(_data = None, _metric = None, _test_var = None):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    if _metric == 'lpvr':
        metric_name = "Landing Page View Rate"
    elif _metric == 'ctra':
        metric_name = "Click Through Rate (All)"
    elif _metric == 'cpc':
        metric_name = "Cost Per Click"
    elif _metric == 'atcr':
        metric_name = "Adds to Cart Rate"
    else:
        _metric == 'ctr'
        metric_name = "Click Through Rate"
    if _test_var is None:
        _test_var = 'ad_name'
    my_range=range(0,len(_data.index))
    ordered_df = _data.sort_values(by=_metric)
    # The vertical plot is made using the hline function
    # I load the seaborn library only to benefit the nice looking feature
    plt.hlines(y=my_range, xmin=ordered_df['lower'], xmax=ordered_df['upper'], color='grey', alpha=0.4)
    plt.scatter(ordered_df['upper'], my_range, color='green', alpha=0.4 , label='Upper CI')
    plt.scatter(ordered_df[_metric], my_range, color='black', alpha=0.4 , label=_metric.upper(), marker = "|")
    plt.scatter(ordered_df['lower'], my_range, color='skyblue', alpha=1, label='Lower CI')
    plt.legend()

    # Add title and axis names
    plt.yticks(my_range, ordered_df[_test_var])
    plt.title("Comparison of "+metric_name+"s with Confidence Intervals", loc='left')
    plt.xlabel(metric_name)
    plt.ylabel(_test_var)
    return(plt)



def reagg(_data = None, _test_vars = None, _var_name = None):
    endrow = len(_data.index)
    _data['spend']=pd.to_numeric(_data['spend'], errors='coerce')
    _data['impressions']=pd.to_numeric(_data['impressions'], errors='coerce')
    _data['link_clicks']=pd.to_numeric(_data['link_clicks'], errors='coerce')
    _data['clicks_all']=pd.to_numeric(_data['clicks_all'], errors='coerce')
    _data['lpv']=pd.to_numeric(_data['lpv'], errors='coerce')
    _data['atc']=pd.to_numeric(_data['atc'], errors='coerce')
    _data['purchases']=pd.to_numeric(_data['purchases'], errors='coerce')
    if _var_name is None:
        _var_name = 'ad_name'
        rdata = _data
    else:
        _data[_var_name]=None
        for key, value in _test_vars.items():
            _data.loc[_data['ad_name'].str.contains(key), _var_name] = value
        rdata = _data.groupby([_var_name])["spend", "impressions", "link_clicks", "clicks_all", "lpv", "atc", "purchases"].sum().reset_index()
    rdata['ctr']=rdata['link_clicks']/rdata['impressions']
    rdata['lpvr']=rdata['lpv']/rdata['impressions']
    rdata['atcr']=rdata['atc']/rdata['impressions']
    rdata['cpc']=rdata['spend']/rdata['link_clicks']
    rdata['cplpv']=rdata['spend']/rdata['lpv']
    rdata['cpatc']=rdata['spend']/rdata['atc']
    rdata = rdata.round({
        'ctr':4,
        'lpvr':4,
        'atcr':4,
        'cpc':2,
        'cplpv':2,
        'cpatc':2
    })
    rdata.ctr = (rdata.ctr * 100).astype(str) + '%'
    rdata.lpvr = (rdata.lpvr * 100).astype(str) + '%'
    rdata.atcr = (rdata.atcr * 100).astype(str) + '%'
    return(rdata)


