import time, re

def date(string):
    '''
    Extracts date from title of thread and returns date in seconds
    '''
    if 'progect ' and '@' in string:
        date = re.findall(r'\w+,\s\w+\s\d{2},\s\d{4}\s@\s\d',
                    string, re.I)[0].replace(',', '').replace('@','')
                    
                    
        dateseconds = time.mktime(time.strptime(date, "%A %B %d %Y %I"))

        return dateseconds
    else:
        return False
    
def confirm(dateseconds):
    '''
    Returns value based on time left from date in seconds input
    '''
    
    time = time.time()
    if (dateseconds - time) <= 0:
        return True, True
    elif (dateseconds - time) <= 600:
        message = '10 minutes'
        title = '10 minutes'
        return message
    
    elif (dateseconds - time) <= 3600:
        messasge = "1 hour"
        title = '1 hour'
        return message
    
    elif (dateseconds - time) <= 86400:
        message = "24 hours"
        title = '24 hours'
        return message, title
    else:
        return False, False
        
def main():
    pass
    
if __name__ == '__mani__':
    main()
