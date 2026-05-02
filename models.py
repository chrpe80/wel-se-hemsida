class User:
    def __init__(self):
        self._id = None
        self._is_authenticated = True
        self._is_active = True
        self._is_anonymous = False
        self._is_admin = None
        self._username = None
        self._password = None
        self._fname = None
        self._lname = None
        self._email = None
        self._phone = None

    # getters
    def get_id(self) -> str:
        return str(self._id)

    @property
    def is_authenticated(self) -> bool:
        return self._is_authenticated

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_anonymous(self) -> bool:
        return self._is_anonymous

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def fname(self):
        return self._fname

    @property
    def lname(self):
        return self._lname

    @property
    def email(self):
        return self._email

    @property
    def phone(self):
        return self._phone

    # setters
    def set_id(self, value):
        self._id = value

    @is_authenticated.setter
    def is_authenticated(self, value):
        self._is_authenticated = value

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @is_anonymous.setter
    def is_anonymous(self, value):
        self._is_anonymous = value

    @is_admin.setter
    def is_admin(self, value):
        self._is_admin = value

    @username.setter
    def username(self, value):
        self._username = value

    @password.setter
    def password(self, value):
        self._password = value

    @fname.setter
    def fname(self, value):
        self._fname = value

    @lname.setter
    def lname(self, value):
        self._lname = value

    @email.setter
    def email(self, value):
        self._email = value

    @phone.setter
    def phone(self, value):
        self._phone = value
