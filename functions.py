import csv
def reportQuery(client, query, path):
  # Specify where to download the file here.
  file = open(path, mode='w', encoding='utf8')
  file.write("\n")
  file.close()
  file = open(path, mode='a', encoding='utf8')

  # Initialize appropriate service.
  report_downloader = client.GetReportDownloader(version='v201809')

  # print(query)
  # print('')

  file.write(report_downloader.DownloadReportAsStringWithAwql(
     query, 'CSV', skip_report_header=False, skip_column_header=False,
      skip_report_summary=False, include_zero_impressions=True))
  file.close()

def dataumQuery(client, query):
    # Initialize appropriate service.
    report_downloader = client.GetReportDownloader(version='v201809')

    # Create report query.
    report_query = query

    tmp = report_downloader.DownloadReportAsStringWithAwql(
        report_query, 'CSV', skip_report_header=False, skip_column_header=False,
        skip_report_summary=False, include_zero_impressions=True)
    #This line grabs the account name from a string of CSV data. It splits all CSV values with a comma
    #grabs it at index 5, and then splits it apart from another value its stuck with.
    tmp =  tmp.split(',')[5].split('\n')[1]

    return tmp;
    
def initDictonary(path, dict):
    with open(path) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            try:
                dict[row[2]] = []
            except IndexError:
                dict[''] = []

    with open(path) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            try:
                dict[row[2]].append(row)
            except IndexError:
                dict[''].append('')

PAGE_SIZE = 500

customers = {}


def GetChildAccounts(account, accounts, links, depth=0):
  """Displays an account tree.

  Args:
    account: dict The account to display.
    accounts: dict Map from customerId to account.
    links: dict Map from customerId to child links.
    depth: int Depth of the current account in the tree.
  """
  prefix = '-' * depth * 2
  customers[account['customerId']] = account['name']
  if account['customerId'] in links:
    for child_link in links[account['customerId']]:
      child_account = accounts[child_link['clientCustomerId']]
      GetChildAccounts(child_account, accounts, links, depth + 1)


def getCustomerIDs(client):
  # Initialize appropriate service.
  managed_customer_service = client.GetService(
      'ManagedCustomerService', version='v201809')

  # Construct selector to get all accounts.
  offset = 0
  selector = {
      'fields': ['CustomerId', 'Name'],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  accounts = {}
  child_links = {}
  parent_links = {}
  root_account = None

  while more_pages:
    # Get serviced account graph.
    page = managed_customer_service.get(selector)
    if 'entries' in page and page['entries']:
      # Create map from customerId to parent and child links.
      if 'links' in page:
        for link in page['links']:
          if link['managerCustomerId'] not in child_links:
            child_links[link['managerCustomerId']] = []
          child_links[link['managerCustomerId']].append(link)
          if link['clientCustomerId'] not in parent_links:
            parent_links[link['clientCustomerId']] = []
          parent_links[link['clientCustomerId']].append(link)
      # Map from customerID to account.
      for account in page['entries']:
        accounts[account['customerId']] = account
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  # Find the root account.
  for customer_id in accounts:
    if customer_id not in parent_links:
      root_account = accounts[customer_id]

  # Display account tree.
  if root_account:
    GetChildAccounts(root_account, accounts, child_links, 0)
  else:
    print('Unable to determine a root account')

  return customers