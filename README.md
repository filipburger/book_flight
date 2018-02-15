# book_flight

This is simple application to search cheapest or fastest flight connection and to create 'fake'
reservation using free API from  Kiwi.com, but can be easily redesigned to application for real use. 
This script was written as entry task to course called _Kiwi.com_ _python_ _weekend_
and should serve to mainly for exercising and educational purposes. To learn more about kiwi.com free API check
[APIARY](https://skypickerpublicapi.docs.apiary.io/#reference/flights) This app is supposed to be launched from command line
using sys.argv as parameters described bellow:

## Usage

### Mandatory parameters:
**--date** after this identifier enter date in format dd/mm/YYYY  
**--from** enter starting destination using airports[iata codes](https://en.wikipedia.org/wiki/IATA_airport_code)  
**--to** final destination in iatacode  

### Optional parameters:
**--return** number of nights you wish to spend in destination, if not speicified single-way itinerary will be returned  
**--bags** number of checked baggage you wish to purchase for your flight, if not specified default is 0, maximum 2  
**--fastest** no values comes after this identifier, it will change search prefereces from default cheapest to fastest  

example:
```python bookflight.py --date 02/04/2018 --from PRG --to BCN --return 5 --bags 1 --fastest```
Will return fastest(shortest duration) flight departing at 2nd April from Prugue to Barcelona with return flight on 7th April.
With one checked baggage.

## Documentation

### Main functions:  
**parse_commandline** - to parse arguments from command line and handling potentional errors caused by wrong user inputs.  
Returns dictionary with keys:values prepared for payload and number of baggage user wish to purchase.  
**parse_payload** - parse payload to meet APIs requirements and add rest of parameters to get desired response from Kiwi.com API.  
**search_flight** - thanks to full using API features our response is sorted by price or flight duration, so this funtion take first result.  
If bag or  two are requested it keeps itinerate result until find some itinerary meet our requirments. Ruturns one cheapest or fastest
itinerary.
**book_flight** - post request in JSON with booking token (for API to recognize which flight we want) and mandatory informations about
our test passenger, returns PNR code and status of reservation.  

### Secondary functions:  
**report** - wrote this function for testing purposes, but I decided to keep it in script as I find more satisfying to see what itinerary has been booked.  
**datetime_convert** - just help function with conversion time stamps in unix to human readable form for string formating used in report
