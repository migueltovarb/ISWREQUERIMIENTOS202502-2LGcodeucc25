# cafeteria/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # Página de inicio
    path("", views.index, name="index"),

    # HU-031 Menú digital
    path("menu/", views.menu, name="menu"),

    # HU-026 Crear pedido
    path("pedido/nuevo/", views.crear_pedido_autoservicio, name="crear_pedido_autoservicio"),

    # Paso intermedio selección de método de pago
    path("pedido/<int:pedido_id>/metodo/", views.seleccionar_metodo_pago, name="seleccionar_metodo_pago"),

    # HU-028 Pagar pedido
    path("pedido/<int:pedido_id>/pago/", views.pagar_pedido, name="pagar_pedido"),

    # HU-029 Confirmación de pago
    path("pedido/<int:pedido_id>/confirmacion/", views.confirmacion_pago, name="confirmacion_pago"),

    # HU-030 Estado del pedido
    path("mis-pedidos/", views.estado_pedidos, name="estado_pedidos"),
    # Cancelar pedido
    path("pedido/<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar_pedido"),
]
