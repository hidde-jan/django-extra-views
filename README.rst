django-extra-views - The missing class-based generic views for Django
=====================================================================

Django's class-based generic views are great, they let you accomplish a large number of web application design patterns in relatively few lines of code.  They do have their limits though, and that's what this library of views aims to overcome.

Features so far
------------------

- FormSet and ModelFormSet views - The formset equivalents of FormView and ModelFormView.
- InlineFormSetView - Lets you edit formsets related to a model (uses inlineformset_factory)
- CreateWithInlinesView and UpdateWithInlinesView - Lets you edit a model and its relations
- GenericInlineFormSetView, the equivalent of InlineFormSetView but for GenericForeignKeys
- Support for generic inlines in CreateWithInlinesView and UpdateWithInlinesView

Still to do
-----------
- Support for pagination in ModelFormSetView

Examples
--------

Defining a FormSetView. ::

    from extra_views import FormSetView
    
    class AddressFormSet(FormSetView):
        form_class = AddressForm
        template_name = 'address_formset.html'

Defining a ModelFormSetView. ::

    from extra_views import ModelFormSetView:

    class ItemFormSetView(ModelFormSetView):
        model = Item
        template_name = 'item_formset.html'

Defining a CreateWithInlinesView and an UpdateWithInlinesView. ::

    from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
    from extra_views.generic import GenericInlineFormSet

    class ItemInline(InlineFormSet):
        model = Item

    class TagInline(GenericInlineFormSet):
        model = Tag

    class CreateOrderView(CreateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]

    class UpdateOrderView(UpdateWithInlinesView):
        model = Order
        inlines = [ItemInline, TagInline]

    # Example URLs.
    urlpatterns = patterns('',
        url(r'^orders/new/$', CreateOrderView.as_view()),
        url(r'^orders/(?P<pk>\d+)/$', UpdateOrderView.as_view()),
    )

More descriptive examples to come.
