import numpy as np
from datetime import datetime, timedelta
import opendrift 
import matplotlib.pyplot as plt 

import cartopy.crs as ccrs
from cartopy import feature as cfeature
import pandas as pd 






# ###########################################################################
# Set the input file
path = '/lustre/storeB/users/magnes/dsa/iaeamereia'
infn = f'{path}/outfile.nc'


histogram_file = '../output/histogram.nc'


# Size (m) of horisontal pixels for concentration 
psize   = 200
latlim = [59.4, 60.1]       # lower lat limits for the histograms
lonlim = [10.2, 10.8]    # lower lon limits for the histograms


# Filter out particles deeper than zmin
# this number will also be included in the file names 
zmin = 10
tag = '_{}m'.format(zmin)
tag = tag+''   # here, you can add specific name tag that will appear in all file names






# ###########################################################################
# Define/edit boxes for analysis (time series etc) here

box1_lon = [10.61, 10.64]        # Nesodden
box1_lat = [59.85, 59.87]
box2_lon = [10.53, 10.55]        # Nersnes
box2_lat = [59.77, 59.782]
box3_lon = [10.71, 10.745]        # Bunnefjorden
box3_lat = [59.84, 59.857]


boxes_org = [
    {'lon': box1_lon, 'lat': box1_lat, 'text': 'Nesodden', 'fc': 'none', 'alpha': 0.8, 'lw': 1, 'ec': 'k'},
    {'lon': box2_lon, 'lat': box2_lat, 'text': 'Nersnes', 'fc': 'none', 'alpha': 0.8, 'lw': 1, 'ec': 'k'},
    {'lon': box3_lon, 'lat': box3_lat, 'text': 'Bunnefjorden', 'fc': 'none', 'alpha': 0.8, 'lw': 1, 'ec': 'k'},
        ]




# plot the boxes on a map
fig = plt.figure()
ax=plt.subplot(projection=ccrs.Orthographic(10.5,60))
proj_pp=ccrs.PlateCarree()
for ibox in boxes_org:
    [lon1, lon2] = ibox['lon']
    [lat1, lat2] = ibox['lat']
    box_coords = [(lon1,lat1), (lon2,lat1), (lon2,lat2), (lon1,lat2), (lon1,lat1)]
    ax.plot(*zip(*box_coords), transform=proj_pp, color='red', linewidth=2 )
    ax.text(lon2, lat2, ibox['text'], horizontalalignment = 'right', transform=proj_pp, zorder=5)
ax.set_extent([10.3, 10.8, 59.5, 59.9], proj_pp)
ax.add_feature(cfeature.GSHHSFeature(scale='full'), facecolor='lightgray', zorder=4)
#ax.coastlines()
ax.gridlines()
#ax.stock_img()
fn='../output/map_locations{}.png'.format(tag)
plt.savefig(fn)
plt.close()






# ###########################################################################
# Read Opendrift output file as xarray

oa = opendrift.open_xarray(infn)
print(oa.ds.trajectory, len(oa.ds.trajectory))
ntra = len(oa.ds.trajectory)
print('ntra: ',ntra)

# Mask on depth 
# deeper than zmin will be masked out
oa.ds = oa.ds.where(oa.ds.z > -zmin)


# Read time variable from opendrift nc file
timefromfile  = np.array([pd.to_datetime(item).to_pydatetime() for item in oa.ds['time'].values])
timedifffromfile = (timefromfile[1] - timefromfile[0])



ntimesfromfile = len(timefromfile)
print('timefromfile',timefromfile[0], timefromfile[-1], len(timefromfile))
[d0,d1] = [timefromfile[0], timefromfile[-1]]

# Set d0 and d1 to limit the time period for the analysis
#d0 = datetime(1994,1,1)
#d1 = datetime(1995,2,28)







# ##############################################################################
# Plot figures and store necessary data 

boxes=boxes_org.copy()



# Set weigths on the trajectories
trajweights = np.ones(ntra) * 1.e10


# #########################
# Use opendrift function to compute horizontal histograms 
h  = oa.get_histogram(pixelsize_m=psize, weights=trajweights
                          ).sel(lon_bin=slice(lonlim[0],lonlim[1]), lat_bin=slice(latlim[0],latlim[1])
                          ).sel( time=slice(d0,d1) )
print( 'h.shape', h.shape )

# Scale by pixel volume to get concentration (atoms/m3)
h = h / (psize*psize*zmin)
h = h / 1000.  # Convert to atoms/L
h.name = 'tracer_concentration'


# SAVE TO NETCDF FILE
h.to_netcdf(histogram_file)

# ######################
# Plot maps of tracer concentration integrated over time
vminconc=-1
vmaxconc=3
map_proj = ccrs.Orthographic(10.5, 60)

b=h.mean(dim='time')
fig=plt.figure(figsize=[8,9])
ax = plt.subplot(projection=map_proj)
b=np.log10(b)
LONS, LATS = np.meshgrid(b['lon_bin'], b['lat_bin'])
b=b.squeeze()

m1 = ax.pcolormesh(LONS,LATS, b.transpose(), vmin=vminconc, vmax=vmaxconc,  cmap='plasma' , shading='nearest', transform=proj_pp, zorder=4)
ax.gridlines(zorder=7)
ax.add_feature(cfeature.GSHHSFeature(scale='full'), facecolor='lightgray', zorder=5)
cb=plt.colorbar(m1, label='log10 Concentration (at/L)')
ax.set_title(' '+tag+'\n'+d0.strftime("%Y%m%d")+' '+d1.strftime("%Y%m%d"))
fn = '../output/tracer_{}.png'.format(tag)
fig.savefig(fn)
plt.close(fig)






# ######################
# Plot maps of tracer age integrated over time
hage  = oa.get_histogram(pixelsize_m=psize, weights=oa.ds['age_seconds'], density=False).sel(lon_bin=slice(lonlim[0],lonlim[1]), lat_bin=slice(latlim[0],latlim[1])).sel( time=slice(d0, d1))
hage.name = 'particle age'
num   = oa.get_histogram(pixelsize_m=psize, weights=None, density=False).sel(lon_bin=slice(lonlim[0],lonlim[1]), lat_bin=slice(latlim[0],latlim[1])).sel( time=slice(d0, d1))
hage = hage / (86400)    # days
hageT  = hage.sum(dim='origin_marker') / num.sum(dim='origin_marker')
hageT.name = 'particle age'
maxage=14
hage = None
num  = None

b = hageT.mean(dim='time') 
fig=plt.figure(figsize=[8,9])
ax = plt.subplot(projection=map_proj)
LONS, LATS = np.meshgrid(b['lon_bin'], b['lat_bin'])
m1 = ax.pcolormesh(LONS,LATS, b.transpose(), vmin=0, vmax=maxage, cmap='rainbow', shading='nearest', transform=proj_pp, zorder=4)
ax.gridlines(zorder=7)
ax.add_feature(cfeature.GSHHSFeature(scale='full'), facecolor='lightgray', zorder=5)
cb=plt.colorbar(m1, label='Age (days)')
ax.set_title('Tracer age '+' '+tag+'\n'+d0.strftime("%Y%m%d")+' '+d1.strftime("%Y%m%d"))
fn = '../output/tracerage_{}.png'.format(tag)
fig.savefig(fn)
plt.close()








# Extract time series of concentration from each of the boxes
for ibox in boxes:
    fig=plt.figure(figsize=[12,9])
    ax1=plt.subplot(1,1,1)
    t1 = h.sel(lon_bin=slice(ibox['lon'][0], ibox['lon'][1]), lat_bin=slice(ibox['lat'][0], ibox['lat'][1])).mean(('lon_bin','lat_bin'))
    t1.sum(dim='origin_marker').plot(label=''+' total',ax=ax1)

    ax1.set_title(''+' concentration')
    
    for ax in [ax1]:
        ax.legend()
        ax.grid()
        ax.set_xlim([d0,d1])
    ax1.set_ylabel(' concentration (at/L)')
    plt.suptitle(ibox['text']+' '+tag)
    fn = '../output/location_ts_{}{}.png'.format(ibox['text'].replace(' ',''), tag)
    plt.savefig(fn)
    plt.close()





