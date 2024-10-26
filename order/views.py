from django.db.models import Sum, Count, F
from django.db.models.functions import Round
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView
from order.forms import CartItemForm
from order.models import Cart, CartItems
from store.models import Category


class CartView(ListView):
    model = CartItems
    template_name = "cart/cart.html"
    context_object_name = "cartitems"

    # when search is triggered it will be redirected
    # to the shop and filter the products accordingly
    def get(self, *args, **kwargs):
        if self.request.GET.get('q'):
            return redirect(f'/store/category/?q={self.request.GET.get('q')}')
        return super().get(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            total_price=Round(
                F("product_quantity")*F("product__product_price")
            )
        )
        return queryset.select_related("product")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # for displaying cart count
        cart = (
            Cart.objects.filter(
                user__id=self.request.user.id
            ).select_related("user")
        )
        cart_count = cart.aggregate(count=Count("cartitems"))

        try:
            subtotal = self.get_queryset().aggregate(
                total=Sum("total_price")
            ).get("total")
            total = subtotal + cart.first().flat_rate
        # if all products have been deleted
        except TypeError:
            subtotal = 0
            total = 0

        # Displaying root categories in the dropdown meny
        categories = Category.objects.filter(parent__isnull=True)

        context["cart_count"] = cart_count.get("count")
        context["total"] = total
        context["subtotal"] = subtotal
        context["flat_rate"] = cart.first().flat_rate
        context["categories_root"] = categories
        return context


class CheckoutView(ListView):
    model = CartItems
    template_name = "checkout/chackout.html"
    context_object_name = "cartitems"

    # when search is triggered it will be redirected
    # to the shop and filter the products accordingly
    def get(self, *args, **kwargs):
        if self.request.GET.get('q'):
            return redirect(f'/store/category/?q={self.request.GET.get('q')}')
        return super().get(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            total_price=Round(
                F("product_quantity")*F("product__product_price")
            )
        )
        return queryset.select_related("product")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Displaying cart items count
        cart = Cart.objects.filter(user_id=self.request.user.id)
        cart_count = cart.aggregate(count=Count("cartitems"))

        # Displaying root categories in the dropdown meny
        categories = Category.objects.filter(parent__isnull=True)

        try:
            # for displaying total
            subtotal = self.get_queryset().aggregate(
                total=Sum("total_price")
            ).get("total")
            total = subtotal + cart.first().flat_rate
        except TypeError:
            # if all products have been deleted
            subtotal = 0
            total = 0

        context["cart_count"] = cart_count.get("count")
        context["total"] = total
        context["subtotal"] = subtotal
        context["flat_rate"] = cart.first().flat_rate
        context["categories_root"] = categories
        return context


class AddToCartView(CreateView):
    model = CartItems
    form_class = CartItemForm

    def get_success_url(self):
        # gets the url where the request happened
        return self.request.META.get('HTTP_REFERER', '')

    def form_valid(self, form):
        new_item = form.save(commit=False)
        new_item.cart_id = self.request.user.id
        new_item.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # prints the validation errors
        print(form.errors.as_json())
        return redirect(self.request.META.get('HTTP_REFERER', ''))


class AddToCartDeleteView(DeleteView):
    # for deleting the cart items
    model = CartItems
    success_url = reverse_lazy("order:cart")
