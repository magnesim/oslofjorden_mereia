# #####################
# LOAD MODEL

from datetime import datetime, timedelta 

from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_ROMS_native, reader_netCDF_CF_generic





#fjordos_url  = 'https://thredds.met.no/thredds/dodsC/fjordos/operational_archive_daily_agg'



o = OceanDrift(loglevel=20)  # Set loglevel to 0 for debug information

days = 14

deploy_time = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
dates = [(deploy_time+timedelta(days=ii)).strftime(format='%Y%m%d') for ii in range(days)]

# #####################
# ADD READERS
# Choose either FjordOS or Norkyst ocean model below

#use_model = 'FjordOS'
use_model = 'Norkyst'


if use_model == 'FjordOS':
    path_of = 'https://thredds.met.no/thredds/dodsC/fjordos/operational_archive/complete_archive'
    fjordos_fns = [path_of+'/ocean_his.nc_'+iidate+'00' for iidate in dates]

    reader_fjordos = reader_ROMS_native.Reader(fjordos_fns)
    reader_list = [reader_fjordos]



elif use_model == 'Norkyst':
    path_norkyst160 = 'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_160m_m71_be'
    path_norkyst800 = 'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_800m_m00_be'
    reader_norkyst160 = reader_netCDF_CF_generic.Reader(path_norkyst160)
    reader_norkyst800 = reader_netCDF_CF_generic.Reader(path_norkyst800)

    reader_list = [reader_norkyst160, reader_norkyst800]

o.add_reader(reader_list)



# #####################
# CONFIGURATION
#o.disable_vertical_motion()
o.set_config('drift:horizontal_diffusivity', 2.5)
o.set_config('general:coastline_action', 'previous')





# #####################
# SEED ELEMENTS

deploy_lon = 10.55
deploy_lat = 59.80


o.seed_elements(lon=deploy_lon, lat=deploy_lat, z=-1, radius=50, number=60000, time=[deploy_time,deploy_time+timedelta(days=days)])







# #####################
# RUN THE MODEL

total_time = 24*days # hours 
time_step = 600 # seconds

o.list_configspec()
o.run(steps=total_time*3600/time_step, time_step=time_step, time_step_output=3600,
       outfile='../output/outfile.nc'
       )











# #####################
# PLOTTING AND POST PROCESSING

buffer=0.02




o.animation(
    color='z',
        #colorbar=True,
#        background=['x_sea_water_velocity', 'y_sea_water_velocity'], scale=100,
        filename='../output/file.mp4',
        buffer=buffer,
        )



