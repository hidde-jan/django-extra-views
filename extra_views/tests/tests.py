from django.forms import ValidationError
from django.test import TestCase
from django.utils.unittest import expectedFailure
from models import Item, Order, Tag
from decimal import Decimal as D

class FormSetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
    
    def test_create(self):
        res = self.client.get('/formset/simple/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertTemplateUsed(res, 'extra_views/address_formset.html')
        self.assertEquals(res.context['formset'].__class__.__name__, 'AddressFormFormSet')
        
    def test_missing_management(self):
        with self.assertRaises(ValidationError):
            self.client.post('/formset/simple/', {})            
        
    def test_success(self):            
        res = self.client.post('/formset/simple/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple/', status_code=302)
        
    @expectedFailure        
    def test_put(self):
        res = self.client.put('/formset/simple/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple/', status_code=302)        

    def test_success_url(self):            
        res = self.client.post('/formset/simple_redirect/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple_redirect/valid/')

    def test_invalid(self):
        data = {
            'form-0-name': u'Joe Bloggs',
            'form-0-city': u'',
            'form-0-line1': u'',
            'form-0-line2': u'',
            'form-0-postcode': u'',
        }
        data.update(self.management_data)
        
        res = self.client.post('/formset/simple/', data, follow=True)        
        self.assertEquals(res.status_code, 200)
        self.assertTrue('postcode' in res.context['formset'].errors[0])
        
    def test_formset_class(self):
        res = self.client.get('/formset/custom/')
        self.assertEqual(res.status_code, 200)
        
       
class ModelFormSetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
    
    def test_create(self):
        res = self.client.get('/modelformset/simple/')        
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertTemplateUsed(res, 'extra_views/item_formset.html')
        self.assertEquals(res.context['formset'].__class__.__name__, 'ItemFormFormSet')
        
    def test_override(self):
        res = self.client.get('/modelformset/custom/')        
        self.assertEqual(res.status_code, 200)
        form = res.context['formset'].forms[0]
        self.assertEquals(form['flag'].value(), True)
        self.assertEquals(form['notes'].value(), 'Write notes here')
        
    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()
             
        data = {
            'form-0-name': 'Bubble Bath',
            'form-0-sku': '1234567890123',
            'form-0-price': D('9.99'),
            'form-0-order': order.id,
            'form-0-status': 0,
        }
        data.update(self.management_data)
        data['form-TOTAL_FORMS'] = u'1'
        res = self.client.post('/modelformset/simple/', data, follow=True)        
        self.assertEqual(res.status_code, 200)
        self.assertEquals(Item.objects.all().count(), 1)
        
#    def test_test_pagination(self):
#        order = Order(name='Dummy Order')
#        order.save()
#        
#        for i in range(10):
#            item = Item(name='Item %i' % i,sku=str(i)*13,price=D('9.99'),order=order, status=0)
#            item.save()
#            
#        print Item.objects.all()
#            
#        res = self.client.get('/modelformset/paged/')        
#        self.assertEqual(res.status_code, 200)


class InlineFormSetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
            'item_set-TOTAL_FORMS': u'2',
            'item_set-INITIAL_FORMS': u'0',
            'item_set-MAX_NUM_FORMS': u'',
        }
        
    
    def test_create(self):
        order = Order(name='Dummy Order')
        order.save()
        
        for i in range(10):
            item = Item(name='Item %i' % i,sku=str(i)*13,price=D('9.99'),order=order, status=0)
            item.save()
        
        res = self.client.get('/inlineformset/1/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        
    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()
        data = {}
        data.update(self.management_data)

        res = self.client.post('/inlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        
    def test_save(self):
        order = Order(name='Dummy Order')
        order.save()
        data = {
            'item_set-0-name': 'Bubble Bath',
            'item_set-0-sku': '1234567890123',
            'item_set-0-price': D('9.99'),
            'item_set-0-order': order.id,
            'item_set-0-status': 0,
            'item_set-1-DELETE': True,
        }
        data.update(self.management_data)

        self.assertEquals(0, order.item_set.count())
        self.client.post('/inlineformset/1/', data, follow=True)
        order = Order.objects.get(id=1)
          
        self.assertEquals(1, order.item_set.count())
        
class GenericInlineFormSetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    
    def test_get(self):
        order = Order(name='Dummy Order')
        order.save()
        
        order2 = Order(name='Other Order')
        order2.save()
        
        tag = Tag(name='Test', content_object=order)
        tag.save()
        
        tag = Tag(name='Test2', content_object=order2)
        tag.save()
        
        res = self.client.get('/genericinlineformset/1/')
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertEquals('Test', res.context['formset'].forms[0]['name'].value())

    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()
        
        
        
        tag = Tag(name='Test',content_object=order)
        tag.save()
        
        data = {
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': 'Updated',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-1-DELETE': True,
            'tests-tag-content_type-object_id-2-DELETE': True,            
        }

        res = self.client.post('/genericinlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals('Updated', res.context['formset'].forms[0]['name'].value())
        
        self.assertEquals(1, Tag.objects.count())
        
    def test_post2(self):
        order = Order(name='Dummy Order')
        order.save()
        
        tag = Tag(name='Test',content_object=order)
        tag.save()
        
        data = {
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': 'Updated',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-1-name': 'Tag 2',
            'tests-tag-content_type-object_id-2-name': 'Tag 3',
        }

        res = self.client.post('/genericinlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals(3, Tag.objects.count())

        
class ModelWithInlinesTests(TestCase):
    urls = 'extra_views.tests.urls'    
    
    def test_create(self):
        res = self.client.get('/inlines/new/')
        self.assertEqual(res.status_code, 200)
        self.assertEquals(0,Tag.objects.count())        
        
        data = {
            'name': u'Dummy Order',
            'item_set-TOTAL_FORMS': u'2',
            'item_set-INITIAL_FORMS': u'0',
            'item_set-MAX_NUM_FORMS': u'',                
            'item_set-0-name': 'Bubble Bath',
            'item_set-0-sku': '1234567890123',
            'item_set-0-price': D('9.99'),
            'item_set-0-status': 0,
            'item_set-0-order': u'',
            'item_set-1-DELETE': True,
            'tests-tag-content_type-object_id-TOTAL_FORMS': 2,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 0,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': u'Test',
            'tests-tag-content_type-object_id-1-DELETE': True,
        }
        
        res = self.client.post('/inlines/new/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals(1,Tag.objects.count())
        

    def test_update(self):
        order = Order(name='Dummy Order')
        order.save()
        
        for i in range(2):
            item = Item(name='Item %i' % i,sku=str(i)*13,price=D('9.99'),order=order, status=0)
            item.save()
            
        tag = Tag(name='Test',content_object=order)
        tag.save()
            
        res = self.client.get('/inlines/1/')

        self.assertEqual(res.status_code, 200)
        order = Order.objects.get(id=1)

        self.assertEquals(2, order.item_set.count())
        self.assertEquals('Item 0', order.item_set.all()[0].name)        
        
        data = {
            'name': u'Dummy Order',
            'item_set-TOTAL_FORMS': u'4',
            'item_set-INITIAL_FORMS': u'2',
            'item_set-MAX_NUM_FORMS': u'',                
            'item_set-0-name': 'Bubble Bath',
            'item_set-0-sku': '1234567890123',
            'item_set-0-price': D('9.99'),
            'item_set-0-status': 0,
            'item_set-0-order': 1,
            'item_set-0-id': 1,
            'item_set-1-name': 'Bubble Bath',
            'item_set-1-sku': '1234567890123',
            'item_set-1-price': D('9.99'),
            'item_set-1-status': 0,
            'item_set-1-order': 1,
            'item_set-1-id': 2,            
            'item_set-2-name': 'Bubble Bath',
            'item_set-2-sku': '1234567890123',
            'item_set-2-price': D('9.99'),
            'item_set-2-status': 0,
            'item_set-2-order': 1,
            'item_set-3-DELETE': True,
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': u'Test',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-0-DELETE': True,              
            'tests-tag-content_type-object_id-1-name': u'Test 2',
            'tests-tag-content_type-object_id-2-name': u'Test 3',                       
        }
        
        res = self.client.post('/inlines/1/', data, follow=True)
        self.assertEqual(res.status_code, 200) 
        
        order = Order.objects.get(id=1)        
        
        self.assertEquals(3, order.item_set.count())
        self.assertEquals(2, Tag.objects.count())
        self.assertEquals('Bubble Bath', order.item_set.all()[0].name)


#class MultiFormViewTests(TestCase):
#    urls = 'extra_views.tests.urls'
#    
#    valid_order = {
#        'order-form_identifier': None,
#        'order-name': 'Joe Bloggs'
#    }
#    valid_address = {
#        'address-form_id': None,
#        'address-name': 'Joe Bloggs',
#        'address-city': u'',
#        'address-line1': u'',
#        'address-line2': u'',
#        'address-postcode': u'ABC 123',
#    }
#    invalid_order = {
#        'order-form_identifier': None,                     
#    }    
#    invalid_address = {
#        'address-form_identifier': None,
#    }
#
#    def test_create(self):
#        res = self.client.get('/multiview/forms/')
#        self.assertEqual(res.status_code, 200)
#        self.assertTrue('order_form' in res.context)
#        self.assertTrue('address_form' in res.context)
#        self.assertEquals(res.context['order_form'].__class__.__name__, 'OrderForm')
#        self.assertEquals(res.context['address_form'].__class__.__name__, 'AddressForm')
#
#    def test_create_formsets(self):
#        res = self.client.get('/multiview/formsets/')
#        self.assertEqual(res.status_code, 200)
#        self.assertTrue('order_form' in res.context)
#        self.assertTrue('items_formset' in res.context)
#        self.assertEquals(res.context['order_form'].__class__.__name__, 'OrderForm')
#        self.assertEquals(res.context['items_formset'].__class__.__name__, 'ItemFormFormSet')
#       
#    def test_post(self):
#        data = {}
#        data.update(self.valid_order)
#        res = self.client.post('/multiview/forms/', data, follow=True)
#        self.assertRedirects(res, '/multiview/forms/valid/', status_code=302)
#        self.assertEquals(Order.objects.all().count(), 1)
#        
#        data = {}
#        data.update(self.valid_order)
#        data.update(self.valid_address)        
#        res = self.client.post('/multiview/forms/', data, follow=True)
#        self.assertEquals(Order.objects.all().count(), 2)        
#        self.assertRedirects(res, '/multiview/forms/valid/', status_code=302)
#
#
#    def test_simple(self):
#        data = {}
#        data.update(self.valid_order)
#        data.update(self.valid_address)        
#        res = self.client.post('/multiview/simple/', data, follow=True)      
#        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
#        
#    def test_invalid_view(self):
#        with self.assertRaises(ImproperlyConfigured):
#            self.client.get('/multiview/error/')
#        
#    def test_invalid_data(self):
#        data = {}
#        data.update(self.valid_address)        
#        res = self.client.post('/multiview/forms/', data, follow=True)
#        self.assertEquals(res.status_code, 404)               
#        
#        
#    def test_nosuccess(self):
#        with self.assertRaises(ImproperlyConfigured):
#            self.client.post('/multiview/nosuccess/', {}, follow=True)        
#        
#    def test_empty_success(self):
#        res = self.client.post('/multiview/simple/', {}, follow=True)
#        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
#        
#    def test_order_success(self):
#        data = {}
#        data.update(self.valid_order)
#        res = self.client.post('/multiview/simple/', data, follow=True)
#        
#        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
#        
#    def test_both_success(self):
#        data = {}
#        data.update(self.valid_order)
#        data.update(self.valid_address)
#        
#        res = self.client.post('/multiview/simple/', data, follow=True)
#        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
        
#    def test_order_invalid(self):
#        data = {}
#        data.update(self.invalid_order)
#        data.update(self.valid_address)
#        
#        res = self.client.post('/multiview/simple/', data, follow=True)
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(len(res.context['order_form'].errors), 1)
#        self.assertEquals(len(res.context['address_form'].errors), 0)
#
#    def test_address_invalid(self):
#        data = {}
#        data.update(self.valid_order)
#        data.update(self.invalid_address)
#        
#        res = self.client.post('/multiview/simple/', data, follow=True)
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(len(res.context['order_form'].errors), 0)
#        self.assertEquals(len(res.context['address_form'].errors), 2)
#        
#    def test_both_invalid(self):
#        data = {}
#        data.update(self.invalid_order)
#        data.update(self.invalid_address)
#        
#        res = self.client.post('/multiview/simple/', data, follow=True)
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(len(res.context['order_form'].errors), 1)
#        self.assertEquals(len(res.context['address_form'].errors), 2)
#        
#    def test_valid_handler(self):
#        data = {}
#        data.update(self.valid_order)
#        
#        res = self.client.post('/multiview/handlers/', data, follow=True)
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(self.client.session['valid_order'], 'Joe Bloggs')
#        self.assertEquals(self.client.session['forms_valid'], 'All')
#
#    def test_invalid_handler(self):
#        data = {}
#        data.update(self.invalid_address)
#        
#        res = self.client.post('/multiview/handlers/', data, follow=True)
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(self.client.session['invalid_address'], 'Error')
#        self.assertEquals(self.client.session['forms_invalid'], 'Any')        
#
#    def test_initial_data(self):
#        res = self.client.get('/multiview/initialdata/')
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(res.context['order_form']['name'].value(), 'Sally Jones')
#        self.assertEquals(res.context['address_form']['name'].value(), 'Sally Jones')
#        self.assertEquals(res.context['address_form']['postcode'].value(), 'ABC 123')
# 
#    def test_initial_handlers(self):
#        res = self.client.get('/multiview/initialhandler/')
#        self.assertEquals(res.status_code, 200)
#        self.assertEquals(res.context['order_form']['name'].value(), 'Bob Jones')
#        self.assertEquals(res.context['address_form']['name'].value(), 'Bob Jones')
#        self.assertEquals(res.context['address_form']['postcode'].value(), 'XYZ 789') 
#
#    def test_formsets_create(self):
#        res = self.client.get('/multiview/formsets/')
#        self.assertEquals(res.status_code, 200)
#        
#    def test_formsets_empty_success(self):
#        res = self.client.post('/multiview/formsets/', {}, follow=True)
#        self.assertEquals(res.status_code, 200)    
#        
#    def test_formsets_success(self):
#        order = Order(name='Dummy Order')
#        order.save()
#        
#        data = {
#            'items-TOTAL_FORMS': u'2',
#            'items-INITIAL_FORMS': u'0',
#            'items-MAX_NUM_FORMS': u'',                
#            'items-0-form_identifier': None,
#            'items-0-name': 'Bubble Bath',
#            'items-0-sku': '1234567890123',
#            'items-0-price': D('9.99'),
#            'items-0-order': order.id,
#            'items-0-status': 0,
#            'items-1-name': 'Toybox',
#            'items-1-sku': '9876543210987',
#            'items-1-price': D('5.99'),
#            'items-1-order': order.id,
#            'items-1-status': 0,            
#        }
#        res = self.client.post('/multiview/formsets/', data, follow=True)
#        self.assertEquals(res.status_code, 200)   
