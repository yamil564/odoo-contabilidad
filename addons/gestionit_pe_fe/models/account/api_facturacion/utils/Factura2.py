from xml.dom import minidom

class Factura2:
    def __init__(self):
        self.doc = minidom.Document()

    def Root(self):
        root = self.doc.createElement('Invoice')
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
    def OperacionID(self, id, ):
        cbcID = self.doc.createElement('cbc:ProfileID')
        cbcID.setAttribute("schemeName", "SUNAT:Identificador de Tipo de Operación")
        cbcID.setAttribute("schemeAgencyName", "PE:SUNAT")
        cbcID.setAttribute("schemeURI", "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo17")
        text = self.doc.createTextNode(str(id))
        cbcID.appendChild(text)
        return cbcID

    # Numeracion, conformada por serie y numero correlativo
    def ID(self, id):
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(id)
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

    def DueDate(self, dueDate):
        cbcPaymentMeans = self.doc.createElement("cbc:DueDate")
        text = self.doc.createTextNode(dueDate)
        cbcPaymentMeans.appendChild(text)
        return cbcPaymentMeans

    def invoiceTypeCode(self, invoicetypecode):
        cbcInvoiceTypeCode = self.doc.createElement('cbc:InvoiceTypeCode')
        cbcInvoiceTypeCode.setAttribute("listAgencyName", "PE:SUNAT")
        cbcInvoiceTypeCode.setAttribute("listName", "SUNAT:Identificador de Tipo de Documento")
        cbcInvoiceTypeCode.setAttribute("listURI", "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01")
        text = self.doc.createTextNode(str(invoicetypecode))
        cbcInvoiceTypeCode.appendChild(text)
        return cbcInvoiceTypeCode


    ## VERSION 2
    def cbcNote(self, code_note, note):
        cbcNote = self.doc.createElement('cbc:Note')
        cbcNote.setAttribute("languageLocaleID", code_note)
        text = self.doc.createTextNode(note)
        cbcNote.appendChild(text)
        return cbcNote

    def documentCurrencyCode(self, documentcurrencycode):
        cbcDocumentCurrencyCode = self.doc.createElement('cbc:DocumentCurrencyCode')
        cbcDocumentCurrencyCode.setAttribute("listID", "ISO 4217 Alpha")
        cbcDocumentCurrencyCode.setAttribute("listName", "Currency")
        cbcDocumentCurrencyCode.setAttribute("listAgencyName", "United Nations Economic Commission for Europe")
        text = self.doc.createTextNode(documentcurrencycode)
        cbcDocumentCurrencyCode.appendChild(text)
        return cbcDocumentCurrencyCode

    ## VERSION 2
    def cacOrderReference(self, nro_order_sale):
        cacOrderReference = self.doc.createElement('cac:OrderReference')
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(str(nro_order_sale))
        cbcID.appendChild(text)
        cacOrderReference.appendChild(cbcID)
        return cacOrderReference

    def cbcLineCountNumeric(self, nro_items):
        cbcLineCountNumeric = self.doc.createElement('cbc:LineCountNumeric')
        text = self.doc.createTextNode(str(nro_items))
        cbcLineCountNumeric.appendChild(text)
        return cbcLineCountNumeric

    def cacDespatchDocumentReference(self, id, typeDocument):
        cacDespatchDocumentReference = self.doc.createElement('cac:DespatchDocumentReference')
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(id)
        cbcID.appendChild(text)
        cacDespatchDocumentReference.appendChild(cbcID)

        cbcDocumentTypeCode = self.doc.createElement("cbc:DocumentTypeCode")
        cbcDocumentTypeCode.setAttribute("listAgencyName", "PE:SUNAT")
        cbcDocumentTypeCode.setAttribute("listName", "SUNAT:Identificador de guía relacionada")
        cbcDocumentTypeCode.setAttribute("listURI", "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01")
        text = self.doc.createTextNode(typeDocument)
        cbcDocumentTypeCode.appendChild(text)
        cacDespatchDocumentReference.appendChild(cbcDocumentTypeCode)
        return cacDespatchDocumentReference


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

    def InvoiceRoot(self, rootXML, versionid, customizationid, tipo_operacion, id,
                    issuedate, issuetime, due_date, invoicetypecode,
                    documentcurrencycode, nro_order_sale, nro_items, notes={}):
        r = rootXML
        r.appendChild(self.UBLVersion(versionid))
        r.appendChild(self.CustomizationID(customizationid))
        r.appendChild(self.OperacionID(tipo_operacion))
        r.appendChild(self.ID(id))
        r.appendChild(self.issueDate(issuedate))
        if issuetime:
            r.appendChild(self.issueTime(issuetime))
        r.appendChild(self.DueDate(due_date))
        r.appendChild(self.invoiceTypeCode(invoicetypecode))
        if notes:
            for note in notes:
                r.appendChild(self.cbcNote(note, notes[note]))
        r.appendChild(self.documentCurrencyCode(documentcurrencycode))
        r.appendChild(self.cbcLineCountNumeric(nro_items))
        r.appendChild(self.cacOrderReference(nro_order_sale))
        return r

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
    DatosProveedor:Datos del Emisor del documento

    Parametros:
       num_doc_ident: Numero de Documento de Identidad
       tipo_doc_ident: Tipo de Documento de Identificacion
       nombre_comercial: Nombre del Comercio
       razon_social: Razon Social
       codigo_local: codigo del Domicilio Fiscal o Anexo
    devuelve:
        XML cac:AccountingSupplierParty  con datos del Emisor
    """

    def cacAccountingSupplierParty(self, num_doc_ident,
                                   tipo_doc_ident,
                                   nombre_comercial,
                                   razon_social,
                                   codigo_local):
        cacAccountingSupplierParty = self.doc.createElement('cac:AccountingSupplierParty')



        cacParty = self.doc.createElement('cac:Party')
        cacAccountingSupplierParty.appendChild(cacParty)

        cacPartyName = self.doc.createElement('cac:PartyName')
        cacParty.appendChild(cacPartyName)

        # Nombre Comercial
        cbcName = self.doc.createElement('cbc:Name')
        text = self.doc.createTextNode(str(nombre_comercial))
        cbcName.appendChild(text)
        cacPartyName.appendChild(cbcName)

        cacPartyTaxScheme = self.doc.createElement('cac:PartyTaxScheme')
        cacParty.appendChild(cacPartyTaxScheme)

        # Razon Social
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(razon_social)
        cbcRegistrationName.appendChild(text)
        cacPartyTaxScheme.appendChild(cbcRegistrationName)

        # Datos de Compania
        cbcCompanyID = self.doc.createElement('cbc:CompanyID')
        cbcCompanyID.setAttribute('schemeID', tipo_doc_ident)
        cbcCompanyID.setAttribute('schemeName', "SUNAT:Identificador de Documento de Identidad")
        cbcCompanyID.setAttribute('schemeAgencyName', "PE:SUNAT")
        cbcCompanyID.setAttribute('schemeURI', "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06")
        text = self.doc.createTextNode(num_doc_ident)
        cbcCompanyID.appendChild(text)
        cacPartyTaxScheme.appendChild(cbcCompanyID)

        cacRegistrationAddress = self.doc.createElement('cac:RegistrationAddress')
        cacPartyTaxScheme.appendChild(cacRegistrationAddress)

        cbcAddressTypeCode = self.doc.createElement('cbc:AddressTypeCode')
        cacRegistrationAddress.appendChild(cbcAddressTypeCode)
        text = self.doc.createTextNode(codigo_local)
        cbcAddressTypeCode.appendChild(text)


        return cacAccountingSupplierParty

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
    DatosCliente: Datos del Adquiriente o Usuario

    Parametros:
        num_doc_identidad: Numero de documento de identidad
        tipo_doc_identidad: Tipo de Documento de identidad
        nombre_cliente:Apellidos y nombres o denominacion o razon social segun RUC
    devuelve:
        XML cac:AccountingCustomerParty  con datos del Cliente
    """

    def cacAccountCustomerParty(self, num_doc_identidad, tipo_doc_identidad, nombre_cliente):
        cacAccountingCustomerParty = self.doc.createElement('cac:AccountingCustomerParty')

        # Apellidos y nombres o denominacion o razon social segun RUC
        cacParty = self.doc.createElement('cac:Party')
        cacAccountingCustomerParty.appendChild(cacParty)

        cacPartyTaxScheme = self.doc.createElement('cac:PartyTaxScheme')
        cacParty.appendChild(cacPartyTaxScheme)

        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(nombre_cliente)
        cbcRegistrationName.appendChild(text)
        cacPartyTaxScheme.appendChild(cbcRegistrationName)

        # Datos de Compania Receptor
        if tipo_doc_identidad is not '-':
            cbcCompanyID = self.doc.createElement('cbc:CompanyID')
            cbcCompanyID.setAttribute('schemeID', tipo_doc_identidad)
            cbcCompanyID.setAttribute('schemeName', "SUNAT:Identificador de Documento de Identidad")
            cbcCompanyID.setAttribute('schemeAgencyName', "PE:SUNAT")
            cbcCompanyID.setAttribute('schemeURI', "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06")
            text = self.doc.createTextNode(num_doc_identidad)
            cbcCompanyID.appendChild(text)
            cacPartyTaxScheme.appendChild(cbcCompanyID)

        cacRegistrationAddress = self.doc.createElement('cac:RegistrationAddress')
        cacPartyTaxScheme.appendChild(cacRegistrationAddress)

        cbcAddressTypeCode = self.doc.createElement('cbc:AddressTypeCode')
        cacRegistrationAddress.appendChild(cbcAddressTypeCode)
        text = self.doc.createTextNode("-")
        cbcAddressTypeCode.appendChild(text)

        return cacAccountingCustomerParty



    def AllowanceCharge(self, discount, currencyID):
        cacAllowanceCharge = self.doc.createElement("cac:AllowanceCharge")

        cbcChargeIndicator = self.doc.createElement("cbc:ChargeIndicator")
        text = self.doc.createTextNode("false")
        cbcChargeIndicator.appendChild(text)

        cbcAllowanceChargeReasonCode=self.doc.createElement("cbc:AllowanceChargeReasonCode")
        text=self.doc.createTextNode("00")
        cbcAllowanceChargeReasonCode.appendChild(text)

        cbcAmount = self.doc.createElement("cbc:Amount")
        cbcAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(discount))
        cbcAmount.appendChild(text)

        cacAllowanceCharge.appendChild(cbcChargeIndicator)
        # cacAllowanceCharge.appendChild(cbcAllowanceChargeReasonCode)
        cacAllowanceCharge.appendChild(cbcAmount)

        return cacAllowanceCharge


    def TaxTotal(self, currencyID, TaxAmount):
        cacTaxTotal = self.doc.createElement("cac:TaxTotal")

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)
        return cacTaxTotal


    def cacTaxSubtotal(self, currencyID, TaxableAmount, TaxAmount, id_imp, tributo_id, tributo_nombre, tributo_codigo):
        cacTaxSubtotal = self.doc.createElement("cac:TaxSubtotal")

        cbcTaxableAmount = self.doc.createElement("cbc:TaxableAmount")
        cbcTaxableAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxableAmount))
        cbcTaxableAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxableAmount)

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory = self.doc.createElement("cac:TaxCategory")

        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID", "UN/ECE 5305")
        cbcID.setAttribute("schemeName", "Tax Category Identifier")
        cbcID.setAttribute("schemeAgencyName", "United Nations Economic Commission for Europe")
        text = self.doc.createTextNode(str(id_imp))
        cbcID.appendChild(text)
        cacTaxCategory.appendChild(cbcID)

        cacTaxScheme = self.doc.createElement("cac:TaxScheme")
        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID", "UN/ECE 5153")
        cbcID.setAttribute("schemeAgencyID", "6")
        text = self.doc.createTextNode(str(tributo_id))
        cbcID.appendChild(text)

        cbcName = self.doc.createElement("cbc:Name")
        text = self.doc.createTextNode(str(tributo_nombre))
        cbcName.appendChild(text)

        cbcTaxTypeCode = self.doc.createElement("cbc:TaxTypeCode")
        text = self.doc.createTextNode(str(tributo_codigo))
        cbcTaxTypeCode.appendChild(text)

        cacTaxScheme.appendChild(cbcID)
        cacTaxScheme.appendChild(cbcName)
        cacTaxScheme.appendChild(cbcTaxTypeCode)

        cacTaxCategory.appendChild(cacTaxScheme)

        cacTaxSubtotal.appendChild(cacTaxCategory)

        return cacTaxSubtotal


    def LegalMonetaryTotal(self, monto_antimp, MontoTotal, total_descuentos, currency_id, monto_incoterms):
        LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")

        LineExtensionAmount = self.doc.createElement("cbc:LineExtensionAmount")
        LineExtensionAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(monto_antimp))
        LineExtensionAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(LineExtensionAmount)

        TaxInclusiveAmount = self.doc.createElement("cbc:TaxInclusiveAmount")
        TaxInclusiveAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(MontoTotal))
        TaxInclusiveAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(TaxInclusiveAmount)

        AllowanceTotalAmount = self.doc.createElement("cbc:AllowanceTotalAmount")
        AllowanceTotalAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(total_descuentos))
        AllowanceTotalAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(AllowanceTotalAmount)

        if monto_incoterms != '0.0':
            ChargeTotalAmount = self.doc.createElement("cbc:ChargeTotalAmount")
            ChargeTotalAmount.setAttribute("currencyID", currency_id)
            text_i = self.doc.createTextNode(monto_incoterms)
            ChargeTotalAmount.appendChild(text_i)
            LegalMonetaryTotal.appendChild(ChargeTotalAmount)

        PayableAmount = self.doc.createElement("cbc:PayableAmount")
        PayableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(MontoTotal))
        PayableAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(PayableAmount)

        return LegalMonetaryTotal


    def InvoiceLine(self, ID, unitCode, quantity, currencyID, amount,
                    precio_unitario, no_onerosa, valor_unitario):
        cacIL = self.cacInvoiceLine(ID, unitCode, quantity, currencyID, amount)
        cacIL.appendChild(self.cacPricingReference(precio_unitario, currencyID, no_onerosa, valor_unitario))
        return cacIL

    """
            cac:InvoiceLine                         1..n    Items de Factura
                cbc:ID                              1       Numero de orden de Item
                cbc:InvoiceQuantity/@unitCode       0..1    Unidad de medida por item(UN/ECE rec20)
                cbc:InvoiceQuantity                 0..1    Cantidad de unidades por item
                cbc:LineExtensionAmount/@currencyID 1       Moneda e importe moentario que es el total de la linea de detalle
                                                            incluyendo variaciones de precio (subvenciones, cargoso o descuentos)
                                                            pero sin impuestos
        """

    def cacInvoiceLine(self, ID, unitCode, quantity, currencyID, amount):

        cacInvoiceLine = self.doc.createElement('cac:InvoiceLine')

        # Identificador de Item
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(ID)
        cbcID.appendChild(text)
        cacInvoiceLine.appendChild(cbcID)

        # Cantidad del Producto
        cbcInvoiceQuantity = self.doc.createElement('cbc:InvoicedQuantity')

        # Codigo de Unidad (Anexo 3)
        cbcInvoiceQuantity.setAttribute('unitCode', unitCode)
        cbcInvoiceQuantity.setAttribute('unitCodeListID', "UN/ECE rec 20")
        cbcInvoiceQuantity.setAttribute('unitCodeListID', " Europe")
        text = self.doc.createTextNode(quantity)
        cbcInvoiceQuantity.appendChild(text)
        cacInvoiceLine.appendChild(cbcInvoiceQuantity)

        # Valor de Venta por Item = valor Unitario*cantidad(Sin impuestos)
        cbcLineExtensionAmount = self.doc.createElement('cbc:LineExtensionAmount')
        cbcLineExtensionAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(amount)
        cbcLineExtensionAmount.appendChild(text)
        cacInvoiceLine.appendChild(cbcLineExtensionAmount)

        return cacInvoiceLine

    """
            cac:PricingReference                    Valores Unitarios               0..1
                cac:AlternativeConditionPrice                                       0..n
                    cbc:PriceAmount/@currencyID     Monto del valor Unitario       0..1
                    cbc:PriceTypeCode               Codigo del valor unitario       0..1
        """

    def cacPricingReference(self, precio_unitario, currencyID, no_onerosa, valor_unitario):
        # Valor referencial unitario por item en operaciones no onerosas y codigo
        cacPricingReference = self.doc.createElement('cac:PricingReference')

        cacAlternativeConditionPrice = self.doc.createElement('cac:AlternativeConditionPrice')
        # Monto de precio de venta
        cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
        cbcPriceAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(str(precio_unitario))
        cbcPriceAmount.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceAmount)

        # Codigo de Tipo de Precio de Venta (Catalogo 16)
        cbcPriceTypeCode = self.doc.createElement('cbc:PriceTypeCode')
        cbcPriceTypeCode.setAttribute("listName", "SUNAT:Indicador de Tipo de Precio")
        cbcPriceTypeCode.setAttribute("listAgencyName", "PE:SUNAT")
        cbcPriceTypeCode.setAttribute("listURI", "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo16")
        text = self.doc.createTextNode("01")
        cbcPriceTypeCode.appendChild(text)
        cacAlternativeConditionPrice.appendChild(cbcPriceTypeCode)
        cacPricingReference.appendChild(cacAlternativeConditionPrice)

        if no_onerosa:
            cacAlternativeConditionPrice02 = self.doc.createElement('cac:AlternativeConditionPrice')
            # Monto de precio de venta
            cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
            cbcPriceAmount.setAttribute('currencyID', currencyID)
            text = self.doc.createTextNode(str(valor_unitario))
            cbcPriceAmount.appendChild(text)
            cacAlternativeConditionPrice02.appendChild(cbcPriceAmount)

            # Codigo de Tipo de Precio de Venta (Catalogo 16)
            cbcPriceTypeCode = self.doc.createElement('cbc:PriceTypeCode')
            text = self.doc.createTextNode("02")
            cbcPriceTypeCode.appendChild(text)
            cacAlternativeConditionPrice02.appendChild(cbcPriceTypeCode)

            cacPricingReference.appendChild(cacAlternativeConditionPrice02)

        return cacPricingReference


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
        TaxableAmount = tax["TaxableAmount"]
        TaxExemptionReasonCode = tax["TaxExemptionReasonCode"]
        TierRange = tax["TierRange"]
        tributo_codigo = tax["tributo_codigo"]
        tributo_nombre = tax["tributo_nombre"]
        tributo_tipo_codigo = tax["tributo_tipo_codigo"]
        percent = tax["percent"]

        # Importe total de un tributo para este item
        cacTaxTotal = self.doc.createElement('cac:TaxTotal')

        # Monto de IGV de la linea
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)

        cacTaxSubtotal = self.doc.createElement('cac:TaxSubtotal')

        cbcTaxableAmount = self.doc.createElement('cbc:TaxableAmount')
        cbcTaxableAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxableAmount)
        cbcTaxableAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxableAmount)

        # Importe explicito a tributar ( = Tasa Porcentaje * Base Imponible)
        cbcTaxAmount = self.doc.createElement('cbc:TaxAmount')
        cbcTaxAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(TaxAmount)
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory = self.doc.createElement('cac:TaxCategory')
        cbcID = self.doc.createElement('cbc:ID')
        cbcID.setAttribute('schemeID', "UN/ECE 5305")
        cbcID.setAttribute('schemeAgencyID', "6")


        # Tipo de Tributo (Catalogo No. 05)
        """
           ID   codigo  Nombre      Descripcion                     Nombre del Tipo de Codigo
           S    1000    IGV         IMPUESTO GENERAL A LAS VENTAS   VAT
           S    2000    ISC         IMPUESTO SELECTIVO AL CONSUMO   EXC
           Z    9996    GRATUITO    OPERACONES GRATUITAS            FRE
           E    9997    EXONERADO   OPERACIONES EXONERADAS          VAT
           O    9998    INAFECTO    OPERACIONES INAFECTAS           FRE    
           S    9999    OTROS       CONCEPTOS DE PAGO				OTH
        """

        if tributo_codigo == "1000":
            # Afectacion del IGV  (Catalogo No. 07)
            text = self.doc.createTextNode("S")
            cbcID.appendChild(text)
        elif tributo_codigo == "2000":
            # Sistema de ISC (Catalogo No 08)
            text = self.doc.createTextNode("S")
            cbcID.appendChild(text)
        elif tributo_codigo == "9996":
            # Sistema de ISC (Catalogo No 08)
            text = self.doc.createTextNode("Z")
            cbcID.appendChild(text)
        elif tributo_codigo == "9997":
            # Sistema de ISC (Catalogo No 08)
            text = self.doc.createTextNode("E")
            cbcID.appendChild(text)
        elif tributo_codigo == "9998":
            # Sistema de ISC (Catalogo No 08)
            text = self.doc.createTextNode("O")
            cbcID.appendChild(text)
        elif tributo_codigo == "9999":
            # Sistema de ISC (Catalogo No 08)
            text = self.doc.createTextNode("S")
            cbcID.appendChild(text)
        cacTaxCategory.appendChild(cbcID)

        cbcPercent = self.doc.createElement("cbc:Percent")
        text = self.doc.createTextNode(percent)
        cbcPercent.appendChild(text)
        cacTaxCategory.appendChild(cbcPercent)

        cbcTaxExemptionReasonCode = self.doc.createElement("cbc:TaxExemptionReasonCode")
        cbcTaxExemptionReasonCode.setAttribute("listName", "SUNAT:Codigo de Tipo de Afectación del IGV")
        cbcTaxExemptionReasonCode.setAttribute("listAgencyName", "PE:SUNAT")
        cbcTaxExemptionReasonCode.setAttribute("listURI", "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07")
        text = self.doc.createTextNode(TaxExemptionReasonCode)
        cbcTaxExemptionReasonCode.appendChild(text)
        cacTaxCategory.appendChild(cbcTaxExemptionReasonCode)

        if tributo_codigo == "1000":
            cbcTierRange = self.doc.createElement('cbc:TierRange')
            text = self.doc.createTextNode(TierRange)
            cbcTierRange.appendChild(text)
            cacTaxCategory.appendChild(cbcTierRange)


        cacTaxScheme = self.doc.createElement('cac:TaxScheme')

        # Tipo de Tributo:Codigo
        cbcID = self.doc.createElement('cbc:ID')
        cbcID.setAttribute("schemeID", "UN/ECE 5153")
        cbcID.setAttribute("schemeName", "Tax Scheme Identifier")
        cbcID.setAttribute("schemeAgencyName", "United Nations Economic Commission for Europe")
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

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
        cac:item                                1
            cbc:Description                     0..n    Descripcion detallada del bien vendido o cedido en uso,
                                                        descripcion o tipo de servicio prestado por item
            cac:sellersItemIdentificaction      0..1    Identificador de elementos de item
            cbc:ID                              0..1    codigo del producto
    """

    def cacItem(self, productID, Description, productIDSunat):
        # Producto
        cacItem = self.doc.createElement('cac:Item')

        # Descripcion del Producto
        cbcDescription = self.doc.createElement('cbc:Description')
        text = self.doc.createTextNode(Description)
        cbcDescription.appendChild(text)
        cacItem.appendChild(cbcDescription)

        # Codigo de Producto
        cacSellersItemIdentification = self.doc.createElement('cac:SellersItemIdentification')
        cacItem.appendChild(cacSellersItemIdentification)
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(productID)
        cbcID.appendChild(text)
        cacSellersItemIdentification.appendChild(cbcID)

        #Codigo de Producto SUNAT
        cacCommodityClassification = self.doc.createElement('cac:CommodityClassification')
        cacItem.appendChild(cacCommodityClassification)
        cbcID = self.doc.createElement('cbc:ID')
        text = self.doc.createTextNode(productIDSunat)
        cbcID.appendChild(text)
        cacCommodityClassification.appendChild(cbcID)

        return cacItem

    """
            cac:price                   0..1
                cbc:priceAmount         1       Valores de venta unitarios por item(VU)
                                                no incluye impuestos
        """

    def cacPrice(self, priceAmount, currencyID):
        # Precio del Producto
        cacPrice = self.doc.createElement('cac:Price')
        cbcPriceAmount = self.doc.createElement('cbc:PriceAmount')
        cbcPriceAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(priceAmount)
        cbcPriceAmount.appendChild(text)
        cacPrice.appendChild(cbcPriceAmount)

        return cacPrice