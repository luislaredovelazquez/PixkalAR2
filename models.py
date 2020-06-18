import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

def upload_location(instance, filename):
    filebase, extension = filename.split('.')
    return 'images/%s.%s' % (instance.usuario.id, extension)

def upload_location_busqueda(instance, filename):
    filebase, extension = filename.split('.')
    return 'images/b%s.%s' % (instance.id, extension)

def upload_location_clase(instance, filename):
    filebase, extension = filename.split('.')
    return 'images/c%s.%s' % (instance.id, extension)

def upload_location_treasure_s(instance, filename):
    filebase, extension = filename.split('.')
    return 'sonidos/s%s.%s' % (instance.id, extension)

def upload_location_c(instance, filename):
    filebase, extension = filename.split('.')
    return 'sonidos/c%s.%s' % (instance.id, extension)

def validate_image(image):
    file_size = image.file.size
    limit_kb = 1500
    if file_size > limit_kb * 1024:
        raise ValidationError("Tamaño máximo del archivo %s KB" % limit_kb)

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class Avatar(models.Model):
    tipo = models.CharField(max_length=200, default='GPS')
    titulo = models.CharField(max_length=100, default="Avatar")
    model_3DName = models.CharField(max_length=200)
    model_Image = models.CharField(max_length=200)
    def __str__(self):
        return self.model_3DName

class Perfil(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    imagen_busqueda = models.ImageField(upload_to=upload_location, validators=[validate_image])

class Busqueda(models.Model):
    OPCIONES_ESTADO = (
        ('I', 'Inactivo'),
        ('C', 'Cancelado'),
        ('A', 'Activo'),
        ('T', 'Terminado'),
    )

#    OPCIONES_DURACION = (
#        ('0', 'Sin limite de tiempo'),
#        ('10', '10 min.'),
#        ('20', '20 min.'),
#        ('30', '30 min.'),
#        ('60', '60 min.'),
#        ('120', '120 min.'),
#        ('180', '180 min.'),
#    )

    titulo_busqueda = models.CharField(max_length=350)
    recompensa = models.CharField(max_length=200)
    creacion = models.DateTimeField(auto_now=True)
    ultima_modificacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(max_length=350, default="")
    numero_personas = models.PositiveSmallIntegerField()
    estado = models.CharField(max_length=1, choices=OPCIONES_ESTADO)
#    duracion = models.CharField(max_length=3, choices=OPCIONES_DURACION, default=0)
#    inicio = models.DateField()
#    fin = models.DateField()
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    no_items = models.PositiveSmallIntegerField(default=0)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, default=1)
    imagen = models.ImageField(upload_to=upload_location_busqueda, default="", validators=[validate_image])
    def __str__(self):
        return self.titulo_busqueda

class BusquedaLugar(models.Model):
    busqueda = models.ForeignKey(Busqueda, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    pregunta = models.TextField(max_length=350, default="")
    respuesta = models.CharField(max_length=20, default="")
    bandera_pregunta = models.SmallIntegerField(default=0)
    sonido = models.FileField(upload_to=upload_location_treasure_s, default="", validators=[validate_image])
    bandera_sonido = models.SmallIntegerField(default=0)
    creacion = models.DateTimeField(auto_now=True)
    ultima_modificacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.busqueda.titulo_busqueda

class BusquedaParticipante(models.Model):
    OPCIONES_ESTADO = (
        ('P', 'Pendiente'),
        ('A', 'Activo'),
        ('G', 'Ganador'),
        ('T', 'Terminado'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    busqueda = models.ForeignKey(Busqueda, on_delete=models.CASCADE)
    items_encontrados = models.SmallIntegerField()
    estado = models.CharField(max_length=1, choices=OPCIONES_ESTADO)
    creacion = models.DateTimeField(auto_now=True)
    ultima_modificacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.busqueda.titulo_busqueda

class ItemEncontrado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    busqueda = models.ForeignKey(Busqueda, on_delete=models.CASCADE)
    lugar = models.ForeignKey(BusquedaLugar, on_delete=models.CASCADE)
    creacion = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.busqueda.titulo_busqueda

class Clase(models.Model):
    OPCIONES_ESTADO = (
        ('I', 'Inactivo'),
        ('C', 'Cancelado'),
        ('A', 'Activo'),
        ('T', 'Terminado'),
    )

    OPCIONES_MARCADOR = (
        ('M', 'Utilizar marcador'),
        ('S', 'Sin marcador'),
    )

    titulo = models.CharField(max_length=350)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    creacion = models.DateTimeField(auto_now=True)
    descripcion = models.TextField(max_length=350, default="")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, default=1)
    imagen = models.ImageField(upload_to=upload_location_clase, default="", validators=[validate_image])
    no_items = models.PositiveSmallIntegerField(default=0)
    bandera_marcador = models.CharField(max_length=1, choices=OPCIONES_MARCADOR, default="M")
    estado = models.CharField(max_length=1, choices=OPCIONES_ESTADO,default="I")
    def __str__(self):
        return self.titulo

class ClaseItem(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    sonido = models.FileField(upload_to=upload_location_c, default="", validators=[validate_image])
    bandera_sonido = models.SmallIntegerField(default=0)
    creacion = models.DateTimeField(auto_now=True)
    ultima_modificacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.clase.titulo

class Dash(models.Model):
    OPCIONES_SERVICIO = (
        ('B', 'Búsqueda'),
        ('C', 'Clase'),
        ('S', 'Stream'),
    )

    OPCIONES_ESTADO = (
        ('I', 'Inactivo'),
        ('C', 'Cancelado'),
        ('A', 'Activo'),
        ('T', 'Terminado'),
    )

    servicio = models.CharField(max_length=1, choices=OPCIONES_SERVICIO, default="M")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=350)
    descripcion = models.TextField(max_length=350, default="")
    imagen = models.CharField(max_length=350)
    url = models.CharField(max_length=350)
    id_actividad = models.IntegerField(default=0)
    estado = models.CharField(max_length=1, choices=OPCIONES_ESTADO, default='A')
    def __str__(self):
        return self.titulo