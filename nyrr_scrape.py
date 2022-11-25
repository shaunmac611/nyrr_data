# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 15:21:26 2022

@author: Shaun
"""
from selenium import webdriver
import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC

SPLIT_NUMBER=16000

def get_marathon_data(year):
    get_nyrr_race_data('M'+year, 'nyc_marathon_'+year+'_data')
    
def get_nyrr_race_data(race_url, save_file=''):
    driver_loc='F:\\Dropbox\Me\My Document\Gitlab\drivers\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(driver_loc)
    #driver.minimize_window()
    driver.get('https://results.nyrr.org/event/'+race_url+'/finishers')
    time.sleep(1)
    
    total_runner_count = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/ul/li[1]/a/span[2]')
    print(total_runner_count.text)
    if int(total_runner_count.text)>SPLIT_NUMBER:
        print('Splitting Racers')
        split_large_race(race_url, save_file)
    else:
        button= '/html/body/div/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/a'
        while True:
            try:
                driver.find_element_by_xpath(button).click()
                time.sleep(.2)
            except ElementNotInteractableException:
                break
        
        runner_count=1
        runner_df = pd.DataFrame(columns=['Name','Gender','Age','Bib','Hometown','Time','Pace','Place'])
        while True:
            try:
                runner_profile = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/div['+str(runner_count)+']'
                runner_info = driver.find_element_by_xpath(runner_profile).text.split('\n')
                runner_data = get_runner_info(runner_info)
                runner_df.loc[len(runner_df)] = runner_data
                runner_count+=1
                if save_file=='':
                    runner_df.to_csv('nyrr_'+race_url+'_data.csv')
                else:
                    runner_df.to_csv(save_file+'.csv')
            except NoSuchElementException:
                print("Pull complete")
                break

def get_runner_info(runner_info):
    runner_info_list=0
    if 'BIB ' in runner_info[1]:
        additional_info=runner_info[1].split('BIB')
        gend_age = additional_info[0][:additional_info[0].find(' ')]
        bib = int(additional_info[-1])
        gender=gend_age[0]
        age = int(gend_age[1:])
        hometown = additional_info[0][additional_info[0].find(' ')+1:-1]
        runner_data = [runner_info[0], gender, age, bib, hometown, runner_info[4], runner_info[6], runner_info[8]]
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
                       runner_info[8+runner_info_list]]
    return runner_data

def split_large_race(race_url, save_file):
    driver_loc='F:\\Dropbox\Me\My Document\Gitlab\drivers\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(driver_loc)
    #driver.minimize_window()
    driver.get('https://results.nyrr.org/event/'+race_url+'/finishers')
    time.sleep(1)
    
    driver.find_element_by_xpath('//*[@id="sort"]/div[1]/div[1]/div[3]/span').click()
    time.sleep(1)
    select = Select(driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[1]/select'))
    select.select_by_visible_text('Less than')
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[3]/input').send_keys(str(SPLIT_NUMBER))
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[17]/div/a[2]').click()
    time.sleep(1)
    
    button= '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/a'

    while True:
        try:
            driver.find_element_by_xpath(button).click()
            time.sleep(.2)
        except ElementNotInteractableException:
            break
    
    runner_count=1
    runner_df = pd.DataFrame(columns=['Name','Gender','Age','Bib','Hometown','Time','Pace','Place'])
    while True:
        try:
            runner_profile = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/div['+str(runner_count)+']/div'
            runner_info = driver.find_element_by_xpath(runner_profile).text.split('\n')
            runner_data = get_runner_info(runner_info)
            runner_df.loc[len(runner_df)] = runner_data
            runner_count+=1
            if save_file=='':
                runner_df.to_csv('nyrr_'+race_url+'_data.csv')
            else:
                runner_df.to_csv(save_file+'.csv')
        except NoSuchElementException:
            print("Pull complete")
            break
    
    driver_loc='F:\\Dropbox\Me\My Document\Gitlab\drivers\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(driver_loc)
    #driver.minimize_window()
    driver.get('https://results.nyrr.org/event/'+race_url+'/finishers')
    time.sleep(1)
    
    driver.find_element_by_xpath('//*[@id="sort"]/div[1]/div[1]/div[3]/span').click()
    time.sleep(1)
    select = Select(driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[1]/select'))
    select.select_by_visible_text('Greater than')
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[4]/div[3]/input').send_keys(str(SPLIT_NUMBER))
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[3]/div[17]/div/a[2]').click()
    time.sleep(1)
    
    button= '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/a'

    while True:
        try:
            driver.find_element_by_xpath(button).click()
            time.sleep(.2)
        except ElementNotInteractableException:
            break
    
    runner_count=1
    while True:
        try:
            runner_profile = '/html/body/div[1]/div[2]/div/main/div/div[2]/div[2]/div/div/div[4]/div['+str(runner_count)+']/div[1]/div/div[1]'
            runner_info = driver.find_element_by_xpath(runner_profile).text.split('\n')
            runner_data = get_runner_info(runner_info)
            runner_df.loc[len(runner_df)] = runner_data
            runner_count+=1
            if save_file=='':
                runner_df.to_csv('nyrr_'+race_url+'_data.csv')
            else:
                runner_df.to_csv(save_file+'.csv')
        except NoSuchElementException:
            print("Pull complete")
            break
