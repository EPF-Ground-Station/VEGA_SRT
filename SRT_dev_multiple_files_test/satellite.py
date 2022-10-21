from urllib.request import urlopen
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class Satellite:
    def __init__(self, tle=""):
        self.TLE = tle

    def get_name(self):
        tle_split = self.TLE.splitlines()
        return tle_split[0]

def get_sat_list():
    with urlopen("https://celestrak.com/NORAD/elements/gp.php?GROUP=active&FORMAT=tle") as f:
        tle_read = f.read().decode()

    tle_lines = tle_read.splitlines(True)

    sat_list = []
    current_sat = Satellite()
    for i, current_line in enumerate(tle_lines):
        current_sat.TLE += current_line
        if i % 3 == 2:
            sat_list.append(current_sat)
            current_sat = Satellite()

    return sat_list

def get_name_list(sat_list):
    names_list = []
    for sat in sat_list:
        names_list.append(sat.get_name())

    return names_list