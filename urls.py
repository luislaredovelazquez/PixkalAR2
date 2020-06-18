from django.urls import path, include, reverse_lazy # new
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


from . import views

app_name = 'pixkal2'
urlpatterns = [
    path('', views.mostrarIndex, name='index'),
    path('markerAR/<avatar_id>/', views.MarkerAR, name='markerar'),
    path('soloAR/<avatar_id>/', views.SoloAR, name='soloar'),
    path('treasure/<busquedalugar_id>/', views.IniciarBusqueda, name='treasure'),
    path('treasure/activarBusqueda/<busqueda_id>/', views.ActivarBusqueda, name='activatetreasure'),
    path('treasure/cancelarBusqueda/<busqueda_id>/', views.CancelarBusqueda, name='canceltreasure'),
    path('treasure/iniciar/<busqueda_id>/', views.ComenzarBusqueda, name='starttreasure'),
    path('treasure/status/<busqueda_id>/<busqueda_lugar_id>', views.StatusBusqueda, name='statustreasure'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('pixkal2:password_reset_done')), name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('pixkal2:password_reset_complete')), name='password_reset_confirm'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.Signup, name='signup'),
    path('registrar/busqueda/', views.RegistrarBusqueda, name='registrarbusqueda'),
    path('busqueda/<int:pk>/editar/', views.EditarBusqueda, name='editarbusqueda'),
    path('busqueda/imagen/actualizar/<int:pk>/', views.ActualizarImagenBusqueda, name='actualizarimagenbusqueda'),
    path('registrar/busquedalugar/<busqueda_id>/', views.RegistrarBusquedaLugar, name='registrarbusquedalugar'),
    path('busquedalugar/<int:pk>/editar/', views.EditarBusquedaLugar, name='editarbusquedalugar'),
    path('dashboard/', views.VerDashboard, name='dashboard'),
    path('misbusquedas/', views.VerMisBusquedas, name='misbusquedas'),
    path('mapa/<busqueda_lugar_id>/', views.VerMapa, name='mapa'),
    path('verAvatar/<busqueda_lugar_id>/', views.VerAvatar, name='verAvatar'),
    path('seleccionarAvatar/<avatar_id>/<busqueda_lugar_id>/', views.SeleccionarAvatar, name='seleccionarAvatar'),
    path('galeriaar/', views.VerGaleriaAR, name='galeriaar'),
    path('perfil/actualizar/', views.ActualizarPerfil, name='actualizarperfil'),
    path('pregunta/actualizar/<blugar>/', views.ActualizarPregunta, name='actualizarpregunta'),
    path('pregunta/eliminar/<blugar>/', views.EliminarPregunta, name='eliminarpregunta'),
    path('pregunta/ver/<blugar>/', views.VerPregunta, name='verpregunta'),
    path('sonido/lugar/<blugar>/<tipo>/', views.AgregarSonido, name='agregarsonido'),
    path('sonido/subir/<blugar>/<tipo>/', views.SubirSonido, name='subirsonido'),
    path('sonido/eliminar/<blugar>/<tipo>/', views.EliminarSonido, name='eliminarsonido'),
    path('modelobAR/<blugar>/<tipo>/', views.ModeloBAR, name='modelobar'),
    path('misclases/', views.VerMisClases, name='misclases'),
    path('clase/registrar/', views.RegistrarClase, name='registrarclase'),
    path('clase/editar/<int:pk>/', views.EditarClase, name='editarclase'),
    path('clase/activar/<clase_id>/', views.ActivarClase, name='activarclase'),
    path('clase/cancelar/<clase_id>/', views.CancelarClase, name='cancelarclase'),
    path('clase/visualizar/<clase_id>/<orden>/', views.VisualizarClase, name='visualizarclase'),
    path('clase/imagen/actualizar/<int:pk>/', views.ActualizarImagenClase, name='actualizarimagenclase'),
    path('item/registrar/<clase_id>/', views.RegistrarItemClase, name='registraritemclase'),
    path('item/actualizar/<item_id>/', views.ActualizarClaseItem, name='actualizaritemclase'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)