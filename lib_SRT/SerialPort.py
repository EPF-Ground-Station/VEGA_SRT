
"""Module containing the private class SerialPort, used by SRT to communicate with APM."""


import serial


class SerialPort:

    """Class aimed at monitoring the interaction with the APM serial port using the serial module"""

    def __init__(self, address, baud, timeo=None):
        """
        :param address: address of the serial port (port on the linux machine)
        :param baud: rate of data exchange
        :param timeo: timeout of the communication. Default to None
        """
        self.ser = serial.Serial(address, baud, timeout=timeo)
        self.connected = False

    def connect(self):
        """
        Connects to the serial port. TODO: implement security check if an error occurs here
        """
        self.ser.open()
        self.connected = True

    def disconnect(self):
        """
        Disconnects the serial port.
        """
        self.connected = False
        self.ser.close()

    def listen(self):
        """Reads last message from SerialPort with appropriate processing. Messages sent by the APM have format:

        {Status}|{Feedback}

        where status can either be OK, Warning or Error. Feedback is the actual return value of the APM : either message
        if status is Warning or Error, or a string containing a value if the status is Success.

        Example message : "Success | 33.85" , answer to command "getAz". The numeric value is thus the current Azimuth
        angle value assumed by the APM Az encoder.

        See APM_embedded_teensy/APM_embedded_teensy_2.ino for more

        :return: Message sent by the APM
        :rtype: str
        """

        status, feedback = self.ser.readline().decode('utf-8').split(" | ")

        if ("Err" in status) or ("Warn" in status):
            print(status + " : " + feedback)
            feedback = feedback.split("APM returned ")[-1]

        return feedback.strip()

    def send_Ser(self, msg: str):
        """Sends message through the serial port to the APM. Returns answer from SerialPort, following the synchronous
        philosophy : one command = one feedback. TODO: Make encoders asynchronous to allow multiple commands, command breaks etc (long term)

        :param msg: Command to send to APM
        :type msg: str
        :return: Feedback from APM after command execution
        :rtype: str
        """

        if self.connected:

            self.ser.reset_input_buffer()  # Discards remaining data in buffer
            self.ser.write((msg).encode())  # Sends message to serial

            answer = self.listen()

            return answer

        else:
            return ""
