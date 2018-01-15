# -*- coding: utf-8 -*-

import json
import csv
import sys
import time
import tweepy
import string
from time import sleep
import facepp
from facepp import API, File
import genderize
from genderize import Genderize
import re
import os





#Tweepy Authentication
auth = tweepy.OAuthHandler('OoAnzGZoyHvjKcS29w9nRD9bF', 'uTPvvPgUBJ92TGuOkDJqu9XZZdyt495QHYhxaOtOJatc78wsaA')
auth.set_access_token('871785994844086274-7gbBEaw6ePbMUOFFlOc7798Bdu4QQDD', '8etB67tfH9jxbRpZgyjDbIvavS1JzXPO5NUY3PprBlmXL')
tweepy_api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#limit handler for Tweepy
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
        	print 'Rate Limit Error'
        	time.sleep(15 * 60)
        except tweepy.error.TweepError:
        	break

#Tweepy API
def tweepy_function(ID):
	for status in limit_handled(tweepy.Cursor(tweepy_api.user_timeline,user_id=ID).items()):
    		name = status.user.name.encode('UTF-8')
    		print name
    		theme_color = status.user.profile_link_color
    		print theme_color
    		image_url = hq_image(status.user.profile_image_url_https)
    		return (name,image_url,theme_color)
	return False



#Face++ Authentication
FACE_API_KEY = "pJUlY8EZZunbUM3SMf6Bi1GCV2SiLJHn"
FACE_API_SECRET = "QnvtLsBqBtrs8R3EcThoE-0BuH77lq_i"
api_server_international = 'https://api-us.faceplusplus.com/facepp/v3/'
faceplusplus_api = API(FACE_API_KEY, FACE_API_SECRET, srv=api_server_international)

#Face++ Detect API
def faceplusplus(image_url):
	if image_url == 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png':
		return 'unknown'
	try:
		res = faceplusplus_api.detect(image_url=image_url,return_attributes='gender')
		faces = res['faces']
		if not faces:
			return 'unknown'
		else:
			has_male = False
			has_female = False
			for face in faces:
				gender = face['attributes']['gender']['value']
				if gender == 'Male':
					has_male = True
				else:
					has_female = True
			if has_male and has_female:
				return 'unknown'
			elif has_male:
				return 'M'
			else:
				return 'F'
	except facepp.APIError as w:
		print w
		return 'error'
	except KeyError:
		print res
		return 'error'

#Genderize Authentication
GENDERIZE_API_KEY = '05af3ca440ee015e12fbef78d8365685'

#Genderize API
def genderize_function(name):
	#lowercase
	name = name.lower()
	regex = re.compile('[^a-z ]')
	#removal of all non-letters	
	name = regex.sub('', name)
	#names = name.split()
	names = name.split()
	print names

	try:
		for x in names:
			gen = Genderize(api_key=GENDERIZE_API_KEY).get([x])
			print gen
			if gen[0]['gender'] != None:
				return (gen[0]['gender'],gen[0]['count'],gen[0]['probability'])
		return ('unknown','unknown','unknown')
	except genderize.GenderizeException:
		pass
		#book.save("liu_f_g1.xls")



#utility function to convert image to higher resolution
def hq_image(image_url):
	return string.replace(image_url,'normal','400x400')


        	
        	


#check command line arguments
if len(sys.argv) != 2:
	print 'this script takes one argument: ground truth dataset'
	sys.exit(0)
	
ground_truth = str(sys.argv[1])
searchObj = re.search( r'(.+)\.json', ground_truth)
if searchObj:
   dataset_name = searchObj.group(1)
else:
   print "Input must be a json file of format: {name}.json"
   sys.exit(0)
   


#search if csv file already exists.if it exists we grab the parsed users' IDs and continue with the remaining users
dataset_exists = False
for file in os.listdir("."):
    if file.endswith(".csv"):
        if dataset_name == file[:-4]:
        	dataset_exists = True
        	break

parsedIDs = []
if dataset_exists:
	with open(dataset_name+'.csv') as csvread:
		 reader = csv.DictReader(csvread)
		 for row in reader:
		     parsedIDs.append(row['ID'])



with open(ground_truth) as json_data:
    d = json.load(json_data)
 
	   

with open(dataset_name+'.csv', 'ab') as csvfile:
    fieldnames = ['ID', 'gender', 'display_name', 'image_url','theme_color', 'faceplusplus_gender',
    'genderize_gender', 'genderize_count','genderize_probability']
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not dataset_exists:
    	writer.writeheader()
    count = 0

    
    for ID, gender in d.iteritems(): #python 2.x https://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops
    	if ID in parsedIDs:
    		continue
    	#testing with a few users
    	count +=1
    	print count
    	if count==500:
    		break
    	
		#TODO:kanei request sto tweepy gia aytous pou den htan prosvasimoi kathe fora pou ksanaksekinaei h diadikasia
    	ans = tweepy_function(ID)	
    	print ans
    	if ans:
			(name,image_url,theme_color) = ans
			#Face++	
			faceplusplus_gender = faceplusplus(image_url)
			#Genderize
			(genderize_gender,genderize_count,genderize_probability) = genderize_function(name)
			print (genderize_gender,genderize_count,genderize_probability)
			#save user info
			writer.writerow({'ID': ID, 'gender': gender, 'display_name': name, 'image_url': image_url, 'theme_color': theme_color,
			'faceplusplus_gender': faceplusplus_gender, 'genderize_gender': genderize_gender , 'genderize_count': genderize_count 
			, 'genderize_probability': genderize_probability})
    
	


	
		
		






        	




	


	
	



		
