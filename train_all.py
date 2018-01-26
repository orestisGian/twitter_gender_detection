from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn import svm
from sklearn.model_selection import cross_val_score,cross_validate,StratifiedKFold
from sklearn import metrics
from sklearn import preprocessing
import json
import numpy as np
from neupy import algorithms, environment
import math
import sys
import re
import csv
import xlrd





environment.reproducible()




workbook = xlrd.open_workbook(filename='../create_excel/liu_f_g.xls')
worksheet = workbook.sheet_by_name('data')

rows = 8460
count = 1
male_count = 0
female_count = 0

f_list = []
X_color_list = []
X_face_list = []
X_name_list = []
Y_list = []
g_list = []
g_pr_list = []
g_c_list = []

for row in xrange(1, rows):

	profile_link_color = worksheet.cell(row, 8).value
	facepp_prediction = worksheet.cell(row, 12).value
	genderize_prediction = worksheet.cell(row, 15).value
	genderize_probability = worksheet.cell(row, 14).value
	genderize_count = worksheet.cell(row, 13).value
	

	j = int(profile_link_color[0:2],16)
	k = int(profile_link_color[2:4],16)
	l = int(profile_link_color[4:6],16)
	


	gender = 1 if worksheet.cell(row, 10).value == 'M' else 0
	
	if facepp_prediction == 'M':
		f_list.append(1)
		X_face_list.append([1])
	elif facepp_prediction == 'F':
		f_list.append(0)
		X_face_list.append([0])
	else:
		f_list.append(0.5)
		X_face_list.append([0.5])
		
	if genderize_prediction == 'male':
		g_list.append(1)
		g_pr_list.append(float(genderize_probability))
		g_c_list.append(int(genderize_count))
		pr = float(genderize_probability)
		ct = int(genderize_count)
		X_name_list.append([1,pr,ct])
		
	elif genderize_prediction == 'female':
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
	Y_list.append(gender)
	count+=1
	
X_name = np.array(X_name_list)
X_face = np.array(X_face_list)
X_color = np.array(X_color_list)
Y = np.array(Y_list)



from sklearn.preprocessing import MinMaxScaler,StandardScaler


scaler = StandardScaler()
X_name = scaler.fit_transform(X_name)


acc_sum_color = 0
acc_sum_face = 0
acc_sum_name = 0
acc_sum_hybrid = 0


kf = StratifiedKFold(n_splits=10) 
kf.get_n_splits(X_color,Y) 
X_hybrid = [None]*(8459)
for train_index, test_index in kf.split(X_color,Y):
	 X_color_train, X_color_test = X_color[train_index], X_color[test_index]
	 X_face_train, X_face_test = X_face[train_index], X_face[test_index]
	 X_name_train, X_name_test = X_name[train_index], X_name[test_index]
	 y_train, y_test = Y[train_index], Y[test_index]

	 pnn = algorithms.PNN()
	 pnn.fit(X_color_train, y_train)
	 predicted_color_prob = pnn.predict_proba(X_color_test)
	 
	 	
	 pnn = algorithms.PNN()
	 pnn.fit(X_face_train, y_train)
	 predicted_face_prob = pnn.predict_proba(X_face_test)
	 	 
	 pnn = algorithms.PNN()
	 pnn.fit(X_name_train, y_train)
	 predicted_name_prob = pnn.predict_proba(X_name_test)
	 
	 pos = 0
	 for i in test_index:
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
	 	
	 	
	 	X_hybrid[i]=[out_color,out_face,out_name]
	 	pos+=1



#print X_hybrid




color_clf = algorithms.PNN()
name_clf = algorithms.PNN()
face_clf = algorithms.PNN()
hybrid_clf = algorithms.PNN()

color_clf.fit(X_color, Y)
face_clf.fit(X_face, Y)
name_clf.fit(X_name, Y)
hybrid_clf.fit(X_hybrid, Y)

from sklearn.externals import joblib
joblib.dump(color_clf, 'color_clf.pkl') 
joblib.dump(name_clf, 'name_clf.pkl') 
joblib.dump(face_clf, 'face_clf.pkl') 
joblib.dump(hybrid_clf, 'hybrid_clf.pkl') 

#na kanw train ton hybrid me ta gender numbers twn individual pou vgazoun gia olo to dataset meta to fit se olo to dataset h me cross-validation twn individual?

#a.5-fold cross validation sta CFG gia na vgalw gender numbers gia olh th vash
#b.training toy hybrid me ta gender numbers se olh th vash
#c.training twn CFG se olh th vash























