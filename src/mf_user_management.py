from src.manager.user_management import User_Manager


manager = User_Manager()


def standard_login( email, password):
    print("MF_standard login")
    return manager.login(email=email, password=password)

def add_user(username, password,  email, first_name, last_name, phone_number):
    return manager.add_user(username, password,  email, first_name, last_name, phone_number)
    

def list_user():
    return manager.list_user()

def edit_user(email, password, role, first_name, last_name):
    return manager.edit_user(email=email, password=password, new_role=role, new_first_name=first_name, new_last_name=last_name)

def delete_user(email):
    return manager.delete_user(email=email)