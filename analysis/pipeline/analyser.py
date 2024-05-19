import json

from proj.tasks import analyze_apk
from celery import group
from celery import chain
from proj import APK_JSON_PATH

"""
    Starts the analysis process.
    Expects the input JSON to be in the following format:

    {
        <package_name>: {
            'mode': 'SINGLE_APK' | 'MULTIPLE_APKS',
            'split_apks': [                             # only necessary if mode=MULTIPLE_APKS
                <split_apk1>,
                <split_apk2>
            ]
        },
        <package_name2>: ...
    }
"""
def main():
    with open(APK_JSON_PATH, 'r') as f:
        data = json.load(f)
    
    packages = []
    for attr, val in data.items():
        if (val['mode'] == 'SINGLE_APK'):
            packages.append({'id': attr, 'split_apks': []})
        else:
            packages.append({'id': attr, 'split_apks': val["split_apks"]})

    tasks = [ analyze_apk.s(packet['id'], packet['split_apks']) for packet in packages ]
    results = group(tasks)().get()

if __name__ == '__main__':
    main()