import faker
import json
import csv
import random
import tqdm

fake = faker.Faker('zh_TW')


def generate_user(records=1000):
    users = []
    user_id_seq = 0
    for _ in range(records):
        users.append({
            'User_ID': f'{user_id_seq:20d}',  
            'User_name': fake.name(),
            'User_phone_number': fake.phone_number(),
            'User_email': fake.email(),
            'User_level': random.choice(['User']*99 + ['Admin'])
        })
        user_id_seq += 1
    print("successfully generated users")
    return users

def generate_org(records=25):
    orgs = []
    org_id_seq = 0
    with open('org_names.json', 'r', encoding='utf-8') as f:
        org_names = json.load(f)
    for i in range(records):
        orgs.append({
            'Org_ID': f'{org_id_seq:20d}',
            'Org_name': org_names[i%len(org_names)],
            'Org_address': fake.address(),
            'Org_phone_number': fake.phone_number(),
            'Org_founded_date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
        })
        org_id_seq += 1
    print("successfully generated orgs")
    return orgs

def generate_event(records=200):
    events = []
    event_id_seq = 0
    with open('event_names.json', 'r', encoding='utf-8') as f:
        event_names = json.load(f)
    for i in range(records):
        events.append({
            'Event_ID': f'{event_id_seq:20d}',
            'Event date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
            'Event_name': event_names[i%len(event_names)],
            'Event_location': fake.address(),
            'Capacity': random.randint(0, 1000),
            'Event_description': fake.text(max_nb_chars=200),
            'Event_start_time': fake.time(pattern="%H:%M:%S", end_datetime=None),
            'Event_end_time': fake.time(pattern="%H:%M:%S", end_datetime=None),
        })
        event_id_seq += 1
    print("successfully generated events")
    return events

def generate_animal(users, orgs, records=100):
    animals = []
    available_user_ids = [user['User_ID'] for user in users if user['User_level'] == 'User']
    available_org_ids = [org['Org_ID'] for org in orgs]
    with open('animal_type.json', 'r', encoding='utf-8') as f:
        animal_types = json.load(f)
    
    for i in range(records):
        animals.append({
            'Animal_ID': f'{i:20d}',
            'Animal_type': random.choice(animal_types),
            'Animal_name': fake.name(),
            'Animal_status': random.choice(['Adopted', 'Sheltered', 'Released']),
            'Reported_date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
            'Reported_reason': fake.text(max_nb_chars=200),
            'Reported_location': fake.address(),
            'Shelter_date': fake.date(pattern="%Y-%m-%d", end_datetime=None) if random.randint(0, 9) < 9 else None,
            'Adopt_user_ID': random.choice(available_user_ids) if random.randint(0, 9) < 9 else None,
            'Report_user_ID': random.choice(available_user_ids),
            'Org_ID': random.choice(available_org_ids),
        })
    print("successfully generated animals")
    return animals

def generate_hospital(records=267):
    hospitals = []
    hospital_id_seq = 0
    with open('animal_hospital.csv', 'r', encoding='utf-8') as f:
        # name,address,phone
        hospital_names = []
        hospital_address = []
        hospital_phone = []
        lines = csv.reader(f)
        for line in lines:
            if len(line) != 3:
                continue
            hospital_names.append(line[0])
            hospital_address.append(line[1])
            hospital_phone.append(line[2])

    for i in range(records):
        hospitals.append({
            'Hospital_ID': f'{hospital_id_seq:20d}',
            'Hospital_name': hospital_names[i%len(hospital_names)],
            'Hospital_adderss': hospital_address[i%len(hospital_address)],
            'Hospital_phone_number': hospital_phone[i%len(hospital_phone)],
        })
        hospital_id_seq += 1
    print("successfully generated hospitals")
    return hospitals

def generate_hold(events, orgs, records=1000):
    holds = []
    available_event_ids = [event['Event_ID'] for event in events]
    available_org_ids = [org['Org_ID'] for org in orgs]
    pbar = tqdm.tqdm(total=records)
    for event_id in available_event_ids:
        holds.append({
            'Event_ID': event_id,
            'Org_ID': random.choice(available_org_ids),
        })
        pbar.update(1)
    while len(holds) < records:
        event_id = random.choice(available_event_ids)
        org_id = random.choice(available_org_ids)
        if {'Event_ID': event_id, 'Org_ID': org_id} not in holds:
            holds.append({
                'Event_ID': event_id,
                'Org_ID': org_id,
            })
            pbar.update(1)
    pbar.close()
    print("successfully generated holds")
    return holds

def generate_attend(users, events, records=100000):
    attends = []
    available_user_ids = [user['User_ID'] for user in users]
    available_event_ids = [event['Event_ID'] for event in events]
    pbar = tqdm.tqdm(total=records)
    while len(attends) < records:
        user_id = random.choice(available_user_ids)
        event_id = random.choice(available_event_ids)
        if {'User_ID': user_id, 'Event_ID': event_id} not in attends:
            attends.append({
                'User_ID': user_id,
                'Event_ID': event_id,
            })
            pbar.update(1)
    print("successfully generated attends")
    return attends

def generate_join(users, orgs, records=2000):
    joins = []
    available_user_ids = [user['User_ID'] for user in users]
    available_org_ids = [org['Org_ID'] for org in orgs]

    while len(joins) < records:
        user_id = random.choice(available_user_ids)
        org_id = random.choice(available_org_ids)
        if {'User_ID': user_id, 'Org_ID': org_id} not in joins:
            joins.append({
                'User_ID': user_id,
                'Org_ID': org_id,
            })
    print("successfully generated joins")
    return joins

def generate_build(orgs, users, records=75):
    builds = []
    available_user_ids = [user['User_ID'] for user in users]
    available_org_ids = [org['Org_ID'] for org in orgs]
    # every org must have at least one admin
    for org_id in available_org_ids:
        builds.append({
            'User_ID': random.choice(available_user_ids),
            'Org_ID': org_id,
        })
    while len(builds) < records:
        user_id = random.choice(available_user_ids)
        org_id = random.choice(available_org_ids)
        if {'User_ID': user_id, 'Org_ID': org_id} not in builds:
            builds.append({
                'User_ID': user_id,
                'Org_ID': org_id,
            })
    print("successfully generated builds")
    return builds

def generate_donate(users, orgs, records=1000):
    donates = []
    available_user_ids = [user['User_ID'] for user in users]
    available_org_ids = [org['Org_ID'] for org in orgs]
    while len(donates) < records:
        user_id = random.choice(available_user_ids)
        org_id = random.choice(available_org_ids)
        if {'User_ID': user_id, 'Org_ID': org_id} not in donates:
            donates.append({
                'User_ID': user_id,
                'Org_ID': org_id,
            })
    print("successfully generated donates")
    return donates

# org2org
def generate_lend_supplement(orgs, records=200):
    lends = []
    available_org_ids = [org['Org_ID'] for org in orgs]
    while len(lends) < records:
        lend_orgs = random.choices(available_org_ids, k=2)
        if {'OrgID_out': lend_orgs[0], 'OrgID_in': lend_orgs[1]} not in lends:
            lends.append({
                'OrgID_out': lend_orgs[0],
                'OrgID_in': lend_orgs[1],
                'Supplement_name': random.choice(['food', 'medicine']),
                'Supplement_quantity': random.randint(0, 100000),
                'Lend_date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
                'Expected_return_date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
            })
    print("successfully generated lend_supplements")
    return lends

def generate_sent_to(animals, hospitals, records=200):
    sent_tos = []
    available_animal_ids = [animal['Animal_ID'] for animal in animals]
    available_hospital_ids = [hospital['Hospital_ID'] for hospital in hospitals]
    while len(sent_tos) < records:
        animal_id = random.choice(available_animal_ids)
        hospital_id = random.choice(available_hospital_ids)
        if {'Animal_ID': animal_id, 'Hospital_ID': hospital_id} not in sent_tos:
            sent_tos.append({
                'Animal_ID': animal_id,
                'Hospital_ID': hospital_id,
                'OrgID': random.choice([animal['Org_ID'] for animal in animals if animal['Animal_ID'] == animal_id]),
                'Sent_date': fake.date(pattern="%Y-%m-%d", end_datetime=None),
                'Return_date': fake.date(pattern="%Y-%m-%d", end_datetime=None) if random.randint(0, 9) < 9 else None,
                'Sent_reason': fake.text(max_nb_chars=200),
            })
    print("successfully generated sent_tos")
    return sent_tos




