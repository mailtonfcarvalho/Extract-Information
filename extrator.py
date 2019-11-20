import re
import pandas
import xlrd
from anuncio import Anuncio


class Extrator(object):
    regex = [r'\$ (\d{1,3}\.\d{3}\,\d{2})', r'(\d{1,3}\.\d{3}) ?\km.*']
    cel = [r'\(\d{2,5}\) \d{4,5}\-\d{4}']
    port = [r' (\d{1}\w{1,6})']
    atr_ar = ['ar', 'ar cond', 'ac', 'ar condicionado', 'a/c']
    atr_dir_hid = ['hidraulica', 'dh', 'dir.e']
    atr_dir_mec = ['mecanica', 'mecam', 'dm', 'dir.m', 'mec']
    atr_num = ['preco', 'quilometragem', 'telefone']
    atr_cel = ['tel']
    atr_port = ['portas']

    def __init__(self):
        pass

    @staticmethod
    def getModelo(cabecalho):
        motor = re.findall(r'\d\.\d', cabecalho)
        ano = re.findall(r'\d{2,4}', cabecalho)
        if not (not motor):
            cabecalho = cabecalho.replace(motor[0], '')
        if not (not ano):
            cabecalho = cabecalho.replace(ano[0], '')
        return cabecalho.lower()

    @staticmethod
    def getAno(chars):
        atr_ano = None
        for index in chars.split():
            if index.isdigit():
                var = int(re.findall(r'\d{2,4}', index)[0])
                if len(index) == 2 and var <= 17:
                    atr_ano = var + 2000
                elif len(index) > 2:
                    atr_ano = var
                else:
                    atr_ano = var + 1900
                break
            else:
                atr_ano = 'N/I'
        return atr_ano

    @staticmethod
    def getMotor(motor):
        potencia = ''
        atr_motor = re.findall(r'\d\.\d', motor)
        for i in atr_motor:
            potencia = i
        return potencia

    @staticmethod
    def getDict(dict):
        dict_csv = pandas.read_csv(dict, delimiter=';')
        atr = dict_csv['atributo']
        val = dict_csv['valores']
        atr_dict = {}
        for i in range(0, len(dict_csv)):
            atr_dict[atr[i]] = val[i]
        return atr_dict

    @staticmethod
    def lerCorpus():
        anuncio = xlrd.open_workbook("corpus.xlsx")
        pagina = anuncio.sheet_by_index(0)
        return pagina

    def getAnuncios(self):
        lin_index = [(4, 5)]
        anuncio_array = []
        pagina = self.lerCorpus()
        for i, j in lin_index:
            for k in range(1, 11):
                obj = Anuncio(pagina.cell_value(rowx=int(i), colx=k),
                              pagina.cell_value(rowx=int(j), colx=k))
                anuncio_array.append(obj)
        return anuncio_array

    @staticmethod
    def compararWord(word, phrase):
        return re.search(r'\b{var}\b'.format(var=word), phrase)

    def extrairInfo(self, cabecalho, corpo):
        template_list = []
        corpo = corpo.lower()
        template_list.append(('modelo', self.getModelo(cabecalho)))
        template_list.append(('ano', self.getAno(cabecalho)))
        template_list.append(('motor', self.getMotor(cabecalho)))

        dict_ei = self.getDict('dict_ei.csv')
        for key in dict_ei.keys():
            dict_split = str(dict_ei[key]).split(',')
            for i in range(0, len(dict_split)):
                if self.compararWord(dict_split[i], corpo) is not None:
                    if self.compararWord(dict_split[i], ','.join(self.atr_ar)) is not None:
                        template_list.append((key, 'sim'))
                    elif dict_split[i] in self.atr_dir_hid:
                        template_list.append((key, 'hidraulica'))
                    elif dict_split[i] in self.atr_dir_mec:
                        template_list.append((key, 'mecanica'))
                    else:
                        template_list.append((key, dict_split[i]))
                elif i + 1 == len(dict_split):
                    atrs = [a for a, _ in template_list]
                    if key not in atrs:
                        info = self.getDict('dict_default.csv').get(key)
                        template_list.append((key, info))
                continue

        for i in range(0, len(self.cel)):
            atr = re.findall(self.cel[i], corpo)
            if not atr:
                valor = 'N/I'
            else:
                valor = atr[0]
            template_list.append((self.atr_cel[i], valor))

        for i in range(0, len(self.regex)):
            atr = re.findall(self.regex[i], corpo)
            if not atr:
                valor = 'N/I'
            else:
                valor = atr[0]
            template_list.append((self.atr_num[i], valor))

        for i in range(0, len(self.port)):
            atr = re.findall(self.port[i], corpo)
            if not atr:
                valor = 'N/I'
            else:
                valor = atr[0]
            template_list.append((self.atr_port[i], valor))

        return template_list
