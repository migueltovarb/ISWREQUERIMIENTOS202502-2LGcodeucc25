# cafeteria/forms.py
from django import forms
from .models import Producto, Pago


class PedidoForm(forms.Form):
    """
    Formulario sencillo para que el cliente seleccione un producto y cantidad.
    Para el MVP, el pedido tendrá un solo producto. Más adelante se puede
    extender a varios productos con formsets o carrito.
    """
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True, stock__gt=0),
        label="Producto"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad"
    )


class SeleccionMetodoPagoForm(forms.Form):
    """Primer paso: seleccionar método de pago."""
    metodo = forms.ChoiceField(choices=Pago.METODOS, label="Método de pago")


class ReferenciaPagoForm(forms.Form):
    """Segundo paso: ingresar referencia y confirmar pago."""
    referencia = forms.CharField(max_length=100, required=False, label="Referencia o comprobante")


class AddToCartForm(forms.Form):
    """Formulario para agregar productos al carrito (sesión)."""
    producto_id = forms.IntegerField(widget=forms.HiddenInput())
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad")

    def clean(self):
        cleaned = super().clean()
        pid = cleaned.get('producto_id')
        cantidad = cleaned.get('cantidad')
        try:
            producto = Producto.objects.get(id=pid, activo=True, stock__gt=0)
        except Producto.DoesNotExist:
            raise forms.ValidationError("Producto no válido o sin stock.")
        if cantidad and cantidad > producto.stock:
            raise forms.ValidationError(f"Stock insuficiente. Disponible: {producto.stock}.")
        cleaned['producto'] = producto
        return cleaned
