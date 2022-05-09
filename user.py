class User:
    def is_active(self):
        return True

    def get_id(self):
        return 'admin'

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False