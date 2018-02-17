import requests
import json
import sys
import datetime

URL = 'https://api.skypicker.com/flights?'
VALID_IDENTIFIERS = {'--date': None,
                     '--from': None,
                     '--to': None,
                     '--return': None,
                     '--bags': ('0', '1', '2')}
MANDATORY = ('date', 'from', 'to')


def parse_commandline(identifiers, mandatory):

    payload = {}
    bags_count = 0

    for identifier, values in identifiers.items():
        try:
            i = sys.argv.index(identifier) + 1
            arg = sys.argv[i]

            if values and arg not in values:  # this one is checking if there is any invalid value
                print('Not permitted value for option {0}.'
                      '\nPermitted: {1}'.format(identifier, values))
                sys.exit()

            param = identifier.strip('--')
            payload[param] = arg

        except ValueError:
            continue
        except IndexError:
            print('Missing value for option {}'.format(identifier))
            sys.exit()

        # now lets check if users date is in correct format and in the future
        try:
            datetime.datetime.strptime(payload['date'], '%d/%m/%Y')
        except ValueError:
            print("Incorrect data format, should be DD/MM/YYYY")
            sys.exit()
        if datetime.datetime.strptime(payload['date'], '%d/%m/%Y') < datetime.datetime.now():
            print('Inserted date is for today or in the past, please type in future date')
            sys.exit()

        if '--bags' in sys.argv:
            bags_count = (sys.argv[sys.argv.index('--bags') + 1])

    for identifier in mandatory:  # this one is checking if user entered mandatory info
            if identifier not in payload:
                print('Missing mandatory identifier: {}.'.format(identifier))
                sys.exit()

    return payload, bags_count


def parse_payload(payload):  # change keys from payload to meet api requirements
    try:
        payload['dateFrom'] = payload.pop('date')
        payload['dateTo'] = payload['dateFrom']  # up limit for flight search
        payload['flyFrom'] = payload.pop('from')

        if '--return' in sys.argv:
            i = sys.argv.index('--return')+1
            night_in_destination = sys.argv[i]
            payload['daysInDestinationFrom'] = night_in_destination
            payload['daysInDestinationTo'] = night_in_destination
            payload['typeFlight'] = 'return'

        # to sort results by duration we need parameter bellow
        if '--fastest' in sys.argv:
            payload['sort'] = 'duration'
        payload['partner'] = 'picky'
    except KeyError:
        pass

    return payload


def search_flight(flights):
    # we let kiwi api to sort results so we want to take first one
    if BAGS_COUNT == 0:
        try:
            return flights[0]
        except KeyError:
            print('No flight found. Try different date/route option...')
            sys.exit()

    # this loop will find first flight with required number of bags
    for flight in flights:
        try:
            if flight['bags_price'][BAGS_COUNT] != 0:
                return flight
        except KeyError:
            continue
    print('Itinerary with required baggage allowance not found.')
    sys.exit()


def datetime_convert(time_stamp):
    # to convert unix stamp to human readable form, will be used in printing report
    return datetime.datetime.fromtimestamp(
        int(time_stamp)).strftime('%Y-%m-%d %H:%M:%S')


def report(itinerary_data, currency, bags_number):

    x = 1  # to mark order of found flights
    report_template = '{0}.{1}:\nDeparture: {2} {3} > Arrival: {4} {5} - flight number: {6}{7}\n'
    print('Your itinerary:\n')
    for segment in itinerary_data['route']:

            if segment['return'] == 0:
                flight_type = 'outbound'
            else:
                flight_type = 'inbound'

            print(report_template.format(x, flight_type, datetime_convert(segment['dTime']),
                  segment['flyFrom'], datetime_convert(segment['aTime']),
                   segment['flyTo'], segment['airline'], segment['flight_no']))
            x += 1

    print('Itinerary price: {0} {1}'.format(result['price'], currency))

    if int(bags_number) > 0:
        print('Price for baggage: {0} {1}'.format(result['bags_price'][str(bags_number)], currency))
        print('Total: {0} {1}\n'.format((result['price'] + result['bags_price'][bags_number]), currency))


def book_flight(booking_token, bags_number):
    data = {'bags': bags_number,
            'booking_token': booking_token,
            'currency': 'EUR',
            'passengers': [{'birthday': '1989-01-25',
                            'documentID': 'EH000000',
                            'email': 'filip.burger@kiwi.com',
                            'firstName': 'test',
                            'lastName': 'test',
                            'title': 'Mr'}]}
    headers = {'Content-type': 'application/json'}
    url = 'http://128.199.48.38:8080/booking'
    response = requests.post(url, data=json.dumps(data), headers=headers).json()
    for key, value in response.items():
        print('{0} : {1}\n'.format(key, value))
    return response


if __name__ == "__main__":

    PAYLOAD, BAGS_COUNT = parse_commandline(VALID_IDENTIFIERS, MANDATORY)
    r = requests.get(URL, params=parse_payload(PAYLOAD))
    print('\nRequest status:', r.status_code, '\n')
    request = json.loads(r.text)
    result = search_flight(request['data'])
    BOOKING_TOKEN = result['booking_token']
    CURRENCY = request['currency']
    report(result, CURRENCY, BAGS_COUNT)
    book_flight(BOOKING_TOKEN, BAGS_COUNT)
