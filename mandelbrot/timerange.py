# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import pyparsing as pp

from mandelbrot.model.timestamp import Timestamp, UTC

EpochDateTime = pp.Word(pp.srange('[1-9]'), pp.srange('[0-9]'))
def parseEpochDateTime(tokens):
    return datetime.datetime.fromtimestamp(int(tokens[0]), UTC)
EpochDateTime.setParseAction(parseEpochDateTime)

ISODateTimeUTC = pp.Regex(r'\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}Z')
def parseISODateTime(tokens):
    return datetime.datetime.strptime(tokens[0], '%Y-%m-%dT%H:%M:%SZ')
ISODateTimeUTC.setParseAction(parseISODateTime)

ISODateTimeAndOffset = pp.Regex(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}')
def parseISODateTimeAndOffset(tokens):
    return datetime.datetime.strptime(tokens[0], '%Y-%m-%dT%H:%M:%S%z')
ISODateTimeAndOffset.setParseAction(parseISODateTimeAndOffset)

ISODateTime = ISODateTimeUTC | ISODateTimeAndOffset

TimeValue = pp.Word(pp.srange('[1-9]'), pp.srange('[0-9]'))

UnitDays = pp.CaselessKeyword('day') | pp.CaselessKeyword('days')
UnitDays.setParseAction(lambda x: lambda hours: hours * 60 * 60 * 24)
UnitHours = pp.CaselessKeyword('hour') | pp.CaselessKeyword('hours')
UnitHours.setParseAction(lambda x: lambda hours: hours * 60 * 60)
UnitMinutes = pp.CaselessKeyword('minute') | pp.CaselessKeyword('minutes')
UnitMinutes.setParseAction(lambda x: lambda minutes: minutes * 60)
UnitSeconds = pp.CaselessKeyword('second') | pp.CaselessKeyword('seconds')
UnitSeconds.setParseAction(lambda x: lambda seconds: seconds)
TimeUnit = UnitDays | UnitHours | UnitMinutes | UnitSeconds

DirectionAgo = pp.CaselessLiteral("ago")
DirectionAgo.setParseAction(lambda x: lambda point,delta: point - delta)
DirectionAhead = pp.CaselessLiteral("ahead")
DirectionAhead.setParseAction(lambda x: lambda point,delta: point + delta)

RelativeDirection = DirectionAgo | DirectionAhead
RelativeDateTime = TimeValue + TimeUnit + RelativeDirection
def parseRelativeDateTime(tokens):
    value = int(tokens[0])
    magnify = tokens[1]
    shift = tokens[2]
    seconds = magnify(value)
    return shift(datetime.datetime.now(UTC), datetime.timedelta(seconds=seconds))
RelativeDateTime.setParseAction(parseRelativeDateTime)

DateTime = ISODateTime | RelativeDateTime | EpochDateTime

ClosedDateTimeRange = DateTime + pp.Suppress(pp.Literal('..')) + DateTime
LeftOpenDateTimeRange = pp.Literal('..') + DateTime
RightOpenDateTimeRange = DateTime + pp.Literal('..')

DateTimeRange = ClosedDateTimeRange | LeftOpenDateTimeRange | RightOpenDateTimeRange

DateTimePlusDelta = DateTime + pp.Suppress(pp.Literal('+')) + TimeValue + TimeUnit
def parseDateTimePlusDelta(tokens):
    start = tokens[0]
    value = int(tokens[1])
    magnify = tokens[2]
    delta = datetime.timedelta(seconds=magnify(value))
    return [start, start + delta]
DateTimePlusDelta.setParseAction(parseDateTimePlusDelta)

NowPlusDelta = pp.Suppress(pp.Literal('+')) + TimeValue + TimeUnit
def parseNowPlusDelta(tokens):
    start = datetime.datetime.now(UTC)
    value = int(tokens[0])
    magnify = tokens[1]
    delta = datetime.timedelta(seconds=magnify(value))
    return [start, start + delta]
NowPlusDelta.setParseAction(parseNowPlusDelta)

DateTimeWindow = ClosedDateTimeRange | DateTimePlusDelta | NowPlusDelta

def datetime_to_timestamp(dt):
    timestamp = Timestamp()
    timestamp.set_datetime(dt)
    return timestamp

def parse_datetime(string):
    """
    Parse a datetime string.  Datetimes may be specified using the following formats:

    ISOFORMAT       ISO-8601 format, e.g. "2015-05-01T12:45:00Z"
    RELATIVE        some magnitude relative to now, e.g. "2 hours ago" or "15 days ahead"
    EPOCH           seconds since the UNIX epoch

    :param string: The timerange to parse
    :type string: str
    :returns: the datetime as a Timestamp
    :rtype: Timestamp
    :raises ValueError: the timerange could not be parsed
    """
    try:
        return datetime_to_timestamp(DateTime.parseString(string, parseAll=True).asList()[0])
    except Exception as e:
        raise ValueError("failed to parse datetime '%s'" % string)

def parse_timerange(string):
    """
    Parse a timerange string.  Timeranges may be specified using the following formats:

    START..END      between START and END
    START..         from START to infinity
    ..END           from -infinity to END
   
    :param string: The timerange to parse
    :type string: str
    :returns: A 2-tuple containing the start and end timestamps
    :rtype: tuple[Timestamp,Timestamp]
    :raises ValueError: the timerange could not be parsed
    """
    try:
        start,end = DateTimeRange.parseString(string, parseAll=True).asList()
        start = None if start == ".." else datetime_to_timestamp(start)
        end = None if end == ".." else datetime_to_timestamp(end)
        return (start,end)
    except Exception as e:
        raise ValueError("failed to parse timerange '%s'" % string)

def parse_timewindow(string):
    """
    Parse a timewindow.  Timewindows may be specified using the following
    formats:

    START..END
    START+DELTA
    +DELTA

    :param string: The timewindow to parse
    :type string: str
    :returns: A 2-tuple containing the start and end timestamps
    :rtype: tuple[Timestamp,Timestamp]
    :raises ValueError: the timewindow could not be parsed
    """
    try:
        start,end = DateTimeWindow.parseString(string, parseAll=True).asList()
        return (datetime_to_timestamp(start), datetime_to_timestamp(end))
    except Exception as e:
        raise ValueError("failed to parse timewindow '%s'" % string)
