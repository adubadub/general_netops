from datetime import datetime

days = [
    'monday', 'mon', 'tuesday', 'tue', 'wednesday', 'wed, ''thursday', 'thu',
    'friday', 'fri', 'saturday', 'sat', 'sunday', 'sun']
months = [
    'january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr', 'may', 
    'june', 'jun', 'july', 'jul', 'august', 'aug', 'september', 'sep', 
    'october', 'oct', 'november', 'nov', 'december', 'dec']
dt_formats = [
    "%a %b %d %H:%M:%S %Y", "%a %b %d %Y %H:%M:%S", "%b %d %H:%M:%S %Y", "%b %d %Y %H:%M:%S"]

def StringtoDT(timestring):
    timestring = timestring.replace(',', '')
    timestring_split = timestring.split()
    today = datetime.today().strftime('%a')
    new_timestring = []
    for i in timestring_split:
        try:
            if int(i) > 31:
                new_timestring.insert(4, i)
            else:
                new_timestring.insert(2, i)
        except:
            if i.lower() in days:
                i = ''.join([char for char in i][0:3])
                new_timestring.insert(0, i)
            if i.lower() in months:
                i = ''.join([char for char in i][0:3])
                new_timestring.insert(1, i)
            if ':' in i:
                if 'pm' in timestring.lower():
                    i_split = i.split(':')
                    hour = int(i_split[0])
                    hour = hour + 12
                    i_split[0] = str(hour)
                    i = ':'.join(i_split)
                    new_timestring.insert(3, i)
                else:
                    new_timestring.insert(3, i)
            if 'utc' in i.lower():
                pass
            if 'am' in i.lower():
                pass

    if len(new_timestring) < 5:
        new_timestring.insert(0, today)
    new_timestring = ' '.join(new_timestring)
    dev_dt = 'Invalid datetime format'

    for val in dt_formats:
        try:
            dev_dt = datetime.strptime(new_timestring, val)
            if dev_dt != 'Invalid datetime format':
                break
        except:
            continue
    return dev_dt

def DTtoString(dtime):
    pass