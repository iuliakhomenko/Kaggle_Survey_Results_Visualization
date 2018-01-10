
# coding: utf-8

import pandas as pd
import numpy as np

#download dataset
path = '/Users/iulia/Google Drive/DAND/P7/final_project/kaggle-survey-2017/multipleChoiceResponses.csv'
df = pd.DataFrame.from_csv(path = path, )
df = df.reset_index()
print df.shape

#downloading exchange rates, converting all 'CompensationAmount' values to USD into new column "Compensation_USD"
ex_rates_df = pd.DataFrame.from_csv(path = '/Users/iulia/Google Drive/DAND/P7/final_project/kaggle-survey-2017/conversionRates.csv')

df = pd.merge(df, ex_rates_df, how = 'left', left_on = ['CompensationCurrency'], right_on = ['originCountry'])

df['CompensationAmount'] = df['CompensationAmount'].str.replace(',','')
df['CompensationAmount'] = df['CompensationAmount'].str.replace('-','')

df['CompensationAmount'] = pd.to_numeric(df['CompensationAmount'])
df['Compensation_USD'] = df['CompensationAmount']*df['exchangeRate']


#Helper function for replacing values in selected column
def replace_value(df, column_name, value_to_replace, target_value):
    df[[column_name]] = df[[column_name]].replace(value_to_replace, target_value)

#Cleaning "Gender" values
replace_value(df,'GenderSelect','Non-binary, genderqueer, or gender non-conforming',
             'Non-binary, genderqueer, gender non-conforming or different identity')
replace_value(df, 'GenderSelect','A different identity', 
              'Non-binary, genderqueer, gender non-conforming or different identity')

#Cleaning 'JobSatisfaction' to numeric
replace_value(df,'JobSatisfaction','10 - Highly Satisfied', 10)
replace_value (df,'JobSatisfaction','1 - Highly Dissatisfied', 1)
replace_value(df,'JobSatisfaction','I prefer not to share', np.nan )
df['JobSatisfaction'] = pd.to_numeric(df['JobSatisfaction'])

#Re-grouping 8 categories in 'EmployerSize' column into 5 categories
replace_value(df, 'EmployerSize','10,000 or more employees', '5000+ employees')
replace_value (df,'EmployerSize','5,000 to 9,999 employees', '5000+ employees')

replace_value (df,'EmployerSize','500 to 999 employees', '100 to 999 employees')
replace_value (df,'EmployerSize','100 to 499 employees', '100 to 999 employees')

replace_value (df,'EmployerSize','20 to 99 employees', '10 to 99 employees')
replace_value (df,'EmployerSize','10 to 19 employees', '10 to 99 employees')

#Selecting data that is relevant for analysis (only respondents who are employed and write code at work)
df_workers = df[(df['EmploymentStatus'] == "Employed full-time") | (df['EmploymentStatus'] == "Employed part-time")|
                     (df['EmploymentStatus'] == "Independent contractor, freelancer, or self-employed")]
df_coding_workers = df_workers[df_workers['CodeWriter'] == 'Yes']
df_coding_workers = df_coding_workers.dropna(axis = 1, how = 'all')
df_coding_workers.to_csv(path_or_buf= '/Users/iulia/Google Drive/DAND/P7/final_project/coding_workers.csv', index = False)


#Creating seperate datasets for respondent with Current Job Title as DataScientist and others (this
#was needed to visualize salary comparison in Tableau project)
df_data_scientist = df[df['CurrentJobTitleSelect'] == 'Data Scientist']
df_others = df[df['CurrentJobTitleSelect'] != 'Data Scientist']
df_data_scientist.to_csv(path_or_buf= '/Users/iulia/Google Drive/DAND/P7/final_project/data_scientists.csv', index = False)
df_others.to_csv(path_or_buf = '/Users/iulia/Google Drive/DAND/P7/final_project/others.csv', index = False )


#Helper function to deal with multiple choice questions in Kaggle survey (many 
#values separated by comma in one cell). In order to dig into those values we 
#needed to 'unlistify' them into seperate rows thus creating new dataset for each
#multiple choice question we wanted to visualize in Tableau

def tidy_split(df, column, sep='|', keep=False):
    
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    return new_df.to_csv(path_or_buf='/Users/iulia/Google Drive/DAND/P7/final_project/%s_df.csv'%(column))


#Creating separate datasets to visualize 4 columns 
tidy_split(df_coding_workers,'WorkChallengesSelect', sep = ',', keep = False)
tidy_split(df_coding_workers,'WorkAlgorithmsSelect', sep =',', keep = False)
tidy_split(df_coding_workers, 'PastJobTitlesSelect', sep = ',', keep = False)
tidy_split(df_coding_workers, 'LearningPlatformSelect', sep = ',', keep = False)


