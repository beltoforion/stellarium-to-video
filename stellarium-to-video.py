#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from skyfield import almanac
from skyfield.api import load, wgs84
from typing import Tuple

import argparse
import isodate
import os
import os.path

from datetime import datetime, date, time, timedelta, timezone
from pathlib import Path
from geopy.geocoders import Nominatim

import subprocess
import time as xxx
import tempfile
import shutil


class Parameters:
    def __init__(self, args : argparse.Namespace) -> None:
        lonlat : list = args.loc[0]
        city : str = args.loc[1]
        view : list[float] = args.view

        self.__az  : float = view[0]
        self.__alt : float = view[1]
        self.__fov : float= view[2]
        self.__lon : float= lonlat[0]
        self.__lat : float= lonlat[1]
        self.__city : str = city
        self.__planet : str = args.planet
        self.__caption : str = args.caption
        self.__outfile : str = args.outfile
        self.__timespan : float = args.timespan
        self.__delta_t : float = args.dt
        self.__fps : float = args.fps
        self.__show_video : bool = args.show_video
        self.__template : str = args.template
        self.__start_date : datetime = self.__determine_start_time(args.date)


    def __determine_start_time(self, date: datetime) -> datetime:
        if date.hour==0 and date.minute==0 and date.second==0 and self.planet=='Earth':
            self.__start_at_sunset = True

            latlon = wgs84.latlon(self.lat, self.lon)
            ts = load.timescale()
            eph = load('de421.bsp')
            observer = eph['Earth'] + latlon

            t = ts.utc(date.year, date.month, date.day)
            t0, t1 = t, ts.utc(t.utc[0], t.utc[1], t.utc[2], 24)
            t_set, y_set = almanac.find_settings(observer, eph['Sun'], t0, t1)
            
            if y_set[0]==False:
                raise ValueError(f'You must specify a specific time because the location {lon},{lat} is experiencing either polar day or polar night! The script cannot compute a sunset time for this date: {date.isoformat()}.')

            return t_set[0].utc_datetime()
        else:
            self.__start_at_sunset = False
            return date
    

    @property
    def alt(self) -> float:
        return self.__alt
    

    @property   
    def az(self) -> float:
        return self.__az
    

    @property
    def fov(self) -> float:
        return self.__fov


    @property
    def lon(self) -> float:
        return self.__lon
    

    @property
    def lat(self) -> float:
        return self.__lat
    

    @property
    def city(self) -> str:
        return self.__city
    

    @property
    def planet(self) -> str:
        return self.__planet
    

    @property
    def start_date(self) -> datetime:
        return self.__start_date
    

    @property
    def caption(self) -> str:
        return self.__caption
    

    @property
    def outfile(self) -> str:
        return self.__outfile
    

    @property
    def timespan(self) -> float:
        return self.__timespan
    

    @property
    def delta_t(self) -> float:
        return self.__delta_t


    @property
    def fps(self) -> float:
        return self.__fps   
    

    @property
    def show_video(self) -> bool:
        return self.__show_video
    
    @property
    def start_at_sunset(self) -> bool:
        return self.__start_at_sunset
    
    @property
    def template(self) -> str:
        return self.__template  


class StellariumToVideo:
    def __init__(self, param : Parameters) -> None:
        tempPath : Path = Path(tempfile.gettempdir()) / 'kalstar_frames'
        self.__frame_folder = tempPath
        self.__final_file = self.__frame_folder / 'final.png'
        self.__param = param

        # Create frame folder if it not already exists
        if os.path.exists(str(self.__frame_folder)):
            shutil.rmtree(str(self.__frame_folder))

        os.mkdir(str(self.__frame_folder))


    def create_script(self, script_path : Path) -> None:
        with open(f'./script/{self.__param.template}', 'r') as file:
            script = file.read()

        if os.name == 'nt':
            script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder).replace("\\", "\\\\"))
        else:
            script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder))


        # set the sript variables
        script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder).replace("\\", "\\\\"))
        script = script.replace("$LAT$", str(self.__param.lat))
        script = script.replace("$LONG$", str(self.__param.lon))
        script = script.replace("$TITLE$", str(self.__param.caption))
        script = script.replace("$DATE$", self.__param.start_date.astimezone(timezone.utc).isoformat().replace("+00:00", ""))
        script = script.replace("$TIMESPAN$", str(self.__param.timespan/3600))
        script = script.replace("$FOV$", str(self.__param.fov))
        script = script.replace("$DELTAT$", str(self.__param.delta_t))
        script = script.replace("$AZ$", str(self.__param.az))
        script = script.replace("$ALT$", str(self.__param.alt))
        script = script.replace("$PLANET$", self.__param.planet)

        # create the script in stellariums script folder
        file = open(script_path / 'stellarium_to_video.ssc', "w")
        file.write(script)
        file.close()

    
    def create_frames(self) -> None:
        if os.name == 'nt':
            proc_stellarium = subprocess.Popen(['C:\\Program Files\\Stellarium\\stellarium.exe', '--startup-script', 'stellarium_to_video.ssc', '--screenshot-dir', str(self.__frame_folder)], stdout=subprocess.PIPE);
        else:        
            proc_stellarium = subprocess.Popen(['stellarium', '--startup-script', 'stellarium_to_video.ssc', '--screenshot-dir', str(self.__frame_folder)], stdout=subprocess.PIPE);

        # wait for script finish
        s = 0
        timeout = 600
        while not os.path.exists(self.__final_file) and s < timeout:
            xxx.sleep(1)
            s = s + 1

        proc_stellarium.kill()


    def create_video(self) -> None:
        proc = subprocess.Popen(['ffmpeg',
                        '-y', # overwrite existing file
                        '-r', str(self.__param.fps),
                        '-f', 'image2',
                        '-i', f'{self.__frame_folder}/frame_%03d.png',
#                        '-s', '1920x1080',
                        '-s', '960x540',                        
                        '-crf', '12',   # niedriger ist besser
                        '-pix_fmt', 'yuv420p',
                        self.__param.outfile], stdout=subprocess.PIPE)
        proc.communicate()

        if (self.__param.show_video):
            proc = subprocess.Popen(['vlc', '--repeat', self.__param.outfile], stdout=subprocess.PIPE)
            proc.communicate()


def arg_to_start_date(s) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        msg = f"Not a valid date: '{s}'."
        raise argparse.ArgumentTypeError(msg)


def arg_to_positive_number(x) -> float:
    x = float(x)
    if x < 0.0:
        raise argparse.ArgumentTypeError("%r is negative"%(x,))
    return x


def arg_to_iso_8661_duration(x) -> float:
    what = isodate.parse_duration(x)
    if isinstance(what, isodate.duration.Duration):
        sec = float(what.years) * 365.25 * 86400 + float(what.months) * 30.44 * 86400 + what.total_seconds()
    else:
        sec = what.total_seconds()
    return sec


def arg_to_vec3(s : str) -> list:
    try:
        list = [float(item) for item in s.split(',')]
        if len(list) != 3:
            raise argparse.ArgumentTypeError("The vector must have three components")
        
        return list
    except ValueError:
        raise argparse.ArgumentTypeError("Each value must be a floating point number")


def arg_to_location(s : str) -> Tuple[list, str]:
    try:
        if ',' in s:
            list = [float(item) for item in s.split(',')]
            if len(list) != 2:
                raise argparse.ArgumentTypeError("Need two comma separated values: longitude, latitude")
            address = ''
        else:
            geolocator = Nominatim(user_agent="stellarium-to-video")
            location = geolocator.geocode(s)
            list = [location.longitude, location.latitude]
            address = location.address

        return (list, address)
    except ValueError:
        raise argparse.ArgumentTypeError("Each value must be a floating point number")


def main() -> None:
    parser = argparse.ArgumentParser("stellarium-to-video.py - A star motion video generator")
    parser.add_argument("-c", "--Caption", dest="caption", help='Caption of the video', required=False, default='The Night Sky')
    parser.add_argument("-d", "--DateTime", dest="date", help='A date time string in UTC. If no date is given todays date is used. If no time is given the animation automatically starts an hour after sunset.', required=False, type=arg_to_start_date, default=date.today().isoformat())
    parser.add_argument("-dt", "--DeltaT", dest="dt", help='Simulated time in between two Frames as an ISO 8601 duration (default="PT20S" -> 20 seconds)', default='PT20S', type=arg_to_iso_8661_duration)
    parser.add_argument("-fps", "--FramesPerSecond", dest="fps", help='Frame rate of the output video', default='30', type=arg_to_positive_number)
    parser.add_argument("-l", "--Location", dest="loc", help='Location of the observer', default="13.9,50.9", type=arg_to_location)
    parser.add_argument("-o", "--Outfile", dest="outfile", help='Output filename', default='out.mp4')
    parser.add_argument("-p", "--Planet", dest="planet", help='The planet you are on.', default='Earth', type=str)
    parser.add_argument("-s", "--Show", dest="show_video", default=True, action='store_true', help='If this flag is set the video is shown after rendering (VLC must be installed)')
    parser.add_argument("-t", "--Template", dest="template", help='The template script. This must be the name of a ssc script in the script folder)', required=False, default='default.ssc', type=str)    
    parser.add_argument("-ts", "--TimeSpan",dest="timespan", help='Total time span covered by the simulation as ISO 8601 duration (default="PT2H" -> 2 hours)', default='PT2H', type=arg_to_iso_8661_duration)
    parser.add_argument("-v", "--View", dest="view", help='Defines the view Altitude, Azimuth, Field of View', default="180,35.0,70.0", type=arg_to_vec3)

    param = Parameters(parser.parse_args())

    print('')
    print('##############################################################')
    print('#                                                            #')
    print('#  Stellarium-To-Video - Generating videos of the night sky  #')
    print('#                                                            #')    
    print('##############################################################')
    print('')    
    print(f'Location:')
    print(f'  - lon={param.lon}, lat={param.lat}, address="{param.city}"')
    print(f'  - planet="{param.planet}"')
    print(f'  - template="{param.template}"')    
    print(f'Time:')
    print(f'  - start={param.start_date.isoformat()}, timespan={param.timespan} s, delta_t={param.delta_t} s')
    print(f'View:')
    print(f'  - alt={param.alt}°, az={param.az}°, fov={param.fov}°')
    print(f'Video:')
    print(f'  - caption="{param.caption}"')
    print(f'  - file="{param.outfile}"')
    print('')

    if param.start_at_sunset:
        print('\033[93m' + 'Warning: No time given. The script will try to use the sunset time of the given day!' + '\033[0m')

    stellarium_data_path : Path
    if os.name == 'nt':
        stellarium_data_path = Path.home() / 'AppData' / 'Roaming' / 'Stellarium'

        # check if stellarium is installed where it is expected. 
        if not os.path.isfile("C:\\Program Files\\Stellarium\\stellarium.exe"):
            raise Exception('Stellarium not found! This script expects stellarium to be installed in C:\\Program Files\\Stellarium\\stellarium.exe!')
    else:
        stellarium_data_path = Path.home() / '.stellarium'

    # Check if there is a local stellarium folder
    if not os.path.isdir(stellarium_data_path.absolute()):
        raise Exception('Stellarium does not seem to be installed!')

    # if there is no local scripts folder, create one
    script_folder = stellarium_data_path / 'scripts'
    if not os.path.isdir(script_folder.absolute()):
        os.mkdir(script_folder.absolute())

    sa = StellariumToVideo(param)
    sa.create_script(script_folder)
    sa.create_frames()
    sa.create_video()


if __name__ == "__main__":
#    try:
        main()
#    except Exception as e:
#        print('\033[91m' + f'Error: {e}' + '\033[0m')
