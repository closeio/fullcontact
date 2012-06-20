import requests
import simplejson
import time
from fullcontact import emails_from_file


def test():
    api_url = 'http://fullcontact.t.proxylocal.com/api/'
    api_get_list_url = 'http://fullcontact.t.proxylocal.com/api/get-list/'
    # get emails from file
    filestream = open('emails_test.csv')
    data = emails_from_file(filestream)
    # post request for lookup
    print 'REQUEST DATA LOOKUP'
    response = requests.post(
        api_url,
        headers={'content-type': 'application/json'},
        data=simplejson.dumps({'data': data})
    ).json
    print 'LOGS\n', response
    # wait for sufficient time 
    print '\nWAIT FOR 30 SECONDS...\n'
    time.sleep(30)
    # get the aggregated data for one contact
    print 'Get the aggregated data as if first 3 emails belonged to one person'
    data_for_get = {'email': ','.join([data_tuple[1] for data_tuple in data[:3]])}
    response = requests.get(
        api_url,
        headers={'content-type': 'application/json'},
        params=data_for_get
    ).json
    print 'RESPONSE\n', response
    # get the list of aggregated data for all emails grouped as if each contact
    # owned 3 consecutive email addresses
    print 'Get the aggregated data as if each contact owned 3 consecutive emails'
    data_for_list_get = []
    counter = 0
    while counter < len(data):
        data_for_list_get.append(data[counter:counter+3])
        counter += 3
    response = requests.post(
        api_get_list_url,
        headers={'content-type': 'application/json'},
        data=simplejson.dumps({'data': data_for_list_get})
    ).json
    print 'RESPONSE\n', response


if __name__ == '__main__':
    test()
