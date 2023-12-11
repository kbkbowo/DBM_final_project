import pandas as pd

file = 'data.xlsx'
xl = pd.read_excel(file, sheet_name=None)

users = xl['users']
events = xl['events']
orgs = xl['orgs']
hospitals = xl['hospitals']
animals = xl['animals']
attends = xl['attends']
holds = xl['holds']
joins = xl['joins']
builds = xl['builds']
donates = xl['donates']
lend_supplements = xl['lend_supplements']
sent_tos = xl['sent_tos']

# save to ./csvs/

users.to_csv('./csvs/users.csv', index=False)
events.to_csv('./csvs/events.csv', index=False)
orgs.to_csv('./csvs/orgs.csv', index=False)
hospitals.to_csv('./csvs/hospitals.csv', index=False)
animals.to_csv('./csvs/animals.csv', index=False)
attends.to_csv('./csvs/attends.csv', index=False)
holds.to_csv('./csvs/holds.csv', index=False)
joins.to_csv('./csvs/joins.csv', index=False)
builds.to_csv('./csvs/builds.csv', index=False)
donates.to_csv('./csvs/donates.csv', index=False)
lend_supplements.to_csv('./csvs/lend_supplements.csv', index=False)
sent_tos.to_csv('./csvs/sent_tos.csv', index=False)
