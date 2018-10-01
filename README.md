# kalstar
 Making videos of the night sky with [Stellarium](https://stellarium.org)
 
 For Details please go to the web page of this project:
 http://beltoforion.de/article.php?a=stellarium_video&hl=en
 
This archive contains a python 3 script that will automate the process of creating videos of the night sky with stellarium. It will take an observation position as well as multiple obvervation parameters as command line options and then create a script for Stellariums scripting engine to compute animation frames for the given date. Once the frames are created the script will invoke ffmpeg to combine the frames into an mp4 video file.

# Command Line Options:

_-long 	float_ 	
Longitude of the observation loaction

_-lat 	float_ 	
Latitude of the observation loaction

-alt 	float 	
Altitude of the center of the field of view

-az 	float 	Azimut in degrees (View direction)
-d 	date (ISO 8601) 	The simulation date. The animation automatically starts an hour after sunset on the specified day.
-fov 	float 	The field of viewin degrees.
-fps 	int 	Frame rate of the output video.
-t 	string 	The title of the video. The video title will be superimposed onto the video.
-ts 	float 	The simulation time span in hours.
-dt 	float 	The time difference between two sucessive frames in seconds.
-o 	string 	The name of the output video file.
-s 	- 	When this flag is specified an instance of VLC will be started once the video is created.

# Example:

The following command will compute the first 2 hours of night sky in Berlin (Germany) on the 25th September of the year 2018. 

python3 kalstar.py -lat 52.5186 -long 13.4083 -t "Look at all the Stars!" \
                   -az 90 -alt 25 -d 2018-09-25 -ts 2 -s -o out.mp4 -fov 70 -dt 30
