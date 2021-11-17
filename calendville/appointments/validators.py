import re

from django import forms


class LengthPasswordValidator:
    def __init__(self, min_length=8, max_length=11):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if self.min_length > len(password) or len(password) > self.max_length:
            raise forms.ValidationError(
                f"La contraseña debe tener entre {self.min_length}"
                f" y {self.max_length} caracteres.")

    def get_help_text(self):
        return (f"La contraseña debe tener entre {self.min_length}"
                f" y {self.max_length} caracteres.")


class ContainsUpperCaseLetterPasswordValidator:

    def validate(self, password, user=None):
        SYMBOL_PATTERN = '(.*[A-Z].*)'
        regex = re.compile(SYMBOL_PATTERN)
        if not regex.search(password):
            raise forms.ValidationError(
                "La contraseña debe tener al menos una mayúscula."
            )

    def get_help_text(self):
        return "La contraseña debe tener al menos una mayúscula."


class ContainsNumberPasswordValidator:

    def validate(self, password, user=None):
        NUMBER_PATTERN = "(?=.*\\d)"
        regex = re.compile(NUMBER_PATTERN)
        if not regex.search(password):
            raise forms.ValidationError(
                "La contraseña debe tener al menos un número."
            )

    def get_help_text(self):
        return "La contraseña debe tener al menos un número."


class ContainsSymbolPasswordValidator:

    def validate(self, password, user=None):
        SYMBOL_PATTERN = '[@_!#$%^&*()<>?/}{~:]'
        regex = re.compile(SYMBOL_PATTERN)
        if not regex.search(password):
            raise forms.ValidationError(
                "La contraseña debe tener al menos un símbolo "
                "(!,@,#,$,%,&,*,<,>,(),~,:,?,/,|,{,})."
            )

    def get_help_text(self):
        return ("La contraseña debe tener al menos un símbolo "
                "(!,@,#,$,%,&,*,<,>,(),~,:,?,/,|,{,})."
                )
