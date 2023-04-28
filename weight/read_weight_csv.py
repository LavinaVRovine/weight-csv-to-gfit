import csv
import datetime
import dateutil.tz
import dateutil.parser
from dateutil import tz
tz.gettz

TIME_ZONE = tz.gettz("Europe/Prague")
DAWN_TIME = datetime.datetime(1970, 1, 1, tzinfo=TIME_ZONE)
POUNDS_PER_KILOGRAM = 2.20462

def nano(val):
  """Converts a number to nano (str)."""
  return '%d' % (int(val) * 1e9)

def epoch_of_time_str(dateTimeStr, tzinfo):
  log_time = datetime.datetime.strptime(dateTimeStr, "%d.%m.%Y %H:%M:%S").replace(tzinfo=tzinfo)
  if log_time.year == 2023 and log_time.month == 1 and log_time.day == 6:
      print()
  return (log_time - DAWN_TIME).total_seconds()

def read_weights_csv():

    weights = []
    for f_name in ("weights", "weights2",):
        is_header = True
        with open(f'{f_name}.csv', 'r', encoding="utf-8") as csvfile:
            weights_reader = csv.reader(csvfile, delimiter=',')
            for row in weights_reader:
                if is_header:
                    is_header=False
                    continue
                weights.append(dict(
                    seconds_from_dawn=epoch_of_time_str(row[0], TIME_ZONE),
                    weight=float(row[1])
                    ))
    return weights

def read_weights_csv_with_gfit_format():
    weights = read_weights_csv()
    gfit_weights = []
    for weight in weights:
        gfit_weights.append(dict(
            dataTypeName='com.google.weight',
            endTimeNanos=nano(weight["seconds_from_dawn"]),
            startTimeNanos=nano(weight["seconds_from_dawn"]),
            value=[dict(fpVal=weight["weight"]/POUNDS_PER_KILOGRAM)],
        ))
    return gfit_weights

if __name__=="__main__":
    gfit_weights = read_weights_csv_with_gfit_format()
