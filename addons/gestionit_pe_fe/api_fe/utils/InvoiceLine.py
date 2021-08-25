from xml.dom import minidom


class Factura:
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

    def invoiceTypeCode(self, invoicetypecode):
        cbcInvoiceTypeCode = self.doc.createElement('cbc:InvoiceTypeCode')
        text = self.doc.createTextNode(str(invoicetypecode))
        cbcInvoiceTypeCode.appendChild(text)
        return cbcInvoiceTypeCode

    def documentCurrencyCode(self, documentcurrencycode):
        cbcDocumentCurrencyCode = self.doc.createElement('cbc:DocumentCurrencyCode')
        text = self.doc.createTextNode(documentcurrencycode)
        cbcDocumentCurrencyCode.appendChild(text)
        return cbcDocumentCurrencyCode

    def DespatchDocumentReference(self,numero_guia):
        DespatchDocumentReference = self.doc.createElement("cac:DespatchDocumentReference")

        ID = self.doc.createElement("cbc:ID")
        text=self.doc.createTextNode(str(numero_guia))
        ID.appendChild(text)

        DocumentTypeCode =self.doc.createElement("cbc:DocumentTypeCode")
        text=self.doc.createTextNode("09")
        DocumentTypeCode.appendChild(text)

        DespatchDocumentReference.appendChild(ID)
        DespatchDocumentReference.appendChild(DocumentTypeCode)

        return DespatchDocumentReference
        
    def PaymentDueDate(self, paymentduedate):
        cacPaymentMeans = self.doc.createElement("cac:PaymentMeans")
        cbcPaymentDueDate = self.doc.createElement("cbc:PaymentDueDate")
        text = self.doc.createTextNode(paymentduedate)
        cbcPaymentDueDate.appendChild(text)
        cacPaymentMeans.appendChild(cbcPaymentDueDate)
        return cacPaymentMeans

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

    def InvoiceRoot(self, rootXML, versionid, customizationid, id,
                    issuedate, issuetime, invoicetypecode,
                    documentcurrencycode, paymentduedate,numero_guia):
        r = rootXML
        # r.appendChild(self.firma())
        r.appendChild(self.UBLVersion(versionid))
        r.appendChild(self.CustomizationID(customizationid))
        # r.appendChild(self.OperacionID('02'))
        r.appendChild(self.ID(id))
        r.appendChild(self.issueDate(issuedate))
        if issuetime:
            r.appendChild(self.issueTime(issuetime))
        r.appendChild(self.invoiceTypeCode(invoicetypecode))
        r.appendChild(self.documentCurrencyCode(documentcurrencycode))
        
        if numero_guia:
            r.appendChild(self.DespatchDocumentReference(numero_guia))
        # if paymentduedate:
        #    r.appendChild(self.PaymentDueDate(str(paymentduedate)))
        return r

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

    """
    pago:Codigo de otros conceptos tributarios (Catalogo 14)
        codigo  Descripcion
        1001	Total valor de venta - operaciones gravadas
        1002	Total valor de venta - operaciones inafectas
        1003	Total valor de venta - operaciones exoneradas
        1004	Total valor de venta - operaciones gratuitas
        1005	Sub total de venta
        2001	Percepciones
        2002	Retenciones
        2003	Detracciones
        2004	Bonificaciones
        2005	Total descuentos
        3001	FISE (Ley 29852) Fondo Inclusion Social Energetico
    Parametros:
        arr_tipo_monetario:Arreglo de objetos de pago [{id:1001,monto:10.00}]
        arr_tipo_monetario:Arreglo de objetos de pago [{id:1001,value:10.00}]
    """

    def ExtensionContent(self, arr_tipo_monetario, arr_otros):
        extUBLExtension = self.doc.createElement('ext:UBLExtension')

        extExtensionContent = self.doc.createElement('ext:ExtensionContent')
        extUBLExtension.appendChild(extExtensionContent)

        # Informacion adicional de tipo monetario
        sacAdditionalInformation = self.doc.createElement('sac:AdditionalInformation')
        extExtensionContent.appendChild(sacAdditionalInformation)

        for monetario in arr_tipo_monetario:
            id = monetario["id"]
            monto = monetario["monto"]
            sacAdditionalMonetaryTotal = self.doc.createElement('sac:AdditionalMonetaryTotal')

            # Codigo del Concepto Adicional
            cbcID = self.doc.createElement('cbc:ID')
            text = self.doc.createTextNode(id)
            cbcID.appendChild(text)
            sacAdditionalMonetaryTotal.appendChild(cbcID)

            # Monto a Pagar
            cbcPayableAmount = self.doc.createElement('cbc:PayableAmount')
            cbcPayableAmount.setAttribute('currencyID', 'PEN')
            text = self.doc.createTextNode(monto)
            cbcPayableAmount.appendChild(text)
            sacAdditionalMonetaryTotal.appendChild(cbcPayableAmount)

            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal)

        for otro in arr_otros:
            # Informacion adicional de cualquier tipo
            sacAdditionalProperty = self.doc.createElement('sac:AdditionalProperty')

            # Codigo del concepto adicional
            cbcID = self.doc.createElement('cbc:ID')
            text = self.doc.createTextNode(otro["id"])
            cbcID.appendChild(text)
            sacAdditionalProperty.appendChild(cbcID)

            # Valor del Concepto
            cbcValue = self.doc.createElement('cbc:Value')
            text = self.doc.createTextNode(otro["value"])
            cbcValue.appendChild(text)
            sacAdditionalProperty.appendChild(cbcValue)

            sacAdditionalInformation.appendChild(sacAdditionalProperty)

        # extUBLExtensions.appendChild(firma())

        return extUBLExtension

    def UBLExtensions(self, arr_tipo_monetario, arr_otros):
        extUBLExtensions = self.doc.createElement('ext:UBLExtensions')
        extUBLExtensions.appendChild(self.ExtensionContent(arr_tipo_monetario, arr_otros))
        return extUBLExtensions

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

    def cacItem(self, productID, Description):
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
        # cbcPriceAmount.setAttribute('currencyID', 'PEN')
        cbcPriceAmount.setAttribute('currencyID', currencyID)
        text = self.doc.createTextNode(priceAmount)
        cbcPriceAmount.appendChild(text)
        cacPrice.appendChild(cbcPriceAmount)

        return cacPrice

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

    def AllowanceCharge(self, discount, currencyID):
        cacAllowanceCharge = self.doc.createElement("cac:AllowanceCharge")

        cbcChargeIndicator = self.doc.createElement("cbc:ChargeIndicator")
        text = self.doc.createTextNode("false")
        cbcChargeIndicator.appendChild(text)

        # cbcAllowanceChargeReasonCode=self.doc.createElement("cbc:AllowanceChargeReasonCode")
        # text=self.doc.createTextNode("00")
        # cbcAllowanceChargeReasonCode.appendChild(text)

        cbcAmount = self.doc.createElement("cbc:Amount")
        cbcAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(discount))
        cbcAmount.appendChild(text)

        cacAllowanceCharge.appendChild(cbcChargeIndicator)
        # cacAllowanceCharge.appendChild(cbcAllowanceChargeReasonCode)
        cacAllowanceCharge.appendChild(cbcAmount)

        return cacAllowanceCharge

    # def AllowanceCharge(self,discount,currencyID):
    #     cacAllowanceCharge=self.doc.createElement("cac:AllowanceCharge")
    #     cbcChargeIndicator=self.doc.createElement("cbc:ChargeIndicator")
    #     text=self.doc.createTextNode("false")
    #     cbcChargeIndicator.appendChild(text)
    #     cbcAmount=self.doc.createElement("cbc:Amount")
    #     cbcAmount.setAttribute("currencyID",currencyID)
    #     text=self.doc.createTextNode(str(discount))
    #     cbcAmount.appendChild(text)

    #     cacAllowanceCharge.appendChild(cbcChargeIndicator)
    #     cacAllowanceCharge.appendChild(cbcAmount)

    #     return cacAllowanceCharge

    def InvoiceLine(self, ID, unitCode, quantity, currencyID, amount,
                    precio_unitario, no_onerosa, valor_unitario):
        cacIL = self.cacInvoiceLine(ID, unitCode, quantity, currencyID, amount)
        cacIL.appendChild(self.cacPricingReference(precio_unitario, currencyID, no_onerosa, valor_unitario))
        return cacIL

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
       codigo_ubigeo: Codigo del ubigeo del Comercio
       nombre_direccion_full:  Direccion Completa y Detallada
       nombre_direccion_division: Urbanizacion o Zona
       nombre_departamento: Nombre del Departamento
       nombre_distrito: Nombre de Distrito
       nombre_proveedor: Nombre de Proveedor
       codigo_pais: Codigo del pais
    devuelve:
    	XML cac:AccountingSupplierParty  con datos del Emisor
    """

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

        # Apellidos y Nombres o Denominacion o Razon Social
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(str(nombre_proveedor))
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

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

        if tipo_doc_identidad is not '-':
            # Numero de documento de identidad
            cbcCustomerAssignedAccountID = self.doc.createElement('cbc:CustomerAssignedAccountID')
            text = self.doc.createTextNode(num_doc_identidad)
            cbcCustomerAssignedAccountID.appendChild(text)
            cacAccountingCustomerParty.appendChild(cbcCustomerAssignedAccountID)

        # Tipo de Documento de Identidad
        cbcAdditionalAccountID = self.doc.createElement('cbc:AdditionalAccountID')
        text = self.doc.createTextNode(tipo_doc_identidad)
        cbcAdditionalAccountID.appendChild(text)
        cacAccountingCustomerParty.appendChild(cbcAdditionalAccountID)

        # Apellidos y nombres o denominacion o razon social segun RUC
        cacParty = self.doc.createElement('cac:Party')
        cacAccountingCustomerParty.appendChild(cacParty)
        cacPartyLegalEntity = self.doc.createElement('cac:PartyLegalEntity')
        cacParty.appendChild(cacPartyLegalEntity)
        cbcRegistrationName = self.doc.createElement('cbc:RegistrationName')
        text = self.doc.createTextNode(nombre_cliente)
        cbcRegistrationName.appendChild(text)
        cacPartyLegalEntity.appendChild(cbcRegistrationName)

        return cacAccountingCustomerParty

    # def IncotermsTotal(self,MontoTotal,currency_id):
    #     LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")
    #     ChargeTotalAmount = self.doc.createElement("cbc:ChargeTotalAmount")
    #     ChargeTotalAmount.setAttribute("currencyID", currency_id)
    #     text = self.doc.createTextNode(str(MontoTotal))
    #     ChargeTotalAmount.appendChild(text)
    #     LegalMonetaryTotal.appendChild(ChargeTotalAmount)
    #     return LegalMonetaryTotal

    def LegalMonetaryTotal(self, MontoTotal, currency_id,total_anticipos=0,descuento_global=0):
        LegalMonetaryTotal = self.doc.createElement("cac:LegalMonetaryTotal")

        if descuento_global:
            AllowanceTotalAmount = self.doc.createElement("cbc:AllowanceTotalAmount")
            AllowanceTotalAmount.setAttribute("currencyID", currency_id)
            text_d = self.doc.createTextNode(str(descuento_global))
            AllowanceTotalAmount.appendChild(text_d)
            LegalMonetaryTotal.appendChild(AllowanceTotalAmount)
        
        if total_anticipos>0:
            PrepaidAmount = self.doc.createElement("cbc:PrepaidAmount")
            PrepaidAmount.setAttribute("currencyID", currency_id)
            text_d = self.doc.createTextNode(str(total_anticipos))
            PrepaidAmount.appendChild(text_d)
            LegalMonetaryTotal.appendChild(PrepaidAmount)
            

        PayableAmount = self.doc.createElement("cbc:PayableAmount")
        PayableAmount.setAttribute("currencyID", currency_id)
        text = self.doc.createTextNode(str(MontoTotal))
        PayableAmount.appendChild(text)
        LegalMonetaryTotal.appendChild(PayableAmount)

        return LegalMonetaryTotal
    
    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################
    """
                "mntAnticipado":250,
		    	"tipoDocumento":"01",
		    	"idRef":"FX10-00000002",
		    	"numDocEmisor":"10763104201",
		    	"tipoDocEmisor":"6"
    """
    def PrepaidPayment(self,mnt_anticipado,tipo_documento,id_ref,num_doc_emisor,tipo_doc_emisor,currencyID):
        cbcPrepaidAmount = self.doc.createElement("cac:PrepaidPayment")

        cbcID = self.doc.createElement("cbc:ID")
        cbcID.setAttribute("schemeID",tipo_documento)
        text = self.doc.createTextNode(id_ref)
        cbcID.appendChild(text)

        cbcPaidAmount = self.doc.createElement("cbc:PaidAmount")
        cbcPaidAmount.setAttribute("currencyID",currencyID)
        text = self.doc.createTextNode(str(round(mnt_anticipado,4)))
        cbcPaidAmount.appendChild(text)

        cbcInstructionID = self.doc.createElement("cbc:InstructionID")
        cbcInstructionID.setAttribute("schemeID",tipo_doc_emisor)
        text = self.doc.createTextNode(num_doc_emisor)
        cbcInstructionID.appendChild(text)

        cbcPrepaidAmount.appendChild(cbcID)
        cbcPrepaidAmount.appendChild(cbcPaidAmount)
        cbcPrepaidAmount.appendChild(cbcInstructionID)

        return cbcPrepaidAmount

    def AdditionalMonetaryTotal(self, currencyID, gravado, exonerado, inafecto, gratuito, total_descuento, 
                                indExportacion=False, percepcion=False, detraccion=False,indAnticipo=False,
                                indVentaItinerante=False,factura_guia=None,indVentaInterna=False):        
        extUBLExtensions = self.doc.createElement("ext:UBLExtensions")
        extUBLExtension = self.doc.createElement("ext:UBLExtension")
        extExtensionContent = self.doc.createElement("ext:ExtensionContent")
        sacAdditionalInformation = self.doc.createElement("sac:AdditionalInformation")

        ## ACTIVAR PARA EXPORTACION
        # idop = '02'
        #idop = ''

        #MODIFICADO ROZVI
        #if incoterm.id != False:
        #    idop = '02'

        if not indExportacion:
            # OPERACIONES GRAVADAS
            sacAdditionalMonetaryTotal_gravado = self.doc.createElement("sac:AdditionalMonetaryTotal")

            cbcID = self.doc.createElement("cbc:ID")
            text = self.doc.createTextNode("1001")
            cbcID.appendChild(text)

            cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
            cbcPayableAmount.setAttribute("currencyID", currencyID)
            text = self.doc.createTextNode(str(gravado))
            cbcPayableAmount.appendChild(text)

            sacAdditionalMonetaryTotal_gravado.appendChild(cbcID)
            sacAdditionalMonetaryTotal_gravado.appendChild(cbcPayableAmount)
            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_gravado)

            
            # OPERACIONES INAFECTAS
            sacAdditionalMonetaryTotal_inafecto = self.doc.createElement("sac:AdditionalMonetaryTotal")
            cbcID = self.doc.createElement("cbc:ID")
            text = self.doc.createTextNode("1002")
            cbcID.appendChild(text)

            cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
            cbcPayableAmount.setAttribute("currencyID", currencyID)
            text = self.doc.createTextNode(str(inafecto))
            cbcPayableAmount.appendChild(text)

            sacAdditionalMonetaryTotal_inafecto.appendChild(cbcID)
            sacAdditionalMonetaryTotal_inafecto.appendChild(cbcPayableAmount)
            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_inafecto)

            # OPERACIONES EXONERADAS
            sacAdditionalMonetaryTotal_exonerado = self.doc.createElement("sac:AdditionalMonetaryTotal")
            cbcID = self.doc.createElement("cbc:ID")
            text = self.doc.createTextNode("1003")
            cbcID.appendChild(text)

            cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
            cbcPayableAmount.setAttribute("currencyID", currencyID)
            text = self.doc.createTextNode(str(exonerado))
            cbcPayableAmount.appendChild(text)

            sacAdditionalMonetaryTotal_exonerado.appendChild(cbcID)
            sacAdditionalMonetaryTotal_exonerado.appendChild(cbcPayableAmount)
            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_exonerado)

            # OPERACIONES GRATUITAS
            sacAdditionalMonetaryTotal_gratuito = self.doc.createElement("sac:AdditionalMonetaryTotal")
            cbcID = self.doc.createElement("cbc:ID")
            text = self.doc.createTextNode("1004")
            cbcID.appendChild(text)

            cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
            cbcPayableAmount.setAttribute("currencyID", currencyID)
            text = self.doc.createTextNode(str(gratuito))
            cbcPayableAmount.appendChild(text)
            
            sacAdditionalMonetaryTotal_gratuito.appendChild(cbcID)
            sacAdditionalMonetaryTotal_gratuito.appendChild(cbcPayableAmount)
            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_gratuito)

            # DESCUENTOS
            sacAdditionalMonetaryTotal_descuento = None
            if total_descuento:
                sacAdditionalMonetaryTotal_descuento = self.doc.createElement("sac:AdditionalMonetaryTotal")
                cbcID = self.doc.createElement("cbc:ID")
                text = self.doc.createTextNode("2005")
                cbcID.appendChild(text)
                cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
                cbcPayableAmount.setAttribute("currencyID", currencyID)
                text = self.doc.createTextNode(str(total_descuento))
                cbcPayableAmount.appendChild(text)
                sacAdditionalMonetaryTotal_descuento.appendChild(cbcID)
                sacAdditionalMonetaryTotal_descuento.appendChild(cbcPayableAmount)

            #PERCEPCIONES
            if percepcion:
                sacAdditionalMonetaryTotal_percepcion = self.doc.createElement("sac:AdditionalMonetaryTotal")
                cbcID = self.doc.createElement("cbc:ID")
                text = self.doc.createTextNode("2001")
                cbcID.appendChild(text)

                sacReferenceAmount = self.doc.createElement("sac:ReferenceAmount")
                sacReferenceAmount.setAttribute("currencyID", currencyID)
                text = self.doc.createTextNode(str(percepcion['mntBaseImponible']))
                sacReferenceAmount.appendChild(text)

                cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
                cbcPayableAmount.setAttribute("currencyID", currencyID)
                text = self.doc.createTextNode(str(percepcion['mntPercepcion']))
                cbcPayableAmount.appendChild(text)

                sacTotalAmount = self.doc.createElement("sac:TotalAmount")
                sacTotalAmount.setAttribute("currencyID", currencyID)
                text = self.doc.createTextNode(str(percepcion['mntTotalMasPercepcion']))
                sacTotalAmount.appendChild(text)

                sacAdditionalMonetaryTotal_percepcion.appendChild(cbcID)
                sacAdditionalMonetaryTotal_percepcion.appendChild(sacReferenceAmount)
                sacAdditionalMonetaryTotal_percepcion.appendChild(cbcPayableAmount)
                sacAdditionalMonetaryTotal_percepcion.appendChild(sacTotalAmount)

                sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_percepcion)
            
            #DETRACCIONES
            if detraccion:
                sacAdditionalMonetaryTotal_detraccion = self.doc.createElement("sac:AdditionalMonetaryTotal")
                
                cbcID = self.doc.createElement("cbc:ID")
                text = self.doc.createTextNode("2003")
                cbcID.appendChild(text)

                cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
                cbcPayableAmount.setAttribute("currencyID", currencyID)
                text = self.doc.createTextNode(str(detraccion["mntDetraccion"]))
                cbcPayableAmount.appendChild(text)

                sacAdditionalMonetaryTotal_detraccion.appendChild(cbcID)
                sacAdditionalMonetaryTotal_detraccion.appendChild(cbcPayableAmount)

            """
            Aplicable solo en el caso que todas las operaciones (lineas o items) comprendidas en
            la factura electrOnica sean gratuitas.
            En el elemento cbc:ID se debe consignar el cOdigo 1002 (segun Catalogo No. 15).
            """
            if gratuito > 0 and gravado == 0 and exonerado == 0 and inafecto == 0 and total_descuento == 0:
                sacAdditionalProperty = self.doc.createElement("sac:AdditionalProperty")
                cbcID = self.doc.createElement("cbc:ID")
                text = self.doc.createTextNode("1002")
                cbcID.appendChild(text)
                cbcValue = self.doc.createElement("cbc:Value")
                # text=self.doc.createTextNode("TRANSFERENCIA GRATUITA DE UN BIEN Y/O SERVICIO PRESTADO GRATUITAMENTE")
                text = self.doc.createTextNode("TRANSFERENCIA GRATUITA")
                cbcValue.appendChild(text)
                sacAdditionalProperty.appendChild(cbcID)
                sacAdditionalProperty.appendChild(cbcValue)
                sacAdditionalInformation.appendChild(sacAdditionalProperty)

            if indVentaItinerante:
                sacAdditionalInformation.appendChild(self.AdditionalProperty("3000","Venta realizada por emisor itinerante"))
                
            if detraccion:
                sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_detraccion)
                sacAdditionalInformation.appendChild(self.AdditionalProperty("3000",detraccion.get("codigo_bb_ss","")))
                sacAdditionalInformation.appendChild(self.AdditionalProperty("3001",detraccion.get("numero_cta_bn","")))

            if sacAdditionalMonetaryTotal_descuento:
                sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_descuento)

            
           
            # VENTA INTERNA
            if indAnticipo:
                sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')
                cbcID = self.doc.createElement('cbc:ID')
                text = self.doc.createTextNode("04")
                cbcID.appendChild(text)
                sacSUNATTransaction.appendChild(cbcID)
                sacAdditionalInformation.appendChild(sacSUNATTransaction)
            elif indVentaItinerante:
                sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')
                cbcID = self.doc.createElement('cbc:ID')
                text = self.doc.createTextNode("05")
                cbcID.appendChild(text)
                sacSUNATTransaction.appendChild(cbcID)
                sacAdditionalInformation.appendChild(sacSUNATTransaction)

                #sacAdditionalInformation.appendChild(self.SUNATEmbededDespatchAdvice("Av. Larco 739","","Lima","150101","Lima","Miraflores","PE"))
            elif indVentaInterna:
                sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')
                cbcID = self.doc.createElement('cbc:ID')
                text = self.doc.createTextNode("01")
                cbcID.appendChild(text)
                sacSUNATTransaction.appendChild(cbcID)
                sacAdditionalInformation.appendChild(sacSUNATTransaction)
            
            if factura_guia:
                SUNATEmbededDespatchAdvice = self.SUNATEmbededDespatchAdvice(direccion_envio=factura_guia.get("direccionEnvio",{}),
                                                                            direccion_origen=factura_guia.get("direccionOrigen",{}),
                                                                            transporte_id=factura_guia.get("transporteId",""),
                                                                            numero_documento_transportista=factura_guia.get("numDocTransportista",""),
                                                                            tipo_documento_transportista=factura_guia.get("tipoDocTransportista",""),
                                                                            nombre_transportista=factura_guia.get("nombreTransportista",""),
                                                                            placa=factura_guia.get("placa",""),
                                                                            codigo_autorizacion_transporte=factura_guia.get("codigoAutorizacionTransporte",""),
                                                                            marca_transporte=factura_guia.get("marcaTransporte",""),
                                                                            modo_codigo_transporte=factura_guia.get("modoCodigoTransporte",""),
                                                                            peso=factura_guia.get("peso",""),
                                                                            unidad_medida=factura_guia.get("unidadMedida",""))
                sacAdditionalInformation.appendChild(SUNATEmbededDespatchAdvice)
        # sac:AdditionalProperty 1002 TRANSFERENCIA GRATUITA DE UN BIOEN O SERVICIO PRESTADO GRATUITAMENTE
        # OBLIGATORIO:



        # TIPO DE OPERACION
        if indExportacion:
            # OPERACIONES INAFECTAS
            sacAdditionalMonetaryTotal_inafecto = self.doc.createElement("sac:AdditionalMonetaryTotal")
            
            cbcID = self.doc.createElement("cbc:ID")
            text = self.doc.createTextNode("1002")
            cbcID.appendChild(text)

            cbcPayableAmount = self.doc.createElement("cbc:PayableAmount")
            cbcPayableAmount.setAttribute("currencyID", currencyID)
            text = self.doc.createTextNode(str(inafecto))
            cbcPayableAmount.appendChild(text)

            sacAdditionalMonetaryTotal_inafecto.appendChild(cbcID)
            sacAdditionalMonetaryTotal_inafecto.appendChild(cbcPayableAmount)
            sacAdditionalInformation.appendChild(sacAdditionalMonetaryTotal_inafecto)

            # EXPORTACIÓN
            sacSUNATTransaction = self.doc.createElement('sac:SUNATTransaction')

            cbcID = self.doc.createElement('cbc:ID')
            text = self.doc.createTextNode("02")
            cbcID.appendChild(text)

            sacSUNATTransaction.appendChild(cbcID)
            sacAdditionalInformation.appendChild(sacSUNATTransaction)

        

        extExtensionContent.appendChild(sacAdditionalInformation)
        extUBLExtension.appendChild(extExtensionContent)
        extUBLExtensions.appendChild(extUBLExtension)

        return extUBLExtensions

    #########################################################################

    def AdditionalProperty(self,ID,VALUE):
        sacAdditionalProperty = self.doc.createElement("sac:AdditionalProperty")
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ID)
        cbcID.appendChild(text)
        cbcValue = self.doc.createElement("cbc:Value")
        text = self.doc.createTextNode(VALUE)
        cbcValue.appendChild(text)

        sacAdditionalProperty.appendChild(cbcID)
        sacAdditionalProperty.appendChild(cbcValue)
        return sacAdditionalProperty

    def cacDeliveryTerms(self,direccion_completa,urbanizacion,provincia,ubigeo,departamento,distrito,codigo_pais):
        cacDeliveryTerms = self.doc.createElement("cac:DeliveryTerms")
        cacDeliveryLocation = self.doc.createElement("cac:DeliveryLocation")
        cacAddress = self.doc.createElement("cac:Address")
        
        cbcPostalZone = self.doc.createElement("cbc:PostalZone")
        text = self.doc.createTextNode(ubigeo)
        cbcPostalZone.appendChild(text)
        cacAddress.appendChild(cbcPostalZone)

        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion_completa)
        cbcStreetName.appendChild(text)
        cacAddress.appendChild(cbcStreetName)

        cbcCitySubdivisionName = self.doc.createElement("cbc:CitySubdivisionName")
        text = self.doc.createTextNode(urbanizacion)
        cbcCitySubdivisionName.appendChild(text)
        cacAddress.appendChild(cbcCitySubdivisionName)

        cbcCityName = self.doc.createElement("cbc:CityName")
        text = self.doc.createTextNode(provincia)
        cbcCityName.appendChild(text)
        cacAddress.appendChild(cbcCityName)

        cbcCountrySubentity = self.doc.createElement("cbc:CountrySubentity")
        text = self.doc.createTextNode(departamento)
        cbcCountrySubentity.appendChild(text)
        cacAddress.appendChild(cbcCountrySubentity)
        
        cbcDistrict = self.doc.createElement("cbc:District")
        text = self.doc.createTextNode(distrito)
        cbcDistrict.appendChild(text)
        cacAddress.appendChild(cbcDistrict)

        cacCountry = self.doc.createElement("cac:Country")
        cbcIdentificationCode = self.doc.createElement("cbc:IdentificationCode")
        text = self.doc.createTextNode(codigo_pais)
        cbcIdentificationCode.appendChild(text)
        cacCountry.appendChild(cbcIdentificationCode)
        cacAddress.appendChild(cacCountry)

        cacDeliveryLocation.appendChild(cacAddress)
        cacDeliveryTerms.appendChild(cacDeliveryLocation)

        return cacDeliveryTerms

            
    def SUNATEmbededDespatchAdvice(self,direccion_envio,direccion_origen,numero_documento_transportista,
                                    tipo_documento_transportista,nombre_transportista,transporte_id,placa,
                                    codigo_autorizacion_transporte,marca_transporte,modo_codigo_transporte,
                                    peso,unidad_medida):
        sacSUNATEmbededDespatchAdvice = self.doc.createElement("sac:SUNATEmbededDespatchAdvice")
        DeliveryAddress = self.DeliveryAddress(direccion_completa=direccion_envio.get("direccionCompleta",""),
                                                urbanizacion=direccion_envio.get("urbanizacion",""),
                                                provincia=direccion_envio.get("provincia",""),
                                                ubigeo=direccion_envio.get("ubigeo",""),
                                                departamento=direccion_envio.get("departamento",""),
                                                distrito=direccion_envio.get("distrito",""),
                                                codigo_pais=direccion_envio.get("codigoPais",""))
        OriginAddress = self.OriginAddress(direccion_completa=direccion_origen.get("direccionCompleta",""),
                                                urbanizacion=direccion_origen.get("urbanizacion",""),
                                                provincia=direccion_origen.get("provincia",""),
                                                ubigeo=direccion_origen.get("ubigeo",""),
                                                departamento=direccion_origen.get("departamento",""),
                                                distrito=direccion_origen.get("distrito",""),
                                                codigo_pais=direccion_origen.get("codigoPais",""))
        SUNATCarrierParty = self.SUNATCarrierParty(numero_documento_transportista,tipo_documento_transportista,nombre_transportista)
        DriverParty = self.DriverParty(transporte_id)
        SUNATRoadTransport = self.SUNATRoadTransport(placa,codigo_autorizacion_transporte,marca_transporte)
        TransportModeCode = self.TransportModeCode(modo_codigo_transporte)
        GrossWeightMeasure = self.GrossWeightMeasure(peso,unidad_medida)

        sacSUNATEmbededDespatchAdvice.appendChild(DeliveryAddress)
        sacSUNATEmbededDespatchAdvice.appendChild(OriginAddress)
        sacSUNATEmbededDespatchAdvice.appendChild(SUNATCarrierParty)
        sacSUNATEmbededDespatchAdvice.appendChild(DriverParty)
        sacSUNATEmbededDespatchAdvice.appendChild(SUNATRoadTransport)
        sacSUNATEmbededDespatchAdvice.appendChild(TransportModeCode)
        sacSUNATEmbededDespatchAdvice.appendChild(GrossWeightMeasure)
        
        return sacSUNATEmbededDespatchAdvice

    def DeliveryAddress(self,direccion_completa,urbanizacion,provincia,ubigeo,departamento,distrito,codigo_pais):
        cacDeliveryAddress = self.doc.createElement("cac:DeliveryAddress")
        
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo)
        cbcID.appendChild(text)
        cacDeliveryAddress.appendChild(cbcID)

        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion_completa)
        cbcStreetName.appendChild(text)
        cacDeliveryAddress.appendChild(cbcStreetName)

        cbcCitySubdivisionName = self.doc.createElement("cbc:CitySubdivisionName")
        text = self.doc.createTextNode(urbanizacion)
        cbcCitySubdivisionName.appendChild(text)
        cacDeliveryAddress.appendChild(cbcCitySubdivisionName)

        cbcCityName = self.doc.createElement("cbc:CityName")
        text = self.doc.createTextNode(provincia)
        cbcCityName.appendChild(text)
        cacDeliveryAddress.appendChild(cbcCityName)

        cbcCountrySubentity = self.doc.createElement("cbc:CountrySubentity")
        text = self.doc.createTextNode(departamento)
        cbcCountrySubentity.appendChild(text)
        cacDeliveryAddress.appendChild(cbcCountrySubentity)

        cbcDistrict = self.doc.createElement("cbc:District")
        text = self.doc.createTextNode(distrito)
        cbcDistrict.appendChild(text)
        cacDeliveryAddress.appendChild(cbcDistrict)

        cacCountry = self.doc.createElement("cac:Country")
        cbcIdentificationCode = self.doc.createElement("cbc:IdentificationCode")
        text = self.doc.createTextNode(codigo_pais)
        cbcIdentificationCode.appendChild(text)
        cacCountry.appendChild(cbcIdentificationCode)
        cacDeliveryAddress.appendChild(cacCountry)

        return cacDeliveryAddress
        
    def OriginAddress(self,direccion_completa,urbanizacion,provincia,ubigeo,departamento,distrito,codigo_pais):
        cacOriginAddress = self.doc.createElement("cac:OriginAddress")
        
        cbcID = self.doc.createElement("cbc:ID")
        text = self.doc.createTextNode(ubigeo)
        cbcID.appendChild(text)
        cacOriginAddress.appendChild(cbcID)

        cbcStreetName = self.doc.createElement("cbc:StreetName")
        text = self.doc.createTextNode(direccion_completa)
        cbcStreetName.appendChild(text)
        cacOriginAddress.appendChild(cbcStreetName)

        cbcCitySubdivisionName = self.doc.createElement("cbc:CitySubdivisionName")
        text = self.doc.createTextNode(urbanizacion)
        cbcCitySubdivisionName.appendChild(text)
        cacOriginAddress.appendChild(cbcCitySubdivisionName)

        cbcCityName = self.doc.createElement("cbc:CityName")
        text = self.doc.createTextNode(provincia)
        cbcCityName.appendChild(text)
        cacOriginAddress.appendChild(cbcCityName)

        cbcCountrySubentity = self.doc.createElement("cbc:CountrySubentity")
        text = self.doc.createTextNode(departamento)
        cbcCountrySubentity.appendChild(text)
        cacOriginAddress.appendChild(cbcCountrySubentity)

        cbcDistrict = self.doc.createElement("cbc:District")
        text = self.doc.createTextNode(distrito)
        cbcDistrict.appendChild(text)
        cacOriginAddress.appendChild(cbcDistrict)

        cacCountry = self.doc.createElement("cac:Country")
        cbcIdentificationCode = self.doc.createElement("cbc:IdentificationCode")
        text = self.doc.createTextNode(codigo_pais)
        cbcIdentificationCode.appendChild(text)
        cacCountry.appendChild(cbcIdentificationCode)
        cacOriginAddress.appendChild(cacCountry)

        return cacOriginAddress
    
    def SUNATCarrierParty(self,numero_documento_trasportista,tipo_documento_trasportista,nombre_transportista):
        SUNATCarrierParty = self.doc.createElement("sac:SUNATCarrierParty")
        
        cbcCustomerAssignedAccountID = self.doc.createElement("cbc:CustomerAssignedAccountID") 
        text = self.doc.createTextNode(numero_documento_trasportista)
        cbcCustomerAssignedAccountID.appendChild(text)
        SUNATCarrierParty.appendChild(cbcCustomerAssignedAccountID)

        cbcAdditionalAccountID = self.doc.createElement("cbc:AdditionalAccountID") 
        text = self.doc.createTextNode(tipo_documento_trasportista)
        cbcAdditionalAccountID.appendChild(text)
        SUNATCarrierParty.appendChild(cbcAdditionalAccountID)

        cacParty = self.doc.createElement("cac:Party")
        cacPartyIdentification = self.doc.createElement("cac:PartyLegalEntity")
        cbcRegistrationName = self.doc.createElement("cbc:RegistrationName") 
        text = self.doc.createTextNode(nombre_transportista)
        cbcRegistrationName.appendChild(text)
        cacPartyIdentification.appendChild(cbcRegistrationName)
        cacParty.appendChild(cacPartyIdentification)
        SUNATCarrierParty.appendChild(cacParty)

        return SUNATCarrierParty

    def DriverParty(self,transporte_id):
        sacDriverParty = self.doc.createElement("sac:DriverParty")
        cacParty = self.doc.createElement("cac:Party")
        cacPartyIdentification = self.doc.createElement("cac:PartyIdentification")

        cbcID = self.doc.createElement("cbc:ID") 
        text = self.doc.createTextNode(transporte_id)
        cbcID.appendChild(text)
        
        cacPartyIdentification.appendChild(cbcID)
        cacParty.appendChild(cacPartyIdentification)
        sacDriverParty.appendChild(cacParty)

        return sacDriverParty

    def SUNATRoadTransport(self,placa,codigo_autorizacion_transporte,marca_transporte):
        SUNATRoadTransport = self.doc.createElement("sac:SUNATRoadTransport")

        cbcLicensePlateID = self.doc.createElement("cbc:LicensePlateID") 
        text = self.doc.createTextNode(placa)
        cbcLicensePlateID.appendChild(text)
        SUNATRoadTransport.appendChild(cbcLicensePlateID)

        cbcTransportAuthorizacionCode = self.doc.createElement("cbc:TransportAuthorizationCode") 
        text = self.doc.createTextNode(codigo_autorizacion_transporte)
        cbcTransportAuthorizacionCode.appendChild(text)
        SUNATRoadTransport.appendChild(cbcTransportAuthorizacionCode)

        cbcBrandName = self.doc.createElement("cbc:BrandName") 
        text = self.doc.createTextNode(marca_transporte)
        cbcBrandName.appendChild(text)
        SUNATRoadTransport.appendChild(cbcBrandName)

        return SUNATRoadTransport
    
    def TransportModeCode(self,modo_codigo_transporte):
        cbcTransportModeCode = self.doc.createElement("cbc:TransportModeCode") 
        text = self.doc.createTextNode(modo_codigo_transporte)
        cbcTransportModeCode.appendChild(text)
        return cbcTransportModeCode

    def GrossWeightMeasure(self,peso,unidad_medida):
        cbcGrossWeightMeasure= self.doc.createElement("cbc:GrossWeightMeasure") 
        cbcGrossWeightMeasure.setAttribute("unitCode",unidad_medida)
        text = self.doc.createTextNode(peso)
        cbcGrossWeightMeasure.appendChild(text)

        return cbcGrossWeightMeasure

    def TaxTotal(self, currencyID, TaxAmount, tributo_id, tributo_nombre, tributo_codigo):
        cacTaxTotal = self.doc.createElement("cac:TaxTotal")

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxTotal.appendChild(cbcTaxAmount)

        cacTaxSubtotal = self.doc.createElement("cac:TaxSubtotal")

        cbcTaxAmount = self.doc.createElement("cbc:TaxAmount")
        cbcTaxAmount.setAttribute("currencyID", currencyID)
        text = self.doc.createTextNode(str(TaxAmount))
        cbcTaxAmount.appendChild(text)
        cacTaxSubtotal.appendChild(cbcTaxAmount)

        cacTaxCategory = self.doc.createElement("cac:TaxCategory")
        cacTaxScheme = self.doc.createElement("cac:TaxScheme")
        cbcID = self.doc.createElement("cbc:ID")
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
        cacTaxTotal.appendChild(cacTaxSubtotal)

        return cacTaxTotal

    #########################################################################
    #########################################################################
    #########################################################################
    #########################################################################

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

    
    def getStatusCdr(self, username, 
                        password,
                        ruc_comprobante,
                        tipo_comprobante,
                        serie_comprobante,
                        numero_comprobante):
        Envelope = self.doc.createElement("SOAP-ENV:Envelope")
        Envelope.setAttribute("xmlns:SOAP-ENV", "http://schemas.xmlsoap.org/soap/envelope/")
        Envelope.setAttribute("xmlns:SOAP-ENC", "http://schemas.xmlsoap.org/soap/encoding/")
        Envelope.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        Envelope.setAttribute("xmlns:xsd","http://www.w3.org/2001/XMLSchema")
        Envelope.setAttribute("xmlns:wsse","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")

        Header = self.doc.createElement("SOAP-ENV:Header")
        Header.setAttribute("xmlns:soapenv","http://schemas.xmlsoap.org/soap/envelope")
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

        Body = self.doc.createElement("SOAP-ENV:Body")
        getStatus = self.doc.createElement("m:getStatusCdr")
        getStatus.setAttribute("xmlns:m","http://service.sunat.gob.pe")
        
        rucComprobante = self.doc.createElement("rucComprobante")
        text = self.doc.createTextNode(ruc_comprobante)
        rucComprobante.appendChild(text)

        tipoComprobante = self.doc.createElement("tipoComprobante")
        text = self.doc.createTextNode(tipo_comprobante)
        tipoComprobante.appendChild(text)


        serieComprobante = self.doc.createElement("serieComprobante")
        text = self.doc.createTextNode(serie_comprobante)
        serieComprobante.appendChild(text)

        numeroComprobante = self.doc.createElement("numeroComprobante")
        text = self.doc.createTextNode(numero_comprobante)
        numeroComprobante.appendChild(text)

        getStatus.appendChild(rucComprobante)
        getStatus.appendChild(tipoComprobante)
        getStatus.appendChild(serieComprobante)
        getStatus.appendChild(numeroComprobante)

        Body.appendChild(getStatus)
        Envelope.appendChild(Body)

        return Envelope
