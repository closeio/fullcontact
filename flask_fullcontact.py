import mongoengine
import simplejson
from flask import Flask, request
from models import UserDataDict

app = Flask(__name__)

mongoengine.connect('fullcontact')


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

