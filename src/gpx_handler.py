import lxml.etree as etree
import datetime as dt

_GPX_NAMESPACE = {"gpx": "http://www.topografix.com/GPX/1/1"}
_GPX_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
_GPX_TIME_INTERVAL = 1


class GpxHandler:
    def __init__(self, input_filename, running_avg_window, hysteresis):
        self.input_filename = input_filename
        self.gpx = etree.parse(self.input_filename)
        self.gpx_timestamps = self.gpx.xpath('//gpx:trkseg/gpx:trkpt/gpx:time', namespaces=_GPX_NAMESPACE)
        self.running_avg_window = running_avg_window
        self.hysteresis = hysteresis

        self.errors = []
        self.running_avg = []
        self.gated_errors = []

    def get_errors(self):
        if len(self.errors) == 0:
            self.__calculate_errors()
        return self.errors

    def get_running_average(self):
        if len(self.running_avg) == 0:
            self.__calculate_running_average()
        return self.running_avg

    def get_gated_errors(self):
        if len(self.gated_errors) == 0:
            self.__calculate_gated_errors()
        return self.gated_errors

    def reset_stats(self):
        self.errors = []
        self.running_avg = []
        self.gated_errors = []

    def fix(self):
        # gated_values = self.get_gated_errors()
        gated_error_buffer = self.__find_first(self.get_gated_errors())

        if gated_error_buffer is None:
            return

        first_time = None
        ideal_elapsed_time = 0

        for timestamp, gated_error in zip(self.gpx_timestamps, self.gated_errors):
            if first_time is None:
                first_time = dt.datetime.strptime(timestamp.text, _GPX_TIME_FORMAT)

            error = gated_error
            if error is None:
                error = gated_error_buffer
            else:
                gated_error_buffer = error

            correct_time = first_time + dt.timedelta(seconds=(ideal_elapsed_time + error))

            timestamp.text = correct_time.strftime(_GPX_TIME_FORMAT)
            ideal_elapsed_time = ideal_elapsed_time + _GPX_TIME_INTERVAL
        self.reset_stats()

    def write(self, output_filename):
        self.gpx.write(open(output_filename, 'wb'), encoding='utf-8', xml_declaration=True)

    def __calculate_errors(self):
        if len(self.errors) > 0:
            self.errors = []

        first_time = None
        ideal_elapsed_time = 0

        for timestamp in self.gpx_timestamps:
            time = dt.datetime.strptime(timestamp.text, _GPX_TIME_FORMAT)
            if first_time is None:
                first_time = time
            self.errors.append((time - first_time).total_seconds() - ideal_elapsed_time)
            ideal_elapsed_time = ideal_elapsed_time + _GPX_TIME_INTERVAL

    def __calculate_running_average(self):
        if len(self.running_avg) > 0:
            self.running_avg = []
        errors = self.get_errors()

        running_avg_elements = []
        for error in errors:
            running_avg_elements.append(error)

            if len(running_avg_elements) > self.running_avg_window:
                running_avg_elements.pop(0)

            if len(running_avg_elements) == self.running_avg_window:
                ravg = sum(running_avg_elements) / len(running_avg_elements)
                self.running_avg.append(ravg)
            elif len(running_avg_elements) > self.running_avg_window / 2:
                self.running_avg.append(None)

        for i in range(0, int(self.running_avg_window / 2)):
            self.running_avg.append(None)

    def __calculate_gated_errors(self):
        if len(self.gated_errors) > 0:
            self.gated_errors = []
        running_avg = self.get_running_average()

        tmp_gated_error = 0
        for avg in running_avg:
            if avg is not None:
                tmp_gated_error = self.__gate(avg, tmp_gated_error)
                self.gated_errors.append(tmp_gated_error)
            else:
                self.gated_errors.append(None)

    def __gate(self, current_value, last_gated_value):
        tmp = last_gated_value - current_value
        if tmp > self.hysteresis:
            return last_gated_value - 1
        elif tmp < -self.hysteresis:
            return last_gated_value + 1
        else:
            return last_gated_value

    def __find_first(self, list):
        for v in list:
            if v is not None:
                return v
        return None
