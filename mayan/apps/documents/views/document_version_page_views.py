import logging

from furl import furl

from django.contrib import messages
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _, ungettext
from django.views.generic import RedirectView

from mayan.apps.common.classes import ModelQueryFields
from mayan.apps.common.settings import setting_home_view
from mayan.apps.converter.literals import DEFAULT_ROTATION, DEFAULT_ZOOM_LEVEL
from mayan.apps.views.generics import (
    MultipleObjectConfirmActionView, SimpleView, SingleObjectListView
)
from mayan.apps.views.mixins import ExternalObjectMixin
from mayan.apps.views.utils import resolve

from ..forms.document_version_page_forms import DocumentVersionPageForm
from ..icons import icon_document_version_pages
#from ..links.document_version_page_links import link_document_file_page_count_update
from ..models.document_models import Document
from ..models.document_version_models import DocumentVersion
from ..models.document_version_page_models import DocumentVersionPage
from ..permissions import permission_document_version_view
from ..settings import (
    setting_rotation_step, setting_zoom_percent_step, setting_zoom_max_level,
    setting_zoom_min_level
)

__all__ = (
    'DocumentVersionPageListView',
    'DocumentVersionPageNavigationFirst', 'DocumentVersionPageNavigationLast',
    'DocumentVersionPageNavigationNext', 'DocumentVersionPageNavigationPrevious',
    'DocumentVersionPageView', 'DocumentVersionPageViewResetView',
    'DocumentVersionPageInteractiveTransformation', 'DocumentVersionPageZoomInView',
    'DocumentVersionPageZoomOutView', 'DocumentVersionPageRotateLeftView',
    'DocumentVersionPageRotateRightView'
)
logger = logging.getLogger(name=__name__)


class DocumentVersionPageListView(ExternalObjectMixin, SingleObjectListView):
    external_object_class = DocumentVersion
    external_object_permission = permission_document_version_view
    external_object_pk_url_kwarg = 'document_version_id'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'list_as_items': True,
            #'no_results_icon': icon_document_version_pages,
            #'no_results_main_link': link_document_file_page_count_update.resolve(
            #    request=self.request, resolved_object=self.external_object
            #),
            'no_results_text': _(
                'This could mean that the document is of a format that is '
                'not supported, that it is corrupted or that the upload '
                'process was interrupted. Use the document page recalculation '
                'action to attempt to introspect the page count again.'
            ),
            'no_results_title': _('No document pages available'),
            'object': self.external_object,
            'title': _('Pages of document version: %s') % self.external_object,
        }

    def get_source_queryset(self):
        queryset = ModelQueryFields.get(model=DocumentVersionPage).get_queryset()
        return queryset.filter(pk__in=self.external_object.pages.all())

'''
class DocumentVersionPageNavigationBase(ExternalObjectMixin, RedirectView):
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_version_page_id'
    external_object_queryset = DocumentVersionPage.valid

    def get_redirect_url(self, *args, **kwargs):
        """
        Attempt to jump to the same kind of view but resolved to a new
        object of the same kind.
        """
        previous_url = self.request.META.get('HTTP_REFERER', None)

        if not previous_url:
            try:
                previous_url = self.external_object.get_absolute_url()
            except AttributeError:
                previous_url = reverse(viewname=setting_home_view.value)

        parsed_url = furl(url=previous_url)

        # Obtain the view name to be able to resolve it back with new keyword
        # arguments.
        resolver_match = resolve(path=force_text(parsed_url.path))

        new_kwargs = self.get_new_kwargs()

        if set(new_kwargs) == set(resolver_match.kwargs):
            # It is the same type of object, reuse the URL to stay in the
            # same kind of view but pointing to a new object
            url = reverse(
                viewname=resolver_match.view_name, kwargs=new_kwargs
            )
        else:
            url = parsed_url.path

        # Update just the path to retain the querystring in case there is
        # transformation data.
        parsed_url.path = url

        return parsed_url.tostr()


class DocumentVersionPageNavigationFirst(DocumentVersionPageNavigationBase):
    def get_new_kwargs(self):
        return {'document_version_page_id': self.external_object.siblings.first().pk}


class DocumentVersionPageNavigationLast(DocumentVersionPageNavigationBase):
    def get_new_kwargs(self):
        return {'document_version_page_id': self.external_object.siblings.last().pk}


class DocumentVersionPageNavigationNext(DocumentVersionPageNavigationBase):
    def get_new_kwargs(self):
        new_document_version_page = self.external_object.siblings.filter(
            page_number__gt=self.external_object.page_number
        ).first()
        if new_document_version_page:
            return {'document_version_page_id': new_document_version_page.pk}
        else:
            messages.warning(
                message=_(
                    'There are no more pages in this document'
                ), request=self.request
            )
            return {'document_version_page_id': self.external_object.pk}


class DocumentVersionPageNavigationPrevious(DocumentVersionPageNavigationBase):
    def get_new_kwargs(self):
        new_document_version_page = self.external_object.siblings.filter(
            page_number__lt=self.external_object.page_number
        ).last()
        if new_document_version_page:
            return {'document_version_page_id': new_document_version_page.pk}
        else:
            messages.warning(
                message=_(
                    'You are already at the first page of this document'
                ), request=self.request
            )
            return {'document_version_page_id': self.external_object.pk}

'''
class DocumentVersionPageView(ExternalObjectMixin, SimpleView):
    external_object_permission = permission_document_version_view
    external_object_pk_url_kwarg = 'document_version_page_id'
    external_object_queryset = DocumentVersionPage
    template_name = 'appearance/generic_form.html'

    def get_extra_context(self):
        zoom = int(self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL))
        rotation = int(self.request.GET.get('rotation', DEFAULT_ROTATION))

        document_version_page_form = DocumentVersionPageForm(
            instance=self.external_object, rotation=rotation, zoom=zoom
        )

        base_title = _('Image of: %s') % self.external_object

        if zoom != DEFAULT_ZOOM_LEVEL:
            zoom_text = '({}%)'.format(zoom)
        else:
            zoom_text = ''

        return {
            'form': document_version_page_form,
            'hide_labels': True,
            'object': self.external_object,
            'rotation': rotation,
            'title': ' '.join((base_title, zoom_text)),
            'read_only': True,
            'zoom': zoom,
        }

'''
class DocumentVersionPageViewResetView(RedirectView):
    pattern_name = 'documents:document_version_page_view'


class DocumentVersionPageInteractiveTransformation(ExternalObjectMixin, RedirectView):
    external_object_class = DocumentVersionPage
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_version_page_id'

    def get_object(self):
        return self.external_object

    def get_redirect_url(self, *args, **kwargs):
        query_dict = {
            'rotation': self.request.GET.get('rotation', DEFAULT_ROTATION),
            'zoom': self.request.GET.get('zoom', DEFAULT_ZOOM_LEVEL)
        }

        url = furl(
            args=query_dict, path=reverse(
                viewname='documents:document_version_page_view', kwargs={
                    'document_version_page_id': self.external_object.pk
                }
            )

        )

        self.transformation_function(query_dict=query_dict)
        # Refresh query_dict to args reference
        url.args = query_dict

        return url.tostr()


class DocumentVersionPageZoomInView(DocumentVersionPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = int(query_dict['zoom']) + setting_zoom_percent_step.value

        if zoom > setting_zoom_max_level.value:
            zoom = setting_zoom_max_level.value

        query_dict['zoom'] = zoom


class DocumentVersionPageZoomOutView(DocumentVersionPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        zoom = int(query_dict['zoom']) - setting_zoom_percent_step.value

        if zoom < setting_zoom_min_level.value:
            zoom = setting_zoom_min_level.value

        query_dict['zoom'] = zoom


class DocumentVersionPageRotateLeftView(DocumentVersionPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            int(query_dict['rotation']) - setting_rotation_step.value
        ) % 360


class DocumentVersionPageRotateRightView(DocumentVersionPageInteractiveTransformation):
    def transformation_function(self, query_dict):
        query_dict['rotation'] = (
            int(query_dict['rotation']) + setting_rotation_step.value
        ) % 360
'''