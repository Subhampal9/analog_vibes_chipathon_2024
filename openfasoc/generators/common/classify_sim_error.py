import warnings
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.get_ngspice_version import check_ngspice_version

def compare_files(template_file, result_file, errors) -> int:
    """Checks if the generated simulation result file matches with 
    the stored template file.

    Args:
    - 'template_file' (string): The stored template file
    - 'result_file' (string): The result file generated by the simulations
    - 'errors' (dict): Dict of dicts containing max and min allowable errors (in percent) for each result type

    Returns:
    - 'int': 
        Returns 2 if the differences in readings are greater than max allowable error,
        Returns 1 if the differences in readings lie between the maximum and minimum allowable error range,
        Returns 0 otherwise
    """
    with open(template_file, 'r') as template, open(result_file, 'r') as result:
        next(template)
        next(result)

        for template_line, result_line in zip(template, result):
            template_data = [float(val) for val in template_line.split()]
            result_data = [float(val) for val in result_line.split()]
            
            freq_diff = (abs(template_data[1] - result_data[1]) / template_data[1]) * 100 if template_data[1] != 0.0 else (abs(template_data[1] - result_data[1])) * 100
            power_diff = (abs(template_data[2] - result_data[2]) / template_data[2]) * 100 if template_data[2] != 0.0 else (abs(template_data[2] - result_data[2])) * 100
            error_diff = (abs(template_data[3] - result_data[3]) / template_data[3]) * 100 if template_data[3] != 0.0 else (abs(template_data[3] - result_data[3])) * 100
            
            if freq_diff > errors['frequency']['max'] or power_diff > errors['power']['max'] or error_diff > errors['error']['max']:
                return 2
            elif freq_diff > errors['frequency']['min'] or power_diff > errors['power']['min'] or error_diff > errors['error']['min']:
                return 1
        return 0
            
def classify_sim_error(template_file, result_file) -> str:
    """Used to propogate out how close the generated simulations results are 
    from the results in the stored template files

    Args:
    - 'template_file' (string): The stored template file
    - 'result_file' (string): The result file generated by the simulations

    Returns:
    - str: The kind of alert
        - 'red' alert for very large difference in generated and template results
        - 'amber' alert if the difference lies within the allowable range
        - 'green' if ok
    """
    ngspice_check_flag = check_ngspice_version()
    alerts = { 0: 'green', 1: 'amber', 2: 'red' }
    
    errors = {
        'frequency': { 'max': 1, 'min': 0.5 },
        'power': { 'max': 1000, 'min': 1000 },
        'error': { 'max': 100, 'min': 50 },
    }
    
    if ngspice_check_flag:
        if compare_files(template_file, result_file, errors) == 0:
            return alerts[0]
        elif compare_files(template_file, result_file, errors) == 1:
            warnings.warn('Simulation results do not match, but ngspice version matches!')
            return alerts[1]
        else:
            return alerts[2]
        
    elif ngspice_check_flag == 0:
        warnings.warn('NGSPICE version does not match!')
        if compare_files(template_file, result_file, errors) == 0:
            return alerts[0]
        elif compare_files(template_file, result_file, errors) == 1:
            warnings.warn('Simulation results do not match!')
            return alerts[1]
        else:
            return alerts[2]
