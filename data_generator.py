import random
import requests
import pandas as pd

from itertools import combinations
from scipy.optimize import linprog

from task_types import Gender, Goal, Human_params

class DataGenerator:
    @staticmethod
    def fill_people_table(n, first_goal=Goal.maintain, first_gender=Gender.male, first_n=0) -> pd.DataFrame:
        min_age = 10
        max_age = 80
        min_height = 130
        max_height = 230
        min_weight = 40
        max_weight = 160
        min_activity_level = 1
        max_activity_level = 7

        url = "https://fitness-calculator.p.rapidapi.com/macrocalculator"

        f = open("key.txt", "r")

        request_headers = {
            "X-RapidAPI-Key": f.read(),
            "X-RapidAPI-Host": "fitness-calculator.p.rapidapi.com"
        }

        df_main = pd.DataFrame(columns=[
            'age', 
            'gender', 
            'height', 
            'weight', 
            'activitylevel', 
            'goal', 
            'protein', 
            'fat', 
            'carbs'
        ])

        for goal in list(Goal):
                if goal.value < first_goal.value:
                    continue
                for gender in list(Gender):
                    if gender.value < first_gender.value and goal.value == first_goal.value:
                        continue
                    for i in range(n):
                        if i < first_n and gender.value == first_gender.value and goal.value == first_goal.value:
                            continue
                        hp = Human_params(
                            random.randint(min_age, max_age),
                            gender,
                            random.randint(min_height, max_height),
                            random.randint(min_weight, max_weight),
                            random.randint(min_activity_level, max_activity_level),
                            goal
                        )
                        response = requests.get(url, headers=request_headers, params=hp.get_dict())

                        if response.ok:
                            pfc_df = pd.DataFrame(response.json()['data']['balanced'], index=[0])
                            hp_df = hp.get_df()
                            
                            hp_df = hp_df.assign(**pfc_df)

                            df_main = pd.concat([df_main, hp_df], ignore_index = True)
                            df_main.reset_index()
                        else:
                            print(f'aborted at goal={goal} and gender={gender} and n={i}')
                            return df_main
        return df_main

    @staticmethod
    def fill_sample(path, product_path):
        df_main = pd.DataFrame(columns=[
            'age', 
            'gender', 
            'height', 
            'weight', 
            'activitylevel', 
            'goal', 
            'protein', 
            'fat', 
            'carbs',
            'products_protein',
            'products_fat',
            'products_carbs'
        ])

        df = pd.read_excel(path).drop(columns=['Unnamed: 0'])
        product_df = pd.read_excel(product_path).drop(columns=['Unnamed: 0'])

        product_comb = []
        
        for i in range(1, len(product_df) + 1):
            product_comb += combinations(product_df['index'].to_list(), i)

        num = len(product_comb)

        for j in product_comb:
            for i in range(len(df)):
                row = df.loc[[i]]
                products_protein = [0] * len(product_df)
                products_fat = [0] * len(product_df)
                products_carbs = [0] * len(product_df)

                for k in j:
                    products_protein[k] = random.uniform(0.1, 30)
                    products_fat[k] = random.uniform(0.1, 30)
                    products_carbs[k] = random.uniform(0.1, 30)


                row.insert(len(row.columns), "products_protein", [products_protein], True)
                row.insert(len(row.columns), "products_fat", [products_fat], True)
                row.insert(len(row.columns), "products_carbs", [products_carbs], True)

                df_main = pd.concat([df_main, row], ignore_index = True)
                df_main.reset_index()

            num -= 1
            print(num)
            
        return df_main

    @staticmethod
    def _get_matrix(main_df: pd.DataFrame, index):
        A = []
        b = []

        pr_list = [-1 * x for x in main_df["products_protein"][index]]
        fat_list = [-1 * x for x in main_df["products_fat"][index]]
        carbs_list = [-1 * x for x in main_df["products_carbs"][index]]

        indeces = []
        true_pr_list = []
        true_fat_list = []
        true_carbs_list = []
        for p, f, c, i in zip(pr_list, fat_list, carbs_list, range(len(fat_list))):
            if p == f == c == 0:
                continue
            indeces.append(i)
            true_pr_list.append(p)
            true_fat_list.append(f)
            true_carbs_list.append(c)
        
        num_product = len(true_pr_list)

        if sum(pr_list) != 0:
            A.append(true_pr_list)
            b.append(-main_df["protein"][index])
        if sum(fat_list) != 0:
            A.append(true_fat_list)
            b.append(-main_df["fat"][index])
        if sum(carbs_list) != 0:
            A.append(true_carbs_list)
            b.append(-main_df["carbs"][index])
        
        for i in range(num_product):
            for j in range(num_product):
                if i == j:
                    continue
                tmp = [0] * num_product
                tmp[i] = -30
                tmp[j] = 1
                A.append(tmp)
                b.append(0)

        return A, b, indeces

    @staticmethod
    def fill_answer(path):
        df = pd.read_json(path)

        results = []

        num = len(df)

        for i in range(len(df)):
            A, b, indeces = DataGenerator._get_matrix(df, i)

            num_product = len(indeces)

            c = [1] * num_product

            bnds = []
            for _ in indeces:
                bnds.append([0.3, None])

            if len(A) == 0:
                res = [0] * num_product
            else:
                res = [x for x in linprog(c, A_ub=A, b_ub=b, bounds=bnds).x]

            res_list = [0] * len(df["products_protein"][i])
            for ind, r in zip(indeces, res):
                res_list[ind] = r
                
            results.append(res_list)

            num -= 1
            print(num)

        df.insert(len(df.columns), "results", results, True)
        df = df.drop('protein', axis=1)
        df = df.drop('fat', axis=1)
        df = df.drop('carbs', axis=1)

        return df