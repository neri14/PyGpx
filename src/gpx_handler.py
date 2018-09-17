import lxml.etree as etree
import datetime as dt

_GPX_NAMESPACE = {"gpx": "http://www.topografix.com/GPX/1/1"}
_GPX_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class GpxHandler:
    def __init__(self, filename, running_avg_window):
        self.filename = filename
        self.gpx = etree.parse(self.filename)
        self.gpx_timestamps = self.gpx.xpath('//gpx:trkseg/gpx:trkpt/gpx:time', namespaces=_GPX_NAMESPACE)
        self.running_avg_window = running_avg_window

        self.errors = []
        self.running_avg = []

    def get_errors(self):
        if len(self.errors) == 0:
            self.__calculate_errors()
        print("self.errors = " + str(len(self.errors)))
        return self.errors

    def get_running_average(self):
        if len(self.running_avg) == 0:
            self.__calculate_running_average()
        print("self.running_avg = " + str(len(self.running_avg)))
        return self.running_avg

    def __calculate_errors(self):
        if len(self.errors) > 0:
            return

        first_time = None
        ideal_elapsed_time = 0

        for timestamp in self.gpx_timestamps:
            time = dt.datetime.strptime(timestamp.text, _GPX_TIME_FORMAT)
            if first_time is None:
                first_time = time
            self.errors.append((time - first_time).total_seconds() - ideal_elapsed_time)
            ideal_elapsed_time = ideal_elapsed_time + 1

    def __calculate_running_average(self):
        if len(self.running_avg) > 0:
            return
        self.__calculate_errors()

        running_avg_elements = []
        for error in self.errors:
            running_avg_elements.append(error)

            if len(running_avg_elements) > self.running_avg_window:
                running_avg_elements.pop(0)

            if len(running_avg_elements) == self.running_avg_window:
                ravg = sum(running_avg_elements) / len(running_avg_elements)
                self.running_avg.append(ravg)
            elif len(running_avg_elements) > self.running_avg_window / 2:
                self.running_avg.append(None)