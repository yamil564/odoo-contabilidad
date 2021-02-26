
import json
import boto3
from controllers import main
from xml.dom import minidom
import random


sqs = boto3.resource('sqs')


def random_string(l):
    def to_char(x):
        if x < 10:
            return chr(48 + x)
        if x < 36:
            return chr(55 + x)
        return chr(61 + x)

    return "".join([to_char(random.randint(0, 61)) for _ in range(l)])


def generate_ticket_request_xml(username, password, numero_ticket):
    doc = minidom.Document()

    Envelope = doc.createElement("soapenv:Envelope")
    Envelope.setAttribute("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
    Envelope.setAttribute("xmlns:ser", "http://service.sunat.gob.pe")
    Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

    Header = doc.createElement("soapenv:Header")
    Security = doc.createElement("wsse:Security")
    UsernameToken = doc.createElement("wsse:UsernameToken")
    Username = doc.createElement("wsse:Username")
    text = doc.createTextNode(username)
    Username.appendChild(text)
    Password = doc.createElement("wsse:Password")
    text = doc.createTextNode(password)
    Password.appendChild(text)
    UsernameToken.appendChild(Username)
    UsernameToken.appendChild(Password)
    Security.appendChild(UsernameToken)
    Header.appendChild(Security)
    Envelope.appendChild(Header)

    Body = doc.createElement("soapenv:Body")
    getStatus = doc.createElement("ser:getStatus")
    ticket = doc.createElement("ticket")
    text = doc.createTextNode(numero_ticket)
    ticket.appendChild(text)
    getStatus.appendChild(ticket)
    Body.appendChild(getStatus)
    Envelope.appendChild(Body)

    return Envelope


def add_task(prev_ans, user, data, signer):
    tipo_envio = data.get("tipoEnvio", 0)
    url = main.urls[tipo_envio]

    message = {
        "request_id": prev_ans['request_id'],
        "user": {
            "id": user.id,
            "ruc": user.ruc
        },
        "doc_type": prev_ans['document_type'],
        "xml": prev_ans['final_xml'],
        "url": url,
        "signer": signer
    }

    queue = sqs.get_queue_by_name(QueueName='ebilling-tasks.fifo')
    queue.send_message(
        MessageBody=json.dumps(message, ensure_ascii=False),
        MessageDeduplicationId=prev_ans['request_id'],
        MessageGroupId=user.id + "-" + prev_ans['document_type']
    )


def add_task_ticket(prev_ans, user, data, signer, ticket):
    tipo_envio = data.get("tipoEnvio", 0)
    url = main.urls[tipo_envio]

    xml = generate_ticket_request_xml(user.ruc+signer['sunat_usuario'], signer['sunat_password'], ticket)
    xml = xml.toxml(encoding="ISO-8859-1").decode()

    message = {
        "request_id": prev_ans['request_id'],
        "user": {
            "id": user.id,
            "ruc": user.ruc
        },
        "doc_type": prev_ans['document_type'],
        "xml": xml,
        "url": url,
        "signer": signer
    }
    message['ticket'] = ticket

    queue = sqs.get_queue_by_name(QueueName='ebilling-tasks.fifo')
    queue.send_message(
        MessageBody=json.dumps(message, ensure_ascii=False),
        MessageDeduplicationId=prev_ans['request_id'] + '_ticket',
        MessageGroupId=random_string(30)
    )
