import argparse
from gpx_handler import GpxHandler
from plotter import plot

_VERSION = "PyGpx 0.0.1"
_DEFAULT_RUNNING_AVG_WINDOW = 60

def main():
    parser = argparse.ArgumentParser(description='PyGpx - tool for GPX file analysis and correction')
    parser.add_argument('--version', action='version', version=_VERSION)
    parser.add_argument('-p', '--plot', dest='plot', action='store_true', help='plot file analysis result')
    parser.add_argument('gpx_file', metavar='FILE', help='path to GPX file')
    parser.add_argument('--running-avg', dest='running_avg_window', action='store', default=_DEFAULT_RUNNING_AVG_WINDOW)
    args = parser.parse_args()

    handler = GpxHandler(args.gpx_file, args.running_avg_window)
    plot(handler.get_errors(), handler.get_running_average())


if __name__ == "__main__":
    main()
