import cv2 #sudo apt-get install python-opencv
import numpy as py
import os
import time

# Arducam 5MP camera with autofocus

try:
	import picamera
	from picamera.array import PiRGBArray
except:
	sys.exit(0)


def focusing(val):
	value = (val << 4) & 0x3ff0
	data1 = (value >> 8) & 0x3f
	data2 = value & 0xf0
	os.system("i2cset -y 0 0x0c %d %d" % (data1,data2))
	
def sobel(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Sobel(img_gray,cv2.CV_16U,1,1)
	return cv2.mean(img_sobel)[0]

def laplacian(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Laplacian(img_gray,cv2.CV_16U)
	return cv2.mean(img_sobel)[0]
	

def calculation(camera):
	rawCapture = PiRGBArray(camera) 
	camera.capture(rawCapture, format="bgr", use_video_port=True)
	image = rawCapture.array
	rawCapture.truncate(0)
	return laplacian(image)
	
	
def autoadjustfocus():
    #open camera
	camera = picamera.PiCamera()
	#open camera preview
	camera.start_preview()
	#set camera resolution
	# Ratio: 16:9
	# Max resolution for focusing: 1920x1088
	# Resolutions: 
	# 	1920x1080
	#	2560x1440
	# Faster processing: 640x360
	camera.resolution = (640, 360)

	print("Start focusing")
	
	max_index = 10
	max_value = 0.0
	last_value = 0.0
	dec_count = 0
	focal_distance = 10
	
	while True:
		#Adjust focus
		focusing(focal_distance)
		#Take image and calculate image clarity
		val = calculation(camera)
		#Find the maximum image clarity
		if val > max_value:
			max_index = focal_distance
			max_value = val
			
		#If the image clarity starts to decrease
		if val < last_value:
			dec_count += 1
		else:
			dec_count = 0
		#Image clarity is reduced by six consecutive frames
		if dec_count > 6:
			break
		last_value = val
		
		#Increase the focal distance
		focal_distance += 10
		if focal_distance > 1000:
			print("\nFocus not properly adjusted, validate and try again...\n")
			break

		print("focal dist = %d, max index = %d, max value = %lf, dec count = %d" % (focal_distance, max_index, max_value, dec_count))

    #Adjust focus to the best
	focusing(max_index)
	
	time.sleep(1)
	print("focal dist = %d, max index = %d, max value = %lf" % (focal_distance, max_index, max_value))
		
	camera.stop_preview()
	camera.close()

	print("Focusing completed\n")
		
if __name__ == "__main__":
	autoadjustfocus()
