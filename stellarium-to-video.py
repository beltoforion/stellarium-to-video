#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from skyfield import almanac
from skyfield.api import load, wgs84

import argparse
import isodate
import os
import os.path

from datetime import datetime, time, timedelta
from pathlib import Path

import subprocess
import time as xxx
import tempfile
import shutil


class StellariumToVideo:
    def __init__(self, args) -> None:
        self.__args = args
        tempPath : Path = Path(tempfile.gettempdir()) / 'kalstar_frames'
        self.__frame_folder = tempPath
        self.__final_file = self.__frame_folder / 'final.png'

        # Create frame folder if it not already exists
        if os.path.exists(str(self.__frame_folder)):
            shutil.rmtree(str(self.__frame_folder))

        os.mkdir(str(self.__frame_folder))


    def create_script(self, script_path : Path) -> None:
        with open('./script/default.ssc', 'r') as file:
            script = file.read()

        if os.name == 'nt':
            script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder).replace("\\", "\\\\"))
        else:
            script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder))
            
        # set the sript variables
        script = script.replace("$FRAME_FOLDER$", str(self.__frame_folder).replace("\\", "\\\\"))
        script = script.replace("$LAT$", str(self.__args.lat))
        script = script.replace("$LONG$", str(self.__args.long))
        script = script.replace("$TITLE$", str(self.__args.title))
        script = script.replace("$DATE$", self.__args.date.isoformat().replace("+00:00", ""))
        script = script.replace("$TIMESPAN$", str(self.__args.timespan/3600))
        script = script.replace("$FOV$", str(self.__args.fov))
        script = script.replace("$DELTAT$", str(self.__args.dt))
        script = script.replace("$AZ$", str(self.__args.az))
        script = script.replace("$ALT$", str(self.__args.alt))

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
                        '-r', str(self.__args.fps),
                        '-f', 'image2',
                        '-s', '1920x1080',
                        '-i', '{0}/frame_%03d.png'.format(self.__frame_folder),
                        '-crf', '12',   # niedriger ist besser
                        '-pix_fmt', 'yuv420p',
                        self.__args.outfile], stdout=subprocess.PIPE);
        proc.communicate()

        if (self.__args.show_video):
            proc = subprocess.Popen(['vlc', '--repeat', self.__args.outfile], stdout=subprocess.PIPE)
            proc.communicate()


def start_date(s) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        msg = f"Not a valid date: '{s}'."
        raise argparse.ArgumentTypeError(msg)


def positive_number(x) -> float:
    x = float(x)
    if x < 0.0:
        raise argparse.ArgumentTypeError("%r is negative"%(x,))
    return x


def iso_8661_duration(x) -> float:
    what = isodate.parse_duration(x)
    if isinstance(what, isodate.duration.Duration):
        sec = float(what.years) * 365.25 * 86400 + float(what.months) * 30.44 * 86400 + what.total_seconds()
    else:
        sec = what.total_seconds()
    return sec


def determine_start_time(date: datetime, lat : float, lon : float, planet : str) -> datetime:
    if date.hour==0 and date.minute==0 and date.second==0 and planet=='Earth':
        print('\033[93m' + 'Warning: No time given. The script will try to use the sunset time of the given day!' + '\033[0m')

        latlon = wgs84.latlon(lat, lon)
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
        return date


def main() -> None:
    parser = argparse.ArgumentParser("kalstar - A star motion video generator")
    parser.add_argument("-long", "--Longitude", dest="long", help='Longitude', default=13.34277, type=float)
    parser.add_argument("-lat", "--Latitude", dest="lat", help='Latitude', default=50.911944, type=float)
    parser.add_argument("-p", "--Planet", dest="planet", help='The planet you are on.', default='Earth', type=str)
    parser.add_argument("-alt", "--Altitude", dest="alt", help='Altitude of the center of the field of view', default=20, type=float)
    parser.add_argument("-az", "--Azimuth", dest="az", help='Azimut in degrees (View direction)', default=0, type=float)
    parser.add_argument("-d", "--DateTime", dest="date", help='A date time string in UTC. If no time is given the animation automatically starts an hour after sunset.', required=True, type=start_date)
    parser.add_argument("-fps", "--FramesPerSecond", dest="fps", help='Frame rate of the output video', default='30', type=positive_number)
    parser.add_argument("-fov", "--FieldOfView", dest="fov", help='The field of view', default='70', type=float)
    parser.add_argument("-t", "--Title", dest="title", help='Caption of the video', required=True)
    parser.add_argument("-ts", "--TimeSpan",dest="timespan", help='Total time span covered by the simulation as ISO 8601 duration (default="PT2H" -> 2 hours)', default='PT2H', type=iso_8661_duration)
    parser.add_argument("-dt", "--DeltaT", dest="dt", help='Simulated time in between two Frames as an ISO 8601 duration (default="PT20S" -> 20 seconds)', default='PT20S', type=iso_8661_duration)
    parser.add_argument("-o", "--Outfile", dest="outfile", help='Output filename', default='out.mp4')
    parser.add_argument("-s", "--Show", dest="show_video", default=False, action='store_true', help='If this flag is set the video is shown after rendering (VLC must be installed)')
    args = parser.parse_args()

    print('Stellarium-To-Video - Generating videos of the night sky:')
    print('-------------------------------------------')
    print(f'Location:')
    print(f'  - "{args.planet}" at long={args.long}°, lat={args.lat}°')
    print(f'Simulation time:')
    print(f'  - Time between frames: {args.dt} secsonds')
    print(f'  - Total duration:      {args.timespan} secsonds')
    args.date = determine_start_time(args.date, args.lat, args.long, args.planet)
    print(f'  - Start time (UTC):   {args.date.isoformat()}')
    print(f'Look at:')
    print(f'  - altitude:         {args.alt}')
    print(f'  - azimut:           {args.az}')
    print(f'Output:')
    print(f'  - Video caption:    "{args.title}"')
    print(f'  - Output file:      "{args.outfile}"')

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

    sa = StellariumToVideo(args)
    sa.create_script(script_folder)
    sa.create_frames()
    sa.create_video()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('\033[91m' + f'Error: {e}' + '\033[0m')
