import csv
import re
import sys
import locale
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from pprint import pprint
import pandas as pd

def read_data(dates_csv, topics_csv):
    """ Reads, cleans, and joins the data from two csv tables exported from Moodle:
        1) dates of the exam 
        2) topics of the exam and the study profiles of the students """
    
    dates = pd.read_csv(dates_csv)
    topics = pd.read_csv(topics_csv)

    # Make the headers consistent:
    rename_patterns = [
        {'Datum': 'date'},
        {'Startzeit': 'begin'},
        {'Endzeit': 'end'},
        {'Vorname': 'first_name'},
        {'Nachname': 'surname'},
        {'Vollständiger Name': 'full_name'},
        {'Teilnehmer-ID': 'id_number'},
        {'Anmeldename': 'id_number'},
        {'Q00_Studienprofil angeben': 'study_profile'},
        {'Q00_Studienprofil eingeben': 'study_profile_other'},
        {'Q01_Schwerpunktthema wählen': 'focus_topic'},
        {'Q02_Schwerpunktthema wählen (G)': 'focus_topic_extra'},
        {'Q03_Weitere Epoche': 'second_topic'},
        {'Q04_Seminar angeben': 'third_topic'}    
    ]

    for pattern in rename_patterns:
        dates.rename(columns=pattern, inplace=True)
        topics.rename(columns=pattern, inplace=True)

    # Clean the data:

    # Convert the German dates into datetime objects:
    # Set the locale to German
    locale.setlocale(locale.LC_TIME, 'de_DE.utf-8')
    # Do the conversion:
    dates['date'] = pd.to_datetime(dates['date'], format='%A, %d. %B %Y', errors='coerce')
    # Reset the locale to the default
    locale.setlocale(locale.LC_TIME, '')

    # Clean the study_profile:
    pattern = r'.*\((.*)\)'
    topics['study_profile'] = topics['study_profile'].str.replace(pattern, lambda match: match.group(1), regex=True)
    topics['study_profile'] = topics['study_profile'].str.replace(r"\bG\b", "B.Ed. G", regex=True)
    topics['study_profile'] = topics['study_profile'].str.replace("GKBA", "Kombi-BA G")
    topics['study_profile'] = topics['study_profile'].str.replace("HRSGe", "Kombi-BA HRSGe")
    topics['study_profile'] = topics['study_profile'].str.replace("GymGe/BK", "Kombi-BA GymGe/BK")

    # Clean the topics
    topics['study_profile_other'] = topics['study_profile_other'].fillna("")
    topics['focus_topic'] = topics['focus_topic'].fillna("")
    topics['focus_topic_extra'] = topics['focus_topic_extra'].fillna("")
    topics['second_topic'] = topics['second_topic'].fillna("")
    topics['third_topic'] = topics['third_topic'].fillna("")

    topics['study_profile_other'] = topics['study_profile'] + topics['study_profile_other']
    topics['focus_topic'] = topics['focus_topic'] + topics['focus_topic_extra']
    topics['focus_topic'] = topics['focus_topic'].str.replace(r'\d\d? :',"")
    topics['second_topic'] = topics['second_topic'].str.replace(r'\d\d? :',"")
    topics['third_topic'] = topics['third_topic'].str.replace(r'\d\d? :',"")

    # Make sure id_number is a string
    dates['id_number'] = dates['id_number'].map(str)
    topics['id_number'] = topics['id_number'].map(str)

    # Merge the two lists
    data = pd.merge(dates, topics, on="id_number")
    
    diff = pd.merge(dates, topics, on="id_number", how="outer", indicator=True)
    
    # Write a report on the differences
    print("\nTermin gebucht ohne Thema:")
    pprint(diff[diff['_merge'] == 'left_only'].loc[:, ['date', 'begin', 'end', 'surname', 'first_name', 'id_number']])
    print("\nThema festgelegt ohne Termin:")
    pprint(diff[diff['_merge'] == 'right_only'].loc[:, ['full_name', 'id_number', 'focus_topic', 'focus_topic_extra', 'second_topic']])

    # Clean the id number
    #data['id_number'] = data['id_number'].astype(str).str.split('.', expand=True)[0]

    print("\nListe zu druckender Protokolle:")
    pprint(data.loc[:, ['date', 'begin', 'end', 'surname', 'first_name', 'id_number', 'study_profile', 'focus_topic', 'focus_topic_extra', 'second_topic']])

    return data, diff

def main():
    dates = "data/termine_2025-03-25.csv"
    topics = "data/themen_2025-03-25.csv"

    data, diff = read_data(dates, topics)
    data.to_csv("data/list.csv", index=True)
    diff[diff['_merge'] == 'left_only'].to_csv("data/list_students_without_topic.csv")


if __name__ == "__main__":
    main()
