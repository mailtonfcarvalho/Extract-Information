# -*- coding: utf-8 -*-

from extrator import Extrator
import unicodedata

extrator = Extrator()
anuncios = extrator.getAnuncios()


def ignore_ascii(chars):
    return unicodedata.normalize('NFKD', chars).encode('ASCII', 'ignore')


for anuncio in anuncios:
    cabecalho = ignore_ascii(anuncio.cabecalho)
    corpo = ignore_ascii(anuncio.corpo)
    for atr, val in extrator.extrairInfo(cabecalho, corpo):
        print str(atr) + ': ' + str(val)
    print ''
