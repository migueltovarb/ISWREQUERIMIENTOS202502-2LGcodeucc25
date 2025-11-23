from django.contrib import admin
from .models import (
    Categoria,
    Producto,
    Promocion,
    Pedido,
    DetallePedido,
    Pago,
    EstadoPedido
)

# --------------------------
# Inline: Detalle del Pedido
# --------------------------
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


# --------------------------
# Admin Pedido
# --------------------------
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "estado", "total", "fecha")
    list_filter = ("estado", "fecha")
    search_fields = ("cliente__username", "id")
    inlines = [DetallePedidoInline]


# --------------------------
# Admin Producto
# --------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre",)


# --------------------------
# Admin Categoría
# --------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


# --------------------------
# Admin Promoción
# --------------------------
@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "porcentaje_descuento", "monto_minimo", "activa", "fecha_inicio", "fecha_fin")
    list_filter = ("activa", "fecha_inicio", "fecha_fin")
    search_fields = ("nombre",)


# --------------------------
# Admin Pago
# --------------------------
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "metodo", "pagado", "fecha_pago")
    list_filter = ("metodo", "pagado")
    search_fields = ("pedido__id",)


# --------------------------
# Admin EstadoPedido
# --------------------------
@admin.register(EstadoPedido)
class EstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "estado", "fecha")
    list_filter = ("estado",)
    search_fields = ("pedido__id",)
