from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
""" Vistas para el catalogo de productos"""
from .models import Categoria, Producto, Cliente, Pedido, PedidoDetalle


from paypal.standard.forms import PayPalPaymentsForm
# Create your views here.


def index(request):
    listaProductos = Producto.objects.all()
    listaCategorias = Categoria.objects.all()
    contex = {
        'productos':listaProductos,
        'categorias':listaCategorias
    }
    return render(request, 'index.html', contex)




def productosPorCategoria(request,categoria_id):
    '''Vista para filtrar por categoria'''
    objCategoria = Categoria.objects.get(pk=categoria_id)
    listaProductos = objCategoria.producto_set.all()
    
    ListaCategorias = Categoria.objects.all()
    
    context = {
        'categorias':ListaCategorias,
        'productos':listaProductos
    }
    return render(request, 'index.html',context)


def productosPorNombre(request):
    """ Vista para filtrado de productos """
    nombre = request.POST['nombre']
    
    listaProductos = Producto.objects.filter(nombre__contains=nombre.upper())
    listaCategorias = Categoria.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos
    }

    return render(request, 'index.html',context)

def productoDetalle(request,producto_id):
    """Vita para el datelle del producto """

    #objProducto = Producto.objects.get(pk=producto_id)
    objProducto = get_object_or_404(Producto,pk=producto_id)
    context={
        'producto':objProducto
    }

    return render(request, 'producto.html',context)

"""Vistas para el carrito de compras"""

from .carrito import Cart


def carrito(request):
    return render(request,'carrito.html')


def agregarCarrito(request,producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST["cantidad"])
    else:
        cantidad = 1 

    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.add(objProducto,cantidad)

    #print(request.session.get("cart"))
    if request.method == 'GET':
        return redirect('/')



    return render(request,'carrito.html')



def eliminarProductoCarrito(request,producto_id):
    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.delete(objProducto)

    return render(request,'carrito.html')


def limpiarCarrito(request):
    carritoProducto = Cart(request)
    carritoProducto.clear()

    return render(request,'carrito.html')

# Vistas para clientes y usuarios
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .forms import ClienteForm

def crearUsuario(request):
    if request.method == 'POST':
        dataUsuario = request.POST['nuevoUsuario']
        dataPassword = request.POST["nuevoPassword"]

        nuevoUsuario = User.objects.create_user(username=dataUsuario,password=dataPassword)
        if nuevoUsuario is not None:
            login(request,nuevoUsuario)
            return redirect('/cuenta')
        


    return render(request,'login.html')

def loginUsuario(request):
    paginaDestino = request.GET.get('next',None)
    context = {
        'destino':paginaDestino
    }


    if request.method == 'POST':
        dataUsuario = request.POST['usuario']
        dataPassword = request.POST['password']
        dataDestino = request.POST['destino']

        usuarioAuth = authenticate(request,username=dataUsuario,password=dataPassword)
        if usuarioAuth is not None:
            login(request,usuarioAuth)
            if dataDestino:  # esto maneja tanto 'None' como cadenas vacías
                return redirect(dataDestino)
            else:
                return redirect('/cuenta')

        
        else:
            context = {
                'mensajeError':'Datos incorrectos'
            }

    return render(request,'login.html',context)


def logoutUsuario(request):
    logout(request)
    return render(request,'login.html')



def cuentaUsuario(request):
    try:
        clienteEditar = Cliente.objects.get(usuario = request.user)

        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
            'direccion':clienteEditar.direccion,
            'telefono':clienteEditar.telefono,
            'sexo':clienteEditar.sexo,
            'fecha_nacimiento':clienteEditar.fecha_nacimiento

        }
    except:
        dataCliente = {
        'nombre':request.user.first_name,
        'apellidos':request.user.last_name,
        'email':request.user.email
    }

    frmCliente = ClienteForm(dataCliente)
    contex = {
        'frmCliente':frmCliente
    }
    
    return render(request,'cuenta.html',contex)


def actualizarCliente(request):
    mensaje=""
    if request.method == "POST":
        frmCliente = ClienteForm(request.POST)
        if frmCliente.is_valid():
            dataCliente = frmCliente.cleaned_data
            
            #actualizar usuario
            actUsuario = User.objects.get(pk=request.user.id)
            actUsuario.first_name = dataCliente["nombre"]
            actUsuario.last_name = dataCliente["apellidos"]
            actUsuario.email = dataCliente["email"]
            actUsuario.save()

            #registrar al clinete
            nuevoCliente = Cliente()
            nuevoCliente.usuario = actUsuario
            nuevoCliente.direccion = dataCliente["direccion"]
            nuevoCliente.telefono = dataCliente["telefono"]
            nuevoCliente.sexo = dataCliente["sexo"]
            nuevoCliente.fecha_nacimiento = dataCliente["fecha_nacimiento"]
            nuevoCliente.save()

            mensaje="Datos Actualizados"
    context = {
        'mensaje':mensaje,
        'frmCliente':frmCliente
    }


    return render(request,'cuenta.html', context)


"""vistas para proceso de compra"""
@login_required(login_url='/login')
def registrarPedido(request):
    try:
        clienteEditar = Cliente.objects.get(usuario = request.user)

        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
            'direccion':clienteEditar.direccion,
            'telefono':clienteEditar.telefono,
            'sexo':clienteEditar.sexo,
            'fecha_nacimiento':clienteEditar.fecha_nacimiento

        }
    except:
        dataCliente = {
        'nombre':request.user.first_name,
        'apellidos':request.user.last_name,
        'email':request.user.email
    }

    frmCliente = ClienteForm()
    context = {
        'frmCliente':frmCliente
    }

    return render(request,'pedido.html',context)
# Prueba de paypal
from paypal.standard.forms import PayPalPaymentsForm


@login_required(login_url='/login')
def confirmarPedido(request):
    context = {}
    if request.method == 'POST':
        #Actulizar usuario
        actUsuario = User.objects.get(pk=request.user.id)
        actUsuario.first_name = request.POST['nombre']
        actUsuario.last_name = request.POST['apellidos']
        actUsuario.save()
        #registramos o actulizamos cliente
        try:
            clientePedido = Cliente.objects.get(usuario=request.user)
            clientePedido.telefono = request.POST['telefono']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.save()
        except:
            clientePedido = Cliente()
            clientePedido.usuario = actUsuario
            clientePedido.direccion = request.POST['direccion']
            clientePedido.telefono = request.POST['telefono']
            clientePedido.save()
        #REGISTRAMOS NUEVO PEDIDO
        nroPedido = ''
        montoTotal = float(request.session.get('cartMontoTotal'))
        nuevoPedido = Pedido()
        nuevoPedido.cliente = clientePedido
        nuevoPedido.save()

        #registramos el detalle del pedido
        carritoPedido = request.session.get('cart')
        for key,value in carritoPedido.items():
            productoPedido = Producto.objects.get(pk=value['producto_id'])
            detalle = PedidoDetalle()
            detalle.pedido = nuevoPedido
            detalle.Producto = productoPedido
            detalle.cantidad = int(value['cantidad'])
            detalle.subtotal = float(value['subtotal'])
            detalle.save()

        #actualizar pedido
        nroPedido = 'PED' + nuevoPedido.fecha_registro.strftime('%Y') + str(nuevoPedido.id)
        nuevoPedido.nro_pedido = nroPedido
        nuevoPedido.monto_total = montoTotal
        nuevoPedido.save()

        #registar pedido de session para el pedido
        request.session['pedidoId'] = nuevoPedido.id

        #creamosun boton de paypal
        paypal_dict = {
        "business": "sb-l2kvw32683138@business.example.com",
        "amount": montoTotal,
        "item_name": "PEDIDO CODIGO : "+ nroPedido,
        "invoice": nroPedido,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri('/gracias'),
        "cancel_return": request.build_absolute_uri('/'),
        }

    # Create the instance.
    formPaypal = PayPalPaymentsForm(initial=paypal_dict)
        
         
    context = {
        'pedido': nuevoPedido,
        'formPaypal': formPaypal

    }
    #limpiamos carrito de compraas
    carrito = Cart(request)
    carrito.clear()


    return render(request,'compra.html', context)


login_required(login_url='/login')
def gracias(request):
    paypalId = request.GET.get('PayerID',None)
    context = {}
    if paypalId is not None:
        pedidoId = request.session.get('pedidoId')
        pedido = Pedido.objects.get(pk=pedidoId)
        pedido.estado = '1'
        pedido.save()
        
        context = {
            'pedido':pedido
        }
    else:
        return redirect('/')
        
    return render(request,'gracias.html',context)
