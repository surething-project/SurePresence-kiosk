from time import sleep

from PIL import Image
#import zbarlight
import os
import base64

file_path = "./images/qr/qr.png"
bad_file_path = "./images/qr/bad.png"

def readQRCode():
	while True:
		sleep(1)
		os.system('raspistill -t 500 -o ./images/qr/qr.png')
		#for now we will use always the same image
		with open(file_path, 'rb') as image_file:
			image = Image.open(image_file)
			image.load()
		#codes = zbarlight.scan_codes(['qrcode'], image)
		codes = None
		if(codes is not None):
			print(codes)
			print(codes[0])
			result = base64.b64decode(codes[0])
			print(result)
			return result
			
#readQRCode()
