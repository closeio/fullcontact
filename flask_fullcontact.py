import mongoengine
import simplejson

from flask import Flask, request, render_template, url_for
from bson import json_util
from forms import ContactForm
from models import UserEmailData, UserPhoneData, UserTwitterData, UserFacebookData
from fullcontact import aggregate_data, batch_lookup, emails_from_file

app = Flask(__name__)

mongoengine.connect('fullcontact')


@app.route('/')
@app.route('/get-data/')
def get_home():
    form = ContactForm()
    return render_template('get.html', form=form, in_get=True)

@app.route('/request-data/')
def post_home():
    form = ContactForm()
    return render_template('post.html', form=form, in_post=True)

@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        form =  ContactForm(request.args)
        if form.validate():
            query = []
            if form.email:
                query.append(('email', form.email.data))
            if form.phone:
                query.append(('phone', form.phone.data.replace('+','')))
            if form.twitter:
                query.append(('twitter', form.twitter.data))
            if form.facebook:
                query.append(('facebookUsername', form.facebook.data))
            userdata = aggregate_data(query)
            return render_template('results/get_results.html', ud=userdata)
    elif request.method == 'POST':
        if request.files.get('file'):
            # get emails from file, if one was uploaded
            batch_data = emails_from_file(request.files.get('file'))
        else:
            batch_data = request.form.get('batch_data')
            if batch_data:
                batch_data = batch_data.replace('facebook', 'facebookUsername').split(',')
                for i in range(len(batch_data)):
                    batch_data[i] = tuple(batch_data[i].split(':'))
        if batch_data:
            response = batch_lookup(batch_data, request.url_root + url_for('webhook')[1:])
        else:
            response = ["Nothing to process"]
        return render_template('results/post_results.html', response=response)


@app.route('/webhook/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        contacttype, contact = request.form['webhookId'].split(':')
        contact = contact.strip()
        data_dict = simplejson.loads(request.form.get('result'))
        if app.debug:
            print 'RECEIVED ', contacttype, ':', contact
        if contacttype == 'email':
            try:
                userdata = UserEmailData.objects.get(email=contact)
            except UserEmailData.DoesNotExist:
                userdata = UserEmailData(email=contact)
        elif contacttype == 'phone':
            try:
                userdata = UserPhoneData.objects.get(phone=contact)
            except UserPhoneData.DoesNotExist:
                userdata = UserPhoneData(phone=contact)
        elif contacttype == 'twitter':
            try:
                userdata = UserTwitterData.objects.get(twitter=contact)
            except UserTwitterData.DoesNotExist:
                userdata = UserTwitterData(twitter=contact)
        elif contacttype == 'facebookUsername':
            try:
                userdata = UserFacebookData.objects.get(facebookUsername=contact)
            except UserFacebookData.DoesNotExist:
                userdata = UserFacebookData(facebookUsername=contact)
        userdata.data_dict = data_dict
        userdata.save()
        if app.debug:
            print 'Account (%s): %s' % (contacttype, contact)
            print 'Status:', data_dict.get('status')
        return "Thanks a lot"

@app.route('/api/', methods=['GET', 'POST'])
def api():
    """ 
    Return the aggregated result for data sent in GET request or 
    send a request to Full Contact API for POST request.
    """
    if request.method == 'POST':
        # request data from Full Contact API
        data_list = request.json.get('data')
        logs = batch_lookup(data_list, request.url_root + url_for('webhook')[1:])
        return simplejson.dumps(logs)
    elif request.method == 'GET' and request.args.items():
        data_list = request.args.items()
        # split the arguments of the same type (separated by comma in GET request)
        for i in range(len(data_list)):
            if len(data_list[i][1].split(',')) > 1:
                data_type = data_list[i][0]
                for data_value in data_list[i][1].split(','):
                    data_list.append((data_type, data_value))
                data_list.pop(i)
        # aggregate the results and return
        userdata = aggregate_data(data_list)
        if userdata:
            return simplejson.dumps(userdata.data_dict, default=json_util.default)
        return '{}'  # empty dictionary

@app.route('/api/get-list/', methods=['POST'])
def get_list():
    """
    Get a list of contact data sets (JSON) in POST message and return the
    aggregated results for each set.
    """
    print 'RECEIVED', request.json.get('data')
    data_lists = request.json.get('data')
    userdata = []
    for data_list in data_lists:
        userdata.append(aggregate_data(data_list).data_dict)
    if userdata:
        return simplejson.dumps(userdata, default=json_util.default)
    return '[]'  # empty list


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')

