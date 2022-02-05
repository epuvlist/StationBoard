#!/usr/bin/python3

'''
Station display board (Zeep / WSDL version)
===========================================

This program presents a live departure board for a selected UK railway
station. It uses a SOAP interface into the National Rail Darwin web service.

This version uses the Python Zeep module to inspect the WSDL. Zeep handles all
the http request and response operations, and also abstracts away all XML parsing,
making these aspects quite simple in the program below. The advantage of using
the WSDL over hard coding the XML request is that if Darwin release a new version
of the WSDL then this can simply be updated in the config file. The program does
not need to know about the underlying XML data schemas, XSD files etc.

The configuration file StationBoard.ini must be present in the same
directory as the program. Important elements which must be present in the
config file are:

Section   Option  Detail
=======   ======  ======
SOAP      key     A valid user key for accessing the Darwin service
SOAP      wsdl    URL of the current WSDL
station   crs     The desired departure station

The config file also contains optional configs for display font
and colours.

# TODO:
# Make columns fixed width to stop it constantly resizing?
# Add a menu with options to config station?
'''

# Module imports

import zeep
from zeep.cache import SqliteCache
from zeep.transports import Transport
import tkinter as tk
from tkinter import messagebox
from datetime import datetime as Tm
from configparser import ConfigParser
from sys import exit

# Class definitions

class OpenLDBWSApp:
    """An interface with the Darwin OpenLDBWS web service for live train running information"""

    def __init__(self):

        global config
        
        # Cache the WSDL in order to improve performance.
        # Example taken from https://docs.python-zeep.org/en/master/client.html#caching-of-wsdl-and-xsd-files
        transport = Transport(cache=SqliteCache())
        
        # Initialise the Zeep client to point to the
        # OpenLDBWS WSDL
        self.client = zeep.Client(wsdl = config['SOAP']['wsdl'], transport=transport)

        # The SOAP header is used to pass the authentication key 
        header = zeep.xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
            zeep.xsd.ComplexType([
                zeep.xsd.Element(
                '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
                zeep.xsd.String()),
                    ])
                )
        
        self.header_value = header(TokenValue=config['SOAP']['key'])
        
    def getServiceInfo(self):
        # Returns a zeep response object for the GetDepartureBoardResponse
        # or None if nothing retrieved

        try:
            response = self.client.service.GetDepartureBoard \
                (numRows=config['display']['rows'], \
                crs=config['station']['crs'], \
                _soapheaders=[self.header_value])
            
            # Save the response for debugging:
            #if response['nrccMessages'] != None:
            #    with open ('DarwinResponse.zeep','w') as f:
            #        f.write(str(response))

        except Exception as ze:
            # (zeep.exceptions.Fault, ConnectionError) as ze:
            display.statusbar_text(f"Web service error: {ze}")
            response = None
            
        else:
            display.statusbar_text('OK')
            
        # The response is a zeep response object. It behaves like
        # a Python dictionary and can be accessed as such, e.g. departure
        # station code is response['locationName'].
        # For full schema see http://lite.realtime.nationalrail.co.uk/openldbws      
        return response
        
# end of OpenLDBWS class definition

class DisplayApp:
    
    """Class holding the Tkinter GUI functionality"""
    
    stop_msg = "Stopping..."

    def __init__(self,bgcolour,headfgcolour,itemfgcolour):
        
        global config
 
        self.root = tk.Tk()
        self.root.config(bg=bgcolour)
        self.mainwindow = tk.Frame(self.root)
        
        # Pack the display window inside the root window, with
        # expand set to true. This has the effect of centering the display
        # window within the root window if the user enlarges or
        # maximises the window.
        self.mainwindow.pack(expand=tk.TRUE)
        
        self.mainwindow.config(bg=bgcolour)
        
        # Apply default font of Arial if none specified in config         
        font_name = config['fonts']['name'] if config.has_option('fonts','name') else 'Arial'

        # Apply default font size of 24 if none specified in config             
        normal_font = (font_name, config['fonts']['normal']) if config.has_option('fonts','normal') else '24'
               
        # Apply default header size of 36 if none specified in config       
        header_font = (font_name,config['fonts']['header']) if config.has_option('fonts','header') else '36'
    
        # Apply default time display size of 24 if none specified in config
        curtime_font = (font_name,config['fonts']['time']) if config.has_option('fonts','time') else '24'

        # Apply default padding of 10 if none specified in config
        self.default_padx = config['display']['padx'] if config.has_option('display','padx') else 10

        # Colours to be used in all item displays on
        # function calls to this object
        self.itemfgcolour = itemfgcolour
        self.bgcolour = bgcolour

        # Create header labels
        self.main_header = tk.Label(self.mainwindow, text='Departures')
        self.main_header.config(font=header_font,bg=bgcolour,fg=headfgcolour)
        self.main_header.grid(sticky=tk.W,row=0,column=0, columnspan=4)

        self.time_header = tk.Label(self.mainwindow, text='Time')
        self.time_header.config(justify=tk.LEFT,font=normal_font,bg=bgcolour,fg=headfgcolour,padx=self.default_padx)
        self.time_header.grid(sticky=tk.W,row=1,column=0)
        
        self.dest_header = tk.Label(self.mainwindow, text='Destination')
        self.dest_header.config(justify=tk.LEFT,font=normal_font,bg=bgcolour,fg=headfgcolour,padx=self.default_padx)
        self.dest_header.grid(sticky=tk.W,row=1,column=1)
        
        self.plat_header = tk.Label(self.mainwindow, text='Plat')
        self.plat_header.config(justify=tk.LEFT,font=normal_font,bg=bgcolour,fg=headfgcolour,padx=self.default_padx)
        self.plat_header.grid(sticky=tk.W,row=1,column=2)
        
        self.expt_header = tk.Label(self.mainwindow, text='Expt')
        self.expt_header.config(justify=tk.LEFT,font=normal_font,bg=bgcolour,fg=headfgcolour,padx=self.default_padx)
        self.expt_header.grid(sticky=tk.W,row=1,column=3)

        self.cars_header = tk.Label(self.mainwindow, text='Cars')
        self.cars_header.config(justify=tk.LEFT,font=normal_font,bg=bgcolour,fg=headfgcolour,padx=self.default_padx)
        self.cars_header.grid(sticky=tk.W,row=1,column=4)

        self.statusbar = tk.Label(self.mainwindow,relief=tk.SUNKEN)
        self.statusbar.config(anchor=tk.W,justify=tk.LEFT,font=('Arial','14'),bg='#CCCCCC')

        self.Esc_to_exit = tk.Label(self.mainwindow,relief=tk.SUNKEN)
        self.Esc_to_exit.config(anchor=tk.W,justify=tk.LEFT,font=('Arial','14'),bg='#CCCCCC')
        self.Esc_to_exit.config(text = 'Esc to exit')
        
        # Create display boxes to be re-used in each refresh of the
        # display, as lists of 10 labels 
        self.time_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.dest_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.plat_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.expt_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.cars_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.delayreason_disp = [tk.Label(self.mainwindow) for x in range(10)]
        self.cancelreason_disp = [tk.Label(self.mainwindow) for x in range(10)]
        
        # Configure the display boxes
        
        for lbl in self.time_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,padx=self.default_padx)

        for lbl in self.dest_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,padx=self.default_padx)

        for lbl in self.plat_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,padx=self.default_padx)

        for lbl in self.expt_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,padx=self.default_padx)
            
        for lbl in self.cars_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,padx=self.default_padx)
  
        for lbl in self.delayreason_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,justify=tk.LEFT,wraplength=450,padx=self.default_padx)
 
        for lbl in self.cancelreason_disp:
            lbl.config(font=normal_font,bg=self.bgcolour,fg=self.itemfgcolour,justify=tk.LEFT,wraplength=450,padx=self.default_padx)
        
        # Label to show the current time
        self.curtime = tk.Label(self.mainwindow)
        self.curtime.config(font=curtime_font,bg=self.bgcolour,fg=self.itemfgcolour)
        
        # Set up keyboard event handler
        self.root.bind("<Key>", self.handle_keyevent)

        # Set up window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self.handle_windowclose)
        
    def statusbar_text(self, msg):
        self.statusbar.config(text = msg)
        
    def update_time(self):
        self.curtime.config(text=Tm.today().strftime('%H:%M:%S'))
        self.curtime.grid(row=0,column=3,columnspan=2)
        
        # Queue again to tick once per second
        if Running:
            self.mainwindow.after(1000,self.update_time)

    def display_info(self,GSBR):
    # Send the received information to the display.
    # This function receives a GetDepartureBoardResponse object as argument.
        
        data_OK = True
        
        if GSBR == None:
            self.statusbar_text("No data received")
            data_OK = False
            
        if data_OK and 'trainServices' not in GSBR:
            self.statusbar_text("No services available")
            data_OK = False
        elif data_OK and GSBR['trainServices'] == None:
            self.statusbar_text("No services available")
            data_OK = False
            
        display_row = 2 # start on row 2 of the window
        row_listindex = 0 # index to the arrays of labels
            
        if data_OK:
        
            # Window title only needs changing on first access
            if display.root.title() == 'tk':
                display.root.title('Departures from %s' % GSBR['locationName'])

            # For each train service, send details to Tkinter window
            for services in GSBR['trainServices']['service']:
            
                try:
                    
                    # Departure time
                    self.time_disp[row_listindex].config(text=services['std'])
                    self.time_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=0)
        
                    # Destination
                    self.dest_disp[row_listindex].config(text=services['destination']['location'][0]['locationName'])
                    self.dest_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=1)
            
                    # Platform
                    # plat = services['platform'] if services['platform'] != None else ''
                    self.plat_disp[row_listindex].config(text=services['platform'] if services['platform'] != None else '')
                                    
                    self.plat_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=2)

                    # Expected time
                    self.expt_disp[row_listindex].config(text=services['etd'])
                    self.expt_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=3)
            
                    # No. of cars
                    self.cars_disp[row_listindex].config(text=services['length'])
                    self.cars_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=4)

                    if services['isCancelled'] and services['cancelReason'] is not None:
                        # if there is a cancel reason then print it on the next row
                        display_row += 1
                        self.cancelreason_disp[row_listindex].config(text=services['cancelReason'])
                        self.cancelreason_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=1,columnspan=4)
                    elif self.cancelreason_disp[row_listindex].grid_info() != {}:
                        # turn it off if no longer present
                        self.cancelreason_disp[row_listindex].grid_remove()
                    
                    #  No need for both cancel and delay reasons, only display
                    #  delayreason if there is no cancelreason
                    if services['cancelReason'] is None and services['delayReason'] is not None:
                        # if there is a delay reason then print it on the next row
                        display_row += 1
                        self.delayreason_disp[row_listindex].config(text=services['delayReason'])
                        self.delayreason_disp[row_listindex].grid(sticky=tk.W,row=display_row,column=1,columnspan=4)
                    elif self.delayreason_disp[row_listindex].grid_info() != {}:
                        # turn it off if no longer present
                        self.delayreason_disp[row_listindex].grid_remove()

                except KeyError as ke:
                    self.statusbar_text(f"Unknown data key {ke}")
               
                display_row += 1
                row_listindex += 1
                
            # Blank out any unused rows following
            global config
            service_numrows = int(config['display']['rows'])
            if row_listindex < service_numrows:
                for item in range(row_listindex, service_numrows):
                    # Check if current item is showing on the grid:
                    # if it is then grid_info will return a non-empty dict.
                    if len(self.time_disp[item].grid_info()):
                        list(map(tk.Label.grid_remove, [self.time_disp[item], self.dest_disp[item], \
                            self.plat_disp[item], self.expt_disp[item], self.cars_disp[item], \
                            self.cancelreason_disp[item], self.delayreason_disp[item]]))                                                       
#                         self.time_disp[item].grid_forget()
#                         self.dest_disp[item].grid_forget()
#                         self.plat_disp[item].grid_forget()
#                         self.expt_disp[item].grid_forget()
#                         self.cars_disp[item].grid_forget()
#                         self.cancelreason_disp[item].grid_forget()
#                         self.delayreason_disp[item].grid_forget()
                    else:
                        break
            
        # Display the status message
        self.statusbar.grid(sticky=tk.EW,row=display_row,column=0,columnspan=4)
        self.Esc_to_exit.grid(sticky=tk.EW,row=display_row,column=4)
        
        # print(f"Updated {Tm.today().strftime('%a %d %b %Y %H:%M:%S')}\n")

    def handle_keyevent(self, event):
        global Running
        # Quit if user pressed Esc
        if event.keycode == 9: #  keycode 9 is the Esc key
            Running = False
            # print("Stopping...")
            self.statusbar_text(DisplayApp.stop_msg)
    
    def handle_windowclose(self):
        global Running
        Running = False
        # print("Stopping...")
        self.statusbar_text(DisplayApp.stop_msg)
    
# end of DisplayApp class definition

# =========
# Main code
# =========

config = ConfigParser()

# Read config settings and check all present
try:
    with open('StationBoard.ini','r') as f:
        config.read_file(f)
        
    # Cannot proceed if any of these vital elements are missing
    if not (config.has_option('station','crs') \
            and config.has_option('SOAP','key')) \
            and config.has_option('SOAP','wsdl'):
        raise KeyError
        
except IOError as e:
    print('Config file DisplayBoard.ini not found or cannot be read')
    exit(e)
    
except KeyError:
    print("Key missing from config file")
    exit()

# Instantiate the web service interface
OpenLDBWS = OpenLDBWSApp()

# Instantiate the DisplayApp
# Use default values if any config values are not read  
display = DisplayApp(config['display']['bgcolour'] if config.has_option('display','bgcolour') else 'black', \
                     config['display']['headfgcolour'] if config.has_option('display','headfgcolour') else 'white', \
                     config['display']['itemfgcolour'] if config.has_option('display','itemfgcolour') else 'yellow')

Running = True

def update_display(display_messages = False):

    GSBRtodisplay = OpenLDBWS.getServiceInfo()
    
    # Display service messages only once on starting the program (when display_messages is True)
    if GSBRtodisplay != None and display_messages and GSBRtodisplay['nrccMessages'] != None:
        messagebox.showinfo("Service update",'\n\n'.join(dict['_value_1'] for dict in GSBRtodisplay['nrccMessages']['message']))

    display.display_info(GSBRtodisplay)
        
    if Running:
        # Update every 15 seconds
        # print(f"Updating at {time.ctime()}")
        display.mainwindow.after(15000,update_display)
    else:
        display.root.destroy()  # terminate Tkinter's mainloop
    
# Main loop

update_display(display_messages = True) # kick off repeating update_display before entering loop
display.update_time() # start the clock display

display.root.mainloop()

print ("Thank you for using Station Board.\nNow fuck off")