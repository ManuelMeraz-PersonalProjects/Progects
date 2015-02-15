import time, re

remind_24 = None
remind_hour = None
remind_10 = None


def date(string):
    '''
    Extracts date from title of thread and returns date in seconds
    '''
    if 'progect' and '@' in string:
        date = re.findall(r'\w+,\s\w+\s\d{1,2},\s\d{4}\s@\s\d{1,2}:\d{2}\s\w+', string, re.I)
        if len(date) == 1:
            date = date[0].replace(',', '').replace('@','')
        
        else:
            return False
                    
                    
        dateseconds = time.mktime(time.strptime(date, "%A %B %d %Y %I:%M %p"))

        return dateseconds
    else:
        return False
    
def confirm(dateseconds):
    '''
    Returns value based on time left from date in seconds input
    '''
    message = None
    title = None
    
    global remind_10
    global remind_24
    global remind_hour
    
    nowtime = dateseconds - time.time()
    if nowtime <= 0:
        return True, True
    elif nowtime <= 600 and remind_10 == None:
        message = '10 minutes'
        title = '10 minutes'
        remind_10 = True
        return message, title
    
    elif nowtime <= 3600 and remind_hour == None:
        message = "1 hour"
        title = '1 hour'
        remind_hour = True
        return message, title
    
    elif nowtime <= 86400 and remind_24 == None:
        message = "24 hours"
        title = '24 hours'
        remind_24 = True
        return message, title
    else:
        return False, False
        
def main():
    string = 'progect  Saturday, February 7, 2015 @ 8 PM PST'
    print (date(string))
    
if __name__ == '__main__':
    main()
