# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 15:21:26 2022

@author: Shaun
"""
import math
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

SPLIT_NUMBER=10**3

BUTTON_XMLS=['/html/body/div/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/a',
             '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/a']

FIVEK_RACES = [['19WH5K','2019_5k_shamrock_washington_heights'],
                ['18JBJ5K','2018_5k_jingle_prospect'],
                ['18FLXC','2018_5k_fred_van_cortlandt'],
                ['21Seasonal','2021_5k_BK'],
                ['191FY5K','2019_5k_CentPark'],
                ['PS5-19','2019_5k_Harlem']]

TENK_RACES=[['22GGG','2022_10k_GGG_centpark'],['22QUEENS','2022_10k_QNs'],
             ['22MINI','2022_10k_MSCR_centpark'],['22MAN10K','2022_10k_MN_CentPark'],
             ['22JK10K','2022_10k_JK_CentPark']]

HALF_RACES=[['22SIHALF','2022_half_SI'],['22BKH','2022_half_BK'],
            ['H2022','2022_half_UA'],['22FREDHALF','2022_half_fred_centpark'],
            ['FRED20','2020_half_fred_centpark']]


def get_multiple_races():
    for race_url, save_file in FIVEK_RACES:
        get_nyrr_race_data(race_url, save_file)

def get_marathon_data(year):
    """Will pull marathon data for a given year if that year is 2014 or later
    Historical marathons can be pulled by submitting the standard get_nyrr_data
    for the race_url found on NYRR.
    
    Params:
        year (str) = 'yyyy'
    """
    get_nyrr_race_data('M'+year, 'nyc_marathon_'+year+'_data')
    
def get_nyrr_race_data(race_url, save_file=''):
    driver = open_new_webpage(race_url)
    runner_count_xml = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/ul/li[1]/a/span[2]'
    total_runner_count = int(driver.find_element_by_xpath(runner_count_xml).text)
    print('Total Finishers: ' + str(total_runner_count))
    driver.close()
    final_df = filter_split_results(total_runner_count, race_url, save_file)
    return final_df

def filter_split_results(total_runner_count, race_url, save_file):
    runner_df = pd.DataFrame(columns=['Name','Gender','Age','Bib','Hometown','Time','Pace','Place'])
    final_df=pd.DataFrame()
    for i in range(math.ceil(total_runner_count/SPLIT_NUMBER)):
        driver = open_new_webpage(race_url)
        filter_runner_list(driver, place_split = SPLIT_NUMBER*i, operator='Greater than')
        load_more_data(driver, limit=SPLIT_NUMBER, filtered=True)
        runner_df = pull_runner_info(driver, runner_df, race_url, save_file, filtered=True)
        final_df = append_dataframes(final_df, runner_df)
        final_df = final_df.drop_duplicates()
        export_nyrr_data(final_df, race_url, save_file)
        driver.close()
        time.sleep(5)
    print('Pull complete')
    return final_df    

def open_new_webpage(race_url):
    driver_loc='F:\\Dropbox\Me\My Document\Gitlab\drivers\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(driver_loc)
    driver.get('https://results.nyrr.org/event/'+race_url+'/finishers')
    time.sleep(1)
    return driver
   
def load_more_data(driver, limit=None, filtered=True):
    while True:
        try:
            driver.find_element_by_xpath(BUTTON_XMLS[0]).click()
            time.sleep(.5)
            if check_for_user_count(driver, limit, filtered=filtered):
                break
        except ElementNotInteractableException:
            try:
                driver.find_element_by_xpath(BUTTON_XMLS[1]).click()
                time.sleep(.5)
                if check_for_user_count(driver, limit, filtered=filtered):
                    break
            except ElementNotInteractableException:
                break

def check_for_user_count(driver, place, filtered=True):
    if filtered:
        add_on_str = '/div'
    else:
        add_on_str = ''
    runner_profile = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/div['+str(place)+']'+add_on_str
    try:
        _ = driver.find_element_by_xpath(runner_profile)
        return True
    except NoSuchElementException:
        return False

def pull_runner_info(driver, runner_df, race_url, save_file, filtered=True, constant_export=True):
    runner_count=1
    while True:
        try:
            if filtered:
                add_on_str = '/div'
            else:
                add_on_str = ''
            runner_profile = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/div['+str(runner_count)+']'+add_on_str
            runner_info = driver.find_element_by_xpath(runner_profile).text.split('\n')
            runner_data = get_runner_info(runner_info)
            runner_df.loc[len(runner_df)] = runner_data
            runner_count+=1
            if constant_export:
                export_nyrr_data(runner_df, race_url, save_file)
        except NoSuchElementException:
            print(str(round(runner_data[7]/1000,0)), end='; ')
            break
    return runner_df
    
def get_runner_info(runner_info):
    runner_info_list=0
    if 'BIB ' in runner_info[1]:
        additional_info=runner_info[1].split('BIB')
        gend_age = additional_info[0][:additional_info[0].find(' ')]
        bib = int(additional_info[-1])
        gender=gend_age[0]
        age = int(gend_age[1:])
        hometown = additional_info[0][additional_info[0].find(' ')+1:-1]
        runner_data = [runner_info[0], gender, age, bib, hometown, runner_info[4], runner_info[6], int(runner_info[8].replace(',', ''))]
    else:
        if runner_info[1][-3:] == 'BIB':
            additional_info = runner_info[1][:-4]
        else:
            additional_info=runner_info[1]
        gend_age = additional_info[:additional_info.find(' ')]
        if gend_age=='Inf':
            age='N/A'
            gender='N/A'
            hometown='N/A'
            runner_info_list=-1
        else:
            gender=gend_age[0]
            age = int(gend_age[1:])
            hometown = additional_info[additional_info.find(' ')+1:-1]
        bib='N/A'
        runner_data = [runner_info[0], gender, age, bib, hometown,
                       runner_info[4+runner_info_list],
                       runner_info[6+runner_info_list],
                       int(runner_info[8+runner_info_list].replace(',', ''))]
    return runner_data

def filter_runner_list(driver, place_split, operator='Greater than'):
    driver.find_element_by_xpath('//*[@id="sort"]/div[1]/div[1]/div[3]/span').click()
    time.sleep(1)
    select = Select(driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[1]/select'))
    select.select_by_visible_text(operator)
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[3]/input').send_keys(str(place_split))
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[17]/div/a[2]').click()
    time.sleep(1)

def append_dataframes(big_df, small_df):
    if big_df.empty:
        big_df = small_df.copy()
    else:
        big_df = big_df.append(small_df)
    return big_df

def export_nyrr_data(df, race_url, save_file):
    if save_file=='':
        df.to_csv('nyrr_'+race_url+'_data.csv')
    else:
        df.to_csv(save_file+'.csv')