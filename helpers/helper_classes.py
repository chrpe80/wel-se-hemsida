class Responses:
    @staticmethod
    def field(field):
        return f"{field} saknas."

    @staticmethod
    def fields():
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
        return "Operationen lyckades inte."

    @staticmethod
    def exists(value):
        return f"{value} finns redan."

    @staticmethod
    def option():
        return "Välj ett alternativ."

    @staticmethod
    def filetype(filetype):
        return f"Filtyp måste vara {filetype}"
