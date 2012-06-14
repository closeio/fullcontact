import argparse
import mongoengine
import requests
import simplejson

from models import UserEmailData, UserPhoneData, UserTwitterData, UserFacebookData

mongoengine.connect('fullcontact') # connect to 'fullcontact' DB

FULL_CONTACT_API_KEY = 'a869e356aca859d6'

# data_list should be a list of tuples:
# ('type', 'data'), e.g.
# ('email', 'wojcikstefan@gmail.com')
# ('phone', '+48601941311')
# ('twitter', 'stefanwojcik')
# ('facebookUsername', 'wojcikstefan')


def aggregate_data(data_list):
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
    # aggregate the data
    if objects:
        userdata = objects[0]

        for obj in objects:
            userdata.data_dict = merge_dicts(userdata.data_dict, obj.data_dict)
        userdata.title = 'Aggregated Data'
        return userdata
    return None

def merge_dicts(dict1, dict2):
    for k, v in dict2.items():
        if dict1.get(k): # if dict1 has the key k of dict2
            # if values are dictionaries, use recursion 
            if isinstance(dict1[k], dict):
                dict1[k] = merge_dicts(dict1[k], dict2[k])
            # compare values of keys
            elif dict2[k] != dict1[k]:
                # if value is list, append distinct results from dict2
                if isinstance(dict1[k], list):
                    for item in dict2[k]:
                        if item not in dict1[k]:
                            dict1[k].append(item)
                else:
                    dict1[k] = [dict1[k], dict2[k]]
        else:
            dict1[k] = dict2[k]
    return dict1



def batch_lookup(data_list, webhook=None, debug=False):
    # divide the data into chunks of 20 (max number for a single batch request)
    data_chunks = []
    counter = 0
    while counter < len(data_list):
        data_chunks.append(data_list[counter:counter+20])
        counter += 20
    # send the request for each chunk
    for chunk in data_chunks:
        request_urls = []
        for data in chunk:
            url = 'https://api.fullcontact.com/v2/person.json?%s=%s' % data
            if webhook:
                url += '&webhookUrl=' + webhook + '&webhookId=%s:%s' % (data)
            request_urls.append(url)
        print 'URL:', url
        post_data = simplejson.dumps({'requests' : request_urls})
        data = requests.post(
            'https://api.fullcontact.com/v2/batch.json',
            params={'apiKey': FULL_CONTACT_API_KEY},
            headers={'content-type': 'application/json'},
            data=post_data
        ).json

        process_log = []
        for person_url, person_json in data['responses'].items():
            log = {}
            if 'email=' in person_url:
                val = scrape_info_from_url(person_url, 'email=')
                log['type'] = 'E-mail'
                log['data'] = val
            elif 'phone=' in person_url:
                val = scrape_info_from_url(person_url, 'phone=')
                log['type'] = 'Phone'
                log['data'] = val
            elif 'twitter=' in person_url:
                val = scrape_info_from_url(person_url, 'twitter=')
                log['type'] = 'Twitter'
                log['data'] = val
            elif 'facebookUsername=' in person_url:
                val = scrape_info_from_url(person_url, 'facebookUsername=')
                log['type'] = 'Facebook'
                log['data'] = val
            else:
                log['type'] = 'Wrong data'
                log['data'] = person_url
            log['status'] =  '%s - %s' % (person_json.get('status'),
                                          person_json.get('message'))
            process_log.append(log)
        return process_log

def scrape_info_from_url(person_url, info):
    ret_val = person_url[person_url.find(info) + len(info):]
    if ret_val.find('&') != -1:
        ret_val = ret_val[:ret_val.find('&')]
    return ret_val


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webhook', help='URL to a callback for delayed Full Contact API response')
    parser.add_argument('-e', '--emails', nargs='+', help='E-mail addresses')
    parser.add_argument('-p', '--phones', nargs='+', help='Phone numbers')
    parser.add_argument('-fb', '--facebooks', nargs='+', help='Facebook usernames')
    parser.add_argument('-t', '--twitters', nargs='+', help='Twitter usernames')
    parser.add_argument('-f', '--file', help='CSV file with e-mail addresses')
    args = parser.parse_args()
    batch_data = []
    if args.file:
        csv = open(args.file)
        counter = 0
        for line in csv:
            if not line.startswith('id') and line.strip():
                batch_data.append(
                    ('email', line.split(',')[-2].replace('"',''))
                )
        csv.close()
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

