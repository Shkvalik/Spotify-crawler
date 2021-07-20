import json
import logging
import os
import sys
from urllib.parse import urlparse


def remove_spaces(s):
    return ' '.join(s.split()).strip()


def send_email(subject, body='', email_to='', files=()):
    """send email using gmail account"""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from scrapy_app.settings import BOT_EMAIL, BOT_PASSWORD, EMAIL_TO
    email_to_list = [email_to] if email_to else EMAIL_TO

    msgRoot = MIMEMultipart()
    msgRoot['From'] = BOT_EMAIL
    msgRoot['To'] = ', '.join(email_to_list)
    msgRoot['Subject'] = subject
    msgRoot.attach(MIMEText(body, 'plain'))  # html

    for file_path in files or []:
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file_path)
        msgRoot.attach(part)

    logging.info(f"Sending email: {subject}. From: {BOT_EMAIL} to: {', '.join(email_to_list)}")
    try:
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.ehlo()
        server.starttls()
        server.login(BOT_EMAIL, BOT_PASSWORD)
        server.sendmail(BOT_PASSWORD, email_to_list, msgRoot.as_string())
        server.close()
        logging.info('Email was sent successfully')

    except Exception as e:
        logging.error('Error sending email')


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    from datetime import date, datetime
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def configure_django():
    """
    Set necessary environment settings - for Django and Scrapy settings modules and run django.setup()
    This function should be called before any import of Django models (used in crawler, email service, etc)
    """
    import django
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dir "scrapy_app"
    project_dir = os.path.dirname(app_dir)                                 # dir "sohb2bcrawlers"
    sys.path.extend([app_dir, project_dir])                                # add dirs to PATH
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_app.settings'           # set path to scrapy settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'db_app.settings'               # set path to django settings
    django.setup()


def format_url(url, replace_scheme=True, replace_query=True, new_domain=''):
    u = urlparse(url.strip())

    # make url begin with "http"
    if replace_scheme:
        u = u._replace(scheme='http')

    # remove query from url
    if replace_query:
        u = u._replace(query=None)

    # for urls with empty beginning - add "http"
    if not u.scheme:
        u = u._replace(scheme='http')

    # for invalid urls (with empty netloc) - get it from path
    if not u.netloc:
        netloc, path = (u.path + '/').split('/', 1)
        u = u._replace(netloc=netloc)
        u = u._replace(path='/' + path)

    # set new domain if needed
    if new_domain:
        u = u._replace(netloc=new_domain)

    # add all urls path ends with '/' (i.e., google.com/search/ except http://google.com/search)
    u = u._replace(path=u.path.rstrip('/') + '/')

    # remove "www" from url
    if u.netloc.startswith('www.'):
        u = u._replace(netloc=u.netloc.replace('www.', '', 1))

    # print(u.netloc, '-', u.path)
    url = u.geturl().lower()
    return url


def load_from_resource(file_name):
    """
    load json dict from resources
    """
    from scrapy_app.settings import RESOURCES_DIR
    with open(os.path.join(RESOURCES_DIR, file_name), mode='r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def flatten_dict(d, parent_key='', sep='_'):
    """Make nested dicts flat"""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ' | '.join(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def format_key(key):
    import string
    key = key.translate(str.maketrans('', '', string.punctuation))  # remove punctuation
    key = remove_spaces(key).replace(' ', '_').lower()
    return key


def extract_text_from_el(el):
    if not any(e._expr.endswith('text()') for e in el):
        el_text = el.xpath('descendant-or-self::text()[normalize-space()]')
    else:
        el_text = el
    return remove_spaces(' '.join(el_text.getall()))


def extract_attrs_data_from_table(response, rows_xpath, key_xpath, value_xpath, data=None):
    """Extract data from HTML key-value table to dict of attrs"""
    data = data if data is not None else {}
    for r in response.xpath(rows_xpath):
        key_el, value_el = r.xpath(key_xpath), r.xpath(value_xpath)

        key = format_key(extract_text_from_el(key_el))
        if not key:
            continue
        value = extract_text_from_el(value_el)
        data[key] = value
    return data


def extract_rows_data_from_table(response, table_xpath, header_xpath=None, rows_xpath=None, data=None):
    """Extract data from HTML table to list of dicts (each element - table row)"""
    data = data if data is not None else []
    header_xpath = header_xpath or 'descendant::tr[1]/th'
    rows_xpath = rows_xpath or 'descendant::tr[position()>1]'

    table = response.xpath(table_xpath)
    table_headers = table.xpath(header_xpath)
    column_names = [format_key(extract_text_from_el(k)) for k in table_headers]

    rows = table.xpath(rows_xpath)
    for row in rows:
        d = {}
        for i, td in enumerate(row.xpath('td')):
            key = column_names[i]
            value = extract_text_from_el(td)
            if not key:
                continue
            d[key] = value
        data.append(d)
    return data


def extract_form_data(response, form_xpath):
    """Extract data from HTML form to dict"""
    form_inputs = response.xpath(form_xpath).xpath('descendant::input[not(@type="button")][not(@type="submit")]')
    form_data = {el.xpath('@name').get(): el.xpath('@value').get() for el in form_inputs}
    return form_data
