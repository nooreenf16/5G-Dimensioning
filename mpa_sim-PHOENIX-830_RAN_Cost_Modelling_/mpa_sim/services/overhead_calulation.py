import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeRegressor
def overhead_per_server(type_of_server,type_of_virtualization,prop_or_not,n):
    """overhead per server.
    
    Parameters
    ----------
    type_of_server : str
        Type of server.
        Here we consider 2 types of servers:
        1.Dell PowerEdge T330 server
        2.Dell PowerEdge T430 server

    type_of_virtualization : str
        There are three types of virtualization: 
        1.KVM (Kernel-based Virtual Machine),
        2.VirtualBox (VirtualBox) and
        3.Docker (Docker).

    prop_or_not : bool
        Whether the server is receiving a proportional or non proportional workload.

    n : int
        Number of cpus in the server.
        "Assuming each physical server has same no.of vms as the no.of cpus in the server." 

    Returns
    -------
    overhead : float
        overhead percentage per virtual server.
    """
    df_t330 = pd.read_csv('mpa_sim-PHOENIX-830_RAN_Cost_Modelling\tests\mpa_sim\static\t330.csv')
    df_t430 = pd.read_csv('mpa_sim-PHOENIX-830_RAN_Cost_Modelling\tests\mpa_sim\static\t430.csv')

    X_t330 = df_t330.drop('overhead', axis=1)
    y_t330 = df_t330['overhead']

    X_t430 = df_t430.drop('overhead', axis=1)
    y_t430 = df_t430['overhead']

    dtree_330 = DecisionTreeRegressor()
    dtree_330.fit(X_t330, y_t330)

    dtree_430 = DecisionTreeRegressor()
    dtree_430.fit(X_t430, y_t430)


    if type_of_server == 'Dell PowerEdge T330 server':
        if type_of_virtualization == 'KVM':
            if prop_or_not == True:
                overhead = dtree_330.predict([[0,1, n]])
            else:
                overhead = dtree_330.predict([[0,0, n]])
        elif type_of_virtualization == 'VirtualBox':
            if prop_or_not == True:
                overhead = dtree_330.predict([[1,1, n]])
            else:
                overhead = dtree_330.predict([[1,0, n]])
        elif type_of_virtualization == 'Docker':
            if prop_or_not == True:
                overhead = dtree_330.predict([[2,1, n]])
            else:
                overhead = dtree_330.predict([[2,0, n]])
        else:
            print('Please enter a valid type of virtualization.')

    elif type_of_server == 'Dell PowerEdge T430 server':
        if type_of_virtualization == 'KVM':
            if prop_or_not == True:
                overhead = dtree_430.predict([[0,1, n]])
            else:
                overhead = dtree_430.predict([[0,0, n]])

        elif type_of_virtualization == 'VirtualBox':
            if prop_or_not == True:
                overhead = dtree_430.predict([[1,1, n]])
            else:
                overhead = dtree_430.predict([[1,0, n]])

        elif type_of_virtualization == 'Docker':
            if prop_or_not == True:
                overhead = dtree_430.predict([[2,1, n]])
            else:
                overhead = dtree_430.predict([[2,0, n]])

        else:
            print('Please enter a valid type of virtualization.')

    else:
        print('Please enter a valid type of server.')


    return overhead[0]