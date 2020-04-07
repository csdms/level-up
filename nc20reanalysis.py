"""
A module for working with NOAA-CIRES 20th Century Reanalysis V2 data.
See http://www.esrl.noaa.gov/psd/data/gridded/data.20thC_ReanV2.html
"""
import time
import calendar
import math
import numpy as np
from scipy.io import netcdf
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap


class Nc20Reanalysis(object):

    sec_in_hour = 60.0 * 60.0

    def __init__(self, reanalysis_file=None):
        self.filename = reanalysis_file
        self.level = None
        self.time = None
        self.hgt = None
        self.lat = None
        self.lon = None
        self.hgt_scaled = None
        self.date = None

    def read(self):
        """Read data from a NOAA-CIRES 20th Century Reanalysis V2 file."""
        try:
            f = netcdf.netcdf_file(self.filename, "r", mmap=False)
        except IOError:
            print('File "' + self.filename + '" cannot be read.')
            return

        self.level = f.variables["level"][0]
        self.time = f.variables["time"]
        self.hgt = f.variables["hgt"]
        self.lat = f.variables["lat"].data
        self.lon = f.variables["lon"].data

        f.close()

    def prep(self):
        """Prepare reanalysis data for plotting."""
        self.hgt_scaled = self.hgt.data * self.hgt.scale_factor \
            + self.hgt.add_offset

        start_time = "0001-01-01"  # from self.time.units
        start_time_cal = time.strptime(start_time, "%Y-%m-%d")
        start_time_sec = calendar.timegm(start_time_cal)
        time_in_sec = self.time.data * self.sec_in_hour + start_time_sec
        time_in_struct_time = [time.gmtime(i) for i in time_in_sec]
        self.date = [time.strftime("%Y-%m-%d", j) for j in time_in_struct_time]

    def view(self, dayofyear=46, show=False, outfile="gph.png"):
        """Draw a contour plot of mean 500 mb heights."""
        map = Basemap(projection="ortho", lon_0=-105, lat_0=60, resolution="l")
        map.drawcoastlines()
        map.drawmapboundary()
        map.drawparallels(range(-90, 120, 30))
        map.drawmeridians(range(0, 420, 60))

        # Transform lat/lon into map coordinates (meters).
        x, y = map(*np.meshgrid(self.lon, self.lat))

        # Extract a single day of heights.
        hgt = self.hgt_scaled[dayofyear, 0, :, :]

        # Set up consistent contour levels so the colorbar doesn't change.
        delta = 100
        hgt_min = math.floor(self.hgt_scaled.min() / delta) * delta
        hgt_max = math.ceil(self.hgt_scaled.max() / delta) * delta
        clevels = np.arange(hgt_min, hgt_max, delta)

        c = map.contourf(x, y, hgt, levels=clevels, cmap=plt.cm.RdYlBu_r)
        cb = map.colorbar(c, "right", size="3%", pad="5%")
        cb.set_label("Geopotential Height (m)")
        plt.title("500 mb Geopotential Heights : " + self.date[dayofyear])
        plt.text(
            0.5 * max(plt.axis()),
            -0.1 * max(plt.axis()),
            "Data: NOAA-CIRES 20th Century Reanalysis, Version 2",
            fontsize=10,
            verticalalignment="bottom",
            horizontalalignment="center",
        )

        if show is True:
            plt.show()
        else:
            plt.savefig(outfile, dpi=96)
            plt.close()


if __name__ == "__main__":
    rean_file = "./data/X174.29.255.181.65.14.23.9.nc"
    n = Nc20Reanalysis()
    n.filename = rean_file
    n.read()
    n.prep()
    n.view(show=False)
