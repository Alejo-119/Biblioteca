from flask import Flask, request, jsonify
from flask_cors import CORS
import pyrebase
from firebaseConfig import firebaseConfig

app = Flask(__name__)
CORS(app)
# Conectar Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

class Usuario:

    def __init__(self, id_usuario, nombre, contraseña, email):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.contraseña = contraseña
        self.email = email

    # Método para registrar un usuario
    def registrar_usuario(self):
        print(f"Usuario {self.nombre} registrado con éxito, su ID de usuario es: {self.id_usuario} :)")
    
    # Método pata modificar los datos de usuario
    def modificar_usuario(self, nombre=None, contraseña=None, email=None):
        if nombre:
            self.nombre = nombre
        if contraseña:
            self.contraseña = contraseña
        if email:
            self.email = email
        print(f"Usuario {self.id_usuario} modificado con éxito.")

    # Método para eliminar el usuario

    def eliminar_usuario(self):
        print(f"Usuario {self.id_usuario} ha sido eliminado :( ")

class Libro:

    def __init__(self, id_libro, autor, titulo, editorial, disponible):
        self.id_libro = id_libro
        self.autor = autor
        self.titulo = titulo
        self.editorial = editorial
        self.disponible = disponible

    # Métododo para mostrar detalles del libro
    def mostrar_detalles(self):
        return{
            "ID": self.id_libro,
            "Autor": self.autor,
            "Título": self.titulo,
            "Editorial": self.editorial,
            "Disponible": self.disponible
        }
    
    # Método para obtener libros disponibles desde Firebase
    @staticmethod
    def obtener_libros_disponibles():
        libros_disponibles = db.child("libros").order_by_child("Disponible").equal_to(True).get()
        return [libro.val() for libro in libros_disponibles.each()]

    # Método para obtener libros no disponibles desde Firebase
    @staticmethod
    def obtener_libros_no_disponibles():
        libros_no_disponibles = db.child("libros").order_by_child("Disponible").equal_to(False).get()
        return [libro.val() for libro in libros_no_disponibles.each()]



class Prestamo:

    def __init__(self, id_prestamo, id_libro, id_usuario, fecha_prestamo, fecha_entrega):
        self.id_prestamo = id_prestamo
        self.id_libro = id_libro
        self.id_usuario = id_usuario
        self.fecha_prestamo = fecha_prestamo
        self.fecha_entrega = fecha_entrega

    # Método para registrar un préstamo
    def registrar_prestamo(self):
        return {
            "ID Préstamo": self.id_prestamo,
            "ID Libro": self.id_libro,
            "Fecha Préstamo": self.fecha_prestamo,
            "Fecha Entrega": self.fecha_entrega,
            "ID Usuario": self.id_usuario
        }
    
    # Método para registrar devolución
    def registrar_devolución(self, fecha_devolucion):
        self.fecha_entrega = fecha_devolucion
        return f"Préstamo {self.id_prestamo} registrado como devuelto el {self.fecha_entrega}."

class Admin:

    def __init__(self, id_admin, usuario, contraseña):
        self.id_admin = id_admin
        self.usuario = usuario
        self.contraseña = contraseña

    # Método para agregar un libro a la base de datos
    def agregar_libro(self, libro):
        return libro.mostrar_detalles()
    
    # Método para eliminar un libro
    def eliminar_libro(self, id_libro):
        return f" Libro con ID {id_libro} ha sido eliminado."
    
    # Método para bloquear a un usuario
    def bloquear_usuario(self, id_usuario):
        return f"Usuario con ID {id_usuario} ha sido bloqueado."

    

# Endpoint para registrar un nuevo libro en la biblioteca
@app.route('/crear_libro', methods=['POST'])
def agregar_libro():
    datos = request.json
    nuevo_libro = Libro(
        id_libro=datos.get('id_libro'),
        autor=datos.get('autor'),
        titulo=datos.get('titulo'),
        editorial=datos.get('editorial'),
        disponible=datos.get('disponible')
    )
    
    # Crear un administrador (usando el asmin por defecto o uno que estés manejando)
    admin = Admin(id_admin="admin", usuario="admin", contraseña="admine123")

    # Usar método agregar_libro
    libro_data = admin.agregar_libro(nuevo_libro)

    # Guardar en Firebase
    db.child("libros").push(libro_data)

    return jsonify({"mensaje": f"Libro '{nuevo_libro.titulo}' agregado con éxito. "}), 201

# Endpoint para hacer un prestamo
@app.route('/registrar_prestamo', methods=['POST'])
def registrar_prestamo():
    datos = request.json
    nuevo_prestamo = Prestamo(
        id_prestamo=datos.get('id_prestamo'),
        id_libro=datos.get('id_libro'),
        fecha_prestamo=datos.get('fecha_prestamo'),
        fecha_entrega=datos.get('fecha_entrega'),
        id_usuario=datos.get('id_usuario')
    )
    
    prestamo_data = nuevo_prestamo.registrar_prestamo()
    
    # Guardar en Firebase
    db.child("prestamos").push(prestamo_data)
    
    return jsonify({"mensaje": "Préstamo registrado con éxito"}), 201

# Endpoint para bloquear un usuario
@app.route('/bloquear_usuario/<id_usuario>', methods=['PUT'])
def bloquear_usuario(id_usuario):
    admin = Admin(id_admin="admin1", usuario="admin", contraseña="admin123")
    
    mensaje = admin.bloquear_usuario(id_usuario)
    
    # Podrías actualizar algo en la base de datos si fuera necesario
    db.child("usuarios").child(id_usuario).update({"bloqueado": True})
    
    return jsonify({"mensaje": mensaje}), 200

# Endpoint para registrar usuario
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    datos = request.json
    nuevo_usuario = Usuario(
        id_usuario=datos.get('id_usuario'),
        nombre=datos.get('nombre'),
        contraseña=datos.get('contraseña'),
        email=datos.get('email')
    )

    # Guardar en Firebase
    db.child("usuarios").push({
        "id_usuario": nuevo_usuario.id_usuario,
        "nombre": nuevo_usuario.nombre,
        "contraseña": nuevo_usuario.contraseña,
        "email": nuevo_usuario.email
    })

    return jsonify({"mensaje": f"Usuario '{nuevo_usuario.nombre}' registrado con éxito."}), 201

# Endpoint para modificar usuarios
@app.route('/modificar_usuario/<id_usuario>', methods=['PUT'])
def modificar_usuario(id_usuario):
    datos = request.json
    usuario_actualizado = db.child("usuarios").child(id_usuario).get().val()

    if usuario_actualizado:
        db.child("usuarios").child(id_usuario).update({
            "nombre": datos.get('nombre', usuario_actualizado["nombre"]),
            "contraseña": datos.get('contraseña', usuario_actualizado["contraseña"]),
            "email": datos.get('email', usuario_actualizado["email"])
        })
        return jsonify({"mensaje": f"Usuario '{id_usuario}' actualizado con éxito."}), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
# Eliminar Usuarios

@app.route('/eliminar_usuario/<id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    db.child("usuarios").child(id_usuario).remove()
    return jsonify({"mensaje": f"Usuario '{id_usuario}' eliminado con éxito. "}), 200

#Definir la ruta principal "/"
@app.route('/')
def home():
    return "¡Bienvenido a la API de la Biblioteca!"


# Obtener libros Disponibles y No Disponibles
@app.route('/libros_disponibles', methods=['GET'])
def obtener_libros_disponibles():
    libros_disponibles = Libro.obtener_libros_disponibles()
    return jsonify(libros_disponibles), 200

@app.route('/libros_no_disponibles', methods=['GET'])
def obtener_libros_no_disponibles():
    libros_no_disponibles = Libro.obtener_libros_no_disponibles()
    return jsonify(libros_no_disponibles), 200


if __name__ == '__main__':
    app.run(debug=True) 