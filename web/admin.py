from django.contrib import admin

# Register your models here.
from .models import Categoria,Producto

admin.site.register(Categoria)
#admin.site.register(Producto)

@admin.register(Producto)
class Productoadmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'Categoria' )
    list_editable = ('precio', ) # para el panel de adminsitracion poder cambiar el precio de manera muy facil