from tkinter import *
from tkinter.ttk import *
from satellite import get_sat_list, get_name_list
import serial
from serial.tools import list_ports

DEBUG = 0

class SRTApp(Tk):
    """Generates a GUI(General user interface) containing a list with all active satelites
    and their TLE. With the help of a search bar and per mouse click a specific satelite can be selected 
    which sends the corresponing TLE to the Teensy device. This triggers that the SRT starts to follow the 
    chosen satelite.
    
    """
    # constructor 
    def __init__(self):
        super(SRTApp, self).__init__()
        self.title("Small Radio Telescope control app")
        window_width = 700
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.sat_list = get_sat_list()  
        self.names_list = get_name_list(self.sat_list)
        self.label_text = StringVar(self, "Choose a satellite to track")

        self._create_widgets()


    def _create_widgets(self):
        """
        Creates and displays the different elements inside the GUI window. 

        :param self.entry : the search bar 
        :param self.tle_list : the list of all selected satelites
        :param self.fixed_title : the title shown in the box on the right "You are tracking"
        :params self.tle_box : the box below the title which shows the TLE

        """
        self.entry = Entry(self)
        self.entry.grid(row=0, column=0)
        self.entry.bind('<KeyRelease>', self._scankey)

        self.tle_list = Listbox(self)
        self.tle_list.grid(row=1, column=0)
        self.tle_list.bind("<<ListboxSelect>>", self._on_select)
        self._update_label(self.names_list)

        self.fixed_title = Label(self, text="You are tracking :")
        self.fixed_title.grid(row=0, column=1)

        self.tle_box = Label(self, textvariable=self.label_text)
        self.tle_box.grid(row=1, column=1)

    
    def _scankey(self, event):
        """
        Search function to filter the satelite list. When a key is tapped inside the bar 
        above the list, only the satelites containing the corresponding key remain. 
        Is executed each time a letter is tapped. 

        :param val : value of the key that triggers the event
        :param event : event which is happening, for example tapping a letter 

        """
        val = event.widget.get() #widget stands for the element in the GUI the event is acting on
        print(val)

        if val == '':
            data = self.names_list
        else:
            data = []
            for name in self.names_list:
                if val.lower() in name.lower():
                    data.append(name)

        self._update_label(data)

    # update the list in the box below the search bar when something is typed inside the search bar 
    def _update_label(self, data):
        self.tle_list.delete(0, 'end')

        # put new data
        for item in data:
            self.tle_list.insert('end', item)

    def _on_select(self, event):
        """
        Updates the box in the GUI on the right once a satelite is clicked on in the list 

        :param name: the name of the satelite selected
        :type name: string
        :param index : the index of the satelite in the original, complete list
        :type index: int
        :param check : control to check if the TLE was sent successfully to the teensy (if sent_tle has worked well)
        :type check: boolean

        """
        name = self.tle_list.get(ANCHOR)
        index = self.names_list.index(name)
        check = self._send_tle(self.sat_list[index].TLE)
        if check:
            self.label_text.set(self.sat_list[index].TLE)
        else:
            self.label_text.set("You don't have the Teensy connected !!!" + "\n\n" + self.sat_list[index].TLE)

 
    def _send_tle(self, tle):
        """
        Sends the TLE of the satelite selected to the Teensy which triggers the telescope to follow the specific satelite
        This code will only function if exactly one teensy is connected to the computer and thus available_ports contains one element.
        A serial port is characterized by the fact that one bit is sent at a time and the bits are sent in serie, which is how microprocessors work. 
        list_ports.comports lists all available ports of the computer
        
        :param available_ports : contains all the serial ports of the computer
        """
        available_ports = []

        for port, desc_port, id in list_ports.comports():
            if desc_port.find("Serial") > 0:
                available_ports.append(port)

        if DEBUG:
            print(tle)
        else:
            if available_ports:
                ser = serial.Serial(available_ports[0])
                ser.write(tle.encode())
                return 1
            else:
                return 0


if __name__ == "__main__":
    app = SRTApp()
    app.mainloop() # continuous refreshement
