import re
import mysql.connector
from conexion import connect
from report import generate_pdf_report, generate_statistical_report, export_users_csv


def is_valid_email(email):
    """Valida el formato de una dirección de correo electrónico."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email.strip()) is not None


def get_user_by_id(user_id):
    """Consulta y retorna un único usuario por su ID (o None si no existe)."""
    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, age FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"[ERROR BD al consultar usuario]: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_user(name, email, age):
    """
    Inserta un nuevo usuario en la base de datos con validaciones estrictas.
    Retorna el ID del usuario creado en caso de éxito, o None/False ante fallos.
    """
    # Validaciones de entrada
    if not name or not str(name).strip():
        print("[VALIDACIÓN] El nombre no puede estar vacío.")
        return False

    if not is_valid_email(email):
        print(f"[VALIDACIÓN] El correo electrónico '{email}' no tiene un formato válido.")
        return False

    try:
        age_int = int(age)
        if age_int < 0 or age_int > 130:
            print("[VALIDACIÓN] La edad debe ser un número positivo coherente (0 - 130).")
            return False
    except (ValueError, TypeError):
        print("[VALIDACIÓN] La edad debe ser un número entero válido.")
        return False

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        query = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (name.strip(), email.strip(), age_int))
        connection.commit()
        new_id = cursor.lastrowid
        print(f"[ÉXITO] Usuario '{name}' creado con éxito (ID asignado: {new_id}).")
        return new_id
    except mysql.connector.IntegrityError as err:
        if err.errno == 1062:  # Entrada duplicada
            print(f"[ERROR DUPLICADO] El correo electrónico '{email}' ya se encuentra registrado.")
        else:
            print(f"[ERROR INTEGRIDAD]: {err}")
        return False
    except mysql.connector.Error as err:
        print(f"[ERROR BD al crear usuario]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def read_users():
    """
    Consulta todos los usuarios registrados en la base de datos.
    Imprime una tabla formateada en consola y retorna la lista de tuplas.
    """
    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, age FROM users ORDER BY id ASC")
        users = cursor.fetchall()

        print("\n" + "=" * 65)
        print(f"{'ID':<6} | {'Nombre':<22} | {'Email':<24} | {'Edad':<6}")
        print("-" * 65)
        if not users:
            print("  No hay usuarios registrados en el sistema.")
        else:
            for u in users:
                print(f"{u[0]:<6} | {u[1]:<22} | {u[2]:<24} | {u[3]:<6}")
        print("=" * 65 + "\n")
        return users
    except mysql.connector.Error as err:
        print(f"[ERROR BD al leer usuarios]: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_user(user_id, name, email, age):
    """
    Actualiza la información de un usuario existente.
    Valida la existencia del ID y retorna True si se actualizó, False en caso contrario.
    """
    try:
        uid = int(user_id)
        age_int = int(age)
    except (ValueError, TypeError):
        print("[VALIDACIÓN] El ID y la edad deben ser valores numéricos enteros.")
        return False

    if not name or not str(name).strip():
        print("[VALIDACIÓN] El nombre no puede estar vacío.")
        return False

    if not is_valid_email(email):
        print(f"[VALIDACIÓN] El correo electrónico '{email}' no tiene un formato válido.")
        return False

    # Verificar existencia previa
    current = get_user_by_id(uid)
    if not current:
        print(f"[ERROR] No se encontró ningún usuario con el ID {uid}.")
        return False

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        query = "UPDATE users SET name=%s, email=%s, age=%s WHERE id=%s"
        cursor.execute(query, (name.strip(), email.strip(), age_int, uid))
        connection.commit()

        if cursor.rowcount > 0:
            print(f"[ÉXITO] Usuario con ID {uid} actualizado con éxito.")
            return True
        else:
            print(f"[INFORMACIÓN] Los datos proporcionados para el ID {uid} son idénticos a los existentes.")
            return True
    except mysql.connector.IntegrityError as err:
        if err.errno == 1062:
            print(f"[ERROR DUPLICADO] El correo electrónico '{email}' ya pertenece a otro usuario.")
        else:
            print(f"[ERROR INTEGRIDAD]: {err}")
        return False
    except mysql.connector.Error as err:
        print(f"[ERROR BD al actualizar usuario]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_user(user_id):
    """
    Elimina un usuario por su ID.
    Valida que el registro exista antes de confirmar la eliminación.
    """
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        print("[VALIDACIÓN] El ID debe ser un número entero válido.")
        return False

    # Verificar si el usuario existe
    if not get_user_by_id(uid):
        print(f"[ERROR] No se encontró ningún usuario con el ID {uid} para eliminar.")
        return False

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (uid,))
        connection.commit()

        if cursor.rowcount > 0:
            print(f"[ÉXITO] Usuario con ID {uid} eliminado con éxito.")
            return True
        else:
            print(f"[ERROR] No se pudo eliminar el usuario con ID {uid}.")
            return False
    except mysql.connector.Error as err:
        print(f"[ERROR BD al eliminar usuario]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def main_menu():
    """Función controladora del menú interactivo por consola."""
    while True:
        print("\n" + "=" * 52)
        print("     SISTEMA CRUD & REPORTES - PROYECTO COMERZIA")
        print("=" * 52)
        print("  1. Registrar nuevo usuario")
        print("  2. Consultar listado de usuarios")
        print("  3. Actualizar información de usuario")
        print("  4. Eliminar usuario")
        print("  5. Generar Reporte 1: PDF General de Usuarios")
        print("  6. Generar Reporte 2: PDF Estadístico y Demográfico")
        print("  7. Exportar Reporte Adicional a CSV (Excel)")
        print("  8. Salir")
        print("=" * 52)

        choice = input("Seleccione una opción (1-8): ").strip()

        if choice == "1":
            print("\n--- REGISTRAR NUEVO USUARIO ---")
            name = input("Nombre completo: ").strip()
            email = input("Correo electrónico: ").strip()
            age_raw = input("Edad: ").strip()
            create_user(name, email, age_raw)

        elif choice == "2":
            print("\n--- LISTADO GENERAL DE USUARIOS ---")
            read_users()

        elif choice == "3":
            print("\n--- ACTUALIZAR USUARIO ---")
            uid_raw = input("ID del usuario a modificar: ").strip()
            name = input("Nuevo nombre completo: ").strip()
            email = input("Nuevo correo electrónico: ").strip()
            age_raw = input("Nueva edad: ").strip()
            update_user(uid_raw, name, email, age_raw)

        elif choice == "4":
            print("\n--- ELIMINAR USUARIO ---")
            uid_raw = input("ID del usuario a eliminar: ").strip()
            confirm = input(f"¿Está seguro de eliminar el ID {uid_raw}? (s/n): ").strip().lower()
            if confirm in ('s', 'si', 'y', 'yes'):
                delete_user(uid_raw)
            else:
                print("Operación cancelada por el usuario.")

        elif choice == "5":
            print("\n--- GENERANDO REPORTE 1: PDF GENERAL ---")
            generate_pdf_report()

        elif choice == "6":
            print("\n--- GENERANDO REPORTE 2: PDF ESTADÍSTICO ---")
            generate_statistical_report()

        elif choice == "7":
            print("\n--- EXPORTANDO REPORTE A CSV ---")
            export_users_csv()

        elif choice == "8":
            print("\nSaliendo del sistema de gestión... ¡Hasta pronto!")
            break
        else:
            print("\n[AVISO] Opción inválida. Por favor seleccione un número del 1 al 8.")


if __name__ == "__main__":
    main_menu()

