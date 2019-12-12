import cv2
import numpy as np 
import os
import requests
import time
from datetime import datetime
import wget
from PIL import Image
from imutils.video import VideoStream


fname = "trainer/trainer.yml"
API_BASE = 'https://vemvai.stopplay.io/'
API_ENDPOINT = 'api/school/log_enter_exit/'
user = 'mpbear'
passw = 'wordpass123'
matched = []
url = 'http://vemvai.stopplay.io/mediafiles/yml/trainer.yml'
ip_camera_rtsp = 'rtsp://192.168.1.8:554/user=admin&password=admin&channel=1&stream=0.sdp?'


if not os.path.isfile(fname):

	print("Downloading data...")
	wget.download(url, fname)
	#exit(0)

face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

#using ip camera
#insert the rtsp or http ip here
cap = VideoStream(src=ip_camera_rtsp).start()

#using webcam
#cap = cv2.VideoCapture(0)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(fname)


while True:  #sorry god of computers for that
	unity = 1
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


		#cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)


		ids, conf = recognizer.predict(gray[y: y + h, x: x + w])

		if conf < 50:

			req = requests.get(API_BASE + f'api/child/inschool/{str(ids)}/', auth = (user, passw))
			#print(req.status_code)
			json = req.json()
			name = json['name']
			#ading the blur 
			cv2.putText(img, name, (x + 2, y + h - 5), cv2.FONT_HERSHEY_DUPLEX, 2, (150,255,0), 2, lineType=cv2.LINE_AA)			
			mask = np.zeros((480, 704, 3), dtype=np.uint8)
			mask = cv2.rectangle(mask, (x, y), (x + w, y+h), (255, 255, 255), -1)
			out = np.where(mask == np.array([255,255,255]), img, blurred_img)


			if json['in_school'] == False: 

				#sending to server
				myobj = {"log_type": "ENTER", "child": ids}
				r = requests.post(url = API_BASE + API_ENDPOINT, data = myobj , auth = (user, passw))
				print(r.status_code)
				Pil_img = Image.fromarray(orig)
				img_numpy = np.array(Pil_img, 'uint8')
				crop_img = img_numpy[y: y + h, x: x + w]
				p = requests.post(url = API_BASE + "api/child/" + str(ids) + "/add_image/", auth = (user, passw))
				print("p " + str(p.status_code))				

				while j >= 1:					

					#ret, img = cap.read()

					if j%1 == 0:
						cv2.putText(img, "Acess Granted!" , (0, 480), cv2.FONT_HERSHEY_DUPLEX, 3, (150,255,0), 2, lineType=cv2.LINE_AA)
									
					cv2.imshow("MapleBear Joao Pessoa Facial Recognition", img)
					cv2.waitKey(5)
					j = j - 1

				#cv2.VideoCapture.grab(cap)
				#time.sleep(1)
			elif json['in_school'] == True:
				cv2.putText(img, "Matched, move on!" , (0, 440), cv2.FONT_HERSHEY_DUPLEX, 1, (150,255,0), 2, lineType=cv2.LINE_AA)

		else:

			cv2.putText(img, 'Matching...', (x + 2, y + h - 5), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, lineType=cv2.LINE_AA)


	cv2.imshow('MapleBear Joao Pessoa Facial Recognition', out)		


	
	
	
	#cv2.imshow('MapleBear Joao Pessoa Facial Recognition', img)		
	k = cv2.waitKey(5) & 0xff
	if k == 27:
		break

cap.stop()
cv2.destroyAllWindows()
del matched[:]


