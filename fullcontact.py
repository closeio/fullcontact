import argparse
import mongoengine
import re
import requests
import simplejson
from urllib import quote
from urllib2 import urlparse

from models import UserEmailData, UserPhoneData, UserTwitterData, UserFacebookData

mongoengine.connect('fullcontact') # connect to 'fullcontact' DB

FULL_CONTACT_API_KEY = ''

# data_list should be a list of tuples:
# ('type', 'data'), e.g.
# ('email', 'wojcikstefan@gmail.com')
# ('phone', '+48601941311')
# ('twitter', 'stefanwojcik')
# ('facebookUsername', 'wojcikstefan')


def aggregate_data(data_list):
    """
    Given a list of contact data of different type, return all the
    aggregated information that can be found about given contact.

    Arguments:
    data_list -- the list of tuples of contact data in the form (type, data)
    """
    objects = []
    # get all the models
    for data in data_list:
        if data[0] == 'email':
            try:
                objects.append(UserEmailData.objects.get(email=data[1]))
            except UserEmailData.DoesNotExist:
                pass
        elif data[0] == 'phone':
            try:
                objects.append(UserPhoneData.objects.get(phone=data[1]))
            except UserPhoneData.DoesNotExist:
                pass
        elif data[0] == 'twitter':
            try:
                objects.append(UserTwitterData.objects.get(twitter=data[1]))
            except UserTwitterData.DoesNotExist:
                pass
        elif data[0] == 'facebookUsername':
            try:
                objects.append(UserFacebookData.objects.get(facebookUsername=data[1]))
            except UserFacebookData.DoesNotExist:
                pass
    # aggregate the data or return None if nothing found
    if objects:
        userdata = objects[0]
        # pop the status and message information - we don't need that in the response
        userdata.safe_pop('status')
        userdata.safe_pop('message')
        for obj in objects:
            obj.safe_pop('status')
            obj.safe_pop('message')
            userdata.data_dict = merge_dicts(userdata.data_dict, obj.data_dict)
        userdata.title = 'Aggregated Data'
        return userdata
    return None


def merge_dicts(dict1, dict2):
    """
    Go through the dictionary dict2 and add any distinct data
    that could not be found in dict1. If the same keys are found, but
    values differ, merge them into a list.

    Arguments:
    dict1 -- dictionary that you want the data appended to
    dict2 -- dictionary, which data should be appended to dict1 (if distinct)
    """
    for k, v in dict2.items():
        if dict1.get(k): # if dict1 has the key k of dict2
            # if values are dictionaries, use recursion 
            if isinstance(dict1[k], dict):
                dict1[k] = merge_dicts(dict1[k], dict2[k])
            # compare values of keys
            elif dict2[k] != dict1[k]:
                # if value is list, append distinct results from dict2
                if isinstance(dict2[k], list):
                    for item in dict2[k]:
                        if item not in dict1[k]:
                            dict1[k].append(item)
                elif isinstance(dict1[k], list):
                    if dict2[k] not in dict1[k]:
                        dict1[k].append(dict2[k])
                else:
                    dict1[k] = [dict1[k], dict2[k]]
        else:
            dict1[k] = dict2[k]
    return dict1


def batch_lookup(data_list, webhook=None, debug=False):
    """
    Send requests to the Full Contact API and return the status logs of those requests.
    If debug is True, print the logs.

    Arguments:
    data_list -- the list of tuples of contact data in the form (type, data)
    webhook -- url with the callback function that handles responses from Full Contact
    debug -- boolean specifying whether some debug information should be printed to the console.
    """
    # divide the data into chunks of 20 (max number for a single batch request)
    data_chunks = []
    counter = 0
    while counter < len(data_list):
        data_chunks.append(data_list[counter:counter+20])
        counter += 20
    # send the request for each chunk
    process_log = []
    for chunk in data_chunks:
        request_urls = []
        for data in chunk:
            # escape params
            if data:
                data = (quote(data[0].encode('utf-8')), quote(data[1].encode('utf-8')))
                url = 'https://api.fullcontact.com/v2/person.json?%s=%s' % (data)
                if webhook:
                    url += '&webhookUrl=' + webhook + '&webhookId=%s:%s' % (data)
            request_urls.append(url)
        post_data = simplejson.dumps({'requests' : request_urls})
        data = requests.post(
            'https://api.fullcontact.com/v2/batch.json',
            params={'apiKey': FULL_CONTACT_API_KEY},
            headers={'content-type': 'application/json'},
            data=post_data
        ).json
        for person_url, person_json in data['responses'].items():
            log = {}
            params = urlparse.parse_qs(urlparse.urlparse(person_url).query)
            if params.get('email'):
                log['type'] = 'email'
                log['data'] = params['email'][0]
            elif params.get('phone'):
                log['type'] = 'phone'
                log['data'] = params['phone'][0]
            elif params.get('twitter'):
                log['type'] = 'twitter'
                log['data'] = params['twitter'][0]
            elif params.get('facebookUsername'):
                log['type'] = 'facebookUsername'
                log['data'] = params['facebookUsername'][0]
            else:
                log['type'] = 'Wrong data'
                log['data'] = person_url
            log['status'] =  '%s - %s' % (person_json.get('status'),
                                          person_json.get('message'))
            process_log.append(log)
            if debug:
                print log
    return process_log


def emails_from_file(filestream):
    """ Given a filestream, scrape e-mail addresses. """
    emails = []
    mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')  # email regex
    # find all email addresses in csv file and append them to batch_data
    for line in filestream:
        mails = mailsrch.findall(line)
        for mail in mails:
            emails.append(('email', mail))
    return emails


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webhook', help='URL to a callback for delayed Full Contact API response')
    parser.add_argument('-e', '--emails', nargs='+', help='E-mail addresses')
    parser.add_argument('-p', '--phones', nargs='+', help='Phone numbers')
    parser.add_argument('-fb', '--facebooks', nargs='+', help='Facebook usernames')
    parser.add_argument('-t', '--twitters', nargs='+', help='Twitter usernames')
    parser.add_argument('-f', '--file', help='File from which you want e-mail addresses scraped')
    args = parser.parse_args()
    batch_data = []
    if args.file:
        filestream = open(args.file)
        batch_data.extend(emails_from_file(filestream))
        filestream.close()
    if args.emails:
        for email in args.emails:
            batch_data.append(('email', email))
    if args.phones:
        for phone in args.phones:
            batch_data.append(('phone', phone))
    if args.twitters:
        for twitter in args.twitters:
            batch_data.append(('twitter', twitter))
    if args.facebooks:
        for facebook in args.facebooks:
            batch_data.append(('facebookUsername', facebook))
    batch_lookup(batch_data, args.webhook, debug=True)

