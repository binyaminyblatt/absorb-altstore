import json
import os
import re
import zipfile
import plistlib
from entitlements import getEntitlements
from dotenv import load_dotenv
import requests
import shutil

from repovars import source, app


load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY is required")

BASE_REPO = os.getenv("BASE_REPO").strip()

if not BASE_REPO:
    raise ValueError("BASE_REPO is required (format: owner/repo)")

BASE_URL = f'https://api.github.com/repos/{BASE_REPO}'

EXTRACT_TO = os.getenv("EXTRACT_TO", "temp")
OUTPUT_TO = os.getenv("OUTPUT_TO", "out")
CACHE_TO = os.getenv("CACHE_TO", "cache")

# Create EXTRACT_TO folder
if not os.path.exists(EXTRACT_TO):
  os.makedirs(EXTRACT_TO)

# Create OUTPUT_TO folder
if not os.path.exists(OUTPUT_TO):
  os.makedirs(OUTPUT_TO)

# Create CACHE_TO folder
if not os.path.exists(CACHE_TO):
  os.makedirs(CACHE_TO)

headers = {
    'User-Agent': 'AltStore-Repo-Generator/1.0',
    'Authorization': f'token {api_key}',  # Replace YOUR_API_KEY with your actual API key
    "Accept": "application/vnd.github+json"
}

response = requests.get(BASE_URL + '/releases', headers=headers)

# AltStore source construction


# Check if request was successful
if response.status_code == 200:
    releases = response.json()
    version_data = {}

    current_release = releases[0]['tag_name']
    # If lastGenerated.json does not exist, or if key "buildVersion" is not the same as the current release tag, then continue
    if not os.path.exists(f'{CACHE_TO}/lastGenerated.json') or json.load(open(f'{CACHE_TO}/lastGenerated.json', 'r'))['buildVersion'] != current_release:
        print(f'Starting to generate source for latest release {current_release}...')
    else:
      # If lastGenerated.json exists and key "buildVersion" is the same as latestPath[:-1], then exit
      print('No new releases found. Exiting.')
      exit()
    
    all_tags = requests.get(BASE_URL + '/tags', headers=headers).json()
    # Iterate over releases
    for release in releases:
        tag_name = release['tag_name']
        assets = release['assets']
        
        # Iterate over assets
        for asset in assets:
            asset_name = asset['name']
            if asset_name.lower().endswith('.ipa'):

              # Download the file at BASE_URL/tdAPP_KEY, then extract the Info.plist and binary from the zip in the Payload folder
              downloadURL = asset['browser_download_url']
              response = requests.get(downloadURL)
              
              with open(f'{EXTRACT_TO}/{asset_name}', 'wb') as f:
                f.write(response.content)
              app_folder = None
              with zipfile.ZipFile(f'{EXTRACT_TO}/{asset_name}', 'r') as zip_ref:
                for name in zip_ref.namelist():
                  if name.startswith("Payload/") and name.endswith(".app/"):
                      app_folder = name.split('/')[1].split('.app')[0]
                      print(f'Found app folder: {app_folder}')
                      break
                zip_ref.extract(f'Payload/{app_folder}.app/Info.plist', path=EXTRACT_TO)
                zip_ref.extract(f'Payload/{app_folder}.app/{app_folder}', path=EXTRACT_TO)

              # Declare the plist to get useful info like CFBundleShortVersionString and CFBundleVersion
              plist = plistlib.load(open(f'{EXTRACT_TO}/Payload/{app_folder}.app/Info.plist', 'rb'))

              doesNotExist = True
              # Check if a version with the same version and buildVersion already exists, if so, break the release loop
              for version in app['versions']:
                if version['version'] == plist['CFBundleShortVersionString'] and version['buildVersion'] == plist['CFBundleVersion']:
                  doesNotExist = False
                  break
              
              if doesNotExist:
                # If this is the first asset, we will add the entitlements and privacy to the app object
                if len(app['versions']) == 0:
                  ##
                  # Adding appPermissions including entitlements and privacy
                  ##
                  if app["bundleIdentifier"] is None:
                    app["bundleIdentifier"] = plist['CFBundleIdentifier']
                    source['featuredApps'].append(plist['CFBundleIdentifier'])
                  min_ios = plist.get('MinimumOSVersion')

                  if app["minimumOSVersion"] is None and min_ios:
                      app["minimumOSVersion"] = min_ios

                  app['appPermissions'] = {}
                  app['appPermissions']['entitlements'] = []

                  for entitlement in getEntitlements(f'{EXTRACT_TO}/Payload/{app_folder}.app/{app_folder}'):
                    # Add entitlement to the entitlements array
                    app['appPermissions']['entitlements'].append(entitlement)

                  app['appPermissions']['privacy'] = {}

                  for key, value in plist.items():
                      # Check if the key starts with "NS" and ends with "UsageDescription"
                      if key.startswith("NS") and key.endswith("UsageDescription"):
                        # Add key-value pairs to the privacy object with the permission name being the key and the value being the value
                        app['appPermissions']['privacy'][key] = value

                # Get the number of bytes of the downloaded file at f'{EXTRACT_TO}/{APP_KEY}'
                appSize = os.path.getsize(f'{EXTRACT_TO}/{asset_name}')

                ##
                # Creating and adding the version
                ##

                # Get the last modified date of the latest build
                lastModified = asset['updated_at']

                # Get the version's commit message
                commit_msg = ''
                for tag in all_tags:
                  if tag['name'] == tag_name:
                    commit_msg = requests.get(tag['commit']['url'], headers=headers).json()['commit']['message']
                    break
                localizedDescription = release["body"]
                localizedDescription = re.sub('<[^<]+?>', '', localizedDescription)  # Remove HTML tags
                localizedDescription = re.sub(r'#{1,6}\s?', '', localizedDescription)  # Remove markdown header tags
                localizedDescription = re.sub(r'\*{2}', '', localizedDescription)
                localizedDescription = re.sub(r'-', '•', localizedDescription)
                localizedDescription = re.sub(r'`', '"', localizedDescription)
                version = {
                  "version": plist['CFBundleShortVersionString'],
                  "buildVersion": plist['CFBundleVersion'],
                  "date": lastModified,
                  "localizedDescription": localizedDescription,
                  "downloadURL": downloadURL,
                  "size": appSize,
                  "minOSVersion": plist['MinimumOSVersion']
                }
                app['versions'].append(version)
                news_identifier = f"release-{plist['CFBundleShortVersionString']}"
                news_entry = {
                    "title": f"{plist['CFBundleShortVersionString']} - {source['name']}",
                    "identifier": news_identifier,
                    "caption": f"Update of {source['name']} just got released!",
                    "date": lastModified,
                    "tintColor": "#000000",
                    "imageURL": source['iconURL'],
                    "notify": True,
                    "url": f"https://github.com/{BASE_REPO}/releases/tag/{tag_name}"
                }
                source['news'].append(news_entry)
                # Add the app to the source
                break
else:
    print('Failed to fetch releases from GitHub API. Status code:', response.status_code)
    exit()
# Add app to the source
source['apps'].append(app)

# Output source variable as json to a file named apps.json
with open(f'{OUTPUT_TO}/apps.json', 'w') as f:
  f.write(json.dumps(source, indent=2))
  print('Source generated.')

# Generate lastGenerated.json and save it to CACHE_TO/lastGenerated.json
lastGenerated = {
  "buildVersion": current_release
}

with open(f'{CACHE_TO}/lastGenerated.json', 'w') as f:
  f.write(json.dumps(lastGenerated, indent=2))

# Delete the EXTRACT_TO folder and its contents
shutil.rmtree(EXTRACT_TO)
