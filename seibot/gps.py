"""GPS time"""
import datetime


def get_gpstime_now():
    """Returns gps time now.
    
    Returns
    -------
    gps_time : float
        The current GPS timestamp.
    """
    gps_epoch = datetime.datetime(
        1980, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc)

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    time_difference = (now_utc - gps_epoch).total_seconds()
    
    # TODO Hardcoded leap seconds.
    leap_seconds = 18

    gps_time = time_difference + leap_seconds

    return gps_time
