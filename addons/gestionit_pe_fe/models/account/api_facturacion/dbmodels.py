import os
from pynamodb import models, attributes, indexes

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()


class UserApiKeyIndex(indexes.GlobalSecondaryIndex):
    class Meta:
        index_name = "ApiKeyIndex"
        projection = indexes.IncludeProjection(['api_secret'])
        read_capacity_units = 5
        write_capacity_units = 5
        region = "us-east-1"
    api_key = attributes.UnicodeAttribute(hash_key=True)


class User(models.Model):
    class Meta:
        table_name = "ei.users"
        if os.environ.get("DYNAMOHOST", "aws") != "aws":
            host = "http://{0}:{1}".format(os.environ.get("DYNAMOHOST"),
                                           os.environ.get('DYNAMOPORT', '8000'))
        region = "us-east-1"

    id = attributes.UnicodeAttribute(hash_key=True)
    client_id = attributes.UnicodeAttribute(null=True)
    client_secret = attributes.UnicodeAttribute(null=True)
    email = attributes.UnicodeAttribute(range_key=True)
    password = attributes.UnicodeAttribute()

    # Datos principales de la empresa (ruc, razon social, y certificado digital)
    ruc = attributes.UnicodeAttribute(null=True)
    razon_social = attributes.UnicodeAttribute(null=True)
    private_key = attributes.UnicodeAttribute(null=True)
    public_key = attributes.UnicodeAttribute(null=True)

    # Indica si la firma es con los certificados de la empresa o con certificados del PSE HIGHLAND TRADING COMPANY SAC
    self_signed = attributes.BooleanAttribute(null=True, default=True)

    # Crendenciales de Uso de Web Service de Facturación Electrónica
    api_key_index = UserApiKeyIndex()
    api_key = attributes.UnicodeAttribute(null=True)
    api_secret = attributes.UnicodeAttribute(null=True)

    # Selector de entidad a donde se remitirá el comprobante electrónico
    # valores: 'sunat' o '', 'efact'
    ose = attributes.UnicodeAttribute(null=True)

    # Credenciales de acceso para SUNAT
    sunat_user = attributes.UnicodeAttribute(null=True)
    sunat_password = attributes.UnicodeAttribute(null=True)

    # Credenciales de acceso para OSE Efact
    ose_efact_password = attributes.UnicodeAttribute(null=True)
    ose_efact_access_key = attributes.UnicodeAttribute(null=True)

    ose_nubefact_user = attributes.UnicodeAttribute(null=True)
    ose_nubefact_password = attributes.UnicodeAttribute(null=True)


class UserAPIIndex(indexes.GlobalSecondaryIndex):
    class Meta:
        read_capacity_units = 5
        write_capacity_units = 5
        index_name = "UserAPIIndex"
        if os.environ.get("DYNAMOHOST", "aws") != "aws":
            host = "http://{0}:{1}".format(os.environ.get("DYNAMOHOST"),
                                           os.environ.get('DYNAMOPORT', '8000'))
        region = "us-east-1"
        projection = indexes.AllProjection()

    user_id = attributes.UnicodeAttribute(hash_key=True)


class Log(models.Model):
    class Meta:
        table_name = "ei.logs"
        if os.environ.get("DYNAMOHOST", "aws") != "aws":
            host = "http://{0}:{1}".format(os.environ.get("DYNAMOHOST"),
                                           os.environ.get('DYNAMOPORT', '8000'))
        region = "us-east-1"

    id = attributes.UnicodeAttribute(hash_key=True)
    timestamp = attributes.NumberAttribute(range_key=True)
    user_id = attributes.UnicodeAttribute(null=False)
    user_id_index = UserAPIIndex()

    estado = attributes.UnicodeAttribute(null=True, default="not-specified")
    request_json = attributes.MapAttribute()
    response_json = attributes.MapAttribute(null=True)
    signed_xml = attributes.UnicodeAttribute(null=True)
    sunat_request_xml = attributes.UnicodeAttribute(null=True)
    sunat_response_xml = attributes.UnicodeAttribute(null=True)
    ticket_info_xml = attributes.UnicodeAttribute(null=True)
    sunat_response_content_xml = attributes.UnicodeAttribute(null=True)
    sunat_response_json = attributes.MapAttribute(null=True)
    s3_saved = attributes.BooleanAttribute(default=False)

    # Deprecated
    signed_xml_data = attributes.UnicodeAttribute(null=True)
    response_xml = attributes.UnicodeAttribute(null=True)
    content_xml = attributes.UnicodeAttribute(null=True)
    unsigned_xml = attributes.UnicodeAttribute(null=True)

    # OSE EFACT
    ose_efact_cdr = attributes.UnicodeAttribute(null=True)
    ose_response_xml = attributes.UnicodeAttribute(null=True)


def create_tables():
    User.create_table(read_capacity_units=100,
                      write_capacity_units=100, wait=True)
    Log.create_table(read_capacity_units=100,
                     write_capacity_units=100, wait=True)


if __name__ == "__main__":
    create_tables()
