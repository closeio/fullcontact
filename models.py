from mongoengine import DictField, Document, EmailField, EmbeddedDocument


class UserDataDict(Document):
    email = EmailField(required=True, unique=True)
    data_dict = DictField(required=True)

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

    def __unicode__(self):
        return '%s (%s)' % (self.email, self.data_dict.get('status'))

