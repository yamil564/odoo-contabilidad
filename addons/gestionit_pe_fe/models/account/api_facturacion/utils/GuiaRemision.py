from xml.dom import minidom


class GuiaRemision:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement('DespatchAdvice')
        self.doc.appendChild(root)
        root.setAttribute('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2')
        root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
        root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        root.setAttribute('xmlns:ccts', 'urn:un:unece:uncefact:documentation:2')
        root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
        root.setAttribute('xmlns:qdt', 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2')
        root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
        root.setAttribute('xmlns:udt', 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        return root

    def firma(self, id):
        UBLExtension = self.doc.createElement("ext:UBLExtension")
        ExtensionContent = self.doc.createElement("ext:ExtensionContent")
        Signature = self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id", id)
        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)
        return UBLExtension

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

    def UBLVersion(self, id):
        UBLVersion = self.doc.createElement('cbc:UBLVersionID')
        text = self.doc.createTextNode(id)
        UBLVersion.appendChild(text)
        return UBLVersion

    def CustomizationID(self, id):
        cbcCustomizationID = self.doc.createElement('cbc:CustomizationID')
        text = self.doc.createTextNode(str(id))
        cbcCustomizationID.appendChild(text)
        return cbcCustomizationID

    # Tipo de operacion
    def OperacionID(self, id):
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(str(id))
        cbcID.appendChild(text)
        return cbcID

    def issueDate(self, fecha):
        cbcIssueDate = self.doc.createElement('cbc:IssueDate')
        text = self.doc.createTextNode(fecha)
        cbcIssueDate.appendChild(text)
        return cbcIssueDate

    def issueTime(self, hora):
        cbcIssueDate = self.doc.createElement('cbc:IssueTime')
        text = self.doc.createTextNode(hora)
        cbcIssueDate.appendChild(text)
        return cbcIssueDate

    def despatchTypeCode(self, invoicetypecode):
        cacInvoiceTypeCode = self.doc.createElement('cac:DespatchAdviceTypeCode')
        text = self.doc.createTextNode(str(invoicetypecode))
        cacInvoiceTypeCode.appendChild(text)
        return cacInvoiceTypeCode

    def Note(self, note):
        Note = self.doc.createElement('cbc:Note')
        text = self.doc.createTextNode(note)
        Note.appendChild(text)
        return Note

    def SummaryRoot(self, rootXML, ubl_version_id, customization_id, id, issue_date, issue_time, type_code_dispatch, note):
        SummaryRoot = rootXML
        SummaryRoot.appendChild(self.UBLVersion(ubl_version_id))
        SummaryRoot.appendChild(self.CustomizationID(customization_id))
        SummaryRoot.appendChild(self.OperacionID(id))
        SummaryRoot.appendChild(self.issueDate(issue_date))
        SummaryRoot.appendChild(self.issueTime(issue_time))
        SummaryRoot.appendChild(self.despatchTypeCode(type_code_dispatch))
        SummaryRoot.appendChild(self.Note(note))
        return SummaryRoot


    def cacOrderReference(self, id, orderTypeCode, orderTypeCodeName):
        cacOrderReference = self.doc.createElement('cac:OrderReference')
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        ID.appendChild(text)
        cacOrderReference.appendChild(ID)

        cbcorderTypeCode = self.doc.createElement("cbc:OrderTypeCode")
        cbcorderTypeCode.setAttribute('name',orderTypeCodeName)
        text = self.doc.createTextNode(orderTypeCode)
        cbcorderTypeCode.appendChild(text)
        cacOrderReference.appendChild(cbcorderTypeCode)

        return cacOrderReference

    def cacAddDocReference(self, id, docTypeCod, docType):
        cacAddDocReference = self.doc.createElement('cac:AdditionalDocumentReference')
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        ID.appendChild(text)
        cacAddDocReference.appendChild(ID)

        cbcdocTypeCod = self.doc.createElement("cbc:DocumentTypeCode")
        text = self.doc.createTextNode(docTypeCod)
        cbcdocTypeCod.appendChild(text)
        cacAddDocReference.appendChild(cbcdocTypeCod)

        cbcdocType = self.doc.createElement("cbc:DocumentType")
        text = self.doc.createTextNode(docType)
        cbcdocType.appendChild(text)
        cacAddDocReference.appendChild(cbcdocType)

        return cacAddDocReference

    def cacDespatchSupplierParty(self, num_doc_ident,
                       tipo_doc_ident, nombre_comercial):
        cacDespatchSupplierParty = self.doc.createElement('cac:DespatchSupplierParty')

        # Numero y tipo de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        cbcCustomerAssignedAccountID.setAttribute('schemeID', tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacDespatchSupplierParty.appendChild(cbcCustomerAssignedAccountID)

        cacParty = self.doc.createElement('cac:Party')
        cacDespatchSupplierParty.appendChild(cacParty)

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyName = self.doc.createElement('cac:PartyName')
        cacParty.appendChild(cacPartyName)
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(nombre_comercial)
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)

        return cacDespatchSupplierParty

    def cacDeliveryCustomerParty(self,num_doc_ident,
                       tipo_doc_ident, nombre_comercial):
        cacDeliveryCustomerParty = self.doc.createElement('cac:DeliveryCustomerParty')

        # Numero y tipo de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        cbcCustomerAssignedAccountID.setAttribute('schemeID', tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacDeliveryCustomerParty.appendChild(cbcCustomerAssignedAccountID)




        cacParty = self.doc.createElement('cac:Party')
        cacDeliveryCustomerParty.appendChild(cacParty)

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(nombre_comercial)
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacDeliveryCustomerParty

    def cacSellerSupplierParty(self,num_doc_ident,
                       tipo_doc_ident,
                               nombre_comercial):
        cacSellerSupplierParty = self.doc.createElement('cac:SellerSupplierParty')

        # Numero y tipo de documento de identidad
        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        cbcCustomerAssignedAccountID.setAttribute('schemeID', tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcCustomerAssignedAccountID.appendChild(text)
        cacSellerSupplierParty.appendChild(cbcCustomerAssignedAccountID)




        cacParty = self.doc.createElement('cac:Party')
        cacSellerSupplierParty.appendChild(cacParty)

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(nombre_comercial)
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacSellerSupplierParty

    def cacCarrierParty(self,num_doc_ident,
                       tipo_doc_ident,
                       nombre):
        cacCarrierParty = self.doc.createElement('cac:DespatchSupplierParty')

        # Numero y tipo de documento de identidad

        cacPartyIdentification = self.doc.createElement('cac:PartyIdentification')
        cacCarrierParty.appendChild(cacPartyIdentification)

        cbcID = self.doc.createElement('cbc:ID')
        cbcID.setAttribute('schemeID', tipo_doc_ident)
        text = self.doc.createTextNode(num_doc_ident)
        cbcID.appendChild(text)
        cacPartyIdentification.appendChild(cbcID)

        cacParty = self.doc.createElement('cac:Party')
        cacCarrierParty.appendChild(cacParty)

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyName = self.doc.createElement('cac:PartyName')
        cacParty.appendChild(cacPartyName)
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(nombre)
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)

        return cacCarrierParty


    def cacShipmentStage(self, id, type_transport, star_date, cacCarrierParty, placa):
        cacShipmentStage = self.doc.createElement('cac:ShipmentStage')
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        ID.appendChild(text)
        cacShipmentStage.appendChild(ID)

        cbcTransportModeCode = self.doc.createElement("cbc:TransportModeCode")
        text = self.doc.createTextNode(type_transport)
        cbcTransportModeCode.appendChild(text)
        cacShipmentStage.appendChild(cbcTransportModeCode)

        cacTransitPeriod = self.doc.createElement("cac:TransitPeriod")
        cacShipmentStage.appendChild(cacTransitPeriod)

        cbcStartDate = self.doc.createElement("cbc:StartDate")
        text = self.doc.createTextNode(star_date)
        cbcStartDate.appendChild(text)
        cacTransitPeriod.appendChild(cbcStartDate)

        cacShipmentStage.appendChild(cacCarrierParty)

        cacTransportMeans = self.doc.createElement("cac:TransportMeans")
        cacShipmentStage.appendChild(cacTransportMeans)

        cacRoadTransport = self.doc.createElement("cac:RoadTransport")
        cacTransportMeans.appendChild(cacRoadTransport)

        cbcLicensePlateID = self.doc.createElement("cac:LicensePlateID")
        text = self.doc.createTextNode(placa)
        cbcLicensePlateID.appendChild(text)
        cacRoadTransport.appendChild(cbcLicensePlateID)

        return cacShipmentStage

    def cacShipmentStage_addDrive(self, root, tipoDoc, numDoc):
        cacShipmentStages = root.getElementsByTagName("cac:ShipmentStage")

        if cacShipmentStages:
            cacDriverPerson = self.doc.createElement("cac:DriverPerson")
            cacShipmentStages.appendChild(cacDriverPerson)

            cbcID = self.doc.createElement("cbc:ID")
            cbcID.setAttribute("schemeID",tipoDoc)
            text = self.doc.createTextNode(numDoc)
            cbcID.appendChild(text)
            cacDriverPerson.appendChild(cbcID)

        return root

    def cacDeliveryAddress(self, ubigeo, direccion):
        cacDeliveryAddress = self.doc.createElement("cac:DeliveryAddress")

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo)
        cbcID.appendChild(text)
        cacDeliveryAddress.appendChild(cbcID)

        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion)
        cbcStreetName.appendChild(text)
        cacDeliveryAddress.appendChild(cbcStreetName)

        return cacDeliveryAddress

    def cacTransportHandlingUnit(self, placa, placa_secundaria):
        cacTransportHandlingUnit = self.doc.createElement("cac:TransportHandlingUnit")

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(placa)
        cbcID.appendChild(text)
        cacTransportHandlingUnit.appendChild(cbcID)

        cacTransportEquipment = self.doc.createElement("cac:TransportEquipment")
        cacTransportHandlingUnit.appendChild(cacTransportEquipment)
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(placa_secundaria)
        cbcID.appendChild(text)
        cacTransportEquipment.appendChild(cbcID)

        return cacTransportHandlingUnit

    def cacOriginAddress(self, ubigeo, direccion):
        cacOriginAddress = self.doc.createElement("cac:DeliveryAddress")

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo)
        cbcID.appendChild(text)
        cacOriginAddress.appendChild(cbcID)

        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion)
        cbcStreetName.appendChild(text)
        cacOriginAddress.appendChild(cbcStreetName)

        return cacOriginAddress

    def cacShipment(self, id, motivo_traslado, description, flag_trasbordo, peso_bruto_gre, unit_gre, nro_bultos, cacShipmentStage, cacDeliveryAddress, cacTransportHandlingUnit, cacOriginAddress, id_puerto_ini, description_puerto_ini, id_puerto_fin):
        cacShipment = self.doc.createElement('cac:Shipment')
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        ID.appendChild(text)
        cacShipment.appendChild(ID)

        cbcHandlingCode = self.doc.createElement("cbc:HandlingCode")
        text = self.doc.createTextNode(motivo_traslado)
        cbcHandlingCode.appendChild(text)
        cacShipment.appendChild(cbcHandlingCode)

        cbcInformation = self.doc.createElement("cbc:Information")
        text = self.doc.createTextNode(description)
        cbcInformation.appendChild(text)
        cacShipment.appendChild(cbcInformation)

        cbcSplitConsignmentIndicator = self.doc.createElement("cbc:SplitConsignmentIndicator")
        text = self.doc.createTextNode(flag_trasbordo)
        cbcSplitConsignmentIndicator.appendChild(text)
        cacShipment.appendChild(cbcSplitConsignmentIndicator)

        cbcGrossWeightMeasure = self.doc.createElement("cbc:GrossWeightMeasure")
        cbcGrossWeightMeasure.setAttribute("unitCode", unit_gre)
        text = self.doc.createTextNode(peso_bruto_gre)
        cbcGrossWeightMeasure.appendChild(text)
        cacShipment.appendChild(cbcGrossWeightMeasure)

        cbcTotalTransportHandlingUnitQuantity = self.doc.createElement("cbc:TotalTransportHandlingUnitQuantity")
        text = self.doc.createTextNode(str(nro_bultos))
        cbcTotalTransportHandlingUnitQuantity.appendChild(text)
        cacShipment.appendChild(cbcTotalTransportHandlingUnitQuantity)

        cacShipment.appendChild(cacShipmentStage)
        cacShipment.appendChild(cacDeliveryAddress)
        cacShipment.appendChild(cacTransportHandlingUnit)
        cacShipment.appendChild(cacOriginAddress)

        cacLoadingPortLocation = self.doc.createElement("cac:LoadingPortLocation")
        cacShipment.appendChild(cacLoadingPortLocation)
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(id_puerto_ini))
        cbcID.appendChild(text)
        cacLoadingPortLocation.appendChild(cbcID)
        cbcDescription = self.doc.createElement("cbc:Description")
        text = self.doc.createTextNode(description_puerto_ini)
        cbcDescription.appendChild(text)
        cacLoadingPortLocation.appendChild(cbcDescription)

        cacFirstArrivalPortLocation = self.doc.createElement("cac:FirstArrivalPortLocation")
        cacShipment.appendChild(cacFirstArrivalPortLocation)
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id_puerto_fin)
        cbcID.appendChild(text)
        cacFirstArrivalPortLocation.appendChild(cbcID)

        return cacShipment

    def cacItem(self, description, id_item):
        cacItem = self.doc.createElement('cac:Item')

        cbcDescription = self.doc.createElement("cbc:Description")
        text = self.doc.createTextNode(description)
        cbcDescription.appendChild(text)
        cacItem.appendChild(cbcDescription)

        cacSellersItemIdentification = self.doc.createElement("cac:SellersItemIdentification")
        cacItem.appendChild(cacSellersItemIdentification)
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id_item)
        cbcID.appendChild(text)
        cacSellersItemIdentification.appendChild(cbcID)

        return cacItem


    def DespatchLine(self, id, cantidad, UOM, cacItem):
        cacDespatchLine = self.doc.createElement('cac:DespatchLine')
        ID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(str(id))
        ID.appendChild(text)
        cacDespatchLine.appendChild(ID)

        cacDeliveredQuantity = self.doc.createElement("cac:DeliveredQuantity")
        cacDeliveredQuantity.setAttribute("unitCode", UOM)
        text = self.doc.createTextNode(str(cantidad))
        cacDeliveredQuantity.appendChild(text)
        cacDespatchLine.appendChild(cacDeliveredQuantity)

        cacOrderLineReference = self.doc.createElement("cac:OrderLineReference")
        cacDespatchLine.appendChild(cacOrderLineReference)
        cbcLineID = self.doc.createElement("cbc:LineID")
        text = self.doc.createTextNode(str(id))
        cbcLineID.appendChild(text)
        cacOrderLineReference.appendChild(cbcLineID)

        cacDespatchLine.appendChild(cacItem)

        return cacDespatchLine


    def sendBill(self, username, password, namefile, contentfile):
        Envelope = self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser", "http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse",
                              "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

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
        sendBill = self.doc.createElement("ser:sendBill")
        fileName = self.doc.createElement("fileName")
        text = self.doc.createTextNode(namefile)
        fileName.appendChild(text)
        contentFile = self.doc.createElement("contentFile")
        text = self.doc.createTextNode(contentfile)
        contentFile.appendChild(text)
        sendBill.appendChild(fileName)
        sendBill.appendChild(contentFile)
        Body.appendChild(sendBill)
        Envelope.appendChild(Body)

        return Envelope









