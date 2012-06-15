import mongoengine
import simplejson
from flask import Flask, request, render_template

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
            print 'FILES', request.files
            batch_data = emails_from_file(request.files.get('file'))
            print batch_data
        else:
            batch_data = request.form.get('batch_data')
            if batch_data:
                batch_data = batch_data.replace('facebook', 'facebookUsername').split(',')
                for i in range(len(batch_data)):
                    batch_data[i] = tuple(batch_data[i].split(':'))
        if batch_data:
            response = batch_lookup(batch_data, request.url_root+'webhook/')
        else:
            response = ["Nothing to process"]
        return render_template('results/post_results.html', response=response)


@app.route('/webhook/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        contacttype, contact = request.form['webhookId'].split(':')
        contact = contact.strip()
        data_dict = simplejson.loads(request.form.get('result'))
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
        print 'Account (%s): %s' % (contacttype, contact)
        print 'Status:', data_dict.get('status')
        return "Thanks a lot"


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')

