from src.manager.user_management import User_Manager


manager = User_Manager()


def standard_login( email, password):
    return manager.login(email=email, password=password)

def add_user(email, password, first_name, last_name, phone_number, role, status):
    return manager.add_user(email, password, first_name, last_name, phone_number, role, status)
    

def list_user():
    return manager.list_user()

def edit_user(first_name, last_name, email, phone_number, role, status):
    return manager.edit_user(first_name, last_name, email, phone_number, role, status)

def delete_user(user_id):
    return manager.delete_user(user_id=user_id)