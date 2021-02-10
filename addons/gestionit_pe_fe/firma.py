from signxml import XMLSigner, XMLVerifier, methods
import xml.etree.ElementTree as ET
from efact21 import Signature
from efact21 import Envelope
import sys
import zipfile
import io
import base64
from xml.dom import minidom
import os
from . import sunat_response_handle, xml_validation


urls = [
    "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService",
    "https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService",
    "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService",
    "https://www.sunat.gob.pe/ol-it-wsconscpegem/billConsultService",
]

# Pruebas
urls_test = [
    "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService",  # Fact
    "https://e-beta.sunat.gob.pe/ol-ti-itemision-guia-gem-beta/billService",  # Guia
    "https://e-beta.sunat.gob.pe/ol-ti-itemision-otroscpe-gem-beta/billService",  # REte
]

# Produccion
urls_production = [
    "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService",  # Fact
    "https://e-guiaremision.sunat.gob.pe/ol-ti-itemision-guia-gem/billService",  # Guia
    "https://e-factura.sunat.gob.pe/ol-ti-itemision-otroscpe-gem/billService",  # REte
]


def firmar(document, signer, key, cert):
    document.signature = Signature.Signature(
        signer["ruc"],
        signer['ruc'],
        signer['razon_social']
    )

    data_document = document.get_document()

    namespaces = {}
    for k, v in data_document.childNodes[0].attributes.items():
        k = k.replace("xmlns", "").split(":")[-1]
        ET.register_namespace(k, v)
        if k:
            namespaces[k] = v
    data_unsigned = ET.fromstring(data_document.toxml(encoding="utf8").decode())
    
    signed_root = XMLSigner(
        method=methods.enveloped,
        digest_algorithm='sha1',
        c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
    ).sign(data_unsigned, key=key.encode(), cert=cert.encode())

    for x in signed_root[0]:
        tag = x.tag.split("}")[-1]
        if tag == "UBLExtension":
            x[0][0].set("Id", "SignatureMT")
            break

    return ET.tostring(signed_root, encoding="ISO-8859-1")


def get_digest_value(xml_binary_content):
    try:
        doc = minidom.parseString(xml_binary_content.decode())
        digestvaluenode = doc.getElementsByTagName("ds:DigestValue")
        if digestvaluenode:
            digestvalue = digestvaluenode[0].firstChild.data
    except Exception as e:
        digestvalue = False

    return digestvalue


def zipear(xml_binary_content, name_file):
    in_memory_zip = io.BytesIO()
    zf = zipfile.ZipFile(in_memory_zip, "w")
    try:
        zf.writestr(name_file, xml_binary_content)
        zf.close()
    except Exception as e:
        raise e

    in_memory_zip.seek(0)
    data_file = in_memory_zip.read()
    documentoZip = base64.b64encode(data_file)
    return documentoZip


def generate_envio_xml(username, password, file_name, doc_zip):
    header = Envelope.Header(username, password)
    body = Envelope.Body(file_name, doc_zip)
    envelope = Envelope.Envelope(header, body)
    return envelope.get_document().toxml()

def generate_envio_resumen_xml(username, password, file_name, doc_zip):
    header = Envelope.Header(username, password)
    body = Envelope.BodyResumen(file_name, doc_zip)
    envelope = Envelope.Envelope(header, body)
    return envelope.get_document().toxml()


def send_xml_sunat(prev_sign, data, user):
    tipo_envio = data.get("tipoEnvio", 0)

    if tipo_envio in [1, 3]:
        url = urls[tipo_envio]
    elif tipo_envio == 0:
        if prev_sign['document_type'] in ["09"]:
            url = urls_test[1]
        else:
            url = urls_test[0]
    elif tipo_envio == 2:
        if prev_sign['document_type'] in ["09"]:
            url = urls_production[1]
        else:
            url = urls_production[0]
    elif tipo_envio == 4:
        url = url_check_xml
    else:
        raise Exception("bad tipoEnvio")
    headers = {"Content-Type": "application/xml"}

    resp = requests.post(
        url,
        data=prev_sign['final_xml'],
        headers=headers,
        timeout=20)
    response_xml = resp.text

    document_type = prev_sign['document_type']
    if document_type in ['01', '03', '07', '08', '09']:
        resp = sunat_response_handle.get_response(response_xml)
    elif document_type in ['RA', 'RC']:
        resp = sunat_response_handle.get_response_ticket(response_xml)
        # Send queue
    else:
        resp = {
            "success": False,
            "message": "Invalid document type."
        }
    resp['response_xml'] = response_xml
    return resp