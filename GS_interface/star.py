import serial
from serial.tools import list_ports

coor= "Hello"

def send_coord(coord):
        """
        Sends the TLE of the satelite selected to the Teensy which triggers the telescope to follow the specific satelite
        This code will only function if exactly one teensy is connected to the computer and thus available_ports contains one element.
        A serial port is characterized by the fact that one bit is sent at a time and the bits are sent in serie, which is how microprocessors work. 
        list_ports.comports lists all available ports of the computer
        
        :param available_ports : contains all the serial ports of the computer
        """
        available_ports = []

        DEBUG = True

        for port, desc_port, id in list_ports.comports():
            print(port)
            print(desc_port)
            if desc_port.find("Serial") > 0:
                print("port available")
                available_ports.append(port)

        if DEBUG:
            print(coord)
        
        if True:
            print("available_ports true")
            ser = serial.Serial("/dev/ttyACM0", 115200)
            ser.write(coord.encode())
            print("wrote")

        print(ser.readline().decode('utf-8'))
        print("read line")

if __name__ == "__main__":
    send_coord(coor)
    print("a")
