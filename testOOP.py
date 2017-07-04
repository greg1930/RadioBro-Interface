from Tkinter import *
import time
import serial
import sys
import subprocess
import struct


class Application(Frame):

    def __init__(self,master):
        self.byte_value = 'None'
        self.value_selected = 0
        self.mylist = []
        self.labellist = []
        self.deletebuttonlist = []
        self.addedbytelist = []
        Frame.__init__(self, master)
        self.grid() #.grid() is used throughout the program as opposed to .pad()
        self.create_widgets() # calls the create_widgets method

    def add_whitespace(self, string, length): # function which returns a string with spaces in it when given the input string and after how many characters there should be a space, as parameters
        return ' '.join(string[i:i+length] for i in xrange(0,len(string),length))

 
    def create_widgets(self):

        self.send_button = Button(self) # creates the send hello world button
        self.send_button["text"] = "Send Hello World"
        self.send_button["command"] = self.send_command # when clicked, the send_command method is called
        self.send_button.grid()

        self.housekeeping_button = Button(self, text = "Housekeeping Packet", command = lambda: self.housekeeping_command(True, self.byte_value))
        self.housekeeping_button.grid(row=2, column=1)

        self.label1 = Label(self) #this label will display the hex value
        self.label1.grid(sticky="W", columnspan=3) # as it is long it has to have a columnspan so that it won't make the other grids unnecessarily big

  

 #       self.entry = Entry(self) #byte text entry
 #       self.entry.grid(sticky="W", row=2, column=0)

        options = {'None','Phase of Transmission Procedure','Phase of Receive Initialization','Phase of Receive Procedure','RSSI (dBm)','RSSI (Watts)', 'Carriage Return', 'Line Feed'}
        selection = StringVar()
        selection.set('None')
        self.info_dropdown = OptionMenu(self, selection, *options, command=self.func)
        self.info_dropdown.grid(row=2, sticky="W")

    def func(self,byte):
        self.byte_value = byte
        self.housekeeping_command(False, byte)
        
        
    def send_command(self):
         self.label1["text"] = "SENT"
         ser = serial.Serial(port=port_selection, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False) #opens the connection. port is set to value as value holds the listbox port selection 
         print(ser.isOpen())
         ser.write(":helloworld\r\n") #the command that is sent
         time.sleep(0.5) #small sleep timer to allow the command to be sent before the connection is closed
         ser.close() # close the connection

    def housekeeping_command(self,button_pressed, byte):
        if button_pressed==True:
            ser = serial.Serial(port=port_selection, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False)
            print(ser.isOpen())
            ser.write("h\r\n")
            time.sleep(1)
            hex_values = ser.readline() #this line stores the hex values (in ASCII) received to hex_values
            hex_values = hex_values.encode('hex') #converts ASCII to hex
            hex_values = self.add_whitespace(hex_values,2)       #adds whitespace every 2 characters
            self.label1["text"] = hex_values #displays hex values on the GUI
            ser.close()

            if byte == 'Phase of Transmission Procedure' or 'Phase of Transmission Procedure' in self.addedbytelist:
                if 'Phase of Transmission Procedure' not in self.addedbytelist:
                    self.addedbytelist.append('Phase of Transmission Procedure')
                self.empty_elements('Phase of Transmission Procedure')
                PTP = hex_values[33:35]
                if PTP=='00':
                    self.mylist.append("Phase of Transmission Procedure - Stand by")
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
                PTP = int(PTP, 16)
                if PTP>=200:
                    self.mylist.append("Phase of Transmission Procedure - Data whitening is active")

            if byte=='Phase of Receive Initialization' or 'Phase of Receive Initialization' in self.addedbytelist:
                if 'Phase of Receive Initialization' not in self.addedbytelist:
                    self.addedbytelist.append('Phase of Receive Initialization')
                self.empty_elements('Phase of Receive Initialization')
                PRI = hex_values[36:38]
                if PRI=='00':
                    self.mylist.append("Phase of Receive Initialization - Default set to RX disabled")
                if PRI=='01':
                    self.mylist.append("Phase of Receive Initialization - Default set to RX enabled")
                    
            if byte=='Phase of Receive Procedure' or 'Phase of Receive Procedure' in self.addedbytelist:
                if 'Phase of Receive Procedure' not in self.addedbytelist:
                    self.addedbytelist.append('Phase of Receive Procedure')
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
            
            
            if 'RSSI (dBm)' in self.addedbytelist or byte == 'RSSI (dBm)':
                if 'RSSI (dBm)' not in self.addedbytelist:
                    self.addedbytelist.append('RSSI (dBm)')
                self.empty_elements('dBm')
                RSSI_value = hex_values[21:24]
                RSSI_value = bin(int(RSSI_value, 16))[2:].zfill(8)
                RSSI_value = self.twos_comp(int(RSSI_value,2), len(RSSI_value))
                self.mylist.append("RSSI value is %s dBm" % (RSSI_value))
            

            if byte=='RSSI (Watts)' or 'RSSI (Watts)' in self.addedbytelist:
                if 'RSSI (Watts)' not in self.addedbytelist:
                    self.addedbytelist.append('RSSI (Watts)')
                self.empty_elements('Watts')
                RSSI_value_power = hex_values[21:24]
                RSSI_value_power = bin(int(RSSI_value_power, 16))[2:].zfill(8)
                RSSI_value_power = self.twos_comp(int(RSSI_value_power,2), len(RSSI_value_power))
                RSSI_value_power = 10**((RSSI_value_power-30)/10)
                self.mylist.append("RSSI value is %s Watts" % (RSSI_value_power))

            if byte=='Carriage Return' or 'Carriage Return' in self.addedbytelist:
                if 'Carriage Return' not in self.addedbytelist:
                    self.addedbytelist.append('Carriage Return')
                self.empty_elements('Carriage Return')
                CR = hex_values[45:47]
                if CR=='0D':
                    self.mylist.append("Carriage Return - True")
                else:
                    self.mylist.append("Carriage Return - False")

            if byte=='Line Feed' or 'Line Feed' in self.addedbytelist:
                if 'Line Feed' not in self.addedbytelist:
                    self.addedbytelist.append('Line Feed')
                self.empty_elements('Line Feed')
                LF = hex_values[48:50]
                if LF=='0A':
                    self.mylist.append("Line Feed - True")
                else:
                    self.mylist.append("Line Feed - False")

            self.refresh_list()
            
            
    def print_list(self):
       
        for i,selections in enumerate(self.mylist, start=4):
            
            self.label = Label(self)
            self.label["text"] = selections
            self.label.grid(row = i, columnspan=3, column=0, sticky="W")
            self.labellist.append(self.label)
            self.delete_button = Button(self,text="Delete", command=lambda : self.delete_element(selections))
            self.delete_button.grid(row = i, column=3, sticky="E")
            self.deletebuttonlist.append(self.delete_button)
            

                  
                
            
 #       byte_entry = self.entry.get()
         #byte_entry*3 - split

    def delete_element(self,element):
        print(element)
        self.mylist.remove(element)
        self.refresh_list()

    def refresh_list(self):
        for selections in self.labellist:
            self.label.destroy()
        for selections in self.deletebuttonlist:
            self.delete_button.destroy()
        self.print_list()

    def empty_elements(self,string):
        keywordFilter = set([string])
        self.mylist = [str for str in self.mylist if not any(i in str for i in keywordFilter)]
    
    def twos_comp(self,val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is

root = Tk()
root.title("test") #title of the window
root.geometry("560x350") #size of the window

listbox = Listbox(root) #creates the listbox for port selection
listbox['height'] = 10
listbox['width'] = 30

port_selection = None #defining this here, allows what is found in the following event handler to be used in the rest of the program
def CurSelet(evt): #event handler called when a user changes the selection in the listbox
    global port_selection
    port_selection = listbox.get(listbox.curselection())
    
     
listbox.bind('<<ListboxSelect>>',CurSelet) #defines the event handler
listbox.grid(sticky="W", columnspan=4)


port_list = subprocess.check_output([sys.executable, "list_ports.py"]) #runs the script that lists the ports as a subprocess and stores what it returns in a variable
port_list = port_list.split() #breaks each port into a seperate lines
for port in port_list: #loops through each port
    listbox.insert(0, port) #adds each port to the listbox

app = Application(root)

root.mainloop()
