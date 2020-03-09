"""
A module for working with NOAA-CIRES 20th Century Reanalysis V2 data.
See http://www.esrl.noaa.gov/psd/data/gridded/data.20thC_ReanV2.html
"""

def read(rean_file):
    """
    Reads data from a NOAA-CIRES 20th Century Reanalysis V2 file (netCDF)
    containing global 2.0-deg daily mean 500 mb heights.

    Usage:
    >>> d = read('/path/to/file')
    >>> print d['hgt'][0,0,:,:]
    """

    from scipy.io import netcdf

    try:
        f = netcdf.netcdf_file(rean_file, 'r', mmap=False)
    except IOError:
        print('File "' + rean_file + '" cannot be read.')
        return

    data = {
        'file':f.filename,
        'level':f.variables['level'][0],
        'time':f.variables['time'], 
        'hgt':f.variables['hgt'], 
        'lat':f.variables['lat'], 
        'lon':f.variables['lon']
        }
    f.close()

    return data


def prep(rean_data):
    """
    Converts data read from a NOAA-CIRES 20th Century Reanalysis V2
    file into more convenient formats. Returns a dict containing lon, lat
    and hgt as NumPy arrays, and time as list of struct_time tuples.

    Usage:
    >>> d = read('/path/to/file')
    >>> p = prep(d)
    """
    
    import time, calendar
    
    # Make a dict for storing results.
    data = {
        'lat' : rean_data['lat'].data, 
        'lon' : rean_data['lon'].data
        }

    # Apply scale_factor and add_offset properties to hgt variable.
    # Add to data dict.
    data['hgt'] = rean_data['hgt'].data * rean_data['hgt'].scale_factor \
                  + rean_data['hgt'].add_offset

    # Convert time variable (which is in hours since 0001-01-01) into
    # calendar dates. Add to data dict.
    start_time = '0001-01-01' # from rean_data['time'].units
    start_time_cal = time.strptime(start_time, '%Y-%m-%d')
    start_time_sec = calendar.timegm(start_time_cal)
    sec_in_hour = 60.0*60.0
    time_in_sec = rean_data['time'].data*sec_in_hour + start_time_sec
    time_in_struct_time = [time.gmtime(i) for i in time_in_sec]
    data['time'] = [time.strftime('%Y-%m-%d', j) for j in time_in_struct_time]

    return data


def view(prep_data, dayofyear=46, show=False, outfile='gph.png'):
    """
    Draws a contour plot of the mean 500 mb geopotential surface for a
    specified day of the year with data from a NOAA-CIRES 20th Century
    Reanalysis file. The plot is saved to a PNG file. 

    Usage:
    >>> d = read('/path/to/file')
    >>> p = prep(d)
    >>> view(p, show=False)
    """

    from matplotlib import pyplot as plt
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    import math

    # Set up map projection.
    map = Basemap(projection='ortho',
                  lon_0=-105,
                  lat_0=60,
                  resolution='l')
    map.drawcoastlines()
    map.drawmapboundary()
    map.drawparallels(range(-90, 120, 30))
    map.drawmeridians(range(0, 420, 60))

    # Transform lat/lon into map coordinates (meters).
    x, y = map(*np.meshgrid(prep_data['lon'], prep_data['lat']))

    # Extract a single day of heights.
    hgt = prep_data['hgt'][dayofyear, 0, :, :]

    # Set up consistent contour levels so the colorbar doesn't change.
    delta = 100
    hgt_min = math.floor(prep_data['hgt'].min()/delta)*delta
    hgt_max = math.ceil(prep_data['hgt'].max()/delta)*delta
    clevels = np.arange(hgt_min, hgt_max, delta)

    # Draw contours of gph and annotate.
    c = map.contourf(x, y, hgt, levels=clevels, cmap=plt.cm.RdYlBu_r)
    cb = map.colorbar(c, 'right', size="3%", pad='5%')
    cb.set_label('Geopotential Height (m)')
    plt.title('500 mb Geopotential Heights : ' + prep_data['time'][dayofyear])
    plt.text(0.5*max(plt.axis()), -0.1*max(plt.axis()),
             'Data: NOAA-CIRES 20th Century Reanalysis, Version 2',
             fontsize=10,
             verticalalignment='bottom',
             horizontalalignment='center')

    # Either show plot or save it to a PNG file.
    if show is True:
        plt.show()
    else:
        plt.savefig(outfile, dpi=96)
        plt.close()

    return

# Example / unit test 
if __name__ == '__main__':
    rean_file = './data/X174.29.255.181.65.14.23.9.nc'
    rean_data = read(rean_file)
    prep_data = prep(rean_data)
    view(prep_data, show=False)
