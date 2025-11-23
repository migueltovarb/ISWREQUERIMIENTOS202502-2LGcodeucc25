# cafeteria/management/commands/seed.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cafeteria.models import Categoria, Producto, Promocion

class Command(BaseCommand):
    help = "Carga datos iniciales de la cafetería"

    def handle(self, *args, **kwargs):
        print("⬇️ Creando datos iniciales...")

        # ---------------------------
        # 1. Usuarios del sistema
        # ---------------------------
        if not User.objects.filter(username="cliente1").exists():
            User.objects.create_user(
                username="cliente1",
                password="1234"
            )
            print("✔ Usuario cliente1 creado")

        if not User.objects.filter(username="barista1").exists():
            User.objects.create_user(
                username="barista1",
                password="1234"
            )
            print("✔ Usuario barista1 creado")

        if not User.objects.filter(username="cajero1").exists():
            User.objects.create_user(
                username="cajero1",
                password="1234"
            )
            print("✔ Usuario cajero1 creado")

        # ---------------------------
        # 2. Categorías
        # ---------------------------
        categorias = [
            "Cafés",
            "Bebidas frías",
            "Snacks",
            "Postres",
        ]

        categoria_objs = []

        for nombre in categorias:
            obj, created = Categoria.objects.get_or_create(nombre=nombre)
            categoria_objs.append(obj)
            if created:
                print(f"✔ Categoría creada: {nombre}")

        # ---------------------------
        # 3. Productos
        # ---------------------------
        productos = [
            ("Americano", "Cafés", 5000, 20),
            ("Latte", "Cafés", 6000, 15),
            ("Capuccino", "Cafés", 6500, 18),
            ("Té Helado", "Bebidas frías", 4500, 25),
            ("Brownie", "Postres", 5500, 12),
            ("Croissant", "Snacks", 4000, 15),
        ]

        for nombre, cat, precio, stock in productos:
            categoria = Categoria.objects.get(nombre=cat)
            obj, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": categoria,
                    "precio": precio,
                    "stock": stock,
                    "activo": True,
                }
            )
            if created:
                print(f"✔ Producto creado: {nombre}")

        # ---------------------------
        # 4. Promoción activa
        # ---------------------------
        promo, created = Promocion.objects.get_or_create(
            nombre="Descuento estudiantes",
            defaults={
                "descripcion": "10% después de 3 compras",
                "porcentaje_descuento": 10,
                "monto_minimo": 10000,
                "activa": True,
            }
        )

        if created:
            print("✔ Promoción creada: Descuento estudiantes")

        print("\n🎉 Datos iniciales cargados correctamente.")
