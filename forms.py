from wtforms import Form, TextField, validators


class ContactForm(Form):
    email = TextField('E-mail', [validators.Optional(), validators.Email(u'Invalid E-mail.')])
    phone = TextField('Phone', [validators.Optional(),])
    twitter = TextField('Twitter', [validators.Optional(),])
    facebook = TextField('Facebook', [validators.Optional(),])

