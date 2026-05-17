class Responses:
    @staticmethod
    def field_missing(field):
        return f"'{field}' måste fyllas i."

    @staticmethod
    def fields_missing(field1, field2):
        return f"Både '{field1}' och '{field2}' måste fyllas i."

    @staticmethod
    def all_fields_are_required():
        return "Alla fält måste fyllas i."

    @staticmethod
    def logged_in():
        return "Du har loggats in."

    @staticmethod
    def logged_out():
        return "Du har loggats ut."

    @staticmethod
    def operation_successful():
        return "Operationen lyckades."

    @staticmethod
    def operation_failed():
        return "Operationen misslyckades."

    @staticmethod
    def duplicate_key(key, value):
        return f"{key} {value} finns redan."

    @staticmethod
    def choose_option():
        return "Välj ett alternativ."

    @staticmethod
    def filetype(filetype):
        return f"Filtypen måste vara {filetype}."
