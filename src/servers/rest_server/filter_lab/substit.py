from string import replace
def substit(string,variables):
    for var in variables.keys():
        val=str(variables[var])
        string=string.replace(var,val)
    return string