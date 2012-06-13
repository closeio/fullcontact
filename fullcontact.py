import argparse
import mongoengine
import requests
import simplejson

mongoengine.connect('fullcontact') # connect to 'fullcontact' DB

FULL_CONTACT_API_KEY = 'a869e356aca859d6'


def batch_lookup(emails_list, webhook=None):
    # divide the emails into chunks of 20 (max number for a single batch request)
    email_chunks = []
    counter = 0
    while counter < len(emails_list):
        email_chunks.append(emails_list[counter:counter+20])
        counter += 20
    # send the request for each chunk
    for chunk in email_chunks:
        request_urls = []
        for email in chunk:
            url = 'https://api.fullcontact.com/v2/person.json?email=%s' % (email)
            if webhook:
                url += '&webhookUrl=' + webhook + '&webhookId=' + email
            request_urls.append(url)
        post_data = simplejson.dumps({'requests' : request_urls})
        data = requests.post(
            'https://api.fullcontact.com/v2/batch.json',
            params={'apiKey': FULL_CONTACT_API_KEY},
            headers={'content-type': 'application/json'},
            data=post_data
        ).json
        for person_url, person_json in data['responses'].items():
            email = person_url[person_url.find('email=') + 6:]
            if email.find('&') != -1:
                email = email[:email.find('&')]
            print 'Email: %s' % (email)
            print 'Status: %s - %s' % (person_json.get('status'),
                                       person_json.get('message'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webhook', help='URL to a callback for delayed Full Contact API response')
    parser.add_argument('-e', '--emails', nargs='+', help='E-mail addresses to look up')
    parser.add_argument('-f', '--file', help='CSV file with e-mail addresses')
    args = parser.parse_args()
    if args.file:
        emails = []
        csv = open(args.file)
        counter = 0
        for line in csv:
            if not line.startswith('id') and line.strip():
                emails.append(line.split(',')[-2].replace('"',''))
        csv.close()
        batch_lookup(emails, args.webhook)
    else:
        batch_lookup(args.emails, args.webhook)

