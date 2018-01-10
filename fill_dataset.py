import json
import csv
import sys
import time
import tweepy
import string


#Tweepy Authentication
auth = tweepy.OAuthHandler('OoAnzGZoyHvjKcS29w9nRD9bF', 'uTPvvPgUBJ92TGuOkDJqu9XZZdyt495QHYhxaOtOJatc78wsaA')
auth.set_access_token('871785994844086274-7gbBEaw6ePbMUOFFlOc7798Bdu4QQDD', '8etB67tfH9jxbRpZgyjDbIvavS1JzXPO5NUY3PprBlmXL')
api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

#utility function to convert image to higher resolution
def hq_image(image_url):
	return string.replace(image_url,'normal','400x400')

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

with open('labels.json') as json_data:
    d = json.load(json_data)
    

with open('dataset.csv', 'wb') as csvfile:
    fieldnames = ['ID', 'gender', 'display_name', 'image_url','theme_color', 'faceplusplus_gender',
    'genderize_gender', 'genderize_count','genderize_probability']
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for ID, gender in d.iteritems(): #python 2.x https://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops
    
    	#testing with a few users
    	count +=1
    	print count
    	if count==21:
    		break
    		
    	for status in limit_handled(tweepy.Cursor(api.user_timeline,user_id=ID).items()):
			name = status.user.name.encode('UTF-8')
			print name
			theme_color = status.user.profile_link_color
			print theme_color
			image_url = hq_image(status.user.profile_image_url_https)
			writer.writerow({'ID': ID, 'gender': gender, 'display_name': name, 'image_url': image_url, 'theme_color': theme_color})
			break #we don't need info from more tweets
			
		
		



        	




	


	
	



		
