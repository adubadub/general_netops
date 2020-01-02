def ConvertTD(duration):
    days, seconds = duration.days, duration.seconds
    days_to_seconds = days * 86400
    total_seconds = days_to_seconds + seconds
    offset = []
    drift = []
    if total_seconds < 86399:
        if total_seconds < 59:
            if total_seconds > 2:
                offset.append('seconds')
                drift.append(duration.seconds)
            else:
                offset.append('GOOD')
                drift.append(duration.seconds)
        else:
            offset.append('minutes')
            drift.append(total_seconds // 60)
    else:
        offset.append('days')
        drift.append(duration.days)

    return offset, drift