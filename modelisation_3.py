# -*- coding: utf-8 -*-
"""modelisation_3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1W1PeIcLcLn7y-zynyhFpcljoS5EHu3-x
"""

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# matplotlib and seaborn for plotting
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 22
import seaborn as sns

# Suppress warnings from pandas
import warnings
warnings.filterwarnings('ignore')

# Memory management
import gc

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.metrics import make_scorer

from sklearn.metrics import f1_score, confusion_matrix, classification_report, recall_score, roc_auc_score, accuracy
from sklearn.model_selection import learning_curve

from sklearn.model_selection import cross_val_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV


# import des données traitées
path_data = "C:\\Users\\Utilisateur\\formation_datascientist\\projet_7_implementez_un_modèle_de_scoring\\"
train_complete = pd.read_csv(path_data + 'train_complete.csv')

X_train_initial = train_complete.drop('TARGET', axis=1)
y_train_initial = train_complete.TARGET


def train_test_spliter(X, y, sampling=0.3):
  # extraction d'un échantillon de sampling % de l'ensemble
  X_train, X_extracted, y_train, y_extracted = train_test_split(X, y, test_size=sampling, stratify=y, random_state=0)
  # création d'un set de test
  X_train, X_test, y_train, y_test = train_test_split(X_extracted, y_extracted, test_size=0.2, stratify=y_extracted, random_state=0)
  # création d'un set de validation
  X_train, X_valid, y_train, y_valid = train_test_split(X_train, y_train, test_size=0.2, stratify=y_train, random_state=0)
  return X_train, y_train, X_valid, y_valid, X_test, y_test


#!pip install xgboost


imputer_mean = SimpleImputer(strategy='mean')
#imputer_knn = KNNImputer(n_neighbors=5)

smote = SMOTE(random_state=0)


model_logistic_1 = Pipeline([('imputer', imputer_mean), ('scaler', StandardScaler()), ('smote', smote), ('classifier', LogisticRegression())])
#model_logistic_2 = Pipeline([('imputer', imputer_knn), ('scaler', StandardScaler()), ('smote', smote), ('classifier', LogisticRegression())])
model_rdmfst_1 = Pipeline([('imputer', imputer_mean), ('smote', smote), ('classifier', RandomForestClassifier(random_state=0))])
model_rdmfst_2 = Pipeline([('imputer', imputer_mean), ('classifier', RandomForestClassifier(class_weight='balanced', random_state=0))])
model_xgb_1 = Pipeline([('imputer', imputer_mean), ('smote', smote), ('classifier', XGBClassifier(random_state=0))])
model_xgb_2 = Pipeline([('classifier', XGBClassifier(random_state=0, scale_pos_weight=8))])
model_lgb_1 = Pipeline([('imputer', imputer_mean), ('smote', smote), ('classifier', LGBMClassifier(random_state=0))])
model_lgb_2 = Pipeline([('classifier', LGBMClassifier(random_state=0, is_unbalance=True))])


def score_metier(y_true, ypred):
  conf_matrix = confusion_matrix(y_true, ypred)
  conf_rav = conf_matrix.ravel()
  FN, FP = conf_rav[2], conf_rav[1]
  return 10 * FN + FP


scorer_metier =  make_scorer(score_metier, greater_is_better=False)


def ComputeAndPrintPerformance(y_valid, ypred_valid, y_valid_hat, y_train, ypred_train, print=False):
    
  # performances sur la validation
  confusion_mat = confusion_matrix(y_valid, ypred_valid)
  class_report = classification_report(y_valid, ypred_valid)
  score_fn = score_metier(y_valid, ypred_valid)
  roc = roc_auc_score(y_valid, y_valid_hat)
  acc = accuracy(y_valid, ypred_valid)
  f1 = f1_score(y_valid, ypred_valid)
 
  # détection de l'overfitting
  train_recall = round(recall_score(y_train, ypred_train), 2)
  valid_recall = round(recall_score(y_valid, ypred_valid), 2)
  # calcul indicateur overfitting : overfitting si proche de 0, sinon proche de 1
  overfit_indicator = round(((1 - train_recall) + (valid_recall / train_recall)) / 2, 2)
  
  # affichage des résultats si demandé
  if print == True:
      print('------------------------------')
      print('confusion_matrix :\n', confusion_mat)
      print('classification_report :\n', class_report)
      print('score_metier = ' , score_fn)
      print('roc auc score = ' , roc)
      print('accuracy = ' , acc)
      print('f1-score = ' , f1)
      print('overfitting indicators : \n')
      print("train recall = ", train_recall)
      print("valid recall = ", valid_recall)
      print('delta train - valid = ', round(train_recall - valid_recall, 2))
      print('overfit_indicator : ', overfit_indicator)
      print('------------------------------')


def evaluation(model):

  model.fit(X_train, y_train)
  
  ypred_valid = model.predict(X_valid)
  y_valid_hat = model.decision_function(X_valid, y_valid)
  ypred_train = model.predict(X_train)

  ComputeAndPrintPerformance(y_valid, ypred_valid, y_valid_hat, y_train, ypred_train, print=True)
  


dict_of_models = {
    'model_logistic_1' : model_logistic_1,
    'model_rdmfst_1' : model_rdmfst_1,
    'model_rdmfst_2' : model_rdmfst_2,
    'model_xgb_1' : model_xgb_1,
    'model_xgb_2' : model_xgb_2,
    'model_lgb_1' : model_lgb_1,
    'model_lgb_2' : model_lgb_2
}

X_train, y_train, X_valid, y_valid, X_test, y_test = train_test_spliter(X_train_initial, y_train_initial, sampling=0.2)

print(X_train.shape)
print(X_valid.shape)

for name, model in dict_of_models.items():
  print(name)
  evaluation(model)
  
  
  
  
def evaluationCV(model, params, random = False):

  search = GridSearchCV(model, params, scoring=scorer_metier, cv=4)
  search.fit(X_train, y_train)
  ypred_valid = model.predict(X_valid)
  ypred_train = model.predict(X_train)

  print(confusion_matrix(y_valid, ypred_valid))
  print(classification_report(y_valid, ypred_valid))
  print('score_metier' , score_metier(y_valid, ypred_valid))
  train_recall, valid_recall = round(recall_score(y_train, ypred_train), 2), round(recall_score(y_valid, ypred_valid), 2)
  print("train recall = ", train_recall)
  print("valid recall = ", valid_recall)
  print('delta train - valid = ', round(train_recall - valid_recall, 2))
  overfit_indicator = round(((1 - train_recall) + (valid_recall / train_recall)) / 2, 2) # overfitting si proche de 0, bon si proche de 1
  print('overfit_indicator : ', overfit_indicator)