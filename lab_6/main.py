import random
from datetime import datetime, timedelta
from pyproj import Geod
import csv
from collections import namedtuple


LandingLine = namedtuple('LandingLine', ['distance', 'width'])


class Airport:
    AIRPORT_TYPE_DESCRIPTION = {
        'heliport': 'Can hold only helicopters',
        'small_airport': 'Can hold only passenger, non-combat planes',
        'seaplane_base': 'Can hold only Marine adopted planes',
        'medium_airport': 'Can hold only passengers planes',
        'large_airport': 'Can hold anything excluding helicopters'
    }

    def __init__(self, airport_id, name, coordinates, airport_type):
        self.id = airport_id
        self.name = name
        self.coordinates = coordinates
        self.airport_type = airport_type
        self.hangars = [None] * random.randint(1, 5)

        self.passengers = []
        self.amount_of_cargo = 0
        self.lines = []

    def operate_aircraft_landing(self, aircraft):
        if None in self.hangars:
            if self.check_if_aircraft_can_land(aircraft):
                self.put_vehicle(aircraft)
                print(f'Aircraft {aircraft.aircraft_id} has successfully landed at {self.name}.')
            else:
                print(f'Aircraft {aircraft.aircraft_id} cannot land at {self.name}. Sending it back.')

    def operate_aircraft_take_off(self, destination_airport='random'):
        if destination_airport == 'random':
            destination_airport = random.choice(list(self.airports.keys()))

        for i, aircraft in enumerate(self.hangars):
            if aircraft is not None and aircraft.destination_airport == destination_airport:
                self.hangars[i] = None

    def put_vehicle(self, aircraft):
        if None in self.hangars:
            self.hangars[self.hangars.index(None)] = aircraft

    def show_airport_type_description(self):
        print(self.AIRPORT_TYPE_DESCRIPTION[self.airport_type]
              if self.airport_type in self.AIRPORT_TYPE_DESCRIPTION else None)

    def get_number_of_free_hangars(self):
        return self.hangars.count(None)

    def show_aircrafts(self):
        print(f'Aircrafts at {self.name}:')
        print(f'- {aircraft.aircraft_id}' for aircraft in self.hangars if aircraft)

    def check_if_aircraft_can_land(self, aircraft):
        if self.airport_type == 'Landing Lines':
            for line in self.lines:
                if (line.distance >= aircraft.required_landing_distance and
                        line.width >= aircraft.required_landing_width * 0.8):
                    return True
            return False
        elif self.airport_type == 'Regular':
            return True

    def __str__(self):
        return f'Airport {self.id} - {self.name} (type: {self.airport_type})'

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, Airport) else False

    def take_passengers(self, passengers):
        self.passengers.extend(passengers)

    def move_passengers_to_aircraft(self, aircraft, passengers):
        if aircraft in self.hangars:
            aircraft.passengers.extend(passengers)
            self.passengers = [i for i in self.passengers if i not in passengers]

    def take_cargo(self, amount):
        self.amount_of_cargo += amount

    def ship_cargo_to_aircraft(self, aircraft, amount):
        if aircraft in self.hangars:
            aircraft.cargo += amount
            self.amount_of_cargo -= amount


def get_airports_data():
    airports = []

    with open('airports_.csv', 'r', encoding='utf-8') as csv_file:
        all_airports = list(csv.DictReader(csv_file))

        airport_types = {}
        selected_airports = []

        for i in all_airports:
            airport_type = i['type']
            if airport_type not in airport_types:
                airport_types[airport_type] = []
            airport_types[airport_type].append(i)

        for airport_type, airport_list in airport_types.items():
            selected = random.sample(airport_list, min(len(airport_list), 20))
            selected_airports.extend(selected)

        for i in selected_airports:
            airport_id = str(i['id']) + '-' + i['ident']
            name = i['name']
            coordinates = (float(i['latitude_deg']), float(i['longitude_deg']))
            airport_type_description = i['type']

            airports.append(Airport(airport_id, name, coordinates, airport_type_description))

        return airports


print(get_airports_data())
