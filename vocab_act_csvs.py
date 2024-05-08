import os
import glob
import zipfile
import re
from session_number import session_number_dict # Custom module for session number mapping
import pandas as pd
from bs4 import BeautifulSoup
import shutil
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess

# Setup requests session with retries
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

# Configure Selenium WebDriver options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Get the current working directory
current_folder = os.getcwd()

def normalize_space(string):
    """Normalize whitespace in a string by replacing multiple spaces with a single space."""    
    return str(re.sub(r'\s+', ' ', string)).strip()
    
def extract_class(value):
    """Extract numeric class information from a string, or return the modified string."""
    if not value[-1].isdigit():
        return value[2:]
    else:
        return str(int(''.join(filter(str.isdigit, value)))) 
        
def unzip_session_activities(path):
    """Unzip session files from specified path."""
    zip_files = glob.glob(path)
    for zip_file in zip_files:
        dir_name = zip_file[:-4]
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(dir_name)
            
def session_number_mapping(session_number):
    """Map session number to a predefined session number or return a default value."""
    if not session_number:
        return 100000000000
    return session_number_dict.get(session_number, 100000000000)   
    
# Define a dictionary for mapping activity types to a display order  
homework_display_order_dict = {
	"matching": 1,
	"pronunciation": 2,
	"missing_letters": 3,
	"spelling": 4,
	"classification": 5,
	"missing_words": 6,
	"dictation": 7,
	"sentence_building": 8,
	"translation": 9,
	"conjugation": 10
}

# Language replacements for localization
replacements = {
    'EN': 'English',
    'FR': 'Français',
    'DE': 'Deutsch',
    'IT': 'Italiano',
    'ES': 'Español',
    'AR': 'اللغة العربية'
}

# Translation dictionary for activity types
vocabulary_activities_dict = {
    "matching": {"en": "Matching", "es": "Palabra correspondiente", "de": "Zuordnung", "it": "Parola corrispondente", "fr": "Mot correspondant"},
    "pronunciation": {"en": "Pronunciation", "es": "Pronunciación", "de": "Aussprache", "it": "Pronuncia", "fr": "Prononciation"},
    "missing_letters": {"en": "Missing letters", "es": "Palabra incompleta", "de": "Fehlende Buchstaben", "it": "Parola incompleta", "fr": "Mot incomplet"},
    "spelling": {"en": "Spelling", "es": "Deletreo", "de": "Rechtschreibung", "it": "Ortografia", "fr": "Orthographe"},
    "classification": {"en": "Classification", "es": "Clasificación", "de": "Klassifizierung", "it": "Classificazione", "fr": "Classification"},
}

def vocabulary_activity_translated(activity_name, lang_abbr):
    """Translate activity names based on the given language abbreviation."""
    lang_code = {"en": "en","es": "es","de": "de","it": "it","fr": "fr"}.get(lang_abbr.lower(), "en")
    translation = vocabulary_activities_dict.get(activity_name.lower(), {}).get(lang_code, "Activity Not Found")
    return translation
    
# Main execution starts here
print("\nProcessing sessions_educational_resources_report.csv ... \n")
 
# Load and process session details from CSV        
sessions_details_df=pd.read_csv(glob.glob(f'sessions_educational_resources_report_*.csv')[0], encoding="utf-8").fillna("")
sessions_details_df=sessions_details_df[sessions_details_df["Meta Session Id"]!=""]
sessions_details_df[["Session Number", "Session Title"]]=sessions_details_df['Session Title'].str.split(':', n=1, expand=True)
sessions_details_df["Session Number"]=sessions_details_df["Session Number"].apply(normalize_space)
sessions_details_df["Session Title"]=sessions_details_df["Session Title"].fillna(sessions_details_df["Session Number"]).apply(normalize_space)
sessions_details_df["Session Number"]=sessions_details_df["Session Number"].apply(session_number_mapping)
sessions_details_df["Grade ID"]=sessions_details_df["Class Grade"].apply(extract_class)
sessions_details_df["Meta Class Id"]=sessions_details_df["Meta Class Id"].replace("", "0")
sessions_details_df[["Meta Session Id","Meta Class Id"]]=sessions_details_df[["Meta Session Id","Meta Class Id"]].astype("int64").astype(str)
sessions_details_df["Class Subject"]=sessions_details_df["Class Subject"].apply(normalize_space)
sessions_details_df["Class Title"]=sessions_details_df["Class Title"].apply(normalize_space)
sessions_details_df["Start Date"] = pd.to_datetime(sessions_details_df["Start Date"])
sessions_details_df["Class Subject"] = sessions_details_df["Class Subject"].replace("الفلسفة والمنطق", "الفلسفة").replace("علم النفس", "علم النفس والاجتماع").replace("الجيولوجيا وعلوم البيئة","الجيولوجيا")
sessions_details_df["Class Title"] = sessions_details_df["Class Title"].replace("الفلسفة والمنطق", "الفلسفة").replace("علم النفس", "علم النفس والاجتماع").replace("الجيولوجيا وعلوم البيئة","الجيولوجيا")
sessions_details_df=sessions_details_df[["Meta Session Id","Session Title","Session Number", "Meta Class Id","Grade ID",
"Class Subject","Class Title","Status", "Start Date", "Country","Class Grade"]]

# User input for paths and credentials
user_input1 = input("Please Type Your Chrome Default Downloads Path: ")                
user_input2 = input("Please Type Your Nagwa Email: ")

# Selenium WebDriver setup and navigation
# Personal browser profile for Chrome, configured for auto-login with company credentials.
# Users must replace the path with the path to their own Chrome profile that has the required access.
chrome = r'"C:\Users\staff\AppData\Local\Google\Chrome\Application\chrome.exe" --profile-directory="Default"'
# Automatically find the default Firefox profile. This example assumes Firefox is installed in the default location.
# Users should ensure the glob pattern correctly points to their Firefox profile directory that is configured for auto-login with company credentials too.
firefox_profile_path = r"C:\Users\staff\AppData\Roaming\Mozilla\Firefox\Profiles\jaqvi6t5.default-release-1680435761577"
firefox_options = FirefoxOptions()
firefox_options.add_argument(f"-profile {firefox_profile_path}")
firefox_options.add_argument("--headless")
firefox_options.log.level = "trace"
service = Service(executable_path=r"[path to geckodriver.exe]")
driver = webdriver.Firefox(service=service, options=firefox_options)

# This URL is used for OAuth2.0 authentication to access specific company resources.
# Replace the URL and client_id with your own authentication details.
driver.get(f"https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?prompt=&.................&login_hint={user_input2}")

# Access to a specific company tool for building sentence activities. Replace with the appropriate URL for your tools.
url='https://.............................'
driver.get(url)

# More WebDriver and chrome browser interactions...
excepted_folders = ['Done', 'output', 'venv', '__pycache__', '.ipynb_checkpoints', 'Sentences_version']
for item in glob.glob(os.path.join(current_folder, "*")):
    if os.path.isdir(item) and all(excepted_name not in item for excepted_name in excepted_folders):
        with ZipFile(glob.glob(os.path.join(item, '*.vocabulary.zip'))[0], 'r') as course_zip:
            course_zip.extractall(os.path.basename(item))
        print(os.path.basename(item))
        for xml in glob.glob(os.path.join(item, '*.vocabulary.xml')):
            session_zip=os.path.basename(xml).replace('.xml', '.session_activities.zip')

            default_download = os.path.join(user_input1, session_zip)
            target_download = os.path.join(item, session_zip)    
            if not os.path.exists(target_download):
                try:
                    session_zip_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{session_zip}')]")))
                    download_url = session_zip_element.get_attribute('href')
                    if os.path.exists(default_download):
                        os.remove(default_download)
                    print(download_url)
                    cmd = f'cmd /c "{chrome} {download_url}"'
                    subprocess.Popen(cmd, shell=True)
                    while not os.path.exists(default_download):
                        time.sleep(1)
                    if os.path.exists(default_download):
                        shutil.move(default_download, target_download)
                        print(f"File moved to {target_download}")
                    else:
                        print(f"File not found: {default_download}") 
                except Exception as e:
                    print(f"{session_zip} not found.{e}") 

        print(f"{os.path.basename(item)} downloads done!")  
        unzip_session_activities(f'{item}/*.session_activities.zip')
        course_vocab = glob.glob(f'{item}/*.vocabulary.xlsx')[0]
        course_vocab_df = pd.read_excel(course_vocab, sheet_name='vocabulary', engine="openpyxl").fillna("")
        
        course_vocab_df["l2"]=course_vocab_df["l2"].map(replacements)
        
        course_vocab_df["metasession_id"]="100000000000"

        for index, row in course_vocab_df.iterrows():
            meta_session_ids = []
            cond1 = (sessions_details_df["Country"]==row["country"])
            cond2 = (sessions_details_df["Class Subject"]==row["l2"])
            cond3 = (sessions_details_df["Grade ID"]==str(row["grade"]))
            if "Live_HR" in course_vocab_df.columns:
                cond4 = (sessions_details_df["Session Number"]==row["Live_HR"])
            else:
                cond4 = (sessions_details_df["Session Number"]==row["Live Session"])
            
            cond5 = ((sessions_details_df['Class Title'].str.contains('Intensive Class'))|(sessions_details_df['Class Title'].str.contains('شرح مكثف')))
            cond6 = ((~sessions_details_df['Class Title'].str.contains('Intensive Class'))&(~sessions_details_df['Class Title'].str.contains('شرح مكثف')))
            cond7 = (sessions_details_df["Class Subject"]==sessions_details_df["Class Title"])

            if 'intensive' in os.path.basename(item).lower():
                matching_rows = sessions_details_df[cond1 & cond2 & cond3 & cond4 & cond5]
            else:
                matching_rows = sessions_details_df[cond1 & cond2 & cond3 & cond4 & cond6 & cond7]

            if len(matching_rows) > 0:
                meta_session_ids = matching_rows["Meta Session Id"].unique()
            if len(meta_session_ids) == 1:
                metasession_id_col = meta_session_ids[0]
                course_vocab_df.loc[index, "metasession_id"] = metasession_id_col  
        
        for xml in glob.glob(f'{item}/*.vocabulary.xml'):
            print(os.path.basename(xml))
            homework_data=[]
            entry_dict={}
            with open(xml, "r", encoding="utf-8") as session_xml_file:
                session_soup = BeautifulSoup(session_xml_file, "lxml-xml")                
                vocabulary_element = session_soup.find("vocabulary")
                section_id_attr = session_soup.find_all("entry")[0].get('section_id', '')
                entry_list = set([(x.get('section_id', ''), x.get('section_title', ''), x.get('section_index', '')) for x in session_soup.find_all("entry")])
                for i in entry_list:
                    entry_dict[i[1]]=[i[0],i[2]]
                country_attr = vocabulary_element.get('country', '')
                section_index_attr = session_soup.find_all("entry")[0].get('section_index', '')

            session_folder_name = os.path.basename(xml).replace('.xml', '.session_activities')
            
            if "Live_HR" in course_vocab_df.columns:
                newFolderNameid=course_vocab_df["Live_HR"][(course_vocab_df["unit_id"]==int(os.path.basename(xml).split(".")[0]))].unique()[0]
            else:
                newFolderNameid=course_vocab_df["Live Session"][(course_vocab_df["unit_id"]==int(os.path.basename(xml).split(".")[0]))].unique()[0]
            new_session_folder_name=f"{item}/({newFolderNameid}) {session_folder_name}"
            for fol in glob.glob(f"{item}/{session_folder_name}"):
                if os.path.isdir(fol) and not os.path.exists(new_session_folder_name):
                    os.rename(fol, new_session_folder_name)
                else:
                    shutil.rmtree(fol)
                    
            for act_xml in glob.glob(f"{new_session_folder_name}/**/*.activity.xml"):
                act_dict={}
                metasession_id=course_vocab_df["metasession_id"][(course_vocab_df["section_id"].astype(str)==section_id_attr)].unique()[0]
                with open(act_xml, "r", encoding="utf-8") as xml_file:
                    act_soup = BeautifulSoup(xml_file, "lxml-xml")
                    activity_element = act_soup.find("activity")
                    item_type_attr = activity_element.get('type', '')
                    item_id_attr = activity_element.get('id', '')
                    item_l2_attr = activity_element.get('l2', '')
                    title_element = act_soup.find('title')
                    type_title = f"{vocabulary_activity_translated(item_type_attr, item_l2_attr)}: {normalize_space(title_element.contents[0])}"
                    
                    title_index = int(entry_dict[normalize_space(title_element.contents[0])][1])
                
                homework_type = item_type_attr
                homework_display_order = homework_display_order_dict[item_type_attr]
                item_id = item_id_attr
                language = item_l2_attr
                locale = country_attr
                title = type_title

                act_dict["metasession_id"]=metasession_id
                act_dict["homework_type"]=homework_type
                act_dict["homework_display_order"]=homework_display_order
                act_dict["duration"]=""
                act_dict["item_id"]=item_id
                act_dict["language"]=language
                act_dict["locale"]=locale
                act_dict["instance_no"]=""
                act_dict["title"]=title
                act_dict["title_index"]=title_index
                homework_data.append(act_dict)
            homework_data_sorted_correctly = sorted(homework_data, key=lambda x: (x['title_index'], homework_display_order_dict[x['homework_type']]))
            new_order_correct = 1  # Starting with 1 and will continue incrementing across different title_index
            for oitem in homework_data_sorted_correctly:
                oitem['homework_display_order'] = new_order_correct
                new_order_correct += 1  # Increment for the next oitem regardless of title_index
            for old_csv in glob.glob(f"{new_session_folder_name}/*.csv"):
                os.remove(old_csv)
            
            
            for i, d in enumerate(homework_data_sorted_correctly, start=1):
                url = "http://12digit.............."      
                response = session.get(url)
                if response.status_code == 200:
                    id_list = response.json()
                    csv_name = id_list[0]
                else:
                    csv_name = '100000000000'
                csv_file_path = f"{new_session_folder_name}/{csv_name}.csv"
                act_df = pd.DataFrame([d])
                act_df=act_df[["metasession_id", "homework_type", "homework_display_order", "duration", "item_id", "language", "locale", "instance_no", "title"]]
                act_df.to_csv(csv_file_path, encoding='utf-8', index=False)

driver.quit() # Ensure to cleanly close the driver after execution is complete
