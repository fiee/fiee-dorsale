# -*- coding: utf-8 -*-
# based on http://djangosnippets.org/snippets/1792/ by monokrome
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core import serializers
from django.db.models import Model
from django.db.models.loading import get_model
from django.db.models.query import QuerySet
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from datetime import date
import decimal, datetime
import csv
import xlwt  # XLS Writer, see pypi
import odf, odf.opendocument, odf.table
import logging
logger = logging.getLogger(settings.PROJECT_NAME)

DEFAULT_PARAMS = {
    'app_label': '',
    'model_name': '',
    'model': None,
    'format': 'csv',
    'fields': [],
    'headers': [],
    'charset': 'utf-8',
    'filename': '',
    'sheet_title': _(u'Export'),
}


class xlswriter(object):
    """
    XLS creator as drop-in replacement for csv.writer
    """
    # style0 = xlwt.easyxf('font: name Arial, color-index red, bold on', num_format_str='#,##0.00')
    # style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

    def __init__(self, targetfile, **kwargs):
        self.params = DEFAULT_PARAMS
        self.params.update(kwargs)

        self.stream = targetfile
        self.xlwb = xlwt.Workbook(encoding=self.params['charset'])
        self.xlws = self.xlwb.add_sheet(self.params['sheet_title'])
        self.rowcounter = 0

    def write_value(self, x, y, val, style):
        self.xlws.write(y, x, val, style)

    def write_formula(self, x, y, formula, style):
        self.xlws.write(y, x, xlwt.Formula(formula), style)

    def set_row_style(self, rownumber, style):
        return self.xlws.row(rownumber).set_style(style)

    def save(self, filename=None):
        if not filename:
            filename = self.stream
        self.xlwb.save(filename)
        self.rowcounter = 0

    def writerow(self, fields, style=None):
        if not style:
            style = xlwt.Style.default_style
        y = self.rowcounter
        for x in range(len(fields)):
            val = fields[x]
            if hasattr(val, 'startswith') and val.startswith('='):
                val = val.strip('=')  # otherwise parsing error
                self.write_formula(x, y, val, style)
            else:
                self.write_value(x, y, val, style)
        self.set_row_style(y, style)
        self.rowcounter += 1

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class odswriter(object):
    """
    ODS creator as drop-in replacement for csv.writer
    """

    def __init__(self, targetfile, **kwargs):
        self.params = DEFAULT_PARAMS
        self.params.update(kwargs)

        self.stream = targetfile
        self.ods = odf.opendocument.OpenDocumentSpreadsheet()
        self.odtable = odf.table.Table(name=self.params['sheet_title'])
        self.ods.spreadsheet.addElement(self.odtable)
        self.rowcounter = 0

    def save(self, filename=None):
        if not filename:
            self.ods.write(self.stream)
        else:
            self.ods.save(filename)
        self.rowcounter = 0

    def writerow(self, fields, style=None):
        row = odf.table.TableRow()
        for x in range(len(fields)):
            val = fields[x]
            args = {'value':val}
            if hasattr(val, 'startswith') and val.startswith('='):
                args = {'formula': val}
            elif type(val) in (str, unicode):
                args = {'stringvalue': val, 'valuetype': 'string'}
            elif type(val) in (decimal.Decimal,):
                args = {'currency': 'EUR', 'valuetype': 'currency'}
            elif type(val) in (int, float):
                args['valuetype'] = 'float'
            elif type(val) in (datetime.datetime, datetime.date):
                args = {'datevalue': val, 'valuetype': 'date'}
            elif type(val) in (datetime.time,):
                args = {'timevalue': val, 'valuetype': 'time'}
            elif type(val) in (bool,):
                args = {'booleanvalue': val, 'valuetype': 'boolean'}
            if style:
                args['stylename'] = style
            row.addElement(odf.table.TableCell(attributes=args))
        self.odtable.addElement(row)
        self.rowcounter += 1

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


ALLOWED_EXPORT_TYPES = {
    'csv': {
        'mimetype': 'text/csv',
        # 'template': 'admin/export/csv',
        'writer': csv.writer
    },
    'json': {
        'mimetype': 'text/json',
        'serializer': 'json',
    },
    'xml': {
        'mimetype': 'text/xml',
        'serializer': 'xml',
    },
    'yaml': {
        'mimetype': 'text/yaml',
        'serializer': 'yaml',
    },
    'py': {
        'mimetype': 'application/python',
        'serializer': 'python',
    },
    'xls': {
        'mimetype': 'application/vnd.ms-excel',
        'writer': xlswriter
    },
    'ods': {
        'mimetype': 'application/vnd.oasis.opendocument.spreadsheet',
        'writer': odswriter
    },
}


def export(request, qs, **kwargs):
    """
    This view exports data in one of several formats.

    Keyword arguments:

    :app_label:
        application name
    :model_name:
        name of model within app_label
    :model: django model
        replacement for app_label and model_name
    :format:
        str, defined by `ALLOWED_EXPORT_TYPES`
        csv, json, xml, yaml, py, xls, ods
        default: csv
    :fields:
        list of model fields
        default: all fields of given model
    :headers:
        column names for some formats
        default: verbose_names of model's fields
    :charset:
        for text formats
        default: utf-8
    :filename:
        output filename
        default: <model_name>_<date>.<format>
    """
    prm = DEFAULT_PARAMS
    prm.update(kwargs)
    exformat = prm['format']

    if not exformat in ALLOWED_EXPORT_TYPES:
        err = _(u'%s is not a supported format.') % exformat
        logger.error(err)
        raise Http404(err)

    if prm['app_label'] and prm['model_name']:
        model = get_model(prm['app_label'], prm['model_name'])
    elif prm['model']:
        model = prm['model']
    else:
        model = None

    if not prm['filename']:
        prm['filename'] = '%s_%s.%s' % (
            slugify(prm['model_name']),
            date.today().strftime('%Y-%m-%d'),
            exformat)
    if model:
        if not prm['fields']:
            prm['fields'] = [f.name for f in model._meta.local_fields]
        if not prm['headers']:
            try:
                prm['headers'] = [getattr(model, f).verbose_name for f in prm['fields']]
            except Exception, e:
                logger.error(e)
                prm['headers'] = prm['fields']

    mimetype = ALLOWED_EXPORT_TYPES[exformat]['mimetype']
    response = HttpResponse(mimetype=mimetype)
    response['Content-Type'] = '%s; charset=%s' % (mimetype, prm['charset'])
    response['Content-Disposition'] = 'attachment; filename=%s' % prm['filename']
    response['Cache-Control'] = 'must-revalidate'
    response['Pragma'] = 'must-revalidate'

    if 'writer' in ALLOWED_EXPORT_TYPES[exformat]:
        writer = ALLOWED_EXPORT_TYPES[exformat]['writer'](response)
        writer.writerow(prm['headers'])
        for item in qs:
            row = []
            for field in prm['fields']:
                val = getattr(item, field)
                if callable(val):
                    val = val()
                if isinstance(val, QuerySet):
                    val = u', '.join(x.__unicode__() for x in val.all())
                elif isinstance(val, Model):
                    val = val.__unicode__()
                elif isinstance(val, bool):
                    val = {True:_(u'Yes'), False:_(u'No')}[val]
                elif val == None:
                    val = _(u'Unknown')
                if type(val) is unicode and prm['format'] != 'ods':
                    val = val.encode(prm['charset'])
                row.append(val)
            writer.writerow(row)
        if hasattr(writer, 'save'):
            writer.save()
    elif 'serializer' in ALLOWED_EXPORT_TYPES[exformat]:
        serializer = serializers.get_serializer(
            ALLOWED_EXPORT_TYPES[exformat]['serializer'])()
        serializer.serialize(
            qs.all(),
            fields=prm['fields'],
            ensure_ascii=False,
            stream=response)
    else:
        err = _(u'Export type for %s must have value for writer or serializer') % exformat
        logger.error(err)
        raise Http404(err)

    return response
