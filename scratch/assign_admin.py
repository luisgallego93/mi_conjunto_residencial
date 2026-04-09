from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario

def assign_admin():
    user = User.objects.filter(username='admin2').first()
    if user:
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        perfil.rol = 'ADMIN_CONJUNTO'
        # Tambien asegurar que tenga nombre completo si es nuevo
        if not perfil.nombre_completo:
            perfil.nombre_completo = "Administrador del Conjunto"
        perfil.save()
        print(f"Rol de {user.username} actualizado a {perfil.rol}")
    else:
        print("Usuario admin2 no encontrado")

if __name__ == "__main__":
    assign_admin()
