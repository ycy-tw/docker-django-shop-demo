from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from .models import OrderItem
from .forms import OrderCreateForm
from .tasks import order_created


@login_required
def order_create(request):

    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()
            order_created.delay(order.id)
            context = {'order': order}
            return render(request,
                          'order/created.html',
                          context)
    else:
        form = OrderCreateForm(instance=request.user)

    context = {
        'cart': cart,
        'form': form
    }
    return render(request, 'order/create.html', context)
