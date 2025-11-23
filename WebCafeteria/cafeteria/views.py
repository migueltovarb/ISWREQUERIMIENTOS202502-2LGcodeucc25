# cafeteria/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from .models import Producto, Pedido, DetallePedido, Pago
from .forms import PedidoForm, SeleccionMetodoPagoForm, ReferenciaPagoForm, AddToCartForm
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('root')

@login_required
def index(request):
    return render(request, "cafeteria/index.html")

def root_redirect(request):
    """Ruta raíz: si está autenticado lleva al menú, si no al login con next hacia menú."""
    if request.user.is_authenticated:
        return redirect('menu')
    return redirect('/accounts/login/?next=/cafeteria/menu/')

# ----------------------------------------------------------
# HU-031 — Visualizar menú digital
# ----------------------------------------------------------
@login_required
def menu(request):
    """
    HU-031: Visualizar menú digital.
    Muestra al cliente los productos disponibles con stock.
    """
    productos = Producto.objects.filter(activo=True, stock__gt=0).select_related("categoria")

    return render(request, "cafeteria/menu.html", {
        "productos": productos,
    })


# ----------------------------------------------------------
# HU-026 — Crear pedido vía autoservicio web
# ----------------------------------------------------------
@login_required
def crear_pedido_autoservicio(request):
    """Vista de carrito: permite agregar múltiples productos antes de crear el pedido."""
    # Carrito en sesión: {producto_id: cantidad}
    cart = request.session.get('cart', {})
    productos = Producto.objects.filter(activo=True, stock__gt=0).select_related('categoria')

    # Manejo de acciones
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = AddToCartForm(request.POST)
            if form.is_valid():
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                prev = cart.get(str(producto.id), 0)
                nueva = min(prev + cantidad, producto.stock)  # limitar por stock
                cart[str(producto.id)] = nueva
                request.session['cart'] = cart
                return redirect('crear_pedido_autoservicio')
        elif action == 'update':
            pid = request.POST.get('producto_id')
            cantidad = int(request.POST.get('cantidad', 1))
            if pid in cart:
                try:
                    prod = Producto.objects.get(id=pid)
                    cart[pid] = max(1, min(cantidad, prod.stock))
                except Producto.DoesNotExist:
                    cart.pop(pid, None)
                request.session['cart'] = cart
            return redirect('crear_pedido_autoservicio')
        elif action == 'remove':
            pid = request.POST.get('producto_id')
            if pid in cart:
                cart.pop(pid)
                request.session['cart'] = cart
            return redirect('crear_pedido_autoservicio')
        elif action == 'finalizar':
            if not cart:
                return redirect('crear_pedido_autoservicio')
            pedido = Pedido.objects.create(cliente=request.user, fecha=timezone.now())
            for pid, cantidad in cart.items():
                try:
                    producto = Producto.objects.get(id=pid)
                except Producto.DoesNotExist:
                    continue
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
            pedido.calcular_total()
            # Limpiar carrito
            request.session['cart'] = {}
            return redirect('seleccionar_metodo_pago', pedido_id=pedido.id)

    # Construir resumen carrito
    cart_items = []
    subtotal = 0
    if cart:
        ids = [int(pid) for pid in cart.keys()]
        map_prod = {p.id: p for p in Producto.objects.filter(id__in=ids)}
        for pid, qty in cart.items():
            pid_int = int(pid)
            prod = map_prod.get(pid_int)
            if not prod:
                continue
            line_total = prod.precio * qty
            subtotal += line_total
            cart_items.append({
                'id': pid_int,
                'nombre': prod.nombre,
                'precio': prod.precio,
                'cantidad': qty,
                'line_total': line_total,
            })

    return render(request, 'cafeteria/crear_pedido.html', {
        'productos': productos,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'cart_empty': len(cart_items) == 0,
        'AddToCartForm': AddToCartForm,
    })


# ----------------------------------------------------------
# HU-028 — Realizar pago digital
# ----------------------------------------------------------
@login_required
def seleccionar_metodo_pago(request, pedido_id):
    """Paso 1: seleccionar método antes de ingresar referencia."""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if request.method == "POST":
        form = SeleccionMetodoPagoForm(request.POST)
        if form.is_valid():
            metodo = form.cleaned_data["metodo"]
            pago, _ = Pago.objects.get_or_create(pedido=pedido)
            pago.metodo = metodo
            pago.pagado = False
            pago.save()
            return redirect("pagar_pedido", pedido_id=pedido.id)
    else:
        form = SeleccionMetodoPagoForm()
    return render(request, "cafeteria/metodo_pago.html", {"pedido": pedido, "form": form})


def pagar_pedido(request, pedido_id):
    """Paso 2: ingresar referencia y confirmar pago (HU-028)."""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    pago = getattr(pedido, "pago", None)
    if pago is None or not pago.metodo:
        return redirect("seleccionar_metodo_pago", pedido_id=pedido.id)

    if request.method == "POST":
        form = ReferenciaPagoForm(request.POST)
        if form.is_valid():
            referencia = form.cleaned_data["referencia"]
            pago.referencia = referencia
            pago.confirmar()
            return redirect("confirmacion_pago", pedido_id=pedido.id)
    else:
        form = ReferenciaPagoForm()

    return render(request, "cafeteria/pago.html", {"pedido": pedido, "pago": pago, "form": form})


# ----------------------------------------------------------
# HU-029 — Confirmación automática de pago
# ----------------------------------------------------------
@login_required
def confirmacion_pago(request, pedido_id):
    """
    HU-029: Confirmación automática de pago.
    Muestra mensaje de éxito + resumen del pedido y pago.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    pago = getattr(pedido, "pago", None)

    return render(request, "cafeteria/confirmacion_pago.html", {
        "pedido": pedido,
        "pago": pago,
    })


# ----------------------------------------------------------
# HU-030 — Consultar estado del pedido
# ----------------------------------------------------------
@login_required
def estado_pedidos(request):
    """
    HU-030: Consultar estado del pedido.
    Lista el historial de pedidos del cliente, con su estado actual.
    """
    pedidos = Pedido.objects.filter(cliente=request.user).exclude(estado='cancelado').order_by("-fecha")

    return render(request, "cafeteria/estado_pedidos.html", {
        "pedidos": pedidos,
    })

@login_required
def cancelar_pedido(request, pedido_id):
    """Marca pedido como cancelado si sigue pendiente."""
    if request.method != 'POST':
        return redirect('estado_pedidos')
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if pedido.estado != 'pendiente':
        messages.warning(request, f"El pedido #{pedido.id} ya no se puede cancelar.")
        return redirect('estado_pedidos')
    pedido.estado = 'cancelado'
    pedido.save()
    messages.success(request, f"Pedido #{pedido.id} marcado como cancelado.")
    return redirect('estado_pedidos')
