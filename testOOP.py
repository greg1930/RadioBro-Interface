from Tkinter import *
import ttk
import matplotlib.animation as anim
import threading
import time
import serial
import sys
import subprocess
import struct
from  __builtin__ import any as b_any
from random import randint
import datetime
import datetime as dt
import os
from pyorbital import orbital
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
LARGE_FONT= ("Verdana", 12)


class menu: #this class creates and displays the preferences menu
    def __init__(self,root): #here the default option menu values are defined, to be overwritten when the user changes the settings
        self.baudSelection = StringVar() #the variable which will be in the optionmenu for the radio settings
        self.paritySelection = StringVar()
        self.databitsSelection = StringVar()
        self.stopbitsSelection = StringVar()
        self.HFCSelection = StringVar()
        self.entry = StringVar()
        self.refreshSelection = StringVar()
        self.write = IntVar()
        self.baudSelection.set('115200') #set the default value for the optionmenu
        self.paritySelection.set('None')
        self.databitsSelection.set('8')
        self.stopbitsSelection.set('1')
        self.HFCSelection.set('False')
        self.entry.set('1')
        self.refreshSelection.set('Minutes')
        self.write.set('1')
        self.baud='115200'
        self.par=serial.PARITY_NONE #here the actual default values which correspond to the optionmenu default values are defined
        self.data=serial.EIGHTBITS
        self.stop=serial.STOPBITS_ONE
        self.HFC='False'
        self.duration = '60'
        
        menubar = Menu(root) #create the menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Preferences", command=self.preferences_window) #when preferences is selected, the preferences_window is called
        filemenu.add_command(label="Quit", command=self.quit)
        menubar.add_cascade(label="GSI", menu=filemenu)
        root.config(menu=menubar)

    def quit(self):
        os._exit(1)

    def preferences_window(self): #this method creates preferences widgets and labels, and allows the user to set new settings values 
        window = Toplevel(root) #creates a new smaller window on top of the existing one
        window.title("Preferences")
    
        close_button = Button(window, text="Close", command=lambda: self.close_window(window)) #call the close_window method when the button is pressed
        close_button.grid(row=28, column=0,columnspan=2)
        
        self.listbox = Listbox(window) #creates the listbox for port selection
        self.listbox['height'] = 10
        self.listbox['width'] = 30
        self.listbox.grid(row=1,rowspan=20, columnspan=5) #given a big row and column span to stop the listbox stretching columns
        self.listbox.bind('<<ListboxSelect>>',self.CurSelet) #listbox attached to teh self.CurSelet event handler
        port_list = subprocess.check_output([sys.executable, "list_ports.py"]) #runs the script that lists the ports as a subprocess and stores what it returns in a variable
        port_list = port_list.split() #breaks each port into a seperate lines
        for port in port_list: #loops through each port
            global port_selection
            self.listbox.insert(0, port) #adds each port to the listbox

        baudrateLabel = Label(window) #create the label that displays which setting this is
        baudrateLabel["text"] = "Baudrate"
        baudrateLabel.grid(row=21, column=0, sticky="W")
        baudOptions={'115200','57600','19200','14400','9600','4800'} #various options for the optionmenu
        baudDropdown = OptionMenu(window, self.baudSelection, *baudOptions, command=self.baud_selection) #create the optionmenu sending the chosen item to self.baud_selection
        baudDropdown.grid(row=21, column=1, sticky="W")

        parityLabel = Label(window)
        parityLabel["text"] = "Parity"
        parityLabel.grid(row=22, column=0, sticky="W")
        parityOptions={'None','Even','Odd','Mark','Space'}
        parityDropdown = OptionMenu(window, self.paritySelection, *parityOptions, command=self.parity_selection)
        parityDropdown.grid(row=22, column=1, sticky="W")

        databitsLabel = Label(window)
        databitsLabel["text"] = "Data Bits"
        databitsLabel.grid(row=23, column=0, sticky="W")
        databitsOptions={'5','6','7','8'}
        databitsDropdown = OptionMenu(window, self.databitsSelection, *databitsOptions, command=self.databits_selection)
        databitsDropdown.grid(row=23, column=1, sticky="W")

        stopbitsLabel = Label(window)
        stopbitsLabel["text"] = "Stop Bits"
        stopbitsLabel.grid(row=24, column=0, sticky="W") 
        stopbitsOptions={'1','1.5','2'}
        stopbitsDropdown = OptionMenu(window, self.stopbitsSelection, *stopbitsOptions, command=self.stopbits_selection)
        stopbitsDropdown.grid(row=24, column=1, sticky="W")

        HFCLabel = Label(window)
        HFCLabel["text"] = "Hardware Flow Control"
        HFCLabel.grid(row=25, column=0, sticky="W")
        HFCOptions={'True','False'}
        HFCDropdown = OptionMenu(window, self.HFCSelection, *HFCOptions, command=self.HFC_selection)
        HFCDropdown.grid(row=25, column=1, sticky="W")

        additionalFrame = Frame(window) #a frame is created inside the grid just to allow multiple widgets inside 1 gridbox
        additionalFrame.grid(row=26,column=1, sticky="nsew")
        refreshLabel = Label(window)
        refreshLabel["text"] = "Refresh Every"
        refreshLabel.grid(row=26, column=0, sticky="W")
        refreshEntry = Entry(additionalFrame, textvariable=self.entry,width=4) #the value entered into the entry box is stored in the self.entry StringVar()
        refreshEntry.grid(row=0,column=0)
        self.entry.trace("w",self.entryCallback)
        refreshOptions={'Seconds','Minutes','Hours'}
        refreshDropdown = OptionMenu(additionalFrame, self.refreshSelection, *refreshOptions, command=self.refreshSelect)
        refreshDropdown.grid(row=0, column=1)

        writeFrame = Frame(window)
        writeFrame.grid(row=27,column=1, sticky="nsew")
        writeLabel = Label(window, text="Write timestamps to file").grid(row=27, column=0, sticky="W")
        writeYes = Radiobutton(writeFrame, text="Yes", variable=self.write, value=1).grid(row=0,column=0)
        writeNo = Radiobutton(writeFrame, text="No", variable=self.write, value=2).grid(row=0,column=1)


    def entryCallback(self,*args):
        self.duration = self.entry.get()
        self.refreshSelect(self.refreshSelection.get())
        
    def close_window(self,window):
        window.withdraw() #closes the preferences window
        
    def CurSelet(self,evt): #event handler called when a user changes the selection in the listbox
        global port_selection
        port_selection = self.listbox.get(self.listbox.curselection()) #get what the user has selected and store it in port_selection

    def get_port_selection(self): #allows other classes to see which port has been selected
        return port_selection

    def set_port_selection(self,selection): #allows other classes to change which port has been selected
        port_selection = selection

    def baud_selection(self,selection):
        self.baudSelection.set(selection) #stores the users selection in the optionmenu StringVar() so when the preferences window is reopened the last choice will still be there
        self.baud=selection #sets the user selection to a variable that isn't a StringVar() for use in the rest of the system

    def get_baud_selection(self): #allows other parts of the system to see which baudrate value has been selected
        return self.baud

    def parity_selection(self,selection):
        self.paritySelection.set(selection)
        if selection=='None': #in this case if statements are required as the options in the optionmenu don't directly correspond with exactly what should be sent to the radio
            self.par=serial.PARITY_NONE
        elif selection=='Even':
            self.par=serial.PARITY_EVEN
        elif selection=='Odd':
            self.par=serial.PARITY_ODD
        elif selection=='Mark':
            self.par=serial.PARITY_MARK
        elif selection=='Space':
            self.par=serial.PARITY_SPACE

    def get_parity_selection(self):
        return self.par

    def databits_selection(self,selection):
        self.databitsSelection.set(selection)
        if selection=='5':
            self.data=serial.FIVEBITS
        elif selection=='6':
            self.data=serial.SIXBITS
        elif selection=='7':
            self.data=serial.SEVENBITS
        elif selection=='8':
            self.data=serial.EIGHTBITS

    def get_databits_selection(self):
        return self.data

    def stopbits_selection(self,selection):
        self.stopbitsSelection.set(selection)
        if selection=='1':
            self.stop=serial.STOPBITS_ONE
        elif selection=='1.5':
            self.stop=serial.STOPBITS_ONE_POINT_FIVE
        elif selection=='2':
            self.stop=serial.STOPBITS_TWO

    def get_stopbits_selection(self):
        return self.stop

    def HFC_selection(self,selection):
        self.HFCSelection.set(selection)
        self.HFC = selection

    def get_HFC_selection(self):
        return self.HFC

    def refreshSelect(self,selection):
        self.refreshSelection.set(selection)
        if self.duration != '':
            if selection=='Minutes':
                self.duration=int(self.duration)*60
            elif selection=='Hours':
                self.duration=int(self.duration)*60*60

    def getRefreshSelection(self):
        return self.duration

    def getWriteSelection(self):
        if self.write.get()==1:
            return True
        else:
            return False

    
class setup(Frame):
    
    def __init__(self,master,menuClass,stamps):
    
        self.menuClass = menuClass #this ensures the same instance of the menu class is used in this class
        self.showStamps = stamps #again, we want the same instance of showStamps to be used
        self.byte_value = 'None' #default user selection value
        self.stamplist=[] #list of created stamps which will be passed into show stamps
        self.mylist = [] #list contains the elements that the user has selected
        self.labellist = [] #list contains all the labels currently displayed on the grid
        self.deletebuttonlist = [] #list contains all the delete buttons currently displayed on the grid
        Frame.__init__(self, master)
        self.configure(height=600, width=800) #size of the setup frame
        self.grid_propagate(0) #force the size of the frame
        self.grid() #.grid() is used throughout the program as opposed to .pad()
        self.create_widgets() # calls the create_widgets method
 
    
    

    def add_whitespace(self, string, length): # function which returns a string with spaces in it when given the input string and after how many characters there should be a space, as parameters
        return ' '.join(string[i:i+length] for i in xrange(0,len(string),length))

 
    def create_widgets(self): #This method creates the widgets that are always displayed

        self.listbox = Listbox(self) #creates the listbox for port selection
        self.listbox['height'] = 10
        self.listbox['width'] = 30
        self.listbox.grid(row=1,rowspan=20, columnspan=5,sticky="W")
        self.listbox.bind('<<ListboxSelect>>',self.CurSelet)
        port_list = subprocess.check_output([sys.executable, "list_ports.py"]) #runs the script that lists the ports as a subprocess and stores what it returns in a variable
        port_list = port_list.split() #breaks each port into a seperate lines
        for port in port_list: #loops through each port
            global port_selection
            self.listbox.insert(0, port) #adds each port to the listbox
        self.send_button = Button(self) # creates the send hello world button
        self.send_button["text"] = "Send Hello World" #text on the button
        self.send_button["command"] = self.send_command # when clicked, the send_command method is called
        self.send_button.grid(sticky="W",row=21, column=0)

        self.add_button = Button(self, text = "Add", command = lambda: self.housekeeping_command(True, self.byte_value)) #when the button is clicked the radio will get the updated hex value and find the bits of it the user wants
        self.add_button.grid(sticky="W",row=22, column=1)

        self.refreshOnce_button=Button(self, text="Refresh Once", command=lambda: self.housekeeping_command(True, 'None')) #refreshes the hex packet and corresponding values, once
        self.refreshOnce_button.grid(row=22, column=3)
        
        self.refresh_button=Button(self, text="Begin Refresh", command=lambda: self.housekeeping_command(True, 'Refresh')) #calls the housekeeping method and tells it to begin refreshing, depending on the time entered in preferences
        self.refresh_button.grid(row=22, column=4)

        self.timestamps_button=Button(self, text="View Timestamps", command=lambda: self.showStamps.showWindow()) #when button pressed, calls the showWindow method inside showStamps passing in the stampList
        self.timestamps_button.grid(row=22, column=5)

        self.label1 = Label(self) #this label will display the hex value
        self.label1.grid(sticky="W", row=23, columnspan=10) # as it is long it has to have a columnspan so that it won't make the other grids unnecessarily big

        options = {'None','Temperature','Supply Voltage','MCU Voltage','Power Amplifier','Phase of Transmission Procedure','Phase of Receive Initialization','Phase of Receive Procedure','RSSI (dBm)','RSSI (Watts)', 'Carriage Return', 'Line Feed'} #the byte options in the drop down menu
        selection = StringVar() #Contains the value the user selects 
        selection.set('None') #default drop down menu value
        self.info_dropdown = OptionMenu(self, selection, *options, command=self.user_selection) #user selection is passed to the user_selection method
        self.info_dropdown.grid(row=22,column=0, sticky="ew")

        self.addall_button = Button(self, text="Add All", command = lambda: self.add_all(options)) #when pressed, calls the add_all method, passing in the list of available options(MCU, RSSI etc)
        self.addall_button.grid(sticky="W", row=22, column=2)

    def CurSelet(self,evt): #event handler called when a user changes the selection in the listbox
        global port_selection
        port_selection = self.listbox.get(self.listbox.curselection())
        self.menuClass.set_port_selection(port_selection)
    
    def user_selection(self,byte): 
        self.byte_value = byte #saves user selection to a variable
        self.housekeeping_command(False, byte) #calls the housekeeping method but passes in a False, as we don't want the selection to be processed until the button is pressed

    def add_all(self,options): #this method adds all possible byte options to the list of added items
        for items in options:
            if items!='None':
                self.mylist.append(items)
        self.housekeeping_command(True,None) #calls housekeeping method but passed in null as the byte value as we don't want to add any more bytes

    
    def refresh_command(self): #method removes the refresh button and callst the housekeeping method, asking it to start a refresh
        print(self.menuClass.getRefreshSelection())
        self.refresh_button.grid_forget()
        self.housekeeping_command(True, 'None')

    def cancel_refresh(self, thread, cancel_button):
        thread.cancel()
        cancel_button.grid_forget() #deletes the cancel button
        self.refresh_button.grid(row=22, column=4) #re-adds the refresh button
 
        
    def send_command(self): #creates a new instance of the radio class and sends helloworld to it
         sendHelloWorld = Radio()
         sendHelloWorld.send(":helloworld\r\n", port_selection, self.baudSelection, self.paritySelection, self.databitsSelection, self.stopbitsSelection, self.HFCSelection, True)
         self.label1["text"] = "SENT"

    def housekeeping_command(self,button_pressed, byte): #this method fetches the hex string and finds out the information that the user wants. button_pressed is there to avoid the method proceeding if it has been called just by an optionmenu selection
           
        if button_pressed==True: #only proceed if the housekeeping butto has been pressed
            radioCom=Radio() #creates a new instance of the Radio class
            sentCommand = radioCom.send("h\r\n", self.menuClass.get_port_selection(), self.menuClass.get_baud_selection(), self.menuClass.get_parity_selection(), self.menuClass.get_databits_selection(), self.menuClass.get_stopbits_selection(), self.menuClass.get_HFC_selection(), False) #sends the h command, passes in False as we don't want to close the connection
            time.sleep(1) #wait before reading to give the radio time
            hex_values = radioCom.read(sentCommand) #this line stores the hex values (in ASCII) received to hex_values
            hex_values = self.add_whitespace(hex_values,2)       #adds whitespace every 2 characters

            if len(hex_values)==50:  #little bit of error checking as we know what length the returned hex string should be
                self.label1["text"] = hex_values #displays hex values on the GUI
            else:
                self.label1["text"] = "Error fetching housekeeping packet"
            if byte=='Refresh':
                thread = threading.Timer(int(self.menuClass.getRefreshSelection()), self.refresh_command) #create a new thread to call self.refresh_command after the number of seconds defined in preferences. It will keep doing this indefinitely 
                thread.start() #start the thread
                cancel_button = Button(self, text="Cancel", command = lambda: self.cancel_refresh(thread,cancel_button)) #this button calls the method which will stop the thread. Therefore the thread is passed into it as a parameter
                cancel_button.grid(row=22,column=4)

            if byte=='Temperature' or self.in_list('Temperature'): #if the user has chosen to add temperature, or temperature has already been added and we just want to refresh it
                self.empty_elements('Temperature') #remove the old temperature data from the list
                Temp = hex_values[6:11] #parse the hex string to get the value we want
                Temp = Temp.replace(" ","") #delete the space between the two hex values
                Temp = int(Temp,16) #converts hex to decimal
                Temp = Temp/100
                Temp_C = Temp - 273.15
                self.mylist.append("Temperature - %s Kelvin (%s Celsius)" % (Temp, Temp_C)) #adds the finalised string to the list of added data
            
            if byte=='Supply Voltage' or self.in_list('Supply Voltage'):
                self.empty_elements('Supply Voltage')
                SV = hex_values[12:17]
                SV = SV.replace(" ","")
                SV = int(SV,16)
                self.mylist.append("Supply Voltage - %s mV" % (SV))

            if byte=='MCU Voltage' or self.in_list('MCU Voltage'):
                self.empty_elements('MCU Voltage')
                MCU = hex_values[18:23]
                MCU = MCU.replace(" ","")
                MCU = int(MCU,16)
                self.mylist.append("MCU Voltage - %s mV" % (MCU))

            if byte=='Power Amplifier' or self.in_list('Power Amplifier'):
                self.empty_elements('Power Amplifier')
                PA = hex_values[24:29]
                PA = PA.replace(" ","")
                PA = int(PA,16)
                self.mylist.append("Power Amplifier - %s mV" % (PA))

            if byte == 'Phase of Transmission Procedure' or self.in_list('Phase of Transmission Procedure'): #only proceed if it is the byte the user has just selected or has been previously selected
                self.empty_elements('Phase of Transmission Procedure') #every time the housekeeping button is pressed we refresh the values so empty the list of bytes first
                PTP = hex_values[33:35] #parses the hex string to get the required hex value. In this case it is byte 11
                if PTP=='00':
                    self.mylist.append("Phase of Transmission Procedure - Stand by") #if this is the correct result, add it to the list
                if PTP=='01':
                    self.mylist.append("Phase of Transmission Procedure - Radio being configured, begin key-up")
                if PTP=='02':
                    self.mylist.append("Phase of Transmission Procedure - Preparing data")
                if PTP=='03':
                    self.mylist.append("Phase of Transmission Procedure - Data is ready to be sent")
                if PTP=='04':
                    self.mylist.append("Phase of Transmission Procedure - Sending data")
                if PTP=='05':
                    self.mylist.append("Phase of Transmission Procedure - Clearing old packet from buffer")
                PTP = int(PTP, 16) #convert to decimal to check if greater than 0xCA (200)
                if PTP>=200:
                    self.mylist.append("Phase of Transmission Procedure - Data whitening is active")

            if byte=='Phase of Receive Initialization' or self.in_list('Phase of Receive Initialization'):
                self.empty_elements('Phase of Receive Initialization')
                PRI = hex_values[36:38]
                if PRI=='00':
                    self.mylist.append("Phase of Receive Initialization - Default set to RX disabled")
                if PRI=='01':
                    self.mylist.append("Phase of Receive Initialization - Default set to RX enabled")
                    
            if byte=='Phase of Receive Procedure' or self.in_list('Phase of Receive Procedure'):
                self.empty_elements('Phase of Receive Procedure')
                PRP = hex_values[39:41]
                if PRP=='00':
                    self.mylist.append("Phase of Receive Procedure - Off")
                if PRP=='01':
                    self.mylist.append("Phase of Receive Procedure - No data clocking yet")
                if PRP=='02':
                    self.mylist.append("Phase of Receive Procedure - On and waiting for preamble")
                if PRP=='03':
                    self.mylist.append("Phase Receive Procedure - On, preamble discovered, waiting on sync word")
                if PRP=='04':
                    self.mylist.append("Phase of Receive Procedure - Data being collected, waiting on end flag")
                if PRP=='05':
                    self.mylist.append("Phase of Receive Procedure - Processing Data")
            
            
            if byte == 'RSSI (dBm)' or self.in_list('dBm'):
                self.empty_elements('dBm')
                RSSI_value = hex_values[42:44]
                RSSI_value = bin(int(RSSI_value, 16))[2:].zfill(8) #as it is signed we need to convert to binary first
                RSSI_value = self.twos_comp(int(RSSI_value,2), len(RSSI_value)) #then convert signed binary to int
                self.mylist.append("RSSI value is %s dBm" % (RSSI_value))
            

            if byte=='RSSI (Watts)' or self.in_list('Watts'):
                self.empty_elements('Watts')
                RSSI_value_power = hex_values[42:44]
                RSSI_value_power = bin(int(RSSI_value_power, 16))[2:].zfill(8)
                RSSI_value_power = self.twos_comp(int(RSSI_value_power,2), len(RSSI_value_power))
                RSSI_value_power = 10**((RSSI_value_power-30)/10) #we need to do a final calculation this time
                self.mylist.append("RSSI value is %s Watts" % (RSSI_value_power))

            if byte=='Carriage Return' or self.in_list('Carriage Return'):
                self.empty_elements('Carriage Return')
                CR = hex_values[45:47]
                if CR=='0d':
                    self.mylist.append("Carriage Return - True")
                else:
                    self.mylist.append("Carriage Return - False")

            if byte=='Line Feed' or self.in_list('Line Feed'):
                self.empty_elements('Line Feed')
                LF = hex_values[48:50]
                if LF=='0a':
                    self.mylist.append("Line Feed - True")
                else:
                    self.mylist.append("Line Feed - False")

            
            for item in self.mylist: #create a stamp for each item in the list of added data
                stamp = self.create_stamp(hex_values,item)
                self.showStamps.addToList(stamp)


            self.refresh_list() #call the refresh_list method
            

    def create_stamp(self, hex_values,item): 
        date_time = ' Radio Data collected at {:%H:%M:%S on %d-%m-%Y}'.format(datetime.datetime.now()) #defines what teh data and time should look like
        stamp = createStamp(date_time, hex_values, item) #creates a stamp object
        return stamp #returns the stamp object
                
    def print_list(self):
        for i,selections in enumerate(self.mylist, start=24): #loop through the list of selected bytes, need an iterator to use as the row value
            self.label = Label(self)
            self.label["text"] = selections #create new label for each item in the list of bytes
            self.label.grid(row = i, columnspan=6, column=0, sticky="W")
            self.labellist.append(self.label) #add this new label to the list of labels
            self.delete_button = Button(self,text="Delete", command=lambda j=selections : self.delete_element(j)) #create new delete button for each item in the list of bytes. When the button is pressed delete_element is called
            self.delete_button.grid(row = i, column=5, sticky="W")
            self.deletebuttonlist.append(self.delete_button) #add this new button to the list of buttons
            
        

    def delete_element(self,element):
        self.mylist.remove(element) #remove the element from the list
        self.refresh_list() #refresh the list again

    def in_list(self, string): #checks to see if a particular byte has already been selected by the user so we know if it should be added when the list is refreshed or not
        if b_any(string in x for x in self.mylist):
            return True
        else:
            return False
        

    def refresh_list(self): #clears everything
        for selections in self.labellist:
            selections.destroy() #destroy every label previously created
        for selections in self.deletebuttonlist:
            selections.destroy() #destroy every button previously created
        self.print_list() #call the method that creates new labels and buttons

    def empty_elements(self,string): #This method matches a string with a smaller substring. Eg. 'dBm' finds 'RSSI (dBm)'
        keywordFilter = set([string])
        self.mylist = [str for str in self.mylist if not any(i in str for i in keywordFilter)] #new list doesn't contain any strings that contain the keyword
    
    def twos_comp(self,val, bits): #twos complement conversion
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val # return positive value as is


class temperature(Frame): #class to display the temperature telemetry

    def __init__(self,temperatureFrame,packet):
        Frame.__init__(self,temperatureFrame)
        self.temperatureArray = []
        self.data = packet
        self.packet = 0
        self.configure(height=600, width=800)
        self.grid_propagate(0) 
 #       self.draw_graph() #calls the draw graph method
        self.label1= Label(self)
        self.label1.grid()
        self.createGraph()
 #       self.fetchPacket()
        self.grid()
        

    def fetchPacket(self):
        self.packet = self.data.getPacket()
        self.label1["text"] = self.packet
        self.temperatureArray.append(int(self.packet[0:2],16))
     

    def startTimer(self,f,a,canvas):   
        thread = threading.Timer(10,self.updateGraph,args=(f,a,canvas))
        thread.start()
    
    def draw_graph(self):
        c_width = 300
        c_height = 350
        c = Canvas(self, width=c_width, height=c_height, bg= 'white')
        c.grid()
        y_stretch = 5
        y_gap=20
        x_stretch=20
        x_width=50
        x_gap=20
        for x, y in enumerate(self.generateData()):
            x0 = x * x_stretch + x * x_width + x_gap
            y0 = c_height - (y * y_stretch + y_gap)
            x1 = x * x_stretch + x * x_width + x_width + x_gap
            y1 = c_height - y_gap
            c.create_rectangle(x0, y0, x1, y1, fill="red")
            c.create_text(x0+2, y0, anchor="sw", text=str(y))
        label1 = Label(self, text = "Real-time Temperature", font=("Helvetica", 16)) #this label will display the hex value
        label1.grid()

    def createGraph(self):
        f = Figure(figsize=(7,10), dpi=50)
        a = f.add_subplot(111)
        xArray = []
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid()
        self.updateGraph(f,a,canvas)
    
    def updateGraph(self,f,a,canvas):
        
        self.fetchPacket()
        xArray = []
        for i,item in enumerate(self.temperatureArray):
            i+=1
            xArray.append(i)
        for item in xArray:
            print(item)
        for item in self.temperatureArray:
            print(item)
        a.clear()
        a.plot(xArray,self.temperatureArray)
        canvas.get_tk_widget().grid_forget()
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid()
        self.startTimer(f,a,canvas)


class createStamp(object): #this class is used to create a stamp object
    def __init__(self,date_time,hex_values,item):
        self.date_time = date_time
        self.hex_values = hex_values
        self.item = item

    @property
    def get_date_time(self): #getter for date_time
        return self.date_time

    @property
    def get_hex_values(self):
        return self.hex_values
    
    @property
    def get_data(self): #getter for data
        return self.item

class showStamps:
    def __init__(self,root,menuClass):
        self.root=root
        self.writeInsertedTimeList = [] #stores the time value of the timestamp to ensure no duplicates
        self.stampList = [] #list of all timestamps
        self.menuClass = menuClass

    
    def addToList(self,stamp):
        self.stampList.append(stamp) #add new timestamp to the list of all timestamps
        if self.menuClass.getWriteSelection() == True:
            self.writeFile() #write timestamp to file if selected in preferences
    
    def showWindow(self):
        
        window = Toplevel(self.root) #creates small window on top of existing window
        window.title("Timestamps")

        self.canvas = Canvas(window, borderwidth=0, background="#ffffff", width=400, height=400) #creates a canvas on the new window
        self.frame = Frame(self.canvas, background="#ffffff") #adds a frame to the canvas
        self.vsb = Scrollbar(window, orient="vertical", command=self.canvas.yview) #adds a scrollbar
        self.canvas.configure(yscrollcommand=self.vsb.set) #configures the scrollbar on the canvas

        self.vsb.pack(side="right", fill="y") 
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure) #method called when the user scrolls
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) #method called when the user uses a mousewheel
        
        insertedTimeList=[] #list stores timestamps that have been inserted so time printouts aren't duplicated
        for i,item in enumerate(self.stampList): #for each stamp in the stamplist
          if item.get_date_time not in insertedTimeList: #only want to print date, time, linebreak and hex values if the time hasn't already been accessed
              if i!=0: #insert a blank line before the date, as long as it isn't the first date
                  blankLabel=Label(self.frame,text=" ")
                  blankLabel.grid()
              timeLabel=Label(self.frame)
              timeLabel["text"] = item.get_date_time
              timeLabel.grid(sticky="W")
              hexLabel=Label(self.frame)
              hexLabel["text"] = "    %s"%(item.get_hex_values)
              hexLabel.grid(sticky="W")
              insertedTimeList.append(item.get_date_time) #add to list to ensure time is not duplicated
              #POSSIBLE BUG - TELEMETRY AND RADIO TIMES COULD MATCH!!!

          if item.get_data!=None: #There will only be data if radio telemetry, not satellite telemetry
              dataLabel=Label(self.frame, text="    %s"%(item.get_data))
              dataLabel.grid(sticky="W")

      

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) #Reset the scroll region to encompass the inner frame'

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta), "units") #adds mousewheel functionality. For windows do: event.delta/120
        
    def writeFile(self):
        with open('timestamps.txt', 'a') as file: #append to timestamps.txt
            my_path = "/Users/gregstewart96/Desktop/timestamps.txt"
            for item in self.stampList  : #for each stamp in the stamplist
                if item.get_date_time not in open('timestamps.txt').read(): #check the timestamp hasn't already been added
                    if item.get_date_time not in self.writeInsertedTimeList: #only want to print date, time, linebreak and hex values if the time hasn't already been accessed
                        if os.path.getsize(my_path)>0: #insert a blank line before the date, as long as the file isn't empty
                            file.write("\n")
                        file.write("%s\n"%(item.get_date_time))
                        file.write("   %s\n"%(item.get_hex_values))
                        self.writeInsertedTimeList.append(item.get_date_time)
                    file.write("   %s\n"%(item.get_data))
        
    
class Radio:
    def send(self,command, port, baud, parity, databits, stopbits, dfc, closeConnection): #enter command to be sent, radio details and whether you want the connection to be closed after being sent
        ser = serial.Serial(port=port, baudrate=baud, parity=parity, bytesize=databits, stopbits=stopbits, rtscts=dfc)
        print(ser.isOpen())
        ser.write(command) #the command that is sent
        time.sleep(0.5) #small sleep timer to allow the command to be sent before the connection is closed
        if closeConnection==True:
            ser.close() #close the connection if we want to
        return ser

    def read(self, ser):
        hex_values = ser.readline() #reads from the radio
        hex_values = hex_values.encode('hex') #converts ASCII to hex
        return hex_values

class satelliteData(Frame):
    def __init__(self,satelliteDataFrame):
        Frame.__init__(self,satelliteDataFrame)
        self.configure(height=600, width=800)
        self.grid_propagate(0)
        self.fetchData()
        self.grid()
        
    def fetchData(self):
##        https://www.space-track.org/basicspacedata/query/class/satcat/COUNTRY/United%20States/orderby/APOGEE%20asc/limit/10/format/csv/metadata/false
##        https://www.space-track.org/basicspacedata/query/class/tle_latest/orderby/OBJECT_NAME%20asc/limit/10/format/html/metadata/false
##        https://www.space-track.org/basicspacedata/query/class/tle_latest/orderby/EPOCH%20asc/limit/10/metadata/false
        var = 1
        sat = "noaa 18"
        orb = orbital.Orbital(sat)

        labelSatellite = Label(self)
        labelSatellite["text"] = "Satellite"
        labelSatellite.grid()
        satellite = Label(self)
        satellite.grid()

        labelTime = Label(self)
        labelTime["text"] = "Time"
        labelTime.grid()
        timeData = Label(self)
        timeData.grid()

        label1 = Label(self)
        label1["text"] = "Position"
        label1.grid()
        positionLabel = Label(self)
        positionLabel.grid()

        label2 = Label(self)
        label2["text"] = "Longitude"
        label2.grid()
        longitude = Label(self)
        longitude.grid()

        label3 = Label(self)
        label3["text"] = "Latitude"
        label3.grid()
        latitude = Label(self)
        latitude.grid()

        label4 = Label(self)
        label4["text"] = "Altitude"
        label4.grid()
        altitude = Label(self)
        altitude.grid()

        label5 = Label(self)
        label5["text"] = "Azimuth and Elevation"
        label5.grid()
        aziEle = Label(self)
        aziEle.grid()

class Telemetry(Frame):
    def __init__(self,root,stamps):
        self.data = 0
        self.data_str = 0
        self.showStamps = stamps
        self.createPacket()
        
    def createPacket(self):
        self.data = [hex(randint(0,255))[2:], hex(randint(0,255))[2:], hex(randint(0,255))[2:], hex(randint(0,255))[2:]]
        self.data_str="".join(self.data)
        stamp = self.create_stamp(self.data_str)
        self.showStamps.addToList(stamp)
        self.startTimer()

    def startTimer(self):
        thread = threading.Timer(10,self.createPacket)
        thread.start()

    def getPacket(self):
        return self.data_str
    def getPacketArray(self):
        return self.data

    def create_stamp(self, hex_values): 
        date_time = ' Telemetry collected at {:%H:%M:%S on %d-%m-%Y}'.format(dt.datetime.now()) #defines what teh data and time should look like
        stamp = createStamp(date_time, hex_values, None) #creates a stamp object
        return stamp #returns the stamp object
        

##        thread = threading.Timer(10)
##
##        while var==1:
##        
##            now = datetime.utcnow()
##            lon = orb.get_lon(now)
##            lat = orb.get_lat(now)
##            alt = orb.get_alt(now)
##
##            
##            satellite["text"] = sat
## 
##            
##            
##            timeData["text"] = now
##            
##            
##            
##            positionLabel["text"] = orb.get_position(now)
##            
##
##            
##            longitude["text"] = lon
##            
##
##            
##            latitude["text"] = lat
##            
##
##            
##            altitude["text"] = alt
##            
##
##            
##            aziEle["text"] = orb.get_observer_look(now, lon, lat, alt)
##            
##
##           
##        
##    
##            for num in range(10,1):
##                timeLabel["text"] = "Next update in %d seconds" % (num)
##                timeLabel.grid()
##                time.sleep(1)
        




        
root = Tk()
root.title("Ground Station Interface") #title of the window


notebook = ttk.Notebook(root,height=600,width=800) #notebook allows multiple frame to be placed on the notebook. Place the notebook on root

setupFrame = ttk.Frame(notebook) #create new frame for the radio information

temperatureFrame = ttk.Frame(notebook) #frame for the temperature telemetry
satelliteDataFrame = ttk.Frame(notebook)
notebook.add(setupFrame,text='Setup') #add the frame to the notebook
notebook.add(temperatureFrame, text='Temperature')
notebook.add(satelliteDataFrame, text="Satellite Data")
s=ttk.Style()
s.theme_use('alt') #set the theme of the notebook

notebook.grid()


menuClass = menu(root) #create instance of menu class. Pass in root to allow the class to add things to it
stamps = showStamps(root,menuClass) #creates instance of showStamps. This is created now as we want to use the same instance throughout the entire system
packet = Telemetry(root,stamps)
app = setup(setupFrame,menuClass,stamps) #call the setup class. Pass in the setupFrame so we can add to it, menu class instance so we can access the settings and our showStamps instance
app = temperature(temperatureFrame,packet) #call the temperature class passing in the temperature frame
app = satelliteData(satelliteDataFrame)

root.mainloop()
