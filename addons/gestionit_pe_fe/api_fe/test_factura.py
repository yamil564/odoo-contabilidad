from  addons.gestionit_pe_fe.api_fe import factura

inv = open("test_factura.json","r")
factura.build_factura(inv.read())