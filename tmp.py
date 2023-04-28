from typing import Iterator
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from googleapiclient.discovery import Resource, build
from pathlib import Path
ROOT_DIR =  Path(os.path.dirname(os.path.abspath(__file__)))

def credentials():
    token_dir_path = ROOT_DIR.joinpath("token.json")
    if token_dir_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_dir_path), SCOPES)
        except ValueError:
            creds = None
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                str(ROOT_DIR.joinpath('client_secret.json')), SCOPES, )
            creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open(token_dir_path, 'w') as token:

                token.write(creds.to_json())
    return creds
# TODO: del in prod
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
MAX_RESULTS = 50
SCOPES = ['https://www.googleapis.com/auth/fitness.body.write']
service: Resource = build("fitness", "v1",credentials=credentials())


fitusr = service.users()
fitdatasrc = fitusr.dataSources()
PROJECT_ID = "955637978660"
data_source = dict(
    type='raw',
    application=dict(name='weight_import'),
    dataType=dict(
      name='com.google.weight',
      field=[dict(format='floatPoint', name='weight')]
    ),
    device=dict(
      type='scale',
      manufacturer='klammert',
      model='klammert-manual',
      uid='ws-50',
      version='1.0',
    )
  )


def get_data_source_id(dataSource):
    return ':'.join((
        dataSource['type'],
        dataSource['dataType']['name'],
        PROJECT_ID,
        dataSource['device']['manufacturer'],
        dataSource['device']['model'],
        dataSource['device']['uid']
    ))
data_source_id = get_data_source_id(data_source)


try:
    service.users().dataSources().get(
        userId='me',
        dataSourceId=data_source_id).execute()
except HttpError as e:
    if not 'DataSourceId not found' in str(e):
        raise e
    # Doesn't exist, so create it.
    x = service.users().dataSources().create(
        userId='me',
        body=data_source).execute()
print()
def nano(val):
  """Converts a number to nano (str)."""
  #return (int(val) * 1e9)
  return '%d' % (int(val) * 1e9)

from weight.read_weight_csv import read_weights_csv
def read_weights_csv_with_gfit_format():
    weights = read_weights_csv()
    gfit_weights = []
    for weight in weights:
        gfit_weights.append(dict(
            dataTypeName='com.google.weight',
            endTimeNanos=nano(weight["seconds_from_dawn"]),
            startTimeNanos=nano(weight["seconds_from_dawn"]),
            value=[dict(fpVal=weight["weight"])],
        ))
    return gfit_weights
weights = read_weights_csv_with_gfit_format()

min_log_ns = min([w["startTimeNanos"] for w in weights])#weights[0]["startTimeNanos"]
max_log_ns = max([w["endTimeNanos"] for w in weights])#weights[-1]["startTimeNanos"]
dataset_id = '%s-%s' % (min_log_ns, max_log_ns)



# service.users().dataSources().datasets().delete(
#         userId='me',
#         dataSourceId=data_source_id,datasetId=dataset_id,).execute(),
#
# exit()

# patch data to google fit
service.users().dataSources().datasets().patch(
  userId='me',
  dataSourceId=data_source_id,
  datasetId=dataset_id,
  body=dict(
    dataSourceId=data_source_id,
    maxEndTimeNs=max_log_ns,
    minStartTimeNs=min_log_ns,
    point=weights,
  )).execute()

print(
# read data to verify
service.users().dataSources().datasets().get(
    userId='me',
    dataSourceId=data_source_id,
    datasetId=dataset_id).execute()
)
