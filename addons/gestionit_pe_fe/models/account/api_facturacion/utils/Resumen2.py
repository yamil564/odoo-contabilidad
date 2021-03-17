#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom import minidom

class Resumen2:
    def __init__(self):
        self.doc = minidom.Document()
    
    def Root(self):
        root = self.doc.createElement('SummaryDocuments')
        self.doc.appendChild(root)
        
        root.setAttribute('xmlns', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SummaryDocuments-1')
        root.setAttribute('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        root.setAttribute('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        root.setAttribute('xmlns:ds', 'http://www.w3.org/2000/09/xmldsig#')
        root.setAttribute('xmlns:ext', 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2')
        root.setAttribute('xmlns:sac', 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1')
        root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        return root
    
    def SummaryDocumentsLine(self, line_id, document_type, number, currency, type_doc_clt, num_doc_clt, 
                            gravado, inafecto, exonerada, exportacion, gratuita, amount_tax, codigo_operacion):
        SummaryDocumentsLine = self.doc.createElement('sac:SummaryDocumentsLine')

        LineID = self.doc.createElement('cbc:LineID')
        text = self.doc.createTextNode(str(line_id))
        LineID.appendChild(text)
        SummaryDocumentsLine.appendChild(LineID)
        
        DocumentTypeCode = self.doc.createElement('cbc:DocumentTypeCode')
        text = self.doc.createTextNode(document_type)
        DocumentTypeCode.appendChild(text)
        SummaryDocumentsLine.appendChild(DocumentTypeCode)

        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(number)
        cbcID.appendChild(text)
        SummaryDocumentsLine.appendChild(cbcID)

        SummaryDocumentsLine.appendChild(self.AccountingCustomerParty(type_doc=type_doc_clt,number_doc=num_doc_clt))

        cacStatus = self.doc.createElement('cac:Status')
        SummaryDocumentsLine.appendChild(cacStatus)

        cbcConditionCode = self.doc.createElement("cbc:ConditionCode")
        text = self.doc.createTextNode(codigo_operacion)
        cbcConditionCode.appendChild(text)
        cacStatus.appendChild(cbcConditionCode)


        total = gravado + amount_tax + inafecto + exonerada
        TotalAmount = self.doc.createElement('sac:TotalAmount')
        TotalAmount.setAttribute('currencyID', currency)
        text = self.doc.createTextNode(str(total))
        TotalAmount.appendChild(text)
        SummaryDocumentsLine.appendChild(TotalAmount)

        if gravado > 0.0:
            BillingPayment_1 = self.doc.createElement('sac:BillingPayment')
            PaidAmount_1 = self.doc.createElement('cbc:PaidAmount')
            PaidAmount_1.setAttribute('currencyID', currency)
            text = self.doc.createTextNode(str(gravado))
            PaidAmount_1.appendChild(text)
            InstructionID_1 = self.doc.createElement('cbc:InstructionID')
            text = self.doc.createTextNode('01')
            InstructionID_1.appendChild(text)
            BillingPayment_1.appendChild(PaidAmount_1)
            BillingPayment_1.appendChild(InstructionID_1)
            SummaryDocumentsLine.appendChild(BillingPayment_1)

        if exonerada > 0.0:
            BillingPayment_2 = self.doc.createElement('sac:BillingPayment')
            PaidAmount_2 = self.doc.createElement('cbc:PaidAmount')
            PaidAmount_2.setAttribute('currencyID', currency)
            text = self.doc.createTextNode(str(exonerada))
            PaidAmount_2.appendChild(text)
            InstructionID_2 = self.doc.createElement('cbc:InstructionID')
            text = self.doc.createTextNode('02')
            InstructionID_2.appendChild(text)
            BillingPayment_2.appendChild(PaidAmount_2)
            BillingPayment_2.appendChild(InstructionID_2)
            SummaryDocumentsLine.appendChild(BillingPayment_2)

        if inafecto>0.0:
            BillingPayment_3 = self.doc.createElement('sac:BillingPayment')
            PaidAmount_3 = self.doc.createElement('cbc:PaidAmount')
            PaidAmount_3.setAttribute('currencyID', currency)
            text = self.doc.createTextNode(str(inafecto))
            PaidAmount_3.appendChild(text)
            InstructionID_3 = self.doc.createElement('cbc:InstructionID')
            text = self.doc.createTextNode('03')
            InstructionID_3.appendChild(text)
            BillingPayment_3.appendChild(PaidAmount_3)
            BillingPayment_3.appendChild(InstructionID_3)
            SummaryDocumentsLine.appendChild(BillingPayment_3)

        if exportacion > 0.0:
            BillingPayment_4 = self.doc.createElement('sac:BillingPayment')
            PaidAmount_4 = self.doc.createElement('cbc:PaidAmount')
            PaidAmount_4.setAttribute('currencyID', currency)
            text = self.doc.createTextNode(str(exportacion))
            PaidAmount_4.appendChild(text)
            InstructionID_4 = self.doc.createElement('cbc:InstructionID')
            text = self.doc.createTextNode('04')
            InstructionID_4.appendChild(text)
            BillingPayment_4.appendChild(PaidAmount_4)
            BillingPayment_4.appendChild(InstructionID_4)
            SummaryDocumentsLine.appendChild(BillingPayment_4)

        if gratuita > 0.0:
            BillingPayment_5 = self.doc.createElement('sac:BillingPayment')
            PaidAmount_5 = self.doc.createElement('cbc:PaidAmount')
            PaidAmount_5.setAttribute('currencyID', currency)
            text = self.doc.createTextNode(str(gratuita))
            PaidAmount_5.appendChild(text)
            InstructionID_5 = self.doc.createElement('cbc:InstructionID')
            text = self.doc.createTextNode('05')
            InstructionID_5.appendChild(text)
            BillingPayment_5.appendChild(PaidAmount_5)
            BillingPayment_5.appendChild(InstructionID_5)
            SummaryDocumentsLine.appendChild(BillingPayment_5)

        return SummaryDocumentsLine

    def AccountingCustomerParty(self, type_doc, number_doc):
        cacAccountingCustomerParty = self.doc.createElement('cac:AccountingCustomerParty')

        cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
        text = self.doc.createTextNode(str(number_doc))
        cbcCustomerAssignedAccountID.appendChild(text)
        cacAccountingCustomerParty.appendChild(cbcCustomerAssignedAccountID)

        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(type_doc)
        cbcAdditionalAccountID.appendChild(text)
        cacAccountingCustomerParty.appendChild(cbcAdditionalAccountID)

        return cacAccountingCustomerParty

    """
            cac:TaxTotal                                        1..n    Informacion acerca del importe total de un tipo particular de impuesto. Una repeticion por IGV, ISC
                cbc:TaxAmount/@currencyID                       1       Importe total de un tributo para este item
                cac:TaxSubtotal
                    cbc:TaxAmount/@currencyID                   1       Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
                    cac:TaxCategory/cbc:TaxExemptionReasonCode  1       Afectacion al IGV (catalogo No 7)
                    cac:TaxCategory/cbc:TierRange               1       Sistema de ISC (catalogo No 8)
                    cac:TaxCategory/cac:TaxScheme/cbc:ID        1       Identificaion del tributo segun el (catalogo No 5)
                    cac:TaxCategory/cac:TaxScheme/cbc:Name      1       Nombre del Tributo (IGV, ISC)
        """

    def cacTaxTotal(self, tax):
        currencyID = tax["currencyID"]
        TaxAmount = tax["TaxAmount"]
        TaxExemptionReasonCode = tax["TaxExemptionReasonCode"]
        TierRange = tax["TierRange"]
        tributo_codigo = tax["tributo_codigo"]
        tributo_nombre = tax["tributo_nombre"]
        tributo_tipo_codigo = tax["tributo_tipo_codigo"]

        # Importe total de un tributo para este item
        cacTaxTotal = self.doc.createElement('cac:TaxTotal')

        # Monto de IGV de la linea
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)

        cacTaxSubtotal = self.doc.createElement('cac:TaxSubtotal')

        # Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory = self.doc.createElement('cac:TaxCategory')
        """
        if tributo_codigo == "1000":
            # Afectacion del IGV  (Catalogo No. 07)
            cbcTaxExemptionReasonCode = self.doc.createElement('cbc:TaxExemptionReasonCode')
            text = self.doc.createTextNode(TaxExemptionReasonCode)
            cbcTaxExemptionReasonCode.appendChild(text)
            cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)
        if tributo_codigo == "2000":
            # Sistema de ISC (Catalogo No 08)
            cbcTierRange = self.doc.createElement("cbc:TierRange")
            text = self.doc.createTextNode(TierRange)
            cbcTierRange.appendChild(text)
            cacTaxCategory.appendChild(cbcTierRange)
        """
        
        # Tipo de Tributo (Catalogo No. 05)
        """
            codigo  Descripcion                              Nombre del Tipo de Codigo
            1000 	IGV    IMPUESTO GENERAL A LAS VENTAS     VAT
            2000 	ISC    IMPUESTO SELECTIVO AL CONSUMO     EXC
            9999 	OTROS CONCEPTOS DE PAGO				     OTH
        """
        cacTaxScheme = self.doc.createElement('cac:TaxScheme')

        # Tipo de Tributo:Codigo
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(tributo_codigo)
        cbcID.appendChild(text)
        cacTaxScheme.appendChild(cbcID)

        # Tipo de Tributo: Nombre
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(tributo_nombre)
        cbcName.appendChild(text)

        cacTaxScheme.appendChild(cbcName)

        # Tipo de Tributo: Tipo de Codigo
        cbcTaxTypeCode = self.doc.createElement('cbc:TaxTypeCode')
        text = self.doc.createTextNode(tributo_tipo_codigo)
        cbcTaxTypeCode.appendChild(text)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cacTaxScheme)
        cacTaxSubtotal.appendChild(cacTaxCategory)
        cacTaxTotal.appendChild(cacTaxSubtotal)

        return cacTaxTotal


    def cacBillingReference(self, number, type_doc):
        cacBillingReference = self.doc.createElement("cac:BillingReference")

        cacInvoiceDocumentReference = self.doc.createElement("cac:InvoiceDocumentReference")
        cacBillingReference.appendChild(cacInvoiceDocumentReference)

        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(number)
        cbcID.appendChild(text)
        cacInvoiceDocumentReference.appendChild(cbcID)

        cbcDocumentTypeCode = self.doc.createElement("cbc:DocumentTypeCode")
        text = self.doc.createTextNode(type_doc)
        cbcDocumentTypeCode.appendChild(text)
        cacInvoiceDocumentReference.appendChild(cbcDocumentTypeCode)

        return cacBillingReference

    def sacSUNATPerceptionSummaryDocumentReference(self, code_percepcion, tasa_percepcion, monto_percepcion, monto_total_w_percepcion, base_imponible):
        sacSUNATPerceptionSummaryDocumentReference = self.doc.createElement("sac:SUNATPerceptionSummaryDocumentReference")

        sacSUNATPerceptionSystemCode = self.doc.createElement("sac:SUNATPerceptionSystemCode")
        text = self.doc.createTextNode(str(code_percepcion))
        sacSUNATPerceptionSystemCode.appendChild(text)
        sacSUNATPerceptionSummaryDocumentReference.appendChild(sacSUNATPerceptionSystemCode)

        sacSUNATPerceptionPercent = self.doc.createElement("sac:SUNATPerceptionPercent")
        text = self.doc.createTextNode(str(tasa_percepcion))
        sacSUNATPerceptionPercent.appendChild(text)
        sacSUNATPerceptionSummaryDocumentReference.appendChild(sacSUNATPerceptionPercent)

        cbcTotalInvoiceAmount = self.doc.createElement("cbc:TotalInvoiceAmount")
        text = self.doc.createTextNode(str(monto_percepcion))
        cbcTotalInvoiceAmount.appendChild(text)
        sacSUNATPerceptionSummaryDocumentReference.appendChild(cbcTotalInvoiceAmount)

        sacSUNATTotalCashed = self.doc.createElement("sac:SUNATTotalCashed")
        text = self.doc.createTextNode(str(monto_total_w_percepcion))
        sacSUNATTotalCashed.appendChild(text)
        sacSUNATPerceptionSummaryDocumentReference.appendChild(sacSUNATTotalCashed)

        cbcTaxableAmount = self.doc.createElement("cbc:TaxableAmount")
        text = self.doc.createTextNode(str(monto_total_w_percepcion))
        cbcTaxableAmount.appendChild(text)
        sacSUNATPerceptionSummaryDocumentReference.appendChild(cbcTaxableAmount)

        return sacSUNATPerceptionSummaryDocumentReference

    def cacAllowanceCharge(self, monto, currency):
        cacAllowanceCharge = self.doc.createElement('cac:AllowanceCharge')
        ChargeIndicator = self.doc.createElement('cbc:ChargeIndicator')
        text = self.doc.createTextNode('true')
        ChargeIndicator.appendChild(text)
        Amount = self.doc.createElement('cbc:Amount')
        Amount.setAttribute('currencyID', currency)
        text = self.doc.createTextNode(str(monto))
        Amount.appendChild(text)
        cacAllowanceCharge.appendChild(ChargeIndicator)
        cacAllowanceCharge.appendChild(Amount)
        return cacAllowanceCharge

    def firma(self,id):
        UBLExtensions = self.doc.createElement("ext:UBLExtensions")

        UBLExtension = self.doc.createElement("ext:UBLExtension")
        
        ExtensionContent = self.doc.createElement("ext:ExtensionContent")
        
        Signature = self.doc.createElement("ds:Signature")
        Signature.setAttribute("Id", id)
        
        ExtensionContent.appendChild(Signature)
        UBLExtension.appendChild(ExtensionContent)
        UBLExtensions.appendChild(UBLExtension)

        return UBLExtensions

    def Signature(self,Id,ruc,razon_social,uri):
        Signature=self.doc.createElement("cac:Signature")
        ID=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(Id)
        ID.appendChild(text)
        Signature.appendChild(ID)

        SignatoryParty=self.doc.createElement("cac:SignatoryParty")
        PartyIdentification=self.doc.createElement("cac:PartyIdentification")
        RUC=self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(ruc)
        RUC.appendChild(text)
        PartyIdentification.appendChild(RUC)
        PartyName=self.doc.createElement("cac:PartyName")
        Name=self.doc.createElement("cbc:Name")
        text=self.doc.createTextNode(razon_social)
        Name.appendChild(text)
        PartyName.appendChild(Name)
        SignatoryParty.appendChild(PartyIdentification)
        SignatoryParty.appendChild(PartyName)

        Signature.appendChild(SignatoryParty)

        DigitalSignatureAttachment=self.doc.createElement("cac:DigitalSignatureAttachment")
        ExternalReference=self.doc.createElement("cac:ExternalReference")
        URI=self.doc.createElement("cbc:URI")
        text=self.doc.createTextNode(uri)
        URI.appendChild(text)
        ExternalReference.appendChild(URI)
        DigitalSignatureAttachment.appendChild(ExternalReference)

        Signature.appendChild(DigitalSignatureAttachment)

        return Signature
    # def UBLExtensions(self):
    #     UBLExtensions = self.doc.createElement('ext:UBLExtensions')
    #     UBLExtensions.appendChild(self.UBLExtension)

    #     return UBLExtensions

    # def UBLExtension(self):
    #     UBLExtension = self.doc.createElement('ext:UBLExtension')
    #     ExtensionContent = self.doc.createElement('ext:ExtensionContent')


    #     #UBLExtension.appendChild(self.UBLExtension)

    #     return UBLExtension

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

    def cacAccountingSupplierParty(self,num_doc_ident,
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
    
    
    def sendBill(self,username,password,namefile,contentfile):
        Envelope=self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv","http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser","http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header=self.doc.createElement("soapenv:Header")
        Security=self.doc.createElement("wsse:Security")
        UsernameToken=self.doc.createElement("wsse:UsernameToken")
        Username=self.doc.createElement("wsse:Username")
        text=self.doc.createTextNode(username)
        Username.appendChild(text)
        Password=self.doc.createElement("wsse:Password")
        text=self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body=self.doc.createElement("soapenv:Body")
        sendBill=self.doc.createElement("ser:sendSummary")
        fileName=self.doc.createElement("fileName")
        text=self.doc.createTextNode(namefile)
        fileName.appendChild(text)
        contentFile=self.doc.createElement("contentFile")
        text=self.doc.createTextNode(contentfile)
        contentFile.appendChild(text)
        sendBill.appendChild(fileName)
        sendBill.appendChild(contentFile)
        Body.appendChild(sendBill)
        Envelope.appendChild(Body)

        return Envelope

    def getStatus(self, username, password, nro_ticket):
        Envelope=self.doc.createElement("soapenv:Envelope")
        Envelope.setAttribute("xmlns:soapenv","http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:ser","http://service.sunat.gob.pe")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header=self.doc.createElement("soapenv:Header")
        Security=self.doc.createElement("wsse:Security")
        UsernameToken=self.doc.createElement("wsse:UsernameToken")
        Username=self.doc.createElement("wsse:Username")
        text=self.doc.createTextNode(username)
        Username.appendChild(text)
        Password=self.doc.createElement("wsse:Password")
        text=self.doc.createTextNode(password)
        Password.appendChild(text)
        UsernameToken.appendChild(Username)
        UsernameToken.appendChild(Password)
        Security.appendChild(UsernameToken)
        Header.appendChild(Security)
        Envelope.appendChild(Header)

        Body=self.doc.createElement("soapenv:Body")
        getStatus=self.doc.createElement("ser:getStatus")
        ticket=self.doc.createElement("ticket")
        text=self.doc.createTextNode(nro_ticket)
        ticket.appendChild(text)
        getStatus.appendChild(ticket)
        Body.appendChild(getStatus)
        Envelope.appendChild(Body)

        return Envelope
