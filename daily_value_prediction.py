import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn import metrics
import xgboost as xgb

class DailyValuePrediction:

    @staticmethod
    def _search_model_params(x_train, y_train):
        params = { 
            'max_depth': [2, 3, 4],
            'learning_rate': [0.05, 0.1, 0.15],
            'n_estimators': [1250, 2500, 2750]
        }

        model = xgb.XGBRegressor(enable_categorical=True)
        search = GridSearchCV(
            estimator=model, 
            param_grid=params, 
            scoring='neg_mean_squared_error', 
            verbose=1
        )

        search.fit(x_train, y_train)
        print("Best parameters:", search.best_params_)
        print("Lowest RMSE: ", (-search.best_score_)**(1/2.0))

    @staticmethod
    def _model_training(x_train, x_test, y_train, y_test):
        params = {
            "objective": "reg:squarederror",
            "n_estimators": 2500,
            "max_depth": 3,
            "learning_rate": 0.1
        }
        
        model = xgb.XGBRegressor(enable_categorical=True, **params)

        eval_set = [(x_test, y_test)]
        model.fit(x_train, y_train, eval_metric="rmse", eval_set=eval_set, verbose=True, early_stopping_rounds=40)
        
        y_predict = model.predict(x_test)

        print('MAE: ', metrics.mean_absolute_error(y_predict, y_test))
        print('RMSE: ', np.sqrt(metrics.mean_squared_error(y_predict, y_test)))
        print('r2: ', np.sqrt(metrics.r2_score(y_predict, y_test)))

        model.save_model('model.json')

    @staticmethod
    def train(df: pd.DataFrame, search_model_params=False):
        x = df.drop('results', axis=1)
        y = df['results']
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.66, random_state = 24)

        categoty_attribs = ['gender', 'activitylevel', 'goal']
        x_train[categoty_attribs] = x_train[categoty_attribs].astype('category')
        x_test[categoty_attribs] = x_test[categoty_attribs].astype('category')

        if search_model_params:
            DailyValuePrediction._search_model_params(x_train, y_train)
        else:
            DailyValuePrediction._model_training(x_train, x_test, y_train, y_test)

    @staticmethod
    def get_answer(df):
        loaded_model = xgb.XGBRegressor()
        loaded_model.load_model('model.json')

        categoty_attribs = ['gender', 'activitylevel', 'goal']
        df[categoty_attribs] = df[categoty_attribs].astype('category')

        answer = loaded_model.predict(df)
        return answer