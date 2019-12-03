import cv2
import numpy as np 
import os
import requests
import time
from datetime import datetime
import wget
from PIL import Image
from imutils.video import VideoStream

subjects = ["", "Anderson", "And", "x"]


fname = "trainer/trainer.yml"
API_BASE = 'https://vemvai.stopplay.io/'
API_ENDPOINT = 'api/school/log_enter_exit/'
user = 'mpbear'
passw = 'wordpass123'
matched = []
url = 'http://vemvai.stopplay.io/mediafiles/yml/trainer.yml'
ip_camera_rtsp = 'rtsp://192.168.1.6:554/user=admin&password=admin&channel=1&stream=0.sdp?'



if not os.path.isfile(fname):

	print("Downloading data...")
	wget.download(url, fname)
	#exit(0)

face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

#using ip camera
#insert the rtsp or http ip here
cap = VideoStream(src=ip_camera_rtsp).start()
#cap = VideoStream('rtsp://192.168.1.3:8080/h264_pcm.sdp') #cellphone camera rtsp
#using webcam
#cap = cv2.VideoCapture(0)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(fname)


while True:  #sorry god of computers for that

	#cv2.VideoCapture.grab(cap)
	#cv2.VideoCapture.retrieve(cap)	
	img = cap.read()
	#reduce J to make the 'acess granted' message faster
	j        = 80 #a time constant to works with frames
	blurred_img = cv2.GaussianBlur(img, (21, 21), 0)
	gray     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#1.4 and 2 was  good
	cv2.resize(gray, (300, 300), interpolation=cv2.INTER_LINEAR)

	faces    = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80,80))
	out = img.copy()

	for(x,y,w,h) in faces:	
		##adding the blur
		#cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)


		ids, conf = recognizer.predict(gray[y: y + h, x: x + w])

		if conf < 50:
			#subjects[] it's the array with the students name
			#ids are the integer identification of every student
			#the code it's like this because the opencv work with integer identification only so we need a table with students information
			#print(conf)
			name = subjects[ids]
			#print(name)
			#cv2.VideoCapture.grab(cap)
			#(x+2, y + h - 5)
			cv2.putText(img, name, (x + 2, y + h - 5), cv2.FONT_HERSHEY_DUPLEX, 2, (150,255,0), 2, lineType=cv2.LINE_AA)			
			mask = np.zeros((480, 704, 3), dtype=np.uint8)
			mask = cv2.rectangle(mask, (x, y), (x + w, y+h), (255, 255, 255), -1)
			out = np.where(mask == np.array([255,255,255]), img, blurred_img)
			##end of blur
			if ids not in matched:

				matched.append(ids) #adds the matched studetn on the matched list

				#sending to server
				myobj = {"log_type": "ENTER", "child": ids}
				r = requests.post(url = API_BASE + API_ENDPOINT, data = myobj , auth = (user, passw))
				print(r.status_code)
				

				while j >= 1:					

					#ret, img = cap.read()

					if j%1 == 0:
						cv2.putText(img, "Acess Granted!" , (0, 480), cv2.FONT_HERSHEY_DUPLEX, 3, (150,255,0), 2, lineType=cv2.LINE_AA)
									
					cv2.imshow("MapleBear Joao Pessoa Facial Recognition", img)
					cv2.waitKey(5)
					j = j - 1

				#cv2.VideoCapture.grab(cap)
				#time.sleep(1)

			elif ids in matched:
				cv2.putText(img, "Matched, move on!" , (0, 440), cv2.FONT_HERSHEY_DUPLEX, 1, (150,255,0), 2, lineType=cv2.LINE_AA)



			

			#sending to server
			#r = requests.post(url = API_BASE + API_ENDPOINT + str(ids), auth = (user, passw))
			#pastebin_url = r.text
			#print(r.status_code)
			#print(pastebin_url)

		else:
			#subjects[] its the array with the students name
			#ids are the integer identification of every student
			#the code it's like this because the opencv work with integer identification only so we need a table with students information

			name = subjects[ids]
			cv2.putText(img, 'Matching...', (x + 2, y + h - 5), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, lineType=cv2.LINE_AA)


	cv2.imshow('MapleBear Joao Pessoa Facial Recognition', out)		


	
	
	
	#cv2.imshow('MapleBear Joao Pessoa Facial Recognition', img)		
	k = cv2.waitKey(5) & 0xff
	if k == 27:
		break

cap.stop()
cv2.destroyAllWindows()
del matched[:]


