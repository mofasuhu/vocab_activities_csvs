# Automated Session Data Processor
This repository contains a Python script, `vocab_act_csvs.py`, designed to automate the processing of educational session data, including handling zip files, extracting and parsing CSV and XML files, and performing data cleanup and transformation tasks. It also demonstrates the use of web automation to download necessary files using Selenium.

## Features
- **Zip File Handling**: Automatically unpacks session-related zip files.
- **Data Extraction and Parsing**: Parses various file types to extract and process data.
- **Web Automation**: Utilizes Selenium to automate web interactions for file downloads.
- **Data Cleanup**: Implements data transformations and normalization using Pandas and BeautifulSoup.

## Prerequisites
Before you run this script, ensure you have the following installed:
- Python 3.7 or higher
- Pip (Python package installer)

## Dependencies
This script uses several Python libraries. Install them using pip:
```
pip install pandas numpy beautifulsoup4 selenium requests
```
Ensure you have the appropriate WebDriver installed for Selenium to interact with your browser (e.g., geckodriver for Firefox).

## Configuring Browser Profiles for Selenium
This script uses Selenium WebDriver to interact with web pages using specific browser profiles that are configured for automatic login through saved sessions. To use this script, you need to set up your browser with access to the necessary web pages and then point the script to use this profile.

### Chrome Configuration
1. **Modify the script**: Replace the path in the `chrome` variable with the path to your Chrome profile.
```
chrome = r'"path_to_your_chrome.exe" --profile-directory="YourProfileDirectory"'
```

### Firefox Configuration
1. **Locate your Firefox profile**: This is usually found in 
```
C:\Users\[YourUsername\]\AppData\Roaming\Mozilla\Firefox\Profiles\
```
2. **Update the script**: Use the correct path to point to your Firefox profile using the glob module.
```
firefox_profile_path = glob.glob(r"path_to_your_firefox_profiles\*.default*")[0]
```

### Important Note
Ensure that the browser profiles used have the necessary permissions and are logged in to the required accounts to ensure seamless script operation. These profiles should be configured only on secure machines to prevent unauthorized access.

## Configuring API Access and OAuth
This script interacts with web APIs that require OAuth2.0 authentication. To run the script successfully, you'll need to configure the OAuth details and endpoint URLs:

### Configuring OAuth for Google Accounts
1. **Create OAuth 2.0 credentials** in the Google Developer Console.
2. **Configure the consent screen** with the necessary scopes.
3. **Set the correct redirect URIs** pointing to your server or local environment.
4. **Replace the client_id** in the script with your own client_id from the Google Developer Console.

### Setting Up URLs
- Replace all instance-specific URLs in the script with the URLs pertinent to your APIs or web services. This includes login URLs, API endpoints, and any redirect URIs used in the script.

### Important Security Note
Avoid exposing sensitive details like client secrets or personal access tokens in your scripts. Always use environment variables or configuration files that are not tracked in your version control system to handle sensitive information.

## Setup

### Clone the Repository:
```
git clone https://github.com/mofasuhu/vocab_activities_csvs.git
cd vocab_activities_csvs
```
### Environment Setup:
Optionally, set up a virtual environment:
On Windows use:
```
python -m venv venv
venv\Scripts\activate
```
### Install Dependencies:
```
pip install -r requirements.txt
```

## Configuration
Before running the script, configure the paths and user credentials in the script. Update the following placeholders in the script:
- **user_input1**: Path to your Chrome default downloads folder.
- **user_input2**: Your Nagwa email.

## Usage
To run the script, use the following command from the terminal:
```
python sentence_act_csvs.py
```
Follow the on-screen prompts to enter required paths and credentials.

## Output
The script will process the data and output:
- Processed CSV files in the specified output directory.
- Logs and status updates in the terminal.

## Example Data
This repository includes an example input and output folders in the `examples` directory:
- `EG ES G11 T2_example_input`: and the script can iteratively work on a lot of folders like this example.
- `sessions_educational_resources_report_example_input.csv`
- `EG ES G11 T2_example_output`: and the script can iteratively give multiple outputs like this example for a lot of input folders too.

### How to Run the Script with Example Data
To run the script using the example input data, follow these steps:
1. Navigate to the script's directory:
```
cd path_to_script
```
and add the example input data in same directory.

## Contributing
Contributions to enhance the functionality or efficiency of this script are welcome. Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
