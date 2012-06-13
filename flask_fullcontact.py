import mongoengine
import simplejson
from flask import Flask, request, render_template

from forms import ContactForm
from models import UserDataDict

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
            objects = []
            if form.email:
                try:
                    objects.append(UserDataDict.objects.get(email=form.email.data,
                                                            data_dict__status=200))
                except UserDataDict.DoesNotExist:
                    pass
            if form.phone:
                pass
            if form.twitter:
                pass
            if form.facebook:
                pass
            if objects:
                # choose distinct info and spit it out
                pass
            else:
                userdata = None
            userdata = []
            for obj in objects:
                data_dict = {}
                data_dict['email'] = obj.email
                data_dict['contactInfo'] = obj.data_dict.get('contactInfo')
                data_dict['photos'] = obj.list_photo_urls()
                data_dict['demographics'] = obj.data_dict.get('demographics')
                data_dict['digitalFootprint'] = obj.data_dict.get('digitalFootprint')
                data_dict['socialProfiles'] = obj.data_dict.get('socialProfiles')
                data_dict['organizations'] = obj.data_dict.get('organizations')
                data_dict['enhancedData'] = obj.data_dict.get('enhancedData')
                userdata.append(data_dict)
            return render_template('results/get_results.html', userdata=userdata)
    elif request.method == 'POST':
        form = ContactForm(request.form)
        if form.validate():
            response = ''
            return render_template('results/post_result.html', response)


@app.route('/webhook/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        email = request.form.get('webhookId')
        data_dict = simplejson.loads(request.form.get('result'))
        try:
            userdata = UserDataDict.objects.get(email=email)
        except UserDataDict.DoesNotExist:
            userdata = UserDataDict(email=email)
        userdata.data_dict = data_dict
        userdata.save()
        print 'Email:', email
        print 'Status:', data_dict.get('status')
        return "Thanks a lot"


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')

