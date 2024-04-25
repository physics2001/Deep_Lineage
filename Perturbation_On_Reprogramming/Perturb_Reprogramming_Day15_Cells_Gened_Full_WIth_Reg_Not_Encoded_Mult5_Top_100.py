# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 11:59:08 2022

@author: zhang
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 00:40:57 2022

@author: zhang
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h5py
import tensorflow as tf
import os
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, TimeDistributed, Layer, Bidirectional, GRU, Activation, Masking
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.activations import relu, softmax
from contextlib import redirect_stdout
from keras.losses import mean_squared_error
import time
from keras.losses import mean_squared_error, categorical_crossentropy
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve
import gc

print(tf.config.list_physical_devices('GPU'))

n_top_genes = 1000
drop_out_list = [0.3]
num_layer_list = [1] #, 2
model_type_list = ["LSTM"] # , "GRU"

with h5py.File('{0}_Genes_Reprogramming_Time_Series_Day_6_9_12_15_Two_Classes.h5'.format(n_top_genes), 'a') as FOB: 
    print("Keys: %s" % FOB.keys())
    X = list(FOB['X'])
    FOB.close()
    
with h5py.File('{0}_Genes_Reprogramming_Time_Series_Gened_Day_21_28_Two_Classes.h5'.format(n_top_genes), 'a') as FOB: 
    print("Keys: %s" % FOB.keys())
    X_Gened = list(FOB['X'])
    FOB.close()

X = np.array(X)
X_Gened = np.array(X_Gened)

TIMESTEPS = X_Gened.shape[1]
FEATURES = X.shape[2]

df = pd.read_csv("Perturb_Reprogramming_{0}_Genes_Not_Encoded_Day_21_28_Gened_Mult5_Change_In_Reprog_Result_With_Init_Class_Info.csv".format(n_top_genes))

max_list = df.loc[:,df.columns[~df.columns.isin(['class_info'])]].max().to_frame().T

max_list = max_list.to_numpy()
max_list = max_list.flatten()

sorted_max_inds = max_list.argsort()

top_100_inds = sorted_max_inds[-100:]

top_20_inds = sorted_max_inds[-20:]

top_20_inds = np.flip(top_20_inds)

min_list = df.loc[:,df.columns[~df.columns.isin(['class_info'])]].max().to_frame().T

min_list = min_list.to_numpy()
min_list = min_list.flatten()

sorted_min_inds = min_list.argsort()

low_20_inds = sorted_min_inds[:20]

low_100_inds = sorted_min_inds[:100]

gene_names = np.loadtxt('Reprogramming_1000_Genes_Logged_True_Scaled_False_Column_Names.txt', dtype=str)

top_20_gene_names = gene_names[top_20_inds]

Reg_Day21_Model_Path = 'Regression_On_Reprogramming_Data/1000_Genes_Two_Classes_Day21/Features_1000_Dropout_0.25_NumLayer2_LSTM/model'
Reg_Day21_Model = load_model(Reg_Day21_Model_Path)
Reg_Day28_Model_Path = 'Regression_On_Reprogramming_Data/1000_Genes_Two_Classes_Day28/Features_1000_Dropout_0.25_NumLayer2_LSTM/model'
Reg_Day28_Model = load_model(Reg_Day28_Model_Path)

for DROP_OUT in drop_out_list: 
    for MODEL_TYPE in model_type_list: 
        for NUM_LAYER in num_layer_list: 
            folder = "Classification_On_Encoded_Reprogramming_Data/{4}_Genes_Not_Encoded_Two_Classes/Features_{0}_Dropout_{1}_NumLayer_{2}_ModelType_{3}/".format(FEATURES, DROP_OUT, NUM_LAYER, MODEL_TYPE, n_top_genes)
            filepath = "model"
            
            model = load_model(folder+filepath)
            y_Gened = model.predict(X_Gened)
            y_Gened = np.array(y_Gened)
            y_Gened_classes = np.argmax(y_Gened, axis=1)
            y_Gened_classes = pd.DataFrame(y_Gened_classes, columns=['class_info'])
            
            RESULT_LIST = []
            X_mod_i = X.copy()
            
            for i in top_20_inds: 
                X_mod_i[:, :, i] = X_mod_i[:, :, i] * 5.0
            Predicted_Day21 = Reg_Day21_Model.predict(X_mod_i)
            Predicted_Day21 = np.array([Predicted_Day21], dtype=np.float32)
            Predicted_Day21 = np.swapaxes(Predicted_Day21, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day21), axis=1, dtype=np.float32)
            
            Predicted_Day28 = Reg_Day28_Model.predict(X_mod_i)
            Predicted_Day28 = np.array([Predicted_Day28], dtype=np.float32)
            Predicted_Day28 = np.swapaxes(Predicted_Day28, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day28), axis=1, dtype=np.float32)
            
            y_Gened_mod_i = model.predict(X_mod_i)
            y_Gened_mod_i = np.array(y_Gened_mod_i)
            delta_p = y_Gened_mod_i[:, 1] - y_Gened[:, 1]
            RESULT_LIST.append(delta_p)
            
            RESULT_LIST = np.array(RESULT_LIST)
            RESULT_LIST = np.swapaxes(RESULT_LIST, 0, 1)
            
            RESULT_DF = pd.DataFrame(RESULT_LIST)
            RESULT_DF = pd.concat((RESULT_DF, y_Gened_classes), axis=1)
            RESULT_DF.to_csv("Perturb_Reprogramming_{0}_Genes_Not_Encoded_Day_21_28_Gened_Mult5_Change_In_Reprog_Result_With_Init_Class_Info_Top_20.csv".format(n_top_genes), index=False)
            
            del X_mod_i, Predicted_Day21, Predicted_Day28, RESULT_LIST, RESULT_DF
            gc.collect()

            RESULT_LIST = []
            X_mod_i = X.copy()
            
            for i in low_20_inds: 
                X_mod_i[:, :, i] = X_mod_i[:, :, i] * 5.0
            Predicted_Day21 = Reg_Day21_Model.predict(X_mod_i)
            Predicted_Day21 = np.array([Predicted_Day21], dtype=np.float32)
            Predicted_Day21 = np.swapaxes(Predicted_Day21, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day21), axis=1, dtype=np.float32)
            
            Predicted_Day28 = Reg_Day28_Model.predict(X_mod_i)
            Predicted_Day28 = np.array([Predicted_Day28], dtype=np.float32)
            Predicted_Day28 = np.swapaxes(Predicted_Day28, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day28), axis=1, dtype=np.float32)
            
            y_Gened_mod_i = model.predict(X_mod_i)
            y_Gened_mod_i = np.array(y_Gened_mod_i)
            delta_p = y_Gened_mod_i[:, 1] - y_Gened[:, 1]
            RESULT_LIST.append(delta_p)
            
            RESULT_LIST = np.array(RESULT_LIST)
            RESULT_LIST = np.swapaxes(RESULT_LIST, 0, 1)
            
            RESULT_DF = pd.DataFrame(RESULT_LIST)
            RESULT_DF = pd.concat((RESULT_DF, y_Gened_classes), axis=1)
            RESULT_DF.to_csv("Perturb_Reprogramming_{0}_Genes_Not_Encoded_Day_21_28_Gened_Mult5_Change_In_Reprog_Result_With_Init_Class_Info_Low_20.csv".format(n_top_genes), index=False)

            del X_mod_i, Predicted_Day21, Predicted_Day28, RESULT_LIST, RESULT_DF
            gc.collect()
            
            RESULT_LIST = []
            X_mod_i = X.copy()
            
            for i in top_100_inds: 
                X_mod_i[:, :, i] = X_mod_i[:, :, i] * 5.0
            Predicted_Day21 = Reg_Day21_Model.predict(X_mod_i)
            Predicted_Day21 = np.array([Predicted_Day21], dtype=np.float32)
            Predicted_Day21 = np.swapaxes(Predicted_Day21, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day21), axis=1, dtype=np.float32)
            
            Predicted_Day28 = Reg_Day28_Model.predict(X_mod_i)
            Predicted_Day28 = np.array([Predicted_Day28], dtype=np.float32)
            Predicted_Day28 = np.swapaxes(Predicted_Day28, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day28), axis=1, dtype=np.float32)
            
            y_Gened_mod_i = model.predict(X_mod_i)
            y_Gened_mod_i = np.array(y_Gened_mod_i)
            delta_p = y_Gened_mod_i[:, 1] - y_Gened[:, 1]
            RESULT_LIST.append(delta_p)
            
            RESULT_LIST = np.array(RESULT_LIST)
            RESULT_LIST = np.swapaxes(RESULT_LIST, 0, 1)
            
            RESULT_DF = pd.DataFrame(RESULT_LIST)
            RESULT_DF = pd.concat((RESULT_DF, y_Gened_classes), axis=1)
            RESULT_DF.to_csv("Perturb_Reprogramming_{0}_Genes_Not_Encoded_Day_21_28_Gened_Mult5_Change_In_Reprog_Result_With_Init_Class_Info_Top_100.csv".format(n_top_genes), index=False)
            
            del X_mod_i, Predicted_Day21, Predicted_Day28, RESULT_LIST, RESULT_DF
            gc.collect()
            
            RESULT_LIST = []
            X_mod_i = X.copy()
            
            for i in low_100_inds: 
                X_mod_i[:, :, i] = X_mod_i[:, :, i] * 5.0
            Predicted_Day21 = Reg_Day21_Model.predict(X_mod_i)
            Predicted_Day21 = np.array([Predicted_Day21], dtype=np.float32)
            Predicted_Day21 = np.swapaxes(Predicted_Day21, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day21), axis=1, dtype=np.float32)
            
            Predicted_Day28 = Reg_Day28_Model.predict(X_mod_i)
            Predicted_Day28 = np.array([Predicted_Day28], dtype=np.float32)
            Predicted_Day28 = np.swapaxes(Predicted_Day28, 0, 1)
            X_mod_i = np.concatenate((X_mod_i, Predicted_Day28), axis=1, dtype=np.float32)
            
            y_Gened_mod_i = model.predict(X_mod_i)
            y_Gened_mod_i = np.array(y_Gened_mod_i)
            delta_p = y_Gened_mod_i[:, 1] - y_Gened[:, 1]
            RESULT_LIST.append(delta_p)
            
            RESULT_LIST = np.array(RESULT_LIST)
            RESULT_LIST = np.swapaxes(RESULT_LIST, 0, 1)
            
            RESULT_DF = pd.DataFrame(RESULT_LIST)
            RESULT_DF = pd.concat((RESULT_DF, y_Gened_classes), axis=1)
            RESULT_DF.to_csv("Perturb_Reprogramming_{0}_Genes_Not_Encoded_Day_21_28_Gened_Mult5_Change_In_Reprog_Result_With_Init_Class_Info_Low_100.csv".format(n_top_genes), index=False)
            
            