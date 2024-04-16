from datetime import datetime

class Dato:
    def __init__(self, id, fec_alta, user_name, codigo_zip, credit_card_num, credit_card_ccv, cuenta_numero, direccion, geo_latitud, geo_longitud, color_favorito, foto_dni, ip, auto, auto_modelo, auto_tipo, auto_color, cantidad_compras_realizadas, avatar, fec_birthday):
        self.id = id
        self.fec_alta = fec_alta
        self.user_name = user_name
        self.codigo_zip = codigo_zip
        self.credit_card_num = credit_card_num
        self.credit_card_ccv = credit_card_ccv
        self.cuenta_numero = cuenta_numero
        self.direccion = direccion
        self.geo_latitud = geo_latitud
        self.geo_longitud = geo_longitud
        self.color_favorito = color_favorito
        self.foto_dni = foto_dni
        self.ip = ip
        self.auto = auto
        self.auto_modelo = auto_modelo
        self.auto_tipo = auto_tipo
        self.auto_color = auto_color
        self.cantidad_compras_realizadas = cantidad_compras_realizadas
        self.avatar = avatar
        self.fec_birthday = fec_birthday

