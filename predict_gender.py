from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn import svm
from sklearn import metrics
from sklearn import preprocessing
import json
import numpy as np
import xlrd
from neupy import algorithms, environment
import math
import sys
import re
import tweepy
import facepp
from facepp import API, File
import genderize
from genderize import Genderize
import string


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
    		#print name
    		theme_color = status.user.profile_link_color
    		#print theme_color
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
	#print names

	try:
		for x in names:
			gen = Genderize(api_key=GENDERIZE_API_KEY).get([x])
			#print gen
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
if len(sys.argv) < 2:
	print 'this script takes at least one twitter ID as argument'
	sys.exit(0)

IDs = []

for i in xrange(1,len(sys.argv)):
	searchObj = re.search( r'^[0-9]+$', sys.argv[i])
	if not searchObj:
		print "Twitter IDs must contain only digits"
		sys.exit(0)
	IDs.append(sys.argv[i])	

f_list = []
X_color_list = []
X_face_list = []
X_name_list = []
Y_list = []
g_list = []
g_pr_list = []
g_c_list = []

for x in IDs:
	ans = tweepy_function(x)	
	#print ans
	if ans:
		(name,image_url,theme_color) = ans
		#Face++	
		facepp_gender = faceplusplus(image_url)
		#Genderize
		(genderize_gender,genderize_count,genderize_probability) = genderize_function(name)
		#print (genderize_gender,genderize_count,genderize_probability)

		j = int(theme_color[0:2],16)
		k = int(theme_color[2:4],16)
		l = int(theme_color[4:6],16)

		if facepp_gender == 'M':
			f_list.append(1)
			X_face_list.append([1])
		elif facepp_gender == 'F':
			f_list.append(0)
			X_face_list.append([0])
		else:
			f_list.append(0.5)
			X_face_list.append([0.5])
	
		if genderize_gender == 'male':
			g_list.append(1)
			g_pr_list.append(float(genderize_probability))
			g_c_list.append(int(genderize_count))
			pr = float(genderize_probability)
			ct = int(genderize_count)
			X_name_list.append([1,pr,ct])
	
		elif genderize_gender == 'female':
			g_list.append(-1)
			g_pr_list.append(float(genderize_probability)*-1)
			g_c_list.append(int(genderize_count)*-1)
			pr = -float(genderize_probability)
			ct = -int(genderize_count)
			X_name_list.append([-1,pr,ct])	

		else:
			g_list.append(0)
			g_pr_list.append(0.0)
			g_c_list.append(0)
			X_name_list.append([0,0,0])		

		X_color_list.append([j,k,l])
	
X_name = np.array(X_name_list)
X_face = np.array(X_face_list)
X_color = np.array(X_color_list)
Y = np.array(Y_list)

from sklearn.preprocessing import MinMaxScaler,StandardScaler


scaler = StandardScaler()
X_name = scaler.fit_transform(X_name)


from sklearn.externals import joblib

color_clf = joblib.load('color_clf.pkl') 
name_clf = joblib.load('name_clf.pkl') 
face_clf = joblib.load('face_clf.pkl') 
hybrid_clf = joblib.load('hybrid_clf.pkl') 

predicted_color_prob = color_clf.predict_proba(X_color)
predicted_face_prob = face_clf.predict_proba(X_face)
predicted_name_prob = name_clf.predict_proba(X_name)

#print predicted_color_prob
#print predicted_face_prob
#print predicted_name_prob


X_hybrid = []
for pos in xrange(len(predicted_color_prob)):
	if math.isnan(predicted_color_prob[pos][0]) or math.isnan(predicted_color_prob[pos][1]):
		out_color = 0.5
	elif predicted_color_prob[pos][0] >= predicted_color_prob[pos][1]:
		out_color = 1 - predicted_color_prob[pos][0]
	else:
		out_color = predicted_color_prob[pos][1]

	if math.isnan(predicted_face_prob[pos][0]) or math.isnan(predicted_face_prob[pos][1]):
		out_face = 0.5	
	elif predicted_face_prob[pos][0] >= predicted_face_prob[pos][1]:
		out_face = 1 - predicted_face_prob[pos][0]
	else:
		out_face = predicted_face_prob[pos][1]
	if math.isnan(predicted_name_prob[pos][0]) or math.isnan(predicted_name_prob[pos][1]):
		out_name = 0.5	
	elif predicted_name_prob[pos][0] >= predicted_name_prob[pos][1]:
		out_name = 1 - predicted_name_prob[pos][0]
	else:
		out_name = predicted_name_prob[pos][1]


	X_hybrid.append([out_color,out_face,out_name])
	#print out_color,out_face,out_name
	
#print X_hybrid
X_hybrid = np.array(X_hybrid)
predicted_hybrid_prob = hybrid_clf.predict_proba(X_hybrid)
#print predicted_hybrid_prob
predictions = []
for i in xrange(len(predicted_hybrid_prob)):
	user = {}
	user['ID'] = IDs[i]
	if math.isnan(predicted_face_prob[i][0]) or math.isnan(predicted_face_prob[i][1]):
		user['gender'] = 'female'
		user['probability'] = 0.5
	if predicted_face_prob[i][0] >= predicted_face_prob[i][1]:
		user['gender'] = 'female'
		user['probability'] = predicted_face_prob[i][0]
	else:
		user['gender'] = 'male'
		user['probability'] = predicted_face_prob[i][1]
	
	predictions.append(user)
		
print predictions
		
		
		
		




