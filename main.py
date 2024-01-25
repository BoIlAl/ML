import pandas as pd

from task_types import Goal, Gender, Human_params
from data_generator import DataGenerator as dg
from text_recognition import TextRecognizer
from daily_value_prediction import DailyValuePrediction as dvp

def to_one_param_task(df: pd.DataFrame):
    products_protein = []
    products_fat = []
    products_carbs = []
    results = []

    for row in range(len(df)):
        not_null = -1
        for ind in range(len(df["products_protein"][row])):
            if df["products_protein"][row][ind] != 0:
                if not_null != -1:
                    not_null = -2
                    break
                not_null = ind
        if not_null == -2:
            break

        products_protein.append(df["products_protein"][row][not_null])
        products_fat.append(df["products_fat"][row][not_null])
        products_carbs.append(df["products_carbs"][row][not_null])
        results.append(df["results"][row][not_null])

    df = df.drop(range(7000, len(df)))
    df = df.drop('products_protein', axis=1)
    df = df.drop('products_fat', axis=1)
    df = df.drop('products_carbs', axis=1)
    df = df.drop('results', axis=1)

    df.insert(len(df.columns), "products_protein", products_protein, True)
    df.insert(len(df.columns), "products_fat", products_fat, True)
    df.insert(len(df.columns), "products_carbs", products_carbs, True)
    df.insert(len(df.columns), "results", results, True)

    return df

if __name__ == '__main__':
    # people_path = 'dataset/people.xlsx'
    # product_path = 'dataset/products.xlsx'
    # task_path = 'dataset/task.json'
    # dataset_json_path = 'dataset/dataset.json'
    # dataset_xlsx_path = 'dataset/dataset.xlsx'

    # dg.fill_people_table(100, first_goal=Goal.weightgain, first_gender=Gender.male, first_n=0).to_excel(people_path)
    # dg.fill_sample(people_path, product_path).to_json(task_path)
    # df = dg.fill_answer(task_path)
    # df.to_excel(dataset_xlsx_path)
    # df.to_json(dataset_json_path)
    
    df = to_one_param_task(pd.read_json('dataset/dataset.json'))
    dvp.train(df)

    #df = df.iloc[[6885]]
    #print(machine_learning.get_answer(df.drop('results', axis=1)))

    # hp = Human_params(23, Gender.male, 177, 60, 2, Goal.mildgain)

    # tr = TextRecognizer()
    # pi = tr.extract_product_info(f'dataset/img19.jpg')

    # task = hp.get_df().assign(**pi)
    # print(dvp.get_answer(task))