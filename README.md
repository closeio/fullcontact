fullcontact
===========

Requirements
------------

Flask
<code>pip install flask</code>

MongoEngine
<code>pip install mongoengine</code>

Usage
------------

The process consists of 2 parts:

1. Set up Flask server to listen for upcoming Full Contact response.
2. Send the request to Full Contact.


To set up Flask server, run <code>python flask_fullcontact.py</code>. By default,
it runs on http://localhost:5000/ and the webhook callback is at http://localhost:5000/webhook.
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
  -f FILE, --file FILE
        CSV file with e-mail addresses
</pre>

Examples:
* <code>python fullcontact.py -e address@one.com address@two.com -w url_to_webhook</code>
* <code>python fullcontact.py -f csv_with_emails.csv -w url_to_webhook</code>

To use the fullcontact.py API, do:

<pre>
<code>
from fullcontact import batch_lookup
...
list_of_emails = ['address@one.com', 'address@two.com', ...]
batch_lookup(list_of_emails, url_to_webhook)
</code>
</pre>

