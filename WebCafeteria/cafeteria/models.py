from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# -----------------------------
#  PRODUCTOS Y CATEGORÍAS
# -----------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


# -----------------------------
#  PROMOCIONES
# -----------------------------
class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monto_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje_descuento}%)"

    def esta_vigente(self):
        hoy = timezone.now().date()
        if self.fecha_inicio and self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        return True


# -----------------------------
#  PEDIDOS
# -----------------------------
class Pedido(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promocion_aplicada = models.ForeignKey(Promocion, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

    def aplicar_promocion(self):
        """Lógica básica para aplicar una promoción automática."""
        promos = Promocion.objects.filter(activa=True)
        for promo in promos:
            if promo.esta_vigente():
                if promo.monto_minimo is None or self.total >= promo.monto_minimo:
                    descuento = (promo.porcentaje_descuento / 100) * self.total
                    self.total = self.total - descuento
                    self.promocion_aplicada = promo
                    self.save()
                    break

    def calcular_total(self):
        total = sum([item.subtotal() for item in self.detallepedido_set.all()])
        self.total = total
        self.aplicar_promocion()
        self.save()


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# -----------------------------
#  PAGOS
# -----------------------------
class Pago(models.Model):

    METODOS = [
        ('tarjeta', 'Tarjeta'),
        ('qr', 'Código QR'),
        ('transferencia', 'Transferencia'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=20, choices=METODOS)
    referencia = models.CharField(max_length=100, null=True, blank=True)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pago de Pedido #{self.pedido.id}"

    def confirmar(self):
        self.pagado = True
        self.fecha_pago = timezone.now()
        self.save()
        # Al confirmar pago, el pedido pasa a pendiente de preparación
        self.pedido.estado = 'pendiente'
        self.pedido.save()


# -----------------------------
#  SEGUIMIENTO DEL CLIENTE
# -----------------------------
class EstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pedido.id} - {self.estado}"
