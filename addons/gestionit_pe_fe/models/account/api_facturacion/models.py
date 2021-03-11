from . import dbmodels
from .controllers import main
import logging
import random


_logger = logging.getLogger(__name__)


def random_string(l):
    def to_char(x):
        if x < 10:
            return chr(48 + x)
        if x < 36:
            return chr(55 + x)
        return chr(61 + x)

    return "".join([to_char(random.randint(0, 61)) for _ in range(l)])


def lamdba(data):

    credentials = {
        "ruc": data["documento"]["numDocEmisor"],
        'razon_social': data["documento"]["nombreEmisor"],
        'usuario': data["company"]["SUNAT_user"],
        'password': data["company"]["SUNAT_pass"],
        'key_private': data["company"]["key_private"],
        'key_public': data["company"]["key_public"],
    }

    main_xml = main.handle(data, credentials, True)
    _logger.info(main_xml)
    # return main_xml

    request_id = random_string(20)

    if data["tipoEnvio"] == 0:
        request_id = "test/%s" % (request_id)

    ans = {
        'request_id': request_id
    }
    ans.update(main_xml)

    # log = dbmodels.Log(
    #     id=request_id,
    #     timestamp=time.time(),
    #     user_id=self.user.id)

    # _logger.info(log)

    # log.request_json = data
    # log.s3_saved = True
    # s3obj = {
    #     "request_json": data,
    #     "response_json": ans,
    # }
    # log.estado = "invalid-request"

    # if not ans['success']:
    #     if "signer" in ans:
    #         del ans['signer']
    #     s3_client.put_object(
    #         Bucket=os.environ['S3_BUCKET'],
    #         Body=json.dumps(s3obj, ensure_ascii=False).encode(
    #             "ISO-8859-1"),
    #         ContentType="application/json",
    #         Key=request_id
    #     )
    #     log.save()
    #     return ans

    # log.estado = "pending-delivery"
    # s3obj['signed_xml'] = main_xml['signed_xml']
    # s3obj['sunat_request_xml'] = main_xml['final_xml']

    # asyncrono = data.get("asyncrono", False)
    # generate_xml_only = data.get("generate-xml-only", False)
    # if generate_xml_only:
    #     ans['sunat_status'] = '-'
    # elif asyncrono:
    #     # worker.add_task(ans, self.user, data, main_xml['signer'])
    #     # log.estado = "pending-delivery"
    #     ans['sunat_status'] = "P"
    # else:
    resp = main.send_xml_sunat(ans, data)

    ans["token"] = resp.get("token")
    ans['sunat_observaciones'] = resp.get('observaciones', [])
    # if resp['success']:
    # log.estado = "sunat-accepted"
    # else:
    # log.estado = "sunat-rejected"
    ans['sunat_errors'] = resp.get('errors', [])
    ans['sunat_status'] = resp.get('status', "-")
    if resp.get("ticket", False):
        ans['ticket'] = resp['ticket']
        #worker.add_task_ticket(ans, self.user, data, main_xml['signer'], resp['ticket'])
        # log.estado = "pending-ticket"
    ans['response_xml'] = resp.get('response_xml')
    if resp.get("xml_content", None):
        ans['response_content_xml'] = resp['xml_content']
        # s3obj['sunat_response_content_xml'] = resp["xml_content"]
        # s3obj['sunat_response_xml'] = resp.get('response_xml')
    # log.save()

    # del ans['signer']
    # del ans['final_xml']

    # s3_client.put_object(
    #     Bucket=os.environ['S3_BUCKET'],
    #     Body=json.dumps(s3obj, ensure_ascii=False).encode("ISO-8859-1"),
    #     ContentType="application/json",
    #     Key=request_id
    # )
    return ans
