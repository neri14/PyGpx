import argparse
from gpx_handler import GpxHandler
from plotter import plot

_VERSION = "PyGpx 0.0.1"
_DEFAULT_RUNNING_AVG_WINDOW = 60
_DEFAULT_HYSTERESIS = 0.7


def get_value_change_count(lst):
    last_val = lst[0]
    count = 0
    for val in lst:
        if val != last_val:
            if last_val is not None:
                count = count + 1
            last_val = val
    return count


def main():
    parser = argparse.ArgumentParser(description='PyGpx - tool for GPX file analysis and correction')
    parser.add_argument('--version', action='version', version=_VERSION)
    parser.add_argument('-p', '--plot', dest='plot', action='store_true', help='plot file analysis result')
    parser.add_argument('gpx_file', metavar='FILE', help='path to GPX file')
    parser.add_argument('--running-avg-window', metavar='W', dest='running_avg_window', action='store', help='running average windows size (default: ' + str(_DEFAULT_RUNNING_AVG_WINDOW) + ')', default=_DEFAULT_RUNNING_AVG_WINDOW)
    parser.add_argument('--hysteresis', metavar='H', dest='hysteresis', action='store', help='hysteresis value (default: ' + str(_DEFAULT_HYSTERESIS) + ')', default=_DEFAULT_HYSTERESIS)

    args = parser.parse_args()

    handler = GpxHandler(args.gpx_file, args.running_avg_window, args.hysteresis)
    print("Gated errors values change " + str(get_value_change_count(handler.get_gated_errors())) + " times")
    plot(handler.get_errors(), handler.get_running_average(), handler.get_gated_errors())


if __name__ == "__main__":
    main()
