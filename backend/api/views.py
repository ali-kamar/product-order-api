from django.db.models import Max, Min
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Order, OrderItem, Product, User
from api.serializers import (OrderSerializer, ProductInfoSerializer,
                             ProductSerializer, OrderCreateSerializer, UserSerializer)

from .filters import InStockFilterBackend, ProductFilter, OrderFilter

# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)

# this is a class-based view that uses Generic Views to handles HTTP requests to list products, this is for get req
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk') # order by pk is important for pagination to work correctly and with no duplicates, it ensures that the products are ordered consistently.
    serializer_class = ProductSerializer
    filterset_class = ProductFilter  # Allows users to filter results based on specific fields 
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
        InStockFilterBackend
        ]
    search_fields = ['name', 'description']  # Enables keyword search across multiple fields
    ordering_fields = ['name', 'price']
    # pagination_class = PageNumberPagination  # Enables pagination for the list of products
    # pagination_class.page_size = 2  # Sets the default page size to 2 products
    # pagination_class.page_query_param = 'pagenumber' 
    # pagination_class.page_size_query_param = 'size'  # Allows clients to specify the page size via a query parameter 
    # pagination_class.max_page_size = 6  # Sets a maximum page size limit to prevent excessive data loading
    pagination_class = LimitOffsetPagination  # Enables limit-offset pagination for the list of products
    pagination_class.default_limit = 2  # Sets the default limit to 2 products per page
    pagination_class.max_limit = 6  # Sets a maximum limit of 6 products per page
    #limit=10 → Give me 10 items.
    #offset=20 → Skip the first 20 items and then give me the next 10 that starts from 21 to 30.

    #this is a decorator that caches the response of the list method for 2 hours (60 * 60 * 2 seconds).
    #This means that if the same request is made within 2 hours, the cached response will be returned instead of hitting the database again.
    #we should override the list method to apply the cache decorator.
    #key_prefix is used to create a unique cache key for the response, so that different responses can be cached separately.
    @method_decorator(cache_page(60 * 60 * 2,  key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(5)
        return super().get_queryset()   

    def get_permissions(self):
        if self.request.method == 'POST':
            # If the request method is POST, only allow admin users to create products
            #class isAdminUser take the request.user after the JWT assign it and check if the user is admin.
            #it search for request.user.is_staff, if true then the user is admin.
            self.permission_classes = [IsAdminUser]
            #we call the parent class's get_permissions method to apply the new permission classes, it Instantiates and returns the list of permissions that this view requires.
            # we can return: return [permission() for permission in self.permission_classes] instead if super().get_permissions()
            #because its job is to dismantle the list
        return super().get_permissions()

# @api_view(['GET'])
# def product_detail(request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'id'

    def get_permissions(self):
        #we used membership test to check the request method instead of using the or operator.
        if self.request.method in ['PUT', 'DELETE', 'PATCH']:
            # If the request method is PUT or DELETE, only allow admin users to update or delete products
            self.permission_classes = [IsAdminUser]
        else:
            # For GET requests, allow any user to view the product details
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Deleted successfully"},
            status=status.HTTP_200_OK
        )

# @api_view(['GET'])
# def order_list(request):
#     orders = Order.objects.prefetch_related('items__product')
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)

# class OrderListAPIView(generics.ListAPIView):
#     #This is saying:“I want to fetch all Orders, and also fetch all related OrderItems and their Products, efficiently, in advance.”
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer

# #get orders for a specific user.   
# class UserOrderListAPIView(generics.ListAPIView):
#     #we prefetch_related to optimize database queries, so we can access related objects without additional queries.
#     #prefetch_related is used for many-to-many and reverse foreign key relationships.
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     ###Authentication = Who Are You?
#     #     Example:
#     # You enter your username and password.Or you send a JWT token with your request.The system checks if the credentials or token are valid. If valid → you're authenticated, and request.user is set.
    
#     ###Authorization is the process of checking what permissions the authenticated user has.
#     # Example:
#     # You're authenticated as john_doe.You try to access the admin dashboard.The system checks:is john_doe.is_staff == True?
#     # If yes → you’re authorized to view the page.
#     # If not → you get a 403 Forbidden response.
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     # Python uses something called method resolution order (MRO).

#     # When the parent class (e.g., ListAPIView) needs to call self.get_queryset(), it looks at the actual object (MyView) and checks if that method is overridden there.

#     # If yes → Python calls your version.

#     # If not → it keeps looking up the chain of parent classes.

#     def get_queryset(self):
#         # if you override a method, you want to call the parent’s method explicitly. Use super().
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        # If the user is not an admin, filter orders by the authenticated user
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
                # If the request method is PUT, PATCH, or DELETE, only allow admin users to update or delete orders
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Order deleted successfully.'}, status=status.HTTP_200_OK)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            # If the request method is POST, use the OrderCreateSerializer
            return OrderCreateSerializer
        return super().get_serializer_class()
    #here we override the perform_create method to automatically set the user field to the authenticated user when creating an order.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # @action(detail=False, methods=['get'], url_path='user-orders')
    # def user_orders(self, request):
    #     queryset = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    


#this is alternative to the api_view decorator and we can define http methods like get, post, put, delete in the same class.
#we use this class for data that is not directly related to a specific model instance, such as aggregated data or statistics.
class ProductInfoApiView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            #this aggregate function returns a dictionary or object so we choosed the max price in the square brackets at the end
            'max_price': products.aggregate(max_price=Max('price'),min_price=Min('price'))['max_price']
        })
        return Response(serializer.data)
    
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    

# @api_view(['GET'])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer({
#         'products': products,
#         'count': len(products),
#         'max_price': products.aggregate(max_price=Max('price'),min_price=Min('price'))['max_price']
#     })
#     return Response(serializer.data)