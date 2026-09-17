db_usuarios = {}

def reg_user():
    doc = input("Ingresa el documento: ")
    nom = input("Nombre completo: ")
    mail = input("Email: ")
    # evito usar la ñ por si las moscas
    passw = input("Contraseña: ")
    
    # Guardamos en el diccionario
    db_usuarios[doc] = {
        "nombre": nom,
        "correo": mail,
        "pass": passw
    }
    print("-> Guardado con éxito!")

def buscar_user():
    cedula = input("Cedula/Doc a buscar: ")
    if cedula in db_usuarios:
        u = db_usuarios[cedula] # una variable corta para no escribir tanto
        print(f"Info encontrada:\n- Nom: {u['nombre']}\n- Mail: {u['correo']}\n- Pass: {u['pass']}")
    else:
        print("Ese usuario no existe en la base de datos.")

def edit_user():
    id_user = input("Documento del usuario a cambiar: ")
    if id_user not in db_usuarios:
        print("No se encontro el usuario.")
        return # salimos rapido de la funcion
        
    print("¿Qué vas a cambiar?\n1. Nombre\n2. Correo\n3. Clave")
    op = input("> ")
    
    if op == "1":
        db_usuarios[id_user]["nombre"] = input("Nuevo nombre: ")
    elif op == "2":
        db_usuarios[id_user]["correo"] = input("Nuevo correo: ")
    elif op == "3":
        db_usuarios[id_user]["pass"] = input("Nueva contraseña: ")
    else:
        print("Opción inválida")
        return
    print("Datos actualizados.")

# --- Flujo principal ---
while True:
    print("\n*** SISTEMA DE USUARIOS ***")
    print("1. Registrar nuevo\n2. Buscar\n3. Modificar datos\n4. Salir")
    
    try:
        select = input("Elige una opción: ")
        if select == "1":
            reg_user()
        elif select == "2":
            buscar_user()
        elif select == "3":
            edit_user()
        elif select == "4":
            print("Bye!")
            break
        else:
            print("Pone un numero del 1 al 4...")
    except Exception as e:
        print("Error inesperado:", e)
