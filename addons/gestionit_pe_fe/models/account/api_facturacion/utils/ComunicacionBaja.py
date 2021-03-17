from xml.dom import minidom

class ComunicacionBaja():
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement('VoidedDocuments')
        self.doc.appendChild(root)

        root.setAttribute('xmlns', 'urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1')
        root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
        root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
        root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        return root

    def VoidedDocumentsLine(self, line_id, document_type, journal, correlativo, motivo):
        VoidedDocumentsLine = self.doc.createElement('sac:VoidedDocumentsLine')
        LineID = self.doc.createElement('cbc:LineID')
        text = self.doc.createTextNode(str(line_id))
        LineID.appendChild(text)
        VoidedDocumentsLine.appendChild(LineID)

        DocumentTypeCode = self.doc.createElement('cbc:DocumentTypeCode')
        text = self.doc.createTextNode(document_type)
        DocumentTypeCode.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentTypeCode)

        DocumentSerialID = self.doc.createElement('sac:DocumentSerialID')
        text = self.doc.createTextNode(journal)
        DocumentSerialID.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentSerialID)

        DocumentNumberID = self.doc.createElement('sac:DocumentNumberID')
        text = self.doc.createTextNode(str(correlativo))
        DocumentNumberID.appendChild(text)
        VoidedDocumentsLine.appendChild(DocumentNumberID)

        VoidReasonDescription = self.doc.createElement('sac:VoidReasonDescription')
        text = self.doc.createTextNode(motivo)
        VoidReasonDescription.appendChild(text)
        VoidedDocumentsLine.appendChild(VoidReasonDescription)

        return VoidedDocumentsLine


    def firma(self, id):
        UBLExtensions = self.doc.createElement("ext:UBLExtensions")

        UBLExtension = self.doc.createElement("ext:UBLExtension")

        ExtensionContent = self.doc.createElement("ext:ExtensionContent")

        Signature = self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id", id)

        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)
        UBLExtensions.appendChild(UBLExtension)

        return UBLExtensions

    def Signature(self, Id, ruc, razon_social, uri):
        Signature = self.doc.createElement("cac:Signature")
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(Id)
        ID.appendChild(text)
        Signature.appendChild(ID)

        SignatoryParty = self.doc.createElement("cac:SignatoryParty")
        PartyIdentification = self.doc.createElement("cac:PartyIdentification")
        RUC = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ruc)
        RUC.appendChild(text)
        PartyIdentification.appendChild(RUC)
        PartyName = self.doc.createElement("cac:PartyName")
        Name = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(razon_social)
        Name.appendChild(text)
        PartyName.appendChild(Name)
        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)

        Signature.appendChild(SignatoryParty)

        DigitalSignatureAttachment = self.doc.createElement("cac:DigitalSignatureAttachment")
        ExternalReference = self.doc.createElement("cac:ExternalReference")
        URI = self.doc.createElement("cbc:URI")
        text = self.doc.createTextNode(uri)
        URI.appendChild(text)
        ExternalReference.appendChild(URI)
        DigitalSignatureAttachment.appendChild(ExternalReference)

        Signature.appendChild(DigitalSignatureAttachment)

        return Signature

    def UBLVersion(self, ubl_version_id):
        UBLVersion = self.doc.createElement('cbc:UBLVersionID')
        text = self.doc.createTextNode(ubl_version_id)
        UBLVersion.appendChild(text)

        return UBLVersion

    def CustomizationID(self, customization_id):
        Customization = self.doc.createElement('cbc:CustomizationID')
        text = self.doc.createTextNode(str(customization_id))
        Customization.appendChild(text)

        return Customization

    def SummaryId(self, summary_id):
        SummaryID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(summary_id)
        SummaryID.appendChild(text)

        return SummaryID

    ## Fecha de emision de los documentos
    def ReferenceDate(self, reference_date):
        ReferenceDate = self.doc.createElement('cbc:ReferenceDate')
        text = self.doc.createTextNode(reference_date)
        ReferenceDate.appendChild(text)
        return ReferenceDate

    ## Fecha de generacion del resumen
    def IssueDate(self, issue_date):
        IssueDate = self.doc.createElement('cbc:IssueDate')
        text = self.doc.createTextNode(issue_date)
        IssueDate.appendChild(text)

        return IssueDate

    def Note(self, note):
        Note = self.doc.createElement('cbc:Note')
        text = self.doc.createTextNode(note)
        Note.appendChild(text)

        return Note

    def SummaryRoot(self, rootXML, ubl_version_id, customization_id, summary_id, reference_date, issue_date, note):
        SummaryRoot = rootXML

        SummaryRoot.appendChild(self.UBLVersion(ubl_version_id))
        SummaryRoot.appendChild(self.CustomizationID(customization_id))
        SummaryRoot.appendChild(self.SummaryId(summary_id))
        SummaryRoot.appendChild(self.ReferenceDate(reference_date))
        SummaryRoot.appendChild(self.IssueDate(issue_date))
        SummaryRoot.appendChild(self.Note(note))

        return SummaryRoot

    def cacAccountingSupplierParty(self, num_doc_ident,
                                   tipo_doc_ident,
                                   nombre_comercial,
                                   codigo_ubigeo,
                                   nombre_direccion_full,
                                   nombre_direccion_division,
                                   nombre_departamento,
                                   nombre_provincia,
                                   nombre_distrito,
                                   nombre_proveedor,
                                   codigo_pais):
        cacAccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')

        # Numero de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacAccountingSupplierParty.appendChild(cbcCustomerAssignedAccountID)

        # tipo de documento de identidad
        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(tipo_doc_ident)
        cbcAdditionalAccountID.appendChild(text)
        cacAccountingSupplierParty.appendChild(cbcAdditionalAccountID)

        cacParty = self.doc.createElement('cac:Party')
        cacAccountingSupplierParty.appendChild(cacParty)

        '''
        cacPartyName = self.doc.createElement('cac:PartyName')
        cacParty.appendChild(cacPartyName)

        # Nombre Comercial
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(str(nombre_comercial))
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)

        # Domicilio Fiscal
        cacPostalAddress = self.doc.createElement('cac:PostalAddress')
        cacParty.appendChild(cacPostalAddress)

        # Codigo de ubigeo
        if codigo_ubigeo:
            cbcID = self.doc.createElement('cbc:ID')
            text = self.doc.createTextNode(str(codigo_ubigeo))
            cbcID.appendChild(text)
            cacPostalAddress.appendChild(cbcID)

        # Direccion Completa y Detallada
        cbcStreetName = self.doc.createElement('cbc:StreetName')
        text = self.doc.createTextNode(nombre_direccion_full)
        cbcStreetName.appendChild(text)
        cacPostalAddress.appendChild(cbcStreetName)

        # Urbanizacion o zona
        if nombre_direccion_division:
            cbcCitySubdivisionName = self.doc.createElement('cbc:CitySubdivisionName')
            text = self.doc.createTextNode(nombre_direccion_division)
            cbcCitySubdivisionName.appendChild(text)
            cacPostalAddress.appendChild(cbcCitySubdivisionName)

        # Nombre de Ciudad
        cbcCityName = self.doc.createElement('cbc:CityName')
        text = self.doc.createTextNode(str(nombre_departamento))
        cbcCityName.appendChild(text)
        cacPostalAddress.appendChild(cbcCityName)

        # Nombre de Provincia
        cbcCountrySubentity = self.doc.createElement('cbc:CountrySubentity')
        text = self.doc.createTextNode(str(nombre_provincia))
        cbcCountrySubentity.appendChild(text)
        cacPostalAddress.appendChild(cbcCountrySubentity)

        # Nombre de Distrito
        cbcDistrict = self.doc.createElement('cbc:District')
        text = self.doc.createTextNode(str(nombre_distrito))
        cbcDistrict.appendChild(text)
        cacPostalAddress.appendChild(cbcDistrict)

        # Codigo de pais
        cacCountry = self.doc.createElement('cac:Country')
        cacPostalAddress.appendChild(cacCountry)
        cbcIdentificationCode = self.doc.createElement('cbc:IdentificationCode')
        text = self.doc.createTextNode(str(codigo_pais))
        cbcIdentificationCode.appendChild(text)
        cacCountry.appendChild(cbcIdentificationCode)
        '''

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(str(nombre_proveedor))
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacAccountingSupplierParty

    def getStatus(self, username, password,numero_ticket):
        #http://schemas.xmlsoap.org/soap/envelope/"
        #http://service.sunat.gob.pe
        #http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd
        Envelope = self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser", "http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header = self.doc.createElement("soapenv:Header")
        Security = self.doc.createElement("wsse:Security")
        UsernameToken = self.doc.createElement("wsse:UsernameToken")
        Username = self.doc.createElement("wsse:Username")
        text = self.doc.createTextNode(username)
        Username.appendChild(text)
        Password = self.doc.createElement("wsse:Password")
        text = self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body = self.doc.createElement("soapenv:Body")
        getStatus = self.doc.createElement("ser:getStatus")
        ticket = self.doc.createElement("ticket")
        text = self.doc.createTextNode(numero_ticket)
        ticket.appendChild(text)
        # contentFile=self.doc.createElement("contentFile")
        # text=self.doc.createTextNode(contentfile)
        # contentFile.appendChild(text)
        getStatus.appendChild(ticket)
        # getStatus.appendChild(contentFile)
        Body.appendChild(getStatus)
        Envelope.appendChild(Body)

        return Envelope
