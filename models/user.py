class Staff:
    def __init__(self, staff_id, first_name, last_name, role, password):
        self.staff_id = staff_id
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.password = password

    @classmethod
    def from_row(cls, row):
        return cls(*row)

    def __repr__(self):
        return f"Staff(staff_id={self.staff_id}, first_name='{self.first_name}', last_name='{self.last_name}', role='{self.role}', password='{self.password}')"
