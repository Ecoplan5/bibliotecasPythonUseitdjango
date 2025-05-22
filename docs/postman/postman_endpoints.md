# Endpoints para Pruebas en Postman - Biblioteca API

## Autenticación

### Obtener Token JWT
- **URL**: `POST /api/token/`
- **Body**:
  ```json
  {
    "username": "tu_usuario",
    "password": "tu_contraseña"
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "refresh": "token_refresh",
    "access": "token_access"
  }
  ```

### Refrescar Token
- **URL**: `POST /api/token/refresh/`
- **Body**:
  ```json
  {
    "refresh": "tu_refresh_token"
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "access": "nuevo_access_token"
  }
  ```

## API Libros

### Listar todos los libros
- **URL**: `GET /api/libros/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta**:
  ```json
  {
    "mensaje": "Se encontraron 2 libros",
    "libros": [
      {
        "id": 1,
        "titulo": "La bella y la bestia",
        "autor": "Frederick",
        "año_publicacion": 2003,
        "cantidad_stock": 4
      },
      {
        "id": 2,
        "titulo": "Otro libro",
        "autor": "Autor Ejemplo",
        "año_publicacion": 2020,
        "cantidad_stock": 10
      }
    ]
  }
  ```

### Obtener libro específico
- **URL**: `GET /api/libros/{id}/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta**:
  ```json
  {
    "mensaje": "Detalles del libro \"La bella y la bestia\"",
    "libro": {
      "id": 1,
      "titulo": "La bella y la bestia",
      "autor": "Frederick",
      "año_publicacion": 2003,
      "cantidad_stock": 4
    }
  }
  ```

### Crear nuevo libro (solo admin)
- **URL**: `POST /api/libros/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "titulo": "Nuevo Libro",
    "autor": "Autor Nuevo",
    "año_publicacion": 2023,
    "cantidad_stock": 5
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro creado exitosamente",
    "libro": {
      "id": 3,
      "titulo": "Nuevo Libro",
      "autor": "Autor Nuevo",
      "año_publicacion": 2023,
      "cantidad_stock": 5
    }
  }
  ```
- **Respuesta de error**:
  ```json
  {
    "mensaje": "Error al crear el libro",
    "errores": {
      "titulo": ["Este campo es requerido."]
    }
  }
  ```

### Actualizar libro (solo admin)
- **URL**: `PUT /api/libros/{id}/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "titulo": "Título Actualizado",
    "autor": "Autor Actualizado",
    "año_publicacion": 2022,
    "cantidad_stock": 8
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro actualizado exitosamente",
    "libro": {
      "id": 1,
      "titulo": "Título Actualizado",
      "autor": "Autor Actualizado",
      "año_publicacion": 2022,
      "cantidad_stock": 8
    }
  }
  ```

### Actualizar parcialmente un libro (solo admin)
- **URL**: `PATCH /api/libros/{id}/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "cantidad_stock": 10
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro actualizado parcialmente con éxito",
    "libro": {
      "id": 1,
      "titulo": "La bella y la bestia",
      "autor": "Frederick",
      "año_publicacion": 2003,
      "cantidad_stock": 10
    }
  }
  ```

### Eliminar libro (solo admin)
- **URL**: `DELETE /api/libros/{id}/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro \"La bella y la bestia\" eliminado exitosamente"
  }
  ```

## API Usuarios

### Listar usuarios (solo admin)
- **URL**: `GET /api/usuarios/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Se encontraron 2 usuarios",
    "usuarios": [
      {
        "id": 1,
        "username": "SuperAdmin",
        "email": "admin@biblioteca.com",
        "rol": "admin",
        "libros_prestados": []
      },
      {
        "id": 2,
        "username": "usuario_regular",
        "email": "usuario@ejemplo.com",
        "rol": "regular",
        "libros_prestados": [1]
      }
    ]
  }
  ```

### Obtener usuario específico
- **URL**: `GET /api/usuarios/{id}/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Detalles del usuario \"usuario_regular\"",
    "usuario": {
      "id": 2,
      "username": "usuario_regular",
      "email": "usuario@ejemplo.com",
      "rol": "regular",
      "libros_prestados": [1]
    }
  }
  ```

### Crear usuario
- **URL**: `POST /api/usuarios/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "rol": "regular"
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Usuario creado exitosamente",
    "usuario": {
      "id": 3,
      "username": "nuevo_usuario",
      "email": "usuario@example.com",
      "rol": "regular",
      "libros_prestados": []
    }
  }
  ```

### Prestar libro a usuario
- **URL**: `POST /api/usuarios/{id}/prestar_libro/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "libro_id": 1
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro \"La bella y la bestia\" prestado exitosamente a usuario_regular",
    "libro": {
      "id": 1,
      "titulo": "La bella y la bestia",
      "autor": "Frederick",
      "año_publicacion": 2003,
      "cantidad_stock": 3
    }
  }
  ```
- **Respuesta de error**:
  ```json
  {
    "mensaje": "Ya tienes prestado el libro \"La bella y la bestia\""
  }
  ```

### Devolver libro
- **URL**: `POST /api/usuarios/{id}/devolver_libro/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Body**:
  ```json
  {
    "libro_id": 1
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Libro \"La bella y la bestia\" devuelto exitosamente por usuario_regular",
    "libro": {
      "id": 1,
      "titulo": "La bella y la bestia",
      "autor": "Frederick",
      "año_publicacion": 2003,
      "cantidad_stock": 4
    }
  }
  ```
- **Respuesta de error**:
  ```json
  {
    "mensaje": "No tienes prestado el libro \"La bella y la bestia\""
  }
  ```

### Consultar libros prestados de un usuario
- **URL**: `GET /api/usuarios/{id}/mis_libros/`
- **Headers**: `Authorization: Bearer {tu_token_access}`
- **Respuesta exitosa**:
  ```json
  {
    "mensaje": "Se encontraron 1 libros prestados a usuario_regular",
    "libros": [
      {
        "id": 1,
        "titulo": "La bella y la bestia",
        "autor": "Frederick",
        "año_publicacion": 2003,
        "cantidad_stock": 3
      }
    ]
  }
  ```

## Interfaz Web (Endpoints para navegador)

### Página principal (Listado de libros)
- **URL**: `GET /libros/`

### Detalle de libro
- **URL**: `GET /libros/{id}/`

### Formulario de nuevo libro (solo admin)
- **URL**: `GET /libros/nuevo/`

### Formulario de editar libro (solo admin)
- **URL**: `GET /libros/{id}/editar/`

### Confirmación de eliminar libro (solo admin)
- **URL**: `GET /libros/{id}/eliminar/`

### Lista de préstamos del usuario
- **URL**: `GET /mis-prestamos/`

### Historial de préstamos (solo admin)
- **URL**: `GET /historial-prestamos/`

### Login
- **URL**: `GET /login/`

### Logout
- **URL**: `GET /logout/`

### Registro de usuario
- **URL**: `GET /registro/` 