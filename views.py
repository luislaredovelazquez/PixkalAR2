from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, authenticate
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Choice, Question, Busqueda, BusquedaLugar, BusquedaParticipante, ItemEncontrado, Avatar, Clase, Perfil, ClaseItem, Dash
from .forms import BusquedaForm, BusquedaLugarForm, SignUpForm, ClaseForm, PerfilForm, BusquedaImagenForm, ItemClaseForm, ClaseImagenForm
from django.conf import settings

def mostrarIndex(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pixkal2:dashboard'))
    else:
        return render(request, 'pixkal2/index.html')
#    context_object_name = 'latest_question_list'

#   def get_queryset(self):
#        """
#        Return the last five published questions (not including those set to be
#        published in the future).
#        """
#        return Question.objects.filter(
#            pub_date__lte=timezone.now()
#        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'pixkal2/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'pixkal2/results.html'

class ARView(generic.DetailView):
    model = Question
    template_name = 'pixkal2/AR.html'

def MarkerAR(request,avatar_id):
    avatar = Avatar.objects.get(id=avatar_id)
    return render(request, 'pixkal2/markerAR.html',{'avatar' : avatar})

def SoloAR(request,avatar_id):
    avatar = Avatar.objects.get(id=avatar_id)
    return render(request, 'pixkal2/soloAR.html',{'avatar' : avatar})

def ActivarBusqueda(request,busqueda_id):
    busqueda = Busqueda.objects.get(id=busqueda_id)
    busqueda.estado = 'A'
    busqueda.save()

    try:
        dash = Dash.objects.get(id_actividad=busqueda_id,servicio='B')
        dash.titulo = busqueda.titulo_busqueda
        dash.descripcion = busqueda.descripcion
        dash.imagen = busqueda.imagen
        dash.estado = 'A'
        dash.save()
    except Dash.DoesNotExist:
        dash = Dash()
        dash.servicio = 'B'
        dash.estado = 'A'
        dash.usuario = request.user
        dash.titulo = busqueda.titulo_busqueda
        dash.descripcion = busqueda.descripcion
        dash.imagen = busqueda.imagen
        dash.url = 'treasure/iniciar/' + str(busqueda.id)
        dash.id_actividad = busqueda.id
        dash.save()

    return render(request, 'pixkal2/activatetreasure.html', {'busqueda': busqueda, 'busqueda_id' : busqueda_id})

def CancelarBusqueda(request,busqueda_id):
    busqueda = Busqueda.objects.get(id=busqueda_id)
    busqueda.estado = 'C'
    busqueda.save()

    try:
        dash = Dash.objects.get(id_actividad=busqueda.id,servicio='B')
        dash.estado = 'I'
        dash.save()
    except Dash.DoesNotExist:
        return render(request, 'pixkal2/canceltreasure.html', {'busqueda': busqueda, 'busqueda_id' : busqueda_id})

    return render(request, 'pixkal2/canceltreasure.html', {'busqueda': busqueda, 'busqueda_id' : busqueda_id})

def IniciarBusqueda(request,busquedalugar_id):
#    busquedalugares = BusquedaLugar.objects.filter(id=busquedalugar_id)
    busquedalugar = get_object_or_404(BusquedaLugar, pk=busquedalugar_id)
    return render(request, 'pixkal2/treasure.html', {'busquedalugar': busquedalugar, 'busqueda_id' : busquedalugar.busqueda.id})

def ComenzarBusqueda(request,busqueda_id):
    busqueda = Busqueda.objects.get(id=busqueda_id)
    busquedalugares = BusquedaLugar.objects.filter(busqueda=busqueda_id)

    numero_lugares = busquedalugares.count()

    if numero_lugares > 0:
        aleatorio = random.randint(1,numero_lugares)
        incremental = 1

        for lugarbusqueda in busquedalugares:
            if incremental == aleatorio:
                siguientelugar = lugarbusqueda
                break
            incremental = incremental + 1
        return render(request, 'pixkal2/starttreasure.html', {'busqueda': busqueda,'siguientelugar': siguientelugar,})

    else:
        mensaje = 'Esta búsqueda no contiene elementos para explorar'
        return render(request,'pixkal2/mensaje_error.html',{'mensaje' : mensaje})

def StatusBusqueda(request,busqueda_id,busqueda_lugar_id):

    participantes = BusquedaParticipante.objects.filter(busqueda=busqueda_id).order_by('-items_encontrados')[:10]
    contar = 0
    primero = BusquedaParticipante()
    for participante in participantes:
        if contar == 0:
            primero = participante
            break

    busqueda_completada = 0
    siguientelugar = BusquedaLugar()
    busquedaparticipante = BusquedaParticipante.objects.get(busqueda=busqueda_id,usuario=request.user)
    busqueda = Busqueda.objects.get(pk=busqueda_id)

#   Validar que no haya terminado la búsqueda previamente
    if busquedaparticipante.items_encontrados == busqueda.no_items:
        busqueda_completada = 1
        return render(request, 'pixkal2/status_treasure.html',{'siguientelugar': siguientelugar, 'busqueda' : busqueda, 'busqueda_completada' : busqueda_completada,'participantes' : participantes,'primero' : primero})

#   Validar que sólo se pueda registrar una vez este item.

    try:
        validar_item = ItemEncontrado.objects.get(busqueda=busqueda_id,usuario=request.user,lugar=busqueda_lugar_id)
    except ItemEncontrado.DoesNotExist:
        validar_item = None

    if validar_item:
        siguientelugar = obtenerAleatorio(busqueda_id,request.user);
        return render(request, 'pixkal2/status_treasure.html',{'siguientelugar': siguientelugar, 'busqueda' : busqueda, 'busqueda_completada' : busqueda_completada,'participantes' : participantes,'primero' : primero})

#Se registra el item encontrado
    itemencontrado = ItemEncontrado()
    itemencontrado.usuario = request.user
    itemencontrado.busqueda = busqueda
    busquedalugar = BusquedaLugar.objects.get(pk=busqueda_lugar_id)
    itemencontrado.lugar = busquedalugar
    itemencontrado.save()

    busquedaparticipante.items_encontrados = busquedaparticipante.items_encontrados + 1
    busquedaparticipante.save()

#En caso de que haya sido el último item se envía a la pantalla de búsqueda terminada
    if busquedaparticipante.items_encontrados == busqueda.no_items:
        busquedaparticipante.estado = "T"
        busquedaparticipante.save()
        busqueda_completada = 1
        return render(request, 'pixkal2/status_treasure.html',{'siguientelugar': siguientelugar, 'busqueda' : busqueda, 'busqueda_completada' : busqueda_completada,'participantes' : participantes,'primero' : primero})

    siguientelugar = obtenerAleatorio(busqueda_id,request.user);
    return render(request, 'pixkal2/status_treasure.html',{'siguientelugar': siguientelugar, 'busqueda' : busqueda, 'busqueda_completada' : busqueda_completada,'participantes' : participantes,'primero' : primero})


def obtenerAleatorio(busqueda_id,usuario_id):
    #Si no fue el último item, se envía al siguiente lugar de manera aletoria
    lugaresbusqueda = BusquedaLugar.objects.filter(busqueda=busqueda_id)
    itemsencontrados = ItemEncontrado.objects.filter(busqueda=busqueda_id,usuario=usuario_id)
    for lugarbusqueda in lugaresbusqueda:
        for itemencontrado in itemsencontrados:
            if lugarbusqueda.id == itemencontrado.lugar.id:
                lugaresbusqueda = lugaresbusqueda.exclude(id = lugarbusqueda.id)

    numero_lugares = lugaresbusqueda.count()
    aleatorio = random.randint(1,numero_lugares)
    incremental = 1

    for lugarbusqueda in lugaresbusqueda:
        if incremental == aleatorio:
            siguientelugar = lugarbusqueda
            break
        incremental = incremental + 1
    return siguientelugar;

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'pixkal2/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('pixkal2:results', args=(question.id,)))

##Lugares


def RegistrarBusqueda(request):
    if request.method == "POST":
        formulario = BusquedaForm(request.POST)
        if formulario.is_valid():
            busqueda = formulario.save(commit=False)
            busqueda.estado = 'Inactivo'
            busqueda.creador = request.user
            perfil = Perfil.objects.get(usuario=request.user)
            busqueda.perfil = perfil
            busqueda.numero_personas = 0
            busqueda.save()
            busqueda_id=busqueda.pk
            return HttpResponseRedirect(reverse('pixkal2:registrarbusquedalugar', args=(busqueda_id,)))
    else:
        form = BusquedaForm()
        editar = 0
        return render(request, 'pixkal2/registrarbusqueda.html', {'form': form, 'editar': editar })

def EditarBusqueda(request, pk):
    busqueda = get_object_or_404(Busqueda, pk=pk)
    if request.method == "POST":
        form = BusquedaForm(request.POST, instance=busqueda)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            try:
                dash = Dash.objects.get(id_actividad=busqueda.id,servicio='B')
                dash.titulo = busqueda.titulo_busqueda
                dash.descripcion = busqueda.descripcion
                dash.imagen = busqueda.imagen
                dash.save()
            except Dash.DoesNotExist:
                return redirect('pixkal2:misbusquedas')

            return redirect('pixkal2:misbusquedas')
    else:
        form = BusquedaForm(instance=busqueda)
        busquedalugares = BusquedaLugar.objects.filter(busqueda=busqueda)
        editar = 1
        return render(request, 'pixkal2/registrarbusqueda.html', {'form': form,'busquedalugares': busquedalugares,'busqueda' : busqueda, 'editar': editar })
    return redirect('pixkal2:misbusquedas')

def ActualizarImagenBusqueda(request,pk):
    busqueda = get_object_or_404(Busqueda, pk=pk)
    if request.method == "POST":
        form = BusquedaImagenForm(request.POST, request.FILES, instance=busqueda)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            try:
                dash = Dash.objects.get(id_actividad=busqueda.id,servicio='B')
                dash.titulo = busqueda.titulo_busqueda
                dash.descripcion = busqueda.descripcion
                dash.imagen = busqueda.imagen
                dash.save()
            except Dash.DoesNotExist:
                return redirect('pixkal2:misbusquedas')

        return redirect('pixkal2:misbusquedas')
    return render(request, 'pixkal2/actualizarimagenbusqueda.html')

def RegistrarBusquedaLugar(request,busqueda_id):
    if request.method == "POST":
        formulario = BusquedaLugarForm(request.POST)
        if formulario.is_valid():
            busquedalugar = formulario.save(commit=False)
            busqueda = Busqueda.objects.get(pk=busqueda_id)
            busquedalugar.busqueda = busqueda
            avatar = get_object_or_404(Avatar, pk=1)
            busquedalugar.avatar = avatar
#            post.published_date = timezone.now()
            busquedalugar.save()
            busqueda.no_items = busqueda.no_items + 1
            busqueda.save()
            busqueda_lugar_id = busquedalugar.id
            return HttpResponseRedirect(reverse('pixkal2:verAvatar', args=(busqueda_lugar_id,)))
    else:
        form = BusquedaLugarForm()
        busquedalugar = BusquedaLugar()
        busquedalugar.id = 0
        return render(request, 'pixkal2/registrarbusquedalugar.html', {'form': form, 'busquedalugar' : busquedalugar})

def EditarBusquedaLugar(request, pk):
    busquedalugar = get_object_or_404(BusquedaLugar, pk=pk)
    if request.method == "POST":
        form = BusquedaLugarForm(request.POST, instance=busquedalugar)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('pixkal2:misbusquedas')
    else:
        form = BusquedaLugarForm(instance=busquedalugar)
        busquedalugar = BusquedaLugar.objects.get(id=pk)
    return render(request, 'pixkal2/registrarbusquedalugar.html', {'form': form,'busquedalugar':busquedalugar})

def AgregarParticipante(request, busqueda_id):
#Luego va a ser POST
    if request.method == "GET":
#Validar que los usuarios no se registren 2 veces
        try:
            validado = BusquedaParticipante.objects.filter(busqueda=busqueda_id,usuario=request.user)
        except ItemEncontrado.DoesNotExist:
            validado = None

        if validado:
            return HttpResponseRedirect(reverse('pixkal2:dashboard'))

        busquedaparticipante = BusquedaParticipante()
        busquedaparticipante.usuario = request.user
        busqueda = Busqueda.objects.get(pk=busqueda_id)
        busquedaparticipante.busqueda = busqueda
        busquedaparticipante.items_encontrados = 0
        busquedaparticipante.estado = 'P'
        busquedaparticipante.save()
        return HttpResponseRedirect(reverse('pixkal2:busquedasparticipo'))
    else:
        return HttpResponseRedirect(reverse('pixkal2:dashboard'))

def VerDashboard(request):
    idusuario = request.user
    dash = Dash.objects.filter(estado='A').order_by('-id')

# Paginador de búsqueda

    page = request.GET.get('page', 1)

    paginator = Paginator(dash, 6)
    try:
        lista_dashboard = paginator.page(page)
    except PageNotAnInteger:
        lista_dashboard = paginator.page(1)
    except EmptyPage:
        lista_dashboard = paginator.page(paginator.num_pages)

    return render(request, 'pixkal2/dashboard.html',{'dashboard' : lista_dashboard,'idusuario' : idusuario})

def VerMisBusquedas(request):
    idusuario = request.user
    misbusquedas = Busqueda.objects.filter(creador=request.user).order_by('-id')
    perfil = get_object_or_404(Perfil, usuario=request.user)
    # Paginador de mis búsquedas

    mipage = request.GET.get('page', 1)

    mipaginator = Paginator(misbusquedas, 6)
    try:
        lista_mibusqueda = mipaginator.page(mipage)
    except PageNotAnInteger:
        lista_mibusqueda = mipaginator.page(1)
    except EmptyPage:
        lista_mibusqueda = mipaginator.page(mipaginator.num_pages)

    return render(request, 'pixkal2/misbusquedas.html',{'misbusquedas' : lista_mibusqueda,'idusuario' : idusuario,'perfil' : perfil})


def VerBusquedasParticipo(request):
    idusuario = request.user
    busquedasparticipo = BusquedaParticipante.objects.filter(usuario=request.user).exclude(estado='G').exclude(estado='T')
    busquedas = Busqueda.objects.filter(estado='A').exclude(creador=request.user).order_by('-id')
    for busqueda in busquedas:
        for busquedaparticipo in busquedasparticipo:
            if busqueda.id == busquedaparticipo.busqueda.id:
                busquedasparticipo = busquedasparticipo.filter(id = busquedaparticipo.id)

# Paginador de búsquedas donde participo

    pageparticipo = request.GET.get('page', 1)

    paginatorparticipo = Paginator(busquedasparticipo, 6)
    try:
        lista_busquedaparticipo = paginatorparticipo.page(pageparticipo)
    except PageNotAnInteger:
        lista_busquedaparticipo = paginatorparticipo.page(1)
    except EmptyPage:
        lista_busquedaparticipo = paginatorparticipo.page(paginatorparticipo.num_pages)

    return render(request, 'pixkal2/busquedasparticipo.html',{'idusuario' : idusuario,'busquedasparticipo' : lista_busquedaparticipo})



def Signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            perfil = Perfil()
            perfil.usuario = user
            avatar = get_object_or_404(Avatar, pk=1)
            perfil.avatar = avatar
            perfil.save()
            login(request, user)
            return HttpResponseRedirect(reverse('pixkal2:dashboard'))
    else:
        form = SignUpForm()
    return render(request, 'pixkal2/signup.html', {'form': form})


def VerMapa(request, busqueda_lugar_id):
    busquedalugar = get_object_or_404(BusquedaLugar, pk=busqueda_lugar_id)
    return render(request, 'pixkal2/mapa.html',{ 'busquedalugar' : busquedalugar })

def VerAvatar(request, busqueda_lugar_id):
    avatares = Avatar.objects.all().order_by('-id')
    mipage = request.GET.get('page', 1)

    mipaginator = Paginator(avatares, 20)
    try:
        lista_mibusqueda = mipaginator.page(mipage)
    except PageNotAnInteger:
        lista_mibusqueda = mipaginator.page(1)
    except EmptyPage:
        lista_mibusqueda = mipaginator.page(mipaginator.num_pages)
    busquedalugar = get_object_or_404(BusquedaLugar, pk=busqueda_lugar_id)
    return render(request, 'pixkal2/verAvatar.html',{ 'busquedalugar' : busquedalugar,'misbusquedas' : lista_mibusqueda,'avatares' : avatares })

def SeleccionarAvatar(request, avatar_id, busqueda_lugar_id):
    if request.method == 'GET':
        avatar = get_object_or_404(Avatar, pk=avatar_id)
        busquedalugar = get_object_or_404(BusquedaLugar, pk=busqueda_lugar_id)
        busquedalugar.avatar = avatar
        busquedalugar.save()
        return HttpResponseRedirect(reverse('pixkal2:misbusquedas'))
#        , args=(question.id,)))
    else:
        return render(request, 'pixkal2/dashboard.html')


def VerInformacionBusqueda(request,busqueda_id):
    busqueda = get_object_or_404(Busqueda, pk=busqueda_id)
    return render(request,'pixkal2/treasure_info.html',{'busqueda' : busqueda})

def VerGaleriaAR(request):
    avatares = Avatar.objects.all().order_by('-id')
    mipage = request.GET.get('page', 1)

    mipaginator = Paginator(avatares, 20)
    try:
        lista_mibusqueda = mipaginator.page(mipage)
    except PageNotAnInteger:
        lista_mibusqueda = mipaginator.page(1)
    except EmptyPage:
        lista_mibusqueda = mipaginator.page(mipaginator.num_pages)
    return render(request,'pixkal2/galeria_ar.html',{'misbusquedas' : lista_mibusqueda,'avatares' : avatares })

def RegistrarClase(request):
    if request.method == "POST":
        formulario = ClaseForm(request.POST)
        if formulario.is_valid():
            clase = formulario.save(commit=False)
            clase.usuario = request.user
            perfil = get_object_or_404(Perfil, usuario=request.user)
            clase.perfil = perfil
            avatar = get_object_or_404(Avatar, id=1)
            clase.avatar = avatar
            clase.save()
#            clase_id=clase.pk
            return HttpResponseRedirect(reverse('pixkal2:dashboard'))
    else:
        form = ClaseForm()
        editar = 0
        return render(request, 'pixkal2/gestionarclase.html', {'form': form, 'editar': editar })

def ActualizarClase(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    if request.method == "POST":
        form = ClaseForm(request.POST, request.FILES, instance=clase)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            try:
                dash = Dash.objects.get(id_actividad=clase.id,servicio='C')
                dash.titulo = clase.titulo
                dash.imagen = clase.imagen
                dash.save()
            except Dash.DoesNotExist:
                return redirect('pixkal2:misclases')

            return redirect('pixkal2:dashboard')
    else:
        form = ClaseForm(instance=clase)
        editar = 1
    return render(request, 'pixkal2/gestionarclase.html', {'form': form, 'editar': editar })

def VerClase(request, clase_id):
    clase = get_object_or_404(Clase, pk=clase_id)
    return render(request, 'pixkal2/verclase.html',{ 'clase' : clase })

def RegistrarPerfil(request):
    if request.method == "POST":
        formulario = PerfilForm(request.POST, request.FILES)
        if formulario.is_valid():
            perfil = formulario.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
#            clase_id=clase.pk
            return HttpResponseRedirect(reverse('pixkal2:dashboard'))
    else:
        form = PerfilForm()
        editar = 0
        return render(request, 'pixkal2/gestionarperfil.html', {'form': form, 'editar': editar })

def ActualizarPerfil(request):
    perfil = get_object_or_404(Perfil, pk=request.user.id)
    if request.method == "POST":
        form = PerfilForm(request.POST,request.FILES, instance=perfil)
        if form.is_valid():
            post = form.save(commit=False)
#            post.author = request.user
#            post.published_date = timezone.now()
            post.save()
            return redirect('pixkal2:dashboard')
    else:
        form = PerfilForm(instance=perfil)
        editar = 1
    return render(request, 'pixkal2/gestionarperfil.html', {'form': form, 'editar': editar })

def ActualizarPregunta(request,blugar):
    busquedalugar = get_object_or_404(BusquedaLugar, pk=blugar)
    if request.method == "POST":
        busquedalugar.bandera_pregunta = 1
        busquedalugar.pregunta = request.POST['pregunta']
        busquedalugar.respuesta = request.POST['respuesta']
        busquedalugar.save()
        return HttpResponseRedirect(reverse('pixkal2:editarbusqueda', args=(busquedalugar.busqueda.id,)))
    else:
        if busquedalugar.bandera_pregunta == 1:
            return render(request, 'pixkal2/gestionarpregunta.html',{'busquedalugar': busquedalugar, 'actualizar': 1 })
        else:
            return render(request, 'pixkal2/gestionarpregunta.html',{'actualizar':0})

def EliminarPregunta(request,blugar):
    busquedalugar = get_object_or_404(BusquedaLugar, pk=blugar)
    busquedalugar.bandera_pregunta = 0
    busquedalugar.save()
    return HttpResponseRedirect(reverse('pixkal2:editarbusqueda', args=(busquedalugar.busqueda.id,)))

def VerPregunta(request,blugar):
    busquedalugar = get_object_or_404(BusquedaLugar, pk=blugar)
    if request.method == "POST":
        if request.POST['respuesta'] == busquedalugar.respuesta:
            return HttpResponseRedirect(reverse('pixkal2:statustreasure', args=(busquedalugar.busqueda.id,busquedalugar.id)))
        else:
            return render(request, 'pixkal2/verpregunta.html',{'busquedalugar': busquedalugar,'error': 1})
    else:
        return render(request, 'pixkal2/verpregunta.html',{'busquedalugar': busquedalugar,'error': 0})

def AgregarSonido(request,blugar,tipo):
    recurso = ""
    if tipo=="busqueda":
        recurso = get_object_or_404(BusquedaLugar, pk=blugar)
    elif tipo=="clase":
        recurso = get_object_or_404(ClaseItem, pk=blugar)
    return render(request,'pixkal2/agregar_sonido.html', {'recurso': recurso, 'tipo' : tipo,})


def SubirSonido(request,blugar,tipo):
    if tipo=="busqueda":
        lugar = get_object_or_404(BusquedaLugar, pk=blugar)
        path = settings.BASE_DIR+"/media/sonidos/"+"s"+str(lugar.id)+".mp3"
        uploadedFile = open(path, "wb")
        uploadedFile.write(request.body)
        uploadedFile.close()
        lugar.sonido = "sonidos/s"+str(lugar.id)+".mp3"
        lugar.bandera_sonido = 1
        lugar.save()
    elif tipo=="clase":
        item = get_object_or_404(ClaseItem, pk=blugar)
        path = settings.BASE_DIR+"/media/sonidos/"+"c"+str(item.id)+".mp3"
        uploadedFile = open(path, "wb")
        uploadedFile.write(request.body)
        uploadedFile.close()
        item.sonido = "sonidos/c"+str(item.id)+".mp3"
        item.bandera_sonido = 1
        item.save()
    # put additional logic like creating a model instance or something like this here
    return HttpResponseRedirect(reverse('pixkal2:dashboard'))

def EliminarSonido(request,blugar,tipo):
    if tipo=="busqueda":
        busquedalugar = get_object_or_404(BusquedaLugar, pk=blugar)
        busquedalugar.bandera_sonido = 0
        busquedalugar.sonido = ""
        busquedalugar.save()
        return HttpResponseRedirect(reverse('pixkal2:editarbusqueda', args=(busquedalugar.busqueda.id,)))
    elif tipo=="clase":
        item = get_object_or_404(ClaseItem, pk=blugar)
        item.bandera_sonido = 0
        item.sonido = ""
        item.save()
        return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(item.clase.id,)))
    return HttpResponseRedirect(reverse('pixkal2:dashboard',))

def ModeloBAR(request,blugar,tipo):
    recurso = ""
    if tipo=="busqueda":
        recurso = get_object_or_404(BusquedaLugar, pk=blugar)
    elif tipo=="clase":
        recurso = get_object_or_404(ClaseItem, pk=blugar)
    return render(request, 'pixkal2/modelobar.html',{'recurso' : recurso})

def VerMisClases(request):
    idusuario = request.user
    misclases = Clase.objects.filter(usuario=request.user).order_by('-id')
    perfil = get_object_or_404(Perfil, usuario=request.user)
    # Paginador de mis clases

    mipage = request.GET.get('page', 1)

    mipaginator = Paginator(misclases, 6)
    try:
        lista_miclase = mipaginator.page(mipage)
    except PageNotAnInteger:
        lista_miclase = mipaginator.page(1)
    except EmptyPage:
        lista_miclase = mipaginator.page(mipaginator.num_pages)

    return render(request, 'pixkal2/misclases.html',{'misclases' : lista_miclase,'idusuario' : idusuario,'perfil' : perfil})

def EditarClase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == "POST":
        form = ClaseForm(request.POST, instance=clase)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            try:
                dash = Dash.objects.get(id_actividad=clase.id,servicio='C')
                dash.titulo = clase.titulo
                dash.descripcion = clase.descripcion
                dash.imagen = clase.imagen
                dash.save()
            except Dash.DoesNotExist:
                return redirect('pixkal2:misclases')

            return redirect('pixkal2:misclases')
    else:
        form = ClaseForm(instance=clase)
        claseitems = ClaseItem.objects.filter(clase=clase)
        editar = 1
        return render(request, 'pixkal2/registrarclase.html', {'form': form,'claseitems': claseitems,'clase' : clase, 'editar': editar })
    return redirect('pixkal2:misclases')

def RegistrarItemClase(request,clase_id):
    if request.method == "POST":
        formulario = ItemClaseForm(request.POST)
        if formulario.is_valid():
            itemclase = formulario.save(commit=False)
            clase = Clase.objects.get(pk=clase_id)
            itemclase.clase = clase
            avatar = get_object_or_404(Avatar, pk=1)
            itemclase.avatar = avatar
#            post.published_date = timezone.now()
            itemclase.save()
            clase.no_items = clase.no_items + 1
            clase.save()
            return HttpResponseRedirect(reverse('pixkal2:misclases',))
    else:
        form = ItemClaseForm()
        return render(request, 'pixkal2/registraritem.html', {'form': form, 'editar' : 0})

def ActualizarClaseItem(request, item_id):
    item = get_object_or_404(ClaseItem, pk=item_id)
    if request.method == "POST":
        form = ItemClaseForm(request.POST, instance=item)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect(reverse('pixkal2:misclases',))
    else:
        form = ItemClaseForm(instance=item)
        editar = 1
    return render(request, 'pixkal2/registraritem.html', {'form': form, 'editar': editar })

def ActivarClase(request,clase_id):
    clase = Clase.objects.get(id=clase_id)
    clase.estado = 'A'
    clase.save()

    try:
        dash = Dash.objects.get(id_actividad=clase_id,servicio='C')
        dash.titulo = clase.titulo
        dash.descripcion = ""
        dash.imagen = clase.imagen
        dash.descripcion = clase.descripcion
        dash.estado = 'A'
        dash.save()
    except Dash.DoesNotExist:
        dash = Dash()
        dash.servicio = 'C'
        dash.estado = 'A'
        dash.usuario = request.user
        dash.titulo = clase.titulo
        dash.descripcion = clase.descripcion
        dash.descripcion = ""
        dash.imagen = clase.imagen
        dash.url = 'clase/visualizar/' + str(clase.id) + '/0/'
        dash.id_actividad = clase.id
        dash.save()

    return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(clase.id,)))

def CancelarClase(request,clase_id):
    clase = Clase.objects.get(id=clase_id)
    clase.estado = 'C'
    clase.save()

    try:
        dash = Dash.objects.get(id_actividad=clase.id,servicio='C')
        dash.estado = 'I'
        dash.save()
    except Dash.DoesNotExist:
        return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(clase.id,)))

    return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(clase.id,)))

def ActualizarImagenClase(request,pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == "POST":
        form = ClaseImagenForm(request.POST, request.FILES, instance=clase)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            try:
                dash = Dash.objects.get(id_actividad=clase.id,servicio='C')
                dash.titulo = clase.titulo
                dash.descripcion = clase.descripcion
                dash.imagen = clase.imagen
                dash.save()
            except Dash.DoesNotExist:
                return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(clase.id,)))

        return HttpResponseRedirect(reverse('pixkal2:editarclase', args=(clase.id,)))
    return render(request, 'pixkal2/actualizarimagenclase.html')

def VisualizarClase(request,clase_id, orden):
    principal_clase = get_object_or_404(Clase, pk=clase_id)
    items = ClaseItem.objects.filter(clase=clase_id)
    item = items[int(orden)]
    orden = int(orden) + 1
    return render(request, 'pixkal2/visualizarclase.html', {'item': item,'orden': orden,'clase_id':clase_id,'clase':principal_clase })
