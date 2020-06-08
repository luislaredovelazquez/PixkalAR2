from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, authenticate
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Choice, Question, Busqueda, BusquedaLugar, BusquedaParticipante, ItemEncontrado, Avatar, Clase, Perfil
from .forms import BusquedaForm, BusquedaLugarForm, SignUpForm, ClaseForm, PerfilForm, BusquedaImagenForm

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

    return render(request, 'pixkal2/activatetreasure.html', {'busqueda': busqueda, 'busqueda_id' : busqueda_id})

def CancelarBusqueda(request,busqueda_id):
    busqueda = Busqueda.objects.get(id=busqueda_id)
    busqueda.estado = 'C'
    busqueda.save()
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
#            post.published_date = timezone.now()
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
#            post.author = request.user
#            post.published_date = timezone.now()
            post.save()
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
    busquedas = Busqueda.objects.filter(estado='A').exclude(creador=request.user).order_by('-id')
    busquedasparticipo = BusquedaParticipante.objects.filter(usuario=request.user).filter(estado='T')
    for busquedaparticipo in busquedasparticipo:
        for busqueda in busquedas:
            if busqueda.id == busquedaparticipo.busqueda.id:
                busquedas = busquedas.exclude(id = busqueda.id)

# Paginador de búsqueda

    page = request.GET.get('page', 1)

    paginator = Paginator(busquedas, 6)
    try:
        lista_busqueda = paginator.page(page)
    except PageNotAnInteger:
        lista_busqueda = paginator.page(1)
    except EmptyPage:
        lista_busqueda = paginator.page(paginator.num_pages)

    return render(request, 'pixkal2/dashboard.html',{'busquedas' : lista_busqueda,'idusuario' : idusuario})

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
        formulario = ClaseForm(request.POST, request.FILES)
        if formulario.is_valid():
            clase = formulario.save(commit=False)
            clase.usuario = request.user
            perfil = get_object_or_404(Perfil, usuario=request.user)
            clase.perfil = perfil
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
#            post.author = request.user
#            post.published_date = timezone.now()
            post.save()
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
