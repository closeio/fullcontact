fullcontact
===========

Requirements
------------

Flask
<code>pip install flask</code>

MongoEngine
<code>pip install mongoengine</code>

WTForms
<code>pip install wtforms</code>


Usage
------------

The process consists of 2 parts:

1. Set up Flask server to listen for upcoming Full Contact response.
2. Send the request to Full Contact.


To set up Flask server, run <code>python flask_fullcontact.py</code>. By default,
it runs on http://localhost:5000/ and the webhook callback is at http://localhost:5000/webhook/.
When testing, you can use <i>proxylocal</i> (http://proxylocal.com/) to make localhost visible
to the outside world.


To request the Full Contact info about some e-mail(s), you can either run the
fullcontact.py from terminal, or use a <i>batch_lookup</i> function from its API.

To request the data from the terminal, use <code>python fullcontact.py</code> 
with additional arguments.

<pre>
   usage: fullcontact.py [-h] [-w WEBHOOK] [-e EMAILS [EMAILS ...]] [-f FILE]

  -h, --help            
        show this help message and exit
  -w WEBHOOK, --webhook webhook
        URL to a callback for delayed Full Contact API response
  -e EMAILS [EMAILS ...], --emails EMAILS [EMAILS ...]
        E-mail addresses to look up
  -p PHONES [PHONES ...], --phones PHONES [PHONES ...]
        Phone numbers
  -t TWITTERS [TWITTERS ...], --twitters TWITTERS [TWITTERS ...]
        Twitter usernames
  -fb FACEBOOKS [FACEBOOKS ...], --facebooks FACEBOOKS [FACEBOOKS ...]
        Facebook usernames
  -f FILE, --file FILE
        CSV file with e-mail addresses
</pre>

Examples:
* <code>python fullcontact.py -e address@one.com address@two.com -w url_to_webhook</code>
* <code>python fullcontact.py -f csv_with_emails.csv -w url_to_webhook</code>
* <code>python fullcontact.py -e address@mail.com -p +13037170414 -fb fb_username -w url_to_webhook</code>

To use the fullcontact.py API, you use lists of tuples (type, data) for both lookup request and data retrieval from DB.

Type can be have one of the following values:
* 'email'
* 'phone'
* 'twitter'
* 'facebookUsername'

<pre>
<code>
from fullcontact import aggregate_data, batch_lookup
...
data_list = [
    ('email', 'address@one.com'),
    ('email', 'address@two.com'),
    ('phone', '+13037170414'),
    ('twitter', 'twitter_username'),
    ('facebookUsername', 'fb_username')
]
# to request separate information about every piece of data (and get logs in return)
response_logs = batch_lookup(data_list, url_to_webhook)
# to get aggregated information about all the pieces of data
userdata = aggregate_data(data_list)
</code>
</pre>

Testing
---------------

There is a test.py file included for testing purposes. Before you run it, make sure the Flask server is
working and is public via <i>proxylocal</i>

<pre>
<code>
python flask_fullcontact.py
proxylocal 5000 --host fullcontact
python test.py
</code>
</pre>
