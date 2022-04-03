import json
from datetime import datetime
from django.db import models

# https://www.programiz.com/python-programming/datetime/strftime

DATETIME_FORMAT_API = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT_HUMAN = '%-d %B %Y %H:%M'
DATE_FORMAT_API = '%Y-%m-%d'
TIME_FORMAT_API = '%H:%M:%S'
DATE_FORMAT_HUMAN = '%-d %B %Y'
TIME_FORMAT_HUMAN = '%H:%M'


class Event(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    poster = models.CharField(max_length=300)
    link = models.CharField(max_length=100)
    day = models.CharField(max_length=30)
    time = models.CharField(max_length=30)
    datetime = models.CharField(max_length=30)
    duration = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    price_preorder = models.FloatField(null=True, blank=True)
    ticket_link = models.CharField(max_length=200)
    venue_name = models.CharField(max_length=200)
    venue_address = models.CharField(max_length=200)


    @staticmethod
    def parse_events(events_api_json):
        events_api = json.loads(events_api_json)['events']
        events = []
        for event_api in events_api:
            try:
                event = Event()

                event.id = event_api['id']
                event.link = f'http://www.alcalaesmusica.org/events/{event.id}'
                event.title = event_api['title']
                event.description = event_api['description']
                event.poster = event_api['poster']
                event.day = event_api['day']
                event.time = event_api['time']
                event.datetime = event.day + ' ' + event.time
                event.duration = event_api['duration']
                event.price = event_api['price']
                event.price_preorder = event_api['price_preorder']
                event.ticket_link = event_api['ticket_link']
                event.venue_name = event_api['venue_name']
                event.venue_address = event_api['venue_address']

                if is_old(event):
                    continue

                events.append(event)
            except Exception as e:
                error = f"Error parsing event: {event_api['id']}, name: {event_api['title']}\nException: {e}"
                print(error)
                raise Exception(error)


        events_sorted = sorted(
            events,
            key=lambda x: datetime.strptime(x.datetime, DATETIME_FORMAT_API), reverse=False
        )

        # for event in events_sorted:
        #     if len(event.event_types_ids) > len(set(event.event_types_ids)) > 1:
        #         raise Exception('hay duplicados!: ' + event.title)

        return events_sorted

    def get_type_names(self):
        return ', '.join([event_type.name for event_type in self.event_types.all()])

    def get_date_from_human_format(self):
        return self.convert_date_to_human_format(self.date_from)

    def get_date_to_human_format(self):
        return self.convert_date_to_human_format(self.date_to)

    def get_date_human_format(self):
        date_human = self.convert_datetime_formats(self.day, DATE_FORMAT_API, DATE_FORMAT_HUMAN)
        day_of_week = self.convert_datetime_formats(self.day, DATE_FORMAT_API, "%A")
        return day_of_week.capitalize() + ", " + date_human

    def get_time_human_format(self):
        time_human = self.convert_datetime_formats(self.time, TIME_FORMAT_API, TIME_FORMAT_HUMAN)
        return time_human

    def get_times(self):
        time_human_from = self.convert_datetime_formats(self.date_from, DATETIME_FORMAT_API, TIME_FORMAT_HUMAN)
        time_human_to = self.convert_datetime_formats(self.date_to, DATETIME_FORMAT_API, TIME_FORMAT_HUMAN)
        if time_human_from == time_human_to:
            return time_human_from
        else:
            return 'De %s a %s' % (time_human_from, time_human_to)
        pass

    def has_times(self):
        time_human_from = self.convert_datetime_formats(self.date_from, DATETIME_FORMAT_API, '%H:%M:%S')
        time_human_to = self.convert_datetime_formats(self.date_to, DATETIME_FORMAT_API, '%H:%M:%S')
        return not (time_human_to == time_human_from == '00:00:00')


    @staticmethod
    def convert_date_to_human_format(date):
        date_parsed = datetime.strptime(date, DATETIME_FORMAT_API)
        return date_parsed.strftime(DATETIME_FORMAT_HUMAN)

    @staticmethod
    def convert_datetime_formats(date, format_from, format_to):
        date_parsed = datetime.strptime(date, format_from)
        return date_parsed.strftime(format_to)

    def date_between(self, date_begin, date_end):
        date = datetime.strptime(self.datetime, DATETIME_FORMAT_API)
        return date_begin <= date <= date_end

    def __str__(self):
        return f'{self.title} - {self.date_from}'


def is_old(event):
    try:
        day = datetime.strptime(event.datetime, DATETIME_FORMAT_API)
        now = datetime.now()
        return day <= now
    except:
        print("(caught) error date: " + event.date_to)
        return False


def remove_duplicates(items):
    return list(dict.fromkeys(items))
