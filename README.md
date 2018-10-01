# kalstar
 Making videos of the night sky with [Stellarium](https://stellarium.org)
 
This archive contains a python 3 script that will automate the process of creating videos of the night sky with stellarium. It will take an observation position as well as multiple obvervation parameters as command line options and then create a script for Stellariums scripting engine to compute animation frames for the given date. Once the frames are created the script will invoke ffmpeg to combine the frames into an mp4 video file.

For more details please go to the [web page of this project](http://beltoforion.de/article.php?a=stellarium_video&hl=en)
 
# Command Line Options:

_-long xx.xxx_ 
Longitude of the observation loaction.

_-lat xx.xxx_ 
Latitude of the observation loaction

_-alt xx.xxx_ 
Altitude of the center of the field of view

_-az 	xx.xxx_ 	
Azimut in degrees (View direction)

_-d YYYY-MM-DD_	
The simulation date. The animation automatically starts an hour after sunset on the specified day.

_-fov xx.xxx_ 	
The field of view in degrees.

_-fps xx_ 	
Frame rate of the output video.

_-t abc_ 	
The title of the video. The video title will be superimposed onto the video.

_-ts xx_ 	
The simulation time span in hours.

_-dt xx_ 	
The time difference between two sucessive frames in seconds.

_-o abc.mp4_ 
The name of the output video file.

_-s_ 	
When this flag is specified an instance of VLC will be started once the video is created.

# Example:

The following command will compute the first 2 hours of night sky in Berlin (Germany) on the 25th September of the year 2018. 

**python3 kalstar.py** -lat 52.5186 -long 13.4083 -t "Look at all the Stars!" -az 90 -alt 25 -d 2018-09-25 -ts 2 -s -o out.mp4 -fov 70 -dt 30
