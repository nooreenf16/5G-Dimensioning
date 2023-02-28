import os
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import MinMaxScaler
import math
import joblib


import mpa_sim



np.random.seed(42)
packageFolder = os.path.dirname(mpa_sim.__file__)
dataFolder = os.path.join(os.path.dirname(mpa_sim.__file__), "services", "pkls")

class CPU_forecasting_model(object):
    """

    A forcasting model to predict the utilizadtion of CPU for CU and DU based on Radisys test results.

    Parameters
    ----------
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    dataFile : 
        A csv file contains radisys test results.

    """

    def __init__(self, simulation_parameters, dataFile = "radisys_testresult.csv") -> None:

        self.simulation_parameters = simulation_parameters

        dataFilePath = os.path.join(dataFolder, dataFile)
        self.df = pd.read_csv(dataFilePath)

    def updateModel(self):

        """

        Train a regression model and save it into a file

        Save models are in the order of model_CU, model_DU, scaler 


        Returns
        -------
            True

        """

        X = self.df[['Numerology', 'Bandwidth MHz', 'Modulation (QAM)', 'Number of cells', 'Number of UEs', 'DL (Mbps)',
            'UL (Mbps)']].copy()
        X['cell_x_ue'] = X.loc[:,'Number of cells'] * X.loc[:,'Number of UEs']
        y_CU = self.df['CU CPU Util %']
        y_DU = self.df['DU CPU Util %']

        #data normalization
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        lm_CU = linear_model.LinearRegression()
        model_CU = lm_CU.fit(X_scaled,y_CU)
        lm_DU = linear_model.LinearRegression()
        model_DU = lm_DU.fit(X_scaled,y_DU)

        savedModelFile = "CPU_models.pkl"
        savedModelPath = os.path.join(dataFolder, savedModelFile)

        joblib.dump([model_CU, model_DU, scaler], savedModelPath, compress=0)

        return True

    def loadModels(self, savedModelFile = "CPU_models.pkl"):
        """

        Load the prebuild models.

        Parameters
        ----------
            savedModelFile : a joblib saved models


        Returns
        -------
        model_CU : LinearRegression()
            returns a pre-built sklearn Linear Regression Model.
        model_DU : LinearRegression()
            returns a pre-built sklearn Linear Regression Model.
        scaler : MinMaxScaler()
            returns a pre-built MinMax Scaler.
 

        """
        savedModelPath = os.path.join(dataFolder, savedModelFile)
        model_CU, model_DU, scaler = joblib.load(savedModelPath)

        return model_CU, model_DU, scaler

    
    def estimateCPU_Utilization_CU_DU(self, model_CU, model_DU, scaler):
        """

        estimate the CPU Utilization for CU and DU.

        Parameters
        ----------
        model_CU : LinearRegression()
            A pre-built sklearn Linear Regression Model.
        model_DU : LinearRegression()
            A pre-built sklearn Linear Regression Model.
        scaler : MinMaxScaler()
            returns a pre-built MinMax Scaler.


        Returns
        -------
        CU_utils : flaot percentages
            returns a float number showing the percenatges of overal CPU Cores for CU.
        DU_utils : flaot percentages
            returns a float number showing the percenatges of overal CPU Cores for DU.

        """

        features = ['Numerology', 'Bandwidth', 'Modulation', 'ru_du_ratio', 'Number_of_UEs', 'DL', 'UL']
        dict_filter = lambda x, y: dict([ (i,x[i]) for i in y if i in set(y) ])


        config = dict_filter(self.simulation_parameters, features)

        
        new_conf = pd.DataFrame([config])
        
        new_conf['DL'] = new_conf['DL'] * config['ru_du_ratio']
        new_conf['UL'] = new_conf['UL'] * config['ru_du_ratio']
        new_conf['cell_x_ue'] = config['ru_du_ratio'] * config["Number_of_UEs"] * self.simulation_parameters['Number_of_carriers']

        new_conf_scaled = scaler.transform(new_conf)

        DU_utils = model_DU.predict(new_conf_scaled)[0]
        # CU_utils = model_CU.predict(new_conf_scaled)[0]

        # calculate the proportion of traffic handles by CU_CP
        config_cucp = config.copy()
        config_cucp['cell_x_ue'] = config['ru_du_ratio'] * config["Number_of_UEs"] * self.simulation_parameters["du_cuup_ratio"] * self.simulation_parameters["cucp_cuup_ratio"] * self.simulation_parameters['Number_of_carriers']
        config_cucp['DL'] *= self.simulation_parameters['signaling_overhead'] * config['ru_du_ratio'] * self.simulation_parameters["du_cuup_ratio"] * self.simulation_parameters["cucp_cuup_ratio"]
        config_cucp['UL'] *= self.simulation_parameters['signaling_overhead'] * config['ru_du_ratio'] * self.simulation_parameters["du_cuup_ratio"] * self.simulation_parameters["cucp_cuup_ratio"]

        new_conf = pd.DataFrame([config_cucp])
        new_conf_scaled = scaler.transform(new_conf)

        CUCP_utils = model_CU.predict(new_conf_scaled)[0]

        # calculate the proportion of traffic handles by CU_UP
        config_cuup = config.copy()
        config_cuup['cell_x_ue'] = config['ru_du_ratio'] * config["Number_of_UEs"] * self.simulation_parameters["du_cuup_ratio"] * self.simulation_parameters['Number_of_carriers']
        config_cuup['DL'] *= (1-self.simulation_parameters['signaling_overhead']) * config['ru_du_ratio'] * self.simulation_parameters["du_cuup_ratio"] 
        config_cuup['UL'] *= (1-self.simulation_parameters['signaling_overhead']) * config['ru_du_ratio'] * self.simulation_parameters["du_cuup_ratio"] 

        new_conf = pd.DataFrame([config_cuup])
        new_conf_scaled = scaler.transform(new_conf)

        CUUP_utils = model_CU.predict(new_conf_scaled)[0]

        return {"DU_utils": DU_utils,
                "CUCP_utils": CUCP_utils,
                "CUUP_utils": CUUP_utils}

    def _estimateCPU_Utilization_CU_DU(self, model_CU, model_DU, scaler):
        """

        estimate the CPU Utilization for CU and DU.

        Parameters
        ----------
        model_CU : LinearRegression()
            A pre-built sklearn Linear Regression Model.
        model_DU : LinearRegression()
            A pre-built sklearn Linear Regression Model.
        scaler : MinMaxScaler()
            returns a pre-built MinMax Scaler.


        Returns
        -------
        CU_utils : flaot percentages
            returns a float number showing the percenatges of overal CPU Cores for CU.
        DU_utils : flaot percentages
            returns a float number showing the percenatges of overal CPU Cores for DU.

        """

        config = self.simulation_parameters
        config['cell_x_ue'] = config['Number_of_cells'] * config["Number_of_UEs"]
        new_conf = pd.DataFrame([config])
        new_conf_scaled = scaler.transform(new_conf)

        CU_utils = model_CU.predict(new_conf_scaled)[0]
        DU_utils = model_DU.predict(new_conf_scaled)[0]


        return {"CU_utils": CU_utils,
                "DU_utils": DU_utils}