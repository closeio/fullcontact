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

The process consists of 2 main operations:

1. Set up Flask server to listen for upcoming Full Contact response.
2. Send the request to Full Contact.


To set up Flask server, run <code>python flask_fullcontact.py</code>. By default,
it runs on http://localhost:5000/ and the webhook callback is at http://localhost:5000/webhook.
When testing, you can use <i>proxylocal</i> to make localhost visible to the outside world.


To request the Full Contact info about some e-mail(s), you can either run the
fullcontact.py from terminal, or use a <i>batch_lookup</i> function from its API.

To request the data from the terminal, use <code>python fullcontact.py</code> 
with additional arguments.

<code>
usage: fullcontact.py [-h] [-w WEBHOOK] [-e EMAILS [EMAILS ...]] [-f FILE]
</code>
optional arguments:
  * -h, --help            
        show this help message and exit
  * -w WEBHOOK, --webhook WEBHOOK
        URL to a callback for delayed Full Contact API response
  * -e EMAILS [EMAILS ...], --emails EMAILS [EMAILS ...]
        E-mail addresses to look up
  * -f FILE, --file FILE  
        CSV file with e-mail addresses

Examples:
* <code>python fullcontact.py -e some_address@domain.com -w url_to_webhook</code>
* <code>python fullcontact.py -f csv_with_emails -w url_to_webhook</code>

To use the fullcontact.py API, do:

<pre>
<code>
from fullcontact import batch_lookup
...
batch_lookup(list_of_email_addresses, url_to_webhook)
</code>
</pre>

