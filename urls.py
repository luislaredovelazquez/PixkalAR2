from django.urls import path, include, reverse_lazy # new
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


from . import views

app_name = 'pixkal2'
urlpatterns = [
    path('', views.mostrarIndex, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:pk>/AR/', views.ARView.as_view(), name='ar'),
    path('markerAR/<avatar_id>/', views.MarkerAR, name='markerar'),
    path('soloAR/<avatar_id>/', views.SoloAR, name='soloar'),
    path('treasure/<busquedalugar_id>/', views.IniciarBusqueda, name='treasure'),
    path('treasure/activarBusqueda/<busqueda_id>/', views.ActivarBusqueda, name='activatetreasure'),
    path('treasure/cancelarBusqueda/<busqueda_id>/', views.CancelarBusqueda, name='canceltreasure'),
    path('treasure/iniciar/<busqueda_id>/', views.ComenzarBusqueda, name='starttreasure'),
    path('treasure/status/<busqueda_id>/<busqueda_lugar_id>', views.StatusBusqueda, name='statustreasure'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('pixkal2:password_reset_done')), name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('pixkal2:password_reset_complete')), name='password_reset_confirm'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.Signup, name='signup'),
    path('registrar/busqueda/', views.RegistrarBusqueda, name='registrarbusqueda'),
    path('busqueda/<int:pk>/editar/', views.EditarBusqueda, name='editarbusqueda'),
    path('registrar/busquedalugar/<busqueda_id>/', views.RegistrarBusquedaLugar, name='registrarbusquedalugar'),
    path('busquedalugar/<int:pk>/editar/', views.EditarBusquedaLugar, name='editarbusquedalugar'),
    path('agregar/participante/<busqueda_id>/', views.AgregarParticipante, name='agregarparticipante'),
    path('dashboard/', views.VerDashboard, name='dashboard'),
    path('misbusquedas/', views.VerMisBusquedas, name='misbusquedas'),
    path('busquedasparticipo/', views.VerBusquedasParticipo, name='busquedasparticipo'),
    path('mapa/<busqueda_lugar_id>/', views.VerMapa, name='mapa'),
    path('verAvatar/<busqueda_lugar_id>/', views.VerAvatar, name='verAvatar'),
    path('seleccionarAvatar/<avatar_id>/<busqueda_lugar_id>/', views.SeleccionarAvatar, name='seleccionarAvatar'),
    path('treasure/informacion/<busqueda_id>/', views.VerInformacionBusqueda, name='treasureinfo'),
    path('galeriaar/', views.VerGaleriaAR, name='galeriaar'),
    path('clase/registrar/', views.RegistrarClase, name='registrarclase'),
    path('clase/actualizar/<clase_id>/', views.ActualizarClase, name='actualizarclase'),
    path('clase/ver/<clase_id>/', views.VerClase, name='verclase'),
    path('perfil/registrar/', views.RegistrarPerfil, name='registrarperfil'),
    path('perfil/actualizar/', views.ActualizarPerfil, name='actualizarperfil'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)