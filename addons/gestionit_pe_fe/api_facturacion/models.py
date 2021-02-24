from . import rpc


class EFact21(rpc.Handler):
    def __init__(self, headers, body):
        self.signed_xml = None
        self.signed_xml_data = None
        self.response_xml = None
        self.xml = None
        self.unsigned_xml = None
        self.user = None
        super(EFact21, self).__init__(headers, body)

    # def prueba(self):
    #     return 'Hola espacio'

    # @auth.auth_required
    def lamdba(self, data):
        print(data)
        usuario = None
        password = None
        if self.user.ose in ["sunat", "efact", None, ""]:
            usuario = self.user.sunat_user
            password = self.user.sunat_password
        elif self.user.ose == "nubefact":
            usuario = self.user.ose_nubefact_user
            password = self.user.ose_nubefact_password

        if self.user.ose in ["sunat", "efact", None, ""] and self.user.self_signed and (usuario is None or password is None):
            raise Exception(
                "Las credenciales de SUNAT no estan configurada para este usuario")

        if self.user.ose in ["nubefact"] and self.user.self_signed and (usuario is None or password is None):
            raise Exception(
                "Las credenciales de la OSE NUBEFACT no estan configurada para este usuario")

        credentials = {
            "ruc": self.user.ruc,
            'razon_social': self.user.razon_social,
            'usuario': usuario,
            'password': password,
            'key_private': self.user.private_key,
            'key_public': self.user.public_key
        }
        main_xml = main.handle(data, credentials, self.user.self_signed)
        request_id = random_string(20)

        if data["tipoEnvio"] == 0:
            request_id = "test/%s" % (request_id)

        ans = {
            'request_id': request_id
        }
        ans.update(main_xml)
        log = dbmodels.Log(
            id=request_id,
            timestamp=time.time(),
            user_id=self.user.id)

        log.request_json = data
        log.s3_saved = True
        s3obj = {
            "request_json": data,
            "response_json": ans,
        }
        log.estado = "invalid-request"
        if not ans['success']:
            if "signer" in ans:
                del ans['signer']
            s3_client.put_object(
                Bucket=os.environ['S3_BUCKET'],
                Body=json.dumps(s3obj, ensure_ascii=False).encode(
                    "ISO-8859-1"),
                ContentType="application/json",
                Key=request_id
            )
            log.save()
            return ans

        log.estado = "pending-delivery"
        s3obj['signed_xml'] = main_xml['signed_xml']
        s3obj['sunat_request_xml'] = main_xml['final_xml']

        asyncrono = data.get("asyncrono", False)
        generate_xml_only = data.get("generate-xml-only", False)
        if generate_xml_only:
            ans['sunat_status'] = '-'
        elif asyncrono:
            worker.add_task(ans, self.user, data, main_xml['signer'])
            log.estado = "pending-delivery"
            ans['sunat_status'] = "P"
        else:
            resp = main.send_xml(ans, data, self.user)
            ans["token"] = resp.get("token")
            ans['sunat_observaciones'] = resp.get('observaciones', [])
            if resp['success']:
                log.estado = "sunat-accepted"
            else:
                log.estado = "sunat-rejected"
                ans['sunat_errors'] = resp.get('errors', [])
            ans['sunat_status'] = resp.get('status', "-")
            if resp.get("ticket", False):
                ans['ticket'] = resp['ticket']
                #worker.add_task_ticket(ans, self.user, data, main_xml['signer'], resp['ticket'])
                log.estado = "pending-ticket"
            ans['response_xml'] = resp.get('response_xml')
            if resp.get("xml_content", None):
                ans['response_content_xml'] = resp['xml_content']
                s3obj['sunat_response_content_xml'] = resp["xml_content"]
            s3obj['sunat_response_xml'] = resp.get('response_xml')
        log.save()

        del ans['signer']
        del ans['final_xml']

        s3_client.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Body=json.dumps(s3obj, ensure_ascii=False).encode("ISO-8859-1"),
            ContentType="application/json",
            Key=request_id
        )

        return ans
