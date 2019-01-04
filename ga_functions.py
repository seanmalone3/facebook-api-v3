import argparse
import pandas as pd
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'ga_secrets_new.json' # Path to client_secrets.json file.
VIEW_ID = '164871100'


def initialize_analyticsreporting():
  """Initializes the analyticsreporting service object.

  Returns:
    analytics an authorized analyticsreporting service object.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage('analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

def get_report(analytics):
  # Use the Analytics Service Object to query the Analytics Reporting API V4.
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions',
                        'alias': 'sessions'},
                      {'expression':'ga:bounces',
                        'alias': 'bounces'},
                      {'expression': 'ga:bounceRate',
                        'alias': 'bounce_rate'},
                      {'expression': 'ga:sessionDuration',
                        'alias': 'session_duration'},
                      {'expression': 'ga:pageviewsPerSession',
                        'alias': 'pageviews_per_session'},
                      {'expression': 'ga:transactions',
                        'alias': 'transactions'},
                     ],
          'dimensions': [{'name': 'ga:campaign'},
                         {'name': 'ga:source'},
                         {'name': 'ga:medium'},
                         {'name': 'ga:adContent'},
                         {'name': 'ga:fullReferrer'}
                        ]
        }]
      }
  ).execute()

def format_response(response):
# """Parses and prints the Analytics Reporting API V4 response"""
    df = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])
            _cmp = None
            _src = None
            _med = None
            _cnt = None
            _ref = None

            for header, dimension in zip(dimensionHeaders, dimensions):
                if header == 'ga:campaign':
                    _cmp = dimension
                if header == 'ga:source':
                    _src = dimension
                if header == 'ga:medium':
                    _med = dimension
                if header == 'ga:adContent':
                    _cnt = dimension
                if header == 'ga:fullReferrer':
                    _ref = dimension
#                 print(header + ': ' + dimension)

            #       _dtr = None
            _ses = None
            _bnc = None
            _bcr = None
            _sed = None
            _pps = None
            _trs = None
            for i, values in enumerate(dateRangeValues):
#                 print('Date range (' + str(i) + ')')
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    mh = metricHeader.get('name')
                    if mh == "sessions":
                        _ses = value
                    if mh == "bounces":
                        _bnc = value
                    if mh == "bounce_rate":
                        _bcr = value
                    if mh == "session_duration":
                        _sed = value
                    if mh == "pageviews_per_session":
                        _pps = value
                    if mh == "transactions":
                        _trs = value
#                     print(metricHeader.get('name') + ': ' + value)

            data_dict = {
                'campaign': _cmp,
                'source': _src,
                'medium': _med,
                'adcontent': _cnt,
                'ref': _ref,
                'sessions': _ses,
                'bounces': _bnc,
                'bounce_rate': _bcr,
                'session_duration': _sed,
                'pageview_per_session': _pps,
                'transaction': _trs
            }
            df.append(data_dict)
        _results = pd.DataFrame(df, columns=['campaign',
                                            'source',
                                            'medium',
                                            'adcontent',
                                            'ref',
                                            'sessions',
                                            'bounces',
                                            'bounce_rate',
                                            'session_duration',
                                            'pageview_per_session',
                                            'transaction'])
    return _results
