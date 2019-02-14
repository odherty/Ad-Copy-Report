import csv
def reportQuery(client, query, path):
  # Specify where to download the file here.
  file = open(path, 'w')
  file.write("\n")
  file.close()
  file = open(path, 'a')

  # Initialize appropriate service.
  report_downloader = client.GetReportDownloader(version='v201809')

  # Create report query.
  report_query = query

  file.write(report_downloader.DownloadReportAsStringWithAwql(
     report_query, 'CSV', skip_report_header=False, skip_column_header=False,
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
    tmp = list(csv.reader(tmp, delimiter=''))
    print(tmp)
    return tmp[3];

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