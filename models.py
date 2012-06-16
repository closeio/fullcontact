from mongoengine import DictField, Document, EmailField, EmbeddedDocument, StringField


class UserData(Document):
    data_dict = DictField(required=True)

    meta = {'allow_inheritance': True}

    def list_photo_urls(self):
        photos = self.data_dict.get('photos')
        if photos:
            return [photo['url'] for photo in photos]
        return None
    
    def to_dict(self):
        out = dict(self._data)
        for k,v in out.items():
            if isinstance(v, EmbeddedDocument):
                out[k] = dict(v._data)
        return out

    def safe_pop(self, fieldname):
        if self.data_dict.has_key(fieldname):
            return self.data_dict.pop(fieldname)
        return None



    def get_title(self):
        return 'Generic User Data'

class UserEmailData(UserData):
    email = EmailField()

    def __unicode__(self):
        return 'E-mail: %s (%s)' % (self.email, self.data_dict.get('status'))

    def get_title(self):
        return self.email

class UserPhoneData(UserData):
    phone = StringField(max_length=16)

    def __unicode__(self):
        return 'Phone: %s (%s)' % (self.phone, self.data_dict.get('status'))

    def get_title(self):
        return self.phone

class UserTwitterData(UserData):
    twitter = StringField(max_length=64)

    def __unicode__(self):
        return 'Twitter: %s (%s)' % (self.twitter, self.data_dict.get('status'))
    
    def get_title(self):
        return self.twitter

class UserFacebookData(UserData):
    facebookUsername = StringField(max_length=64)
 
    def __unicode__(self):
        return 'Facebook: %s (%s)' % (self.facebookUsername, self.data_dict.get('status'))

    def get_title(self):
        return self.facebookUsername


