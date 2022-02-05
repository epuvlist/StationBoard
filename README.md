# Station display board (Zeep / WSDL version)
Train departures real time display using the UK National Rail Darwin web service.

This Python program presents a live departure board for a selected UK railway
station. It uses a SOAP interface into the National Rail Darwin web service.

It requires the Python modules Zeep and Tkinter.

wsdl_test.py is included as an example of a Zeep interface. It interrogates the openly 
available oorsprong.org webservice for a list of countries.

This version uses the Python Zeep module to inspect the WSDL. Zeep handles all
the http request and response operations, and also abstracts away all XML parsing,
making these aspects quite simple in the program below. The advantage of using
the WSDL over hard coding the XML request is that if Darwin release a new version
of the WSDL then this can simply be updated in the config file. The program does
not need to know about the underlying XML data schemas, XSD files etc.

The configuration file StationBoard.ini must be present in the same
directory as the program. Important elements which must be present in the
config file are:

- SOAP section
* key:  A valid user key for accessing the Darwin service. To obtain a key visit 
      https://www.nationalrail.co.uk/100296.aspx.
      
* wsdl: URL of the current WSDL

- station section

* crs: Three-letter station code for the desired departure station. For a list
     of codes see https://www.nationalrail.co.uk/stations_destinations/48541.aspx

The config file also contains optional configs for display font
and colours.
