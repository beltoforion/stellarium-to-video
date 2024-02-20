# Stellarium-To-Video
Automatically creating videos of the night sky with [Stellarium](https://stellarium.org) (0.20.4 or higher) and Linux/BSD.
 
This python script will automate the process of creating videos of the night sky with stellarium. It will take an observation position and other observation parameters as command line options and then create a [script](http://beltoforion.de/article.php?a=stellarium_video&hl=en#idStellariumScript) for Stellariums built in scripting engine to compute the animation frames. Once the frames are created the script will invoke ffmpeg to combine the 
frames into an mp4 video file.

For more details please go to the [web page of this project](https://beltoforion.de/en/stellarium_video/)

https://user-images.githubusercontent.com/2202567/184002878-0f915485-8a63-49ae-8221-273f61b2c728.mp4


# Prerequisites:
In order to use this script [Stellarium](https://stellarium.org) and [ffmpeg](https://www.ffmpeg.org/) must be installed. You will also need [vlc](https://www.videolan.org/vlc/) if you want to use the -s option.

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
The simulation date and time as an ISO 8601 compliant string. If the string does not contain a time and the planet is earth the simulation will start at sunset of the given day.

_-fov xx.xxx_ 	
The field of view in degrees.

_-fps xx_ 	
Frame rate of the output video.

_-t abc_ 	
The title of the video. The video title will be superimposed onto the video.

_-ts xx_ 	
The simulation time as an ISO 8601 duration. (i.e. PT2H for two hours)

_-dt xx_ 	
The time difference between two sucessive frames as an ISO 8601 duration (i.e. PT20S for 20 seconds).

_-o abc.mp4_ 
The name of the output video file.

_-s_ 	
When this flag is specified an instance of VLC will be started once the video is created.

# Example:

The following command will compute the first 2 hours of night sky in Berlin (Germany) on the 25th September of the year 2023. 

**python3 kalstar.py** -lat 52.5186 -long 13.4083 -t "Look at all the Stars!" -az 90 -alt 25 -d 2023-09-25 -ts 2 -s -o out.mp4 -fov 70 -dt 30


**python3 kalstar.py** -lat 50.9 -long 13.9 -t "Analemma" -az 180 -alt 35 -d 2024-06-20T12:00:00 -ts P1Y -s -o analemma.mp4 -fov 80 -dt P1D

# Acknowledgements:
This script is using [Skyfield](https://rhodesmill.org/skyfield/) for computing sunset times.
