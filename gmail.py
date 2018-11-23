import imaplib, email, os, smtplib, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication

user = 'Mojanazwa@gmail.com'
password = '!haslo'
imap_url = 'imap.gmail.com'
attachments_dir = 'sciezka gdzie mają zapisywać się załączniki'

con = imaplib.IMAP4_SSL(imap_url)
con.login(user, password)
con.select('INBOX')

#funkcje potrzebe do odczytywania zawartości mejla
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def get_emails(result_bytes):
    msgs = []
    for num in result_bytes[0].split():
        typ, data = con.fetch(num,'(RFC822)')
        msgs.append(data)
    return msgs

# funkcje potrzebne do pobierania załączników
def search(key,value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data

def get_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName):
            filePath = os.path.join(attachments_dir, fileName)
            with open(filePath,'wb') as f:
                f.write(part.get_payload(decode=True))

def get_raw(lastOneEmails):
    result, data = con.fetch(lastOneEmails, '(RFC822)')
    raw = email.message_from_bytes(data[0][1])
    return raw

def get_lastElement(email,con):
    checkData = search('FROM', email, con)
    listOfEmails = checkData[0].split()
    lastOneEmails = listOfEmails[-1]
    return lastOneEmails

# Odczytywanie zawartości mejla
# msgs = get_emails(search('FROM', 'nazwauzytkownika@gmail.com',con))

# for msg in msgs:
#
#     print('Email: \n')
#     message = get_body(email.message_from_bytes(msg[0][1]))
#     print(message.decode('utf-8'))
#
#     print('\n\n')

def download_attachment(email):
    
    #pobiera najnowszy załącznik od danego mejla
    lastOneEmails = get_lastElement(email,con)

    raw = get_raw(lastOneEmails)
    get_attachments(raw)
    print('Jest nowy załącznik!')

    saveFile.seek(0)
    saveFile.write(str(lastOneEmails))
    saveFile.truncate()
    return False

def send_attachment(toaddr,fileName):

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(user,password)

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = toaddr
    msg['Subject'] = 'temat mejla'
    body = 'Treść mejla'
    msg.attach(MIMEText(body,'plain'))

    path = os.path.join('sciezkadozałacznika',fileName)

    attachment = open(path ,'rb')
    part = MIMEApplication(attachment.read(),_subtype='pdf')
    attachment.close()
    part.add_header('Content-Disposition', 'attachment', filename=fileName)
    msg.attach(part)

    text = msg.as_string()

    server.sendmail(user,toaddr,text)
    server.quit()
    print('Mejl z załącznikiem został wysłany!')

#uruchamianie
download_attachment('mejlodkogochcemysciagnaczalaczniki@gmail.com')
send_attachment('dokogowysylamy@gmail.com','nazwazalacznika')



