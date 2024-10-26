from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView
from store.models import Product, ProductReviews
from store.models import Category, ShopReviews, ProductTags
from order.models import Cart


class IndexView(ListView):
    model = ShopReviews
    # Displays the Company reviews in a list at the bottom of the homepage
    template_name = "homepage/index.html"
    queryset = ShopReviews.objects.select_related("user")
    context_object_name = "reviews"

    # when search is triggered it will be redirected
    # to the shop and filter the products accordingly
    def get(self, *args, **kwargs):
        if self.request.GET.get('q'):
            return redirect(f'/store/category/?q={self.request.GET.get('q')}')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # for displaying the dropdown menu with only root categories
        categories = Category.objects.filter(parent__isnull=True)
        # for displaying cart item count
        cart = Cart.objects.filter(user_id=self.request.user.id)
        cart_count = cart.aggregate(count=Count("cartitems"))
        context["cart_count"] = cart_count.get("count")
        context["categories_root"] = categories
        return context


class CategoryListingsView(ListView):
    model = Product
    template_name = "shop/shop.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search-q filters by the name
        if self.request.GET.get('q'):
            queryset = queryset.filter(
                product_name__icontains=self.request.GET.get('q')
            ).prefetch_related("tags")

        # Filter - p(price) filters by the price and t(tags) by tags
        if self.request.GET.get('t') or self.request.GET.get('p'):
            tags = None
            if self.request.GET.get('t'):
                tags = str(self.request.GET.get('t'))

            # price by default is 50
            queryset = queryset.filter(
                product_price__lte=float(self.request.GET.get('p'))
            ).prefetch_related("tags")

            if tags:
                # If the tags is selected
                queryset = queryset.filter(tags=tags).prefetch_related("tags")

        # Sort-fruitlist orders by price if price is
        # selected(value is 2) or does not sort.
        if self.request.GET.get('fruitlist'):
            if self.request.GET.get('fruitlist') == "2":
                queryset = queryset.order_by("product_price")

        # for individual category get the slug
        category_slug = self.kwargs.get("slug")
        if category_slug:
            # Filter the products by the individual category
            # and its descendants.
            category = Category.objects.filter(slug=category_slug)
            categories = category.get_descendants(include_self=True)
            queryset = (
                queryset
                .filter(product_category__in=categories)
                .prefetch_related("tags")
            )
        return queryset.prefetch_related("product_category", "tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(parent__isnull=True)
        # for displaying cart item count
        cart = Cart.objects.filter(user_id=self.request.user.id)
        cart_count = cart.aggregate(count=Count("cartitems"))
        # for displaying tags filter fields
        product_tags = ProductTags.objects.all()

        # for the individual category change the categories variable
        # to its descendants. To make the category.html get the
        # subcategories as well.
        category_slug = self.kwargs.get("slug")
        if category_slug:
            category = Category.objects.filter(slug=category_slug)
            categories = (
                category
                .get_descendants(include_self=False)
                .annotate(count=Count("product") + Count('children__product'))
            )

        # for counting how many products are in each category
        else:
            categories = (
                categories
                .get_descendants(include_self=True)
                .annotate(count=Count('product') + Count('children__product'))
                .filter(parent__isnull=True)
            )

        context["categories"] = categories
        # for displaying the dropdown menu with only root categories
        context["categories_root"] = (
            Category.objects.filter(parent__isnull=True)
        )
        context["cart_count"] = cart_count.get("count")
        context["product_tags"] = product_tags
        # To make pagination work with filtering, search and sorting
        context["get_param"] = self.request.GET
        return context


class ContactView(TemplateView):
    template_name = "contact/contact.html"

    # when search is triggered it will be redirected
    # to the shop and filter the products accordingly
    def get(self, *args, **kwargs):
        if self.request.GET.get('q'):
            return redirect(f'/store/category/?q={self.request.GET.get('q')}')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # for displaying the dropdown menu with only root categories
        categories = Category.objects.filter(parent__isnull=True)
        # for displaying cart item count
        cart = Cart.objects.filter(user_id=self.request.user.id)
        cart_count = cart.aggregate(count=Count("cartitems"))
        context["cart_count"] = cart_count.get("count")
        context["categories_root"] = categories
        return context


class ProductView(DetailView):
    model = Product
    template_name = "product_detail/shop-detail.html"
    pk_url_kwarg = "id"
    queryset = Product.objects.prefetch_related("product_category", "tags")

    # when search is triggered it will be redirected
    # to the shop and filter the products accordingly
    def get(self, *args, **kwargs):
        if self.request.GET.get('q'):
            return redirect(f"/store/category/?q={self.request.GET.get('q')}")
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_reviews = ProductReviews.objects.filter(
            product=self.object
        ).select_related("user")
        # initial quantity for the product
        quantity = 1

        categories = (
            Category.objects
            .all()
            .get_descendants(include_self=True)
            .annotate(count=Count('product') + Count('children__product'))
            .filter(parent__isnull=True)
        )
        # for displaying cart item count
        cart = Cart.objects.filter(user_id=self.request.user.id)
        cart_count = cart.aggregate(count=Count("cartitems"))

        context["reviews"] = product_reviews
        # for displaying the dropdown menu with only root categories
        context["categories_root"] = categories
        context["quantity"] = quantity
        context["cart_count"] = cart_count.get("count")
        return context
