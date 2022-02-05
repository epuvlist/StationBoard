import zeep
from zeep.cache import SqliteCache
from zeep.transports import Transport

transport = Transport(cache=SqliteCache())

client = zeep.Client(wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL', transport=transport)

response = client.service.ListOfCountryNamesByCode()

for countries in response:
    cCode = countries['sISOCode']
    print(f"{countries['sName']}, {cCode}, {client.service.CapitalCity(cCode)}, {client.service.CountryCurrency(cCode)['sName']}")