# #####################
# LOAD MODEL

from datetime import datetime, timedelta 

from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_ROMS_native, reader_netCDF_CF_generic


o = OceanDrift(loglevel=20)  # Set loglevel to 0 for debug information



# #####################
# SET START TIME

#deploy_time = datetime(2024,6,16,9,0)
deploy_time = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
indate = deploy_time.strftime(format='%Y%m%d')




# #####################
# ADD READERS
# Choose either FjordOS or Norkyst ocean model below

#use_model = 'FjordOS'
use_model = 'Norkyst'


if use_model == 'FjordOS':
    fjordos_fn = 'ocean_his.nc_'+indate+'00'
    #fjordos_fn = 'ocean_his.nc_fc'

    path_of = 'https://thredds.met.no/thredds/dodsC/fjordos/operational_archive/complete_archive/' 
    #path_of = 'https://thredds.met.no/thredds/dodsC/fjordos/operational_archive/daily'

    #reader_arome = reader_netCDF_CF_generic.Reader(f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{str(deploy_time.year)}/{deploy_time.month:02d}/{deploy_time.day:02d}/meps_det_2_5km_{indate}T00Z.nc')
    reader_fjordos = reader_ROMS_native.Reader(path_of+'/'+fjordos_fn)

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
o.set_config('drift:horizontal_diffusivity', 1.5)
o.set_config('drift:stokes_drift',False)
#o.set_config('seed:wind_drift_factor',0.02)





# #####################
# SEED ELEMENTS

deploy_lon = 10.55
deploy_lat = 59.80
#deploy_lon = 10.65
#deploy_lat = 59.10



o.seed_elements(lon=deploy_lon, lat=deploy_lat, z=-1, radius=50, number=2000, time=deploy_time)







# #####################
# RUN THE MODEL

total_time = 9 # hours 
time_step = 300 # seconds

o.list_configspec()
o.run(steps=total_time*3600/time_step, time_step=time_step, time_step_output=900)











# #####################
# PLOTTING AND POST PROCESSING

buffer=0.05

o.animation(
    color='z',
        #colorbar=True,
#        background=['x_sea_water_velocity', 'y_sea_water_velocity'], scale=100,
        #filename='../output/file1.mp4',
        buffer=buffer,
        )

o.plot(
    linecolor='z',
    buffer=buffer,
#    show_elements=False,
    #filename='file.png',
    )







# ######################
# NEW SIMULATION; DISABLE WIND DRIFT
o2 = OceanDrift(loglevel=20)
o2.add_reader(reader_list)

o2.disable_vertical_motion()
o2.set_config('drift:horizontal_diffusivity', 1.5)
o2.set_config('drift:stokes_drift',False)
# o2.set_config('seed:wind_drift_factor',0.)
o2.seed_elements(lon=deploy_lon, lat=deploy_lat, z=-1., radius=50, number=2000, time=deploy_time )
o2.list_configspec()
o2.run(steps=total_time*3600/time_step, time_step=time_step, time_step_output=900)


o.animation(compare=o2, legend=['with vertical motion', 'without vertical motion'], 
            buffer=buffer, 
            #filename='../output/file2.mp4'
            )
