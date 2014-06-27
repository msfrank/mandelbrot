import datetime
from dateutil.tz import tzutc
from mandelbrot.timerange import parse_datetime, parse_timerange, parse_timewindow

def test_parse_epoch_datetime():
    t = parse_datetime("1403784000")
    assert t == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())

def test_parse_iso_datetime():
    t = parse_datetime("2014-06-26T12:00:00Z")
    assert t == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())

def test_parse_relative_datetime():
    now = datetime.datetime.now(tzutc())
    t = parse_datetime("1 hour ago")
    assert t >= now - datetime.timedelta(hours=1)
    assert t < now - datetime.timedelta(hours=1) + datetime.timedelta(seconds=5)

def test_parse_timerange_closed_range():
    start,end = parse_timerange("2014-06-26T12:00:00Z .. 2014-06-26T13:00:00Z")
    assert start == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())
    assert end   == datetime.datetime(2014, 6, 26, 13, 0, 0, 0, tzutc())

def test_parse_timerange_left_open_range():
    start,end = parse_timerange(".. 2014-06-26T13:00:00Z")
    assert start == None
    assert end   == datetime.datetime(2014, 6, 26, 13, 0, 0, 0, tzutc())

def test_parse_timerange_right_open_range():
    start,end = parse_timerange("2014-06-26T12:00:00Z ..")
    assert start == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())
    assert end   == None

def test_parse_timewindow_closed_range():
    start,end = parse_timewindow("2014-06-26T12:00:00Z .. 2014-06-26T13:00:00Z")
    assert start == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())
    assert end   == datetime.datetime(2014, 6, 26, 13, 0, 0, 0, tzutc())

def test_parse_timewindow_datetime_plus_delta():
    start,end = parse_timewindow("2014-06-26T12:00:00Z + 2 hours")
    assert start == datetime.datetime(2014, 6, 26, 12, 0, 0, 0, tzutc())
    assert end   == datetime.datetime(2014, 6, 26, 14, 0, 0, 0, tzutc())

def test_parse_timewindow_now_plus_delta():
    now = datetime.datetime.now(tzutc())
    start,end = parse_timewindow("+ 2 hours")
    assert start >= now
    assert start < now + datetime.timedelta(seconds=5)
    assert end > start
    assert end - start == datetime.timedelta(hours=2)
