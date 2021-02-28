# Archivos:

## server.py

### create_user()
  POST, recibe un JSON conteniendo 'username', 'password'. 
  'username' tiene que ser un email.
  'password' debe de estar entre 8 y 40 caracteres.
  Si el metodo es exitoso, solo indica que lo fue (el usuario aun tiene que hacer login).
  
 ### login()
  POST, recibe un JSON conteniendo 'username', 'password'. 
  De ser exitoso, retorna un JSON con el 'user_id' y 'token' (jwt) asignado. Cada vez que el usuario haga login o realize un pedido (crear o listar notas), recibe un nuevo token. Esto actua como forma de renovar el token en relacion al tiempo de expiracion.
  
 ### save_note()
  POST, recibe un JSON con un 'user_id', 'token', 'title', 'content'
  Verifica si el JWT dentro de 'token' es valido para el 'user_id', y si aun no expira
  Valida si 'title' y 'content' cumplen con los parametros definidos por el schema en schema.py
  Si todo es correcto, guarda la nota y retorna un JSON con 'user_id' y un nuevo 'token'.
  
 ### get_all_notes()
 GET, .../list-user-notes/<user_id>/<token>
  Verifica si el 'token' es valido para el usuario.
  De serlo, retorna un JSON conteniendo el 'user_id', 'token', y una lista con las notas creadas por el usuario correspondiente.
  
 ### logout()
  POST, recibe un JSON con el 'user_id'
  Elimina cualquier registro de un JWT relacionado a ese usuario dentro de la base de datos, esto significa que el usuario ya no cuenta con forma de utilizar ningun metodo excepto login.
  

## models.py
Contiene los dos modelos User() y Notes().  BaseModel() es utilizado para definir la base de datos a usar. Este archivo tambien se encarga de crear las tablas en caso estas no exista aun.

## schema.py
Define los schemas utilizados para los objetos que luego entran en User() y Notes().  Asi mismo, contiene los metodos para validar si los objetos a ser insertados cumplen con estos schemas.

## token_utilites.py
Maneja la creacion y validacion de jwt relacionados a los usuarios.  Cuando un usuario hace login o cuando realiza algun otro request de manera exitosa, un nuevo token es asignado a el e insertado en la base de datos, asignado a dicho usuario.  Cualquier request que el usuario haga (excepto logout), tendra que entregar dicho nuevo token.
El token expira cuando el usuario hace logout, o luego de 30 minutos.
