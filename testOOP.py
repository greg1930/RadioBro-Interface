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

        self.label2 = Label(self) #this label will display the hex value
        self.label2.grid(row=4, columnspan=3) # as it is long it has to have a columnspan so that it won't make the other grids unnecessarily big

 #       self.entry = Entry(self) #byte text entry
 #       self.entry.grid(sticky="W", row=2, column=0)

        options = {'None','RSSI', 'option2'}
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

            if byte=='RSSI':
                RSSI_value = hex_values[39:41]
                RSSI_value = bin(int('ca', 16))[2:].zfill(8)
                RSSI_value = self.twos_comp(int(RSSI_value,2), len(RSSI_value))
                RSSI_value = 10**((RSSI_value-30)/10)
                self.label2["text"] = RSSI_value 

     
 #       byte_entry = self.entry.get()
         #byte_entry*3 - split
    
    def twos_comp(self,val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is

root = Tk()
root.title("test") #title of the window
root.geometry("450x350") #size of the window

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
