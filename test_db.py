from db_mysql import create_user, authenticate_user, get_credits

print("Creando usuario de prueba...")
ok = create_user("leo", "1234")

print("Creado:", ok)
print("Auth correcto:", authenticate_user("leo", "1234"))
print("Auth incorrecto:", authenticate_user("leo", "fail"))
print("Créditos:", get_credits("leo"))
