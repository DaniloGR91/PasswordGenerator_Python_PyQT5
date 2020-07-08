from design import *
from config import *
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QDialogButtonBox
from PyQt5.QtCore import QSettings
import sys
import json
import random


class PassGenerador(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.conectar_database()

        # Settings
        self.settings = QSettings('COMPANY', 'PASS GENERATOR')
        self.settings.setValue('letters', True)
        self.settings.setValue('numbers', True)
        self.settings.setValue('special', False)
        self.settings.setValue('char_numb', 15)

        # Mensagem inicial LabelOutput
        self.labelOutput.setText(f'Bem-Vindo')

        # Tarefas/Status
        self.mostrando_senha = False
        self.cadastrando_senha = False
        self.alterando_senha = False
        self.excluindo_senha = False

        # Botões
        self.btnMostrarSenha.clicked.connect(self.mostrar_senha)
        self.btnMostrarApps.clicked.connect(self.mostrar_apps)
        self.btnCadastrarSenha.clicked.connect(self.cadastrar_senha)
        self.btnTool.clicked.connect(self.btn_settings)
        self.btnAlterarSenha.clicked.connect(self.alterar_senha)
        self.btnExcluirSenha.clicked.connect(self.excluir_senha)

        # InputUser
        self.inputUser.setReadOnly(True)
        self.inputUser.returnPressed.connect(self.keypress_input)

    def conectar_database(self):
        try:
            with open('senhas.json', 'r') as arq:
                arquivo = arq.read()
                db = json.loads(arquivo)
            self.statusbar.showMessage('Banco de dados aberto com sucesso.')
            self.database = db
        except FileNotFoundError:
            arq = open('senhas.json', 'w')
            arq.close()
            db = {}
            self.statusbar.showMessage('Banco de dados criado com sucesso.')
            self.database = db
        except json.decoder.JSONDecodeError:
            db = {}
            self.statusbar.showMessage(
                'Banco de dados com erro. Novo banco de dados criado.')
            self.database = db

    # Função chamada quando o usuário inputa algo no teclado
    def keypress_input(self):
        if self.mostrando_senha:
            self.inputkeypress_mostrar_senha()
        if self.cadastrando_senha:
            self.inputkeypress_cadastrar_senha()
        if self.alterando_senha:
            self.inputkeypress_alterar_senha()
        if self.excluindo_senha:
            self.inputkeypress_excluir_senha()

    # Função chamada quando usuário clica em Mostrar uma senha
    def mostrar_senha(self):
        self.labelInstrunction.setText(
            'Digite o App/Site que você deseja ver:')
        self.inputUser.setReadOnly(False)
        self.mostrando_senha = True

    def inputkeypress_mostrar_senha(self):
        text_inputed = self.inputUser.text()
        text_inputed = text_inputed.strip().capitalize()
        try:
            solicited_password = self.database[text_inputed]
            self.labelOutput.setText(f'{text_inputed}: {solicited_password}')
        except KeyError:
            try:
                solicited_password = self.database[text_inputed.lower()]
                self.labelOutput.setText(
                    f'{text_inputed}: {solicited_password}')
            except KeyError:
                self.labelOutput.setText(
                    f'{text_inputed} não foi encontrado. Você digitou corretamente?')
        self.mostrando_senha = False
        self.inativar_input()

    # Função chamada quando usuário clica em mostrar apps
    def mostrar_apps(self):
        string_apps = 'Os sites e apps com senhas salvas no seu banco são:\n'
        for k in self.database.keys():
            string_apps += f'- {k}\n'
        self.labelOutput.setText(string_apps)

    # Função chamada quando usuário clica em cadastrar senha
    def cadastrar_senha(self):
        self.labelInstrunction.setText(
            'Digite o App/Site desejado:')
        self.inputUser.setReadOnly(False)
        self.cadastrando_senha = True

    def inputkeypress_cadastrar_senha(self):
        text_inputed = self.inputUser.text()
        text_inputed = text_inputed.strip().capitalize()
        if self.validar_app(text_inputed):
            password = self.gerar_senha()
            self.salvar_senha(text_inputed, password)
        self.inativar_input()
        self.cadastrando_senha = False

    def gerar_senha(self):
        letters = True if self.settings.value('letters') == 'true' else False
        numbers = True if self.settings.value('numbers') == 'true' else False
        special_characters = True if self.settings.value(
            'special') == 'true' else False
        char_numb = self.settings.value('char_numb')

        if letters and numbers and special_characters:
            strings = 'abcdefghijklmnopqrstuvxwyzABCDEFGHIJKLMNOPQRSTUVWYXZ!@#$%&*()=+_-<>/0123456789'
        elif letters and numbers and not special_characters:
            strings = 'abcdefghijklmnopqrstuvxwyzABCDEFGHIJKLMNOPQRSTUVWYXZ0123456789'
        elif letters and special_characters and not numbers:
            strings = 'abcdefghijklmnopqrstuvxwyzABCDEFGHIJKLMNOPQRSTUVWYXZ!@#$%&*()=+_-<>/'
        elif numbers and special_characters and not letters:
            strings = '!@#$%&*()=+_-<>/0123456789'
        elif letters and not numbers and not special_characters:
            strings = 'abcdefghijklmnopqrstuvxwyzABCDEFGHIJKLMNOPQRSTUVWYXZ'
        elif numbers and not letters and not special_characters:
            strings = '0123456789'
        elif special_characters and not letters and not numbers:
            strings = '!@#$%&*()=+_-<>/'

        password = ''.join(random.choices(strings, k=char_numb))
        return password

    def validar_app(self, app):
        if app == '':
            self.labelOutput.setText('Digite um app válido.')
            return False
        elif app in self.database.keys():
            self.labelOutput.setText('Você digitou um app já cadastrado')
            return False
        else:
            return True

    def salvar_senha(self, app=None, password=None):
        if app == None and password == None:
            with open('senhas.json', 'w') as arq:
                arq.write(json.dumps(self.database))
        else:
            self.database[app] = password
            with open('senhas.json', 'w') as arq:
                arq.write(json.dumps(self.database))
            self.labelOutput.setText(
                f'Senha cadastrada com sucesso: \n{app}: {password}')

    # Função chamada quando usuário aperta no botão de configuraçoes
    def btn_settings(self):
        config = Configuration()
        config.exec_()

    # Função chamada quando usuário aperta no botão alterar senha
    def alterar_senha(self):
        self.labelInstrunction.setText(
            'Digite o App/Site desejado:')
        self.inputUser.setReadOnly(False)
        self.alterando_senha = True

    def inputkeypress_alterar_senha(self):
        text_inputed = self.inputUser.text()
        text_inputed = text_inputed.strip().capitalize()
        if self.validar_app_existente(text_inputed):
            password = self.gerar_senha()
            self.salvar_senha(text_inputed, password)
            self.labelOutput.setText(
                f'Nova senha cadastrada com sucesso.\n{text_inputed}: {password}')
        self.inativar_input()
        self.alterando_senha = False

    def validar_app_existente(self, app):
        if app in self.database.keys():
            return True
        else:
            self.labelOutput.setText('App não encontrado.')
            return False

    # Função chamada quando usuário aperta no botão excluir senha
    def excluir_senha(self):
        self.labelInstrunction.setText(
            'Digite o App/Site desejado:')
        self.inputUser.setReadOnly(False)
        self.excluindo_senha = True

    def inputkeypress_excluir_senha(self):
        text_inputed = self.inputUser.text()
        text_inputed = text_inputed.strip().capitalize()
        if self.validar_app_existente(text_inputed):
            self.database.pop(text_inputed)
            self.salvar_senha()
            self.labelOutput.setText(
                f'Senha de {text_inputed} excluida com sucesso.')
        self.inativar_input()
        self.excluindo_senha = False

    def inativar_input(self):
        self.labelInstrunction.setText('')
        self.inputUser.setText('')
        self.inputUser.setReadOnly(True)


class Configuration(Ui_Dialog, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)

        self.buttonBox.button(
            QDialogButtonBox.Ok).clicked.connect(self.btn_ok)
        self.buttonBox.button(
            QDialogButtonBox.Cancel).clicked.connect(self.close)

        if pass_generator.settings.value('letters') == 'true':
            self.ckbLetter.setChecked(True)
        else:
            self.ckbLetter.setChecked(False)

        if pass_generator.settings.value('numbers') == 'true':
            self.ckbNumber.setChecked(True)
        else:
            self.ckbNumber.setChecked(False)

        if pass_generator.settings.value('special') == 'true':
            self.ckbSpecialChar.setChecked(True)
        else:
            self.ckbSpecialChar.setChecked(False)

        self.spbCharNumber.setValue(pass_generator.settings.value('char_numb'))

    def btn_ok(self):
        if self.ckbLetter.checkState() == 2:
            pass_generator.settings.setValue('letters', True)
        else:
            pass_generator.settings.setValue('letters', False)

        if self.ckbNumber.checkState() == 2:
            pass_generator.settings.setValue('numbers', True)
        else:
            pass_generator.settings.setValue('numbers', False)

        if self.ckbSpecialChar.checkState() == 2:
            pass_generator.settings.setValue('special', True)
        else:
            pass_generator.settings.setValue('special', False)

        pass_generator.settings.setValue(
            'char_numb', self.spbCharNumber.value())

        self.accept()


if __name__ == "__main__":
    qt = QApplication(sys.argv)
    pass_generator = PassGenerador()
    pass_generator.show()
    qt.exec_()
