from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
import base64
from datetime import datetime
from .models import Usuario, Dato, PersonaRegistrada

def login(request):
    """Vista para el login de usuarios - CON BASE DE DATOS"""
    
    # Si el usuario ya está logueado, redirigir a inicio
    if request.session.get('usuario_autenticado'):
        return redirect('inicio_admin')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        
        print(f"Intentando login: {nombre}")  # Para debug
        
        # VALIDACIÓN ESPECIAL PARA USUARIO "dani" CON CONTRASEÑA "1"
        if nombre == 'dani' and contrasena == '1':
            # Autenticación exitosa para usuario especial
            request.session['usuario_autenticado'] = True
            request.session['nombre_usuario'] = nombre
            request.session.modified = True
            
            print("Login especial exitoso!")  # Para debug
            return redirect('inicio_admin')
        
        try:
            # Buscar usuario en la base de datos
            usuario = Usuario.objects.get(nombre=nombre)
            
            # Verificar contraseña usando el método del modelo
            if usuario.verificar_contrasena(contrasena):
                # Autenticación exitosa
                request.session['usuario_autenticado'] = True
                request.session['nombre_usuario'] = nombre
                request.session['usuario_id'] = usuario.id
                request.session.modified = True
                
                print("Login exitoso!")  # Para debug
                return redirect('inicio_admin')
            else:
                # Contraseña incorrecta
                raise Usuario.DoesNotExist
                
        except Usuario.DoesNotExist:
            # Autenticación fallida
            print("Login fallido!")  # Para debug
            context = {
                'error': 'Nombre de usuario o contraseña incorrectos'
            }
            return render(request, 'login.html', context)
    
    # Si es GET, mostrar el formulario de login
    return render(request, 'login.html')


def logout(request):
    """Vista para cerrar sesión"""
    if 'usuario_autenticado' in request.session:
        del request.session['usuario_autenticado']
    if 'nombre_usuario' in request.session:
        del request.session['nombre_usuario']
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    
    request.session.modified = True
    return redirect('login')

def eliminar_usuario(request, id):
    """Vista para eliminar un usuario específico"""
    if request.session.get('usuario_autenticado'):
        usuario = get_object_or_404(Usuario, id=id)
        usuario.delete()
    
    return redirect('agregar_usuario')

def agregar_usuario(request):
    """Vista para AGREGAR nuevos usuarios"""
    
    # Verificar autenticación
    if not request.session.get('usuario_autenticado'):
        return redirect('login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        
        if nombre and contrasena:
            # Crear nuevo usuario (el save() se encarga de hashear la contraseña)
            try:
                usuario = Usuario(nombre=nombre, contrasena=contrasena)
                usuario.save()
            except:
                # Si el usuario ya existe, mostrar error
                context = {
                    'usuarios_guardados': Usuario.objects.all(),
                    'error': 'El usuario ya existe'
                }
                return render(request, 'agregar_usuario.html', context)
        
        return redirect('agregar_usuario')
    
    context = {
        'usuarios_guardados': Usuario.objects.all()
    }
    return render(request, 'agregar_usuario.html', context)

def eliminar_dato(request, id):
    """Vista para eliminar un dato específico"""
    if request.session.get('usuario_autenticado'):
        dato = get_object_or_404(Dato, id=id)
        dato.delete()
    
    return redirect('inicio_admin')

def agregar_dato(request):
    """Vista para AGREGAR nuevos datos"""
    
    # Verificar autenticación
    if not request.session.get('usuario_autenticado'):
        return redirect('login')
    
    if request.method == 'POST':
        imagenes = request.FILES.getlist('imagen')
        texto = request.POST.get('texto', '').strip()
        titulo = request.POST.get('titulo', '').strip()
        
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
        fecha_grupo = fecha_actual.strftime("%Y%m%d%H%M%S")
        
        if texto:
            for imagen in imagenes:
                if imagen:
                    # Convertir imagen a base64
                    imagen_base64 = base64.b64encode(imagen.read()).decode('utf-8')
                    imagen_base64 = f"data:{imagen.content_type};base64,{imagen_base64}"
                    
                    # Crear nuevo dato en la base de datos
                    nuevo_dato = Dato(
                        imagen=imagen_base64,
                        texto=texto,
                        titulo=titulo if titulo else f"Grupo {fecha_formateada}",
                        fecha_grupo=fecha_grupo
                    )
                    nuevo_dato.save()
        
        return redirect('agregar_dato')
    
    context = {
        'datos_guardados': Dato.objects.all().order_by('-fecha'),
        'nombre_usuario': request.session.get('nombre_usuario', 'Usuario')
    }
    return render(request, 'agregar.html', context)

def inicio_admin(request):
    """Vista para MOSTRAR los datos agrupados por fecha"""
    
    # Verificar si el usuario está autenticado
    if not request.session.get('usuario_autenticado'):
        return redirect('login')
    
    # Obtener todos los datos ordenados por fecha
    datos = Dato.objects.all().order_by('-fecha')
    
    # Agrupar datos por fecha_grupo
    datos_agrupados = {}
    for dato in datos:
        fecha_grupo = dato.fecha_grupo
        if fecha_grupo not in datos_agrupados:
            datos_agrupados[fecha_grupo] = {
                'fecha': dato.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                'titulo': dato.titulo,
                'items': []
            }
        datos_agrupados[fecha_grupo]['items'].append(dato)
    
    # Convertir a lista para facilitar el template
    grupos_ordenados = []
    for fecha_grupo, grupo_data in datos_agrupados.items():
        grupos_ordenados.append({
            'fecha_grupo': fecha_grupo,
            'fecha': grupo_data['fecha'],
            'titulo': grupo_data['titulo'],
            'items': grupo_data['items']
        })
    
    # Ordenar por fecha (más reciente primero)
    grupos_ordenados.sort(key=lambda x: x['fecha_grupo'], reverse=True)
    
    context = {
        'grupos_datos': grupos_ordenados,
        'nombre_usuario': request.session.get('nombre_usuario', 'Usuario')
    }
    return render(request, 'inicio_admin.html', context)

def inicio(request):
    """Vista principal para visitantes"""
    
    # Manejar registro de personas
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        carnet = request.POST.get('carnet', '').strip()
        
        if nombre and carnet:
            # Guardar en base de datos
            nueva_persona = PersonaRegistrada(nombre=nombre, carnet=carnet)
            nueva_persona.save()
    
    # Obtener todos los datos ordenados por fecha
    datos = Dato.objects.all().order_by('-fecha')
    
    # Agrupar datos por fecha_grupo
    datos_agrupados = {}
    for dato in datos:
        fecha_grupo = dato.fecha_grupo
        if fecha_grupo not in datos_agrupados:
            datos_agrupados[fecha_grupo] = {
                'fecha': dato.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                'titulo': dato.titulo,
                'items': []
            }
        datos_agrupados[fecha_grupo]['items'].append(dato)
    
    grupos_ordenados = []
    for fecha_grupo, grupo_data in datos_agrupados.items():
        grupos_ordenados.append({
            'fecha_grupo': fecha_grupo,
            'fecha': grupo_data['fecha'],
            'titulo': grupo_data['titulo'],
            'items': grupo_data['items']
        })
    
    grupos_ordenados.sort(key=lambda x: x['fecha_grupo'], reverse=True)
    
    context = {
        'grupos_datos': grupos_ordenados,
        'personas': PersonaRegistrada.objects.all().order_by('-fecha_registro'),
        'nombre_usuario': request.session.get('nombre_usuario', 'Usuario')
    }
    return render(request, 'inicio.html', context)