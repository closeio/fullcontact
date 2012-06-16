import requests
import simplejson
import time
from fullcontact import emails_from_file


def test():
    get_url = 'http://fullcontact.t.proxylocal.com/get.json'
    post_url = 'http://fullcontact.t.proxylocal.com/post.json'
    # get emails from file
    filestream = open('emails_test.csv')
    data = emails_from_file(filestream)
    # build the post request
    print 'REQUEST DATA LOOKUP'
    response = requests.post(
        post_url,
        headers={'content-type': 'application/json'},
        data=simplejson.dumps({'data': data})
    ).json
    print 'LOGS\n', response
    # wait for sufficient time 
    print '\nWAIT FOR 30 SECONDS...\n'
    time.sleep(30)
    # get the data
    print 'Get the aggregated data'
    response = requests.post(
        get_url,
        headers={'content-type': 'application/json'},
        data=simplejson.dumps({'data': data})
    ).json
    print 'RESPONSE\n', response


if __name__ == '__main__':
    test()
