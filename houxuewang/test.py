import datetime
to_day = datetime.datetime.now()
log_file_path = './log/scrapy {}_{}_{}.log'.format(to_day.year, to_day.month, to_day.day)
print(log_file_path)