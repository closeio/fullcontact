from fullcontact import aggregate_data, batch_lookup, emails_from_file


def main():
    # have the webhook working by:
    #   1. python flask_fullcontact.py
    #   2. proxylocal 5000 --host fullcontact
    webhook = 'http://fullcontact.t.proxylocal.com/webhook/'
    # request lookup for emails, phone, twitter and facebook
    data_list = [
        ('email', 'wojcikstefan@gmail.com'),
        ('email', 'stefan_wojcik@o2.pl'),
        ('phone', '+48601941311'),
        ('twitter', 'stefanwojcik'),
        ('facebookUsername', 'wojcikstefan')
    ]
    batch_lookup(data_list, webhook, debug=True)
    # request lookup for emails from CSV file
    batch_lookup(emails_from_file(open('emails_test.csv')), webhook)
    # aggregate data from 2 emails, phone, twitter and facebook
    u = aggregate_data(data_list)
    print u.to_dict()

if __name__ == '__main__':
    main()
