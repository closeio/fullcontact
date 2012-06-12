import mongoengine
import requests
import sys
from models import UserDataDict

FULL_CONTACT_API_KEY = '7c9834fccb1df3fb'


def lookup(email):
    mongoengine.connect('fullcontact')  # connect to 'fullcontact' DB
    #url = 'https://api.fullcontact.com/v2/person.json?email=%s&apiKey=%s' % (email, FULL_CONTACT_API_KEY)
    data = requests.get(
        'https://api.fullcontact.com/v2/person.json',
        params={'email': email, 'apiKey': FULL_CONTACT_API_KEY}
    ).json
    #data = simplejson.loads(urlopen(url).read())
    # check if there's given e-mail has already been looked up
    # if so, update it; if not, create a new user data
    try:
        userdata = UserDataDict.objects.get(email=email)
        print 'Updating %s' % (email)
        userdata.data_dict = data
        userdata.save()
    except UserDataDict.DoesNotExist:
        print 'Creating %s' % (email)
        userdatadict = UserDataDict(email=email, data_dict=data)
        userdatadict.save()
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        lookup(sys.argv[1])
    else:
        print 'Usage:\n\tfullcontact.py email_address'

