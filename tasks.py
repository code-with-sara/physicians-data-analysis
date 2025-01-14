# -*- coding: utf-8 -*-
"""tasks.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1P8FooRwJnWICILQTlxMgmNAWiol0hv6S
"""

import pandas as pd

data4_path = r'C:\Users\RC\Downloads\rounding_data_fac_scheduling_contract.xlsx'
rounding_data_contract = pd.read_excel(data4_path, sheet_name='Sheet1')
data6_path = r'C:\Users\RC\Downloads\physician_names.xlsx'
physician_name = pd.read_excel(data6_path)
data7_path = r'C:\Users\RC\Downloads\rounding_scheduale_updated_Data_round_consult_timesept_2024.xlsx'
schedule_round_consult = pd.read_excel(data7_path, sheet_name='Sheet1')
data8_path = r'C:\Users\RC\Downloads\round_patient_rp_starttime_sept_2024.xlsx'
round_patient = pd.read_excel(data8_path, sheet_name='Sheet1')
data9_path = r'C:\Users\RC\Downloads\facility_active_status_sept_2024.xlsx'
fac_active_status= pd.read_excel(data9_path, sheet_name='Sheet1')

pd.set_option('display.max_columns', None)

physician_name['Physician'] = physician_name['LastName'] + ' ' + physician_name['FirstName']

"""## **Master** **Dataset**"""

def process_dataframe(schedule_round_consult, fac_active_status, round_patient, physician_name, rounding_data_contract):
    # Merging the schedule_round_consult with fac_active_status
    r_sch = pd.merge(schedule_round_consult, fac_active_status, left_on='rc_fac_key', right_on='fac_key', how='left')

    # Processing the 'rp_date' field in round_patient
    round_patient['rp_date'] = pd.to_datetime(round_patient['rp_starttime'])
    round_patient['rp_date'] = pd.to_datetime(round_patient['rp_date'].dt.date)

    # Converting 'rc_date' to datetime in r_sch
    r_sch['rc_date'] = pd.to_datetime(r_sch['rc_date_of_consult'])

    # Merging r_sch and round_patient
    r_sch_rp = pd.merge(r_sch, round_patient, left_on=['rc_phy_key', 'rc_fac_key', 'rc_date'], right_on=['rp_phy_key', 'rp_fac_key', 'rp_date'], how='left')

    # Renaming columns
    r_sch_rp = r_sch_rp.rename(columns={'fac_name': 'Facility'})

    # Calculating rounding and patient durations
    r_sch_rp['rct_rounding_duration'] = pd.to_datetime(r_sch_rp['rct_rounding_end_time']) - pd.to_datetime(r_sch_rp['rct_rounding_start_time'])
    r_sch_rp['rp_duration'] = pd.to_datetime(r_sch_rp['rp_endtime']) - pd.to_datetime(r_sch_rp['rp_starttime'])

    # Extracting the day of the week
    r_sch_rp['day_of_week'] = pd.to_datetime(r_sch_rp['rc_date']).dt.day

    # Merging with physician_name
    r_sch_rp_ph = pd.merge(r_sch_rp, physician_name[['ID', 'IsActive', 'IsDisable', 'Physician']], left_on='rc_phy_key', right_on='ID', how='left')

    # Merging with rounding_data_contract and dropping duplicates
    rsch_rp_ph = pd.merge(r_sch_rp_ph, rounding_data_contract[['ucd_title', 'cas_fac_key']].drop_duplicates(), left_on='rc_fac_key', right_on='cas_fac_key', how='left')

    # Renaming columns
    rsch_rp_ph = rsch_rp_ph.rename(columns={
        'ucd_title': 'rounding_contract_type',
        'IsActive': 'phy_is_active',
        'IsDisable': 'phy_is_Disable'
    })

    # Dropping unnecessary columns
    rsch_rp_ph.drop(columns=['ID', 'cas_fac_key', 'rp_fac_key', 'rp_phy_key', 'fac_key'], inplace=True)

    # Aggregating new and follow-up cases
    new_cases = rsch_rp_ph[rsch_rp_ph['cas_ctp_key'] == 164.0].groupby(['Facility', 'rp_date']).count().reset_index()
    .rename(columns={'cas_ctp_key': 'new_case_count'})[['new_case_count', 'Facility', 'rp_date']]
    follow_up_cases = rsch_rp_ph[rsch_rp_ph['cas_ctp_key'] == 163.0].groupby(['Facility', 'rp_date']).count().reset_index()
    .rename(columns={'cas_ctp_key': 'followup_case_count'})[['followup_case_count', 'Facility', 'rp_date']]

    # Returning the final processed dataframe
    return rsch_rp_ph


processed_df = process_dataframe(schedule_round_consult, fac_active_status, round_patient, physician_name, rounding_data_contract)
processed_df.head()

"""Priority"""

def phy_priority(processed_df):

    phys_priority = processed_df.groupby(['Physician', 'Facility'])['rp_date'].nunique().unstack(fill_value=0)
    return phys_priority

phy_priority(processed_df)

"""credentialPriority"""

def get_credential(processed_df):

    credentials = ((processed_df.groupby(['Physician', 'Facility'])['rp_date'].nunique().unstack(fill_value=0)) > 0).astype(int)
    return credentials

get_credential(processed_df)

"""List of Facilities on particular date"""

def get_facilities_on_input_date(processed_df, input_date):

    # Filter DataFrame based on the provided date
    filtered_df = processed_df[processed_df['rp_date'] == input_date]

    # Get unique facilities for that date
    facilities = filtered_df['Facility'].unique().tolist()

    # Return the list of facilities or a message if none are found
    if len(facilities) > 0:
        return facilities
    else:
        return f"No facilities found for the date {input_date}."

input_date = "2023-08-31"  # Manually provide the date
facilities = get_facilities_on_input_date(processed_df, input_date)
facilities

"""List of every Physicians according to date"""

def get_physicians_on_input_date(processed_df, input_date):

    # Filter DataFrame based on the provided date
    filtered_df = processed_df[processed_df['rp_date'] == input_date]

    # Get unique physicians for that date
    physcian = filtered_df['Physician'].unique()

    # Return the list of physcians or a message if none are found
    if len(physcian) > 0:
        return physcian
    else:
        return f"No physcians found for the date {input_date}."

input_date = "2023-08-31"  # Manually provide the date
physcians = get_physicians_on_input_date(processed_df, input_date)
physcians

result_df = processed_df.groupby(['Facility']).agg(
            avg_new_case_count=('cas_ctp_key', (lambda x: (x == 164.0).mean())),  # Average of new cases
            total_cases=('cas_ctp_key', 'size')  # Keep total cases count for reference
        ).reset_index()

"""Average no of cases for each Facility"""

# case_counts(processed_df, case_type='followup_case').sort_values('avg_followup_case_count')

"""Time Per Case"""

def calculate_time_per_case_per_day(processed_df):

    # Convert the rounding times to timedelta if needed (assuming they are in a correct format)
    processed_df['rct_rounding_duration'] = pd.to_timedelta(processed_df['rct_rounding_duration'], errors='coerce')

    # Group by Physician and rp_date (to get daily totals for each physician)
    grouped = processed_df.groupby(['Physician', 'rp_date'])

    # Calculate total time spent by each physician per day
    total_duration_per_day = grouped['rct_rounding_duration'].sum()

    # Count the number of cases per physician per day
    cases_per_day = grouped.size()

    # Create a new DataFrame to return the results
    result = pd.DataFrame({
        'Total Time Spent': total_duration_per_day,
        'Number of Cases': cases_per_day,
    })

    # Calculate the average time per case by dividing total time spent by the number of cases
    result['Average Time Per Case'] = result['Total Time Spent'] / result['Number of Cases']

    return result

# Example usage:
avg_time_per_case_per_day_df = calculate_time_per_case_per_day(processed_df)
avg_time_per_case_per_day_df

"""cases per Facility"""

def calculate_cases_per_facility(processed_df, facility_column):

    # Group by facility
    grouped = processed_df.groupby(facility_column)

    # Total cases per facility
    total_cases = grouped.size()

    # Count new cases (assuming 164.0 represents new cases)
    new_cases = grouped.apply(lambda x: (x['cas_ctp_key'] == 164.0).sum())

    # Count follow-up cases (assuming 163.0 represents follow-up cases)
    follow_up_cases = grouped.apply(lambda x: (x['cas_ctp_key'] == 163.0).sum())

    # Calculate the average new and follow-up cases per facility
    avg_new_cases = new_cases / total_cases
    avg_follow_up_cases = follow_up_cases / total_cases

    # Create a DataFrame to return results
    result = pd.DataFrame({
        'Total Cases': total_cases,
        'New Cases': new_cases,
        'Follow-up Cases': follow_up_cases,
        'Average New Cases': avg_new_cases,
        'Average Follow-up Cases': avg_follow_up_cases
    })

    return result

cases_per_facility_df = calculate_cases_per_facility(processed_df, 'Facility')
cases_per_facility_df

"""total time required matrix"""

grouped = processed_df.groupby(['Physician', 'Facility'])['rct_rounding_duration'].unique().unstack(fill_value=pd.Timedelta(0))
# grouped

def calculate_total_time_matrix(processed_df, physician_column, facility_column, duration_column):

    processed_df[duration_column] = pd.to_timedelta(processed_df[duration_column], errors='coerce')

    grouped = processed_df.groupby([physician_column, facility_column])[duration_column].unique().unstack(fill_value=pd.Timedelta(0))
    return grouped

time_matrix_updated = calculate_total_time_matrix(processed_df, 'Physician', 'Facility', 'rp_duration')
time_matrix_updated.head()

"""dataset for ML model"""

def case_counts(processed_df):
    result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
        new_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 164.0).sum()),
        followup_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 163.0).sum()),
        total_cases = ('cas_ctp_key', 'size')
    ).reset_index()


    return result_df

cases = case_counts(processed_df)
cases

def time_per_case(processed_df):
    case_time = processed_df.groupby(['Physician', 'Facility'])['rct_rounding_duration'].sum().dt.total_seconds().unstack(fill_value=0)
    return case_time

time_per_case(processed_df)

def case_counts_per_day(processed_df, case_type):
    # Ensure 'rp_date' is in datetime format
    processed_df['rp_date'] = pd.to_datetime(processed_df['rp_date'], errors='coerce')

    if case_type == 'new_case':
        # Group by Facility and rp_date, then count new cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            new_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 164.0).sum()),  # Count of new cases (164)
        ).reset_index()

    elif case_type == 'followup_case':
        # Group by Facility and rp_date, then count follow-up cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            followup_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 163.0).sum())  # Count of follow-up cases (163)
        ).reset_index()

    elif case_type == 'total_cases':
        # Group by Facility and rp_date, then count total cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            total_cases_count=('cas_ctp_key', 'size')  # Count total cases per day
        ).reset_index()

    else:
        raise ValueError("Invalid case_type. Use 'new_case', 'followup_case', or 'total_cases'.")

    return result_df
case_counts_per_day(processed_df, 'new_case')

"""Time per case"""

def time_per_case(processed_df):
    case_time = processed_df.groupby(['Physician', 'Facility'])['rct_rounding_duration'].sum().dt.total_seconds().unstack(fill_value=0)
    return case_time

time = time_per_case(processed_df)
time

# Convert the 'rct_rounding_duration' column to a duration in days to calculate cases per day
processed_df['rct_rounding_duration_days'] = pd.to_timedelta(processed_df['rct_rounding_duration'], errors='coerce').dt.total_seconds() / (60 * 60 * 24)

# Filter out rows where 'rct_rounding_duration_days' is NaN
filtered_data = processed_df.dropna(subset=['rct_rounding_duration_days'])

# Group by 'Facility' and calculate cases per day for each case type
case_per_day = filtered_data.groupby('Facility').agg(
    new_case_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: ((x == 164.0).sum()) / filtered_data['rct_rounding_duration_days'].sum()),
    followup_case_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: ((x == 163.0).sum()) / filtered_data['rct_rounding_duration_days'].sum()),
    total_cases_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: x.size / filtered_data['rct_rounding_duration_days'].sum())
).reset_index()
case_per_day

def case_counts_per_day(processed_df, case_type):
    # Ensure 'rp_date' is in datetime format
    processed_df['rp_date'] = pd.to_datetime(processed_df['rp_date'], errors='coerce')

    if case_type == 'new_case':
        # Group by Facility and rp_date, then count new cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            new_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 164.0).sum()),  # Count of new cases (164)
        ).reset_index()

    elif case_type == 'followup_case':
        # Group by Facility and rp_date, then count follow-up cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            followup_case_count=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 163.0).sum())  # Count of follow-up cases (163)
        ).reset_index()

    elif case_type == 'total_cases':
        # Group by Facility and rp_date, then count total cases per day
        result_df = processed_df.groupby(['Facility', 'rp_date']).agg(
            total_cases_count=('cas_ctp_key', 'size')  # Count total cases per day
        ).reset_index()

    else:
        raise ValueError("Invalid case_type. Use 'new_case', 'followup_case', or 'total_cases'.")

    return result_df
case_counts_per_day(processed_df, 'followup_case')

def case_per_day_by_facility(processed_df):
    # Convert rct_rounding_duration to numeric days
    processed_df['rct_rounding_duration_days'] = pd.to_timedelta(processed_df['rct_rounding_duration'], errors='coerce').dt.total_seconds() / (60 * 60 * 24)

    # Drop rows with invalid duration values
    filtered_data = processed_df.dropna(subset=['rct_rounding_duration_days'])

    # Group by Facility and calculate cases per day for each case type
    case_per_day = filtered_data.groupby('Facility').agg(
        new_case_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 164.0).sum() / filtered_data.loc[x.index, 'rct_rounding_duration_days'].sum()),
        followup_case_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: (x == 163.0).sum() / filtered_data.loc[x.index, 'rct_rounding_duration_days'].sum()),
        total_cases_per_day=pd.NamedAgg(column='cas_ctp_key', aggfunc=lambda x: x.size / filtered_data.loc[x.index, 'rct_rounding_duration_days'].sum())
    ).reset_index()

    return case_per_day
case_per_day_by_facility(processed_df)

processed_df['rct_rounding_duration']

from modules import time_per_case

time_per_case(processed_df)