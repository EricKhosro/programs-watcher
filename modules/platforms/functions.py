import requests
from hashlib import md5


def get_resource(tmp_dir, url, platformName):
    domainList = requests.get(url, allow_redirects=True)
    open(F"{tmp_dir}{platformName}.json", 'wb').write(domainList.content)


def generate_program_key(programName, programURL):
    program_key = md5(
        f"{programName}|{programURL}".encode('utf-8')).hexdigest()
    return program_key


def find_program(db, platformName, programKey):
    data = db[platformName].find_one({'programKey': programKey})
    return data


def remove_elements(array1, array2):
    for element in array2:
        array1.remove(element)


def save_data(db, platformName, programKey, dataJson):
    db[platformName].update_one({'programKey': programKey}, {
        '$set': dataJson}, upsert=True)

def check_send_notification(first_time, is_update, data, watcherData, monitor, notifications):
    pt_notify_status = False
    notify_status = False

    # Check if the program is in the specific programs list
    # if watcherData['programURL'] in monitor['specific_programs']:
    #     pt_notify_status = True  # Allow notification if it's a specific program

    # Monitor program types (RDP and VDP)
    if data['isNewProgram']:
        if data['programType'] == "rdp" and monitor['rdp']:
            pt_notify_status = True
        elif data['programType'] == "vdp" and monitor["vdp"]:
            pt_notify_status = True
    else:
        if watcherData['programType'] == "rdp" and monitor['rdp']:
            pt_notify_status = True
        elif watcherData['programType'] == "vdp" and monitor["vdp"]:
            pt_notify_status = True   

    # Exclude program URLs
    if watcherData['programURL'] in monitor['excluded_programs']:
        print(f"Program {watcherData['programURL']} is excluded from notifications")
        return False  # Block notifications early

    # Check the notification conditions
    if pt_notify_status:
        # First-time setup should not trigger notifications unless updates exist
        if not first_time:
            if data['isNewProgram'] and notifications['new_program']:
                notify_status = True
            elif is_update and not data['isNewProgram']:
                notify_status = True

    return notify_status
