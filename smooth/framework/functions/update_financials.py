import math

def update_financials(component, financials):
    # Calculate OPEX or CAPEX for this component.
    # Params:
    #  component: object of this component
    #  financials: financial object of this component. This can be either the "capex" or the "opex" dict.
    #
    # This function is calculating a fix CAPEX and OPEX value for components where CAPEX and OPEX are dependant on
    # certain values. The following list shows possible fitting methods. The fitting method is chosen by the CAPEX and
    # OPEX key:
    #
    # "fix"      --> already the fix value, nothing has to be done
    # "spec"     --> cost value needs to be multiplied with the dependant value
    # "exp"      --> exponential cost fitting
    # "poly"     --> polynomial cost fitting
    # "free"     --> polynomial cost fitting with free choosable exponents
    #
    # If multiple keys are defined, the calculations are done sequentially in order.

    # Check if this financial dictionary is empty. If so, nothing has to be calculated.
    if not financials:
        return

    # If the keys are not given as a list, they are transformed to one so they can be iterated.
    if type(financials['key']) is not list:
        financials['key'] = [financials['key']]
        financials['fitting_value'] = [financials['fitting_value']]
        financials['dependant_value'] = [financials['dependant_value']]

    # Loop through each CAPEX or OPEX key.
    for this_index in range(len(financials['key'])):
        update_cost(component, financials, this_index)


def update_cost(component, financials, index):
    this_key = financials['key'][index]
    if this_key == 'fix':
        # Fixed costs do not have to be processed further.
        pass
    elif this_key == 'spec':
        update_spec(component, financials, index)
    elif this_key == 'exp':
        update_exp(component, financials, index)
    elif this_key == 'poly':
        update_poly(component, financials, index)
    elif this_key == 'free':
        update_free(component, financials, index)
    else:
        raise ValueError('CAPEX or OPEX key {} not recognized. Please choose a valid key.'.format(this_key))


def update_spec(component, financials, index):
    # Case: The fitting value is multiplied with the dependant value to get the costs.

    # Get the dependant value (either if given as a component parameter of else it is the previous cost value).
    dependant_value = get_dependant_value(component, financials, index)
    # Get the fitting value, which is the current cost if "cost" is chosen.
    if financials['fitting_value'][index] == 'cost':
        fitting_value = financials['cost']
    else:
        fitting_value = financials['fitting_value'][index]
    # Calculate the costs [EUR].
    financials['cost'] = dependant_value * fitting_value


def update_exp(component, financials, index):
    # Case: An exponential fitting of the cost function is wanted. Here 3 variables are used in the following order:
    # Function if 3 fitting parameters are given:
    # fv_1 + fv_2*exp(fv_3*Parameter)
    # Function if 2 fitting parameters are given:
    # fv_1*exp(fv_2)

    # Get the dependant value (either if given as a component parameter of else it is the previous cost value).
    dependant_value = get_dependant_value(component, financials, index)

    # Get the fitting values.
    fv = financials['fitting_value'][index]

    if len(fv) == 2:
        # If only two fitting values are given, it is assumed that the constant value is 0.
        fv = [0, *fv]
    # Calculate the costs [EUR].
    financials['cost'] = fv[0] + fv[1] * math.exp(fv[2] * dependant_value)


def update_poly(component, financials, index):
    # Case: An polynomial fitting of the cost function is wanted. In this case, an arbitrary number of fitting
    # parameters can be given. They will be used in the following order:
    # Fitting values fv_1, fv_2, fv_3, ..... fv_n.
    # Function:
    # fv_1 + fv_2*dependant_value + fv_3*dependant_value^2 + ... fv_n*dependant_value^(n-1)

    # Get the dependant value (either if given as a component parameter of else it is the previous cost value).
    dependant_value = get_dependant_value(component, financials, index)

    # Get the fitting values.
    fv = financials['fitting_value'][index]
    # Get the number of fitting values [-].
    n_fv = len(fv)

    # In a loop, calculate the costs [EUR].
    cost = 0
    for i_fv in range(n_fv):
        cost += fv[i_fv] * dependant_value ** i_fv

    financials['cost'] = cost


def update_free(component, financials, index):
    # Case: An "free" fitting of the cost function is wanted. In this case, an arbitrary number of fitting parameters
    # can be given. They will be used in the following order:
    # Fitting values fv_1, fv_2, fv_3, ..... fv_n.
    # Function:
    # fv_1*dependant_value^fv_2 + fv_3*dependant_value^fv_4 + ... fv_(n-1)*dependant_value^fv_n

    # Get the dependant value (either if given as a component parameter of else it is the previous cost value).
    dependant_value = get_dependant_value(component, financials, index)

    # Get the fitting values.
    fv = financials['fitting_value'][index]
    # Get the number of fitting values [-].
    n_fv = len(fv)

    # The number of fitting values needs to be even, otherwise throw an error.
    if n_fv % 2 != 0:
        raise ValueError('In component {}, the number of fitting values is {}, but it needs to be even!'.format(
            component['name'], n_fv))

    # Cost value [EUR]
    cost = 0
    for i in range(int(n_fv/2)):
        cost += fv[i*2] * dependant_value**fv[i*2 + 1]

    # Save the costs [EUR].
    financials['cost'] = cost


def get_dependant_value(component, financials, index):
    # Get an attribute of the component as the dependant value.
    dependant_value = getattr(component, financials['dependant_value'][index])
    if financials['dependant_value'][index] == 'capex':
        # If the capex are chosen as the dependant value, the capex costs are meant.
        dependant_value = dependant_value['cost']

    return dependant_value



