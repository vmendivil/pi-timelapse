from picamera import PiCamera
import errno
import os
import sys
import threading
from datetime import datetime
from time import sleep
import yaml
import autofocus

config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0

startHour = config['startHour']
startMinute = config['startMinute']
endHour = config['endHour']
endMinute = config['endMinute']
enableTimeframe = config['enableTimeframe']


def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
        print("\nDirectory created: {}\n".format(dir))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_camera_options(camera):
    # Set camera resolution.
    if config['resolution']:
        camera.resolution = (
            config['resolution']['width'],
            config['resolution']['height']
        )
    
    # Set ISO.
    if config['iso']:
        camera.iso = config['iso']

    # Set shutter speed.
    if config['shutter_speed']:
        camera.shutter_speed = config['shutter_speed']
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)
        camera.exposure_mode = 'off'

    # Set white balance.
    if config['white_balance']:
        camera.awb_mode = 'off'
        camera.awb_gains = (
            config['white_balance']['red_gain'],
            config['white_balance']['blue_gain']
        )

    # Set camera rotation
    if config['rotation']:
        camera.rotation = config['rotation']

    return camera


def create_timelapse_media():
    # Create an animated gif (Requires ImageMagick).
    if config['create_gif']:
        print ("\nCreating animated gif.\n")
        os.system('convert -delay 10 -loop 0 ' + dir + '/image-*.jpg ' + dir + '/timelapse.gif') 

    # Create a video (Requires ffmpeg).
    if config['create_video']:
        print ("\nCreating video.\n")
        os.system('ffmpeg -framerate 10 -i ' + dir + '/image-%05d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')


def isLapseTimeHoursValid():
    # Determine if current time is within range to take pictures
    now = datetime.now().timetz()

    def isStartTimeValid():
        if startHour == now.hour:
            return startMinute <= now.minute
        else:
            return startHour < now.hour

    def isEndTimeValid():
        if now.hour == endHour:
            return now.minute <= endMinute
        else:
            return now.hour < endHour

    return not enableTimeframe or (enableTimeframe and isStartTimeValid() and isEndTimeValid())


def capture_image():
    try:
        global image_number

        # Set a timer to take another picture at the proper interval after this picture is taken
        if (image_number < (config['total_images'])):
            
            # Validate timeframe is valid
            while not isLapseTimeHoursValid():
                print ("Timelapse on hold at: {}".format(datetime.now()))
                sleep(config['waitingPeriod'])

            # Sleep and call "new" thread
            threading.Timer(config['interval'], capture_image).start() # TODO: This generates new thread?

            # Update counter
            image_number += 1

            now = datetime.now()
            print("{} of {} at {}".format(image_number, config['total_images'], now.strftime("%Y-%m-%d %H:%M:%S")))

            # Start up the camera.
            camera = PiCamera()
            set_camera_options(camera)

            # Capture a picture.
            camera.capture(dir + '/image-{0:05d}.jpg'.format(image_number))
            camera.close()
        else: # TODO: Fix the fact of possible multiple threads and move below code at the end of the file
            print ("\nTime-lapse capture complete!\n")
            # TODO: This doesn't pop user into the except block below :(.
            create_timelapse_media()
            sys.exit()

    except (KeyboardInterrupt, SystemExit):
        print ("\nTime-lapse capture terminated.\n")


# Create directory based on current timestamp.
dir = os.path.join(
    sys.path[0],
    'Timelapse-' + datetime.now().strftime('%Y%m%d_%H%M%S')
)

# Kick off the capture process.
print ("\nTime-lapse capture started!\n")
print ("\nResolution: {}x{}\n\n".format(config['resolution']['width'],config['resolution']['height']))

create_timestamped_dir(dir)
autofocus.autoadjustfocus()
capture_image()
